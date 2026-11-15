class_name RewardUI
extends Node
## Wheel of fortune (one free spin a day, more for emeralds) and the 7-day daily gift.

const COLORS := [Color("#FFD23F"), Color("#6FC8F5"), Color("#FF8A6A"), Color("#8EDB4A"),
	Color("#FFB060"), Color("#B58CF0"), Color("#F27A9E"), Color("#5ED6B0")]

var hud: Hud
var wheel_btn: TextureButton
var gift_btn: TextureButton
var _wheel_dot: Control
var _gift_dot: Control
var _win: Control
var _disc: Control
var _spin_btn: TextureButton
var _result: Label
var _spinning := false
var _mine: Control
var _mine_body: Control
var _mine_sprite: Sprite2D
var _daily: Control
var _daily_row: HBoxContainer
var _daily_btn: TextureButton


class Disc:
	extends Control
	var colors: Array = []

	func _draw() -> void:
		var r := size.x / 2
		var c := size / 2
		draw_circle(c, r, Color("#5A3410"))
		var n := colors.size()
		for i in n:
			var pts := PackedVector2Array([c])
			for k in 13:
				var a := TAU * (i + k / 12.0) / n - PI / 2
				pts.append(c + Vector2(cos(a), sin(a)) * (r - 14))
			draw_colored_polygon(pts, colors[i])
		for i in n:
			var a := TAU * i / n - PI / 2
			draw_line(c, c + Vector2(cos(a), sin(a)) * (r - 14), Color("#5A3410"), 6.0)
		draw_circle(c, 46, Color("#5A3410"))
		draw_circle(c, 36, Color("#FFF6DC"))


func setup(h: Hud) -> void:
	hud = h
	wheel_btn = hud._round_button("ico_wheel.png", Vector2(26, 800), 128)
	wheel_btn.pressed.connect(open_wheel)
	_wheel_dot = _dot(wheel_btn)
	gift_btn = hud._round_button("ico_gift.png", Vector2(170, 800), 128)
	gift_btn.pressed.connect(open_daily)
	_gift_dot = _dot(gift_btn)
	_build_wheel()
	_build_daily()
	_build_mine()
	refresh()


func _dot(b: Control) -> Control:
	var d := hud._tex("badge.png")
	d.modulate = Color(1.0, 0.45, 0.35)
	d.position = Vector2(84, -6)
	var l := hud._label("!", 34)
	l.size = Vector2(56, 56)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	d.add_child(l)
	b.add_child(d)
	return d


func refresh() -> void:
	_wheel_dot.visible = Game.wheel_free()
	_gift_dot.visible = Game.daily_ready()


func _reward_icon(r: Array, box: float) -> Control:
	match str(r[0]):
		"coins":
			var t := hud._tex("coin.png")
			t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			t.size = Vector2(box, box)
			return t
		"emerald":
			var t := hud._tex("gem.png")
			t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			t.size = Vector2(box, box)
			return t
	return hud._item_icon(str(r[0]), box)


func _reward_text(r: Array) -> String:
	match str(r[0]):
		"coins":
			return "+%d" % int(r[1])
		"emerald":
			return "+%d" % int(r[1])
	return "%d× %s" % [int(r[1]), tr("ITEM_" + str(r[0]))]


# ------------------------------------------------------------------ wheel

func _build_wheel() -> void:
	_win = hud._panel_window(Vector2(1000, 1120), "WHEEL_TITLE")[0]
	hud.extra_windows.append(_win)
	_disc = Disc.new()
	_disc.colors = COLORS
	_disc.size = Vector2(720, 720)
	_disc.position = Vector2(140, 110)
	_disc.pivot_offset = Vector2(360, 360)
	_disc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_win.add_child(_disc)
	var n := Game.WHEEL.size()
	for i in n:
		var a := TAU * (i + 0.5) / n - PI / 2
		var holder := Control.new()
		holder.position = Vector2(360, 360) + Vector2(cos(a), sin(a)) * 240
		holder.rotation = a + PI / 2
		_disc.add_child(holder)
		var ic := _reward_icon(Game.WHEEL[i], 104)
		ic.position = Vector2(-52, -76)
		holder.add_child(ic)
		var l := hud._label(str(int(Game.WHEEL[i][1])), 40)
		l.position = Vector2(-60, 26)
		l.size = Vector2(120, 50)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		holder.add_child(l)
	var ptr := Polygon2D.new()
	ptr.polygon = PackedVector2Array([Vector2(-44, 0), Vector2(44, 0), Vector2(0, 86)])
	ptr.color = Color("#E8402E")
	ptr.position = Vector2(500, 84)
	_win.add_child(ptr)
	var edge := Line2D.new()
	edge.points = PackedVector2Array([Vector2(-44, 0), Vector2(44, 0), Vector2(0, 86), Vector2(-44, 0)])
	edge.width = 8
	edge.default_color = Color("#5A3410")
	ptr.add_child(edge)
	_result = hud._dark(hud._label("", 44))
	_result.position = Vector2(0, 850)
	_result.size = Vector2(1000, 70)
	_result.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_win.add_child(_result)
	_spin_btn = hud._pill("", Vector2(270, 940), 460)
	_spin_btn.pressed.connect(_spin)
	_win.add_child(_spin_btn)


func open_wheel() -> void:
	_result.text = ""
	_update_spin_label()
	hud._open(_win)


func _update_spin_label() -> void:
	(_spin_btn.get_child(0) as Label).text = tr("WHEEL_FREE") if Game.wheel_free() else tr("WHEEL_PAID") % Game.WHEEL_COST


func _spin() -> void:
	if _spinning:
		return
	var idx := Game.spin_wheel()
	if idx < 0:
		Game.toast.emit(tr("NOT_ENOUGH_EMERALDS"), "gem.png")
		return
	_spinning = true
	_result.text = ""
	Audio.play("click")
	var n := Game.WHEEL.size()
	var target := -TAU * (idx + 0.5) / n
	var from := fposmod(_disc.rotation, TAU)
	_disc.rotation = from
	var to := target - TAU * 5.0
	while to > from - TAU * 4.0:
		to -= TAU
	var tw := create_tween()
	tw.tween_property(_disc, "rotation", to, 3.2).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	tw.tween_callback(func() -> void:
		_spinning = false
		Audio.play("levelup")
		_result.text = _reward_text(Game.WHEEL[idx])
		Game.toast.emit(_reward_text(Game.WHEEL[idx]), "coin.png")
		_update_spin_label()
		refresh())


# ------------------------------------------------------------------ daily gift

func _build_daily() -> void:
	_daily = hud._panel_window(Vector2(1640, 620), "DAILY_TITLE")[0]
	hud.extra_windows.append(_daily)
	_daily_row = HBoxContainer.new()
	_daily_row.position = Vector2(50, 120)
	_daily_row.add_theme_constant_override("separation", 16)
	_daily.add_child(_daily_row)
	_daily_btn = hud._pill("DAILY_CLAIM", Vector2(590, 470), 460)
	_daily_btn.pressed.connect(func() -> void:
		var r := Game.claim_daily()
		if r.is_empty():
			return
		Audio.play("levelup")
		Game.toast.emit(_reward_text(r), "coin.png")
		_fill_daily()
		refresh())
	_daily.add_child(_daily_btn)


func open_daily() -> void:
	_fill_daily()
	hud._open(_daily)


func _fill_daily() -> void:
	for c in _daily_row.get_children():
		c.queue_free()
	var ready := Game.daily_ready()
	for i in Game.DAILY.size():
		var done := i < Game.daily_streak or (not ready and Game.daily_streak == 0)
		var cur := ready and i == Game.daily_streak
		var t := hud._patch("panel.png", 44, 44)
		t.custom_minimum_size = Vector2(206, 310)
		t.self_modulate = Color(1.0, 0.9, 0.5) if cur else (Color(0.78, 0.9, 0.7) if done else Color(1.0, 0.97, 0.88))
		var d := hud._dark(hud._label(tr("DAILY_DAY") % (i + 1), 30))
		d.position = Vector2(0, 14)
		d.size = Vector2(206, 44)
		d.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		t.add_child(d)
		var ic := _reward_icon(Game.DAILY[i], 120)
		ic.position = Vector2(43, 70)
		t.add_child(ic)
		var l := hud._label("✓" if done else str(int(Game.DAILY[i][1])), 46)
		l.position = Vector2(0, 210)
		l.size = Vector2(206, 60)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		t.add_child(l)
		_daily_row.add_child(t)
	_daily_btn.visible = ready


# ------------------------------------------------------------------ mine

func _build_mine() -> void:
	_mine = hud._panel_window(Vector2(1300, 860), "MINE_TITLE")[0]
	hud.extra_windows.append(_mine)
	_mine_body = Control.new()
	_mine.add_child(_mine_body)


func open_mine(s: Sprite2D) -> void:
	_mine_sprite = s
	_fill_mine()
	hud._open(_mine)


func _fill_mine() -> void:
	for c in _mine_body.get_children():
		c.queue_free()
	var info := hud._dark(hud._label("MINE_INFO", 32))
	info.position = Vector2(60, 96)
	info.size = Vector2(1180, 50)
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_mine_body.add_child(info)
	# tools: one framed tile each, with the amount and what it digs up
	var x := 70.0
	for tool in Game.MINE_TOOLS:
		var have := Game.count(tool)
		var t := hud._patch("panel.png", 44, 44)
		t.position = Vector2(x, 160)
		t.size = Vector2(272, 400)
		t.self_modulate = Color(1.0, 0.93, 0.7) if have > 0 else Color(0.8, 0.8, 0.8)
		_mine_body.add_child(t)
		var ic := hud._item_icon(tool, 150)
		ic.position = Vector2(61, 24)
		t.add_child(ic)
		var n := hud._label("x%d" % have, 44)
		n.position = Vector2(0, 170)
		n.size = Vector2(272, 56)
		n.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		t.add_child(n)
		var y := hud._dark(hud._label(tr("MINE_YIELD") % int(Game.MINE_TOOLS[tool]), 28))
		y.position = Vector2(0, 232)
		y.size = Vector2(272, 44)
		y.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		t.add_child(y)
		var b := hud._pill("MINE_DIG", Vector2(26, 290), 220, have > 0)
		b.pressed.connect(func() -> void: _dig(tool))
		t.add_child(b)
		x += 296.0
	# ores in stock: a separate cream frame
	var stock := hud._patch("panel.png", 44, 44)
	stock.position = Vector2(70, 590)
	stock.size = Vector2(1160, 210)
	stock.self_modulate = Color(0.86, 0.93, 1.0)
	_mine_body.add_child(stock)
	var ox := 40.0
	for ore in Game.MINE_ORES:
		var ic := hud._item_icon(ore, 120)
		ic.position = Vector2(ox, 20)
		stock.add_child(ic)
		var l := hud._label(str(Game.count(ore)), 44)
		l.position = Vector2(ox, 140)
		l.size = Vector2(120, 56)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		stock.add_child(l)
		ox += 180.0
	if _mine_sprite != null:
		var mv := hud._pill("DECO_MOVE", Vector2(920, 66), 300)
		mv.scale = Vector2(0.8, 0.8)
		mv.position = Vector2(960, 640)
		mv.pressed.connect(func() -> void:
			_mine.hide()
			hud.world_move_deco(_mine_sprite))
		_mine_body.add_child(mv)


func _dig(tool: String) -> void:
	var got := Game.dig_mine(tool)
	if got.is_empty():
		Game.toast.emit(tr("BARN_FULL"), "ico_barn.png")
		return
	Audio.play("harvest", 0.8)
	for k in got:
		Game.toast.emit("+%d %s" % [int(got[k]), tr("ITEM_" + str(k))], "item_%s.png" % k)
	_fill_mine()
