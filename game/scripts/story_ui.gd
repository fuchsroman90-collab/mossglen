class_name StoryUI
extends Node
## Story UI: dialogue box, quest tracker, village windows (restore, market, museum, library).
## Uses the HUD's widget helpers so everything shares the 2D style.

var hud: Hud
var _dialog: Control
var _portrait: TextureRect
var _name: Label
var _text: Label
var _lines: Array = []
var _line := 0
var _chars := 0.0
var _npc := ""
var _tracker: Control
var _tracker_icon: TextureRect
var _tracker_text: Label
var _village: Control
var _village_body: Control


func setup(h: Hud) -> void:
	hud = h
	# quest tracker under the left buttons
	_tracker = hud._patch("panel.png", 44, 44)
	_tracker.position = Vector2(170, 130)
	_tracker.size = Vector2(560, 150)
	_tracker.mouse_filter = Control.MOUSE_FILTER_STOP
	hud._root.add_child(_tracker)
	_tracker_icon = TextureRect.new()
	_tracker_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_tracker_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_tracker_icon.position = Vector2(18, 14)
	_tracker_icon.size = Vector2(110, 120)
	_tracker_icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tracker.add_child(_tracker_icon)
	_tracker_text = hud._dark(hud._label("", 30))
	_tracker_text.position = Vector2(136, 12)
	_tracker_text.size = Vector2(404, 126)
	_tracker_text.autowrap_mode = TextServer.AUTOWRAP_WORD
	_tracker.add_child(_tracker_text)
	_tracker.gui_input.connect(func(e: InputEvent) -> void:
		var tap: bool = (e is InputEventMouseButton and e.pressed) or (e is InputEventScreenTouch and e.pressed)
		if tap and not Game.quest().is_empty():
			talk(Game.quest()["npc"]))
	# dialogue box
	_dialog = hud._patch("panel.png", 44, 44)
	_dialog.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_dialog.offset_left = -900
	_dialog.offset_right = 900
	_dialog.offset_top = -420
	_dialog.offset_bottom = -60
	_dialog.mouse_filter = Control.MOUSE_FILTER_STOP
	_dialog.visible = false
	hud._root.add_child(_dialog)
	_portrait = TextureRect.new()
	_portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_portrait.position = Vector2(30, -120)
	_portrait.size = Vector2(320, 440)
	_portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_dialog.add_child(_portrait)
	_name = hud._label("", 46)
	_name.position = Vector2(380, 24)
	_name.size = Vector2(1000, 64)
	_dialog.add_child(_name)
	_text = hud._dark(hud._label("", 40))
	_text.position = Vector2(380, 96)
	_text.size = Vector2(1360, 220)
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD
	_text.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_dialog.add_child(_text)
	var more := hud._label("▶", 40)
	more.position = Vector2(1710, 270)
	more.size = Vector2(60, 60)
	_dialog.add_child(more)
	_dialog.gui_input.connect(_on_dialog_input)
	# village window (restore / market / museum / library)
	_village = hud._panel_window(Vector2(1300, 760), "")[0]
	_village_body = Control.new()
	_village.add_child(_village_body)
	hud.extra_windows.append(_village)
	Game.quest_changed.connect(refresh_tracker)
	refresh_tracker()


func is_open() -> bool:
	return _dialog.visible


func _process(delta: float) -> void:
	if _dialog.visible and _line < _lines.size():
		var full: String = _lines[_line]
		if _chars < full.length():
			_chars += delta * 55.0
			_text.text = full.substr(0, int(_chars))


# ------------------------------------------------------------------ dialogue

func talk(npc: String) -> void:
	var lines := Game.talk(npc)
	if lines.is_empty():
		var q := Game.quest()
		if not q.is_empty() and q["npc"] == npc:
			lines = [goal_text()]
		else:
			lines = [tr("NPC_IDLE_" + npc)]
	_npc = npc
	_lines = lines
	_line = 0
	_chars = 0.0
	_portrait.texture = Atlas.tex("npc_%s_0" % npc)
	_name.text = Game.npc_name(npc)
	_text.text = ""
	hud.close_menus()
	hud.hide_hint()
	_dialog.visible = true
	_dialog.pivot_offset = _dialog.size / 2
	_dialog.scale = Vector2(0.8, 0.8)
	hud.create_tween().tween_property(_dialog, "scale", Vector2.ONE, 0.2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	Audio.play("pop", 1.1)


func _on_dialog_input(e: InputEvent) -> void:
	var tap: bool = (e is InputEventMouseButton and e.pressed) or (e is InputEventScreenTouch and e.pressed)
	if not tap:
		return
	var full: String = _lines[_line]
	if _chars < full.length():
		_chars = full.length()
		_text.text = full
		return
	_line += 1
	_chars = 0.0
	Audio.play("click")
	if _line >= _lines.size():
		_dialog.visible = false


# ------------------------------------------------------------------ tracker

func goal_text() -> String:
	var q := Game.quest()
	if q.is_empty():
		return tr("QUEST_ALL_DONE")
	var g: Dictionary = q["goal"]
	var who := Game.npc_name(q["npc"])
	match Game.quest_stage:
		"intro":
			return tr("QUEST_TALK") % who
		"ready":
			return tr("QUEST_RETURN") % who
	var what := ""
	if g["id"] == "any":
		what = ""
	elif g["type"] == "restore":
		what = tr("VILLAGE_" + str(g["id"]))
	else:
		what = tr("ITEM_" + str(g["id"]))
	return tr("GOAL_" + str(g["type"])) % [what, Game.quest_progress, int(g["n"])]


func refresh_tracker() -> void:
	var q := Game.quest()
	if q.is_empty():
		_tracker.visible = false
		return
	_tracker.visible = true
	_tracker_icon.texture = Atlas.tex("npc_%s_0" % q["npc"])
	_tracker_text.text = goal_text()
	_tracker.pivot_offset = Vector2(0, 75)
	_tracker.scale = Vector2(1.08, 1.08)
	hud.create_tween().tween_property(_tracker, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


# ------------------------------------------------------------------ village windows

func _window(title: String, h: float) -> void:
	for c in _village_body.get_children():
		c.queue_free()
	(_village.get_child(0) as Label).text = title
	_village.size.y = h
	_village.offset_top = -h / 2
	_village.offset_bottom = h / 2
	hud._open(_village)
	Audio.play("whoosh")


func open_restore(id: String) -> void:
	var d := Game.restore_def(id)
	_window(tr("VILLAGE_" + id), 700)
	var info := hud._dark(hud._label(tr("RESTORE_INFO_" + id), 34))
	info.position = Vector2(60, 100)
	info.size = Vector2(1180, 110)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD
	_village_body.add_child(info)
	var x := 60.0
	for k in d["need"]:
		var sl := hud._tex("slot.png")
		sl.position = Vector2(x, 240)
		_village_body.add_child(sl)
		var ic := hud._item_icon(k, 100)
		ic.position = Vector2(x + 14, 252)
		_village_body.add_child(ic)
		var c := hud._label("%d/%d" % [Game.count(k), int(d["need"][k])], 34)
		c.position = Vector2(x - 10, 380)
		c.size = Vector2(148, 50)
		c.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		if Game.count(k) < int(d["need"][k]):
			c.add_theme_color_override("font_color", Color("FF8A80"))
		_village_body.add_child(c)
		x += 170.0
	var coin := hud._tex("coin.png")
	coin.scale = Vector2(0.8, 0.8)
	coin.position = Vector2(x + 20, 262)
	_village_body.add_child(coin)
	var cl := hud._label(str(int(d["coins"])), 44)
	cl.position = Vector2(x + 110, 262)
	cl.size = Vector2(200, 80)
	if Game.coins < int(d["coins"]):
		cl.add_theme_color_override("font_color", Color("FF8A80"))
	_village_body.add_child(cl)
	if Game.level < int(d["unlock"]):
		var lv := hud._dark(hud._label(tr("FROM_LEVEL") % int(d["unlock"]), 40))
		lv.position = Vector2(60, 500)
		lv.size = Vector2(1180, 70)
		lv.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_village_body.add_child(lv)
		return
	var go := hud._pill("RESTORE", Vector2(450, 490), 400, Game.can_restore(id))
	_village_body.add_child(go)
	go.pressed.connect(func() -> void:
		if Game.restore(id):
			Audio.play("levelup")
			_village.hide()
			Game.toast.emit(tr("RESTORED") % tr("VILLAGE_" + id), "ico_check.png"))


func open_market() -> void:
	_window(tr("VILLAGE_market"), 640)
	var info := hud._dark(hud._label("MARKET_INFO", 34))
	info.position = Vector2(60, 100)
	info.size = Vector2(1180, 80)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD
	_village_body.add_child(info)
	var wishes := Game.market_wishes()
	for i in wishes.size():
		var it: String = wishes[i]
		var x := 80.0 + i * 400.0
		var sl := hud._tex("slot.png")
		sl.scale = Vector2(1.2, 1.2)
		sl.position = Vector2(x + 90, 210)
		_village_body.add_child(sl)
		var ic := hud._item_icon(it, 120)
		ic.position = Vector2(x + 106, 226)
		_village_body.add_child(ic)
		var nm := hud._dark(hud._label("ITEM_" + it, 34))
		nm.position = Vector2(x, 380)
		nm.size = Vector2(340, 50)
		nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_village_body.add_child(nm)
		var b := hud._pill("", Vector2(x + 30, 440), 280, Game.count(it) > 0)
		_village_body.add_child(b)
		var coin := hud._tex("coin.png")
		coin.scale = Vector2(0.55, 0.55)
		coin.position = Vector2(30, 14)
		b.add_child(coin)
		var p := hud._label("%d  (×%d)" % [int(ceil(Game.price(it) * 1.5)), Game.count(it)], 34)
		p.position = Vector2(90, 0)
		p.size = Vector2(180, 86)
		b.add_child(p)
		b.pressed.connect(func() -> void:
			if Game.sell_market(it) > 0:
				Audio.play("coin")
				open_market())


func open_museum() -> void:
	_window(tr("VILLAGE_museum"), 640)
	var caught := Game.fish_log.size()
	var seen := Game.dino_seen.size()
	var lines := [tr("MUSEUM_FOSSILS") % Game.museum_fossils, tr("MUSEUM_FISH") % [caught, Game.fish.size()],
		tr("MUSEUM_DINOS") % [seen, Game.dinos.size()]]
	for i in lines.size():
		var l := hud._dark(hud._label(lines[i], 40))
		l.position = Vector2(80, 110 + i * 80)
		l.size = Vector2(1140, 70)
		_village_body.add_child(l)
	var b := hud._pill("DONATE_FOSSIL", Vector2(380, 420), 540, Game.count("fossil") > 0)
	_village_body.add_child(b)
	b.pressed.connect(func() -> void:
		if Game.donate_fossil():
			Audio.play("levelup", 1.3)
			open_museum())


func open_library() -> void:
	_window(tr("VILLAGE_library"), 820)
	var qs: Array = Game.story["quests"]
	var de := TranslationServer.get_locale().begins_with("de")
	var text := ""
	for i in mini(Game.quest_index, qs.size()):
		text += "• %s: %s\n" % [Game.npc_name(qs[i]["npc"]), qs[i]["done_de" if de else "done_en"]]
	if text == "":
		text = tr("LIBRARY_EMPTY")
	var l := hud._dark(hud._label(text, 32))
	l.position = Vector2(70, 100)
	l.size = Vector2(1160, 680)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	l.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_village_body.add_child(l)
