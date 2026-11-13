extends Node
## Player economy, inventory, progression, language and local save.
## Cloud save comes in M6; the save format is versioned for that.

signal coins_changed(value: int)
signal emeralds_changed(value: int)
signal xp_changed(xp: int, needed: int, level: int)
signal inventory_changed(item: String, count: int)
signal leveled_up(level: int, unlocked: Array)
signal toast(text: String, icon: String)
signal orders_changed
signal fish_caught(id: String)

const I18N_PATH := "res://i18n/strings.txt"
const SAVE_PATH := "user://save.json"
const SAVE_VERSION := 1
const LOCALES := ["de", "en"]
const AUTOSAVE_SECONDS := 5.0

var crops: Dictionary = {}  ## crop id -> {grow, sell, xp, unlock, yield}
var crop_order: Array = []
var items: Dictionary = {}  ## product id -> {sell}
var buildings: Dictionary = {}  ## building id -> {slots, fx, recipes[]}
var animal_defs: Dictionary = {}  ## animal kind -> {feed, product, time, xp, unlock}
var orders: Array = []  ## [{need: {item: n}, coins, xp, wait_until}]
var fish: Array = []  ## species from data/fish.json
var fish_by_id: Dictionary = {}
var fish_log: Dictionary = {}  ## id -> {"n": caught, "best": cm}
var rod := 0  ## 0 wood, 1 bamboo, 2 gold
var spots: Dictionary = {}  ## fishing spot -> {"stock": float, "t": unix}
const SPOT_MAX := 5.0
const SPOT_REGEN := 90.0  ## seconds per fish
const RODS := [{"id": "rod_wood", "price": 0, "unlock": 1}, {"id": "rod_bamboo", "price": 150, "unlock": 4},
	{"id": "rod_gold", "price": 600, "unlock": 8}]
const ORDER_SLOTS := 6
const ORDER_WAIT := 20.0
var coins := 60
var emeralds := 5
var xp := 0
var level := 1
var inventory: Dictionary = {"wheat": 6, "feed_chicken": 3}
var barn_capacity := 80
var extra_fields := 0
var font_bold: FontVariation
var font_regular: FontVariation
## World layout from the save (fields), applied by world.gd. Empty = default farm.
var saved_world: Dictionary = {}
var world_saver: Callable  ## () -> Dictionary, provided by world.gd
var persist := true

var _dirty := false
var _save_timer := 0.0


func _ready() -> void:
	font_bold = _font(600)
	font_regular = _font(500)
	_load_crops()
	items = _json("res://data/items.json")
	buildings = _json("res://data/buildings.json")
	animal_defs = _json("res://data/animals.json")
	fish = JSON.parse_string(FileAccess.get_file_as_string("res://data/fish.json"))
	for f in fish:
		fish_by_id[f["id"]] = f
	_load_translations()
	var lang := OS.get_locale_language()
	TranslationServer.set_locale(lang if lang in LOCALES else "en")
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--smoke") or a.begins_with("--bench") or a.begins_with("--shot") or a.begins_with("--demo"):
			persist = false
	if persist:
		load_game()
	ensure_orders()


func _process(delta: float) -> void:
	if not _dirty or not persist:
		return
	_save_timer += delta
	if _save_timer >= AUTOSAVE_SECONDS:
		save_game()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_APPLICATION_PAUSED \
			or what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		if persist and _dirty:
			save_game()


func mark_dirty() -> void:
	_dirty = true


# ------------------------------------------------------------------ economy

func add_coins(n: int) -> void:
	coins += n
	coins_changed.emit(coins)
	mark_dirty()


func spend_coins(n: int) -> bool:
	if coins < n:
		return false
	add_coins(-n)
	return true


func add_emeralds(n: int) -> void:
	emeralds += n
	emeralds_changed.emit(emeralds)
	mark_dirty()


func xp_needed() -> int:
	return 8 + level * 6


func add_xp(n: int) -> void:
	xp += n
	var unlocked: Array = []
	while xp >= xp_needed():
		xp -= xp_needed()
		level += 1
		for c in crop_order:
			if int(crops[c]["unlock"]) == level:
				unlocked.append(c)
				add_item(c, 2, true)  # a starter gift for each new crop
		leveled_up.emit(level, unlocked)
	xp_changed.emit(xp, xp_needed(), level)
	mark_dirty()


# ------------------------------------------------------------------ inventory

func count(item: String) -> int:
	return int(inventory.get(item, 0))


func stored() -> int:
	var n := 0
	for v in inventory.values():
		n += int(v)
	return n


func space() -> int:
	return barn_capacity - stored()


## Adds items; returns how many fit. force ignores the barn limit (gifts).
func add_item(item: String, n: int, force := false) -> int:
	var fit := n if force else mini(n, space())
	if fit <= 0:
		return 0
	inventory[item] = count(item) + fit
	inventory_changed.emit(item, count(item))
	mark_dirty()
	return fit


func take_item(item: String, n := 1) -> bool:
	if count(item) < n:
		return false
	inventory[item] = count(item) - n
	if inventory[item] <= 0:
		inventory.erase(item)
	inventory_changed.emit(item, count(item))
	mark_dirty()
	return true


func price(item: String) -> int:
	if crops.has(item):
		return int(crops[item]["sell"])
	return int(items.get(item, {}).get("sell", 1))


## Items in barn display order: crops, then products in data order.
func item_order() -> Array:
	return crop_order + items.keys()


func sell(item: String, n := 1) -> int:
	n = mini(n, count(item))
	if n <= 0:
		return 0
	take_item(item, n)
	var earned: int = n * price(item)
	add_coins(earned)
	return earned


func is_unlocked(crop: String) -> bool:
	return level >= int(crops[crop]["unlock"])


func has_all(need: Dictionary) -> bool:
	for k in need:
		if count(k) < int(need[k]):
			return false
	return true


func take_all(need: Dictionary) -> bool:
	if not has_all(need):
		return false
	for k in need:
		take_item(k, int(need[k]))
	return true


# ------------------------------------------------------------------ fishing

func spot_stock(spot: String) -> int:
	var now := Time.get_unix_time_from_system()
	var d: Dictionary = spots.get(spot, {"stock": SPOT_MAX, "t": now})
	var st := minf(SPOT_MAX, float(d["stock"]) + (now - float(d["t"])) / SPOT_REGEN)
	spots[spot] = {"stock": st, "t": now}
	return int(floor(st))


func take_fish(spot: String) -> bool:
	if spot_stock(spot) < 1:
		return false
	spots[spot]["stock"] = float(spots[spot]["stock"]) - 1.0
	mark_dirty()
	return true


## Picks a fish for a place ("pond"/"river"/"sea") and time ("day"/"dusk"/"night").
## quality 0..1 from the timing ring: better timing -> rarer fish and bigger size.
func roll_fish(loc: String, time: String, quality: float) -> Dictionary:
	var weights := {1: 60.0, 2: 26.0 + 10.0 * quality, 3: 9.0 + 9.0 * quality + 6.0 * rod, 4: 1.0 + 2.0 * quality + 2.0 * rod}
	var pool: Array = []
	var total := 0.0
	for f in fish:
		if f["loc"] != loc or (f["time"] != "any" and f["time"] != time):
			continue
		var w: float = weights[int(f["rarity"])]
		pool.append([f, w])
		total += w
	var r := randf() * total
	var pick: Dictionary = pool[0][0]
	for p in pool:
		r -= p[1]
		if r <= 0.0:
			pick = p[0]
			break
	var lo: float = pick["size"][0]
	var hi: float = pick["size"][1]
	var size := lo + (hi - lo) * pow(randf(), 1.6 - quality)
	return {"id": pick["id"], "size": snappedf(size, 0.1)}


## Logs a catch. Returns {"new": bool, "record": bool}.
func record_catch(id: String, size: float) -> Dictionary:
	var e: Dictionary = fish_log.get(id, {"n": 0, "best": 0.0})
	var res := {"new": int(e["n"]) == 0, "record": size > float(e["best"]) and int(e["n"]) > 0}
	fish_log[id] = {"n": int(e["n"]) + 1, "best": maxf(float(e["best"]), size)}
	fish_caught.emit(id)
	mark_dirty()
	return res


func fish_value(id: String, size: float) -> int:
	var f: Dictionary = fish_by_id[id]
	var mid := (float(f["size"][0]) + float(f["size"][1])) * 0.5
	return maxi(1, int(round(float(f["price"]) * clampf(size / mid, 0.7, 1.5))))


func fish_name(id: String) -> String:
	var f: Dictionary = fish_by_id[id]
	return f["de"] if TranslationServer.get_locale().begins_with("de") else f["en"]


func buy_rod(level_idx: int) -> bool:
	var r: Dictionary = RODS[level_idx]
	if rod >= level_idx or level < int(r["unlock"]) or not spend_coins(int(r["price"])):
		return false
	rod = level_idx
	mark_dirty()
	return true


# ------------------------------------------------------------------ orders

## Items the player can currently make or grow (order candidates). Feeds are excluded.
func orderable_items() -> Array:
	var out: Array = []
	for c in crop_order:
		if is_unlocked(c):
			out.append(c)
	for a in animal_defs:
		if level >= int(animal_defs[a]["unlock"]):
			out.append(animal_defs[a]["product"])
	for b in buildings:
		for r in buildings[b]["recipes"]:
			if level >= int(r["unlock"]) and not str(r["out"]).begins_with("feed_"):
				out.append(r["out"])
	return out


func make_order() -> Dictionary:
	var pool := orderable_items()
	pool.shuffle()
	var kinds := mini(pool.size(), 1 + randi() % 3)
	var need := {}
	var value := 0
	for i in kinds:
		var it: String = pool[i]
		var p := price(it)
		var qty := clampi(int(round(randf_range(2.0, 6.0) * 10.0 / float(p + 6))) + 1, 1, 6)
		need[it] = qty
		value += qty * p
	return {"need": need, "coins": int(ceil(value * 1.4)), "xp": maxi(2, int(round(value / 5.0))), "wait_until": 0.0}


func ensure_orders() -> void:
	while orders.size() < ORDER_SLOTS:
		orders.append(make_order())


func order_ready(i: int) -> bool:
	return orders[i]["wait_until"] <= Time.get_unix_time_from_system()


func deliver(i: int) -> bool:
	var o: Dictionary = orders[i]
	if not order_ready(i) or not take_all(o["need"]):
		return false
	add_coins(int(o["coins"]))
	add_xp(int(o["xp"]))
	var fresh := make_order()
	fresh["wait_until"] = Time.get_unix_time_from_system() + 4.0  # a short pause before the next truck arrives
	orders[i] = fresh
	orders_changed.emit()
	mark_dirty()
	return true


## Throw an order away; a new one arrives after a short wait. No penalty (cozy).
func discard(i: int) -> void:
	var fresh := make_order()
	fresh["wait_until"] = Time.get_unix_time_from_system() + ORDER_WAIT
	orders[i] = fresh
	orders_changed.emit()
	mark_dirty()


func max_fields() -> int:
	return 12 + 3 * level


func field_price() -> int:
	return 15 + 10 * extra_fields


# ------------------------------------------------------------------ save

func save_game() -> void:
	_dirty = false
	_save_timer = 0.0
	if not persist:
		return
	var data := {
		"version": SAVE_VERSION,
		"saved_at": Time.get_unix_time_from_system(),
		"coins": coins, "emeralds": emeralds, "xp": xp, "level": level,
		"inventory": inventory, "extra_fields": extra_fields, "orders": orders,
		"fish_log": fish_log, "rod": rod, "spots": spots,
		"locale": TranslationServer.get_locale().substr(0, 2),
		"music": Audio.music_enabled,
		"world": world_saver.call() if world_saver.is_valid() else {},
	}
	var tmp := SAVE_PATH + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		push_warning("save failed: %s" % FileAccess.get_open_error())
		return
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
	DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp), ProjectSettings.globalize_path(SAVE_PATH))


func load_game() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or int(parsed.get("version", 0)) != SAVE_VERSION:
		push_warning("save file unreadable, starting fresh")
		return false
	coins = int(parsed["coins"])
	emeralds = int(parsed["emeralds"])
	xp = int(parsed["xp"])
	level = int(parsed["level"])
	inventory = {}
	for k in parsed["inventory"]:
		inventory[k] = int(parsed["inventory"][k])
	extra_fields = int(parsed.get("extra_fields", 0))
	if parsed.has("locale"):
		TranslationServer.set_locale(parsed["locale"])
	if parsed.has("music"):
		Audio.set_music_enabled.call_deferred(bool(parsed["music"]))
	saved_world = parsed.get("world", {})
	fish_log = {}
	for k in parsed.get("fish_log", {}):
		var e: Dictionary = parsed["fish_log"][k]
		fish_log[k] = {"n": int(e["n"]), "best": float(e["best"])}
	rod = int(parsed.get("rod", 0))
	spots = parsed.get("spots", {})
	orders = []
	for o in parsed.get("orders", []):
		var need := {}
		for k in o["need"]:
			need[k] = int(o["need"][k])
		orders.append({"need": need, "coins": int(o["coins"]), "xp": int(o["xp"]),
			"wait_until": float(o.get("wait_until", 0.0))})
	return true


func reset_save() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))


# ------------------------------------------------------------------ misc

func toggle_language() -> void:
	var cur := TranslationServer.get_locale().substr(0, 2)
	TranslationServer.set_locale("en" if cur == "de" else "de")
	mark_dirty()


func _load_crops() -> void:
	crops = JSON.parse_string(FileAccess.get_file_as_string("res://data/crops.json"))
	crop_order = crops.keys()
	crop_order.sort_custom(func(a, b) -> bool: return int(crops[a]["unlock"]) < int(crops[b]["unlock"]))


func _json(path: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func _font(weight: int) -> FontVariation:
	var f := FontVariation.new()
	f.base_font = load("res://fonts/Fredoka.ttf")
	var ts := TextServerManager.get_primary_interface()
	f.variation_opentype = {ts.name_to_tag("wght"): weight}
	return f


## Tab separated: key<TAB>de<TAB>en
func _load_translations() -> void:
	var f := FileAccess.open(I18N_PATH, FileAccess.READ)
	if f == null:
		push_error("missing " + I18N_PATH)
		return
	var header := f.get_line().split("\t")
	var tables: Array[Translation] = []
	for i in range(1, header.size()):
		var t := Translation.new()
		t.locale = header[i]
		tables.append(t)
	while not f.eof_reached():
		var line := f.get_line()
		if line.strip_edges().is_empty():
			continue
		var cols := line.split("\t")
		for i in range(1, min(cols.size(), header.size())):
			tables[i - 1].add_message(cols[0], cols[i])
	for t in tables:
		TranslationServer.add_translation(t)
