class_name Hud
extends CanvasLayer
## HUD built in code. Authored in 2x units inside a root control scaled by 0.5,
## so the 2x UI textures stay crisp on high-density screens.

const UI := "res://art/generated/"
const OUTLINE := Color("4A3222")
const CREAM := Color("FFF8E6")

var coin_icon: Control
var _root: Control
var _coin_label: Label
var _emerald_label: Label
var _level_label: Label
var _xp_fill: NinePatchRect
var _xp_width := 0.0
var _fps_label: Label
var _hint: Label
var _music_label: Label


func _ready() -> void:
	_root = Control.new()
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.scale = Vector2(0.5, 0.5)
	add_child(_root)
	get_viewport().size_changed.connect(_fit)
	_fit()

	# level star + xp bar (top left)
	var xp_back := _patch("ui_bar_back.png", 26, 18)
	xp_back.position = Vector2(118, 46)
	xp_back.size = Vector2(300, 52)
	_root.add_child(xp_back)
	_xp_fill = _patch("ui_bar_fill.png", 18, 14)
	_xp_fill.position = Vector2(126, 54)
	_xp_width = 284.0
	_xp_fill.size = Vector2(36, 36)
	_root.add_child(_xp_fill)
	var star := _icon("icon_star", Vector2(150, 144))
	star.position = Vector2(12, 0)
	_root.add_child(star)
	_level_label = _label(str(Game.level), 54)
	_level_label.position = Vector2(12, 34)
	_level_label.size = Vector2(150, 70)
	_level_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_root.add_child(_level_label)

	# currencies (top right)
	var c := _counter("icon_coin", str(Game.coins), 0)
	coin_icon = c[0]
	_coin_label = c[1]
	var e := _counter("icon_emerald", str(Game.emeralds), 1)
	_emerald_label = e[1]

	# round buttons (bottom right)
	var music := _round_button("♪", 0)
	_music_label = music
	music.get_parent().pressed.connect(_on_music)
	var lang := _round_button("BTN_LANG", 1)
	lang.get_parent().pressed.connect(func() -> void:
		Audio.play("click")
		Game.toggle_language())

	_hint = _label("HINT_START", 40)
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_hint.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_hint.offset_top = -150
	_hint.offset_bottom = -90
	_root.add_child(_hint)

	_fps_label = _label("", 26)
	_fps_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_fps_label.offset_left = 24
	_fps_label.offset_top = -56
	_fps_label.modulate.a = 0.75
	_root.add_child(_fps_label)

	Game.coins_changed.connect(func(v: int) -> void: _set_counter(_coin_label, v))
	Game.emeralds_changed.connect(func(v: int) -> void: _set_counter(_emerald_label, v))
	Game.xp_changed.connect(_on_xp)
	_on_xp(Game.xp, Game.xp_needed(), Game.level)


func _fit() -> void:
	_root.size = get_viewport().get_visible_rect().size * 2.0


func _process(_delta: float) -> void:
	_fps_label.text = "%d FPS" % Engine.get_frames_per_second()


func hide_hint() -> void:
	if _hint.visible and _hint.modulate.a >= 1.0:
		create_tween().tween_property(_hint, "modulate:a", 0.0, 0.6).finished.connect(_hint.hide)


func _on_music() -> void:
	Audio.play("click")
	Audio.set_music_enabled(not Audio.music_enabled)
	_music_label.modulate.a = 1.0 if Audio.music_enabled else 0.35


func _on_xp(xp: int, needed: int, level: int) -> void:
	var w := maxf(36.0, _xp_width * float(xp) / float(needed))
	create_tween().tween_property(_xp_fill, "size:x", w, 0.35).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	if _level_label.text != str(level):
		_level_label.text = str(level)
		_pop(_level_label, 1.6)


func _set_counter(label: Label, v: int) -> void:
	label.text = str(v)
	_pop(label, 1.3)


func _pop(c: Control, s: float) -> void:
	c.pivot_offset = c.size / 2
	c.scale = Vector2(s, s)
	create_tween().tween_property(c, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


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


func _icon(sprite_name: String, box: Vector2) -> TextureRect:
	var t := TextureRect.new()
	t.texture = Atlas.tex(sprite_name)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.size = box
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


func _label(text: String, font_size: int) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Game.font_bold)
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", CREAM)
	l.add_theme_color_override("font_outline_color", OUTLINE)
	l.add_theme_constant_override("outline_size", maxi(8, font_size / 4))
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## Capsule with icon and number, stacked in the top right corner.
func _counter(icon_name: String, value: String, row: int) -> Array:
	var holder := Control.new()
	holder.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	holder.offset_left = -390
	holder.offset_top = 22 + row * 104
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(holder)
	var cap := _patch("ui_capsule.png", 40, 30)
	cap.position = Vector2(46, 14)
	cap.size = Vector2(300, 80)
	holder.add_child(cap)
	var label := _label(value, 46)
	label.position = Vector2(110, 14)
	label.size = Vector2(190, 74)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	label.add_theme_color_override("font_color", Color("5A3A20"))
	label.add_theme_color_override("font_outline_color", Color(1, 1, 1, 0))
	label.add_theme_constant_override("outline_size", 0)
	holder.add_child(label)
	var icon := _icon(icon_name, Vector2(108, 104))
	icon.position = Vector2(0, 0)
	holder.add_child(icon)
	var plus := TextureButton.new()
	plus.texture_normal = load(UI + "ui_btn_green.png")
	plus.ignore_texture_size = true
	plus.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
	plus.position = Vector2(318, 18)
	plus.size = Vector2(70, 74)
	plus.focus_mode = Control.FOCUS_NONE
	plus.pressed.connect(func() -> void: Audio.play("click"))
	holder.add_child(plus)
	var pl := _label("+", 54)
	pl.size = Vector2(70, 68)
	pl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	plus.add_child(pl)
	return [icon, label]


func _round_button(text: String, index: int) -> Label:
	var b := TextureButton.new()
	b.texture_normal = load(UI + "ui_btn_yellow.png")
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
	b.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	b.offset_left = -150 - index * 140
	b.offset_top = -160
	b.offset_right = b.offset_left + 124
	b.offset_bottom = b.offset_top + 130
	b.focus_mode = Control.FOCUS_NONE
	b.button_down.connect(func() -> void: b.scale = Vector2(0.92, 0.92))
	b.button_up.connect(func() -> void: b.scale = Vector2.ONE)
	b.pivot_offset = Vector2(62, 62)
	_root.add_child(b)
	var l := _label(text, 46)
	l.size = Vector2(124, 120)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	b.add_child(l)
	return l
