"""Post-process cached renders and pack them into atlas pages for Godot.

Output (game/art/generated/):
    atlas_<n>.png
    atlas.json   name -> [page, x, y, w, h, anchor_x, anchor_y]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import post  # noqa: E402

PAGE = 2048
GAP = 2


class Shelf:
    """Simple shelf packer, items sorted by height."""

    def __init__(self, size):
        self.size = size
        self.pages = [[]]  # list of shelves per page: [y, h, x]

    def place(self, w, h):
        for pi, shelves in enumerate(self.pages):
            for s in shelves:
                if h <= s[1] and s[2] + w <= self.size:
                    x = s[2]
                    s[2] += w + GAP
                    return pi, x, s[0]
            y = shelves[-1][0] + shelves[-1][1] + GAP if shelves else 0
            if y + h <= self.size:
                shelves.append([y, h, w + GAP])
                return pi, 0, y
        self.pages.append([[0, h, w + GAP]])
        return len(self.pages) - 1, 0, 0


MASK_SCALE = 4
# Atlas pages are VRAM compressed (BPTC on desktop, ASTC on phones) with mipmaps: ~4x less GPU memory.
ATLAS_IMPORT = ('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n\n[params]\n\n'
                'compress/mode=2\ncompress/high_quality=true\nmipmaps/generate=true\n'
                'process/fix_alpha_border=true\ndetect_3d/compress_to=0\n')
# Tap masks are loaded as plain Images (CPU side) for pixel-exact taps.
MASK_IMPORT = '[remap]\n\nimporter="image"\ntype="Image"\n'


def write_mask(page: np.ndarray, path: Path) -> None:
    """Alpha of an atlas page at 1/MASK_SCALE, max-pooled so thin parts stay tappable."""
    a = page[..., 3]
    h, w = a.shape
    a = a[:h - h % MASK_SCALE, :w - w % MASK_SCALE]
    m = a.reshape(h // MASK_SCALE, MASK_SCALE, w // MASK_SCALE, MASK_SCALE).max(axis=(1, 3))
    Image.fromarray((m > 0.5).astype(np.uint8) * 255, "L").save(path, optimize=True)


def ensure_import(png: Path, text: str) -> None:
    imp = png.with_name(png.name + ".import")
    if imp.exists():
        cur = imp.read_text()
        want_importer = text.split("importer=")[1].split("\n")[0]
        if f"importer={want_importer}" in cur and ("compress/mode=2" in cur or "image" in want_importer):
            return
    imp.write_text(text)


def build(out_dir: Path, extra: dict | None = None) -> dict:
    """extra: name -> (image float RGBA, ax, ay) for non-Blender sprites."""
    cache = HERE / ".cache"
    meta = json.loads((cache / "meta.json").read_text())
    sprites = {}
    for name, m in sorted(meta.items()):
        obj = cache / f"{name}.png"
        sh = cache / f"{name}_shadow.png" if m["shadow"] else None
        px = 2.5 if name.startswith("icon_") else post.OUTLINE_PX
        img = post.composite(obj, sh, outline_px=px)
        img, ax, ay = post.trim(img, m["ax"], m["ay"])
        sprites[name] = (img, ax, ay)
    if extra:
        sprites.update(extra)

    order = sorted(sprites, key=lambda n: -sprites[n][0].shape[0])
    packer = Shelf(PAGE)
    placed = {}
    for name in order:
        img = sprites[name][0]
        h, w = img.shape[:2]
        placed[name] = packer.place(w, h)
    pages = [np.zeros((PAGE, PAGE, 4), np.float32) for _ in packer.pages]
    data = {}
    for name, (pi, x, y) in placed.items():
        img, ax, ay = sprites[name]
        h, w = img.shape[:2]
        pages[pi][y:y + h, x:x + w] = img
        data[name] = [pi, x, y, w, h, int(ax), int(ay)]
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("atlas_*.png"):
        old.unlink()
    for i, p in enumerate(pages):
        used = max((y + sprites[n][0].shape[0] for n, (pi, x, y) in placed.items() if pi == i), default=1)
        hh = 1 << (int(used) - 1).bit_length()  # power-of-two height, trims empty space
        page = p[:min(PAGE, hh)]
        post.to_pil(page).save(out_dir / f"atlas_{i}.png", optimize=True)
        write_mask(page, out_dir / f"atlas_{i}_mask.png")
        ensure_import(out_dir / f"atlas_{i}.png", ATLAS_IMPORT)
        ensure_import(out_dir / f"atlas_{i}_mask.png", MASK_IMPORT)
    (out_dir / "atlas.json").write_text(json.dumps({"pages": len(pages), "frames": data}, indent=0, sort_keys=True))
    print(f"pack: {len(data)} sprites on {len(pages)} page(s)")
    return data
