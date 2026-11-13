extends Node
## Player economy + language. Local only for now (cloud save comes in M6).

signal coins_changed(value: int)
signal emeralds_changed(value: int)
signal xp_changed(xp: int, needed: int, level: int)

const I18N_PATH := "res://i18n/strings.txt"
const LOCALES := ["de", "en"]

var coins := 50
var emeralds := 5
var xp := 0
var level := 1
var font_bold: FontVariation
var font_regular: FontVariation


func _ready() -> void:
	font_bold = _font(600)
	font_regular = _font(500)
	_load_translations()
	var lang := OS.get_locale_language()
	TranslationServer.set_locale(lang if lang in LOCALES else "en")


func add_coins(n: int) -> void:
	coins += n
	coins_changed.emit(coins)


func xp_needed() -> int:
	return 8 + level * 6


func add_xp(n: int) -> void:
	xp += n
	while xp >= xp_needed():
		xp -= xp_needed()
		level += 1
	xp_changed.emit(xp, xp_needed(), level)


func _font(weight: int) -> FontVariation:
	var f := FontVariation.new()
	f.base_font = load("res://fonts/Fredoka.ttf")
	var ts := TextServerManager.get_primary_interface()
	f.variation_opentype = {ts.name_to_tag("wght"): weight}
	return f


func add_emeralds(n: int) -> void:
	emeralds += n
	emeralds_changed.emit(emeralds)


func toggle_language() -> void:
	var cur := TranslationServer.get_locale().substr(0, 2)
	TranslationServer.set_locale("en" if cur == "de" else "de")


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
