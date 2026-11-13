// Wind sway for plants and trees. Bends the top of a sprite sideways.
// Sprites must have their anchor (ground contact) at the node origin.
shader_type canvas_item;

uniform float strength = 3.0;   // max sideways offset in px at `height`
uniform float speed = 1.3;
uniform float height = 120.0;   // px above the anchor that get the full offset
// seasons: recolour green foliage (trees, bushes) - crops keep foliage = 0
uniform float foliage = 0.0;
uniform float autumn = 0.0;     // 0..1 green -> gold/orange/red, picked per plant
uniform float frost = 0.0;      // 0..1 snow on the lit, upward parts
uniform float bloom = 0.0;      // 0..1 fresh spring green

varying float pick;
varying vec2 local;

void vertex() {
	vec2 world = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xy;
	float t = TIME * speed + world.x * 0.013 + world.y * 0.021;
	float w = sin(t) * 0.7 + sin(t * 2.3 + 1.7) * 0.3;
	float k = clamp(-VERTEX.y / height, 0.0, 1.5);
	pick = fract(sin(dot(world, vec2(12.9898, 78.233))) * 43758.5453);
	local = VERTEX;
	VERTEX.x += w * strength * k;
}

void fragment() {
	vec4 c = COLOR;
	if (foliage > 0.5) {
		float green = clamp((c.g - max(c.r, c.b)) * 5.0, 0.0, 1.0);
		float lum = dot(c.rgb, vec3(0.3, 0.59, 0.11));
		vec3 col = c.rgb;
		// spring: a touch brighter and more yellow-green
		col = mix(col, col * vec3(1.08, 1.06, 0.88), bloom * green);
		// autumn: keep the shading (lum), swap the hue; a few plants stay green
		vec3 hue = pick < 0.35 ? vec3(1.0, 0.62, 0.18) : (pick < 0.62 ? vec3(0.95, 0.38, 0.16)
				: (pick < 0.85 ? vec3(1.0, 0.82, 0.25) : vec3(0.62, 0.78, 0.25)));
		col = mix(col, clamp(hue * lum * 1.9, 0.0, 1.0), autumn * green);
		// winter: muted green with snow on the lit, upward parts, more of it higher on the plant
		float up = smoothstep(0.22, 0.55, lum) * clamp(-local.y / (height * 0.6), 0.35, 1.0);
		vec3 snow = vec3(0.9, 0.95, 1.0) * (0.8 + 0.3 * lum);
		vec3 winter = mix(col * vec3(0.78, 0.88, 0.92), snow, up * 0.9);
		col = mix(col, winter, frost * green);
		c.rgb = col;
	}
	COLOR = c;
}
