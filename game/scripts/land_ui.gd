class_name LandUI
extends Node
## M9.5 windows: silo/barn storage with upgrades, land parcel popup, obstacle popup,
## and the card shop (tabs on top, horizontal cards along the bottom of the screen).

const TILE := 176.0
const CARD := Vector2(330, 440)
const TABS := ["fields", "buildings", "animals"]

var hud: Hud
var world: Node
var _store: Control
var _store_title: Label
var _store_grid: GridContainer
var _store_bar: Control
var _store_silo := false
var _store_sel := ""
var _upgrade: Control
var _popup: Control
var _shop: Control
var _shop_row: HBoxContainer
var _shop_tab := "fields"
var _tab_buttons: Dictionary = {}


func setup(h: Hud) -> void:
	hud = h
	_build_store()
	_build_popup()
	_build_shop()


# ------------------------------------------------------------------ storage

func _build_store() -> void:
	var r: Array = hud._panel_window(Vector2(1240, 980), "BARN")
	_store = r[0]
	_store_title = r[1]
	var scroll := ScrollContainer.new()
	scroll.position = Vector2(50, 110)
	scroll.size = Vector2(1140, 600)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	_store.add_child(scroll)
	_store_grid = GridContainer.new()
	_store_grid.columns = 6
	_store_grid.add_theme_constant_override("h_separation", 14)
	_store_grid.add_theme_constant_override("v_separation", 14)
	scroll.add_child(_store_grid)
	_store_bar = Control.new()
	_store_bar.position = Vector2(50, 730)
	_store.add_child(_store_bar)
	hud.extra_windows.append(_store)
	_upgrade = hud._panel_window(Vector2(1000, 640), "UPGRADE")[0]
	hud.extra_windows.append(_upgrade)


func open_store(silo: bool) -> void:
	Audio.play("whoosh")
	_store_silo = silo
	_store_sel = ""
	_fill_store()
	hud._open(_store)


func refresh_store() -> void:
	if _store.visible:
		_fill_store()
	if world:
		world.farm.refresh_silo()


func _fill_store() -> void:
	var silo := _store_silo
	_store_title.text = "%s  %d / %d" % [tr("SILO" if silo else "BARN"), Game.stored(silo), Game.capacity(silo)]
	for c in _store_grid.get_children():
		c.queue_free()
	var items: Array = []
	for id in Game.item_order():
		if Game.in_silo(id) == silo and Game.count(id) > 0:
			items.append(id)
	if _store_sel == "" and not items.is_empty():
		_store_sel = items[0]
	for id in items:
		_store_grid.add_child(_tile(id))
	if items.is_empty():
		var l := hud._dark(hud._label("STORE_EMPTY", 36))
		l.custom_minimum_size = Vector2(1100, 200)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_store_grid.add_child(l)
	_fill_store_bar()


func _tile(id: String) -> Control:
	var b := TextureButton.new()
	b.texture_normal = load(Hud.UI + "slot.png")
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	b.custom_minimum_size = Vector2(TILE, TILE)
	b.focus_mode = Control.FOCUS_NONE
	if id == _store_sel:
		b.modulate = Color(1.15, 1.1, 0.8)
	hud._press_feedback(b)
	var icon := hud._item_icon(id, TILE - 40)
	icon.position = Vector2(20, 14)
	b.add_child(icon)
	var n := hud._label(str(Game.count(id)), 34)
	n.position = Vector2(0, TILE - 60)
	n.size = Vector2(TILE - 14, 50)
	n.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	b.add_child(n)
	b.pressed.connect(func() -> void:
		Audio.play("click")
		_store_sel = id
		_fill_store())
	return b


func _fill_store_bar() -> void:
	for c in _store_bar.get_children():
		c.queue_free()
	var which := "silo" if _store_silo else "barn"
	var up := hud._pill("UPGRADE", Vector2(820, 120), 320)
	up.pressed.connect(func() -> void: _open_upgrade(which))
	_store_bar.add_child(up)
	if _store_sel == "" or Game.count(_store_sel) <= 0:
		return
	var id := _store_sel
	var name_l := hud._dark(hud._label("ITEM_" + id, 42))
	name_l.position = Vector2(0, 0)
	name_l.size = Vector2(520, 60)
	_store_bar.add_child(name_l)
	var coin := hud._tex("coin.png")
	coin.scale = Vector2(0.5, 0.5)
	coin.position = Vector2(540, 6)
	_store_bar.add_child(coin)
	var price := hud._dark(hud._label(str(Game.price(id)), 38))
	price.position = Vector2(600, 0)
	price.size = Vector2(120, 60)
	_store_bar.add_child(price)
	var one := hud._pill("SELL_ONE", Vector2(0, 120), 360)
	one.pressed.connect(func() -> void: _sell(id, 1))
	_store_bar.add_child(one)
	var all := hud._pill("SELL_ALL", Vector2(380, 120), 300)
	all.pressed.connect(func() -> void: _sell(id, Game.count(id)))
	_store_bar.add_child(all)


func _sell(id: String, n: int) -> void:
	if Game.sell(id, n) > 0:
		Audio.play("coin", 1.0, 0.05)
		if Game.count(id) <= 0:
			_store_sel = ""
		_fill_store()


func _open_upgrade(which: String) -> void:
	Audio.play("click")
	for c in _upgrade.get_children().slice(2):
		c.queue_free()
	(_upgrade.get_child(0) as Label).text = tr("UPGRADE_" + which.to_upper()) % \
			[Game.capacity(which == "silo"), Game.capacity(which == "silo") + Game.STORE_STEP]
	var need := Game.upgrade_need(which)
	var items: Array = Game.UPGRADE_ITEMS[which]
	for i in items.size():
		var id: String = items[i]
		var x := 90.0 + i * 290.0
		var slot := hud._tex("slot.png")
		slot.position = Vector2(x, 130)
		slot.scale = Vector2(1.3, 1.3)
		_upgrade.add_child(slot)
		var icon := hud._item_icon(id, 140)
		icon.position = Vector2(x + 18, 146)
		_upgrade.add_child(icon)
		var have := Game.count(id)
		var l := hud._label("%d / %d" % [have, need], 40)
		l.position = Vector2(x - 20, 330)
		l.size = Vector2(240, 60)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		if have < need:
			l.add_theme_color_override("font_color", Color("FF8A7A"))
		_upgrade.add_child(l)
		var nm := hud._dark(hud._label("ITEM_" + id, 30))
		nm.position = Vector2(x - 20, 390)
		nm.size = Vector2(240, 50)
		nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_upgrade.add_child(nm)
	var go := hud._pill("UPGRADE", Vector2(320, 490), 360, Game.can_upgrade(which))
	go.pressed.connect(func() -> void:
		if Game.upgrade_store(which):
			Audio.play("levelup")
			Game.toast.emit(tr("UPGRADED") % Game.capacity(which == "silo"), "ico_%s.png" % which)
			_upgrade.hide()
			if world:
				world.farm.refresh_silo()
			_fill_store())
	_upgrade.add_child(go)
	hud._open(_upgrade)
	_store.show()


# ------------------------------------------------------------------ popups (parcel, obstacle)

func _build_popup() -> void:
	_popup = hud._panel_window(Vector2(900, 620), "")[0]
	hud.extra_windows.append(_popup)


func _clear_popup(title: String) -> void:
	for c in _popup.get_children().slice(2):
		c.queue_free()
	(_popup.get_child(0) as Label).text = title


func open_parcel(id: String) -> void:
	_clear_popup(tr("LAND_TITLE"))
	var c := Farm.parcel_cost(id)
	var info := hud._dark(hud._label(tr("LAND_INFO"), 34))
	info.position = Vector2(60, 100)
	info.size = Vector2(780, 90)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_popup.add_child(info)
	for i in Game.LAND_ITEMS.size():
		var it: String = Game.LAND_ITEMS[i]
		var x := 90.0 + i * 250.0
		var slot := hud._tex("slot.png")
		slot.position = Vector2(x, 200)
		_popup.add_child(slot)
		var icon := hud._item_icon(it, 110)
		icon.position = Vector2(x + 18, 214)
		_popup.add_child(icon)
		var have := Game.count(it)
		var l := hud._label("%d / %d" % [have, int(c["items"])], 36)
		l.position = Vector2(x - 30, 360)
		l.size = Vector2(210, 56)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		if have < int(c["items"]):
			l.add_theme_color_override("font_color", Color("FF8A7A"))
		_popup.add_child(l)
	var why: String = world.farm.can_buy_parcel(id)
	var go := hud._pill("", Vector2(250, 460), 400, why == "")
	(go.get_child(0) as Label).text = "%s  %s" % [tr("LAND_BUY"), Hud.fmt(int(c["coins"]))]
	go.pressed.connect(func() -> void:
		if world.farm.buy_parcel(id):
			Game.toast.emit(tr("LAND_DONE"), "ico_build.png")
			_popup.hide())
	_popup.add_child(go)
	if why != "":
		var wl := hud._dark(hud._label(why, 30))
		wl.position = Vector2(60, 420)
		wl.size = Vector2(780, 40)
		wl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_popup.add_child(wl)
	hud._open(_popup)


func open_obstacle(s: Sprite2D) -> void:
	var tool: String = s.get_meta("tool")
	if not Farm.cell_open(world.cell_at(s.position)):
		Game.toast.emit(tr("LAND_LOCKED"), "ico_lock.png")
		return
	_clear_popup(tr("OBSTACLE_" + tool))
	var slot := hud._tex("slot.png")
	slot.position = Vector2(330, 120)
	slot.scale = Vector2(1.4, 1.4)
	_popup.add_child(slot)
	var icon := hud._item_icon(tool, 160)
	icon.position = Vector2(352, 140)
	_popup.add_child(icon)
	var have := Game.count(tool)
	var l := hud._label("%s: %d" % [tr("ITEM_" + tool), have], 38)
	l.position = Vector2(0, 340)
	l.size = Vector2(900, 60)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_popup.add_child(l)
	var hint := hud._dark(hud._label("TOOL_HINT", 28))
	hint.position = Vector2(60, 400)
	hint.size = Vector2(780, 50)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_popup.add_child(hint)
	var go := hud._pill("USE_TOOL", Vector2(270, 470), 360, have > 0)
	go.pressed.connect(func() -> void:
		_popup.hide()
		world.farm.clear_obstacle(s))
	_popup.add_child(go)
	hud._open(_popup)


# ------------------------------------------------------------------ shop

func _build_shop() -> void:
	_shop = Control.new()
	_shop.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_shop.offset_top = -CARD.y - 190
	_shop.offset_bottom = 0
	_shop.mouse_filter = Control.MOUSE_FILTER_STOP
	_shop.visible = false
	hud._root.add_child(_shop)
	var back := hud._patch("panel.png", 44, 44)
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.offset_top = 120
	back.self_modulate = Color(1.0, 0.86, 0.45)
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_shop.add_child(back)
	var tabs := HBoxContainer.new()
	tabs.position = Vector2(40, 0)
	tabs.add_theme_constant_override("separation", 14)
	_shop.add_child(tabs)
	for t in TABS:
		var b := TextureButton.new()
		b.texture_normal = load(Hud.UI + "tab_%s.png" % t)
		b.ignore_texture_size = true
		b.stretch_mode = TextureButton.STRETCH_SCALE
		b.custom_minimum_size = Vector2(150, 136)
		b.focus_mode = Control.FOCUS_NONE
		hud._press_feedback(b)
		b.pressed.connect(func() -> void:
			Audio.play("click")
			_shop_tab = t
			_fill_shop())
		tabs.add_child(b)
		_tab_buttons[t] = b
	var close := TextureButton.new()
	close.texture_normal = load(Hud.UI + "btn_round.png")
	close.ignore_texture_size = true
	close.stretch_mode = TextureButton.STRETCH_SCALE
	close.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	close.offset_left = -130
	close.offset_top = 20
	close.offset_right = -34
	close.offset_bottom = 122
	close.focus_mode = Control.FOCUS_NONE
	hud._press_feedback(close)
	close.pressed.connect(func() -> void:
		Audio.play("click")
		_shop.hide())
	var x := hud._tex("ico_close.png")
	x.position = Vector2(16, 16)
	close.add_child(x)
	_shop.add_child(close)
	var scroll := ScrollContainer.new()
	scroll.set_anchors_preset(Control.PRESET_FULL_RECT)
	scroll.offset_left = 40
	scroll.offset_right = -40
	scroll.offset_top = 160
	scroll.offset_bottom = -20
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_ALWAYS
	_shop.add_child(scroll)
	_shop_row = HBoxContainer.new()
	_shop_row.add_theme_constant_override("separation", 22)
	scroll.add_child(_shop_row)
	hud.extra_windows.append(_shop)


func open_shop(tab := "") -> void:
	Audio.play("whoosh")
	if tab != "":
		_shop_tab = tab
	hud.close_menus()
	_fill_shop()
	_shop.show()
	_shop.modulate.a = 1.0
	_shop.pivot_offset = Vector2(0, _shop.size.y)
	_shop.scale = Vector2(1, 0.85)
	hud.create_tween().tween_property(_shop, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK) \
		.set_ease(Tween.EASE_OUT)


func is_shop_open() -> bool:
	return _shop.visible


func _fill_shop() -> void:
	for t in _tab_buttons:
		var b: TextureButton = _tab_buttons[t]
		b.modulate = Color.WHITE if t == _shop_tab else Color(0.8, 0.8, 0.8)
		b.scale = Vector2.ONE if t == _shop_tab else Vector2(0.92, 0.92)
	for c in _shop_row.get_children():
		c.queue_free()
	match _shop_tab:
		"fields":
			_shop_row.add_child(_card("item_field", "FIELD", "%d / %d" % [world.fields.size(), Game.max_fields()],
				Game.field_price(), 1, func() -> void:
					_shop.hide()
					hud.buy_field.emit()))
			for i in range(1, Game.RODS.size()):
				var r: Dictionary = Game.RODS[i]
				if Game.rod >= i:
					continue
				_shop_row.add_child(_card(r["id"], r["id"].to_upper(), "ROD_SUB", int(r["price"]), int(r["unlock"]),
					func() -> void:
						if Game.buy_rod(i):
							Audio.play("levelup")
							Game.toast.emit(tr(r["id"].to_upper()), r["id"] + ".png")
							_fill_shop()
						else:
							Game.toast.emit(tr("NOT_ENOUGH_COINS"), "coin.png")))
		"buildings":
			for k in Game.placeables:
				var d: Dictionary = Game.placeables[k]
				if not d.get("building", false):
					continue
				var owned := Game.placed_count(k) > 0
				_shop_row.add_child(_card("@" + k, "PLACE_" + k, "OWNED" if owned else "BUILD_SUB_" + k,
					int(d["price"]), int(d["unlock"]), func() -> void: _buy_place(k), owned))
		"animals":
			for k in Game.placeables:
				var d: Dictionary = Game.placeables[k]
				if not d.has("animal"):
					continue
				var animal: String = d["animal"]
				var have := Game.placed_count(k) > 0
				if not have:
					_shop_row.add_child(_card("@" + k, "PLACE_" + k, "BUILD_SUB_" + k, int(d["price"]),
						int(d["unlock"]), func() -> void: _buy_place(k)))
				else:
					var n := int(world.pens[animal]["p"].get("n", 0)) if world.pens.has(animal) else 0
					_shop_row.add_child(_card("@" + animal, "ANIMAL_" + animal, "%d / %d" % [n, int(d["cap"])],
						world.animal_price(animal), int(d["unlock"]), func() -> void:
							var why: String = world.buy_animal(animal)
							if why != "":
								Game.toast.emit(why, "coin.png")
							else:
								_fill_shop(), n >= int(d["cap"])))


func _buy_place(kind: String) -> void:
	var d: Dictionary = Game.placeables[kind]
	if Game.coins < int(d["price"]):
		Game.toast.emit(tr("NOT_ENOUGH_COINS"), "coin.png")
		return
	_shop.hide()
	world.start_place_kind(kind)


## A shop card: picture, name, a sub line and a price button. Locked cards are grey with a lock.
func _card(icon: String, title: String, sub: String, price: int, unlock: int, act: Callable, done := false) -> Control:
	var locked := Game.level < unlock
	var card := hud._patch("panel.png", 44, 44)
	card.custom_minimum_size = CARD
	card.self_modulate = Color(0.72, 0.72, 0.74) if locked else Color(1.0, 0.97, 0.88)
	var pic := TextureRect.new()
	pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	pic.position = Vector2(30, 70)
	pic.size = Vector2(CARD.x - 60, 190)
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if icon.begins_with("@"):
		var n := icon.substr(1)
		var spr := n if Atlas.has(n) else ("%s_idle_se_0" % n if Atlas.has("%s_idle_se_0" % n) else "site_big")
		if Atlas.has(spr):
			pic.texture = Atlas.tex(spr)
	else:
		pic.texture = load(Hud.UI + icon + ".png")
	if locked:
		pic.modulate = Color(0.25, 0.25, 0.28, 0.75)
	card.add_child(pic)
	var t := hud._dark(hud._label(title, 36))
	t.position = Vector2(10, 16)
	t.size = Vector2(CARD.x - 20, 54)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	card.add_child(t)
	var st := hud._dark(hud._label(sub if not locked else tr("UNLOCK_AT") % unlock, 26))
	st.position = Vector2(14, 264)
	st.size = Vector2(CARD.x - 28, 70)
	st.autowrap_mode = TextServer.AUTOWRAP_WORD
	st.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	card.add_child(st)
	if locked:
		var lock := hud._tex("ico_lock.png")
		lock.position = Vector2(CARD.x / 2 - 40, 130)
		card.add_child(lock)
		return card
	if done:
		return card
	var b := hud._pill("", Vector2(40, 334), CARD.x - 80)
	(b.get_child(0) as Label).text = "    " + Hud.fmt(price) if price > 0 else tr("FREE")
	if price > 0:
		var coin := hud._tex("coin.png")
		coin.scale = Vector2(0.5, 0.5)
		coin.position = Vector2(46, 18)
		b.add_child(coin)
	b.pressed.connect(func() -> void:
		Audio.play("click")
		act.call())
	card.add_child(b)
	return card
