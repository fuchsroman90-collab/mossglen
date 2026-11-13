class_name Field
extends Node2D
## A soil bed that grows one crop. Growth uses wall-clock time, so it keeps
## progressing while the game is closed (offline growth).

enum State { EMPTY, GROWING, RIPE }

var state: State = State.EMPTY
var crop := ""
var planted_at := 0.0
var cell := Vector2i.ZERO
var _stage := -1
var _soil: Sprite2D
var _crop: Sprite2D


func setup(sway: Material) -> void:
	_soil = Atlas.sprite("field")
	add_child(_soil)
	_crop = Sprite2D.new()
	_crop.material = sway
	add_child(_crop)
	set_process(false)


static func now() -> float:
	return Time.get_unix_time_from_system()


func grow_time() -> float:
	return float(Game.crops[crop]["grow"]) if crop != "" else 1.0


func plant(kind: String, at := -1.0) -> bool:
	if state != State.EMPTY:
		return false
	crop = kind
	state = State.GROWING
	planted_at = now() if at < 0.0 else at
	_update_stage(true)
	set_process(state == State.GROWING)
	return true


func harvest() -> String:
	if state != State.RIPE:
		return ""
	var c := crop
	state = State.EMPTY
	crop = ""
	_stage = -1
	_crop.texture = null
	return c


func progress() -> float:
	if state == State.EMPTY:
		return 0.0
	return clampf((now() - planted_at) / grow_time(), 0.0, 1.0)


func seconds_left() -> int:
	return maxi(0, ceili(grow_time() - (now() - planted_at)))


func _ready() -> void:
	# Godot enables _process automatically; only growing fields need it
	set_process(state == State.GROWING)


func _process(_delta: float) -> void:
	if state != State.GROWING:
		set_process(false)
		return
	_update_stage(false)


func _update_stage(force_pop: bool) -> void:
	var p := progress()
	var stage := 3 if p >= 1.0 else int(p * 3.0)
	if p >= 1.0:
		state = State.RIPE
		set_process(false)
	if stage != _stage:
		_stage = stage
		Atlas.apply(_crop, "%s_%d" % [crop, stage])
		if force_pop or stage > 0:
			squash(_crop)


## Ghost look while being placed or moved.
func set_ghost(on: bool, ok := true) -> void:
	modulate = Color(1, 1, 1) if not on else (Color(0.55, 1.0, 0.55, 0.9) if ok else Color(1.0, 0.42, 0.42, 0.9))
	z_index = 50 if on else 0


func to_save() -> Dictionary:
	return {"x": cell.x, "y": cell.y, "crop": crop, "t": planted_at}


static func squash(n: Node2D, amount := 0.25) -> void:
	n.scale = Vector2(1.0 + amount, 1.0 - amount)
	var tw := n.create_tween()
	tw.tween_property(n, "scale", Vector2.ONE, 0.45).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
