class_name FishingUI
extends Control
## Relaxed fishing minigame (never fails):
## cast -> wait -> bite -> a white ring shrinks onto the gold target ring.
## Tap when they overlap: better timing gives rarer and bigger fish.
## No tap still lands a fish (lowest quality). Then a catch card: sell or release.

signal finished

const RING_TIME := 1.35
const RING_FROM := 2.3
const RING_TO := 0.35

var hud: Hud
var spot := ""
var loc := "pond"
var time_name := "day"

var _state := ""
var _t := 0.0
var _wait := 0.0
var _quality := 0.0
var _disc: TextureRect
var _bobber: TextureRect
var _target: TextureRect
var _ring: TextureRect
var _msg: Label
var _card: Control
var _catch: Dictionary


func start(h: Hud, spot_id: String, place: String, time_of_day: String) -> void:
	hud = h
	spot = spot_id
	loc = place
	time_name = time_of_day
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0.05, 0.1, 0.12, 0.45)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	var centre := Control.new()
	centre.set_anchors_preset(Control.PRESET_CENTER)
	centre.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(centre)
	_disc = hud._tex("water_disc.png")
	_disc.position = Vector2(-260, -270)
	centre.add_child(_disc)
	_target = hud._tex("ring_target.png")
	_target.position = Vector2(-128, -128)
	_target.pivot_offset = Vector2(128, 128)
	_target.visible = false
	centre.add_child(_target)
	_ring = hud._tex("ring_move.png")
	_ring.position = Vector2(-128, -128)
	_ring.pivot_offset = Vector2(128, 128)
	_ring.visible = false
	centre.add_child(_ring)
	_bobber = hud._tex("bobber.png")
	_bobber.position = Vector2(-48, -60)
	_bobber.pivot_offset = Vector2(48, 60)
	centre.add_child(_bobber)
	_msg = hud._label("FISH_WAIT", 52)
	_msg.position = Vector2(-500, 300)
	_msg.size = Vector2(1000, 80)
	_msg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	centre.add_child(_msg)
	_card = Control.new()
	_card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	centre.add_child(_card)
	Audio.play("splash")
	_bobber.scale = Vector2(0.3, 0.3)
	create_tween().tween_property(_bobber, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	_state = "wait"
	_wait = randf_range(1.2, 2.6)
	_t = 0.0


func _process(delta: float) -> void:
	_t += delta
	match _state:
		"wait":
			_bobber.position.y = -60 + sin(_t * 3.0) * 6.0
			if _t >= _wait:
				_bite()
		"bite":
			if has_meta("auto_tap") and _t > RING_TIME * (RING_FROM - 1.0) / (RING_FROM - RING_TO):
				_land(1.0)
				return
			var k := clampf(_t / RING_TIME, 0.0, 1.0)
			var sc := lerpf(RING_FROM, RING_TO, k)
			_ring.scale = Vector2(sc, sc)
			_bobber.position.y = -50 + sin(_t * 30.0) * 5.0
			if k >= 1.0:
				_land(0.0)


func _bite() -> void:
	_state = "bite"
	_t = 0.0
	Audio.play("pop", 0.8)
	_msg.text = "FISH_BITE"
	_target.visible = true
	_ring.visible = true
	_ring.scale = Vector2(RING_FROM, RING_FROM)
	_bobber.rotation = 0.3


func _gui_input(event: InputEvent) -> void:
	var tap: bool = (event is InputEventScreenTouch and event.pressed) or \
			(event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT)
	if not tap:
		return
	accept_event()
	if _state == "bite":
		var d := absf(_ring.scale.x - 1.0)
		_land(clampf(1.0 - d / 0.65, 0.0, 1.0))
	elif _state == "wait":
		pass  # tapping too early does nothing (no fail state)


func _land(q: float) -> void:
	_state = "reel"
	_quality = q
	_ring.visible = false
	_target.visible = false
	Audio.play("reel")
	_msg.text = "FISH_PERFECT" if q > 0.8 else ("FISH_GOOD" if q > 0.45 else "FISH_OK")
	var tw := create_tween()
	tw.tween_property(_bobber, "position:y", -140.0, 0.55).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tw.tween_callback(_show_catch)


func _show_catch() -> void:
	_state = "card"
	_bobber.visible = false
	_msg.text = ""
	_catch = Game.roll_fish(loc, time_name, _quality)
	var id: String = _catch["id"]
	var size: float = _catch["size"]
	var info := Game.record_catch(id, size)
	Audio.play("splash", 1.3)
	var f: Dictionary = Game.fish_by_id[id]
	var panel := hud._patch("panel.png", 44, 44)
	panel.position = Vector2(-380, -330)
	panel.size = Vector2(760, 640)
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	_card.add_child(panel)
	var icon := hud._tex("fish_%s.png" % id)
	icon.scale = Vector2(2.6, 2.6)
	icon.position = Vector2(380 - 128 * 1.3, 60)
	panel.add_child(icon)
	var name_l := hud._dark(hud._label(Game.fish_name(id), 56))
	name_l.position = Vector2(0, 310)
	name_l.size = Vector2(760, 80)
	name_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	panel.add_child(name_l)
	var stars := ""
	for i in int(f["rarity"]):
		stars += "★"
	var size_l := hud._dark(hud._label("%.1f cm   %s" % [size, stars], 40))
	size_l.position = Vector2(0, 380)
	size_l.size = Vector2(760, 60)
	size_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	panel.add_child(size_l)
	if info["new"] or info["record"]:
		var badge := hud._label("FISH_NEW" if info["new"] else "FISH_RECORD", 44)
		badge.add_theme_color_override("font_color", Color("FFD23F"))
		badge.position = Vector2(470, 30)
		badge.size = Vector2(260, 60)
		badge.rotation = 0.18
		panel.add_child(badge)
	var value := Game.fish_value(id, size)
	var sell := hud._pill("", Vector2(60, 470), 300, true)
	panel.add_child(sell)
	var coin := hud._tex("coin.png")
	coin.scale = Vector2(0.6, 0.6)
	coin.position = Vector2(34, 14)
	sell.add_child(coin)
	var sl := hud._label("+%d" % value, 44)
	sl.position = Vector2(100, 0)
	sl.size = Vector2(180, 86)
	sell.add_child(sl)
	sell.pressed.connect(func() -> void:
		Game.add_coins(value)
		Audio.play("coin")
		_close())
	var xp := 1 + int(f["rarity"]) * 2
	var rel := hud._pill("", Vector2(400, 470), 300, true)
	panel.add_child(rel)
	var rl := hud._label(tr("FISH_RELEASE") + "  +%d XP" % xp, 34)
	rl.size = Vector2(300, 86)
	rl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rel.add_child(rl)
	rel.pressed.connect(func() -> void:
		Game.add_xp(xp)
		Audio.play("splash", 1.4)
		_close())
	panel.pivot_offset = panel.size / 2
	panel.scale = Vector2(0.5, 0.5)
	create_tween().tween_property(panel, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _close() -> void:
	finished.emit()
	queue_free()
