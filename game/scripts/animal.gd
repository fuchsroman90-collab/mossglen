class_name Animal
extends Node2D
## Wandering farm animal with pre-rendered frame animations.
## Frames are named "<kind>_<anim>_<facing>_<i>", facing "se" or "ne";
## south-west / north-west are the same frames mirrored.

const CONFIG := {
	"chicken": {
		"speed": 72.0, "anims": {"idle": [6, 6.0], "walk": [8, 13.0], "peck": [6, 10.0]},
		"shadow": Vector2(0.75, 0.8), "tap_height": 50.0, "sound": "cluck",
	},
	"dino": {
		"speed": 58.0, "anims": {"idle": [8, 7.0], "walk": [8, 9.0]},
		"shadow": Vector2(1.45, 1.4), "tap_height": 80.0, "sound": "pop",
	},
}

var kind := "chicken"
var random_point: Callable  ## () -> Vector2, a random spot inside the pen

var _cfg: Dictionary
var _sprite: Sprite2D
var _anim := "idle"
var _facing := "se"
var _flip := false
var _t := 0.0
var _frame := -1
var _target := Vector2.ZERO
var _wait := 0.0


func _ready() -> void:
	_cfg = CONFIG[kind]
	var sh := Atlas.sprite("shadow_blob")
	sh.scale = _cfg["shadow"]
	sh.modulate.a = 0.9
	add_child(sh)
	_sprite = Sprite2D.new()
	add_child(_sprite)
	_wait = randf_range(0.2, 2.5)
	_target = position
	_facing = "se" if randf() < 0.6 else "ne"
	_flip = randf() < 0.5
	_t = randf() * 3.0
	_show()


func _process(delta: float) -> void:
	_t += delta
	if _anim == "walk":
		var to := _target - position
		var step: float = _cfg["speed"] * delta
		if to.length() <= step:
			position = _target
			_wait = randf_range(1.2, 4.0)
			_play("peck" if _cfg["anims"].has("peck") and randf() < 0.55 else "idle")
		else:
			position += to.normalized() * step
	elif _anim == "peck":
		if _t * _cfg["anims"]["peck"][1] >= _cfg["anims"]["peck"][0] * 2:
			_play("idle")
	else:
		_wait -= delta
		if _wait <= 0.0:
			_pick_target()
	_show()


func _play(anim: String) -> void:
	_anim = anim
	_t = 0.0
	_frame = -1


func _show() -> void:
	var a: Array = _cfg["anims"][_anim]
	var f := int(_t * a[1]) % int(a[0])
	if f == _frame:
		return
	_frame = f
	Atlas.apply(_sprite, "%s_%s_%s_%d" % [kind, _anim, _facing, f])
	_sprite.scale.x = -1.0 if _flip else 1.0


func _pick_target() -> void:
	_target = random_point.call()
	var d := _target - position
	_facing = "se" if d.y >= 0.0 else "ne"
	_flip = d.x < 0.0
	_play("walk")


## Player tapped the animal.
func poke() -> void:
	Audio.play(_cfg["sound"], 1.0, 0.12)
	var tw := create_tween()
	tw.tween_property(_sprite, "position:y", -30.0, 0.14).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tw.tween_property(_sprite, "position:y", 0.0, 0.24).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_BOUNCE)
	if _anim == "walk":
		_play("idle")
	_wait = 0.8


func tap_point() -> Vector2:
	return position + Vector2(0, -_cfg["tap_height"])
