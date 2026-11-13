extends Node
## Sprite atlas pages produced by tools/art/build.py (Blender pre-renders).
## Every frame has an anchor (ground contact point); sprites created here are
## offset so the node origin sits on that anchor.

const DIR := "res://art/generated/"

const MASK_SCALE := 4  ## tap masks are 1/4 size (tools/art/pack.py)

var pages: Array[Texture2D] = []
var masks: Array[Image] = []  ## alpha > 0.5 per page, CPU side, for pixel-exact taps
var _frames: Dictionary = {}
var _cache: Dictionary = {}


func _ready() -> void:
	var f := FileAccess.open(DIR + "atlas.json", FileAccess.READ)
	assert(f != null, "atlas.json missing - run tools/art/build.py")
	var data: Dictionary = JSON.parse_string(f.get_as_text())
	_frames = data["frames"]
	for i in int(data["pages"]):
		pages.append(load(DIR + "atlas_%d.png" % i))
		masks.append(load(DIR + "atlas_%d_mask.png" % i))


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


## True if the frame is opaque at a pixel given relative to the frame's top-left corner.
func opaque(sprite_name: String, local: Vector2) -> bool:
	var d: Array = _frames[sprite_name]
	if local.x < 0 or local.y < 0 or local.x >= float(d[3]) or local.y >= float(d[4]):
		return false
	var m: Image = masks[int(d[0])]
	var p := Vector2i((Vector2(d[1], d[2]) + local) / MASK_SCALE)
	if p.x >= m.get_width() or p.y >= m.get_height():
		return false
	return m.get_pixelv(p).r > 0.5


## Same test for any AtlasTexture cut from a page (local = pixel inside its region).
func opaque_region(at: AtlasTexture, local: Vector2) -> bool:
	var i := pages.find(at.atlas)
	if i < 0 or not Rect2(Vector2.ZERO, at.region.size).has_point(local):
		return i < 0
	var m: Image = masks[i]
	var p := Vector2i((at.region.position + local) / MASK_SCALE)
	return p.x < m.get_width() and p.y < m.get_height() and m.get_pixelv(p).r > 0.5
