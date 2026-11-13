extends Node
## Music + pooled sound effects on separate buses.

const SFX := ["click", "pop", "plant", "harvest", "coin", "cluck", "whoosh", "moo", "baa", "oink", "splash",
	"reel", "levelup", "dig", "achieve"]
## music loop -> volume offset in dB (the vale loop is mixed a little hotter)
const TRACKS := {"meadow": 0.0, "night": 0.0, "village": 0.0, "vale": -2.5}
const FADE := 3.0
const AREA_HOLD := 2.5  ## seconds an area must stay before the music changes
const POOL_SIZE := 12

var _music: AudioStreamPlayer
var _music_b: AudioStreamPlayer  ## second player for cross-fades
var _songs: Dictionary = {}
var track := ""
var _want := ""
var _want_t := 0.0
var _pool: Array[AudioStreamPlayer] = []
var _streams: Dictionary = {}
var music_enabled := true
var sfx_enabled := true


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_bus("Music", -9.0)
	_ensure_bus("SFX", -3.0)
	for n in SFX:
		_streams[n] = load("res://audio/generated/sfx_%s.wav" % n)
	for i in POOL_SIZE:
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_pool.append(p)
	_music = AudioStreamPlayer.new()
	_music.bus = "Music"
	add_child(_music)
	_music_b = AudioStreamPlayer.new()
	_music_b.bus = "Music"
	add_child(_music_b)
	for t in TRACKS:
		var song: AudioStreamOggVorbis = load("res://audio/generated/music_%s.ogg" % t)
		song.loop = true
		_songs[t] = song


func play_music(name := "meadow") -> void:
	track = name
	_want = name
	_music.stream = _songs[name]
	_music.volume_db = -30.0
	_music.play()
	create_tween().tween_property(_music, "volume_db", TRACKS[name], 2.5)


## Asks for the loop that fits the current area; switches after it has been wanted for a moment.
func set_area(name: String) -> void:
	if not _songs.has(name) or track == "":
		return
	if name != _want:
		_want = name
		_want_t = Time.get_ticks_msec() / 1000.0
		return
	if name != track and Time.get_ticks_msec() / 1000.0 - _want_t >= AREA_HOLD:
		_crossfade(name)


func _crossfade(name: String) -> void:
	track = name
	var old := _music
	_music = _music_b
	_music_b = old
	_music.stream = _songs[name]
	_music.volume_db = -40.0
	_music.play()
	var tw := create_tween().set_parallel()
	tw.tween_property(_music, "volume_db", TRACKS[name], FADE)
	tw.tween_property(old, "volume_db", -40.0, FADE)
	tw.chain().tween_callback(old.stop)


func set_sfx_enabled(on: bool) -> void:
	sfx_enabled = on
	AudioServer.set_bus_mute(AudioServer.get_bus_index("SFX"), not on)


func set_music_enabled(on: bool) -> void:
	music_enabled = on
	AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"), not on)


## pitch: base pitch scale, jitter: random +- variation so repeats never sound robotic
func play(sfx_name: String, pitch := 1.0, jitter := 0.05, volume_db := 0.0) -> void:
	for p in _pool:
		if not p.playing:
			p.stream = _streams[sfx_name]
			p.pitch_scale = pitch * (1.0 + randf_range(-jitter, jitter))
			p.volume_db = volume_db
			p.play()
			return


func _ensure_bus(bus_name: String, db: float) -> void:
	if AudioServer.get_bus_index(bus_name) != -1:
		return
	AudioServer.add_bus()
	var i := AudioServer.bus_count - 1
	AudioServer.set_bus_name(i, bus_name)
	AudioServer.set_bus_volume_db(i, db)
	AudioServer.set_bus_send(i, "Master")
