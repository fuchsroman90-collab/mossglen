extends Node
## Sprite atlas produced by tools/art/build.py.
## Every sprite has an anchor (ground contact point); sprites created here
## are offset so the node origin sits on that anchor.

const TEX_PATH := "res://art/generated/atlas.png"
const DATA_PATH := "res://art/generated/atlas.json"

var texture: Texture2D
var _frames: Dictionary = {}
var _cache: Dictionary = {}


func _ready() -> void:
	texture = load(TEX_PATH)
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	assert(f != null, "atlas.json missing - run tools/art/build.py")
	_frames = JSON.parse_string(f.get_as_text())


func has(sprite_name: String) -> bool:
	return _frames.has(sprite_name)


func names() -> Array:
	return _frames.keys()


func tex(sprite_name: String) -> AtlasTexture:
	if _cache.has(sprite_name):
		return _cache[sprite_name]
	var d: Array = _frames[sprite_name]
	var t := AtlasTexture.new()
	t.atlas = texture
	t.region = Rect2(d[0], d[1], d[2], d[3])
	_cache[sprite_name] = t
	return t


func anchor(sprite_name: String) -> Vector2:
	var d: Array = _frames[sprite_name]
	return Vector2(d[4], d[5])


func apply(s: Sprite2D, sprite_name: String) -> void:
	s.texture = tex(sprite_name)
	s.centered = false
	s.offset = -anchor(sprite_name)


func sprite(sprite_name: String) -> Sprite2D:
	var s := Sprite2D.new()
	apply(s, sprite_name)
	return s
