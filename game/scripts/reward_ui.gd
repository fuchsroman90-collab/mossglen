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
var _stand: Control
var _stand_body: Control
var _stand_sprite: Sprite2D
var _stand_pick := ""
var _timer: Control
var _timer_fill: ColorRect
var _timer_title: Label
var _timer_time: Label
var _timer_cost: Label
var _timer_left: Callable
var _timer_total := 1.0
var _timer_speed: Callable
var _timer_hide := 0.0
var _vis: Control
var _vis_body: Control
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
	_stand = hud._panel_window(Vector2(1400, 900), "STAND_TITLE")[0]
	hud.extra_windows.append(_stand)
	_stand_body = Control.new()
	_stand.add_child(_stand_body)
	# market awning over the window: red and cream stripes with a scalloped edge
	var aw := Control.new()
	aw.position = Vector2(-40, -150)
	aw.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_stand.add_child(aw)
	_stand.move_child(aw, 0)
	for i in 12:
		var col := Color("E0302A") if i % 2 == 0 else Color("FFF4E2")
		var stripe := Polygon2D.new()
		stripe.polygon = PackedVector2Array([Vector2(60 + i * 110, 0), Vector2(60 + (i + 1) * 110, 0),
			Vector2(20 + (i + 1) * 123.3, 150), Vector2(20 + i * 123.3 - 20, 150)])
		stripe.polygon = PackedVector2Array([Vector2(80 + i * 110, 0), Vector2(80 + (i + 1) * 110, 0),
			Vector2((i + 1) * 123.3, 150), Vector2(i * 123.3, 150)])
		stripe.color = col
		aw.add_child(stripe)
		var scallop := Polygon2D.new()
		var pts := PackedVector2Array()
		for k in 13:
			var a := PI * k / 12.0
			pts.append(Vector2(i * 123.3 + 61.65 - cos(a) * 61.65, 150 + sin(a) * 44.0))
		scallop.polygon = pts
		scallop.color = col
		aw.add_child(scallop)
	_vis = hud._panel_window(Vector2(1320, 760), "VISITOR_TITLE")[0]
	hud.extra_windows.append(_vis)
	_vis_body = Control.new()
	_vis.add_child(_vis_body)
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


# ------------------------------------------------------------------ visiting buyer

func open_visitor(s: Sprite2D) -> void:
	if s == null:
		return
	var o: Dictionary = s.get_meta("visitor")
	for c in _vis_body.get_children():
		c.queue_free()
	var pic := TextureRect.new()
	pic.texture = Atlas.tex("npc_pip_0")
	pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	pic.position = Vector2(30, 110)
	pic.size = Vector2(420, 600)
	_vis_body.add_child(pic)
	# speech bubble with the offer in its own frame
	var bub := hud._patch("panel.png", 44, 44)
	bub.position = Vector2(470, 110)
	bub.size = Vector2(790, 330)
	bub.self_modulate = Color(1, 1, 1)
	_vis_body.add_child(bub)
	var say := hud._dark(hud._label(tr("VISITOR_ASK"), 36))
	say.position = Vector2(30, 22)
	say.size = Vector2(730, 60)
	say.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bub.add_child(say)
	var n := hud._label("%d×" % int(o["n"]), 60)
	n.position = Vector2(110, 120)
	n.size = Vector2(130, 80)
	n.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	bub.add_child(n)
	var ic := hud._item_icon(o["item"], 140)
	ic.position = Vector2(250, 92)
	bub.add_child(ic)
	var arrow := hud._label("➜", 60)
	arrow.position = Vector2(400, 120)
	arrow.modulate = Color("#FFD23F")
	bub.add_child(arrow)
	var coin := hud._tex("coin.png")
	coin.position = Vector2(480, 116)
	bub.add_child(coin)
	var pay := hud._label(Hud.fmt(int(o["pay"])), 60)
	pay.position = Vector2(580, 120)
	bub.add_child(pay)
	var have := Game.count(o["item"])
	var hv := hud._dark(hud._label(tr("VISITOR_HAVE") % [have, tr("ITEM_" + str(o["item"]))], 30))
	hv.position = Vector2(30, 262)
	hv.size = Vector2(730, 44)
	hv.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bub.add_child(hv)
	var yes := hud._pill("VISITOR_YES", Vector2(560, 480), 620, have >= int(o["n"]))
	yes.pressed.connect(func() -> void:
		if Game.accept_visitor(o):
			Audio.play("levelup")
			Game.toast.emit("+%s" % Hud.fmt(int(o["pay"])), "coin.png")
			_vis.hide()
			hud.visitor_done.emit())
	_vis_body.add_child(yes)
	var no := hud._pill("VISITOR_NO", Vector2(560, 600), 620)
	no.self_modulate = Color(1.0, 0.85, 0.4)
	no.pressed.connect(func() -> void:
		_vis.hide()
		hud.visitor_done.emit())
	_vis_body.add_child(no)
	hud._open(_vis)


# ------------------------------------------------------------------ roadside stand

func open_stand(s: Sprite2D) -> void:
	_stand_sprite = s
	_stand_pick = ""
	_fill_stand()
	hud._open(_stand)


func _process(d: float) -> void:
	if _stand != null and _stand.visible and Engine.get_process_frames() % 30 == 0:
		_fill_stand()
	if _timer != null and _timer.visible:
		var left: float = _timer_left.call()
		_timer_hide -= d
		if left <= 0.0 or _timer_hide <= 0.0:
			_timer.visible = false
			return
		_timer_fill.size.x = 820.0 * clampf(1.0 - left / maxf(_timer_total, 1.0), 0.03, 1.0)
		_timer_time.text = Hud._fmt_time(int(ceil(left)))
		_timer_cost.text = str(speed_cost(left))


# ------------------------------------------------------------------ time bar with speed-up

static func speed_cost(left: float) -> int:
	return 1 + int(left / 180.0)


## Bottom bar: what is being made, how long it still takes, and a lightning button that finishes it for emeralds.
func show_timer(title: String, left_fn: Callable, total: float, speed_fn: Callable) -> void:
	if _timer == null:
		_timer = hud._patch("panel.png", 44, 44)
		_timer.size = Vector2(900, 150)
		hud._root.add_child(_timer)
		var track := ColorRect.new()
		track.color = Color("1F4F9E")
		track.position = Vector2(40, 52)
		track.size = Vector2(820, 46)
		_timer.add_child(track)
		_timer_fill = ColorRect.new()
		_timer_fill.color = Color("4FB4F5")
		_timer_fill.position = Vector2(40, 52)
		_timer_fill.size = Vector2(10, 46)
		_timer.add_child(_timer_fill)
		_timer_title = hud._label("", 44)
		_timer_title.position = Vector2(0, -34)
		_timer_title.size = Vector2(900, 60)
		_timer_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_timer.add_child(_timer_title)
		_timer_time = hud._label("", 40)
		_timer_time.position = Vector2(0, 92)
		_timer_time.size = Vector2(900, 56)
		_timer_time.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_timer.add_child(_timer_time)
		var b := hud._round_button("ico_bolt.png", Vector2(900, -6), 160)
		hud._root.remove_child(b)
		_timer.add_child(b)
		b.pressed.connect(_speed_up)
		var tag := hud._patch("panel.png", 44, 44)
		tag.position = Vector2(1050, 34)
		tag.size = Vector2(170, 86)
		_timer.add_child(tag)
		_timer_cost = hud._dark(hud._label("1", 44))
		_timer_cost.position = Vector2(20, 12)
		tag.add_child(_timer_cost)
		var gem := hud._tex("gem.png")
		gem.position = Vector2(86, 14)
		gem.scale = Vector2(0.6, 0.6)
		tag.add_child(gem)
	_timer.position = Vector2(hud._root.size.x * 0.5 - 560.0, hud._root.size.y - 340.0)
	_timer_title.text = title
	_timer_left = left_fn
	_timer_total = total
	_timer_speed = speed_fn
	_timer_hide = 6.0
	_timer.visible = true


func _speed_up() -> void:
	var left: float = _timer_left.call()
	var cost := speed_cost(left)
	if Game.emeralds < cost:
		Game.toast.emit(tr("NOT_ENOUGH_EMERALDS"), "gem.png")
		return
	Game.add_emeralds(-cost)
	_timer_speed.call()
	_timer.visible = false
	Audio.play("levelup", 1.3)


func _fill_stand() -> void:
	for c in _stand_body.get_children():
		c.queue_free()
	var now := Time.get_unix_time_from_system()
	# top frame: the four slots on the counter
	for i in Game.STAND_SLOTS:
		var t := hud._patch("panel.png", 44, 44)
		t.position = Vector2(60 + i * 322, 110)
		t.size = Vector2(300, 330)
		_stand_body.add_child(t)
		if i >= Game.stand.size():
			t.self_modulate = Color(1.0, 0.82, 0.42)
			var e := hud._dark(hud._label("STAND_EMPTY", 30))
			e.position = Vector2(0, 140)
			e.size = Vector2(300, 44)
			e.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			t.add_child(e)
			continue
		var sl: Dictionary = Game.stand[i]
		var sold := Game.stand_sold(i)
		t.self_modulate = Color(0.78, 0.95, 0.7) if sold else Color(1.0, 0.93, 0.7)
		var ic := hud._item_icon(sl["item"], 130)
		ic.position = Vector2(85, 16)
		t.add_child(ic)
		var n := hud._label("x%d" % int(sl["n"]), 40)
		n.position = Vector2(180, 100)
		t.add_child(n)
		var coin := hud._tex("coin.png")
		coin.scale = Vector2(0.55, 0.55)
		coin.position = Vector2(70, 160)
		t.add_child(coin)
		var pay := hud._label(Hud.fmt(int(sl["pay"])), 40)
		pay.position = Vector2(130, 162)
		t.add_child(pay)
		if sold:
			var b := hud._pill("STAND_COLLECT", Vector2(30, 232), 240)
			b.pressed.connect(func() -> void:
				var got := Game.stand_collect(i)
				if got > 0:
					Audio.play("levelup")
					Game.toast.emit("+%s" % Hud.fmt(got), "coin.png")
				_fill_stand())
			t.add_child(b)
		else:
			var left := int(ceil(float(sl["t0"]) + float(sl["dur"]) - now))
			var w := hud._dark(hud._label(tr("STAND_WAIT") % [left / 60, left % 60], 30))
			w.position = Vector2(0, 250)
			w.size = Vector2(300, 44)
			w.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			t.add_child(w)
	# bottom frame: choose goods, then a price
	var box := hud._patch("panel.png", 44, 44)
	box.position = Vector2(60, 470)
	box.size = Vector2(1280, 370)
	box.self_modulate = Color(0.86, 0.93, 1.0)
	_stand_body.add_child(box)
	if Game.stand.size() >= Game.STAND_SLOTS:
		var f := hud._dark(hud._label("STAND_FULL", 34))
		f.position = Vector2(0, 150)
		f.size = Vector2(1280, 50)
		f.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		box.add_child(f)
		return
	if _stand_pick == "" or Game.count(_stand_pick) < 1:
		_stand_pick = ""
		var h := hud._dark(hud._label("STAND_PICK", 32))
		h.position = Vector2(30, 16)
		box.add_child(h)
		var goods: Array = []
		for k in Game.inventory:
			if Game.count(k) > 0 and Game.price(k) > 0 and Game.items.get(k, {}).get("kind", "") != "tool":
				goods.append(k)
		goods.sort_custom(func(a: String, b: String) -> bool: return Game.count(a) > Game.count(b))
		for j in mini(goods.size(), 16):
			var k: String = goods[j]
			var gb := TextureButton.new()
			gb.texture_normal = load(Hud.UI + "slot.png")
			gb.position = Vector2(30 + (j % 8) * 152, 70 + (j / 8) * 146)
			gb.pressed.connect(func() -> void:
				_stand_pick = k
				Audio.play("click")
				_fill_stand())
			box.add_child(gb)
			var gi := hud._item_icon(k, 96)
			gi.position = Vector2(22, 12)
			gi.mouse_filter = Control.MOUSE_FILTER_IGNORE
			gb.add_child(gi)
			var gl := hud._label(str(Game.count(k)), 32)
			gl.position = Vector2(80, 92)
			gl.mouse_filter = Control.MOUSE_FILTER_IGNORE
			gb.add_child(gl)
		return
	var n_put := mini(Game.count(_stand_pick), 5)
	var pi := hud._item_icon(_stand_pick, 150)
	pi.position = Vector2(40, 40)
	box.add_child(pi)
	var pl := hud._dark(hud._label("%d× %s" % [n_put, tr("ITEM_" + _stand_pick)], 36))
	pl.position = Vector2(30, 210)
	box.add_child(pl)
	var back := hud._pill("STAND_BACK", Vector2(30, 280), 220)
	back.pressed.connect(func() -> void:
		_stand_pick = ""
		_fill_stand())
	box.add_child(back)
	for lv in 3:
		var pay_v := int(ceil(float(Game.price(_stand_pick)) * n_put * float(Game.STAND_PRICES[lv][0])))
		var secs := int(45.0 * n_put * float(Game.STAND_PRICES[lv][1]))
		var pt := hud._patch("panel.png", 44, 44)
		pt.position = Vector2(300 + lv * 322, 30)
		pt.size = Vector2(300, 310)
		box.add_child(pt)
		var tl := hud._dark(hud._label(["STAND_CHEAP", "STAND_FAIR", "STAND_DEAR"][lv], 32))
		tl.position = Vector2(0, 16)
		tl.size = Vector2(300, 44)
		tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		pt.add_child(tl)
		var pv := hud._label(Hud.fmt(pay_v), 56)
		pv.position = Vector2(0, 70)
		pv.size = Vector2(300, 70)
		pv.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		pt.add_child(pv)
		var tv := hud._dark(hud._label(tr("STAND_WAIT") % [secs / 60, secs % 60], 28))
		tv.position = Vector2(0, 146)
		tv.size = Vector2(300, 40)
		tv.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		pt.add_child(tv)
		var pb := hud._pill("STAND_PUT", Vector2(30, 210), 240)
		pb.pressed.connect(func() -> void:
			if Game.stand_put(_stand_pick, n_put, lv):
				Audio.play("pop")
				_stand_pick = ""
			_fill_stand())
		pt.add_child(pb)
