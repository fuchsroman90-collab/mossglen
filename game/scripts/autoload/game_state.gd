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
signal dino_hatched(species: String)
signal quest_changed
signal restored_building(id: String)
signal settings_changed
signal achievements_changed
signal game_event(type: String, id: String)

const I18N_PATH := "res://i18n/strings.txt"
const SAVE_PATH := "user://save.json"
const SAVE_VERSION := 2  ## 2 = M9.5 progression (empty farm); older saves start fresh
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
var dinos: Array = []  ## species data from data/dinos.json
var dino_by_id: Dictionary = {}
var meadow: Array = ["moosaurus", "moosaurus"]  ## dinos living on the farm meadow
var dino_seen: Dictionary = {"moosaurus": true}
var digs: Dictionary = {}  ## dig spot -> unix time when it is full again
var story: Dictionary = {}  ## data/story.json
var quest_index := 0
var quest_progress := 0
var quest_stage := "intro"  ## intro (talk to npc) -> active -> ready (talk to claim) ; "end" after the arc
var restored: Dictionary = {}  ## village building -> true
var museum_fossils := 0
var achievements: Array = []  ## data/achievements.json
var stats: Dictionary = {}  ## "harvest" / "harvest:wheat" / "earn" ... -> total
var ach_claimed: Dictionary = {}  ## achievement id -> tiers already claimed (0..3)
var season_events: Dictionary = {}  ## data/events.json: one festival goal per season
var festival: Dictionary = {}  ## "autumn_2026" -> {"n": progress, "claimed": tiers claimed}
var tutorial_step := 0  ## see tutorial.gd; -1 = finished or skipped (old saves skip it)
const SEASONS := ["spring", "summer", "autumn", "winter"]
const SEASON_BONUS := 0.8  ## crops of the current season grow in 80 % of the time
var season_override := ""
## Player options (accessibility). text: UI scale 1.0 / 1.15 / 1.3
var settings: Dictionary = {"text": 1.0, "reduce_motion": false, "sfx": true}  ## --season=winter for screenshots and tests
const VALLEY_LEVEL := 4
const MEADOW_MAX := 8
const DIG_REGEN := 180.0
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
var inventory: Dictionary = {"wheat": 3, "axe": 1, "shovel": 1}
## Storage: crops go to the silo, everything else (goods, tools, materials) to the barn.
var silo_level := 0
var barn_level := 0
const STORE_BASE := 50
const STORE_STEP := 25
const UPGRADE_ITEMS := {"silo": ["rivet", "plank", "rope"], "barn": ["nail", "hinge", "paint"]}
const LAND_ITEMS := ["stake", "land_map", "tape"]
const TOOLS := ["axe", "saw", "dynamite", "shovel"]
## Random finds while playing: item -> weight
const DROPS := {"axe": 10, "saw": 7, "dynamite": 7, "shovel": 10, "stake": 6, "land_map": 6, "tape": 6,
	"rivet": 5, "plank": 5, "rope": 5, "nail": 5, "hinge": 5, "paint": 5}
var placeables: Dictionary = {}  ## data/placeables.json
var land: Dictionary = {}  ## unlocked parcel id -> true (the start parcels are always open)
var cleared: Dictionary = {}  ## obstacle key "x,y" -> true
var placed: Array = []  ## [{"k": kind, "x": cell x, "y": cell y, "done": unix time the build finishes}]
const TRUCK_TRIP := 45.0  ## seconds for the delivery round trip
var truck_back_at := 0.0  ## unix time the delivery truck returns; 0 = parked
var truck_cargo := 0  ## coins waiting on the returned truck
var truck_xp := 0
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
	story = _json("res://data/story.json")
	dinos = JSON.parse_string(FileAccess.get_file_as_string("res://data/dinos.json"))
	for d in dinos:
		dino_by_id[d["id"]] = d
	achievements = JSON.parse_string(FileAccess.get_file_as_string("res://data/achievements.json"))
	season_events = _json("res://data/events.json")
	placeables = _json("res://data/placeables.json")
	_load_translations()
	var lang := OS.get_locale_language()
	TranslationServer.set_locale(lang if lang in LOCALES else "en")
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--smoke") or a.begins_with("--bench") or a.begins_with("--shot") or a.begins_with("--demo"):
			persist = false
		if a.begins_with("--season="):
			season_override = a.substr(9)
	if not persist:
		tutorial_step = 0 if "--tutorial" in OS.get_cmdline_user_args() else -1
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
	if n > 0:
		_count_stat("earn", n)
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


## Gentle early levels, then a quadratic curve so later levels take a few play sessions (balancing, M9).
func xp_needed() -> int:
	return 10 + level * 6 + int(1.5 * level * level)


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


func in_silo(item: String) -> bool:
	return crops.has(item)


func capacity(silo: bool) -> int:
	return STORE_BASE + STORE_STEP * (silo_level if silo else barn_level)


## Items stored in the silo (true) or the barn (false).
func stored(silo := false) -> int:
	var n := 0
	for k in inventory:
		if in_silo(k) == silo:
			n += int(inventory[k])
	return n


## Free room for an item in its store.
func space(item := "") -> int:
	var silo := in_silo(item)
	return capacity(silo) - stored(silo)


## Adds items; returns how many fit. force ignores the store limit (gifts, rewards).
func add_item(item: String, n: int, force := false) -> int:
	var fit := n if force else mini(n, space(item))
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


## Real calendar seasons (northern hemisphere): Mar-May spring, Jun-Aug summer, Sep-Nov autumn, Dec-Feb winter.
func season() -> String:
	if season_override != "":
		return season_override
	var m: int = Time.get_date_dict_from_system()["month"]
	return SEASONS[((m + 9) % 12) / 3]


func in_season(crop: String) -> bool:
	return crops.get(crop, {}).get("season", "") == season()


func grow_time(crop: String) -> float:
	var g := float(crops[crop]["grow"])
	return g * SEASON_BONUS if in_season(crop) else g


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
	event("catch", "any")
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


# ------------------------------------------------------------------ story

func quest() -> Dictionary:
	var qs: Array = story["quests"]
	return qs[quest_index] if quest_index < qs.size() else {}


func npc_name(id: String) -> String:
	return story["npcs"][id]["de" if TranslationServer.get_locale().begins_with("de") else "en"]


## Game events that can advance the current quest.
func event(type: String, id: String, n := 1) -> void:
	_count_stat(type, n)
	if id != "any":
		_count_stat(type + ":" + id, n)
	_festival_count(type, id, n)
	game_event.emit(type, id)
	var q := quest()
	if q.is_empty() or quest_stage != "active":
		return
	var g: Dictionary = q["goal"]
	if g["type"] != type or (g["id"] != "any" and g["id"] != id):
		return
	quest_progress = mini(quest_progress + n, int(g["n"]))
	if quest_progress >= int(g["n"]):
		quest_stage = "ready"
	quest_changed.emit()
	mark_dirty()


# ------------------------------------------------------------------ storage upgrades, finds, land

func upgrade_need(which: String) -> int:
	return 1 + (silo_level if which == "silo" else barn_level)


func can_upgrade(which: String) -> bool:
	for it in UPGRADE_ITEMS[which]:
		if count(it) < upgrade_need(which):
			return false
	return true


func upgrade_store(which: String) -> bool:
	if not can_upgrade(which):
		return false
	var n := upgrade_need(which)
	for it in UPGRADE_ITEMS[which]:
		take_item(it, n)
	if which == "silo":
		silo_level += 1
	else:
		barn_level += 1
	add_xp(10 * n)
	inventory_changed.emit("", 0)
	mark_dirty()
	return true


## Rolls a random find (tool or material) with the given chance; returns the item id or "".
var finds_enabled := true  ## smoke tests switch random finds off to stay deterministic


func roll_find(chance: float) -> String:
	if not finds_enabled or randf() >= chance:
		return ""
	var total := 0
	for k in DROPS:
		total += int(DROPS[k])
	var r := randi() % total
	for k in DROPS:
		r -= int(DROPS[k])
		if r < 0:
			if add_item(k, 1) > 0:
				return k
			return ""
	return ""


func placed_count(kind: String) -> int:
	var n := 0
	for p in placed:
		if p["k"] == kind:
			n += 1
	return n


## Price of the next field: grows with every field you own.
func next_field_price() -> int:
	var n := placed_count("field")
	return 0 if n < 3 else 10 + (n - 3) * 15 + (n - 3) * (n - 3) * 2


# ------------------------------------------------------------------ seasonal festival

## Key of the running festival, e.g. "autumn_2026" (winter Jan/Feb belongs to the winter that began in December).
func festival_key() -> String:
	var d := Time.get_date_dict_from_system()
	var y: int = d["year"]
	if season() == "winter" and int(d["month"]) <= 2:
		y -= 1
	return "%s_%d" % [season(), y]


func festival_def() -> Dictionary:
	return season_events.get(season(), {})


func festival_state() -> Dictionary:
	var k := festival_key()
	if not festival.has(k):
		festival[k] = {"n": 0, "claimed": 0}
	return festival[k]


func _festival_count(type: String, id: String, n: int) -> void:
	var f := festival_def()
	if f.is_empty() or f["type"] != type or (f["id"] != "any" and f["id"] != id):
		return
	var st := festival_state()
	var before := festival_claimable()
	st["n"] = int(st["n"]) + n
	if festival_claimable() != before:
		achievements_changed.emit()


func festival_reached() -> int:
	var t := 0
	for need in festival_def().get("tiers", []):
		if int(festival_state()["n"]) >= int(need):
			t += 1
	return t


func festival_claimable() -> bool:
	return festival_reached() > int(festival_state()["claimed"])


## Claims the next festival tier; returns [coins, emeralds] (empty if nothing to claim).
func claim_festival() -> Array:
	if not festival_claimable():
		return []
	var st := festival_state()
	var tier := int(st["claimed"])
	var f := festival_def()
	var c := int(f["coins"][tier])
	var g := int(f["gems"][tier])
	st["claimed"] = tier + 1
	if c > 0:
		add_coins(c)
	if g > 0:
		add_emeralds(g)
	add_xp(10 * (tier + 1))
	achievements_changed.emit()
	mark_dirty()
	return [c, g]


# ------------------------------------------------------------------ achievements

func _count_stat(key: String, n: int) -> void:
	var before := _claimable_count()
	stats[key] = int(stats.get(key, 0)) + n
	if _claimable_count() != before:
		achievements_changed.emit()


func stat(key: String) -> int:
	match key:
		"#fish_species":
			return fish_log.size()
		"#dino_species":
			return dino_seen.size()
		"#level":
			return level
	return int(stats.get(key, 0))


## Number of tiers (0..3) the player has reached for an achievement.
func ach_reached(a: Dictionary) -> int:
	var v := stat(a["stat"])
	var t := 0
	for need in a["tiers"]:
		if v >= int(need):
			t += 1
	return t


func ach_claimable(a: Dictionary) -> bool:
	return ach_reached(a) > int(ach_claimed.get(a["id"], 0))


func _claimable_count() -> int:
	var n := 0
	for a in achievements:
		if ach_claimable(a):
			n += 1
	return n


func claimable_achievements() -> int:
	return _claimable_count()


## Claims the next tier; returns the emeralds given (0 if nothing to claim).
func claim_achievement(id: String) -> int:
	for a in achievements:
		if a["id"] != id or not ach_claimable(a):
			continue
		var tier := int(ach_claimed.get(id, 0))
		var gems := int(a["gems"][tier])
		ach_claimed[id] = tier + 1
		add_emeralds(gems)
		add_xp(5 * (tier + 1))
		achievements_changed.emit()
		mark_dirty()
		return gems
	return 0


## Talk to a villager. Returns the lines to show (empty if they have nothing to say right now).
func talk(npc: String) -> Array:
	var q := quest()
	if q.is_empty() or q["npc"] != npc:
		return []
	var de := TranslationServer.get_locale().begins_with("de")
	if quest_stage == "intro":
		quest_stage = "active"
		quest_progress = 0
		var g: Dictionary = q["goal"]
		if g["type"] == "restore" and restored.has(g["id"]):
			quest_progress = 1
			quest_stage = "ready"
		quest_changed.emit()
		mark_dirty()
		return q["intro_de" if de else "intro_en"]
	if quest_stage == "ready":
		var r: Dictionary = q["reward"]
		add_coins(int(r.get("coins", 0)))
		add_emeralds(int(r.get("emeralds", 0)))
		add_xp(int(r.get("xp", 0)))
		quest_index += 1
		quest_stage = "intro" if quest_index < story["quests"].size() else "end"
		quest_progress = 0
		quest_changed.emit()
		mark_dirty()
		return [q["done_de" if de else "done_en"]]
	return []


func restore_def(id: String) -> Dictionary:
	return story["restore"][id]


func can_restore(id: String) -> bool:
	var d := restore_def(id)
	return not restored.has(id) and level >= int(d["unlock"]) and has_all(d["need"]) and coins >= int(d["coins"])


func restore(id: String) -> bool:
	if not can_restore(id):
		return false
	var d := restore_def(id)
	take_all(d["need"])
	spend_coins(int(d["coins"]))
	restored[id] = true
	add_xp(20)
	restored_building.emit(id)
	if id == "cafe":
		ensure_orders()
	event("restore", id)
	mark_dirty()
	return true


func order_slots() -> int:
	return ORDER_SLOTS + (1 if restored.has("cafe") else 0)


## Three goods Pip wants today, paid with +50 %. Same for the whole day.
func market_wishes() -> Array:
	var pool := orderable_items()
	pool.sort()
	var rng := RandomNumberGenerator.new()
	rng.seed = int(Time.get_unix_time_from_system() / 86400.0)
	var out: Array = []
	while out.size() < mini(3, pool.size()):
		var it: String = pool[rng.randi() % pool.size()]
		if not out.has(it):
			out.append(it)
	return out


func sell_market(item: String) -> int:
	if count(item) < 1:
		return 0
	take_item(item, 1)
	var p := int(ceil(price(item) * 1.5))
	add_coins(p)
	return p


func donate_fossil() -> bool:
	if not take_item("fossil"):
		return false
	museum_fossils += 1
	add_xp(5)
	return true


# ------------------------------------------------------------------ dinos

func dig_ready(spot: String) -> bool:
	return Time.get_unix_time_from_system() >= float(digs.get(spot, 0.0))


## Digs a spot. Returns the found item id ("" if the spot is still empty).
func dig(spot: String) -> String:
	if not dig_ready(spot):
		return ""
	digs[spot] = Time.get_unix_time_from_system() + DIG_REGEN
	var r := randf()
	var found := "fossil"
	if r > 0.78:
		# egg: rarer species are harder to find
		var w := {1: 50.0, 2: 24.0, 3: 6.0, 4: 2.0}
		var total := 0.0
		for d in dinos:
			total += w[int(d["rarity"])]
		var x := randf() * total
		for d in dinos:
			x -= w[int(d["rarity"])]
			if x <= 0.0:
				found = "egg_" + str(d["id"])
				break
	elif r > 0.5:
		found = "amber"
	add_item(found, 1, true)
	add_xp(2)
	event("dig", "any")
	mark_dirty()
	return found


func hatch(species: String) -> bool:
	if meadow.size() >= MEADOW_MAX:
		return false
	meadow.append(species)
	dino_seen[species] = true
	_count_stat("hatch", 1)
	dino_hatched.emit(species)
	mark_dirty()
	return true


func dino_name(id: String) -> String:
	var d: Dictionary = dino_by_id[id]
	return d["de"] if TranslationServer.get_locale().begins_with("de") else d["en"]


# ------------------------------------------------------------------ orders

## Items the player can currently make or grow (order candidates). Feeds are excluded.
## True if a building or pen of this kind is built (and finished).
func owns(kind: String) -> bool:
	for p in placed:
		if p["k"] == kind and float(p.get("done", 0.0)) <= 0.0:
			return true
	return false


## Only goods the farm can actually make right now (M9.5: buildings and pens are bought).
func orderable_items() -> Array:
	var out: Array = []
	for c in crop_order:
		if is_unlocked(c):
			out.append(c)
	for k in placeables:
		var d: Dictionary = placeables[k]
		if d.has("animal") and owns(k):
			out.append(animal_defs[d["animal"]]["product"])
	if not meadow.is_empty():
		out.append("primeval_egg")
	for b in buildings:
		if b == "nest" or not owns(b):
			continue
		for r in buildings[b]["recipes"]:
			if level >= int(r["unlock"]) and not str(r["out"]).begins_with("feed_") \
					and not str(r["out"]).begins_with("dino_"):
				out.append(r["out"])
	return out


func make_order() -> Dictionary:
	if tutorial_step >= 0 and stats.get("deliver", 0) == 0 and orders.is_empty():
		return {"need": {"wheat": 2}, "coins": 12, "xp": 3, "wait_until": 0.0}
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
	while orders.size() < order_slots():
		orders.append(make_order())


func order_ready(i: int) -> bool:
	return orders[i]["wait_until"] <= Time.get_unix_time_from_system()


func truck_away() -> bool:
	return truck_back_at > Time.get_unix_time_from_system()


## Hands an order to the delivery truck: it drives off and brings the coins and XP back (M9.5).
func deliver(i: int) -> bool:
	var o: Dictionary = orders[i]
	if truck_away() or not order_ready(i) or not take_all(o["need"]):
		return false
	truck_cargo += int(o["coins"])
	truck_xp += int(o["xp"])
	truck_back_at = Time.get_unix_time_from_system() + TRUCK_TRIP
	event("deliver", "any")
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
	return 6 + 3 * level


func field_price() -> int:
	return next_field_price()


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
		"meadow": meadow, "dino_seen": dino_seen, "digs": digs,
		"quest": {"i": quest_index, "p": quest_progress, "s": quest_stage}, "restored": restored,
		"museum_fossils": museum_fossils,
		"stats": stats, "ach_claimed": ach_claimed, "tutorial": tutorial_step, "festival": festival,
		"silo_level": silo_level, "barn_level": barn_level, "land": land, "cleared": cleared, "placed": placed,
		"truck": {"back": truck_back_at, "cargo": truck_cargo, "xp": truck_xp},
		"locale": TranslationServer.get_locale().substr(0, 2),
		"music": Audio.music_enabled,
		"settings": settings,
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
	var st: Dictionary = parsed.get("settings", {})
	for k in st:
		if settings.has(k):
			settings[k] = st[k]
	Audio.set_sfx_enabled.call_deferred(bool(settings["sfx"]))
	saved_world = parsed.get("world", {})
	fish_log = {}
	for k in parsed.get("fish_log", {}):
		var e: Dictionary = parsed["fish_log"][k]
		fish_log[k] = {"n": int(e["n"]), "best": float(e["best"])}
	rod = int(parsed.get("rod", 0))
	spots = parsed.get("spots", {})
	meadow = parsed.get("meadow", meadow)
	dino_seen = parsed.get("dino_seen", dino_seen)
	digs = parsed.get("digs", {})
	var qd: Dictionary = parsed.get("quest", {})
	quest_index = int(qd.get("i", 0))
	quest_progress = int(qd.get("p", 0))
	quest_stage = str(qd.get("s", "intro"))
	restored = parsed.get("restored", {})
	museum_fossils = int(parsed.get("museum_fossils", 0))
	stats = {}
	for k in parsed.get("stats", {}):
		stats[k] = int(parsed["stats"][k])
	ach_claimed = {}
	for k in parsed.get("ach_claimed", {}):
		ach_claimed[k] = int(parsed["ach_claimed"][k])
	tutorial_step = int(parsed.get("tutorial", 0))
	silo_level = int(parsed.get("silo_level", 0))
	barn_level = int(parsed.get("barn_level", 0))
	land = parsed.get("land", {})
	cleared = parsed.get("cleared", {})
	placed = parsed.get("placed", [])
	var tr_d: Dictionary = parsed.get("truck", {})
	truck_back_at = float(tr_d.get("back", 0.0))
	truck_cargo = int(tr_d.get("cargo", 0))
	truck_xp = int(tr_d.get("xp", 0))
	festival = {}
	for k in parsed.get("festival", {}):
		var fe: Dictionary = parsed["festival"][k]
		festival[k] = {"n": int(fe["n"]), "claimed": int(fe["claimed"])}
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

func set_setting(key: String, value: Variant) -> void:
	settings[key] = value
	if key == "sfx":
		Audio.set_sfx_enabled(bool(value))
	settings_changed.emit()
	mark_dirty()


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
