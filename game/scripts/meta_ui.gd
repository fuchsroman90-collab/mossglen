class_name MetaUI
extends Node
## Achievements window + trophy button, season chip, and the settings window
## (music, sounds, reduce motion, interface size, language, tutorial).
## Uses the HUD's widget helpers so it shares the 2D style.

const ROW_H := 158.0
const MEDALS := ["medal_bronze", "medal_silver", "medal_gold"]

var hud: Hud
var trophy: TextureButton
var _badge: Control
var _badge_label: Label
var _ach: Control
var _ach_list: VBoxContainer
var _settings: Control
var _toggles: Dictionary = {}  ## key -> TextureButton
var _text_value: Label
var _chip: TextureButton
var _chip_dot: Control
var _fest: Control
var _fest_body: Control
var _lang_value: Label


func setup(h: Hud) -> void:
	hud = h
	# trophy button under the dino-pedia button, with a red counter when something can be claimed
	trophy = hud._round_button("ico_trophy.png", Vector2(26, 640), 128)
	trophy.pressed.connect(open_achievements)
	_badge = hud._tex("badge.png")
	_badge.modulate = Color(1.0, 0.45, 0.35)
	_badge.position = Vector2(84, -6)
	trophy.add_child(_badge)
	_badge_label = hud._label("", 30)
	_badge_label.size = Vector2(56, 56)
	_badge_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_badge.add_child(_badge_label)
	_ach = hud._panel_window(Vector2(1500, 1020), "ACHIEVEMENTS")[0]
	var scroll := ScrollContainer.new()
	scroll.position = Vector2(40, 110)
	scroll.size = Vector2(1420, 870)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	_ach.add_child(scroll)
	_ach_list = VBoxContainer.new()
	_ach_list.custom_minimum_size = Vector2(1420, 0)
	_ach_list.add_theme_constant_override("separation", 10)
	scroll.add_child(_ach_list)
	hud.extra_windows.append(_ach)
	for sig in [Game.achievements_changed, Game.leveled_up, Game.fish_caught, Game.dino_hatched]:
		sig.connect(func(_a = null, _b = null) -> void: _refresh_badge())
	_build_season_chip()
	_build_settings()
	_refresh_badge()


# ------------------------------------------------------------------ achievements

func _refresh_badge() -> void:
	var n := Game.claimable_achievements()
	var was := _badge.visible and _badge_label.text != ""
	_badge.visible = n > 0
	_badge_label.text = str(n) if n > 0 else ""
	if n > 0 and not was:
		hud._pop(trophy, 1.25)
	if _ach.visible:
		_fill_achievements()
	_chip_dot.visible = Game.festival_claimable()
	if _fest.visible:
		_fill_festival()


func open_achievements() -> void:
	Audio.play("click")
	_fill_achievements()
	hud._open(_ach)


func _fill_achievements() -> void:
	for c in _ach_list.get_children():
		c.queue_free()
	# claimable first, then by progress
	var list: Array = Game.achievements.duplicate()
	list.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var ca := Game.ach_claimable(a)
		if ca != Game.ach_claimable(b):
			return ca
		return _ratio(a) > _ratio(b))
	for a in list:
		_ach_list.add_child(_ach_row(a))


func _ratio(a: Dictionary) -> float:
	var claimed := int(Game.ach_claimed.get(a["id"], 0))
	if claimed >= 3:
		return -1.0
	return float(Game.stat(a["stat"])) / float(a["tiers"][claimed])


func _ach_row(a: Dictionary) -> Control:
	var id: String = a["id"]
	var claimed := int(Game.ach_claimed.get(id, 0))
	var reached := Game.ach_reached(a)
	var row := hud._patch("panel.png", 44, 44)
	row.custom_minimum_size = Vector2(1420, ROW_H)
	row.self_modulate = Color(1.0, 0.97, 0.9) if claimed < 3 else Color(0.92, 1.0, 0.86)
	for i in 3:
		var m := hud._tex((MEDALS[i] if i < claimed else "medal_empty") + ".png")
		m.position = Vector2(30 + i * 62, 42)
		m.scale = Vector2(0.95, 0.95)
		row.add_child(m)
	var next := mini(claimed, 2)
	var target := int(a["tiers"][next])
	var title := hud._dark(hud._label("ACH_%s_T" % id, 40))
	title.position = Vector2(240, 18)
	title.size = Vector2(640, 56)
	row.add_child(title)
	var desc := hud._dark(hud._label(tr("ACH_%s_D" % id) % target, 30))
	desc.position = Vector2(240, 70)
	desc.size = Vector2(640, 44)
	desc.modulate.a = 0.85
	row.add_child(desc)
	# progress capsule
	var v := Game.stat(a["stat"])
	var back := hud._patch("bar_back.png", 32, 30)
	back.position = Vector2(900, 40)
	back.size = Vector2(300, 64)
	row.add_child(back)
	var k := clampf(float(v) / float(target), 0.0, 1.0) if claimed < 3 else 1.0
	var fill := hud._patch("bar_fill.png", 20, 18)
	fill.position = Vector2(12, 12)
	fill.size = Vector2(40.0 + 236.0 * k, 40)
	back.add_child(fill)
	var num := hud._label("%s / %s" % [Hud.fmt(mini(v, target)), Hud.fmt(target)] if claimed < 3 else "", 28)
	num.size = Vector2(300, 64)
	num.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	back.add_child(num)
	if reached > claimed:
		var gems := int(a["gems"][claimed])
		var b := hud._pill(tr("ACH_CLAIM") % gems, Vector2(1220, 30), 176)
		var gem := hud._tex("gem.png")
		gem.scale = Vector2(0.5, 0.5)
		gem.position = Vector2(112, 18)
		b.add_child(gem)
		(b.get_child(0) as Label).size.x = 120
		b.pressed.connect(func() -> void: _claim(id))
		row.add_child(b)
	elif claimed >= 3:
		var done := hud._dark(hud._label("ACH_DONE", 32))
		done.position = Vector2(1210, 40)
		done.size = Vector2(200, 64)
		done.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		row.add_child(done)
	return row


func _claim(id: String) -> void:
	var gems := Game.claim_achievement(id)
	if gems <= 0:
		return
	Audio.play("achieve")
	Game.toast.emit(tr("ACH_TOAST") % [tr("ACH_%s_T" % id), gems], "ico_trophy.png")
	_fill_achievements()
	_refresh_badge()


# ------------------------------------------------------------------ season

func _build_season_chip() -> void:
	var s := Game.season()
	_chip = TextureButton.new()
	_chip.texture_normal = load(Hud.UI + "season_%s.png" % s)
	_chip.ignore_texture_size = true
	_chip.stretch_mode = TextureButton.STRETCH_SCALE
	_chip.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_chip.offset_left = -112
	_chip.offset_top = 250
	_chip.offset_right = -24
	_chip.offset_bottom = 338
	_chip.focus_mode = Control.FOCUS_NONE
	hud._press_feedback(_chip)
	hud._root.add_child(_chip)
	_chip_dot = hud._tex("badge.png")
	_chip_dot.modulate = Color(1.0, 0.45, 0.35)
	_chip_dot.scale = Vector2(0.6, 0.6)
	_chip_dot.position = Vector2(58, -4)
	_chip.add_child(_chip_dot)
	_chip.pressed.connect(open_festival)
	_fest = hud._panel_window(Vector2(1160, 760), "")[0]
	_fest_body = Control.new()
	_fest.add_child(_fest_body)
	hud.extra_windows.append(_fest)


func open_festival() -> void:
	Audio.play("click")
	_fill_festival()
	hud._open(_fest)


func _fill_festival() -> void:
	for c in _fest_body.get_children():
		c.queue_free()
	var s := Game.season()
	var f := Game.festival_def()
	var st := Game.festival_state()
	(_fest.get_child(0) as Label).text = tr("FEST_" + s)
	var badge := hud._tex("season_%s.png" % s)
	badge.position = Vector2(60, 120)
	badge.scale = Vector2(2.2, 2.2)
	_fest_body.add_child(badge)
	var goal := hud._dark(hud._label("FEST_GOAL_" + s, 40))
	goal.position = Vector2(260, 120)
	goal.size = Vector2(840, 70)
	goal.autowrap_mode = TextServer.AUTOWRAP_WORD
	_fest_body.add_child(goal)
	var info := hud._dark(hud._label(tr("FEST_INFO") % _season_crops(), 32))
	info.position = Vector2(260, 196)
	info.size = Vector2(840, 90)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD
	info.modulate.a = 0.85
	_fest_body.add_child(info)
	# progress capsule with three stage medals
	var tiers: Array = f["tiers"]
	var top := float(tiers[2])
	var n := int(st["n"])
	var back := hud._patch("bar_back.png", 32, 30)
	back.position = Vector2(80, 360)
	back.size = Vector2(1000, 70)
	_fest_body.add_child(back)
	var fill := hud._patch("bar_fill.png", 20, 18)
	fill.position = Vector2(12, 13)
	fill.size = Vector2(44.0 + 932.0 * clampf(n / top, 0.0, 1.0), 44)
	back.add_child(fill)
	var num := hud._label("%d / %d" % [mini(n, int(top)), int(top)], 30)
	num.size = Vector2(1000, 70)
	num.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	back.add_child(num)
	for i in 3:
		var x := 80.0 + 950.0 * float(tiers[i]) / top
		var reached := n >= int(tiers[i])
		var m := hud._tex((MEDALS[i] if reached else "medal_empty") + ".png")
		m.position = Vector2(x - 36, 440)
		_fest_body.add_child(m)
		var c := int(f["coins"][i])
		var reward := hud._label("+%d" % (c if c > 0 else int(f["gems"][i])), 30)
		reward.position = Vector2(x - 110, 512)
		reward.size = Vector2(110, 56)
		reward.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		_fest_body.add_child(reward)
		var ic := hud._tex("coin.png" if c > 0 else "gem.png")
		ic.scale = Vector2(0.45, 0.45)
		ic.position = Vector2(x + 4, 514)
		_fest_body.add_child(ic)
		if i < int(st["claimed"]):
			var ok := hud._tex("ico_check.png")
			ok.position = Vector2(x - 32, 446)
			_fest_body.add_child(ok)
	if Game.festival_claimable():
		var b := hud._pill("FEST_CLAIM", Vector2(430, 600), 300)
		b.pressed.connect(func() -> void:
			var got := Game.claim_festival()
			if got.is_empty():
				return
			Audio.play("achieve")
			Game.toast.emit(tr("FEST_TOAST") % [tr("FEST_" + s), int(Game.festival_state()["claimed"])],
				"season_%s.png" % s)
			_refresh_badge())
		_fest_body.add_child(b)


func _season_crops() -> String:
	var names: Array = []
	for c in Game.crop_order:
		if Game.in_season(c):
			names.append(tr("ITEM_" + c))
	return ", ".join(names) if not names.is_empty() else "-"


# ------------------------------------------------------------------ settings

func _build_settings() -> void:
	var w := 760.0
	_settings = hud._panel_window(Vector2(w, 760), "SETTINGS")[0]
	var y := 120.0
	_toggle_row("SET_MUSIC", "ico_note.png", y, func() -> bool: return Audio.music_enabled, func(on: bool) -> void:
		Audio.set_music_enabled(on)
		Game.mark_dirty())
	y += 104
	_toggle_row("SET_SFX", "", y, func() -> bool: return bool(Game.settings["sfx"]), func(on: bool) -> void:
		Game.set_setting("sfx", on))
	y += 104
	_toggle_row("SET_MOTION", "", y, func() -> bool: return bool(Game.settings["reduce_motion"]),
		func(on: bool) -> void: Game.set_setting("reduce_motion", on))
	y += 104
	_text_value = _value_row("SET_TEXT", y, func() -> void:
		var steps := [1.0, 1.15, 1.3]
		var i := steps.find(float(Game.settings["text"]))
		Game.set_setting("text", steps[(i + 1) % steps.size()])
		_sync())
	y += 104
	_lang_value = _value_row("SET_LANG", y, func() -> void:
		Game.toggle_language()
		_sync())
	y += 116
	var tut := hud._pill("SET_TUTORIAL", Vector2(60, y), w - 120)
	tut.pressed.connect(func() -> void:
		Audio.play("click")
		hide_settings()
		Game.tutorial_step = 0
		Game.mark_dirty()
		hud.tutorial.restart())
	_settings.add_child(tut)
	_sync()


func _row_label(key: String, y: float) -> void:
	var l := hud._dark(hud._label(key, 40))
	l.position = Vector2(60, y)
	l.size = Vector2(440, 84)
	_settings.add_child(l)


func _toggle_row(key: String, _icon: String, y: float, getter: Callable, setter: Callable) -> void:
	_row_label(key, y)
	var b := TextureButton.new()
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	b.position = Vector2(560, y + 6)
	b.size = Vector2(144, 77)
	b.focus_mode = Control.FOCUS_NONE
	b.set_meta("get", getter)
	hud._press_feedback(b)
	b.pressed.connect(func() -> void:
		Audio.play("click")
		setter.call(not getter.call())
		_sync())
	_settings.add_child(b)
	_toggles[key] = b


func _value_row(key: String, y: float, on_press: Callable) -> Label:
	_row_label(key, y)
	var b := hud._pill("", Vector2(500, y), 204)
	b.pressed.connect(func() -> void:
		Audio.play("click")
		on_press.call())
	_settings.add_child(b)
	return b.get_child(0) as Label


func _sync() -> void:
	for key in _toggles:
		var b: TextureButton = _toggles[key]
		var on: bool = (b.get_meta("get") as Callable).call()
		b.texture_normal = load(Hud.UI + ("toggle_on.png" if on else "toggle_off.png"))
	_text_value.text = "%d %%" % roundi(float(Game.settings["text"]) * 100.0)
	_lang_value.text = "SET_LANG_VALUE"


func is_settings_open() -> bool:
	return _settings.visible


func toggle_settings() -> void:
	Audio.play("click")
	if _settings.visible:
		hide_settings()
		return
	_sync()
	hud._open(_settings)


func hide_settings() -> void:
	_settings.hide()
