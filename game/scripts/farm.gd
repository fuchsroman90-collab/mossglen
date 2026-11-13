class_name Farm
extends Node
## M9.5 progression: land parcels, obstacles, placeable buildings/pens with a construction phase,
## and the delivery truck at the order board. Owned by the world; uses the world's sprite helpers.

## Parcel grid inside the farm area (x 0..23, y 1..22). Boundaries of columns / rows in grid cells.
const COLS := [0, 4, 8, 14, 20, 24]
const ROWS := [1, 3, 9, 14, 18, 23]
const START := ["p2_1", "p3_1", "p2_2", "p3_2"]
## Fixed buildings of a new farm (cell = sprite anchor cell)
const FIXED := {"farmhouse": Vector2i(9, 5), "barn": Vector2i(16, 5), "silo": Vector2i(12, 4),
	"order_board": Vector2i(12, 7)}
const START_FIELDS := [Vector2i(11, 11), Vector2i(12, 11), Vector2i(13, 11)]
## Obstacle sprite -> tool that clears it
const OBSTACLES := {"tree_oak": "axe", "tree_oak_b": "axe", "tree_autumn": "axe", "tree_pine": "saw",
	"tree_pine_b": "saw", "rock": "dynamite", "rock_small": "dynamite", "bush": "shovel", "bush_berry": "shovel"}
const TRUCK_PARK := Vector2(14.3, 8.1)
## Truck route: parking -> up the village road -> out of sight behind the village
const TRUCK_ROUTE := [Vector2(14.3, 8.1), Vector2(13.4, 8.4), Vector2(13.4, 1.0), Vector2(13.4, -1.6)]

var w: Node  ## world.gd
var obstacles: Dictionary = {}  ## "x,y" -> Sprite2D
var signs: Dictionary = {}  ## parcel id -> Sprite2D
var sites: Dictionary = {}  ## index in Game.placed -> Sprite2D (construction site)
var fixed: Dictionary = {}  ## kind -> Sprite2D
var truck: Sprite2D
var _truck_crate: Sprite2D
var _silo_level_shown := -1


func setup(world: Node) -> void:
	w = world
	if Game.placed.is_empty():
		_new_farm()


# ------------------------------------------------------------------ geometry

static func parcel_id(c: int, r: int) -> String:
	return "p%d_%d" % [c, r]


static func parcel_rect(id: String) -> Rect2i:
	var p := id.substr(1).split("_")
	var c := int(p[0])
	var r := int(p[1])
	return Rect2i(COLS[c], ROWS[r], COLS[c + 1] - COLS[c], ROWS[r + 1] - ROWS[r])


static func parcel_at(cell: Vector2i) -> String:
	for c in COLS.size() - 1:
		for r in ROWS.size() - 1:
			if cell.x >= COLS[c] and cell.x < COLS[c + 1] and cell.y >= ROWS[r] and cell.y < ROWS[r + 1]:
				return parcel_id(c, r)
	return ""


static func all_parcels() -> Array:
	var out := []
	for c in COLS.size() - 1:
		for r in ROWS.size() - 1:
			out.append(parcel_id(c, r))
	return out


## Rings away from the start area: 1 next to it, 2 at the corners/edges.
static func parcel_ring(id: String) -> int:
	var p := id.substr(1).split("_")
	var c := int(p[0])
	var r := int(p[1])
	return maxi(maxi(2 - c, c - 3), maxi(maxi(1 - r, r - 2), 0)) if not id in START else 0


static func parcel_cost(id: String) -> Dictionary:
	var ring := parcel_ring(id)
	return {"coins": 150 * ring * ring + 100, "items": ring, "level": 3 if ring == 1 else 7}


static func is_open_parcel(id: String) -> bool:
	return id in START or Game.land.has(id)


## True if the cell is on opened land (or outside the farm area, where nothing can be built anyway).
static func cell_open(cell: Vector2i) -> bool:
	var id := parcel_at(cell)
	return id != "" and is_open_parcel(id)


static func hash01(cell: Vector2i, salt: float) -> float:
	var h := sin(cell.x * 127.1 + cell.y * 311.7 + salt * 74.7) * 43758.5453
	return h - floorf(h)


# ------------------------------------------------------------------ new farm

func _new_farm() -> void:
	for k in FIXED:
		var c: Vector2i = FIXED[k]
		Game.placed.append({"k": k, "x": c.x, "y": c.y, "done": 0.0})
	for c: Vector2i in START_FIELDS:
		Game.placed.append({"k": "field", "x": c.x, "y": c.y, "done": 0.0})
	Game.mark_dirty()


## Footprint of a placed thing (cells it blocks).
static func footprint(kind: String, cell: Vector2i) -> Rect2i:
	if kind == "field":
		return Rect2i(cell, Vector2i.ONE)
	var d: Dictionary = Game.placeables.get(kind, {})
	var size := Vector2i(int(d.get("size", [1, 1])[0]), int(d.get("size", [1, 1])[1]))
	if kind == "barn":
		return Rect2i(cell - Vector2i(2, 2), Vector2i(6, 5))
	return Rect2i(cell - size / 2, size)


# ------------------------------------------------------------------ building the farm

## Reserves cells used by placed things, then places obstacles and parcel signs.
func build_land(occupied: Dictionary) -> void:
	for p in Game.placed:
		var r := footprint(p["k"], Vector2i(int(p["x"]), int(p["y"])))
		for x in range(r.position.x, r.end.x):
			for y in range(r.position.y, r.end.y):
				occupied[Vector2i(x, y)] = true
	# keep the truck's parking spot and the road free
	for c in [Vector2i(14, 8), Vector2i(15, 8), Vector2i(13, 8)]:
		occupied[c] = true
	for x in range(COLS[0], COLS[COLS.size() - 1]):
		for y in range(ROWS[0], ROWS[ROWS.size() - 1]):
			var cell := Vector2i(x, y)
			if occupied.has(cell) or Game.cleared.has(_key(cell)):
				continue
			var id := parcel_at(cell)
			var density := 0.07 if id in START else 0.2
			if hash01(cell, 1.0) >= density:
				continue
			var r := hash01(cell, 2.0)
			var kind: String
			if r < 0.3:
				kind = "tree_oak" if r < 0.18 else "tree_oak_b"
			elif r < 0.5:
				kind = "tree_pine" if r < 0.4 else "tree_pine_b"
			elif r < 0.7:
				kind = "rock" if r < 0.58 else "rock_small"
			else:
				kind = "bush" if r < 0.85 else "bush_berry"
			var off := Vector2(hash01(cell, 3.0) - 0.5, hash01(cell, 4.0) - 0.5) * 0.3
			var mat: Material = null if kind.begins_with("rock") else (w._sway_tree if kind.begins_with("tree") else w._sway_bush)
			var s: Sprite2D = w._add_prop(kind, Vector2(cell) + off, mat)
			s.set_meta("obstacle", _key(cell))
			s.set_meta("tool", OBSTACLES[kind])
			s.set_meta("squash", 0.06)
			obstacles[_key(cell)] = s
			occupied[cell] = true
	_place_signs()


## Ground mask for the shader: 1 on own land and outside the farm, 0 on locked parcels.
func land_texture() -> ImageTexture:
	var img := Image.create(w.MASK_SIZE, w.MASK_SIZE, false, Image.FORMAT_L8)
	img.fill(Color.WHITE)
	for id in all_parcels():
		if is_open_parcel(id):
			continue
		var r := parcel_rect(id)
		for x in range(r.position.x, r.end.x):
			for y in range(r.position.y, r.end.y):
				img.set_pixel(x - w.MAP_MIN, y - w.MAP_MIN, Color.BLACK)
	return ImageTexture.create_from_image(img)


## A locked parcel is offered for sale once it touches your land.
static func on_frontier(id: String) -> bool:
	var p := id.substr(1).split("_")
	var c := int(p[0])
	var r := int(p[1])
	for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
		var n: Vector2i = Vector2i(c, r) + d
		if n.x < 0 or n.y < 0 or n.x >= COLS.size() - 1 or n.y >= ROWS.size() - 1:
			continue
		if is_open_parcel(parcel_id(n.x, n.y)):
			return true
	return false


func _place_signs() -> void:
	for s in signs.values():
		w.props.erase(s)
		s.queue_free()
	signs.clear()
	if w.ground:
		(w.ground.material as ShaderMaterial).set_shader_parameter("land_tex", land_texture())
	for id in all_parcels():
		if is_open_parcel(id) or not on_frontier(id):
			continue
		var r := parcel_rect(id)
		var s: Sprite2D = w._add_prop("sign_parcel", Vector2(r.position) + Vector2(r.size) * 0.5 - Vector2(0.5, 0.5), null)
		s.set_meta("parcel", id)
		s.set_meta("squash", 0.1)
		s.z_index = 1
		signs[id] = s
	_shade_locked()


## Locked land is drawn a little darker and greyer, so the open farm reads at a glance.
func _shade_locked() -> void:
	for o: Sprite2D in obstacles.values():
		var id := parcel_at(w.cell_at(o.position))
		var c := o.self_modulate
		var k := 1.0 if is_open_parcel(id) else 0.82
		o.modulate = Color(k, k, k * 1.02)
		o.self_modulate = c


func _key(cell: Vector2i) -> String:
	return "%d,%d" % [cell.x, cell.y]


## Spawns everything in Game.placed (fields are created by the world itself).
func spawn_placed() -> void:
	for i in Game.placed.size():
		var p: Dictionary = Game.placed[i]
		var k: String = p["k"]
		if k == "field":
			continue
		var cell := Vector2i(int(p["x"]), int(p["y"]))
		if float(p.get("done", 0.0)) > 0.0:
			_add_site(i)
			continue
		_spawn(k, cell, p)


func _spawn(k: String, cell: Vector2i, p: Dictionary) -> void:
	var d: Dictionary = Game.placeables.get(k, {})
	if d.get("fixed", false):
		var spr: String = "silo_%d" % mini(Game.silo_level, 3) if k == "silo" else str(d["sprite"])
		var s: Sprite2D = w._add_prop(spr, Vector2(cell), null)
		s.set_meta("squash", 0.04)
		s.set_meta("fixed", k)
		fixed[k] = s
		if k == "barn":
			w._dirt_rect(Rect2i(14, 3, 6, 5))
		elif k == "order_board":
			_spawn_truck()
		return
	if d.get("building", false):
		var size := Vector2i(int(d["size"][0]), int(d["size"][1]))
		var b: ProductionBuilding = w._add_building(k, cell, size)
		if k == "beehive":
			b.position = w.grid_to_world(Vector2(cell) + Vector2(0.6, 0.4))
		return
	if d.has("animal"):
		w._add_pen(k, cell, int(p.get("n", 0)))


# ------------------------------------------------------------------ construction

func _add_site(i: int) -> void:
	var p: Dictionary = Game.placed[i]
	var size: Vector2i = footprint(p["k"], Vector2i(int(p["x"]), int(p["y"]))).size
	var spr := "site_small" if size.x <= 2 else "site_big"
	var s: Sprite2D = w._add_prop(spr, Vector2(int(p["x"]), int(p["y"])), null)
	s.set_meta("site", i)
	s.set_meta("squash", 0.06)
	w._dirt_rect(footprint(p["k"], Vector2i(int(p["x"]), int(p["y"]))), 0.6)
	sites[i] = s


## Starts building something on the map (coins already paid).
func start_build(kind: String, cell: Vector2i) -> void:
	var d: Dictionary = Game.placeables[kind]
	var p := {"k": kind, "x": cell.x, "y": cell.y, "done": Time.get_unix_time_from_system() + float(d.get("build", 10))}
	if d.has("animal"):
		p["n"] = 1  # every pen comes with its first animal
	Game.placed.append(p)
	var r := footprint(kind, cell)
	for x in range(r.position.x, r.end.x):
		for y in range(r.position.y, r.end.y):
			w.occupied[Vector2i(x, y)] = true
	_add_site(Game.placed.size() - 1)
	Audio.play("whoosh")
	w._puff(w.grid_to_world(Vector2(cell)), "fx_smoke", 6)
	Game.mark_dirty()


func site_left(i: int) -> float:
	return maxf(0.0, float(Game.placed[i]["done"]) - Time.get_unix_time_from_system())


## Tap on a construction site: finish it when the time is up.
func tap_site(s: Sprite2D) -> void:
	var i: int = s.get_meta("site")
	var left := site_left(i)
	if left > 0.0:
		Game.toast.emit(tr("BUILD_LEFT") % Hud._fmt_time(int(left)), "ico_build.png")
		return
	var p: Dictionary = Game.placed[i]
	p["done"] = 0.0
	sites.erase(i)
	w.props.erase(s)
	s.queue_free()
	_spawn(p["k"], Vector2i(int(p["x"]), int(p["y"])), p)
	w._puff(w.grid_to_world(Vector2(int(p["x"]), int(p["y"]))), "fx_smoke", 10)
	Audio.play("levelup", 1.2)
	Game.add_xp(5)
	Game.event("build", p["k"])
	Game.toast.emit(tr("BUILD_DONE") % tr("PLACE_" + p["k"]), "ico_build.png")
	Game.mark_dirty()


# ------------------------------------------------------------------ obstacles and parcels

func clear_obstacle(s: Sprite2D) -> bool:
	var tool: String = s.get_meta("tool")
	if not cell_open(w.cell_at(s.position)):
		Game.toast.emit(tr("LAND_LOCKED"), "ico_lock.png")
		return false
	if not Game.take_item(tool, 1):
		Game.toast.emit(tr("NEED_TOOL") % tr("ITEM_" + tool), "item_%s.png" % tool)
		return false
	var key: String = s.get_meta("obstacle")
	Game.cleared[key] = true
	obstacles.erase(key)
	w.props.erase(s)
	w.occupied.erase(w.cell_at(s.position))
	var pos := s.position
	var t := create_tween()
	if tool == "dynamite":
		Audio.play("dig", 0.7)
		w._puff(pos + Vector2(0, -40), "fx_smoke", 14)
		t.tween_property(s, "scale", Vector2(1.25, 0.6), 0.12)
		t.tween_property(s, "modulate:a", 0.0, 0.15)
	else:
		Audio.play("dig" if tool == "shovel" else "whoosh", 1.1)
		w._puff(pos + Vector2(0, -60), "fx_leaf" if tool != "shovel" else "fx_grain", 8)
		t.tween_property(s, "rotation", 0.5 if tool != "shovel" else 0.0, 0.25)
		t.parallel().tween_property(s, "modulate:a", 0.0, 0.3)
	t.tween_callback(s.queue_free)
	var coins := 4 + int(hash01(w.cell_at(pos), 5.0) * 8.0)
	Game.add_coins(coins)
	Game.add_xp(3)
	w._float_reward(pos + Vector2(0, -90), coins)
	Game.event("clear", tool)
	var found := Game.roll_find(0.3)
	if found != "":
		w._float_reward(pos + Vector2(0, -150), 1, "item_%s.png" % found)
	Game.mark_dirty()
	return true


func can_buy_parcel(id: String) -> String:
	var c := parcel_cost(id)
	if Game.level < int(c["level"]):
		return tr("LAND_LEVEL") % int(c["level"])
	if Game.coins < int(c["coins"]):
		return tr("NOT_ENOUGH_COINS")
	for it in Game.LAND_ITEMS:
		if Game.count(it) < int(c["items"]):
			return tr("NEED_ITEMS")
	return ""


func buy_parcel(id: String) -> bool:
	if can_buy_parcel(id) != "":
		return false
	var c := parcel_cost(id)
	Game.add_coins(-int(c["coins"]))
	for it in Game.LAND_ITEMS:
		Game.take_item(it, int(c["items"]))
	Game.land[id] = true
	var s: Sprite2D = signs.get(id)
	if s:
		w._puff(s.position, "fx_smoke", 10)
	_place_signs()
	Audio.play("levelup")
	Game.add_xp(20 * parcel_ring(id))
	Game.event("expand", id)
	Game.mark_dirty()
	return true


# ------------------------------------------------------------------ silo look

func refresh_silo() -> void:
	var s: Sprite2D = fixed.get("silo")
	if s == null:
		return
	# fill level 0..3 drawn as grain in the window
	var k := float(Game.stored(true)) / float(Game.capacity(true))
	var lvl := 0 if k < 0.05 else (1 if k < 0.4 else (2 if k < 0.8 else 3))
	if lvl == _silo_level_shown:
		return
	_silo_level_shown = lvl
	var name := "silo_%d" % lvl
	if Atlas.has(name):
		Atlas.apply(s, name)
		s.set_meta("sprite", name)


# ------------------------------------------------------------------ delivery truck

func _spawn_truck() -> void:
	truck = Sprite2D.new()
	Atlas.apply(truck, "truck_se")
	truck.position = w.grid_to_world(TRUCK_PARK)
	w.objects.add_child(truck)
	_truck_crate = Sprite2D.new()
	Atlas.apply(_truck_crate, "coin_crate")
	_truck_crate.position = Vector2(-20, -120)
	_truck_crate.visible = false
	truck.add_child(_truck_crate)
	_update_truck(true)


func truck_away() -> bool:
	return Game.truck_away()


func truck_waiting() -> bool:
	return not truck_away() and Game.truck_cargo > 0


func collect_truck() -> void:
	if not truck_waiting():
		return
	var c := Game.truck_cargo
	Game.add_coins(c)
	Game.add_xp(Game.truck_xp)
	Game.truck_cargo = 0
	Game.truck_xp = 0
	Audio.play("coin")
	w._float_reward(truck.position + Vector2(0, -140), c)
	var found := Game.roll_find(0.35)
	if found != "":
		w._float_reward(truck.position + Vector2(40, -200), 1, "item_%s.png" % found)
	Field.squash(truck, 0.08)
	Game.event("truck", "any")
	Game.mark_dirty()


func truck_tap(world_pos: Vector2) -> bool:
	if truck == null or not truck.visible:
		return false
	if not truck.get_rect().has_point(truck.to_local(world_pos)):
		return false
	if truck_waiting():
		collect_truck()
	else:
		w.hud.open_orders()
	return true


## Moves the truck along its route while it is away (out, wait, back).
func _update_truck(snap := false) -> void:
	if truck == null:
		return
	_truck_crate.visible = truck_waiting()
	if not truck_away():
		truck.visible = true
		truck.position = w.grid_to_world(TRUCK_PARK)
		Atlas.apply(truck, "truck_se")
		return
	var left := Game.truck_back_at - Time.get_unix_time_from_system()
	var t := 1.0 - left / Game.TRUCK_TRIP  # 0..1 over the whole trip
	var drive := 0.25  # share of the trip spent driving each way
	var k: float
	var going := t < 0.5
	if t < drive:
		k = t / drive
	elif t > 1.0 - drive:
		k = (1.0 - t) / drive
	else:
		truck.visible = false
		return
	truck.visible = true
	var pts: Array = TRUCK_ROUTE
	var seg := k * (pts.size() - 1)
	var i := mini(int(seg), pts.size() - 2)
	var g: Vector2 = (pts[i] as Vector2).lerp(pts[i + 1], seg - i)
	truck.position = w.grid_to_world(g)
	var dir: Vector2 = (pts[i + 1] as Vector2) - (pts[i] as Vector2)
	if not going:
		dir = -dir
	# grid -y = north-east on screen, grid +y = south-west
	var facing := "truck_ne" if dir.y < -0.1 else ("truck_sw" if dir.y > 0.1 else "truck_se")
	Atlas.apply(truck, facing)
	truck.position.y += sin(Time.get_ticks_msec() * 0.03) * 1.5


func _process(_delta: float) -> void:
	_update_truck()
