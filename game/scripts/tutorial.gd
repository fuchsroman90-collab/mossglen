class_name Tutorial
extends Node
## First-time guide: a pointing hand over the thing to tap and a short text box.
## Steps (M9.5, empty farm): 0 sow wheat, 1 clear a tree with the axe, 2 harvest, 3 build a chicken coop,
## 4 deliver an order with the truck, 5 collect the truck's coins, 6 open Brumm's quest.
## Progress is Game.tutorial_step (-1 = done or skipped). Each step advances on a game event.

const STEPS := 7

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
		if Game.tutorial_step == 6 and (Game.quest_stage != "intro" or Game.quest_index > 0):
			_advance())
	_show()


func active() -> bool:
	return Game.tutorial_step >= 0 and Game.tutorial_step < STEPS


func restart() -> void:
	Game.tutorial_step = 0
	_show()


func _on_event(type: String, _id: String) -> void:
	var want: Array = [["plant"], ["clear"], ["harvest"], ["build"], ["deliver"], ["truck"]]
	var st := Game.tutorial_step
	if st >= 0 and st < want.size() and type in want[st]:
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
	var shop_step: bool = Game.tutorial_step == 3 and hud.land.is_shop_open()
	var busy: bool = hud.any_menu_open() and not shop_step
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
			return _nearest_field(Field.State.EMPTY)
		1:
			var best := none
			var centre: Vector2 = hud._root.size * 0.5
			for o: Sprite2D in world.farm.obstacles.values():
				if o.get_meta("tool") == "axe" and Farm.cell_open(world.cell_at(o.position)):
					var p := _screen(o.position + Vector2(0, -80))
					if p.distance_to(centre) < best.distance_to(centre):
						best = p
			return best
		2:
			_text.text = "TUT_2" if _field_ripe() else "TUT_2_WAIT"
			return _nearest_field(Field.State.RIPE)
		3:
			# shop button -> coop card (animals tab) -> place it -> tap the finished site
			for i in world.farm.sites:
				if Game.placed[i]["k"] == "coop":
					var site: Sprite2D = world.farm.sites[i]
					var ready: bool = world.farm.site_left(i) <= 0.0
					_text.text = "TUT_3_DONE" if ready else "TUT_3_WAIT"
					return _screen(site.position + Vector2(0, -60)) if ready else none
			if world._place_kind != "":
				_text.text = "TUT_3_PLACE"
				return none
			if hud.land.is_shop_open():
				_text.text = "TUT_3_SHOP"
				if hud.land._shop_tab != "animals":
					hud.land._shop_tab = "animals"
					hud.land._fill_shop()
				return Vector2(205, hud._root.size.y - 90)
			_text.text = "TUT_3"
			return Vector2(150, hud._root.size.y - 150)
		4:
			var b: Sprite2D = world.farm.fixed.get("order_board")
			return _screen(b.position + Vector2(0, -120)) if b else none
		5:
			if not world.farm.truck_waiting():
				_text.text = "TUT_5_WAIT"
				return none
			_text.text = "TUT_5"
			return _screen(world.farm.truck.position + Vector2(0, -90))
		6:
			return Vector2(330, 240)
	return none


func _nearest_field(state: Field.State) -> Vector2:
	var best := Vector2(-9999, -9999)
	var centre: Vector2 = hud._root.size * 0.5
	for f: Field in world.fields.values():
		if f.state == state:
			var p := _screen(f.position)
			if p.distance_to(centre) < best.distance_to(centre):
				best = p
	return best


func _field_ripe() -> bool:
	for f: Field in world.fields.values():
		if f.state == Field.State.RIPE:
			return true
	return false


func _screen(world_pos: Vector2) -> Vector2:
	var p: Vector2 = world.get_viewport().get_canvas_transform() * world_pos
	return p / hud._root.scale.x
