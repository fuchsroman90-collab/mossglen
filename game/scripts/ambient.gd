class_name Ambient
extends Node2D
## Life in the air: butterflies fluttering over the farm and thin drifting wisps of mist
## (references hd2_butterflies_visitor and the haze in every hd2_* picture).

const COLORS := [Color("#2F8FF0"), Color("#FF8A2A"), Color("#FFD23F"), Color("#F25C9A"), Color("#2F8FF0")]

var cam: Camera2D
var _flies: Array[Node2D] = []
var _mist: Array[Sprite2D] = []


func setup(camera: Camera2D, butterflies := 12, wisps := 5) -> void:
	cam = camera
	z_index = 70
	for i in butterflies:
		var b := Node2D.new()
		var col: Color = COLORS[i % COLORS.size()]
		for side in [-1.0, 1.0]:
			var wing := Polygon2D.new()
			wing.polygon = PackedVector2Array([Vector2(0, 0), Vector2(side * 16, -14), Vector2(side * 20, -2),
				Vector2(side * 13, 4), Vector2(side * 15, 12), Vector2(side * 4, 9)])
			wing.color = col
			b.add_child(wing)
			var rim := Line2D.new()
			rim.points = wing.polygon
			rim.closed = true
			rim.width = 2.5
			rim.default_color = col.darkened(0.55)
			wing.add_child(rim)
		var body := Line2D.new()
		body.points = PackedVector2Array([Vector2(0, -7), Vector2(0, 9)])
		body.width = 3.5
		body.default_color = Color("#2A1A10")
		b.add_child(body)
		b.set_meta("ph", randf() * TAU)
		b.set_meta("home", Vector2(randf_range(-900, 900), randf_range(-500, 500)))
		b.scale = Vector2(1.9, 1.9) * randf_range(0.8, 1.2)
		add_child(b)
		_flies.append(b)
	var grad := Gradient.new()
	grad.set_color(0, Color(1, 1, 1, 0.5))
	grad.set_color(1, Color(1, 1, 1, 0.0))
	var tex := GradientTexture2D.new()
	tex.gradient = grad
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 256
	tex.height = 256
	for i in wisps:
		var m := Sprite2D.new()
		m.texture = tex
		m.scale = Vector2(randf_range(3.0, 5.0), randf_range(0.7, 1.1))
		m.modulate.a = randf_range(0.35, 0.5)
		m.set_meta("off", Vector2(randf_range(-1400, 1400), randf_range(-700, 700)))
		m.set_meta("v", randf_range(12.0, 26.0))
		add_child(m)
		_mist.append(m)


func set_active(flies: bool, mist: bool) -> void:
	for b in _flies:
		b.visible = flies
	for m in _mist:
		m.visible = mist


func _process(delta: float) -> void:
	if cam == null:
		cam = get_viewport().get_camera_2d()
		if cam == null:
			return
	var t := Time.get_ticks_msec() * 0.001
	var z := 1.0 / maxf(cam.zoom.x, 0.05)
	for b in _flies:
		var ph: float = b.get_meta("ph")
		var home: Vector2 = b.get_meta("home")
		b.position = cam.position + home * z + Vector2(sin(t * 0.7 + ph) * 90.0 + sin(t * 2.3 + ph * 2.0) * 25.0,
				cos(t * 0.9 + ph * 1.3) * 60.0 + sin(t * 3.1 + ph) * 12.0) * z
		var flap := absf(sin(t * 14.0 + ph))
		b.get_child(0).scale.x = 0.25 + 0.75 * flap
		b.get_child(1).scale.x = 0.25 + 0.75 * flap
		b.rotation = sin(t * 0.7 + ph) * 0.4
	for m in _mist:
		var off: Vector2 = m.get_meta("off")
		off.x += float(m.get_meta("v")) * delta
		if off.x > 1700.0:
			off.x = -1700.0
		m.set_meta("off", off)
		m.position = cam.position + off * z
