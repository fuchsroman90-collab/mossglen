# Mossglen

A cozy 2.5D farm valley game for Windows, Android and iOS, built with Godot 4.
All graphics are 3D models built in code with Blender and pre-rendered to sprites;
music and sound are generated from code too.

- Plan and status: [brain/GOAL.md](brain/GOAL.md)
- Art rules: [docs/STYLE_BIBLE.md](docs/STYLE_BIBLE.md)
- Working notes for Claude Code: [CLAUDE.md](CLAUDE.md) and `brain/`

## Layout

| Folder | Content |
|---|---|
| `game/` | Godot project (scripts, shaders, generated assets, fonts) |
| `tools/art/` | Blender models (`blender/`), render cache, post-processing, atlas packing |
| `tools/audio/` | Music composition and sound synthesis |
| `brain/` | Goal/plan, log, decisions, taste notes, reference analysis |
| `.claude/skills/` | Project skills for Claude Code |
| `docs/` | Style bible, licenses |

## Requirements

- Godot 4.7.2 (standard, not .NET)
- Art: Python 3.13 with `bpy==5.3.0 numpy pillow` (`pip install bpy` = Blender as a module)
- Audio: Python with `numpy scipy`

## Commands

```bash
python tools/art/build.py          # render changed 3D assets, pack atlas, ground, UI
python tools/art/build.py --pack   # only re-pack (no Blender)
python tools/audio/build.py        # rebuild music and sounds
godot --headless --path game --import
godot --path game                  # play
godot --headless --path game -- --smoke   # self test, exit code 0/1
godot --path game -- --bench       # stress scene, prints frame times
godot --path game -- --demo        # fields start in mixed growth stages
```

## Controls

- Tap/click an empty field to sow, swipe across fields to sow many.
- Swipe across ripe wheat to harvest.
- Drag to move the camera, mouse wheel or pinch to zoom.
- Tap animals, trees and the barn.

## License

Code and assets: all rights reserved. See [LICENSE](LICENSE).
Font Fredoka: SIL Open Font License (`game/fonts/OFL.txt`). See [docs/LICENSES.md](docs/LICENSES.md).
