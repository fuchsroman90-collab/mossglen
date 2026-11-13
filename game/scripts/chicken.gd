class_name Chicken
extends Node2D
## Wanders inside its pen, hops while walking, pecks when idle.

const SPEED := 38.0

var random_point: Callable  ## () -> Vector2, a random spot inside the pen
var _sprite: Sprite2D
var _target := Vector2.ZERO
var _wait := 0.0
var _walk_t := 0.0
var _frame_t := 0.0
var _frame := 0


func _ready() -> void:
	_sprite = Atlas.sprite("chicken_0")
	add_child(_sprite)
	_wait = randf_range(0.2, 2.0)
	_target = position


func _process(delta: float) -> void:
	if _wait > 0.0:
		_wait -= delta
		_sprite.position.y = 0.0
		if _wait <= 0.0:
			_pick_target()
		return
	var to := _target - position
	var step := SPEED * delta
	if to.length() <= step:
		position = _target
		_wait = randf_range(1.0, 3.5)
		if randf() < 0.5:
			_peck()
		return
	position += to.normalized() * step
	_walk_t += delta
	_sprite.position.y = -absf(sin(_walk_t * 11.0)) * 3.0
	_frame_t += delta
	if _frame_t > 0.14:
		_frame_t = 0.0
		_frame = 1 - _frame
		Atlas.apply(_sprite, "chicken_%d" % _frame)


func _pick_target() -> void:
	_target = random_point.call()
	_sprite.scale.x = -1.0 if _target.x < position.x else 1.0


func _peck() -> void:
	var tw := create_tween()
	tw.tween_property(_sprite, "rotation", 0.35 * _sprite.scale.x, 0.12)
	tw.tween_property(_sprite, "rotation", 0.0, 0.18)
	tw.tween_property(_sprite, "rotation", 0.35 * _sprite.scale.x, 0.12)
	tw.tween_property(_sprite, "rotation", 0.0, 0.18)


## Player tapped the chicken.
func poke() -> void:
	Audio.play("cluck", 1.0, 0.12)
	var tw := create_tween()
	tw.tween_property(_sprite, "position:y", -18.0, 0.14).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tw.tween_property(_sprite, "position:y", 0.0, 0.22).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_BOUNCE)
	_wait = 0.6
