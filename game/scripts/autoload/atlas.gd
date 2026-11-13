extends Node
## Sprite atlas pages produced by tools/art/build.py (Blender pre-renders).
## Every frame has an anchor (ground contact point); sprites created here are
## offset so the node origin sits on that anchor.

const DIR := "res://art/generated/"

var pages: Array[Texture2D] = []
var _frames: Dictionary = {}
var _cache: Dictionary = {}


func _ready() -> void:
	var f := FileAccess.open(DIR + "atlas.json", FileAccess.READ)
	assert(f != null, "atlas.json missing - run tools/art/build.py")
	var data: Dictionary = JSON.parse_string(f.get_as_text())
	_frames = data["frames"]
	for i in int(data["pages"]):
		pages.append(load(DIR + "atlas_%d.png" % i))


func has(sprite_name: String) -> bool:
	return _frames.has(sprite_name)


func names() -> Array:
	return _frames.keys()


func tex(sprite_name: String) -> AtlasTexture:
	if _cache.has(sprite_name):
		return _cache[sprite_name]
	var d: Array = _frames[sprite_name]
	var t := AtlasTexture.new()
	t.atlas = pages[int(d[0])]
	t.region = Rect2(d[1], d[2], d[3], d[4])
	_cache[sprite_name] = t
	return t


func anchor(sprite_name: String) -> Vector2:
	var d: Array = _frames[sprite_name]
	return Vector2(d[5], d[6])


func size(sprite_name: String) -> Vector2:
	var d: Array = _frames[sprite_name]
	return Vector2(d[3], d[4])


func apply(s: Sprite2D, sprite_name: String) -> void:
	s.texture = tex(sprite_name)
	s.centered = false
	s.offset = -anchor(sprite_name)


func sprite(sprite_name: String) -> Sprite2D:
	var s := Sprite2D.new()
	apply(s, sprite_name)
	return s


## Image of one frame (for pixel-exact tap tests).
func image_of(sprite_name: String) -> Image:
	var d: Array = _frames[sprite_name]
	return pages[int(d[0])].get_image()
