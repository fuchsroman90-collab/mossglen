---
name: mossglen-dev
description: Build, run, test and screenshot the Mossglen Godot project, and work with its CI. Use for any code change in game/, for checking that the game still runs, for performance checks, and before every push.
---

# Mossglen – Godot development

- Godot **4.7.2** standard (not .NET), renderer GL Compatibility.
- Scripts are built in code (no big .tscn files). Autoloads: `Atlas`, `Game`, `Audio`.
- World units = 2x pixels: tile 256 x 128. `world.gd` has `grid_to_world()` / `cell_at()`.
- Ground = one Polygon2D with `shaders/ground.gdshader`: grass + dirt textures in grid space and a
  per-cell dirt mask (`_dirt()`, `_dirt_rect()` in world.gd). Paths, pens and building pads are mask cells.
- Animals: `scripts/animal.gd` (CONFIG per kind: frame counts, fps, speed).
- HUD: `scripts/hud.gd`, authored in 2x units inside a root Control scaled 0.5. Font: Fredoka (OFL).
  All UI art is 2D from `tools/art/ui.py` (SVG -> `game/art/generated/ui/`). Roman wants UI in 2D.
- Data: `game/data/crops.json`. Economy, inventory, level, save: `scripts/autoload/game_state.gd`
  (`user://save.json`, versioned). World layout (fields) is saved via `Game.world_saver`.
- Godot pitfall: a script with `_process` gets processing enabled when it enters the tree, even if
  `set_process(false)` was called before. Disable it in `_ready()` (see field.gd).

## Commands

```bash
godot --headless --path game --import                 # (re)import assets
godot --headless --path game -- --smoke               # self test, exit code 0/1
godot --path game -- --bench                          # stress scene, prints frame times
godot --path game -- --demo                           # fields in mixed growth stages
godot --path game -- --shot=/tmp/shot.png --zoom=0.52 # screenshot after 3 s, then quit
#   extra screenshot switches: --at=x,y (grid centre) --time=0..1 (day phase) --ui=picker|barn|shop|place
#   --settings (open settings). --smoke/--bench/--shot/--demo never read or write the save file.
```

Headless Linux (cloud session) screenshots need a virtual display and software GL:
```bash
xvfb-run -a -s "-screen 0 1600x900x24" godot --path game --rendering-driver opengl3 \
  --resolution 1600x900 -- --shot=/tmp/shot.png
```
Software rendering is slow; FPS numbers from it mean nothing. Real FPS only on devices.

## Before pushing

1. `--smoke` green.
2. A screenshot looked at (Read the PNG) - visual changes must be checked in context.
3. `brain/LOG.md` updated.
4. CI (`.github/workflows/build.yml`) builds Windows EXE + Android APK from the committed
   assets; it does **not** re-render art (Blender is too heavy for CI).
