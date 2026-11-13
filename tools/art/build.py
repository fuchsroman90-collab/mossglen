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


ICON_BOX = 112  # px, square; same size as the old 2D icons, which the HUD layout expects


def export_item_icons() -> int:
    """3D-rendered item icons (frames "uiitem_<id>") -> ui/item_<id>.png, outlined and centred in a square."""
    import json

    import numpy as np
    from PIL import Image

    import post
    cache = HERE / ".cache"
    meta = json.loads((cache / "meta.json").read_text())
    n = 0
    for name in sorted(meta):
        if not name.startswith("uiitem_"):
            continue
        img = post.composite(cache / f"{name}.png", None, outline_px=3.0)
        img, _, _ = post.trim(img, 0, 0, pad=2)
        pil = post.to_pil(img)
        k = (ICON_BOX - 8) / max(pil.size)
        pil = pil.resize((max(1, round(pil.size[0] * k)), max(1, round(pil.size[1] * k))), Image.LANCZOS)
        out = Image.new("RGBA", (ICON_BOX, ICON_BOX), (0, 0, 0, 0))
        out.alpha_composite(pil, ((ICON_BOX - pil.size[0]) // 2, (ICON_BOX - pil.size[1]) // 2))
        out.save(OUT / "ui" / f"item_{name[7:]}.png", optimize=True)
        n += 1
    return n


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
    for name, img in ui.ui_images_all().items():
        img.save(OUT / "ui" / f"{name}.png", optimize=True)
    print("3D item icons:", export_item_icons())
    print("ground + ui written to", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
