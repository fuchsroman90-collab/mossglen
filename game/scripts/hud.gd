class_name Hud
extends CanvasLayer
## 2D HUD (flat vector pieces from tools/art/ui.py), laid out like the reference HUD:
## level star + XP bar top left, big outlined numbers with coin/gem and "+" top right,
## round yellow buttons on the left, big shop button bottom left.
## Authored in 2x units inside a root control scaled by 0.5.

signal shop_pressed

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

const XP_X := 150.0
const XP_W := 440.0


func _ready() -> void:
	_root = Control.new()
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.scale = Vector2(0.5, 0.5)
	add_child(_root)
	get_viewport().size_changed.connect(_fit)
	_fit()

	# XP bar with the level star overlapping its left end
	var back := _patch("bar_back.png", 32, 30)
	back.position = Vector2(XP_X, 34)
	back.size = Vector2(XP_W, 68)
	_root.add_child(back)
	_xp_fill = _patch("bar_fill.png", 20, 18)
	_xp_fill.position = Vector2(XP_X + 13, 47)
	_xp_fill.size = Vector2(40, 42)
	_root.add_child(_xp_fill)
	_xp_label = _label("", 36)
	_xp_label.position = Vector2(XP_X + 60, 32)
	_xp_label.size = Vector2(XP_W - 70, 70)
	_xp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_root.add_child(_xp_label)
	var star := _tex("star.png")
	star.position = Vector2(14, 4)
	_root.add_child(star)
	_level_label = _label(str(Game.level), 62)
	_level_label.position = Vector2(14, 34)
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


func _process(_delta: float) -> void:
	_fps_label.text = "%d FPS" % Engine.get_frames_per_second()


func hide_hint() -> void:
	if _hint.visible and _hint.modulate.a >= 1.0:
		create_tween().tween_property(_hint, "modulate:a", 0.0, 0.6).finished.connect(_hint.hide)


func _on_xp(xp: int, needed: int, level: int) -> void:
	var w := maxf(40.0, (XP_W - 26.0) * float(xp) / float(needed))
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
