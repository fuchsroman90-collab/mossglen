---
name: mossglen-art
description: Mossglen graphics pipeline. Use for ANY art task in this repo - new or changed sprites, animals, buildings, plants, icons, UI pieces, ground textures - and whenever Roman comments on how something looks. Covers the Blender pre-render pipeline (bpy), the style rules, and the review loop.
---

# Mossglen Art Pipeline (Blender pre-rendered 3D -> 2D sprites)

Before you start: read `brain/taste/LIKES.md`, `brain/taste/DISLIKES.md`,
`brain/references/REFERENCES.md` and `docs/STYLE_BIBLE.md`.

## How it works

```
tools/art/blender/kit.py          camera, light, materials, shapes, fit+render
tools/art/blender/assets/*.py     one function per model, *_frames() registries
tools/art/render.py               renders changed frames into tools/art/.cache (hash cache)
tools/art/post.py                 shadow tint, darkened-colour outline, trim
tools/art/pack.py                 atlas_<n>.png + atlas.json (page,x,y,w,h,ax,ay)
tools/art/ground.py, ui.py        numpy: seamless grass/dirt, blob shadow, glossy UI 9-slices
tools/art/build.py                runs everything -> game/art/generated/
```

Setup: Python 3.13, `pip install bpy==5.3.0 numpy pillow` (bpy is Blender as a module, no GUI).

Commands:
```bash
python tools/art/build.py              # render what changed + pack (full run ~10 min on 2 cores)
python tools/art/build.py chicken      # only frames whose name contains "chicken"
python tools/art/build.py --pack       # no Blender, only post + pack
python tools/art/build.py --force      # re-render everything
```

## Fixed conventions (do not change without updating the game code)

- 1 grid tile = 1 m. Grid x -> world +X, grid y -> world -Y.
- Ortho camera rot (60°, 0, 45°): dimetric 2:1. **2x resolution: tile diamond 256 x 128 px.**
- Anchor = projection of world origin = ground contact point. Model everything around (0,0,0).
- Models face local +X. yaw 0 = screen down-right ("se"), yaw 90 = up-right ("ne").
  Godot mirrors these for sw/nw.
- Animation frames: `<kind>_<anim>_<facing>_<i>` (see `game/scripts/animal.gd` CONFIG).
- Static props get a baked soft shadow (shadow-catcher pass). Animals get no baked shadow;
  the game puts `shadow_blob` under them.
- Light from upper-left-front (`kit.LIGHT_DIR`), sky fill + green bounce from the world shader,
  Cycles 40-64 spp + OpenImageDenoise, view transform "Standard" (saturated).

## Building good-looking models (lessons learned)

- **Organic bodies**: metaballs via `kit.blob()`. Use `kit.chain()` for necks, tails, legs:
  a sparse row of balls looks like a bead string (rejected look). Separate blob() calls never
  merge, so use separate blobs for parts that must stay distinct (wings, legs).
- **Place details on the real surface**: convert with `kit.to_mesh()`, then `kit.Surface([...])`
  and `.toward(center, direction)` to raycast. Never guess positions on metaball surfaces:
  spots and eyes float otherwise.
- **Eyes**: `animals.eye()`, embedded ~60 % into the head, pupils look at the camera, emissive glint.
- **Foliage**: `nature.leaf_clump()` + `foliage_mat()`. Leaf look comes from voronoi BUMP
  (shading), not from colour spots (colour spots looked like polka dots, rejected).
- **Pines**: star-shaped drooping tiers (`star_tier`), not smooth cones (looked like a skirt).
- **Buildings**: build from many small bevelled parts (planks, shingles, stones) with `var=`
  colour jitter. Add props (hay, barrels, flower boxes). Ground pads are painted by the game's
  ground shader (dirt mask), not part of the sprite.
- Materials: `kit.mat(..., edge=, edge_color=)` darkens towards the silhouette; post.py adds a
  2 px outline in the darkened edge colour. Never pure black outlines.

- **Moving parts as separate camera-facing sprites**: mill sails are modelled in a plane facing
  `kit.TO_CAM` and rotated in Godot (2D rotation is then exact). Offset = (hub·R·PPM, -hub·U·PPM).
- Round windows in pairs on a cylinder read as a face. Avoid two symmetric round openings.
- Use `kit.Surface` + `place_on` for spots on animals; keep them thin (scale z ≈ 0.12) or they bulge.

## Review loop (mandatory)

1. Render the changed frames (test sheet: compose them on grass colour, look at them with Read).
2. Compare against `brain/references/` (same quality level?) and the taste files.
3. Fix and re-render until it does not fall behind the references. Then run the game screenshot
   (see mossglen-dev skill) and check it in context.
4. Write what you learned into this skill and `brain/LOG.md`; Roman's reactions into `brain/taste/`.

## Atlas import (M9)

`pack.py` writes `atlas_N.png` + `atlas_N_mask.png` and their `.import` files: pages are VRAM compressed
(`compress/mode=2`, high quality = BPTC/ASTC) with mipmaps; masks are imported as `Image` and used for
pixel-exact taps (`Atlas.opaque_region`). Never read pixels from the atlas textures themselves.
Seasonal looks are shader-only (`ground.gdshader` season_tint/snow, `sway.gdshader` foliage/autumn/frost/bloom):
new trees/bushes get them for free if their leaves are green and they use the tree/bush sway material.

## Item icons are 3D (Roman, 2026-11-13)

Item icons (crops, goods, tools, materials, eggs) are Blender renders, never flat SVG: add a model to
`assets/items.py` (`item_frames`, name `uiitem_<id>`), keep it simple and chunky, put labels on `_front(root)`
so they face the camera, lean flat things with `_lean`. `build.py` exports them to `ui/item_<id>.png`.
Reference: `brain/references/img/hd_item_icons_3d.png`. HUD frames, buttons and glyphs stay 2D (`ui.py`).
