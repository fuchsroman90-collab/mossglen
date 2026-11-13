class_name Weather
extends CanvasLayer
## Screen-space seasonal particles: spring petals, summer fireflies (night only),
## autumn leaves, winter snow. Sits between the world and the HUD and is not
## darkened by the day/night CanvasModulate, so it is dimmed by hand at night.

const UI := "res://art/generated/ui/"

var season := ""
var _fall: CPUParticles2D
var _flies: CPUParticles2D
var _night := false


func setup(s: String) -> void:
	layer = 1
	season = s
	match s:
		"spring":
			_fall = _faller("fx_petal", 16, 18.0, Vector2(0.45, 0.8))
			_fall.color = Color(1, 1, 1, 0.95)
		"autumn":
			_fall = _faller("fx_fall_leaf", 12, 16.0, Vector2(0.55, 0.95))
			var g := Gradient.new()
			g.offsets = PackedFloat32Array([0.0, 0.35, 0.36, 0.7, 0.71, 1.0])
			g.colors = PackedColorArray([Color("F59A3A"), Color("F59A3A"), Color("E2502E"), Color("E2502E"),
				Color("F7C64A"), Color("F7C64A")])
			_fall.color_initial_ramp = g
		"winter":
			_fall = _faller("fx_snow", 70, 14.0, Vector2(0.3, 0.75))
			_fall.angular_velocity_min = 0.0
			_fall.angular_velocity_max = 0.0
			_fall.initial_velocity_min = 35.0
			_fall.initial_velocity_max = 70.0
	if s == "summer":
		_flies = CPUParticles2D.new()
		_flies.texture = load(UI + "fx_firefly.png")
		_flies.amount = 18
		_flies.lifetime = 7.0
		_flies.preprocess = 7.0
		_flies.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		_flies.direction = Vector2(0, -1)
		_flies.spread = 180.0
		_flies.gravity = Vector2.ZERO
		_flies.initial_velocity_min = 6.0
		_flies.initial_velocity_max = 22.0
		_flies.scale_amount_min = 0.5
		_flies.scale_amount_max = 0.9
		var a := Gradient.new()
		a.offsets = PackedFloat32Array([0.0, 0.2, 0.4, 0.55, 0.75, 1.0])
		a.colors = PackedColorArray([Color(1, 1, 1, 0), Color(1, 1, 1, 1), Color(1, 1, 1, 0.3), Color(1, 1, 1, 1),
			Color(1, 1, 1, 0.6), Color(1, 1, 1, 0)])
		_flies.color_ramp = a
		_flies.emitting = false
		_flies.visible = false
		add_child(_flies)
	get_viewport().size_changed.connect(_fit)
	_fit()


func _faller(tex: String, amount: int, life: float, scale_range: Vector2) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.texture = load(UI + tex + ".png")
	p.amount = amount
	p.lifetime = life
	p.preprocess = life
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.direction = Vector2(0.35, 1.0)
	p.spread = 20.0
	p.gravity = Vector2(6, 12)
	p.initial_velocity_min = 45.0
	p.initial_velocity_max = 80.0
	p.angular_velocity_min = -90.0
	p.angular_velocity_max = 90.0
	p.angle_min = 0.0
	p.angle_max = 360.0
	p.tangential_accel_min = -12.0
	p.tangential_accel_max = 12.0
	p.scale_amount_min = scale_range.x
	p.scale_amount_max = scale_range.y
	add_child(p)
	return p


func _fit() -> void:
	var size := get_viewport().get_visible_rect().size
	if _fall:
		# emit from a band above the screen that is wider than it, to cover the sideways drift
		_fall.position = Vector2(size.x * 0.4, -40)
		_fall.emission_rect_extents = Vector2(size.x * 0.75, 30)
	if _flies:
		_flies.position = size * 0.5
		_flies.emission_rect_extents = size * 0.5


## Called by the world with the day phase brightness (1 = noon, ~0.6 = night).
func set_light(c: Color, night: bool) -> void:
	if _fall:
		_fall.modulate = Color(c.r, c.g, c.b, 1.0)
	if _flies and night != _night:
		_night = night
		_flies.visible = night
		_flies.emitting = night


func set_motion(on: bool) -> void:
	visible = on
	if _fall:
		_fall.emitting = on
