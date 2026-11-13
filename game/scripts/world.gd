extends Node2D
## M0 test farm: lawn shader, fields, barn, nature, animals, camera and touch input.
##
## World units are 2x pixels: one grid cell is a 256 x 128 diamond.
## Grid -> world: ((x - y) * 128, (x + y) * 64), cell centres on integer coords.
##
## Command line (after "--"):
##   --smoke        run self checks and quit with exit code 0/1
##   --bench[=file] stress scene, vsync off, prints frame time stats and quits
##   --demo         fields start in mixed growth stages
##   --shot=file    save a screenshot after 3 s and quit (implies --demo)
##   --zoom=z       start zoom (for screenshots)

const HudScript := preload("res://scripts/hud.gd")
const FieldScript := preload("res://scripts/field.gd")
const AnimalScript := preload("res://scripts/animal.gd")
const SwayShader := preload("res://shaders/sway.gdshader")
const GroundShader := preload("res://shaders/ground.gdshader")

const HALF_W := 128.0
const HALF_H := 64.0
const MAP_MIN := -10
const MAP_MAX := 36
const MASK_SIZE := 64
const ZOOM_MIN := 0.2
const ZOOM_MAX := 1.0
const ZOOM_START := 0.52
const TAP_SLOP := 14.0
const BRUSH_STEP := 18.0

enum Mode { NONE, PAN, PINCH, PLANT, HARVEST }

var ground: Polygon2D
var objects: Node2D
var fx: Node2D
var cam: Camera2D
var hud: Hud
var fields: Dictionary = {}  # Vector2i -> Field
var animals: Array[Animal] = []
var props: Array[Sprite2D] = []  # tappable scenery (barn, trees, bushes)
var occupied: Dictionary = {}

var _sway_crop: ShaderMaterial
var _sway_tree: ShaderMaterial
var _sway_bush: ShaderMaterial
var _mask: Image
var _touches: Dictionary = {}
var _mode := Mode.NONE
var _moved := 0.0
var _pinch_dist := 0.0
var _brush_last := Vector2.ZERO
var _stroke_cells: Dictionary = {}
var _combo := 0
var _args: Dictionary = {}
var _bench_times := PackedFloat32Array()
var _bench_clock := 0.0
var _page_images: Dictionary = {}


func _ready() -> void:
	_parse_args()
	_sway_crop = _make_sway(5.0, 1.6, 60.0)
	_sway_tree = _make_sway(5.0, 1.1, 420.0)
	_sway_bush = _make_sway(3.0, 1.4, 120.0)
	_mask = Image.create(MASK_SIZE, MASK_SIZE, false, Image.FORMAT_RG8)
	objects = Node2D.new()
	objects.y_sort_enabled = true
	fx = Node2D.new()
	fx.z_index = 100
	_build_farm()
	_build_ground()
	add_child(objects)
	add_child(fx)
	cam = Camera2D.new()
	add_child(cam)
	cam.make_current()
	cam.position = grid_to_world(Vector2(11.5, 11.0))
	if _args.has("at"):
		var p: PackedStringArray = str(_args["at"]).split(",")
		cam.position = grid_to_world(Vector2(float(p[0]), float(p[1])))
	var z := float(_args.get("zoom", ZOOM_START))
	cam.zoom = Vector2(z, z)
	hud = HudScript.new()
	add_child(hud)

	if _args.has("smoke"):
		_run_smoke.call_deferred()
		return
	if _args.has("bench"):
		_setup_bench()
		return
	if _args.has("demo") or _args.has("shot"):
		_demo_state()
	Audio.play_music()
	if _args.has("shot"):
		_take_shot(_args["shot"])


# ------------------------------------------------------------------ coords

func grid_to_world(g: Vector2) -> Vector2:
	return Vector2((g.x - g.y) * HALF_W, (g.x + g.y) * HALF_H)


func world_to_grid(w: Vector2) -> Vector2:
	return Vector2(w.x / (2.0 * HALF_W) + w.y / (2.0 * HALF_H), w.y / (2.0 * HALF_H) - w.x / (2.0 * HALF_W))


func cell_at(world: Vector2) -> Vector2i:
	var g := world_to_grid(world)
	return Vector2i(roundi(g.x), roundi(g.y))


func screen_to_world(p: Vector2) -> Vector2:
	return cam.position + (p - get_viewport_rect().size * 0.5) / cam.zoom.x


# ------------------------------------------------------------------ build

func _make_sway(strength: float, speed: float, height: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SwayShader
	m.set_shader_parameter("strength", strength)
	m.set_shader_parameter("speed", speed)
	m.set_shader_parameter("height", height)
	return m


func _dirt(cell: Vector2i, amount := 1.0) -> void:
	var p := cell - Vector2i(MAP_MIN, MAP_MIN)
	if p.x < 0 or p.y < 0 or p.x >= MASK_SIZE or p.y >= MASK_SIZE:
		return
	var cur := _mask.get_pixelv(p)
	_mask.set_pixelv(p, Color(maxf(cur.r, amount), cur.g, 0))


func _water(cell: Vector2i, amount := 1.0) -> void:
	var p := cell - Vector2i(MAP_MIN, MAP_MIN)
	var cur := _mask.get_pixelv(p)
	_mask.set_pixelv(p, Color(cur.r, maxf(cur.g, amount), 0))
	occupied[cell] = true


func _dirt_rect(r: Rect2i, amount := 1.0) -> void:
	for x in range(r.position.x, r.end.x):
		for y in range(r.position.y, r.end.y):
			_dirt(Vector2i(x, y), amount)


func _build_ground() -> void:
	ground = Polygon2D.new()
	var a := grid_to_world(Vector2(MAP_MIN - 8, MAP_MIN - 8))
	var b := grid_to_world(Vector2(MAP_MAX + 8, MAP_MIN - 8))
	var c := grid_to_world(Vector2(MAP_MAX + 8, MAP_MAX + 8))
	var d := grid_to_world(Vector2(MAP_MIN - 8, MAP_MAX + 8))
	ground.polygon = PackedVector2Array([a, b, c, d])
	var m := ShaderMaterial.new()
	m.shader = GroundShader
	m.set_shader_parameter("grass_tex", load("res://art/generated/ground_grass.png"))
	m.set_shader_parameter("dirt_tex", load("res://art/generated/ground_dirt.png"))
	m.set_shader_parameter("mask_tex", ImageTexture.create_from_image(_mask))
	m.set_shader_parameter("mask_origin", Vector2(MAP_MIN, MAP_MIN))
	m.set_shader_parameter("mask_size", float(MASK_SIZE))
	ground.material = m
	add_child(ground)


func _build_farm() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 42

	# paths
	for x in range(2, 24):
		_dirt(Vector2i(x, 9))
		occupied[Vector2i(x, 9)] = true
	for y in range(10, 22):
		_dirt(Vector2i(9, y))
		occupied[Vector2i(9, y)] = true
	for y in range(5, 9):
		_dirt(Vector2i(20, y))
		occupied[Vector2i(20, y)] = true

	# fields 4 x 3
	for x in range(11, 15):
		for y in range(11, 14):
			_add_field(Vector2i(x, y))

	# barn on a dirt pad, hay and barrels are part of the sprite
	_dirt_rect(Rect2i(14, 3, 6, 5))
	_dirt(Vector2i(13, 4), 0.6)
	var barn := _add_prop("barn", Vector2(16, 5), null)
	barn.set_meta("squash", 0.04)
	barn.set_meta("sound", "whoosh")
	for x in range(14, 20):
		for y in range(3, 8):
			occupied[Vector2i(x, y)] = true

	# chicken pen: dirt floor, fence, trough
	var pen := Rect2i(3, 12, 4, 4)
	_dirt_rect(pen, 0.85)
	_fence_rect(pen, Vector2i(pen.position.x + 1, pen.end.y))
	_add_static("trough", Vector2(4.6, 12.4))
	_add_static("hay", Vector2(6.2, 12.3))
	for i in 5:
		_add_animal("chicken", pen, rng)

	# dino meadow (grass floor, a rock, a lazy baby dino)
	var meadow := Rect2i(16, 11, 4, 4)
	_fence_rect(meadow, Vector2i(meadow.position.x, meadow.end.y))
	_add_prop("rock", Vector2(18.9, 11.6), null)
	_add_prop("bush", Vector2(16.2, 11.3), _sway_bush)
	for i in 2:
		_add_animal("dino", Rect2i(meadow.position + Vector2i(0, 1), meadow.size - Vector2i(1, 1)), rng,
				Vector2(16.4 + i * 2.0, 12.2 + i * 1.6))

	# flower borders along the main path
	var kinds := ["flowers_lavender", "flowers_sun", "flowers_rose", "flowers_white"]
	for x in range(3, 23, 2):
		for y in [8, 10]:
			var cell := Vector2i(x, y)
			if occupied.has(cell) or (x >= 10 and x <= 15 and y == 10) or (x >= 14 and y == 8):
				continue
			if rng.randf() < 0.55:
				_add_prop(kinds[rng.randi() % kinds.size()], Vector2(cell), _sway_bush)
				occupied[cell] = true

	# decoration near the barn and fields
	for spot in [Vector2(21.3, 4.2), Vector2(21.6, 5.6)]:
		_add_static("barrel" if spot.y < 5 else "crate", spot)
	for spot in [Vector2(10.4, 14.6), Vector2(15.4, 10.4)]:
		_add_prop("bush_berry", spot, _sway_bush)

	# pond in the south-west with stones, reeds and flowers on the shore
	var pond := {Vector2i(3, 18): 1.0, Vector2i(4, 18): 1.0, Vector2i(5, 18): 0.9, Vector2i(3, 19): 1.0,
		Vector2i(4, 19): 1.0, Vector2i(5, 19): 1.0, Vector2i(6, 19): 0.7, Vector2i(4, 20): 1.0,
		Vector2i(5, 20): 0.9, Vector2i(2, 19): 0.6, Vector2i(4, 17): 0.6, Vector2i(3, 20): 0.6}
	for c: Vector2i in pond:
		_water(c, pond[c])
	for spot in [Vector2(6.3, 18.1), Vector2(2.2, 17.8), Vector2(6.1, 20.4)]:
		_add_prop("rock_small", spot, null)
	for spot in [Vector2(2.0, 20.6), Vector2(6.9, 19.3), Vector2(4.4, 21.3)]:
		_add_prop("flowers_lavender", spot, _sway_bush)
	_add_prop("bush", Vector2(1.8, 18.9), _sway_bush)
	_add_prop("tree_oak_b", Vector2(1.2, 16.6), _sway_tree)
	for x in range(1, 9):
		for y in range(16, 23):
			occupied[Vector2i(x, y)] = true

	# extra flowers and bushes so the farm feels lived in
	for spot in [Vector2(10.3, 10.5), Vector2(15.6, 14.3), Vector2(13.2, 14.6), Vector2(19.3, 16.4),
			Vector2(8.2, 12.2), Vector2(8.3, 16.4), Vector2(12.6, 7.7), Vector2(21.4, 10.6),
			Vector2(17.6, 8.2), Vector2(10.4, 17.5), Vector2(14.5, 16.6), Vector2(7.8, 10.5)]:
		var cell := Vector2i(spot.round())
		if occupied.has(cell):
			continue
		_add_prop(kinds[rng.randi() % kinds.size()], spot, _sway_bush)
		occupied[cell] = true
	for spot in [Vector2(2.3, 11.4), Vector2(7.6, 15.6), Vector2(20.6, 13.0), Vector2(15.4, 17.2)]:
		var cell := Vector2i(spot.round())
		if not occupied.has(cell):
			_add_prop("bush" if rng.randf() < 0.5 else "bush_berry", spot, _sway_bush)
			occupied[cell] = true

	# trees and scenery around the farm, denser towards the edge
	var inner := Rect2i(0, 1, 24, 22)
	var trees := ["tree_oak", "tree_oak", "tree_oak_b", "tree_pine", "tree_pine_b", "tree_pine", "tree_autumn"]
	var tries := 0
	var placed := 0
	while placed < 150 and tries < 4000:
		tries += 1
		var cell := Vector2i(rng.randi_range(MAP_MIN + 1, MAP_MAX - 2), rng.randi_range(MAP_MIN + 1, MAP_MAX - 2))
		if inner.has_point(cell) or occupied.has(cell):
			continue
		var r := rng.randf()
		var off := Vector2(rng.randf_range(-0.25, 0.25), rng.randf_range(-0.25, 0.25))
		if r < 0.78:
			_add_prop(trees[rng.randi() % trees.size()], Vector2(cell) + off, _sway_tree)
		elif r < 0.9:
			_add_prop("bush" if rng.randf() < 0.6 else "bush_berry", Vector2(cell) + off, _sway_bush)
		else:
			_add_prop("rock" if rng.randf() < 0.5 else "rock_small", Vector2(cell) + off, null)
		occupied[cell] = true
		placed += 1
	for spot in [Vector2(12, 3.5), Vector2(22, 15), Vector2(21.5, 18.5), Vector2(1.5, 5.5)]:
		_add_prop("tree_apple", spot, _sway_tree)
		occupied[Vector2i(spot)] = true
	for i in 16:
		var cell := Vector2i(rng.randi_range(2, 22), rng.randi_range(3, 21))
		if occupied.has(cell) or cell.y >= 11 and cell.y <= 16 and cell.x >= 2 and cell.x <= 20:
			continue
		var kind: String = ["bush", "rock_small", "flowers_white", "flowers_lavender"][rng.randi() % 4]
		_add_prop(kind, Vector2(cell), null if kind.begins_with("rock") else _sway_bush)
		occupied[cell] = true


func _fence_rect(r: Rect2i, gate: Vector2i) -> void:
	for x in range(r.position.x, r.end.x):
		for y in range(r.position.y, r.end.y):
			occupied[Vector2i(x, y)] = true
	# fence_x runs along grid x, placed on the cell border (y - 0.5)
	for x in range(r.position.x, r.end.x):
		_add_static("fence_x", Vector2(x, r.position.y - 0.5))
		if Vector2i(x, r.end.y) != gate:
			_add_static("fence_x", Vector2(x, r.end.y - 0.5))
	for y in range(r.position.y, r.end.y):
		_add_static("fence_y", Vector2(r.position.x - 0.5, y))
		_add_static("fence_y", Vector2(r.end.x - 0.5, y))


func _add_field(cell: Vector2i) -> Field:
	var f: Field = FieldScript.new()
	f.cell = cell
	f.position = grid_to_world(Vector2(cell))
	f.setup(_sway_crop)
	objects.add_child(f)
	fields[cell] = f
	occupied[cell] = true
	return f


func _add_prop(sprite_name: String, g: Vector2, mat: Material) -> Sprite2D:
	var s := _add_static(sprite_name, g)
	s.material = mat
	s.set_meta("squash", 0.1)
	props.append(s)
	return s


func _add_static(sprite_name: String, g: Vector2) -> Sprite2D:
	var s := Atlas.sprite(sprite_name)
	s.position = grid_to_world(g)
	s.set_meta("sprite", sprite_name)
	objects.add_child(s)
	return s


func _add_animal(kind: String, pen: Rect2i, rng: RandomNumberGenerator, start := Vector2(-999, -999)) -> Animal:
	var a: Animal = AnimalScript.new()
	a.kind = kind
	var pick := func() -> Vector2:
		return grid_to_world(Vector2(randf_range(pen.position.x - 0.2, pen.end.x - 0.8),
				randf_range(pen.position.y - 0.2, pen.end.y - 0.8)))
	a.random_point = pick
	a.position = grid_to_world(Vector2(pen.position) + Vector2(rng.randf_range(0, pen.size.x - 1),
			rng.randf_range(0, pen.size.y - 1)))
	if start.x > -999.0:
		a.position = grid_to_world(start)
	objects.add_child(a)
	animals.append(a)
	return a


# ------------------------------------------------------------------ input

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			zoom_at(event.position, 1.1)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			zoom_at(event.position, 1.0 / 1.1)
	elif event is InputEventScreenTouch:
		if event.pressed:
			_touches[event.index] = event.position
			_on_press(event.position)
		else:
			_touches.erase(event.index)
			_on_release(event.position)
	elif event is InputEventScreenDrag:
		_touches[event.index] = event.position
		_on_drag(event)


func _on_press(pos: Vector2) -> void:
	if _touches.size() >= 2:
		_mode = Mode.PINCH
		var p: Array = _touches.values()
		_pinch_dist = p[0].distance_to(p[1])
		return
	_moved = 0.0
	_combo = 0
	_stroke_cells.clear()
	var f: Field = fields.get(cell_at(screen_to_world(pos)))
	if f != null and f.state == Field.State.RIPE:
		_mode = Mode.HARVEST
	elif f != null and f.state == Field.State.EMPTY:
		_mode = Mode.PLANT
	else:
		_mode = Mode.PAN
		return
	_brush_last = pos
	_brush_at(pos)


func _on_drag(event: InputEventScreenDrag) -> void:
	match _mode:
		Mode.PAN:
			_moved += event.relative.length()
			cam.position -= event.relative / cam.zoom.x
			_clamp_cam()
		Mode.PINCH:
			if _touches.size() >= 2:
				var p: Array = _touches.values()
				var d: float = p[0].distance_to(p[1])
				if _pinch_dist > 0.0:
					zoom_at((p[0] + p[1]) * 0.5, d / _pinch_dist)
				_pinch_dist = d
		Mode.PLANT, Mode.HARVEST:
			# interpolate so fast swipes never skip a field
			var from := _brush_last
			var dist := from.distance_to(event.position)
			var steps := maxi(1, int(dist / BRUSH_STEP))
			for i in range(1, steps + 1):
				_brush_at(from.lerp(event.position, float(i) / steps))
			_brush_last = event.position


func _on_release(pos: Vector2) -> void:
	if _mode == Mode.PINCH:
		_mode = Mode.NONE if _touches.size() < 2 else Mode.PINCH
		return
	if _touches.is_empty():
		if _mode == Mode.PAN and _moved < TAP_SLOP:
			_tap(screen_to_world(pos))
		_mode = Mode.NONE


func _brush_at(screen_pos: Vector2) -> void:
	var cell := cell_at(screen_to_world(screen_pos))
	if _stroke_cells.has(cell):
		return
	var f: Field = fields.get(cell)
	if f == null:
		return
	_stroke_cells[cell] = true
	if _mode == Mode.HARVEST and f.harvest():
		_on_harvested(f)
	elif _mode == Mode.PLANT and f.plant():
		Audio.play("plant", 1.0 + 0.05 * mini(_combo, 8))
		_combo += 1
		_puff(f.position + Vector2(0, -20), "fx_leaf", 3)
		hud.hide_hint()


func _tap(world: Vector2) -> void:
	for a in animals:
		if world.distance_to(a.tap_point()) < 60.0:
			a.poke()
			return
	# topmost (front-most) prop first
	var best: Sprite2D = null
	for s in props:
		if s.get_rect().has_point(s.to_local(world)) and _opaque_at(s, world):
			if best == null or s.position.y > best.position.y:
				best = s
	if best != null:
		Field.squash(best, best.get_meta("squash", 0.1))
		Audio.play(best.get_meta("sound", "pop"), 1.0, 0.1)
		var n: String = best.get_meta("sprite", "")
		if n.begins_with("tree") or n.begins_with("bush") or n.begins_with("flowers"):
			_puff(best.position + Vector2(0, -Atlas.anchor(n).y * 0.6), "fx_leaf", 5)


func _opaque_at(s: Sprite2D, world: Vector2) -> bool:
	var at: AtlasTexture = s.texture
	var img: Image = _page_images.get(at.atlas)
	if img == null:
		img = at.atlas.get_image()
		_page_images[at.atlas] = img
	var local := s.to_local(world) - s.offset
	var px := Vector2i(at.region.position + local)
	if not Rect2i(Vector2i(at.region.position), Vector2i(at.region.size)).has_point(px):
		return false
	return img.get_pixelv(px).a > 0.5


func zoom_at(screen_pos: Vector2, factor: float) -> void:
	var before := screen_to_world(screen_pos)
	var z := clampf(cam.zoom.x * factor, ZOOM_MIN, ZOOM_MAX)
	cam.zoom = Vector2(z, z)
	cam.position += before - screen_to_world(screen_pos)
	_clamp_cam()


func _clamp_cam() -> void:
	var c := grid_to_world(Vector2(13, 13))
	cam.position = cam.position.clamp(c - Vector2(2800, 1700), c + Vector2(2800, 1700))


# ------------------------------------------------------------------ juice

func _on_harvested(f: Field) -> void:
	_combo += 1
	var pitch := 1.0 + 0.06 * mini(_combo - 1, 10)
	Audio.play("harvest", pitch, 0.02)
	get_tree().create_timer(0.12).timeout.connect(func() -> void: Audio.play("coin", pitch, 0.0, -5.0))
	Game.add_coins(Field.REWARD)
	Game.add_xp(1)
	_puff(f.position + Vector2(0, -40), "fx_grain", 6)
	_float_reward(f.position + Vector2(0, -90), Field.REWARD)
	hud.hide_hint()


func _puff(pos: Vector2, sprite_name: String, n: int) -> void:
	for i in n:
		var s := Atlas.sprite(sprite_name)
		s.position = pos
		s.rotation = randf_range(-PI, PI)
		fx.add_child(s)
		var dir := Vector2(randf_range(-1.0, 1.0), randf_range(-1.6, -0.5)) * randf_range(50.0, 110.0)
		var tw := s.create_tween().set_parallel(true)
		tw.tween_property(s, "position", pos + dir, 0.55).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		tw.tween_property(s, "rotation", s.rotation + randf_range(-3.0, 3.0), 0.55)
		tw.tween_property(s, "modulate:a", 0.0, 0.3).set_delay(0.3)
		tw.chain().tween_callback(s.queue_free)


func _float_reward(pos: Vector2, amount: int) -> void:
	var n := Node2D.new()
	n.position = pos
	fx.add_child(n)
	var icon := Atlas.sprite("icon_coin")
	icon.centered = true
	icon.offset = Vector2.ZERO
	icon.scale = Vector2(0.42, 0.42)
	icon.position = Vector2(-34, 0)
	n.add_child(icon)
	var l := Label.new()
	l.text = "+%d" % amount
	l.position = Vector2(-4, -34)
	l.add_theme_font_override("font", Game.font_bold)
	l.add_theme_font_size_override("font_size", 52)
	l.add_theme_color_override("font_color", Color("FFF8E6"))
	l.add_theme_color_override("font_outline_color", Color("4A3222"))
	l.add_theme_constant_override("outline_size", 16)
	n.add_child(l)
	n.scale = Vector2(0.4, 0.4)
	var tw := n.create_tween()
	tw.tween_property(n, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(n, "position:y", pos.y - 100.0, 0.9).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(n, "modulate:a", 0.0, 0.35).set_delay(0.6)
	tw.tween_callback(n.queue_free)


# ------------------------------------------------------------------ tools

func _parse_args() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_args[kv[0]] = kv[1] if kv.size() > 1 else ""


func _demo_state() -> void:
	var i := 0
	for f: Field in fields.values():
		f.plant(Field.now() - Field.GROW_TIME * float((i * 7) % 5) / 3.2)
		i += 1


func _take_shot(path: String) -> void:
	await get_tree().create_timer(3.0).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	print("screenshot saved: ", path)
	get_tree().quit()


func _run_smoke() -> void:
	var errors: Array[String] = []
	for n in ["field", "wheat_0", "wheat_3", "barn", "chicken_walk_se_0", "chicken_peck_ne_5", "dino_idle_se_0",
			"tree_oak", "tree_pine", "fence_x", "fence_y", "icon_coin", "icon_emerald", "icon_star", "shadow_blob"]:
		if not Atlas.has(n):
			errors.append("missing sprite " + n)
	for g in [Vector2i(0, 0), Vector2i(5, -3), Vector2i(12, 7)]:
		if cell_at(grid_to_world(Vector2(g)) + Vector2(30, 10)) != g:
			errors.append("cell_at mismatch at %s" % g)
	var f: Field = fields.values()[0]
	if cell_at(f.position) != f.cell:
		errors.append("field cell mismatch")
	if not f.plant(Field.now() - 100.0) or f.state != Field.State.RIPE:
		errors.append("plant/ripen failed")
	var before := Game.coins
	if not f.harvest():
		errors.append("harvest failed")
	_on_harvested(f)
	if Game.coins != before + Field.REWARD:
		errors.append("coins not added")
	TranslationServer.set_locale("de")
	if tr("HINT_START") == "HINT_START":
		errors.append("translations not loaded")
	if errors.is_empty():
		print("SMOKE OK (%d fields, %d props, %d animals, %d atlas pages)" % [
			fields.size(), props.size(), animals.size(), Atlas.pages.size()])
		get_tree().quit(0)
	else:
		for e in errors:
			printerr("SMOKE FAIL: ", e)
		get_tree().quit(1)


func _setup_bench() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for x in range(-4, 26):
		for y in range(17, 32):
			var cell := Vector2i(x, y)
			if occupied.has(cell):
				continue
			if (x + y) % 5 == 0:
				_add_prop("tree_oak" if rng.randf() < 0.6 else "tree_pine", Vector2(cell), _sway_tree)
				occupied[cell] = true
			else:
				_add_field(cell).plant(Field.now() - 100.0)
	var pen := Rect2i(0, 24, 20, 6)
	for i in 40:
		_add_animal("chicken", pen, rng)
	for i in 6:
		_add_animal("dino", pen, rng)
	cam.position = grid_to_world(Vector2(11, 22))
	cam.zoom = Vector2.ONE * ZOOM_MIN
	print("bench: %d fields, %d props, %d animals" % [fields.size(), props.size(), animals.size()])


func _process(delta: float) -> void:
	if not _args.has("bench"):
		return
	_bench_clock += delta
	if _bench_clock < 2.0:
		return
	_bench_times.append(delta * 1000.0)
	if _bench_clock < 12.0:
		return
	var sorted := _bench_times.duplicate()
	sorted.sort()
	var total := 0.0
	for t in sorted:
		total += t
	var avg := total / sorted.size()
	var p99: float = sorted[int(sorted.size() * 0.99)]
	var report := "frames=%d avg=%.2fms (%.0f fps) p99=%.2fms worst=%.2fms renderer=%s gpu=%s" % [
		sorted.size(), avg, 1000.0 / avg, p99, sorted[-1],
		RenderingServer.get_current_rendering_method(), RenderingServer.get_video_adapter_name()]
	print("BENCH ", report)
	var out: String = _args["bench"] if _args["bench"] != "" else "user://bench.txt"
	var file := FileAccess.open(out, FileAccess.WRITE)
	if file:
		file.store_line(report)
	get_tree().quit()
