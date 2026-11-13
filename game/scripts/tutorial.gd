class_name Tutorial
extends Node
## First-time guide: a pointing hand over the thing to tap and a short text box.
## Steps: 0 sow wheat, 1 feed chickens, 2 harvest, 3 open the order board, 4 open Brumm's quest.
## Progress is Game.tutorial_step (-1 = done or skipped). Each step advances on a game event.

const STEPS := 5

var hud: Hud
var world: Node  ## world.gd, set by the world
var _hand: TextureRect
var _box: Control
var _text: Label
var _t := 0.0
var _swipe := 0.0


func setup(h: Hud) -> void:
	hud = h
	_hand = hud._tex("hand.png")
	_hand.visible = false
	hud._root.add_child(_hand)
	_box = hud._patch("panel.png", 44, 44)
	_box.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_box.offset_left = -640
	_box.offset_right = 640
	_box.offset_top = -270
	_box.offset_bottom = -60
	_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_box.visible = false
	hud._root.add_child(_box)
	_text = hud._dark(hud._label("", 38))
	_text.position = Vector2(48, 20)
	_text.size = Vector2(980, 170)
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD
	_box.add_child(_text)
	var skip := hud._pill("TUT_SKIP", Vector2(1050, 54), 200)
	skip.pressed.connect(func() -> void:
		Audio.play("click")
		_finish(false))
	_box.add_child(skip)
	_box.mouse_filter = Control.MOUSE_FILTER_PASS
	Game.game_event.connect(_on_event)
	Game.quest_changed.connect(func() -> void:
		if Game.tutorial_step == 4 and (Game.quest_stage != "intro" or Game.quest_index > 0):
			_advance())
	_show()


func active() -> bool:
	return Game.tutorial_step >= 0 and Game.tutorial_step < STEPS


func restart() -> void:
	Game.tutorial_step = 0
	_show()


func _on_event(type: String, _id: String) -> void:
	match Game.tutorial_step:
		0:
			if type == "plant":
				_advance()
		1:
			if type == "feed":
				_advance()
		2:
			if type == "harvest":
				_advance()
		3:
			if type == "open":
				_advance()


func _advance() -> void:
	Game.tutorial_step += 1
	Game.mark_dirty()
	if Game.tutorial_step >= STEPS:
		_finish(true)
		return
	Audio.play("pop")
	_show()


func _finish(done: bool) -> void:
	Game.tutorial_step = -1
	Game.mark_dirty()
	_box.hide()
	_hand.hide()
	if done:
		Audio.play("achieve")
		Game.toast.emit(tr("TUT_DONE"), "star.png")


func _show() -> void:
	if not active():
		_box.hide()
		_hand.hide()
		return
	hud.hide_hint()
	_text.text = "TUT_%d" % Game.tutorial_step
	_box.show()
	_box.pivot_offset = _box.size / 2
	_box.scale = Vector2(0.9, 0.9)
	hud.create_tween().tween_property(_box, "scale", Vector2.ONE, 0.2).set_trans(Tween.TRANS_BACK) \
		.set_ease(Tween.EASE_OUT)


func _process(delta: float) -> void:
	if not active() or world == null:
		return
	# the guide steps aside while a menu is open (except for the step that is about the menu)
	var busy: bool = hud.any_menu_open()
	_box.visible = not busy
	_t += delta
	var target := _target()
	if busy or target.x < -9000.0:
		_hand.visible = false
		return
	_hand.visible = true
	var bob := absf(sin(_t * 4.0)) * 26.0
	var swipe := Vector2.ZERO
	if Game.tutorial_step == 2 and _field_ripe():
		_swipe = fmod(_t * 0.6, 1.0)
		swipe = Vector2(lerpf(-160.0, 160.0, _swipe), lerpf(-80.0, 80.0, _swipe))
		bob = 0.0
	# fingertip of hand.png sits at (51, 120)
	_hand.position = target + swipe - Vector2(51, 120 + bob)


## Where the hand should point, in HUD root units. x < -9000 means "nowhere".
func _target() -> Vector2:
	var none := Vector2(-9999, -9999)
	match Game.tutorial_step:
		0:
			var best := none
			var centre: Vector2 = hud._root.size * 0.5
			for f: Field in world.fields.values():
				if f.state == Field.State.EMPTY:
					var p := _screen(f.position)
					if p.distance_to(centre) < best.distance_to(centre):
						best = p
			return best
		1:
			for a: Animal in world.animals:
				if a.kind == "chicken":
					return _screen(a.position + Vector2(0, -60))
		2:
			_text.text = "TUT_2" if _field_ripe() else "TUT_2_WAIT"
			for f: Field in world.fields.values():
				if f.state == Field.State.RIPE:
					return _screen(f.position)
			return none
		3:
			for s in world.props:
				if s.get_meta("sprite", "") == "order_board":
					return _screen(s.position + Vector2(0, -120))
		4:
			return Vector2(330, 240)
	return none


func _field_ripe() -> bool:
	for f: Field in world.fields.values():
		if f.state == Field.State.RIPE:
			return true
	return false


func _screen(world_pos: Vector2) -> Vector2:
	var p: Vector2 = world.get_viewport().get_canvas_transform() * world_pos
	return p / hud._root.scale.x
