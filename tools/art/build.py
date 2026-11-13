"""Build all Mossglen graphics.

    python tools/art/build.py            # render changed 3D assets, pack atlas, ground, UI
    python tools/art/build.py --pack     # skip rendering, only post/pack (no Blender needed)
    python tools/art/build.py barn       # re-render only frames containing "barn"
    python tools/art/build.py --force    # re-render everything (~15 min on 2 cores)

Needs Python 3.13 + `pip install bpy==5.3.0 numpy pillow resvg-py` for rendering.
Packing alone needs only numpy + pillow + resvg-py (2D UI).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "game" / "art" / "generated"
sys.path.insert(0, str(HERE))


def main(argv):
    import ground
    import pack
    import ui

    if "--pack" not in argv:
        import render
        render.main([a for a in argv if a != "--pack"])

    extra = {"shadow_blob": (ground.blob_shadow(), 60, 28), "fx_smoke": (ground.smoke_puff(), 36, 36)}
    pack.build(OUT, extra)

    ground.grass().save(OUT / "ground_grass.png", optimize=True)
    ground.dirt().save(OUT / "ground_dirt.png", optimize=True)
    (OUT / "ui").mkdir(exist_ok=True)
    for name, img in ui.ui_images().items():
        img.save(OUT / "ui" / f"{name}.png", optimize=True)
    print("ground + ui written to", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
