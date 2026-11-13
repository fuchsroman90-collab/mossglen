"""Render all Mossglen art from code into game/art/generated.

Usage:  python tools/art/build.py

Outputs
  atlas.png / atlas.json   world sprites, packed. json: name -> [x, y, w, h, anchor_x, anchor_y]
  ground.png / ground.json ground tiles in a fixed grid for the TileSet
  ui_*.png                 UI textures used standalone (9-slice panels, buttons, icons)
  ../../icon.png           app icon
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

from PIL import Image
import resvg_py

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import assets_ground as G  # noqa: E402
import assets_world as W  # noqa: E402
import assets_ui as U  # noqa: E402
import palette as P  # noqa: E402

OUT = HERE.parent.parent / "game" / "art" / "generated"
PAD = 2

SPRITES = {
    "field": G.field,
    **{f"wheat_{i}": (lambda i=i: W.wheat(i)) for i in range(4)},
    "tree_oak": lambda: W.tree_oak(0),
    "tree_apple": lambda: W.tree_oak(1),
    "tree_pine": W.tree_pine,
    "bush": lambda: W.bush(False),
    "bush_berry": lambda: W.bush(True),
    "rock": W.rock,
    "barn": W.barn,
    "chicken_0": lambda: W.chicken(0),
    "chicken_1": lambda: W.chicken(1),
    "fence_x": lambda: W.fence("x"),
    "fence_y": lambda: W.fence("y"),
    "fx_sparkle": U.sparkle,
    "fx_leaf": U.leaf_particle,
    "fx_grain": U.grain_particle,
    "icon_coin": U.coin,
    "icon_emerald": U.emerald,
}

UI = {
    "ui_panel": U.panel,
    "ui_button_green": lambda: U.button(P.leaf, P.leaf_dark, P.leaf_light),
    "ui_button_cream": lambda: U.button(P.cream_dark, P.wood, P.cream),
    "ui_coin": U.coin,
    "ui_emerald": U.emerald,
}


def render(canvas) -> Image.Image:
    png = resvg_py.svg_to_bytes(svg_string=canvas.svg())
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")


def crop(img: Image.Image, ax: float, ay: float):
    bbox = img.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("empty sprite")
    x0, y0, x1, y1 = bbox
    x0, y0 = max(0, x0 - 1), max(0, y0 - 1)
    x1, y1 = min(img.width, x1 + 1), min(img.height, y1 + 1)
    edge = (x0 == 0 or y0 == 0 or x1 == img.width or y1 == img.height)
    return img.crop((x0, y0, x1, y1)), ax - x0, ay - y0, edge


def pack(items: dict[str, Image.Image], width: int = 1024):
    """Shelf packer, tallest first. Grows height to the next power of two."""
    order = sorted(items, key=lambda n: (-items[n].height, n))
    x = y = shelf = 0
    pos = {}
    for n in order:
        im = items[n]
        if x + im.width + PAD > width:
            x, y, shelf = 0, y + shelf + PAD, 0
        pos[n] = (x + PAD, y + PAD)
        x += im.width + PAD
        shelf = max(shelf, im.height)
    h = 1
    while h < y + shelf + PAD * 2:
        h *= 2
    atlas = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    for n, (px, py) in pos.items():
        atlas.paste(items[n], (px, py))
    return atlas, pos


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- world atlas
    imgs, anchors = {}, {}
    for name, fn in SPRITES.items():
        cv = fn()
        im, ax, ay, edge = crop(render(cv), cv.ax, cv.ay)
        if edge:
            print(f"WARNING: {name} touches the canvas border, enlarge its canvas")
        imgs[name], anchors[name] = im, (ax, ay)
    width = 1024
    while True:
        atlas, pos = pack(imgs, width)
        if atlas.height <= width * 2:
            break
        width *= 2
    atlas.save(OUT / "atlas.png", optimize=True)
    data = {n: [pos[n][0], pos[n][1], imgs[n].width, imgs[n].height,
                round(anchors[n][0], 2), round(anchors[n][1], 2)] for n in sorted(imgs)}
    (OUT / "atlas.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"atlas {atlas.width}x{atlas.height}, {len(imgs)} sprites")

    # ---- ground grid
    tiles = G.GROUND_TILES
    cw, ch = G.CELL_W, G.CELL_H
    ground = Image.new("RGBA", (cw * len(tiles), ch), (0, 0, 0, 0))
    for i, (name, fn) in enumerate(tiles):
        ground.paste(render(fn()), (i * cw, 0))
    ground.save(OUT / "ground.png", optimize=True)
    (OUT / "ground.json").write_text(json.dumps(
        {"cell": [cw, ch], "tiles": [n for n, _ in tiles]}, indent=1), encoding="utf-8")
    print(f"ground {ground.width}x{ground.height}, {len(tiles)} tiles")

    # ---- standalone UI textures
    for name, fn in UI.items():
        render(fn()).save(OUT / f"{name}.png", optimize=True)
    print(f"ui {len(UI)} textures")

    # ---- app icon: barn on a grass disc
    icon = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    bg = render(_icon_bg())
    icon.alpha_composite(bg)
    barn, bax, bay, _ = crop(render(W.barn()), W.barn().ax, W.barn().ay)
    barn = barn.resize((int(barn.width * 1.0), int(barn.height * 1.0)), Image.LANCZOS)
    icon.alpha_composite(barn, (int(256 - bax), int(400 - bay)))
    icon.save(OUT.parent.parent / "icon.png", optimize=True)
    print("icon 512x512")


def _icon_bg():
    from svgkit import Canvas
    c = Canvas(512, 512, 0, 0)
    c.rect(0, 0, 512, 512, 110, c.linear([(0, P.sky), (0.62, "#D9F0E8"), (0.62, P.grass), (1, P.grass_dark)], 0, 0, 0, 512), stroke=None)
    return c


if __name__ == "__main__":
    main()
