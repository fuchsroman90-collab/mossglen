extends Node2D
## M0 test farm: ground, fields, barn, nature, chickens, camera and touch input.
##
## Command line (after "--"):
##   --smoke        run self checks headless and quit with exit code 0/1
##   --bench[=file] stress scene, vsync off, prints frame time stats and quits
##   --demo         fields start in mixed growth stages
##   --shot=file    save a screenshot after 2.5 s and quit (implies --demo)

const HudScript := preload("res://scripts/hud.gd")
const FieldScript := preload("res://scripts/field.gd")
const ChickenScript := preload("res://scripts/chicken.gd")
const SwayShader := preload("res://shaders/sway.gdshader")

const MAP_MIN := -10
const MAP_MAX := 36
const ZOOM_MIN := 0.45
const ZOOM_MAX := 1.6
const TAP_SLOP := 14.0
const BRUSH_STEP := 18.0

enum Mode { NONE, PAN, PINCH, PLANT, HARVEST }

var ground: TileMapLayer
var objects: Node2D
var fx: Node2D
var cam: Camera2D
var hud: Hud
var fields: Dictionary = {}  # Vector2i -> Field
var chickens: Array[Chicken] = []
var props: Array[Sprite2D] = []  # tappable scenery (barn, trees, bushes)
var occupied: Dictionary = {}

var _sway_crop: ShaderMaterial
var _sway_tree: ShaderMaterial
var _tile_index: Dictionary = {}
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
var _atlas_image: Image


func _ready() -> void:
	_parse_args()
	_sway_crop = _make_sway(2.2, 1.6, 30.0)
	_sway_tree = _make_sway(3.0, 1.1, 200.0)
	_build_ground()
	objects = Node2D.new()
	objects.y_sort_enabled = true
	add_child(objects)
	fx = Node2D.new()
	fx.z_index = 100
	add_child(fx)
	_build_farm()
	cam = Camera2D.new()
	add_child(cam)
	cam.make_current()
	cam.position = grid_to_world(Vector2(13, 9))
	cam.zoom = Vector2.ONE * 0.75
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
	return ground.map_to_local(Vector2i.ZERO) + Vector2((g.x - g.y) * 64.0, (g.x + g.y) * 32.0)


func cell_at(world: Vector2) -> Vector2i:
	return ground.local_to_map(world)


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


func _build_ground() -> void:
	var info: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/generated/ground.json"))
	var names: Array = info["tiles"]
	var ts := TileSet.new()
	ts.tile_shape = TileSet.TILE_SHAPE_ISOMETRIC
	ts.tile_layout = TileSet.TILE_LAYOUT_DIAMOND_DOWN
	ts.tile_size = Vector2i(128, 64)
	var src := TileSetAtlasSource.new()
	src.texture = load("res://art/generated/ground.png")
	src.texture_region_size = Vector2i(int(info["cell"][0]), int(info["cell"][1]))
	for i in names.size():
		src.create_tile(Vector2i(i, 0))
		_tile_index[names[i]] = i
	ts.add_source(src, 0)
	ground = TileMapLayer.new()
	ground.tile_set = ts
	add_child(ground)
	for x in range(MAP_MIN, MAP_MAX):
		for y in range(MAP_MIN, MAP_MAX):
			_set_ground(Vector2i(x, y), "grass")


func _set_ground(cell: Vector2i, kind: String) -> void:
	var h := absi(hash(cell)) % 100
	var tile_name: String
	if kind == "path":
		tile_name = "path_1" if h < 30 else "path_0"
	else:
		tile_name = "grass_0" if h < 50 else "grass_1" if h < 75 else "grass_2" if h < 87 else "grass_3"
	ground.set_cell(cell, 0, Vector2i(_tile_index[tile_name], 0))


func _build_farm() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 42

	# paths
	for x in range(3, 23):
		_set_ground(Vector2i(x, 9), "path")
		occupied[Vector2i(x, 9)] = true
	for y in range(10, 21):
		_set_ground(Vector2i(9, y), "path")
		occupied[Vector2i(9, y)] = true

	# fields 4 x 3
	for x in range(11, 15):
		for y in range(11, 14):
			_add_field(Vector2i(x, y))

	# barn (footprint ~3x3 around grid 16,5)
	var barn := _add_prop("barn", Vector2(16, 5), null)
	for x in range(14, 19):
		for y in range(3, 8):
			occupied[Vector2i(x, y)] = true
	barn.set_meta("squash", 0.05)

	# chicken pen with fences and a gate
	var pen := Rect2i(3, 12, 4, 4)
	for x in range(pen.position.x, pen.end.x):
		for y in range(pen.position.y, pen.end.y):
			occupied[Vector2i(x, y)] = true
		_add_fence("fence_x", Vector2(x, pen.position.y - 0.5))
		if x != pen.position.x + 1:
			_add_fence("fence_x", Vector2(x, pen.end.y - 0.5))
	for y in range(pen.position.y, pen.end.y):
		_add_fence("fence_y", Vector2(pen.position.x - 0.5, y))
		_add_fence("fence_y", Vector2(pen.end.x - 0.5, y))
	for i in 4:
		_add_chicken(pen, rng)

	# trees and scenery around the farm
	var inner := Rect2i(1, 2, 22, 20)
	var tries := 0
	var placed := 0
	while placed < 90 and tries < 2000:
		tries += 1
		var cell := Vector2i(rng.randi_range(MAP_MIN + 2, MAP_MAX - 3), rng.randi_range(MAP_MIN + 2, MAP_MAX - 3))
		if inner.has_point(cell) or occupied.has(cell):
			continue
		var r := rng.randf()
		var kind := "tree_oak" if r < 0.45 else "tree_pine" if r < 0.8 else "tree_apple" if r < 0.88 else "bush"
		_add_prop(kind, Vector2(cell) + Vector2(rng.randf_range(-0.2, 0.2), rng.randf_range(-0.2, 0.2)), _sway_tree)
		occupied[cell] = true
		placed += 1
	for spot in [Vector2(20, 4), Vector2(12, 4), Vector2(19, 15), Vector2(21, 18)]:
		_add_prop("tree_apple", spot, _sway_tree)
		occupied[Vector2i(spot)] = true
	for i in 14:
		var cell := Vector2i(rng.randi_range(2, 22), rng.randi_range(3, 21))
		if occupied.has(cell):
			continue
		var kind: String = ["bush", "bush_berry", "rock"][rng.randi() % 3]
		_add_prop(kind, Vector2(cell), _sway_crop if kind != "rock" else null)
		occupied[cell] = true


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
	var s := Atlas.sprite(sprite_name)
	s.position = grid_to_world(g)
	s.material = mat
	s.set_meta("squash", 0.1)
	objects.add_child(s)
	props.append(s)
	return s


func _add_fence(sprite_name: String, g: Vector2) -> void:
	var s := Atlas.sprite(sprite_name)
	s.position = grid_to_world(g)
	objects.add_child(s)


func _add_chicken(pen: Rect2i, rng: RandomNumberGenerator) -> void:
	var c: Chicken = ChickenScript.new()
	var pick := func() -> Vector2:
		return grid_to_world(Vector2(randf_range(pen.position.x - 0.25, pen.end.x - 0.75),
				randf_range(pen.position.y - 0.25, pen.end.y - 0.75)))
	c.random_point = pick
	c.position = grid_to_world(Vector2(pen.position) + Vector2(rng.randf_range(0, 3), rng.randf_range(0, 3)))
	objects.add_child(c)
	chickens.append(c)


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
		_puff(f.position + Vector2(0, -8), "fx_leaf", 3)
		hud.hide_hint()


func _tap(world: Vector2) -> void:
	for c in chickens:
		if world.distance_to(c.position + Vector2(0, -22)) < 28.0:
			c.poke()
			return
	# topmost (front-most) prop first
	var best: Sprite2D = null
	for s in props:
		if s.get_rect().has_point(s.to_local(world)) and _opaque_at(s, world):
			if best == null or s.position.y > best.position.y:
				best = s
	if best != null:
		Field.squash(best, best.get_meta("squash", 0.1))
		Audio.play("pop" if best.texture != Atlas.tex("barn") else "whoosh", 1.0, 0.1)
		if best.texture != Atlas.tex("barn") and best.texture != Atlas.tex("rock"):
			_puff(best.position + Vector2(0, -60), "fx_leaf", 4)


func _opaque_at(s: Sprite2D, world: Vector2) -> bool:
	var at: AtlasTexture = s.texture
	var img := at.atlas.get_image() if _atlas_image == null else _atlas_image
	_atlas_image = img
	var local := s.to_local(world) - s.offset
	var px := Vector2i(at.region.position + local)
	if not Rect2i(Vector2i(at.region.position), Vector2i(at.region.size)).has_point(px):
		return false
	return img.get_pixelv(px).a > 0.3


func zoom_at(screen_pos: Vector2, factor: float) -> void:
	var before := screen_to_world(screen_pos)
	var z := clampf(cam.zoom.x * factor, ZOOM_MIN, ZOOM_MAX)
	cam.zoom = Vector2(z, z)
	cam.position += before - screen_to_world(screen_pos)
	_clamp_cam()


func _clamp_cam() -> void:
	var c := grid_to_world(Vector2(13, 13))
	cam.position = cam.position.clamp(c - Vector2(1300, 750), c + Vector2(1300, 750))


# ------------------------------------------------------------------ juice

func _on_harvested(f: Field) -> void:
	_combo += 1
	var pitch := 1.0 + 0.06 * mini(_combo - 1, 10)
	Audio.play("harvest", pitch, 0.02)
	get_tree().create_timer(0.12).timeout.connect(func() -> void: Audio.play("coin", pitch, 0.0, -5.0))
	Game.add_coins(Field.REWARD)
	_puff(f.position + Vector2(0, -16), "fx_grain", 5)
	_float_reward(f.position + Vector2(0, -36), Field.REWARD)
	hud.hide_hint()


func _puff(pos: Vector2, sprite_name: String, n: int) -> void:
	for i in n:
		var s := Atlas.sprite(sprite_name)
		s.position = pos
		s.rotation = randf_range(-PI, PI)
		fx.add_child(s)
		var dir := Vector2(randf_range(-1.0, 1.0), randf_range(-1.6, -0.5)) * randf_range(25.0, 55.0)
		var tw := s.create_tween().set_parallel(true)
		tw.tween_property(s, "position", pos + dir, 0.55).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		tw.tween_property(s, "rotation", s.rotation + randf_range(-3.0, 3.0), 0.55)
		tw.tween_property(s, "modulate:a", 0.0, 0.3).set_delay(0.3)
		tw.chain().tween_callback(s.queue_free)


func _float_reward(pos: Vector2, amount: int) -> void:
	var n := Node2D.new()
	n.position = pos
	fx.add_child(n)
	var icon := Sprite2D.new()
	icon.texture = Atlas.tex("icon_coin")
	icon.scale = Vector2(0.55, 0.55)
	icon.position = Vector2(-14, 0)
	n.add_child(icon)
	var l := Label.new()
	l.text = "+%d" % amount
	l.position = Vector2(-1, -18)
	l.add_theme_font_size_override("font_size", 26)
	l.add_theme_color_override("font_color", Color("FFF4DC"))
	l.add_theme_color_override("font_outline_color", Color("4A3A2E"))
	l.add_theme_constant_override("outline_size", 8)
	n.add_child(l)
	n.scale = Vector2(0.4, 0.4)
	var tw := n.create_tween()
	tw.tween_property(n, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(n, "position:y", pos.y - 50.0, 0.9).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
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
		f.plant(Field.now() - Field.GROW_TIME * float(i % 5) / 3.5)
		i += 1


func _take_shot(path: String) -> void:
	await get_tree().create_timer(2.5).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	print("screenshot saved: ", path)
	get_tree().quit()


func _run_smoke() -> void:
	var errors: Array[String] = []
	for n in ["field", "wheat_0", "wheat_3", "barn", "chicken_0", "chicken_1", "tree_oak", "fence_x", "icon_coin"]:
		if not Atlas.has(n):
			errors.append("missing sprite " + n)
	var step := ground.map_to_local(Vector2i(1, 0)) - ground.map_to_local(Vector2i.ZERO)
	if not step.is_equal_approx(Vector2(64, 32)):
		errors.append("unexpected iso step %s" % step)
	var f: Field = fields.values()[0]
	if cell_at(f.position) != f.cell:
		errors.append("cell_at mismatch")
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
		print("SMOKE OK (%d fields, %d props, %d chickens)" % [fields.size(), props.size(), chickens.size()])
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
	var count := 0
	for x in range(-4, 26):
		for y in range(14, 30):
			var cell := Vector2i(x, y)
			if occupied.has(cell):
				continue
			if (x + y) % 5 == 0:
				_add_prop("tree_oak" if rng.randf() < 0.6 else "tree_pine", Vector2(cell), _sway_tree)
				occupied[cell] = true
			else:
				_add_field(cell).plant(Field.now() - 100.0)
			count += 1
	var pen := Rect2i(0, 22, 20, 6)
	for i in 40:
		_add_chicken(pen, rng)
	cam.position = grid_to_world(Vector2(11, 20))
	cam.zoom = Vector2.ONE * ZOOM_MIN
	print("bench: %d fields, %d props, %d chickens" % [fields.size(), props.size(), chickens.size()])


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
