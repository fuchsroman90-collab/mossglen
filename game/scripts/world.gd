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
const ProductionScript := preload("res://scripts/production.gd")
const SwayShader := preload("res://shaders/sway.gdshader")
const GroundShader := preload("res://shaders/ground.gdshader")
const WeatherScript := preload("res://scripts/weather.gd")

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

const LONG_PRESS := 0.45
const DAY_SECONDS := 20.0 * 60.0

enum Mode { NONE, PAN, PINCH, PLANT, HARVEST, SOW_PENDING, GROW_PENDING, PLACE }

var ground: Polygon2D
var objects: Node2D
var fx: Node2D
var cam: Camera2D
var hud: Hud
var fields: Dictionary = {}  # Vector2i -> Field
var animals: Array[Animal] = []
var production: Dictionary = {}  # building id -> ProductionBuilding
const VILLAGE := {"cafe": Vector2(9.2, -2.4), "market": Vector2(16.4, -2.2), "museum": Vector2(20.4, -3.2),
	"library": Vector2(5.8, -3.0), "lighthouse": Vector2(2.4, -6.4)}
const NPC_SPOTS := {"brumm": Vector2(12.2, 0.4), "lotte": Vector2(11.4, -5.1), "fenna": Vector2(29.8, 8.3),
	"pip": Vector2(15.2, -0.7)}
var _village: Dictionary = {}
var npcs: Dictionary = {}  # id -> Node2D
var _swimmers_root: Node2D
var _dig_sprites: Array[Sprite2D] = []
var _meadow_rect := Rect2i()
var _dig_t := 0.0
var _swimmers: Array[Sprite2D] = []
const POND_CELLS := [Vector2i(3, 18), Vector2i(4, 18), Vector2i(3, 19), Vector2i(4, 19), Vector2i(5, 19),
	Vector2i(4, 20)]
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
var selected_crop := "wheat"
var _press_time := 0.0
var _press_pos := Vector2.ZERO
var _press_field: Field = null
var _picker_field: Field = null
var _no_seed_warned := false
var _placing: Field = null
var _placing_new := false
var _place_cell := Vector2i.ZERO
var _place_from := Vector2i.ZERO
var _daylight: CanvasModulate
var _sky: Gradient
var _day_t := 0.0
var weather: Weather
var _sway_base: Dictionary = {}  ## material -> strength, to restore after "reduce motion"


func _ready() -> void:
	_parse_args()
	_sway_crop = _make_sway(5.0, 1.6, 60.0)
	_sway_tree = _make_sway(5.0, 1.1, 420.0)
	_sway_bush = _make_sway(3.0, 1.4, 120.0)
	_mask = Image.create(MASK_SIZE, MASK_SIZE, false, Image.FORMAT_RGB8)
	objects = Node2D.new()
	objects.y_sort_enabled = true
	fx = Node2D.new()
	fx.z_index = 100
	_build_farm()
	_build_ground()
	_load_world_state.call_deferred()
	add_child(_swimmers_root)
	add_child(objects)
	add_child(fx)
	Game.fish_caught.connect(func(_id: String) -> void: _refresh_swimmers())
	Game.dino_hatched.connect(_on_dino_hatched)
	Game.restored_building.connect(_on_restored)
	_update_digs.call_deferred()
	_refresh_swimmers.call_deferred()
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
	hud.layer = 2
	add_child(hud)
	hud.tutorial.world = self
	hud.shop_pressed.connect(hud.open_shop)
	hud.seed_chosen.connect(_on_seed_chosen)
	hud.buy_field.connect(_on_buy_field)
	hud.place_confirm.connect(_on_place_confirm)
	hud.place_cancel.connect(_on_place_cancel)
	Game.leveled_up.connect(_on_level_up)
	Game.world_saver = _save_world
	_build_daylight()
	_apply_season()
	_update_daylight()
	Game.settings_changed.connect(_apply_motion)
	_apply_motion()

	if _args.has("smoke"):
		_run_smoke.call_deferred()
		return
	if _args.has("bench"):
		_setup_bench()
		return
	if (_args.has("demo") or _args.has("shot")) and not _args.has("tutorial"):
		_demo_state()
	Audio.play_music()
	if _args.has("settings"):
		hud._toggle_settings.call_deferred()
	if _args.has("ui"):
		_debug_ui.call_deferred(str(_args["ui"]))
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
	_mask.set_pixelv(p, Color(maxf(cur.r, amount), cur.g, cur.b))


func _water(cell: Vector2i, amount := 1.0) -> void:
	var p := cell - Vector2i(MAP_MIN, MAP_MIN)
	if p.x < 0 or p.y < 0 or p.x >= MASK_SIZE or p.y >= MASK_SIZE:
		return
	var cur := _mask.get_pixelv(p)
	_mask.set_pixelv(p, Color(cur.r, maxf(cur.g, amount), cur.b))
	occupied[cell] = true


func _moss(cell: Vector2i, amount := 1.0) -> void:
	var p := cell - Vector2i(MAP_MIN, MAP_MIN)
	if p.x < 0 or p.y < 0 or p.x >= MASK_SIZE or p.y >= MASK_SIZE:
		return
	var cur := _mask.get_pixelv(p)
	_mask.set_pixelv(p, Color(cur.r, cur.g, maxf(cur.b, amount)))


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

	# fields: from the save, or the default 4 x 3 block
	var saved: Array = Game.saved_world.get("fields", [])
	if saved.is_empty():
		for x in range(11, 15):
			for y in range(11, 14):
				_add_field(Vector2i(x, y))
	else:
		for d in saved:
			var f := _add_field(Vector2i(int(d["x"]), int(d["y"])))
			if str(d["crop"]) != "" and Game.crops.has(str(d["crop"])):
				f.plant(str(d["crop"]), float(d["t"]))

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
	_meadow_rect = Rect2i(meadow.position + Vector2i(0, 1), meadow.size - Vector2i(1, 1))
	for i in Game.meadow.size():
		_add_animal("dino_" + str(Game.meadow[i]), _meadow_rect, rng,
				Vector2(16.4 + (i % 3) * 1.2, 11.8 + (i / 3) * 1.0 + (i % 2) * 0.4))

	# production buildings on dirt pads
	_add_building("feed_mill", Vector2i(5, 5))
	_add_building("bakery", Vector2i(11, 5))
	_add_building("dairy", Vector2i(17, 17))
	_add_building("jam_kitchen", Vector2i(22, 2))
	_add_building("loom", Vector2i(2, 2))
	_add_building("popcorn", Vector2i(8, 2))
	_add_building("sauce_kitchen", Vector2i(13, 20))
	_add_building("candle_maker", Vector2i(18, 21))
	var hive := _add_building("beehive", Vector2i(7, 12), Vector2i(1, 1))
	hive.position = grid_to_world(Vector2(7.6, 12.4))

	# sheep and pig pens
	var sheep := Rect2i(21, 12, 3, 3)
	_dirt_rect(sheep, 0.45)
	_fence_rect(sheep, Vector2i(sheep.position.x, sheep.end.y))
	for i in 3:
		_add_animal("sheep", sheep, rng, Vector2(21.3 + i * 0.8, 12.6 + (i % 2) * 1.0))
	var pigs := Rect2i(20, 17, 3, 3)
	_dirt_rect(pigs, 0.95)
	_fence_rect(pigs, Vector2i(pigs.position.x + 1, pigs.end.y))
	_add_static("trough", Vector2(21.4, 17.2))
	for i in 2:
		_add_animal("pig", pigs, rng, Vector2(20.5 + i * 1.2, 18.2 + i * 0.5))

	# cow pasture below the fields
	var cows := Rect2i(11, 16, 4, 3)
	_dirt_rect(cows, 0.7)
	_fence_rect(cows, Vector2i(cows.position.x + 2, cows.position.y - 1), true)
	_add_static("trough", Vector2(13.6, 16.3))
	for i in 2:
		_add_animal("cow", cows, rng, Vector2(11.6 + i * 1.6, 17.0 + i * 0.6))

	# order board at the crossroads
	var board := _add_prop("order_board", Vector2(7.6, 7.7), null)
	board.set_meta("squash", 0.06)
	for c in [Vector2i(7, 7), Vector2i(8, 7), Vector2i(8, 8)]:
		occupied[c] = true

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

	# Mossbrook village by the sea in the north
	for x in range(-10, 40):
		for y in range(-10, -6):
			_water(Vector2i(x, y), 1.0 if y < -7 else 0.6)
		_dirt(Vector2i(x, -6), 0.75)
		_dirt(Vector2i(x, -5), 0.35)
	for x in range(-2, 25):
		for y in range(-6, 1):
			occupied[Vector2i(x, y)] = true
	_dirt_rect(Rect2i(7, -3, 12, 3), 0.7)
	for y in range(-1, 9):
		_dirt(Vector2i(13, y), 0.85)
		occupied[Vector2i(13, y)] = true
	_add_static("fountain", Vector2(12.6, -2.2))
	for id in ["cafe", "market", "museum", "library", "lighthouse"]:
		var pos: Vector2 = VILLAGE[id]
		var b := _add_prop(id if Game.restored.has(id) else id + "_ruin", pos, null)
		b.set_meta("village", id)
		b.set_meta("squash", 0.04)
		_village[id] = b
	var pier := _add_prop("dock_sea", Vector2(10.4, -5.8), null)
	pier.set_meta("spot", "sea")
	pier.set_meta("squash", 0.04)
	for spot in [Vector2(5.0, -0.2), Vector2(21.5, -0.5), Vector2(23.4, -3.2), Vector2(15.4, 0.4)]:
		_add_prop("tree_apple" if int(spot.x) % 2 == 0 else "bush_berry", spot, _sway_tree)
	for spot in [Vector2(10.5, 0.2), Vector2(18.6, 0.4), Vector2(6.8, -0.6)]:
		_add_prop("flowers_rose", spot, _sway_bush)
	for id in NPC_SPOTS:
		_add_npc(id, NPC_SPOTS[id])

	# the Primeval Vale beyond the creek
	for x in range(28, 37):
		for y in range(-2, 19):
			var edge := minf(float(x - 28) / 2.0 + 0.3, 1.0)
			_moss(Vector2i(x, y), edge)
			occupied[Vector2i(x, y)] = true
	for x in range(29, 34):
		_dirt(Vector2i(x, 6), 0.8)
	_dirt(Vector2i(33, 7), 0.7)
	_dirt(Vector2i(33, 8), 0.7)
	_add_static("bridge", Vector2(27.5, 6.0))
	_add_static("sign_valley", Vector2(29.3, 7.5))
	var digs := [Vector2(30.2, 3.0), Vector2(32.3, 3.6), Vector2(31.2, 9.2), Vector2(34.5, 4.6), Vector2(30.4, 11.6),
		Vector2(32.6, 11.0)]
	for i in digs.size():
		_dirt(Vector2i(digs[i].round()), 0.55)
		var d := _add_prop("dig_full", digs[i], null)
		d.set_meta("dig", "dig_%d" % i)
		d.set_meta("squash", 0.12)
		_dig_sprites.append(d)
	_add_building("nest", Vector2i(34, 13))
	for spot in [Vector2(29.0, 1.5), Vector2(35.5, 2.5), Vector2(35.8, 8.5), Vector2(29.2, 14.6), Vector2(31.6, 15.8),
			Vector2(35.6, 16.5), Vector2(30.0, 17.5), Vector2(34.4, 0.2)]:
		_add_prop("cycad" if int(spot.x * 10) % 3 == 0 else "cycad_b", spot, _sway_tree)
	for spot in [Vector2(31.0, 1.0), Vector2(33.6, 1.8), Vector2(29.0, 4.4), Vector2(35.4, 6.4), Vector2(31.8, 7.4),
			Vector2(29.4, 9.4), Vector2(35.2, 11.0), Vector2(32.0, 13.4), Vector2(30.0, 14.0), Vector2(33.0, 16.0)]:
		_add_prop("fern_big", spot, _sway_bush)
	for spot in [Vector2(33.5, 9.8), Vector2(29.6, 16.0), Vector2(36.0, 13.5)]:
		_add_prop("rock", spot, null)

	# fishing docks: pond and the creek on the east side
	var d1 := _add_prop("dock_pond", Vector2(7.3, 18.5), null)
	d1.set_meta("spot", "pond")
	d1.set_meta("squash", 0.04)
	for y in range(-9, 37):
		var cx := 26 + int(round(sin(y * 0.33) * 1.3))
		_water(Vector2i(cx, y), 1.0)
		_water(Vector2i(cx + 1, y), 1.0)
		_water(Vector2i(cx - 1, y), 0.45)
		_water(Vector2i(cx + 2, y), 0.45)
	var d2 := _add_prop("dock_creek", Vector2(24.4, 10.0), null)
	d2.set_meta("spot", "river")
	d2.set_meta("squash", 0.04)
	occupied[Vector2i(24, 10)] = true
	_swimmers_root = Node2D.new()

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
	for spot in [Vector2(12, 3.5), Vector2(21.5, 18.5), Vector2(1.5, 5.5), Vector2(15.5, 21.5),
			Vector2(23.5, 9.8)]:
		var cell := Vector2i(spot.round())
		if occupied.has(cell) or occupied.has(Vector2i(spot)):
			continue
		_add_prop("tree_apple", spot, _sway_tree)
		occupied[cell] = true
	for i in 16:
		var cell := Vector2i(rng.randi_range(2, 22), rng.randi_range(3, 21))
		if occupied.has(cell) or cell.y >= 11 and cell.y <= 16 and cell.x >= 2 and cell.x <= 20:
			continue
		var kind: String = ["bush", "rock_small", "flowers_white", "flowers_lavender"][rng.randi() % 4]
		_add_prop(kind, Vector2(cell), null if kind.begins_with("rock") else _sway_bush)
		occupied[cell] = true


func _fence_rect(r: Rect2i, gate: Vector2i, gate_on_top := false) -> void:
	for x in range(r.position.x, r.end.x):
		for y in range(r.position.y, r.end.y):
			occupied[Vector2i(x, y)] = true
	# fence_x runs along grid x, placed on the cell border (y - 0.5)
	for x in range(r.position.x, r.end.x):
		if not (gate_on_top and Vector2i(x, r.position.y - 1) == gate):
			_add_static("fence_x", Vector2(x, r.position.y - 0.5))
		if gate_on_top or Vector2i(x, r.end.y) != gate:
			_add_static("fence_x", Vector2(x, r.end.y - 0.5))
	for y in range(r.position.y, r.end.y):
		_add_static("fence_y", Vector2(r.position.x - 0.5, y))
		_add_static("fence_y", Vector2(r.end.x - 0.5, y))


func _add_building(id: String, cell: Vector2i, size := Vector2i(3, 3)) -> ProductionBuilding:
	var b: ProductionBuilding = ProductionScript.new()
	b.setup(id)
	b.position = grid_to_world(Vector2(cell))
	objects.add_child(b)
	production[id] = b
	var r := Rect2i(cell - size / 2, size)
	if size.x > 1:
		_dirt_rect(r, 0.75)
	for x in range(r.position.x, r.end.x):
		for y in range(r.position.y, r.end.y):
			occupied[Vector2i(x, y)] = true
	return b


func _add_npc(id: String, g: Vector2) -> void:
	var n := Node2D.new()
	n.position = grid_to_world(g)
	n.set_meta("npc", id)
	var sh := Atlas.sprite("shadow_blob")
	sh.scale = Vector2(1.2, 1.1)
	n.add_child(sh)
	var s := Atlas.sprite("npc_%s_0" % id)
	s.name = "Body"
	n.add_child(s)
	var mark := Label.new()
	mark.name = "Mark"
	mark.text = "!"
	mark.add_theme_font_override("font", Game.font_bold)
	mark.add_theme_font_size_override("font_size", 90)
	mark.add_theme_color_override("font_color", Color("FFD23F"))
	mark.add_theme_color_override("font_outline_color", Color("5A3410"))
	mark.add_theme_constant_override("outline_size", 22)
	mark.position = Vector2(-22, -Atlas.anchor("npc_%s_0" % id).y - 130)
	n.add_child(mark)
	n.set_meta("t", randf() * 3.0)
	objects.add_child(n)
	npcs[id] = n


func _update_npcs(delta: float) -> void:
	var q := Game.quest()
	for id in npcs:
		var n: Node2D = npcs[id]
		var t: float = n.get_meta("t") + delta
		n.set_meta("t", t)
		var body: Sprite2D = n.get_node("Body")
		var f := int(t * 5.0) % 6
		var wave := fmod(t, 9.0) < 1.6
		var frame := ("npc_%s_wave_%d" % [id, int(t * 6.0) % 4]) if wave else ("npc_%s_%d" % [id, f])
		if body.get_meta("frame", "") != frame:
			Atlas.apply(body, frame)
			body.set_meta("frame", frame)
		var mark: Label = n.get_node("Mark")
		mark.visible = not q.is_empty() and q["npc"] == id and Game.quest_stage != "active"
		if mark.visible:
			mark.position.y = -Atlas.anchor("npc_%s_0" % id).y - 130 + sin(t * 4.0) * 8.0


func _on_restored(id: String) -> void:
	var b: Sprite2D = _village[id]
	Atlas.apply(b, id)
	b.set_meta("sprite", id)
	Field.squash(b, 0.15)
	_puff(b.position + Vector2(0, -120), "fx_leaf", 12)


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
	if mat == _sway_tree or mat == _sway_bush:
		# per-plant random for the season shader, carried in the blue channel (see sway.gdshader)
		var h := absf(sin(g.x * 12.9898 + g.y * 78.233) * 43758.5453)
		s.self_modulate = Color(1, 1, 0.9 + 0.1 * (h - floorf(h)))
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
	a.pen_id = "dino" if kind.begins_with("dino_") else kind
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
	_press_time = 0.0
	_press_pos = pos
	_stroke_cells.clear()
	_no_seed_warned = false
	if _placing != null:
		_mode = Mode.PLACE
		_move_ghost(pos)
		return
	hud.hide_seed_picker()
	var f: Field = fields.get(cell_at(screen_to_world(pos)))
	_press_field = f
	if f == null:
		_mode = Mode.PAN
	elif f.state == Field.State.RIPE:
		_mode = Mode.HARVEST
		_brush_last = pos
		_brush_at(pos)
	elif f.state == Field.State.EMPTY:
		_mode = Mode.SOW_PENDING
	else:
		_mode = Mode.GROW_PENDING


func _on_drag(event: InputEventScreenDrag) -> void:
	_moved += event.relative.length()
	match _mode:
		Mode.PAN:
			cam.position -= event.relative / cam.zoom.x
			_clamp_cam()
		Mode.PINCH:
			if _touches.size() >= 2:
				var p: Array = _touches.values()
				var d: float = p[0].distance_to(p[1])
				if _pinch_dist > 0.0:
					zoom_at((p[0] + p[1]) * 0.5, d / _pinch_dist)
				_pinch_dist = d
		Mode.PLACE:
			_move_ghost(event.position)
		Mode.SOW_PENDING:
			if _moved > TAP_SLOP:
				_mode = Mode.PLANT
				_brush_last = _press_pos
				_brush_at(_press_pos)
				_brush_stroke(event.position)
		Mode.GROW_PENDING:
			if _moved > TAP_SLOP:
				_mode = Mode.PAN
		Mode.PLANT, Mode.HARVEST:
			_brush_stroke(event.position)


func _brush_stroke(to: Vector2) -> void:
	# interpolate so fast swipes never skip a field
	var from := _brush_last
	var steps := maxi(1, int(from.distance_to(to) / BRUSH_STEP))
	for i in range(1, steps + 1):
		_brush_at(from.lerp(to, float(i) / steps))
	_brush_last = to


func _on_release(pos: Vector2) -> void:
	if _mode == Mode.PINCH:
		_mode = Mode.NONE if _touches.size() < 2 else Mode.PINCH
		return
	if not _touches.is_empty():
		return
	var tap := _moved < TAP_SLOP
	match _mode:
		Mode.PAN:
			if tap:
				_tap(screen_to_world(pos))
		Mode.SOW_PENDING:
			if tap and _press_field != null:
				_picker_field = _press_field
				hud.show_seed_picker(pos, selected_crop)
		Mode.GROW_PENDING:
			if tap and _press_field != null:
				var f := _press_field
				hud.show_field_info(get_viewport().get_canvas_transform() * f.position, f.crop, f.seconds_left(),
						f.progress())
	_mode = Mode.NONE
	_press_field = null


func _check_long_press(delta: float) -> void:
	if _mode != Mode.SOW_PENDING and _mode != Mode.GROW_PENDING:
		return
	_press_time += delta
	if _press_time >= LONG_PRESS and _moved < TAP_SLOP and _press_field != null:
		_start_move(_press_field)
		_mode = Mode.PLACE


func _brush_at(screen_pos: Vector2) -> void:
	var cell := cell_at(screen_to_world(screen_pos))
	if _stroke_cells.has(cell):
		return
	var f: Field = fields.get(cell)
	if f == null:
		return
	_stroke_cells[cell] = true
	if _mode == Mode.HARVEST and f.state == Field.State.RIPE:
		_harvest(f)
	elif (_mode == Mode.PLANT or _mode == Mode.SOW_PENDING) and f.state == Field.State.EMPTY:
		_sow(f, selected_crop)


func _sow(f: Field, crop: String) -> bool:
	if not Game.take_item(crop):
		if not _no_seed_warned:
			_no_seed_warned = true
			Game.toast.emit(tr("NO_SEEDS"), "item_%s.png" % crop)
		return false
	f.plant(crop)
	Game.event("plant", crop)
	Audio.play("plant", 1.0 + 0.05 * mini(_combo, 8))
	_combo += 1
	_puff(f.position + Vector2(0, -20), "fx_leaf", 3)
	hud.hide_hint()
	Game.mark_dirty()
	return true


func _harvest(f: Field) -> void:
	var crop := f.crop
	var amount: int = int(Game.crops[crop]["yield"])
	if Game.space() < amount:
		if not _no_seed_warned:
			_no_seed_warned = true
			Game.toast.emit(tr("BARN_FULL"), "ico_barn.png")
		return
	f.harvest()
	Game.add_item(crop, amount)
	Game.event("harvest", crop, amount)
	_combo += 1
	var pitch := 1.0 + 0.06 * mini(_combo - 1, 10)
	Audio.play("harvest", pitch, 0.02)
	Game.add_xp(int(Game.crops[crop]["xp"]))
	_puff(f.position + Vector2(0, -40), "fx_grain" if crop == "wheat" else "fx_leaf", 6)
	_float_reward(f.position + Vector2(0, -90), amount, "item_%s.png" % crop)
	hud.hide_hint()


## Tapping one animal handles its whole pen: collect what is ready, else feed the hungry ones.
func _animal_tap(a: Animal) -> void:
	var pen: Array[Animal] = []
	for x in animals:
		if x.pen_id == a.pen_id:
			pen.append(x)
	var ready := pen.filter(func(x: Animal) -> bool: return x.is_ready())
	if not ready.is_empty():
		var got := 0
		for x: Animal in ready:
			if Game.space() < 1:
				Game.toast.emit(tr("BARN_FULL"), "ico_barn.png")
				break
			var item := x.collect()
			Game.add_item(item, 1)
			Game.event("collect", item)
			Game.add_xp(int(x.def()["xp"]))
			_float_reward(x.position + Vector2(0, -120), 1, "item_%s.png" % item)
			got += 1
		if got > 0:
			Audio.play("harvest", 1.15)
		return
	var hungry := pen.filter(func(x: Animal) -> bool: return x.is_hungry())
	if not hungry.is_empty():
		var feed: String = a.def()["feed"]
		var fed := 0
		for x: Animal in hungry:
			if not Game.take_item(feed):
				break
			x.feed()
			fed += 1
		if fed == 0:
			Game.toast.emit(tr("NEED_FEED"), "item_%s.png" % feed)
		else:
			_puff(a.position + Vector2(0, -40), "fx_grain", 4)
			Game.event("feed", a.kind, fed)
		return
	var soonest := a
	for x in pen:
		if x.seconds_left() < soonest.seconds_left():
			soonest = x
	a.poke()
	hud.show_field_info(get_viewport().get_canvas_transform() * a.position, a.def()["product"],
			soonest.seconds_left(), soonest.progress())


func _on_seed_chosen(crop: String) -> void:
	selected_crop = crop
	if _picker_field != null and _picker_field.state == Field.State.EMPTY:
		_combo = 0
		_no_seed_warned = false
		if _sow(_picker_field, crop):
			hud.show_hint("HINT_SWIPE")
	_picker_field = null


func _tap(world: Vector2) -> void:
	for id in npcs:
		var n: Node2D = npcs[id]
		if world.distance_to(n.position + Vector2(0, -110)) < 90.0:
			hud.story.talk(id)
			return
	for a in animals:
		if world.distance_to(a.tap_point()) < 70.0:
			if a.produces():
				_animal_tap(a)
			else:
				a.poke()
			return
	# production buildings (front-most first)
	var hit: ProductionBuilding = null
	for b: ProductionBuilding in production.values():
		if b.sprite.get_rect().has_point(b.sprite.to_local(world)) and _opaque_at(b.sprite, world):
			if hit == null or b.position.y > hit.position.y:
				hit = b
	if hit != null and hit.id == "nest" and Game.level < Game.VALLEY_LEVEL:
		Game.toast.emit(tr("VALLEY_LOCKED"), "ico_dino.png")
		return
	if hit != null:
		Field.squash(hit.sprite, 0.05)
		if not hit.done.is_empty():
			var got := hit.collect()
			if got.is_empty():
				Game.toast.emit(tr("BARN_FULL"), "ico_barn.png")
			for g in got:
				Audio.play("harvest", 1.1)
				_float_reward(hit.position + Vector2(0, -Atlas.anchor(hit.id).y * 0.6), g[1], "item_%s.png" % g[0])
		elif hit.is_auto():
			var pr := hit.current_progress()
			hud.show_field_info(get_viewport().get_canvas_transform() * hit.position, "honey", int(pr.x), pr.y)
			Game.toast.emit(tr("BEES_WORK"), "item_honey.png")
		else:
			hud.open_production(hit)
		return
	# topmost (front-most) prop first
	var best: Sprite2D = null
	for s in props:
		if s.get_rect().has_point(s.to_local(world)) and _opaque_at(s, world):
			if best == null or s.position.y > best.position.y:
				best = s
	if best != null:
		Field.squash(best, best.get_meta("squash", 0.1))
		var n: String = best.get_meta("sprite", "")
		if n == "barn":
			hud.open_barn()
			return
		if n == "order_board":
			hud.open_orders()
			return
		if best.has_meta("village"):
			var vid: String = best.get_meta("village")
			if not Game.restored.has(vid):
				hud.story.open_restore(vid)
			else:
				match vid:
					"market":
						hud.story.open_market()
					"museum":
						hud.story.open_museum()
					"library":
						hud.story.open_library()
					"cafe":
						hud.open_orders()
					"lighthouse":
						Audio.play("levelup", 1.4)
			return
		if best.has_meta("spot") and best.get_meta("spot") == "sea" and not Game.restored.has("lighthouse"):
			Game.toast.emit(tr("SEA_LOCKED"), "bobber.png")
			return
		if best.has_meta("dig"):
			if Game.level < Game.VALLEY_LEVEL:
				Game.toast.emit(tr("VALLEY_LOCKED"), "ico_dino.png")
				return
			var found := Game.dig(best.get_meta("dig"))
			if found == "":
				Game.toast.emit(tr("DIG_EMPTY"), "item_fossil.png")
			else:
				Audio.play("dig")
				_puff(best.position + Vector2(0, -30), "fx_grain", 6)
				_float_reward(best.position + Vector2(0, -110), 1, "item_%s.png" % found)
				if found.begins_with("egg_"):
					Audio.play("levelup", 1.2)
					Game.toast.emit(tr("DIG_FOUND") % tr("ITEM_" + found), "item_%s.png" % found)
				_update_digs()
			return
		if best.has_meta("spot"):
			var spot: String = best.get_meta("spot")
			if Game.spot_stock(spot) < 1:
				Game.toast.emit(tr("FISH_EMPTY"), "bobber.png")
			else:
				Game.take_fish(spot)
				hud.start_fishing(spot, spot, time_name())
			return
		Audio.play(best.get_meta("sound", "pop"), 1.0, 0.1)
		if n.begins_with("tree") or n.begins_with("bush") or n.begins_with("flowers"):
			_puff(best.position + Vector2(0, -Atlas.anchor(n).y * 0.6), "fx_leaf", 5)


func _opaque_at(s: Sprite2D, world: Vector2) -> bool:
	var at := s.texture as AtlasTexture
	if at == null:
		return true
	return Atlas.opaque_region(at, s.to_local(world) - s.offset)


func zoom_at(screen_pos: Vector2, factor: float) -> void:
	var before := screen_to_world(screen_pos)
	var z := clampf(cam.zoom.x * factor, ZOOM_MIN, ZOOM_MAX)
	cam.zoom = Vector2(z, z)
	cam.position += before - screen_to_world(screen_pos)
	_clamp_cam()


func _clamp_cam() -> void:
	var c := grid_to_world(Vector2(16, 8))
	cam.position = cam.position.clamp(c - Vector2(3600, 2400), c + Vector2(3600, 2400))


# ------------------------------------------------------------------ build mode

func _on_buy_field() -> void:
	if 12 + Game.extra_fields >= Game.max_fields():
		Game.toast.emit(tr("MAX_FIELDS"), "item_field.png")
		return
	if Game.coins < Game.field_price():
		Game.toast.emit(tr("NOT_ENOUGH_COINS"), "coin.png")
		return
	var f: Field = FieldScript.new()
	f.setup(_sway_crop)
	objects.add_child(f)
	_placing = f
	_placing_new = true
	_place_cell = cell_at(cam.position)
	_update_ghost()
	hud.set_placing(true)


func _start_move(f: Field) -> void:
	_placing = f
	_placing_new = false
	_place_from = f.cell
	_place_cell = f.cell
	fields.erase(f.cell)
	occupied.erase(f.cell)
	Audio.play("pop", 1.2)
	_update_ghost()
	hud.set_placing(true)


func _move_ghost(screen_pos: Vector2) -> void:
	var c := cell_at(screen_to_world(screen_pos))
	if c != _place_cell:
		_place_cell = c
		_update_ghost()


func can_place(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < 24 and c.y < 23 and not occupied.has(c)


func _update_ghost() -> void:
	_placing.cell = _place_cell
	_placing.position = grid_to_world(Vector2(_place_cell))
	_placing.set_ghost(true, can_place(_place_cell))


func _on_place_confirm() -> void:
	if _placing == null:
		return
	if not can_place(_place_cell):
		Audio.play("pop", 0.7)
		Field.squash(_placing, 0.15)
		return
	if _placing_new:
		if not Game.spend_coins(Game.field_price()):
			Game.toast.emit(tr("NOT_ENOUGH_COINS"), "coin.png")
			_on_place_cancel()
			return
		Game.extra_fields += 1
	_finish_place(_place_cell)
	Audio.play("plant", 0.9)


func _on_place_cancel() -> void:
	if _placing == null:
		return
	if _placing_new:
		_placing.queue_free()
		_placing = null
		hud.set_placing(false)
	else:
		_finish_place(_place_from)


func _finish_place(c: Vector2i) -> void:
	var f := _placing
	_placing = null
	f.cell = c
	f.position = grid_to_world(Vector2(c))
	f.set_ghost(false)
	fields[c] = f
	occupied[c] = true
	Field.squash(f, 0.2)
	hud.set_placing(false)
	Game.mark_dirty()


# ------------------------------------------------------------------ day / night

func _build_daylight() -> void:
	_daylight = CanvasModulate.new()
	add_child(_daylight)
	_sky = Gradient.new()
	_sky.offsets = PackedFloat32Array([0.0, 0.18, 0.28, 0.72, 0.82, 0.92, 1.0])
	_sky.colors = PackedColorArray([Color(0.6, 0.66, 0.9), Color(1.0, 0.86, 0.82), Color(1, 1, 1),
		Color(1, 1, 1), Color(1.0, 0.84, 0.7), Color(0.6, 0.66, 0.9), Color(0.6, 0.66, 0.9)])


## 0..1 over one in-game day. Uses wall-clock time so it matches across sessions.
func day_phase() -> float:
	if _args.has("time"):
		return float(_args["time"])
	return fmod(Time.get_unix_time_from_system() / DAY_SECONDS + 0.35, 1.0)


## "day", "dusk" (dawn counts as dusk) or "night" for the fish tables.
func _update_digs() -> void:
	for d in _dig_sprites:
		var full := Game.dig_ready(d.get_meta("dig"))
		var want := "dig_full" if full else "dig_empty"
		if d.get_meta("sprite") != want:
			Atlas.apply(d, want)
			d.set_meta("sprite", want)


func _on_dino_hatched(species: String) -> void:
	var rng := RandomNumberGenerator.new()
	var a := _add_animal("dino_" + species, _meadow_rect, rng,
			Vector2(_meadow_rect.position) + Vector2(1.2, 1.0))
	Audio.play("levelup")
	_puff(a.position + Vector2(0, -60), "fx_leaf", 8)
	Game.toast.emit(tr("DINO_HATCHED") % Game.dino_name(species), "ico_dino.png")


func time_name() -> String:
	var p := day_phase()
	if p >= 0.28 and p < 0.72:
		return "day"
	if (p >= 0.12 and p < 0.28) or (p >= 0.72 and p < 0.88):
		return "dusk"
	return "night"


## Caught species swim in the farm pond as dark shapes under the surface.
func _refresh_swimmers() -> void:
	var ids: Array = Game.fish_log.keys().filter(func(k: String) -> bool:
		return Game.fish_by_id[k]["loc"] == "pond")
	ids = ids.slice(maxi(0, ids.size() - 8))
	while _swimmers.size() < ids.size():
		var s := Sprite2D.new()
		s.modulate = Color(0.12, 0.25, 0.38, 0.55)
		s.scale = Vector2(0.42, 0.42)
		s.position = grid_to_world(Vector2(POND_CELLS[randi() % POND_CELLS.size()]))
		s.set_meta("target", s.position)
		_swimmers_root.add_child(s)
		_swimmers.append(s)
	for i in ids.size():
		_swimmers[i].texture = load("res://art/generated/ui/fish_%s.png" % ids[i])


func _move_swimmers(delta: float) -> void:
	for s in _swimmers:
		var t: Vector2 = s.get_meta("target")
		if s.position.distance_to(t) < 6.0:
			var c: Vector2i = POND_CELLS[randi() % POND_CELLS.size()]
			t = grid_to_world(Vector2(c) + Vector2(randf_range(-0.4, 0.4), randf_range(-0.4, 0.4)))
			s.set_meta("target", t)
		var d := (t - s.position).normalized()
		s.position += d * 40.0 * delta
		s.flip_h = d.x > 0.0


func _update_daylight() -> void:
	_daylight.color = _sky.sample(day_phase())
	if weather:
		weather.set_light(_daylight.color, time_name() == "night")
	Audio.set_area(_music_area())


## Which music loop fits the current view: night everywhere after dark, else by area.
func _music_area() -> String:
	if time_name() == "night":
		return "night"
	var g := world_to_grid(cam.position) if cam else Vector2(11, 11)
	if g.x >= 26.5:
		return "vale"
	if g.y < 1.0 and g.x > 4.0 and g.x < 26.0:
		return "village"
	return "meadow"


# ------------------------------------------------------------------ seasons

func _apply_season() -> void:
	var s := Game.season()
	var gm := ground.material as ShaderMaterial
	var tint := {"spring": Vector3(0.98, 1.04, 0.92), "summer": Vector3(1.04, 1.0, 0.84),
		"autumn": Vector3(1.12, 0.96, 0.7), "winter": Vector3(0.9, 0.96, 0.9)}
	gm.set_shader_parameter("season_tint", tint.get(s, Vector3.ONE))
	gm.set_shader_parameter("snow", 0.78 if s == "winter" else 0.0)
	for m: ShaderMaterial in [_sway_tree, _sway_bush]:
		m.set_shader_parameter("foliage", 1.0)
		m.set_shader_parameter("bloom", 1.0 if s == "spring" else 0.0)
		m.set_shader_parameter("autumn", 0.85 if s == "autumn" else 0.0)
		m.set_shader_parameter("frost", 1.0 if s == "winter" else 0.0)
	weather = WeatherScript.new()
	add_child(weather)
	weather.setup(s)


func _apply_motion() -> void:
	var calm: bool = Game.settings["reduce_motion"]
	for m: ShaderMaterial in [_sway_crop, _sway_tree, _sway_bush]:
		if not _sway_base.has(m):
			_sway_base[m] = m.get_shader_parameter("strength")
		m.set_shader_parameter("strength", 0.0 if calm else _sway_base[m])
	if weather:
		weather.set_motion(not calm)


# ------------------------------------------------------------------ save

func _save_world() -> Dictionary:
	var out: Array = []
	for f: Field in fields.values():
		out.append(f.to_save())
	if _placing != null and not _placing_new:
		var d := _placing.to_save()
		d["x"] = _place_from.x
		d["y"] = _place_from.y
		out.append(d)
	var b := {}
	for id in production:
		b[id] = production[id].to_save()
	var pens := {}
	for a in animals:
		if a.produces():
			if not pens.has(a.pen_id):
				pens[a.pen_id] = []
			pens[a.pen_id].append(a.fed_at)
	return {"fields": out, "buildings": b, "pens": pens}


func _load_world_state() -> void:
	var w: Dictionary = Game.saved_world
	for id in w.get("buildings", {}):
		if production.has(id):
			production[id].load_save(w["buildings"][id])
	var pens: Dictionary = w.get("pens", {})
	var idx := {}
	for a in animals:
		if not a.produces() or not pens.has(a.pen_id):
			continue
		var i: int = idx.get(a.pen_id, 0)
		if i < pens[a.pen_id].size():
			var t := float(pens[a.pen_id][i])
			if t > 0.0:
				a.feed(t)
		idx[a.pen_id] = i + 1


# ------------------------------------------------------------------ juice

func _on_level_up(level: int, unlocked: Array) -> void:
	Audio.play("levelup")
	Game.toast.emit(tr("LEVEL_UP") % level, "star.png")
	for c in unlocked:
		get_tree().create_timer(1.2).timeout.connect(func() -> void:
			Game.toast.emit(tr("NEW_CROP") % tr("ITEM_" + c), "item_%s.png" % c))


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


func _float_reward(pos: Vector2, amount: int, icon_file := "coin.png") -> void:
	var n := Node2D.new()
	n.position = pos
	fx.add_child(n)
	var icon := Sprite2D.new()
	icon.texture = load("res://art/generated/ui/" + icon_file)
	icon.scale = Vector2(0.7, 0.7)
	icon.position = Vector2(-34, 0)
	n.add_child(icon)
	var l := Label.new()
	l.text = "+%d" % amount
	l.position = Vector2(-4, -34)
	l.add_theme_font_override("font", Game.font_bold)
	l.add_theme_font_size_override("font_size", 52)
	l.add_theme_color_override("font_color", Color("FFFFFF"))
	l.add_theme_color_override("font_outline_color", Color("3A2410"))
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
	var now := Time.get_unix_time_from_system()
	for f in Game.fish.slice(0, 6):
		Game.fish_log[f["id"]] = {"n": 1, "best": float(f["size"][0])}
	_refresh_swimmers.call_deferred()
	var k := 0
	for a in animals:
		if a.produces():
			a.feed(now - float(a.def()["time"]) * (1.2 if k % 2 == 0 else 0.4))
			k += 1
	Game.add_item("wheat", 12, true)
	production["bakery"].start(0)
	production["bakery"].queue[0]["end"] = now - 1.0
	production["feed_mill"].start(0)
	var i := 0
	for f: Field in fields.values():
		var crop: String = Game.crop_order[i % Game.crop_order.size()]
		var g := Game.grow_time(crop)
		f.plant(crop, Field.now() - g * float((i * 7) % 5) / 3.2)
		i += 1


## Opens a menu for screenshots: picker, barn, shop, place.
func _debug_ui(which: String) -> void:
	Game.add_item("corn", 4, true)
	Game.add_item("carrot", 3, true)
	Game.level = 3
	match which:
		"picker":
			var f: Field = fields[Vector2i(12, 12)]
			f.harvest()
			f.state = Field.State.EMPTY
			_picker_field = f
			hud.show_seed_picker(get_viewport().get_canvas_transform() * f.position, "corn")
		"barn":
			hud.open_barn()
		"shop":
			hud.open_shop()
		"prod":
			Game.add_item("egg", 3, true)
			hud.open_production(production["bakery"])
		"fish":
			hud.start_fishing("pond", "pond", "day")
		"catch":
			hud.start_fishing("pond", "pond", "day")
			hud.fishing._wait = 0.1
			hud.fishing.set_meta("auto_tap", true)
		"talk":
			hud.story.talk("brumm")
		"restore":
			hud.story.open_restore("cafe")
		"pedia":
			for d in Game.dinos.slice(0, 6):
				Game.dino_seen[d["id"]] = true
			hud.open_dinopedia()
			hud._fill_pedia("trikeri")
		"fest":
			Game.festival_state()["n"] = 170
			Game.festival_state()["claimed"] = 1
			hud.meta.open_festival()
		"ach":
			Game.stats = {"harvest": 1240, "harvest:wheat": 520, "collect": 75, "make": 30, "deliver": 12,
				"catch": 8, "dig": 3, "earn": 4200}
			Game.ach_claimed = {"farmer": 2, "wheat": 1, "rancher": 1, "maker": 0, "level": 3}
			Game.level = 22
			hud.meta.open_achievements()
		"album":
			for f in Game.fish.slice(0, 22):
				Game.record_catch(f["id"], float(f["size"][1]) * 0.8)
			hud.open_album()
			hud._fill_album("moon_carp")
		"orders":
			Game.add_item("egg", 3, true)
			Game.add_item("wheat", 8, true)
			Game.discard(5)
			hud.open_orders()
		"place":
			Game.add_coins(100)
			_on_buy_field()
			_place_cell = Vector2i(15, 12)
			_update_ghost()


func _take_shot(path: String) -> void:
	await get_tree().create_timer(3.0).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	print("screenshot saved: ", path)
	get_tree().quit()


func _run_smoke() -> void:
	var errors: Array[String] = []
	var need := ["field", "barn", "chicken_walk_se_0", "chicken_peck_ne_5", "dino_moosaurus_idle_se_0", "dig_full", "nest", "bridge", "tree_oak",
		"tree_pine", "fence_x", "fence_y", "shadow_blob"]
	for c in Game.crop_order:
		for st in 4:
			need.append("%s_%d" % [c, st])
		if not ResourceLoader.exists("res://art/generated/ui/item_%s.png" % c):
			errors.append("missing ui icon for " + c)
	for n in need:
		if not Atlas.has(n):
			errors.append("missing sprite " + n)
	for g in [Vector2i(0, 0), Vector2i(5, -3), Vector2i(12, 7)]:
		if cell_at(grid_to_world(Vector2(g)) + Vector2(30, 10)) != g:
			errors.append("cell_at mismatch at %s" % g)
	# sow -> ripen -> harvest -> sell
	var f: Field = fields.values()[0]
	var seeds := Game.count("wheat")
	_mode = Mode.PLANT
	if not _sow(f, "wheat") or Game.count("wheat") != seeds - 1:
		errors.append("sowing did not use a seed")
	f.planted_at -= 1000.0
	f._update_stage(false)
	if f.state != Field.State.RIPE:
		errors.append("crop did not ripen")
	_harvest(f)
	if f.state != Field.State.EMPTY or Game.count("wheat") != seeds + 1:
		errors.append("harvest did not add 2 wheat")
	var coins := Game.coins
	if Game.sell("wheat", 1) != 3 or Game.coins != coins + 3:
		errors.append("selling failed")
	# level up unlocks corn with a gift
	Game.add_xp(Game.xp_needed())
	if Game.level < 2 or not Game.is_unlocked("corn") or Game.count("corn") < 2:
		errors.append("level up / unlock failed")
	# buy and place a field, then move it
	Game.add_coins(500)
	var before_fields := fields.size()
	_on_buy_field()
	var free := Vector2i(20, 20)
	while not can_place(free):
		free.x -= 1
	_place_cell = free
	_on_place_confirm()
	if fields.size() != before_fields + 1 or not fields.has(free) or Game.extra_fields != 1:
		errors.append("field placement failed")
	_start_move(fields[free])
	var to := free + Vector2i(-1, 0)
	while not can_place(to):
		to.x -= 1
	_place_cell = to
	_on_place_confirm()
	if not fields.has(to) or fields.has(free):
		errors.append("moving a field failed")
	# save data round trip
	var data: Dictionary = JSON.parse_string(JSON.stringify(_save_world()))
	if data["fields"].size() != fields.size():
		errors.append("save world mismatch")
	_update_daylight()
	TranslationServer.set_locale("de")
	# production: bread from wheat, then collect
	Game.add_item("wheat", 6, true)
	var bakery: ProductionBuilding = production["bakery"]
	if not bakery.start(0):
		errors.append("bakery could not start bread")
	bakery.queue[0]["end"] = Time.get_unix_time_from_system() - 1.0
	bakery.tick()
	var bread_before := Game.count("bread")
	bakery.collect()
	if Game.count("bread") != bread_before + 1:
		errors.append("bakery did not produce bread")
	# animals: feed chickens, ripen, collect eggs via a tap on the pen
	Game.add_item("feed_chicken", 10, true)
	var hen: Animal = null
	for a in animals:
		if a.kind == "chicken":
			hen = a
			break
	_animal_tap(hen)
	if hen.is_hungry():
		errors.append("chicken was not fed")
	for a in animals:
		if a.kind == "chicken" and a.fed_at > 0.0:
			a.fed_at -= 1000.0
	var eggs := Game.count("egg")
	_animal_tap(hen)
	if Game.count("egg") <= eggs:
		errors.append("no eggs collected")
	# orders: deliver a fully stocked order
	Game.ensure_orders()
	for k in Game.orders[0]["need"]:
		Game.add_item(k, int(Game.orders[0]["need"][k]), true)
	var c0 := Game.coins
	if not Game.deliver(0) or Game.coins <= c0:
		errors.append("order delivery failed")
	# bees work on their own
	var hive: ProductionBuilding = production["beehive"]
	if hive.queue.is_empty():
		errors.append("beehive did not start by itself")
	for name in ["jam_kitchen", "loom", "popcorn", "sauce_kitchen", "candle_maker"]:
		if not production.has(name):
			errors.append("missing building " + name)
	var kinds := {}
	for a in animals:
		kinds[a.kind] = true
	for k in ["chicken", "cow", "sheep", "pig", "dino_moosaurus"]:
		if not kinds.has(k):
			errors.append("missing animal " + k)
	# fishing: stock, roll, record, album
	var st := Game.spot_stock("pond")
	if st < 1 or not Game.take_fish("pond") or Game.spot_stock("pond") != st - 1:
		errors.append("fishing spot stock broken")
	var got := Game.roll_fish("pond", "day", 1.0)
	if not Game.fish_by_id.has(got["id"]) or Game.fish_by_id[got["id"]]["loc"] != "pond":
		errors.append("rolled a fish from the wrong place")
	var rc := Game.record_catch(got["id"], got["size"])
	if not rc["new"] or not Game.fish_log.has(got["id"]):
		errors.append("catch not recorded")
	for loc in ["pond", "river"]:
		for tn in ["day", "dusk", "night"]:
			Game.roll_fish(loc, tn, 0.5)
	hud.start_fishing("river", "river", "night")
	if hud.fishing == null:
		errors.append("fishing overlay did not open")
	# dinos: dig in the vale, hatch an egg in the nest, it joins the meadow
	Game.level = maxi(Game.level, Game.VALLEY_LEVEL)
	Game.digs.clear()
	var found := Game.dig("dig_0")
	if found == "" or Game.dig("dig_0") != "":
		errors.append("digging broken")
	Game.add_item("egg_trikeri", 1, true)
	var nest: ProductionBuilding = production["nest"]
	var r_idx := -1
	for i in nest.recipes().size():
		if nest.recipes()[i]["out"] == "dino_trikeri":
			r_idx = i
	var dinos_before := animals.size()
	if not nest.start(r_idx):
		errors.append("nest could not start")
	nest.queue[0]["end"] = Time.get_unix_time_from_system() - 1.0
	nest.tick()
	nest.collect()
	if animals.size() != dinos_before + 1 or not Game.dino_seen.has("trikeri"):
		errors.append("hatching did not add a dino")
	hud.open_dinopedia()
	# story: talk to Brumm, harvest wheat, claim the reward
	Game.quest_index = 0
	Game.quest_stage = "intro"
	if Game.talk("brumm").is_empty() or Game.quest_stage != "active":
		errors.append("quest intro failed")
	Game.event("harvest", "wheat", 6)
	var lvl_coins := Game.coins
	if Game.quest_stage != "ready" or Game.talk("brumm").is_empty() or Game.quest_index != 1 \
			or Game.coins <= lvl_coins:
		errors.append("quest completion failed")
	hud.story.talk("brumm")
	# restore the lighthouse
	Game.level = maxi(Game.level, 5)
	Game.add_item("candle", 2, true)
	Game.add_item("cloth", 1, true)
	Game.add_coins(1000)
	if not Game.restore("lighthouse") or _village["lighthouse"].get_meta("sprite") != "lighthouse":
		errors.append("restoring the lighthouse failed")
	if Game.order_slots() != Game.ORDER_SLOTS:
		errors.append("order slots wrong before the cafe")
	var ws := _save_world()
	if not ws.has("buildings") or not ws["pens"].has("chicken"):
		errors.append("production state not saved")
	if tr("HINT_START") == "HINT_START" or tr("ITEM_corn") != "Mais":
		errors.append("translations not loaded")
	# M9: seasons
	for se in Game.SEASONS:
		Game.season_override = se
		var bonus := 0
		for c in Game.crop_order:
			if Game.in_season(c):
				bonus += 1
				if Game.grow_time(c) >= float(Game.crops[c]["grow"]):
					errors.append("season bonus missing for " + c)
		if bonus == 0:
			errors.append("no crop in season " + se)
	Game.season_override = ""
	if not Game.season() in Game.SEASONS:
		errors.append("calendar season unknown")
	# M9: achievements - stats count, a reached tier can be claimed once
	var gems_before := Game.emeralds
	Game.event("deliver", "any", 10)
	var orders_ach: Dictionary = Game.achievements.filter(func(a: Dictionary) -> bool:
		return a["id"] == "orders")[0]
	if not Game.ach_claimable(orders_ach) or Game.claim_achievement("orders") <= 0 \
			or Game.emeralds <= gems_before or Game.ach_claimable(orders_ach):
		errors.append("achievement claim failed")
	hud.meta.open_achievements()
	if hud.meta._ach_list.get_child_count() != Game.achievements.size():
		errors.append("achievement list incomplete")
	# M9: seasonal festival counts matching events and pays out each stage once
	var fd := Game.festival_def()
	var coins_f := Game.coins
	Game.event(fd["type"], fd["id"] if fd["id"] != "any" else "wheat", int(fd["tiers"][0]))
	if not Game.festival_claimable() or Game.claim_festival().is_empty() or Game.coins <= coins_f \
			or Game.festival_claimable():
		errors.append("festival stage failed")
	hud.meta.open_festival()
	# M9: settings
	hud.meta.toggle_settings()
	Game.set_setting("text", 1.3)
	if absf(hud._root.scale.x - 0.65) > 0.001:
		errors.append("interface size not applied")
	Game.set_setting("text", 1.0)
	Game.set_setting("reduce_motion", true)
	if float(_sway_tree.get_shader_parameter("strength")) != 0.0 or weather.visible:
		errors.append("reduce motion not applied")
	Game.set_setting("reduce_motion", false)
	hud.close_menus()
	# M9: tutorial runs through all steps on game events
	hud.tutorial.restart()
	Game.event("plant", "wheat")
	Game.event("feed", "chicken")
	Game.event("harvest", "wheat")
	hud.open_orders()
	hud.close_menus()
	Game.quest_index = 0
	Game.quest_stage = "intro"
	Game.talk("brumm")
	if Game.tutorial_step != -1:
		errors.append("tutorial stuck at step %d" % Game.tutorial_step)
	# M9: music loops exist and can be switched
	Audio.play_music("meadow")
	Audio._crossfade("vale")
	if Audio.track != "vale" or Audio._songs.size() != 4:
		errors.append("music switch failed")
	if errors.is_empty():
		print("SMOKE OK (%d fields, %d props, %d animals, %d atlas pages, level %d)" % [
			fields.size(), props.size(), animals.size(), Atlas.pages.size(), Game.level])
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
				_add_field(cell).plant(Game.crop_order[(x * 3 + y) % 5], Field.now() - 5000.0)
	var pen := Rect2i(0, 24, 20, 6)
	for i in 40:
		_add_animal("chicken", pen, rng)
	for i in 6:
		_add_animal("dino", pen, rng)
	cam.position = grid_to_world(Vector2(11, 22))
	cam.zoom = Vector2.ONE * ZOOM_MIN
	print("bench: %d fields, %d props, %d animals" % [fields.size(), props.size(), animals.size()])


func _process(delta: float) -> void:
	_check_long_press(delta)
	_move_swimmers(delta)
	_update_npcs(delta)
	_dig_t += delta
	if _dig_t > 1.0:
		_dig_t = 0.0
		_update_digs()
	_day_t += delta
	if _day_t > 1.0:
		_day_t = 0.0
		_update_daylight()
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
