extends Node
## Music + pooled sound effects on separate buses.

const SFX := ["click", "pop", "plant", "harvest", "coin", "cluck", "whoosh", "moo", "baa", "oink", "splash",
	"reel", "levelup", "dig"]
const POOL_SIZE := 12

var _music: AudioStreamPlayer
var _pool: Array[AudioStreamPlayer] = []
var _streams: Dictionary = {}
var music_enabled := true


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
	var song: AudioStreamWAV = load("res://audio/generated/music_meadow.wav")
	song.loop_mode = AudioStreamWAV.LOOP_FORWARD
	song.loop_begin = 0
	song.loop_end = int(song.get_length() * song.mix_rate)
	_music.stream = song


func play_music() -> void:
	_music.volume_db = -30.0
	_music.play()
	create_tween().tween_property(_music, "volume_db", 0.0, 2.5)


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
