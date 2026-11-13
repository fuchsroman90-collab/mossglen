class_name ProductionBuilding
extends Node2D
## A production building with a queue. Jobs run one after another on wall-clock
## time, so they finish while the game is closed. Finished goods wait in the
## building until the player collects them.

signal changed

var id := ""
var def: Dictionary
var queue: Array = []  ## [{"r": recipe index, "end": unix time when done}]
var done: Array = []   ## finished recipe indices waiting for pickup
var sprite: Sprite2D
var _bubble: Node2D
var _bubble_icon: Sprite2D
var _sails: Sprite2D
var _fx_t := 0.0
var _bees: Array[Sprite2D] = []


func setup(building_id: String) -> void:
	id = building_id
	def = Game.buildings[id]
	sprite = Atlas.sprite(id)
	add_child(sprite)
	var fx: Dictionary = def.get("fx", {})
	if fx.has("sails"):
		_sails = Atlas.sprite("mill_sails")
		_sails.position = Vector2(fx["sails"][0], fx["sails"][1])
		add_child(_sails)
	if fx.has("bees"):
		for i in 4:
			var bee := Atlas.sprite("fx_bee")
			bee.set_meta("phase", i * 1.7)
			bee.z_index = 4
			add_child(bee)
			_bees.append(bee)
	_bubble = Node2D.new()
	_bubble.position = Vector2(0, -Atlas.anchor(id).y - 40)
	_bubble.visible = false
	add_child(_bubble)
	var back := Sprite2D.new()
	back.texture = load("res://art/generated/ui/slot.png")
	back.scale = Vector2(0.9, 0.9)
	_bubble.add_child(back)
	_bubble_icon = Sprite2D.new()
	_bubble_icon.scale = Vector2(0.8, 0.8)
	_bubble.add_child(_bubble_icon)
	tick()


func recipes() -> Array:
	return def["recipes"]


func slots() -> int:
	return int(def["slots"])


func is_working() -> bool:
	return not queue.is_empty()


## Moves jobs whose time has passed into `done`. Returns true if anything changed.
func is_auto() -> bool:
	return bool(def.get("auto", false))


func tick() -> bool:
	var now := Time.get_unix_time_from_system()
	var moved := false
	if is_auto():
		# keeps itself busy: a new batch starts whenever there is room
		while queue.size() + done.size() < slots():
			var begin := now if queue.is_empty() else float(queue[-1]["end"])
			queue.append({"r": 0, "end": begin + float(recipes()[0]["time"])})
	while not queue.is_empty() and float(queue[0]["end"]) <= now:
		done.append(int(queue.pop_front()["r"]))
		moved = true
	if moved:
		_refresh()
		changed.emit()
	return moved


func can_start(r: int) -> bool:
	var rec: Dictionary = recipes()[r]
	return Game.level >= int(rec["unlock"]) and queue.size() + done.size() < slots() and Game.has_all(rec["in"])


func start(r: int) -> bool:
	if not can_start(r):
		return false
	var rec: Dictionary = recipes()[r]
	Game.take_all(rec["in"])
	var begin := Time.get_unix_time_from_system()
	if not queue.is_empty():
		begin = maxf(begin, float(queue[-1]["end"]))
	queue.append({"r": r, "end": begin + float(rec["time"])})
	Field.squash(sprite, 0.06)
	_refresh()
	changed.emit()
	Game.mark_dirty()
	return true


## Seconds left and progress (0..1) of the running job.
func current_progress() -> Vector2:
	if queue.is_empty():
		return Vector2(0, 0)
	var rec: Dictionary = recipes()[int(queue[0]["r"])]
	var left := float(queue[0]["end"]) - Time.get_unix_time_from_system()
	var total := float(rec["time"])
	return Vector2(maxf(0.0, left), clampf(1.0 - left / total, 0.0, 1.0))


## Collects finished goods that fit into the barn. Returns [[item, n], ...].
func collect() -> Array:
	var got: Array = []
	while not done.is_empty():
		var rec: Dictionary = recipes()[int(done[0])]
		var n := int(rec["n"])
		if Game.space() < n:
			break
		done.pop_front()
		Game.add_item(rec["out"], n)
		Game.add_xp(int(rec["xp"]))
		got.append([rec["out"], n])
	if not got.is_empty():
		_refresh()
		changed.emit()
	return got


func _refresh() -> void:
	_bubble.visible = not done.is_empty()
	if _bubble.visible:
		var rec: Dictionary = recipes()[int(done[0])]
		_bubble_icon.texture = load("res://art/generated/ui/item_%s.png" % rec["out"])


func _process(delta: float) -> void:
	tick()
	if not _bees.is_empty():
		var t := Time.get_ticks_msec() * 0.001
		for b in _bees:
			var ph: float = b.get_meta("phase")
			b.position = Vector2(cos(t * 1.3 + ph) * 90.0 + sin(t * 3.1 + ph) * 20.0,
					-110.0 + sin(t * 1.7 + ph * 2.0) * 45.0)
			b.scale.x = -1.0 if sin(t * 1.3 + ph) > 0.0 else 1.0
	if _bubble.visible:
		_bubble.position.y = -Atlas.anchor(id).y - 40 + sin(Time.get_ticks_msec() * 0.004) * 8.0
	if is_working():
		if _sails != null:
			_sails.rotation += delta * 1.6
		_fx_t += delta
		var fx: Dictionary = def.get("fx", {})
		if fx.has("smoke") and _fx_t > 0.6:
			_fx_t = 0.0
			_smoke(Vector2(fx["smoke"][0], fx["smoke"][1]))
	elif _sails != null:
		_sails.rotation += delta * 0.25  # idle breeze


func _smoke(at: Vector2) -> void:
	var s := Atlas.sprite("fx_smoke")
	s.centered = true
	s.offset = Vector2.ZERO
	s.position = at
	s.scale = Vector2(0.5, 0.5)
	s.modulate.a = 0.8
	s.z_index = 5
	add_child(s)
	var tw := s.create_tween().set_parallel(true)
	tw.tween_property(s, "position", at + Vector2(randf_range(-20, 30), -110), 2.2)
	tw.tween_property(s, "scale", Vector2(1.3, 1.3), 2.2)
	tw.tween_property(s, "modulate:a", 0.0, 2.2).set_ease(Tween.EASE_IN)
	tw.chain().tween_callback(s.queue_free)


func to_save() -> Dictionary:
	return {"queue": queue, "done": done}


func load_save(d: Dictionary) -> void:
	queue = []
	for q in d.get("queue", []):
		queue.append({"r": int(q["r"]), "end": float(q["end"])})
	done = []
	for x in d.get("done", []):
		done.append(int(x))
	tick()
	_refresh()
