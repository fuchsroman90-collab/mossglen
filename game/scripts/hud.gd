class_name Hud
extends CanvasLayer
## Currency bar, settings buttons, hint and FPS counter. Built in code.

const OUTLINE := Color("4A3A2E")
const UI := "res://art/generated/"

var coin_icon: TextureRect
var _coin_label: Label
var _emerald_label: Label
var _fps_label: Label
var _hint: Label
var _music_btn: Button


func _ready() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.theme = _make_theme()
	add_child(root)

	var bar := HBoxContainer.new()
	bar.position = Vector2(16, 14)
	bar.add_theme_constant_override("separation", 14)
	root.add_child(bar)
	var c := _counter(UI + "ui_coin.png", str(Game.coins))
	bar.add_child(c[0])
	coin_icon = c[1]
	_coin_label = c[2]
	var e := _counter(UI + "ui_emerald.png", str(Game.emeralds))
	bar.add_child(e[0])
	_emerald_label = e[2]

	var right := HBoxContainer.new()
	right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	right.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	right.position = Vector2(-16, 14)
	right.add_theme_constant_override("separation", 10)
	root.add_child(right)
	_music_btn = _button("BTN_MUSIC_ON")
	_music_btn.pressed.connect(_on_music)
	right.add_child(_music_btn)
	var lang := _button("BTN_LANG")
	lang.pressed.connect(func() -> void:
		Audio.play("click")
		Game.toggle_language())
	right.add_child(lang)

	_hint = Label.new()
	_hint.text = "HINT_START"
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_hint.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_hint.position.y = -64
	_hint.add_theme_color_override("font_color", Color("FFF4DC"))
	_hint.add_theme_color_override("font_outline_color", OUTLINE)
	_hint.add_theme_constant_override("outline_size", 10)
	root.add_child(_hint)

	_fps_label = Label.new()
	_fps_label.position = Vector2(22, 80)
	_fps_label.add_theme_font_size_override("font_size", 16)
	_fps_label.add_theme_color_override("font_color", Color(1, 1, 1, 0.8))
	_fps_label.add_theme_color_override("font_outline_color", OUTLINE)
	_fps_label.add_theme_constant_override("outline_size", 6)
	root.add_child(_fps_label)

	Game.coins_changed.connect(func(v: int) -> void: _set_counter(_coin_label, v))
	Game.emeralds_changed.connect(func(v: int) -> void: _set_counter(_emerald_label, v))


func _process(_delta: float) -> void:
	_fps_label.text = "%d FPS" % Engine.get_frames_per_second()


func hide_hint() -> void:
	if _hint.visible and _hint.modulate.a >= 1.0:
		create_tween().tween_property(_hint, "modulate:a", 0.0, 0.6).finished.connect(_hint.hide)


func _on_music() -> void:
	Audio.play("click")
	Audio.set_music_enabled(not Audio.music_enabled)
	_music_btn.text = "BTN_MUSIC_ON" if Audio.music_enabled else "BTN_MUSIC_OFF"


func _set_counter(label: Label, v: int) -> void:
	label.text = str(v)
	label.pivot_offset = label.size / 2
	label.scale = Vector2(1.3, 1.3)
	create_tween().tween_property(label, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _counter(icon_path: String, value: String) -> Array:
	var panel := PanelContainer.new()
	var box := HBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	panel.add_child(box)
	var icon := TextureRect.new()
	icon.texture = load(icon_path)
	icon.custom_minimum_size = Vector2(44, 44)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	box.add_child(icon)
	var label := Label.new()
	label.text = value
	label.custom_minimum_size.x = 70
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	box.add_child(label)
	return [panel, icon, label]


func _button(key: String) -> Button:
	var b := Button.new()
	b.text = key
	b.custom_minimum_size = Vector2(110, 52)
	b.focus_mode = Control.FOCUS_NONE
	return b


func _make_theme() -> Theme:
	var t := Theme.new()
	t.default_font_size = 24
	t.set_color("font_color", "Label", OUTLINE)

	var panel := StyleBoxTexture.new()
	panel.texture = load(UI + "ui_panel.png")
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		panel.set_texture_margin(side, 22)
	panel.content_margin_left = 12
	panel.content_margin_right = 18
	panel.content_margin_top = 8
	panel.content_margin_bottom = 10
	t.set_stylebox("panel", "PanelContainer", panel)

	var btn := StyleBoxTexture.new()
	btn.texture = load(UI + "ui_button_cream.png")
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		btn.set_texture_margin(side, 22)
	btn.content_margin_bottom = 10
	var pressed := btn.duplicate()
	pressed.modulate_color = Color(0.9, 0.86, 0.8)
	t.set_stylebox("normal", "Button", btn)
	t.set_stylebox("hover", "Button", btn)
	t.set_stylebox("pressed", "Button", pressed)
	t.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	t.set_color("font_color", "Button", OUTLINE)
	t.set_color("font_hover_color", "Button", OUTLINE)
	t.set_color("font_pressed_color", "Button", OUTLINE)
	t.set_font_size("font_size", "Button", 20)
	return t
