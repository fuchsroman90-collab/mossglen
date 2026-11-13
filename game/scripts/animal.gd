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
	"cow": {
		"speed": 46.0, "anims": {"idle": [6, 6.0], "walk": [8, 9.0], "eat": [6, 6.0]},
		"shadow": Vector2(1.7, 1.6), "tap_height": 75.0, "sound": "pop",
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
var fed_at := 0.0  ## unix time of the last feeding, 0 = hungry
var pen_id := ""
var _bubble: Node2D
var _bubble_icon: Sprite2D


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
	if Game.animal_defs.has(kind):
		_bubble = Node2D.new()
		_bubble.position = Vector2(0, -_cfg["tap_height"] * 2.1)
		add_child(_bubble)
		var back := Sprite2D.new()
		back.texture = load("res://art/generated/ui/slot.png")
		back.scale = Vector2(0.62, 0.62)
		_bubble.add_child(back)
		_bubble_icon = Sprite2D.new()
		_bubble_icon.scale = Vector2(0.55, 0.55)
		_bubble.add_child(_bubble_icon)
		_update_bubble()


# ------------------------------------------------------------------ production

func def() -> Dictionary:
	return Game.animal_defs.get(kind, {})


func produces() -> bool:
	return Game.animal_defs.has(kind)


func is_hungry() -> bool:
	return produces() and fed_at <= 0.0


func is_ready() -> bool:
	return produces() and fed_at > 0.0 and Time.get_unix_time_from_system() - fed_at >= float(def()["time"])


func seconds_left() -> int:
	if fed_at <= 0.0:
		return 0
	return maxi(0, ceili(float(def()["time"]) - (Time.get_unix_time_from_system() - fed_at)))


func progress() -> float:
	if fed_at <= 0.0:
		return 0.0
	return clampf((Time.get_unix_time_from_system() - fed_at) / float(def()["time"]), 0.0, 1.0)


func feed(at := -1.0) -> void:
	fed_at = Time.get_unix_time_from_system() if at < 0.0 else at
	if at < 0.0:
		var eat := "peck" if _cfg["anims"].has("peck") else "eat"
		if _cfg["anims"].has(eat):
			_play(eat)
		Audio.play(_cfg["sound"], 1.1, 0.1)
	_update_bubble()


func collect() -> String:
	if not is_ready():
		return ""
	fed_at = 0.0
	_update_bubble()
	poke()
	return def()["product"]


func _update_bubble() -> void:
	if _bubble == null:
		return
	if is_ready():
		_bubble.visible = true
		_bubble.modulate.a = 1.0
		_bubble_icon.texture = load("res://art/generated/ui/item_%s.png" % def()["product"])
	elif is_hungry():
		_bubble.visible = true
		_bubble.modulate.a = 0.55
		_bubble_icon.texture = load("res://art/generated/ui/item_%s.png" % def()["feed"])
	else:
		_bubble.visible = false


func _process(delta: float) -> void:
	_t += delta
	if _bubble != null:
		if not _bubble.visible and is_ready():
			_update_bubble()
		if _bubble.visible:
			_bubble.position.y = -_cfg["tap_height"] * 2.1 + sin(Time.get_ticks_msec() * 0.004 + position.x) * 6.0
	if _anim == "walk":
		var to := _target - position
		var step: float = _cfg["speed"] * delta
		if to.length() <= step:
			position = _target
			_wait = randf_range(1.2, 4.0)
			if _cfg["anims"].has("peck") and randf() < 0.55:
				_play("peck")
			elif _cfg["anims"].has("eat") and randf() < 0.35:
				_play("eat")
			else:
				_play("idle")
		else:
			position += to.normalized() * step
	elif _anim == "peck" or _anim == "eat":
		if _t * _cfg["anims"][_anim][1] >= _cfg["anims"][_anim][0] * 2:
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
