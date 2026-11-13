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
var _music_btn: Label
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
	# bottom left: shop (build / seeds menu)
	var shop := _round_button("ico_shop.png", Vector2(20, -250), 196, true)
	shop.pressed.connect(func() -> void:
		Audio.play("click")
		shop_pressed.emit())

	_build_settings()
	_build_barn()
	_build_shop()
	_build_place_bar()
	_toasts = Control.new()
	_toasts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_toasts.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_toasts.offset_top = 230
	_root.add_child(_toasts)
	Game.toast.connect(toast)
	Game.inventory_changed.connect(func(_i: String, _c: int) -> void:
		if _barn.visible:
			_fill_barn())

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


func _fit() -> void:
	_root.size = get_viewport().get_visible_rect().size * 2.0


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


func any_menu_open() -> bool:
	return _barn.visible or _shop.visible or _settings.visible


func close_menus() -> void:
	for m in [_barn, _shop, _settings]:
		m.hide()
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
	var p := screen_pos * 2.0 - Vector2(w * 0.5, 290)
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
	(_info.get_node("Name") as Label).text = "CROP_" + crop
	(_info.get_node("Fill") as Control).size.x = maxf(38.0, 256.0 * progress)
	(_info.get_node("Time") as Label).text = "%d:%02d" % [seconds / 60, seconds % 60] if seconds > 0 else tr("READY")
	_info.position = screen_pos * 2.0 - Vector2(170, 260)
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


func open_barn() -> void:
	Audio.play("whoosh")
	_fill_barn()
	_open(_barn)


func _fill_barn() -> void:
	_barn_title.text = "%s  %d / %d" % [tr("BARN"), Game.stored(), Game.barn_capacity]
	for c in _barn_rows.get_children():
		c.queue_free()
	var y := 0.0
	for crop in Game.crop_order:
		if not Game.is_unlocked(crop) and Game.count(crop) == 0:
			continue
		var row := Control.new()
		row.position = Vector2(0, y)
		_barn_rows.add_child(row)
		var slot := _tex("slot.png")
		slot.scale = Vector2(0.95, 0.95)
		row.add_child(slot)
		var icon := _tex("item_%s.png" % crop)
		icon.scale = Vector2(0.82, 0.82)
		icon.position = Vector2(14, 10)
		row.add_child(icon)
		var name_l := _dark(_label("CROP_" + crop, 40))
		name_l.position = Vector2(140, 6)
		name_l.size = Vector2(300, 60)
		row.add_child(name_l)
		var cnt := _dark(_label("× %d" % Game.count(crop), 36))
		cnt.position = Vector2(140, 58)
		cnt.size = Vector2(160, 56)
		row.add_child(cnt)
		var coin := _tex("coin.png")
		coin.scale = Vector2(0.5, 0.5)
		coin.position = Vector2(300, 64)
		row.add_child(coin)
		var price := _dark(_label(str(int(Game.crops[crop]["sell"])), 36))
		price.position = Vector2(360, 58)
		price.size = Vector2(80, 56)
		row.add_child(price)
		var one := _pill("SELL_ONE", Vector2(470, 18), 240, Game.count(crop) > 0)
		row.add_child(one)
		one.pressed.connect(func() -> void: _sell(crop, 1))
		var all := _pill("SELL_ALL", Vector2(730, 18), 150, Game.count(crop) > 0)
		row.add_child(all)
		all.pressed.connect(func() -> void: _sell(crop, Game.count(crop)))
		y += 140.0
	# fit the window to its rows
	var h := 150.0 + y
	_barn.offset_top = -h / 2
	_barn.offset_bottom = h / 2
	_barn.size.y = h


func _sell(crop: String, n: int) -> void:
	var earned := Game.sell(crop, n)
	if earned > 0:
		Audio.play("coin", 1.0, 0.05)
		_fill_barn()


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
	for c in _shop.get_children().slice(2):
		c.queue_free()
	var card := Control.new()
	card.position = Vector2(60, 120)
	_shop.add_child(card)
	var slot := _tex("slot.png")
	slot.scale = Vector2(1.3, 1.3)
	card.add_child(slot)
	var icon := _tex("item_field.png")
	icon.scale = Vector2(1.15, 1.15)
	icon.position = Vector2(19, 16)
	card.add_child(icon)
	var name_l := _dark(_label("FIELD", 48))
	name_l.position = Vector2(200, 10)
	name_l.size = Vector2(300, 70)
	card.add_child(name_l)
	var have := _dark(_label("%d / %d" % [12 + Game.extra_fields, Game.max_fields()], 34))
	have.position = Vector2(200, 72)
	have.size = Vector2(300, 50)
	card.add_child(have)
	var buy := _pill("", Vector2(200, 140), 260, true)
	card.add_child(buy)
	var coin := _tex("coin.png")
	coin.scale = Vector2(0.62, 0.62)
	coin.position = Vector2(30, 12)
	buy.add_child(coin)
	var price := _label(str(Game.field_price()), 44)
	price.position = Vector2(100, 0)
	price.size = Vector2(140, 86)
	buy.add_child(price)
	buy.pressed.connect(func() -> void:
		Audio.play("click")
		_shop.hide()
		buy_field.emit())
	_open(_shop)


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

func _build_settings() -> void:
	_settings = _patch("panel.png", 44, 44)
	_settings.position = Vector2(170, 170)
	_settings.size = Vector2(430, 300)
	_settings.visible = false
	_root.add_child(_settings)
	var title := _dark(_label("SETTINGS", 42))
	title.position = Vector2(0, 26)
	title.size = Vector2(430, 60)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_settings.add_child(title)
	var music := _text_button("BTN_MUSIC_ON", Vector2(40, 100), "ico_note.png")
	_music_btn = music[1]
	music[0].pressed.connect(func() -> void:
		Audio.play("click")
		Audio.set_music_enabled(not Audio.music_enabled)
		_music_btn.text = "BTN_MUSIC_ON" if Audio.music_enabled else "BTN_MUSIC_OFF")
	var lang := _text_button("BTN_LANG", Vector2(40, 186), "", "Aa")
	lang[0].pressed.connect(func() -> void:
		Audio.play("click")
		Game.toggle_language())


func _toggle_settings() -> void:
	Audio.play("click")
	if _settings.visible:
		var tw := create_tween()
		tw.tween_property(_settings, "scale", Vector2(0.85, 0.85), 0.1)
		tw.tween_callback(_settings.hide)
		return
	_settings.visible = true
	_settings.pivot_offset = Vector2(0, 0)
	_settings.scale = Vector2(0.6, 0.6)
	create_tween().tween_property(_settings, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


# ------------------------------------------------------------------ widgets

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
