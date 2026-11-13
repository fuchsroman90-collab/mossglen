// Lawn with soft dirt patches (paths, pens, building pads) in one draw call.
// Works in grid space: 1 cell = 256 x 128 px diamond in the world.
shader_type canvas_item;

uniform sampler2D grass_tex : repeat_enable, filter_linear_mipmap;
uniform sampler2D dirt_tex : repeat_enable, filter_linear_mipmap;
uniform sampler2D land_tex : filter_linear;    // 1 = own land (or outside the farm), 0 = still locked
uniform sampler2D mask_tex : filter_linear;   // r = dirt, g = water, b = primeval moss per cell
uniform vec2 mask_origin = vec2(-10.0, -10.0);  // grid coord of mask pixel (0, 0)
uniform float mask_size = 64.0;
uniform float tex_cells = 4.0;                  // grid cells covered by one grass texture
uniform vec3 season_tint = vec3(1.0);           // multiplies the lawn colour
uniform float snow = 0.0;                       // 0..1 patchy snow on the lawn

varying vec2 world;

void vertex() {
	world = VERTEX;
}

void fragment() {
	vec2 g = vec2(world.x / 256.0 + world.y / 128.0, world.y / 128.0 - world.x / 256.0);
	vec4 gr = texture(grass_tex, g / tex_cells);
	// large, slow colour variation so the repeat is not visible
	float macro = texture(grass_tex, g / 29.0 + vec2(0.31, 0.77)).a;
	vec3 grass = gr.rgb * mix(0.92, 1.07, macro);
	vec3 dirt = texture(dirt_tex, g / 3.0).rgb;

	float m = texture(mask_tex, (g - mask_origin + 0.5) / mask_size).r;
	float n = texture(grass_tex, g / 2.3 + vec2(0.5)).a - 0.5;
	float e = smoothstep(0.40, 0.56, m + n * 0.28);
	// grass casts a little shade onto the dirt along the border
	float rim = smoothstep(0.0, 0.35, e) * (1.0 - smoothstep(0.35, 0.9, e));
	dirt *= 1.0 - 0.22 * rim;
	grass *= 1.0 - 0.08 * smoothstep(0.0, 0.5, e);
	// primeval vale: deeper, bluer green with soft moss blotches
	float moss = texture(mask_tex, (g - mask_origin + 0.5) / mask_size).b;
	float blotch = smoothstep(0.45, 0.7, texture(grass_tex, g / 5.0 + vec2(0.2, 0.6)).a);
	vec3 vale = grass * vec3(0.7, 0.9, 0.82) + vec3(0.0, 0.03, 0.05);
	vale = mix(vale, vale * vec3(0.82, 1.05, 0.8), blotch);
	grass = mix(grass, vale, smoothstep(0.2, 0.8, moss));
	grass *= season_tint;
	// winter: a soft snow blanket, thinner in hollows where grass tips poke through; paths mostly clear
	float sn = texture(grass_tex, g / 11.0 + vec2(0.71, 0.13)).a * 0.75
			+ texture(grass_tex, g / 3.3 + vec2(0.37, 0.52)).a * 0.25;
	float th = mix(0.75, 0.2, snow);
	float cover = smoothstep(th, th + 0.09, sn) * step(0.001, snow);
	float blades = smoothstep(0.35, 0.8, dot(gr.rgb, vec3(0.2, 0.7, 0.1)) / max(0.01, dot(grass, vec3(0.2, 0.7, 0.1))) - 0.6);
	cover *= 1.0 - 0.55 * blades * (1.0 - smoothstep(th + 0.1, th + 0.3, sn));
	float inner = smoothstep(th + 0.04, th + 0.22, sn);
	vec3 snowcol = mix(vec3(0.83, 0.89, 0.96), vec3(0.97, 0.98, 1.0), inner) * mix(0.96, 1.02, macro);
	grass = mix(grass, snowcol, cover);
	dirt = mix(dirt, snowcol * 0.97, cover * 0.3);
	vec3 col = mix(grass, dirt, e);

	// pond: sandy shore, shallow turquoise rim, deeper blue centre, moving glints
	vec2 mw = texture(mask_tex, (g - mask_origin + 0.5) / mask_size).rg;
	float wv = mw.g + n * 0.22;
	float shore = smoothstep(0.22, 0.4, wv);
	float water = smoothstep(0.42, 0.5, wv);
	float depth = smoothstep(0.55, 0.95, mw.g);
	col = mix(col, dirt * 1.04, shore);
	vec3 shallow = vec3(0.47, 0.83, 0.86);
	vec3 deep = vec3(0.16, 0.6, 0.78);
	vec3 wcol = mix(shallow, deep, depth);
	float ripple = sin(g.x * 9.0 + TIME * 1.3 + sin(g.y * 5.0 + TIME * 0.7) * 1.5)
			* sin(g.y * 11.0 - TIME * 1.1);
	wcol += vec3(0.75, 0.95, 1.0) * smoothstep(0.82, 0.98, ripple) * 0.35 * depth;
	// bright foam line just inside the shore
	float foam = smoothstep(0.42, 0.47, wv) * (1.0 - smoothstep(0.47, 0.56, wv));
	wcol = mix(wcol, vec3(0.92, 0.99, 1.0), foam * 0.7);
	col = mix(col, wcol, water);
	// land that is not yours yet: a little darker and greyer, with a soft edge
	float own = smoothstep(0.25, 0.75, texture(land_tex, (g - mask_origin + 0.5) / mask_size).r);
	float lum = dot(col, vec3(0.3, 0.59, 0.11));
	col = mix(mix(col, vec3(lum), 0.35) * vec3(0.78, 0.8, 0.78), col, own);
	COLOR = vec4(col, 1.0);
}
