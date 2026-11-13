class_name Field
extends Node2D
## A soil bed that grows one crop. Growth uses wall-clock time so it keeps
## progressing while the game is closed (once saving exists).

enum State { EMPTY, GROWING, RIPE }

const CROP := "wheat"
const GROW_TIME := 12.0  # seconds, short for the M0 test scene
const REWARD := 2

var state: State = State.EMPTY
var planted_at := 0.0
var cell := Vector2i.ZERO
var _stage := -1
var _crop: Sprite2D


func setup(sway: Material) -> void:
	add_child(Atlas.sprite("field"))
	_crop = Sprite2D.new()
	_crop.material = sway
	add_child(_crop)
	set_process(false)


static func now() -> float:
	return Time.get_unix_time_from_system()


func plant(at := -1.0) -> bool:
	if state != State.EMPTY:
		return false
	state = State.GROWING
	planted_at = now() if at < 0.0 else at
	_update_stage(true)
	set_process(true)
	return true


func harvest() -> bool:
	if state != State.RIPE:
		return false
	state = State.EMPTY
	_stage = -1
	_crop.texture = null
	return true


func progress() -> float:
	if state == State.EMPTY:
		return 0.0
	return clampf((now() - planted_at) / GROW_TIME, 0.0, 1.0)


func _process(_delta: float) -> void:
	_update_stage(false)


func _update_stage(force_pop: bool) -> void:
	var p := progress()
	var stage := 3 if p >= 1.0 else int(p * 3.0)
	if p >= 1.0:
		state = State.RIPE
		set_process(false)
	if stage != _stage:
		_stage = stage
		Atlas.apply(_crop, "%s_%d" % [CROP, stage])
		if force_pop or stage > 0:
			squash(_crop)


static func squash(n: Node2D, amount := 0.25) -> void:
	n.scale = Vector2(1.0 + amount, 1.0 - amount)
	var tw := n.create_tween()
	tw.tween_property(n, "scale", Vector2.ONE, 0.45).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
