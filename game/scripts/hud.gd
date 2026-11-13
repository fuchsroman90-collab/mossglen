class_name Hud
extends CanvasLayer
## 2D HUD (flat vector pieces from tools/art/ui.py), laid out like the reference HUD:
## level star + XP bar top left, big outlined numbers with coin/gem and "+" top right,
## round yellow buttons on the left, big shop button bottom left.
## Authored in 2x units inside a root control scaled by 0.5.

signal shop_pressed
signal seed_chosen(crop: String)
signal buy_field
signal place_confirm
signal place_cancel

const UI := "res://art/generated/ui/"
const OUTLINE := Color("3A2410")
const WHITE := Color("FFFFFF")

var coin_target: Control  ## where flying coins land
var _root: Control
var _coin_label: Label
var _gem_label: Label
var _level_label: Label
var _xp_label: Label
var _xp_fill: NinePatchRect
var _settings: Control
var _fps_label: Label
var _hint: Label
var _picker: Control
var _picker_t := 0.0
var _barn: Control
var _barn_rows: Control
var _barn_title: Label
var _shop: Control
var _place_bar: Control
var _info: Control
var _info_t := 0.0
var _toasts: Control
var _prod: Control
var _prod_b: ProductionBuilding
var _prod_body: Control
var _prod_progress: Array = []  ## [fill NinePatchRect, time Label]
var _orders: Control
var _orders_body: Control
var _refresh_t := 0.0
var _album: Control
var _album_body: Control
var fishing: FishingUI = null
var story: StoryUI
var extra_windows: Array[Control] = []
var meta: MetaUI
var land: LandUI
var tutorial: Tutorial
var _pedia: Control
var _pedia_body: Control

## Level star at STAR_POS; its right tip (in star.png pixels) defines where the XP bar starts.
const STAR_POS := Vector2(14, 4)
const STAR_TIP := Vector2(148.5, 62.0)
const XP_W := 470.0
const XP_H := 72.0
const XP_TUCK := 24.0  ## how far the star tip reaches into the bar


func _ready() -> void:
	_root = Control.new()
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.scale = Vector2(0.5, 0.5)
	add_child(_root)
	get_viewport().size_changed.connect(_fit)
	Game.settings_changed.connect(_fit)
	_fit()

	# XP bar and level star as one unit: the star's right tip reaches into the bar's left end
	var tip := STAR_POS + STAR_TIP
	var xp := Control.new()
	xp.mouse_filter = Control.MOUSE_FILTER_IGNORE
	xp.position = Vector2(tip.x - XP_TUCK, tip.y - XP_H / 2).round()
	_root.add_child(xp)
	var frame := _tex("xp_frame.png")
	xp.add_child(frame)
	_xp_fill = _patch("bar_fill.png", 20, 18)
	_xp_fill.position = Vector2(13, 14)
	_xp_fill.size = Vector2(44, 44)
	xp.add_child(_xp_fill)
	_xp_label = _label("", 36)
	_xp_label.position = Vector2(XP_TUCK + 10, 0)
	_xp_label.size = Vector2(XP_W - XP_TUCK - 20, XP_H)
	_xp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	xp.add_child(_xp_label)
	var star := _tex("star.png")
	star.position = STAR_POS
	_root.add_child(star)
	_level_label = _label(str(Game.level), 62)
	_level_label.position = STAR_POS + Vector2(0, 30)
	_level_label.size = Vector2(160, 100)
	_level_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_root.add_child(_level_label)

	# currencies, top right: big number, icon, plus button
	var c := _currency("coin.png", Game.coins, 0)
	_coin_label = c[0]
	coin_target = c[1]
	_gem_label = _currency("gem.png", Game.emeralds, 1)[0]

	# left column: settings
	var gear := _round_button("ico_gear.png", Vector2(26, 190), 128)
	gear.pressed.connect(_toggle_settings)
	var album := _round_button("ico_book.png", Vector2(26, 340), 128)
	album.pressed.connect(open_album)
	var pedia := _round_button("ico_dino.png", Vector2(26, 490), 128)
	pedia.pressed.connect(open_dinopedia)
	# bottom left: shop (build / seeds menu)
	var shop := _round_button("ico_shop.png", Vector2(20, -250), 196, true)
	shop.pressed.connect(func() -> void:
		Audio.play("click")
		shop_pressed.emit())

	meta = MetaUI.new()
	add_child(meta)
	meta.setup(self)
	land = LandUI.new()
	add_child(land)
	land.setup(self)
	_settings = meta._settings
	story = StoryUI.new()
	add_child(story)
	story.setup(self)
	_build_barn()
	_build_shop()
	_build_place_bar()
	_prod = _panel_window(Vector2(1180, 600), "")[0]
	_prod_body = Control.new()
	_prod.add_child(_prod_body)
	_album = _panel_window(Vector2(1480, 1000), "ALBUM")[0]
	_album_body = Control.new()
	_album.add_child(_album_body)
	_pedia = _panel_window(Vector2(1500, 900), "DINOPEDIA")[0]
	_pedia_body = Control.new()
	_pedia.add_child(_pedia_body)
	_orders = _panel_window(Vector2(1320, 900), "ORDERS")[0]
	_orders_body = Control.new()
	_orders.add_child(_orders_body)
	Game.orders_changed.connect(func() -> void:
		if _orders.visible:
			_fill_orders())
	_toasts = Control.new()
	_toasts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_toasts.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_toasts.offset_top = 230
	_root.add_child(_toasts)
	Game.toast.connect(toast)
	Game.inventory_changed.connect(func(_i: String, _c: int) -> void:
		_fill_barn()
		if _prod.visible:
			_fill_prod()
		if _orders.visible:
			_fill_orders())

	_hint = _label("HINT_START", 42)
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_hint.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_hint.offset_top = -150
	_hint.offset_bottom = -86
	_root.add_child(_hint)

	_fps_label = _label("", 24)
	_fps_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_fps_label.offset_left = -170
	_fps_label.offset_top = -50
	_fps_label.modulate.a = 0.6
	_root.add_child(_fps_label)

	Game.coins_changed.connect(func(v: int) -> void: _set_number(_coin_label, v))
	Game.emeralds_changed.connect(func(v: int) -> void: _set_number(_gem_label, v))
	Game.xp_changed.connect(_on_xp)
	_on_xp(Game.xp, Game.xp_needed(), Game.level)
	tutorial = Tutorial.new()
	add_child(tutorial)
	tutorial.setup(self)


func _fit() -> void:
	var k := 0.5 * float(Game.settings["text"])
	_root.scale = Vector2(k, k)
	_root.size = get_viewport().get_visible_rect().size / k


func _process(delta: float) -> void:
	_fps_label.text = "%d FPS" % Engine.get_frames_per_second()
	if _picker != null and _picker.visible:
		_picker_t -= delta
		if _picker_t <= 0.0:
			hide_seed_picker()
	if _info != null and _info.visible:
		_info_t -= delta
		if _info_t <= 0.0:
			_info.hide()
	_refresh_t += delta
	if _refresh_t >= 0.25:
		_refresh_t = 0.0
		if _prod.visible and _prod_b != null and not _prod_progress.is_empty():
			var pr := _prod_b.current_progress()
			(_prod_progress[0] as Control).size.x = 22.0 + 64.0 * pr.y
			(_prod_progress[1] as Label).text = _fmt_time(int(ceil(pr.x)))
		if _orders.visible:
			for c in _orders_body.get_children():
				if c.has_meta("wait_label"):
					var i: int = c.get_meta("index")
					var left := int(ceil(float(Game.orders[i]["wait_until"]) - Time.get_unix_time_from_system()))
					if left <= 0:
						_fill_orders()
						break
					(c.get_meta("wait_label") as Label).text = _fmt_time(left)


func any_menu_open() -> bool:
	return _barn.visible or _shop.visible or _settings.visible or _prod.visible or _orders.visible \
			or _album.visible or _pedia.visible or fishing != null or story.is_open() \
			or extra_windows.any(func(w: Control) -> bool: return w.visible)


static func _fmt_time(sec: int) -> String:
	sec = maxi(0, sec)
	if sec >= 3600:
		return "%d:%02d:%02d" % [sec / 3600, (sec / 60) % 60, sec % 60]
	return "%d:%02d" % [sec / 60, sec % 60]


func close_menus() -> void:
	for m in [_barn, _shop, _settings, _prod, _orders, _album, _pedia]:
		m.hide()
	for w in extra_windows:
		w.hide()
	hide_seed_picker()


func hide_hint() -> void:
	if _hint.visible and _hint.modulate.a >= 1.0:
		create_tween().tween_property(_hint, "modulate:a", 0.0, 0.6).finished.connect(_hint.hide)


func _on_xp(xp: int, needed: int, level: int) -> void:
	# fill starts hidden under the star tip so even 0 XP shows a small blue cap
	var w := XP_TUCK + 20.0 + (XP_W - 26.0 - XP_TUCK - 20.0) * float(xp) / float(needed)
	create_tween().tween_property(_xp_fill, "size:x", w, 0.35).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	_xp_label.text = "%d / %d" % [xp, needed]
	if _level_label.text != str(level):
		_level_label.text = str(level)
		_pop(_level_label, 1.7)


## Thousands separated with a thin space, like the reference ("4 852 770").
static func fmt(v: int) -> String:
	var s := str(absi(v))
	var out := ""
	while s.length() > 3:
		out = " " + s.substr(s.length() - 3) + out
		s = s.substr(0, s.length() - 3)
	return ("-" if v < 0 else "") + s + out


func _set_number(label: Label, v: int) -> void:
	label.text = fmt(v)
	_pop(label, 1.25)


func _pop(c: Control, s: float) -> void:
	c.pivot_offset = c.size / 2
	c.scale = Vector2(s, s)
	create_tween().tween_property(c, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


# ------------------------------------------------------------------ seed picker

## Row of seed slots above a field. screen_pos is in viewport pixels.
func show_seed_picker(screen_pos: Vector2, selected: String) -> void:
	hide_seed_picker()
	_picker = Control.new()
	_picker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(_picker)
	var n := Game.crop_order.size()
	var w := n * 132.0
	var p := screen_pos / _root.scale.x - Vector2(w * 0.5, 290)
	p.x = clampf(p.x, 20, _root.size.x - w - 20)
	p.y = clampf(p.y, 200, _root.size.y - 300)
	_picker.position = p
	for i in n:
		var crop: String = Game.crop_order[i]
		var b := TextureButton.new()
		b.texture_normal = load(UI + "slot.png")
		b.ignore_texture_size = true
		b.stretch_mode = TextureButton.STRETCH_SCALE
		b.position = Vector2(i * 132, 0)
		b.size = Vector2(124, 130)
		b.focus_mode = Control.FOCUS_NONE
		_picker.add_child(b)
		var icon := _tex("item_%s.png" % crop)
		icon.scale = Vector2(0.86, 0.86)
		icon.position = Vector2(14, 10)
		b.add_child(icon)
		if Game.is_unlocked(crop):
			var badge := _tex("badge.png")
			badge.position = Vector2(80, 82)
			b.add_child(badge)
			var c := _label(str(Game.count(crop)), 32)
			c.position = Vector2(80, 82)
			c.size = Vector2(56, 56)
			c.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			b.add_child(c)
			if Game.count(crop) == 0:
				icon.modulate = Color(1, 1, 1, 0.45)
			b.pressed.connect(func() -> void:
				Audio.play("click")
				seed_chosen.emit(crop)
				hide_seed_picker())
		else:
			icon.modulate = Color(0.35, 0.35, 0.35, 0.8)
			var lock := _tex("lock.png")
			lock.position = Vector2(30, 24)
			b.add_child(lock)
			var lv := _label(tr("FROM_LEVEL") % int(Game.crops[crop]["unlock"]), 28)
			lv.position = Vector2(0, 92)
			lv.size = Vector2(124, 40)
			lv.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			b.add_child(lv)
			b.disabled = true
		if crop == selected:
			b.pivot_offset = b.size / 2
			b.scale = Vector2(1.12, 1.12)
		# staggered pop-in
		b.modulate.a = 0.0
		var tw := b.create_tween()
		tw.tween_interval(i * 0.04)
		tw.tween_property(b, "modulate:a", 1.0, 0.12)
	_picker_t = 5.0


func hide_seed_picker() -> void:
	if _picker != null:
		_picker.queue_free()
		_picker = null


# ------------------------------------------------------------------ field info bubble

func show_field_info(screen_pos: Vector2, crop: String, seconds: int, progress: float) -> void:
	if _info == null:
		_info = _patch("panel.png", 44, 44)
		_info.size = Vector2(340, 170)
		_root.add_child(_info)
		var name_l := _dark(_label("", 36))
		name_l.name = "Name"
		name_l.position = Vector2(0, 18)
		name_l.size = Vector2(340, 50)
		name_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_info.add_child(name_l)
		var back := _patch("bar_back.png", 32, 30)
		back.position = Vector2(30, 70)
		back.size = Vector2(280, 60)
		_info.add_child(back)
		var fill := _patch("bar_fill.png", 18, 16)
		fill.name = "Fill"
		fill.position = Vector2(42, 81)
		fill.size = Vector2(40, 38)
		_info.add_child(fill)
		var t := _label("", 30)
		t.name = "Time"
		t.position = Vector2(30, 68)
		t.size = Vector2(280, 62)
		t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_info.add_child(t)
	(_info.get_node("Name") as Label).text = "ITEM_" + crop
	(_info.get_node("Fill") as Control).size.x = maxf(38.0, 256.0 * progress)
	(_info.get_node("Time") as Label).text = "%d:%02d" % [seconds / 60, seconds % 60] if seconds > 0 else tr("READY")
	_info.position = screen_pos / _root.scale.x - Vector2(170, 260)
	_info.show()
	_info_t = 2.2


# ------------------------------------------------------------------ toast

func toast(text: String, icon_file := "") -> void:
	var box := Control.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_toasts.add_child(box)
	var l := _label(text, 48)
	l.size = Vector2(1400, 80)
	l.position = Vector2(-700, 0)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(l)
	if icon_file != "":
		var ic := _tex(icon_file)
		ic.position = Vector2(-56, -110)
		box.add_child(ic)
	box.position.y = _toasts.get_child_count() * 20.0
	box.scale = Vector2(0.5, 0.5)
	var tw := box.create_tween()
	tw.tween_property(box, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_interval(1.8)
	tw.tween_property(box, "modulate:a", 0.0, 0.4)
	tw.tween_callback(box.queue_free)


# ------------------------------------------------------------------ barn (inventory + selling)

func _panel_window(size: Vector2, title_key: String) -> Array:
	var p := _patch("panel.png", 44, 44)
	p.mouse_filter = Control.MOUSE_FILTER_STOP
	p.size = size
	p.set_anchors_preset(Control.PRESET_CENTER)
	p.offset_left = -size.x / 2
	p.offset_top = -size.y / 2
	p.offset_right = size.x / 2
	p.offset_bottom = size.y / 2
	p.visible = false
	_root.add_child(p)
	var title := _label(title_key, 54)
	title.position = Vector2(0, 12)
	title.size = Vector2(size.x, 80)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	p.add_child(title)
	var close := TextureButton.new()
	close.texture_normal = load(UI + "btn_round.png")
	close.ignore_texture_size = true
	close.stretch_mode = TextureButton.STRETCH_SCALE
	close.position = Vector2(size.x - 70, -30)
	close.size = Vector2(96, 102)
	close.focus_mode = Control.FOCUS_NONE
	_press_feedback(close)
	close.pressed.connect(func() -> void:
		Audio.play("click")
		p.hide())
	p.add_child(close)
	var x := _tex("ico_close.png")
	x.position = Vector2(16, 16)
	close.add_child(x)
	return [p, title]


func _open(p: Control) -> void:
	close_menus()
	p.show()
	p.pivot_offset = p.size / 2
	p.scale = Vector2(0.7, 0.7)
	create_tween().tween_property(p, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _build_barn() -> void:
	var w := _panel_window(Vector2(980, 860), "BARN")
	_barn = w[0]
	_barn_title = w[1]
	_barn_rows = Control.new()
	_barn_rows.position = Vector2(50, 110)
	_barn.add_child(_barn_rows)


func open_barn(silo := false) -> void:
	land.open_store(silo)


func _fill_barn() -> void:
	land.refresh_store()


## Green capsule button with a text label.
func _pill(key: String, pos: Vector2, width: float, enabled := true) -> TextureButton:
	var b := TextureButton.new()
	b.texture_normal = load(UI + "pill_green.png")
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	b.position = pos
	b.size = Vector2(width, 96)
	b.focus_mode = Control.FOCUS_NONE
	b.disabled = not enabled
	if not enabled:
		b.modulate = Color(1, 1, 1, 0.45)
	_press_feedback(b)
	var l := _label(key, 34)
	l.size = Vector2(width, 86)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	b.add_child(l)
	return b


# ------------------------------------------------------------------ shop

func _build_shop() -> void:
	_shop = _panel_window(Vector2(760, 470), "SHOP")[0]


func open_shop() -> void:
	land.open_shop()

func open_dinopedia() -> void:
	Audio.play("click")
	_fill_pedia("")
	_open(_pedia)


func _fill_pedia(selected: String) -> void:
	for c in _pedia_body.get_children():
		c.queue_free()
	var seen := 0
	for i in Game.dinos.size():
		var d: Dictionary = Game.dinos[i]
		var known := Game.dino_seen.has(d["id"])
		if known:
			seen += 1
		var b := TextureButton.new()
		b.texture_normal = load(UI + "slot.png")
		b.ignore_texture_size = true
		b.stretch_mode = TextureButton.STRETCH_SCALE
		b.position = Vector2(70 + (i % 5) * 280, 110 + (i / 5) * 290)
		b.size = Vector2(250, 262)
		b.focus_mode = Control.FOCUS_NONE
		if d["id"] == selected:
			b.modulate = Color(1.0, 0.95, 0.7)
		_pedia_body.add_child(b)
		var ic := _item_icon("dino_" + str(d["id"]), 210)
		ic.position = Vector2(20, 20)
		if not known:
			ic.modulate = Color(0.1, 0.12, 0.18, 0.35)
		b.add_child(ic)
		var stars := ""
		for k in int(d["rarity"]):
			stars += "★"
		var st := _label(stars, 30)
		st.position = Vector2(0, 214)
		st.size = Vector2(250, 40)
		st.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.add_child(st)
		var did: String = d["id"]
		b.pressed.connect(func() -> void:
			Audio.play("click")
			_fill_pedia(did))
	(_pedia.get_child(0) as Label).text = "%s  %d / %d" % [tr("DINOPEDIA"), seen, Game.dinos.size()]
	var info := _dark(_label("", 36))
	info.position = Vector2(70, 700)
	info.size = Vector2(1360, 170)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD
	info.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_pedia_body.add_child(info)
	if selected == "":
		info.text = tr("DINO_UNKNOWN") if seen < Game.dinos.size() else ""
	elif Game.dino_seen.has(selected):
		var d: Dictionary = Game.dino_by_id[selected]
		info.text = "%s\n%s" % [Game.dino_name(selected), d["fact_de"] if TranslationServer.get_locale().begins_with("de") else d["fact_en"]]
	else:
		info.text = "???\n" + tr("DINO_UNKNOWN")


# ------------------------------------------------------------------ fishing

func start_fishing(spot: String, place: String, time_of_day: String) -> void:
	if fishing != null:
		return
	close_menus()
	fishing = FishingUI.new()
	_root.add_child(fishing)
	fishing.size = _root.size
	fishing.start(self, spot, place, time_of_day)
	fishing.finished.connect(func() -> void: fishing = null)


func open_album() -> void:
	Audio.play("click")
	_fill_album("")
	_open(_album)


func _fill_album(selected: String) -> void:
	for c in _album_body.get_children():
		c.queue_free()
	var caught := 0
	for i in Game.fish.size():
		var f: Dictionary = Game.fish[i]
		var known := Game.fish_log.has(f["id"])
		if known:
			caught += 1
		var b := TextureButton.new()
		b.texture_normal = load(UI + "slot.png")
		b.ignore_texture_size = true
		b.stretch_mode = TextureButton.STRETCH_SCALE
		b.position = Vector2(56 + (i % 10) * 138, 110 + (i / 10) * 150)
		b.size = Vector2(128, 134)
		b.focus_mode = Control.FOCUS_NONE
		if f["id"] == selected:
			b.modulate = Color(1.0, 0.95, 0.7)
		_album_body.add_child(b)
		var ic := _tex("fish_%s.png" % f["id"])
		ic.scale = Vector2(0.86, 0.86)
		ic.position = Vector2(9, 22)
		if not known:
			ic.modulate = Color(0.1, 0.12, 0.18, 0.35)
		b.add_child(ic)
		var fid: String = f["id"]
		b.pressed.connect(func() -> void:
			Audio.play("click")
			_fill_album(fid))
	var title := _album.get_child(0) as Label
	title.text = "%s  %d / %d" % [tr("ALBUM"), caught, Game.fish.size()]
	var info := _dark(_label("ALBUM_HINT", 36))
	info.position = Vector2(56, 730)
	info.size = Vector2(1370, 200)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD
	info.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_album_body.add_child(info)
	if selected != "":
		var f: Dictionary = Game.fish_by_id[selected]
		var where := tr("LOC_" + str(f["loc"])) + "  •  " + tr("TIME_" + str(f["time"]))
		if Game.fish_log.has(selected):
			var e: Dictionary = Game.fish_log[selected]
			info.text = "%s\n%s\n%s %.1f cm  •  %s %d" % [Game.fish_name(selected), where, tr("BEST"),
				float(e["best"]), tr("CAUGHT"), int(e["n"])]
		else:
			info.text = "???\n%s" % where


# ------------------------------------------------------------------ production

func open_production(b: ProductionBuilding) -> void:
	if _prod_b != null and _prod_b.changed.is_connected(_fill_prod):
		_prod_b.changed.disconnect(_fill_prod)
	_prod_b = b
	b.changed.connect(_fill_prod)
	_fill_prod()
	_open(_prod)
	Audio.play("whoosh")


func _fill_prod() -> void:
	var b := _prod_b
	for c in _prod_body.get_children():
		c.queue_free()
	_prod_progress = []
	(_prod.get_child(0) as Label).text = "BUILDING_" + b.id
	# queue strip
	var strip := Control.new()
	strip.position = Vector2(60, 110)
	_prod_body.add_child(strip)
	var items: Array = []
	for d in b.done:
		items.append([int(d), "done"])
	for i in b.queue.size():
		items.append([int(b.queue[i]["r"]), "run" if i == 0 else "wait"])
	for i in b.slots():
		var sl := _tex("slot.png")
		sl.position = Vector2(i * 140, 0)
		strip.add_child(sl)
		if i >= items.size():
			sl.modulate.a = 0.55
			continue
		var rec: Dictionary = b.recipes()[items[i][0]]
		var ic := _item_icon(rec["out"], 100)
		ic.position = Vector2(14, 12)
		sl.add_child(ic)
		match items[i][1]:
			"done":
				var ck := _tex("ico_check.png")
				ck.position = Vector2(70, 70)
				sl.add_child(ck)
			"wait":
				ic.modulate.a = 0.5
			"run":
				var back := _patch("bar_back.png", 20, 18)
				back.position = Vector2(8, 126)
				back.size = Vector2(112, 40)
				sl.add_child(back)
				var fill := _patch("bar_fill.png", 10, 10)
				fill.position = Vector2(16, 133)
				fill.size = Vector2(22, 26)
				sl.add_child(fill)
				var t := _label("", 26)
				t.position = Vector2(0, 160)
				t.size = Vector2(128, 40)
				t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
				sl.add_child(t)
				_prod_progress = [fill, t]
	var hint := _dark(_label("QUEUE", 32))
	hint.position = Vector2(b.slots() * 140 + 90, 140)
	hint.size = Vector2(500, 60)
	_prod_body.add_child(hint)
	# recipes
	var y := 330.0
	for r in b.recipes().size():
		var rec: Dictionary = b.recipes()[r]
		# the nest only lists eggs the player actually has
		if rec.get("spawn", false) and Game.count(rec["in"].keys()[0]) == 0:
			continue
		var row := Control.new()
		row.position = Vector2(60, y)
		_prod_body.add_child(row)
		var sl := _tex("slot.png")
		row.add_child(sl)
		var ic := _item_icon(rec["out"], 100)
		ic.position = Vector2(14, 12)
		row.add_child(ic)
		var nm := _dark(_label("ITEM_" + str(rec["out"]), 38))
		nm.position = Vector2(150, 0)
		nm.size = Vector2(340, 56)
		row.add_child(nm)
		var tm := _dark(_label("%s  •  +%d XP" % [_fmt_time(int(rec["time"])), int(rec["xp"])], 28))
		tm.position = Vector2(150, 56)
		tm.size = Vector2(340, 50)
		row.add_child(tm)
		var x := 500.0
		for k in rec["in"]:
			var need := int(rec["in"][k])
			var ii := _tex("item_%s.png" % k)
			ii.scale = Vector2(0.6, 0.6)
			ii.position = Vector2(x, 8)
			row.add_child(ii)
			var cnt := _label("%d/%d" % [Game.count(k), need], 30)
			cnt.position = Vector2(x - 6, 70)
			cnt.size = Vector2(80, 44)
			cnt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			if Game.count(k) < need:
				cnt.add_theme_color_override("font_color", Color("FF8A80"))
			row.add_child(cnt)
			x += 96.0
		if Game.level < int(rec["unlock"]):
			var lk := _tex("lock.png")
			lk.position = Vector2(850, 18)
			row.add_child(lk)
			var lv := _dark(_label(tr("FROM_LEVEL") % int(rec["unlock"]), 34))
			lv.position = Vector2(930, 18)
			lv.size = Vector2(160, 64)
			row.add_child(lv)
		else:
			var make := _pill("MAKE", Vector2(820, 12), 270, b.can_start(r))
			make.pressed.connect(func() -> void:
				if b.start(r):
					Audio.play("plant", 1.1))
			row.add_child(make)
		y += 150.0
	var h := y + 30.0
	_prod.size.y = h
	_prod.offset_top = -h / 2
	_prod.offset_bottom = h / 2


# ------------------------------------------------------------------ orders

func open_orders() -> void:
	Game.event("open", "orders")
	_fill_orders()
	_open(_orders)
	Audio.play("whoosh")


func _fill_orders() -> void:
	for c in _orders_body.get_children():
		c.queue_free()
	for i in Game.orders.size():
		var o: Dictionary = Game.orders[i]
		var card := _patch("panel.png", 44, 44)
		card.mouse_filter = Control.MOUSE_FILTER_PASS
		card.position = Vector2(50 + (i % 3) * 410, 110 + (i / 3) * 385)
		card.size = Vector2(390, 370)
		card.set_meta("index", i)
		_orders_body.add_child(card)
		if not Game.order_ready(i):
			var wl := _dark(_label("NEXT_ORDER", 32))
			wl.position = Vector2(0, 110)
			wl.size = Vector2(390, 60)
			wl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			card.add_child(wl)
			var t := _dark(_label("", 44))
			t.position = Vector2(0, 170)
			t.size = Vector2(390, 70)
			t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			card.add_child(t)
			card.set_meta("wait_label", t)
			card.modulate.a = 0.75
			continue
		var need: Dictionary = o["need"]
		var n := need.size()
		var x := 195.0 - n * 58.0
		for k in need:
			var ii := _tex("item_%s.png" % k)
			ii.scale = Vector2(0.92, 0.92)
			ii.position = Vector2(x + 6, 34)
			card.add_child(ii)
			var cnt := _label("%d/%d" % [Game.count(k), int(need[k])], 32)
			cnt.position = Vector2(x, 132)
			cnt.size = Vector2(116, 44)
			cnt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			if Game.count(k) < int(need[k]):
				cnt.add_theme_color_override("font_color", Color("FF8A80"))
			card.add_child(cnt)
			x += 116.0
		var coin := _tex("coin.png")
		coin.scale = Vector2(0.55, 0.55)
		coin.position = Vector2(40, 192)
		card.add_child(coin)
		var cl := _dark(_label(str(int(o["coins"])), 36))
		cl.position = Vector2(104, 186)
		cl.size = Vector2(110, 64)
		card.add_child(cl)
		var st := _tex("star.png")
		st.scale = Vector2(0.38, 0.38)
		st.position = Vector2(210, 186)
		card.add_child(st)
		var xl := _dark(_label(str(int(o["xp"])), 36))
		xl.position = Vector2(276, 186)
		xl.size = Vector2(90, 64)
		card.add_child(xl)
		var go := _pill("DELIVER", Vector2(30, 258), 230, Game.has_all(need) and not Game.truck_away())
		go.pressed.connect(func() -> void:
			if Game.truck_away():
				Game.toast.emit(tr("TRUCK_AWAY"), "ico_truck.png")
			elif Game.deliver(i):
				Audio.play("whoosh", 0.9)
				Game.toast.emit(tr("TRUCK_GONE"), "ico_truck.png")
				close_menus())
		card.add_child(go)
		var bin := TextureButton.new()
		bin.texture_normal = load(UI + "btn_round.png")
		bin.ignore_texture_size = true
		bin.stretch_mode = TextureButton.STRETCH_SCALE
		bin.position = Vector2(276, 258)
		bin.size = Vector2(84, 89)
		bin.focus_mode = Control.FOCUS_NONE
		_press_feedback(bin)
		bin.pressed.connect(func() -> void:
			Audio.play("click")
			Game.discard(i))
		card.add_child(bin)
		var xi := _tex("ico_close.png")
		xi.scale = Vector2(0.8, 0.8)
		xi.position = Vector2(16, 16)
		bin.add_child(xi)


# ------------------------------------------------------------------ placement bar

func _build_place_bar() -> void:
	_place_bar = Control.new()
	_place_bar.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_place_bar.offset_top = -230
	_place_bar.visible = false
	_root.add_child(_place_bar)
	var ok := _bar_button("btn_round_green.png", "ico_check.png", Vector2(-170, 0))
	ok.pressed.connect(func() -> void: place_confirm.emit())
	var no := _bar_button("btn_round.png", "ico_close.png", Vector2(30, 0))
	no.pressed.connect(func() -> void: place_cancel.emit())


func _bar_button(tex: String, icon: String, pos: Vector2) -> TextureButton:
	var b := TextureButton.new()
	b.texture_normal = load(UI + tex)
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	b.position = pos
	b.size = Vector2(140, 148)
	b.focus_mode = Control.FOCUS_NONE
	_press_feedback(b)
	_place_bar.add_child(b)
	var i := _tex(icon)
	i.scale = Vector2(1.3, 1.3)
	i.position = Vector2(28, 28)
	b.add_child(i)
	return b


func set_placing(on: bool) -> void:
	_place_bar.visible = on
	_hint.offset_top = -330 if on else -150
	_hint.offset_bottom = -266 if on else -86
	if on:
		close_menus()
		_hint.text = "PLACE_HINT"
		_hint.modulate.a = 1.0
		_hint.show()
	elif _hint.text == "PLACE_HINT":
		_hint.hide()


func show_hint(key: String) -> void:
	_hint.text = key
	_hint.modulate.a = 1.0
	_hint.show()


# ------------------------------------------------------------------ settings

func _toggle_settings() -> void:
	meta.toggle_settings()


# ------------------------------------------------------------------ widgets

## Icon texture for any item id. Dinos use their 3D idle frame from the atlas.
static func item_texture(id: String) -> Texture2D:
	if id.begins_with("dino_"):
		return Atlas.tex("%s_idle_se_0" % id)
	return load(UI + "item_%s.png" % id)


func _item_icon(id: String, box := 112.0) -> TextureRect:
	var t := TextureRect.new()
	t.texture = item_texture(id)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.size = Vector2(box, box)
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


func _patch(file: String, mx: int, my: int) -> NinePatchRect:
	var p := NinePatchRect.new()
	p.texture = load(UI + file)
	p.patch_margin_left = mx
	p.patch_margin_right = mx
	p.patch_margin_top = my
	p.patch_margin_bottom = my
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p


func _tex(file: String) -> TextureRect:
	var t := TextureRect.new()
	t.texture = load(UI + file)
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


func _label(text: String, font_size: int) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Game.font_bold)
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", WHITE)
	l.add_theme_color_override("font_outline_color", OUTLINE)
	l.add_theme_constant_override("outline_size", maxi(10, font_size / 3))
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.25))
	l.add_theme_constant_override("shadow_offset_y", 4)
	l.add_theme_constant_override("shadow_offset_x", 0)
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## Big outlined number + icon + small round "+" button, stacked top right.
func _currency(icon_file: String, value: int, row: int) -> Array:
	var holder := Control.new()
	holder.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	holder.offset_left = -480
	holder.offset_top = 18 + row * 112
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(holder)
	var label := _label(fmt(value), 66)
	label.position = Vector2(0, 4)
	label.size = Vector2(250, 100)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	holder.add_child(label)
	var icon := _tex(icon_file)
	icon.position = Vector2(262, 0)
	holder.add_child(icon)
	var plus := TextureButton.new()
	plus.texture_normal = load(UI + "btn_round.png")
	plus.ignore_texture_size = true
	plus.stretch_mode = TextureButton.STRETCH_SCALE
	plus.position = Vector2(378, 12)
	plus.size = Vector2(84, 89)
	plus.focus_mode = Control.FOCUS_NONE
	plus.pressed.connect(func() -> void: Audio.play("click"))
	_press_feedback(plus)
	holder.add_child(plus)
	var p := _tex("ico_plus.png")
	p.position = Vector2(11, 10)
	p.scale = Vector2(0.97, 0.97)
	plus.add_child(p)
	return [label, icon]


func _round_button(icon_file: String, pos: Vector2, size: float, bottom := false) -> TextureButton:
	var b := TextureButton.new()
	b.texture_normal = load(UI + "btn_round.png")
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	if bottom:
		b.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
		b.offset_left = pos.x
		b.offset_top = pos.y
		b.offset_right = pos.x + size
		b.offset_bottom = pos.y + size * 1.06
	else:
		b.position = pos
		b.size = Vector2(size, size * 1.06)
	b.focus_mode = Control.FOCUS_NONE
	_press_feedback(b)
	_root.add_child(b)
	var icon := _tex(icon_file)
	var tex_size: Vector2 = icon.texture.get_size()
	var k := size * 0.62 / tex_size.x
	icon.scale = Vector2(k, k)
	icon.position = (Vector2(size, size) - tex_size * k) * 0.5
	b.add_child(icon)
	return b


func _dark(l: Label) -> Label:
	l.add_theme_color_override("font_color", Color("5A3410"))
	l.add_theme_constant_override("outline_size", 0)
	l.add_theme_constant_override("shadow_offset_y", 0)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	return l


func _text_button(key: String, pos: Vector2, icon_file := "", glyph := "") -> Array:
	var b := TextureButton.new()
	b.texture_normal = load(UI + "btn_round_green.png")
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	b.position = pos
	b.size = Vector2(80, 85)
	b.focus_mode = Control.FOCUS_NONE
	_press_feedback(b)
	_settings.add_child(b)
	if icon_file != "":
		var ic := _tex(icon_file)
		ic.scale = Vector2(0.55, 0.55)
		ic.position = Vector2(14, 12)
		b.add_child(ic)
	if glyph != "":
		var g := _label(glyph, 34)
		g.size = Vector2(80, 80)
		g.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.add_child(g)
	var l := _dark(_label(key, 40))
	l.position = pos + Vector2(100, 4)
	l.size = Vector2(280, 76)
	_settings.add_child(l)
	return [b, l]


func _press_feedback(b: BaseButton) -> void:
	b.button_down.connect(func() -> void:
		b.pivot_offset = b.size / 2
		b.scale = Vector2(0.9, 0.9))
	b.button_up.connect(func() -> void:
		create_tween().tween_property(b, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT))
