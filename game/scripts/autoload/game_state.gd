extends Node
## Player economy, inventory, progression, language and local save.
## Cloud save comes in M6; the save format is versioned for that.

signal coins_changed(value: int)
signal emeralds_changed(value: int)
signal xp_changed(xp: int, needed: int, level: int)
signal inventory_changed(item: String, count: int)
signal leveled_up(level: int, unlocked: Array)
signal toast(text: String, icon: String)

const I18N_PATH := "res://i18n/strings.txt"
const SAVE_PATH := "user://save.json"
const SAVE_VERSION := 1
const LOCALES := ["de", "en"]
const AUTOSAVE_SECONDS := 5.0

var crops: Dictionary = {}  ## crop id -> {grow, sell, xp, unlock, yield}
var crop_order: Array = []
var coins := 60
var emeralds := 5
var xp := 0
var level := 1
var inventory: Dictionary = {"wheat": 6}
var barn_capacity := 50
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
	_load_translations()
	var lang := OS.get_locale_language()
	TranslationServer.set_locale(lang if lang in LOCALES else "en")
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--smoke") or a.begins_with("--bench") or a.begins_with("--shot") or a.begins_with("--demo"):
			persist = false
	if persist:
		load_game()


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


func sell(item: String, n := 1) -> int:
	n = mini(n, count(item))
	if n <= 0 or not crops.has(item):
		return 0
	take_item(item, n)
	var earned: int = n * int(crops[item]["sell"])
	add_coins(earned)
	return earned


func is_unlocked(crop: String) -> bool:
	return level >= int(crops[crop]["unlock"])


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
		"inventory": inventory, "extra_fields": extra_fields,
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
