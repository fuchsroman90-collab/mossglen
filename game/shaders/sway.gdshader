// Wind sway for plants and trees. Bends the top of a sprite sideways.
// Sprites must have their anchor (ground contact) at the node origin.
shader_type canvas_item;

uniform float strength = 3.0;   // max sideways offset in px at `height`
uniform float speed = 1.3;
uniform float height = 120.0;   // px above the anchor that get the full offset

void vertex() {
	vec2 world = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xy;
	float t = TIME * speed + world.x * 0.013 + world.y * 0.021;
	float w = sin(t) * 0.7 + sin(t * 2.3 + 1.7) * 0.3;
	float k = clamp(-VERTEX.y / height, 0.0, 1.5);
	VERTEX.x += w * strength * k;
}
