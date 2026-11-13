# Mossglen

A cozy 2.5D farm valley game for Windows, Android and iOS, built with Godot 4.
All graphics, music and sound are generated from code in `tools/`.

See [PLAN.md](PLAN.md) for the roadmap and [docs/STYLE_BIBLE.md](docs/STYLE_BIBLE.md) for the art rules.

## Layout

| Folder | Content |
|---|---|
| `game/` | Godot project (scripts, shaders, generated assets) |
| `tools/art/` | SVG asset code → `game/art/generated/` (atlas + ground tiles + UI) |
| `tools/audio/` | Music composition and sound synthesis → `game/audio/generated/` |
| `docs/` | Style bible, licenses |
| `.github/workflows/` | CI: regenerate assets, smoke test, Windows + Android builds |

## Requirements

- Godot 4.7.2 (standard, not .NET)
- Python 3.12 with `numpy scipy pillow resvg-py`

## Commands

```bash
python tools/art/build.py          # rebuild all graphics
python tools/audio/build.py        # rebuild music and sounds (~1 min)
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
- Tap chickens, trees and the barn.

## License

All rights reserved. See [LICENSE](LICENSE).
