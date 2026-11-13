"""Flat 2D UI (HUD, buttons, icons) drawn as SVG from code and rasterised with resvg.

Style (Roman, 13.11.2026: "UI in 2D, closer to the references"):
bold flat shapes, strong vertical gradients, white rims, thick warm-dark outline,
a soft gloss highlight on top and a small drop shadow. Rendered at 2x.
"""
from __future__ import annotations

import io
import math

import numpy as np
import resvg_py
from PIL import Image

OUT = "#5A3410"       # warm dark outline for yellow/gold pieces
OUT_BLUE = "#173F78"
OUT_GREEN = "#0D4F33"


def render(svg: str, w: int, h: int) -> Image.Image:
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
           f'{svg}</svg>')
    data = resvg_py.svg_to_bytes(svg_string=doc)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")


def grad(gid, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def shadow_filter(fid="sh", dy=5, blur=3, op=0.35):
    return (f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="150%">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{blur}"/><feOffset dy="{dy}"/>'
            f'<feComponentTransfer><feFuncA type="linear" slope="{op}"/></feComponentTransfer>'
            f'<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


# ---------------------------------------------------------------- pieces

def round_button(size=128, top="#FFE56B", bottom="#F39C12", rim_top="#FFFFFF", rim_bot="#F4E3B4"):
    c = size / 2
    r = size / 2 - 6
    defs = (grad("rim", [(0, rim_top), (1, rim_bot)]) + grad("face", [(0, top), (1, bottom)])
            + shadow_filter())
    body = (f'<g filter="url(#sh)">'
            f'<circle cx="{c}" cy="{c}" r="{r}" fill="{OUT}"/>'
            f'<circle cx="{c}" cy="{c}" r="{r - 4}" fill="url(#rim)"/>'
            f'<circle cx="{c}" cy="{c}" r="{r - 11}" fill="url(#face)" stroke="#C9780E" stroke-width="2.5"/>'
            f'<ellipse cx="{c}" cy="{c - r * 0.42}" rx="{r * 0.58}" ry="{r * 0.26}" fill="#FFFFFF" opacity="0.5"/>'
            f'</g>')
    return render(f"<defs>{defs}</defs>{body}", size, size + 8)


def star(size=160, top="#9BE3FF", bottom="#2E86DE"):
    c = size / 2
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = size * 0.45 if i % 2 == 0 else size * 0.22
        pts.append(f"{c + math.cos(a) * r:.1f},{c + 4 + math.sin(a) * r:.1f}")
    p = " ".join(pts)
    defs = grad("sf", [(0, top), (1, bottom)]) + shadow_filter()
    body = (f'<g filter="url(#sh)">'
            f'<polygon points="{p}" fill="{OUT_BLUE}" stroke="{OUT_BLUE}" stroke-width="16" stroke-linejoin="round"/>'
            f'<polygon points="{p}" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="7" stroke-linejoin="round"/>'
            f'<polygon points="{p}" fill="url(#sf)" stroke="url(#sf)" stroke-width="1" stroke-linejoin="round"/>'
            f'<ellipse cx="{c - size * 0.06}" cy="{c - size * 0.12}" rx="{size * 0.2}" ry="{size * 0.09}" '
            f'fill="#FFFFFF" opacity="0.45" transform="rotate(-20 {c} {c})"/></g>')
    return render(f"<defs>{defs}</defs>{body}", size, size + 10)


def coin(size=104):
    c = size / 2
    r = size / 2 - 7
    leaf = (f'M {c} {c - r * 0.5} C {c + r * 0.42} {c - r * 0.3} {c + r * 0.35} {c + r * 0.28} {c} {c + r * 0.48} '
            f'C {c - r * 0.35} {c + r * 0.28} {c - r * 0.42} {c - r * 0.3} {c} {c - r * 0.5} Z')
    defs = (grad("cg", [(0, "#FFF09A"), (0.55, "#FFCB2E"), (1, "#F09A12")])
            + grad("cr", [(0, "#FFD860"), (1, "#D9870C")]) + shadow_filter(dy=3, blur=2))
    body = (f'<g filter="url(#sh)">'
            f'<circle cx="{c}" cy="{c}" r="{r + 3}" fill="#7A4A0C"/>'
            f'<circle cx="{c}" cy="{c}" r="{r}" fill="url(#cr)"/>'
            f'<circle cx="{c}" cy="{c}" r="{r * 0.78}" fill="url(#cg)" stroke="#D88A10" stroke-width="3"/>'
            f'<path d="{leaf}" fill="#F7B21E" stroke="#A9650A" stroke-width="3.5" '
            f'transform="rotate(-28 {c} {c})"/>'
            f'<path d="M {c} {c - r * 0.42} L {c} {c + r * 0.4}" stroke="#A9650A" stroke-width="3" '
            f'stroke-linecap="round" transform="rotate(-28 {c} {c})"/>'
            f'<path d="M {c - r * 0.62} {c - r * 0.25} A {r * 0.7} {r * 0.7} 0 0 1 {c - r * 0.1} {c - r * 0.68}" '
            f'stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" fill="none" opacity="0.75"/></g>')
    return render(f"<defs>{defs}</defs>{body}", size, size + 6)


def gem(size=104):
    s = size / 100.0

    def P(*pts):
        return " ".join(f"{x * s:.1f},{y * s:.1f}" for x, y in pts)
    outline = P((12, 36), (30, 14), (70, 14), (88, 36), (50, 90))
    facets = [
        (P((30, 14), (70, 14), (62, 34), (38, 34)), "#9FF5CF"),
        (P((12, 36), (30, 14), (38, 34)), "#4FDCA0"),
        (P((70, 14), (88, 36), (62, 34)), "#25B37A"),
        (P((12, 36), (38, 34), (50, 90)), "#2CC487"),
        (P((38, 34), (62, 34), (50, 90)), "#5FE8AE"),
        (P((62, 34), (88, 36), (50, 90)), "#169A64"),
    ]
    body = (f'<defs>{shadow_filter(dy=3, blur=2)}</defs><g filter="url(#sh)">'
            f'<polygon points="{outline}" fill="{OUT_GREEN}" stroke="{OUT_GREEN}" stroke-width="12" stroke-linejoin="round"/>')
    for pts, col in facets:
        body += f'<polygon points="{pts}" fill="{col}" stroke="{col}" stroke-width="0.8" stroke-linejoin="round"/>'
    body += (f'<polygon points="{P((36, 18), (52, 18), (46, 28), (38, 28))}" fill="#FFFFFF" opacity="0.7"/>'
             f'<path d="M {78 * s} {14 * s} l {3 * s} {7 * s} l {7 * s} {3 * s} l {-7 * s} {3 * s} l {-3 * s} {7 * s} '
             f'l {-3 * s} {-7 * s} l {-7 * s} {-3 * s} l {7 * s} {-3 * s} Z" fill="#FFFFFF"/></g>')
    return render(body, size, size + 6)


def capsule_back(w=128, h=64):
    """9-slice XP bar frame: dark outline, white rim, deep blue inside."""
    r = h / 2
    defs = grad("rim", [(0, "#FFFFFF"), (1, "#E6DCC4")]) + grad("in", [(0, "#1E3557"), (1, "#2D4B78")])
    body = (f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="{r - 2}" fill="{OUT}"/>'
            f'<rect x="6" y="6" width="{w - 12}" height="{h - 12}" rx="{r - 6}" fill="url(#rim)"/>'
            f'<rect x="12" y="12" width="{w - 24}" height="{h - 24}" rx="{r - 12}" fill="url(#in)"/>')
    return render(f"<defs>{defs}</defs>{body}", w, h)


def capsule_fill(w=64, h=40, top="#9DEBFF", mid="#3FB3F5", bottom="#1F7FD6"):
    r = h / 2
    defs = grad("f", [(0, top), (0.5, mid), (1, bottom)])
    body = (f'<rect x="0" y="0" width="{w}" height="{h}" rx="{r}" fill="url(#f)"/>'
            f'<rect x="{r * 0.6}" y="{h * 0.14}" width="{w - r * 1.2}" height="{h * 0.26}" rx="{h * 0.13}" '
            f'fill="#FFFFFF" opacity="0.45"/>')
    return render(f"<defs>{defs}</defs>{body}", w, h)


def panel(w=160, h=160):
    """9-slice panel for menus/tooltips: cream with wooden-brown outline and rim."""
    defs = grad("p", [(0, "#FFFBEA"), (1, "#F2E2BC")]) + shadow_filter(dy=6, blur=4)
    body = (f'<g filter="url(#sh)"><rect x="4" y="4" width="{w - 8}" height="{h - 16}" rx="30" fill="{OUT}"/>'
            f'<rect x="9" y="9" width="{w - 18}" height="{h - 26}" rx="25" fill="#C98C4A"/>'
            f'<rect x="15" y="15" width="{w - 30}" height="{h - 38}" rx="20" fill="url(#p)"/></g>')
    return render(f"<defs>{defs}</defs>{body}", w, h)


# ---------------------------------------------------------------- glyphs on buttons

def _glyph(paths: str, size=96):
    return render(paths, size, size)


def gear(size=96):
    c = size / 2
    teeth = 8
    pts = []
    for i in range(teeth * 4):
        a = i / (teeth * 4) * 2 * math.pi
        r = size * 0.38 if (i % 4) in (0, 1) else size * 0.29
        pts.append(f"{c + math.cos(a + 0.1) * r:.1f},{c + math.sin(a + 0.1) * r:.1f}")
    p = " ".join(pts)
    return _glyph(f'<polygon points="{p}" fill="#FFF8E4" stroke="{OUT}" stroke-width="7" stroke-linejoin="round"/>'
                  f'<circle cx="{c}" cy="{c}" r="{size * 0.12}" fill="#F3A41C" stroke="{OUT}" stroke-width="6"/>',
                  size)


def note(size=96):
    o = f'stroke="{OUT}" stroke-width="6" stroke-linejoin="round"'
    return _glyph(f'<path d="M34 64 L34 22 L74 14 L74 56" fill="none" stroke="{OUT}" stroke-width="16" '
                  f'stroke-linecap="round" stroke-linejoin="round"/>'
                  f'<path d="M34 64 L34 22 L74 14 L74 56" fill="none" stroke="#FFF8E4" stroke-width="7" '
                  f'stroke-linecap="round" stroke-linejoin="round"/>'
                  f'<ellipse cx="26" cy="66" rx="13" ry="10" fill="#FFF8E4" {o}/>'
                  f'<ellipse cx="66" cy="58" rx="13" ry="10" fill="#FFF8E4" {o}/>', size)


def shop(size=128):
    """Market stall: striped scalloped awning over a wooden counter with goods."""
    o = f'stroke="{OUT}" stroke-width="6" stroke-linejoin="round"'
    stripes = ""
    for i in range(5):
        x = 16 + i * 19.2
        col = "#E8473B" if i % 2 == 0 else "#FFF8E4"
        stripes += f'<path d="M{x:.1f} 30 L{x + 19.2:.1f} 30 L{x + 19.2:.1f} 52 A9.6 9.6 0 0 1 {x:.1f} 52 Z" fill="{col}"/>'
    return render(
        f'<rect x="22" y="58" width="84" height="46" rx="6" fill="#C98C4A" {o}/>'
        f'<rect x="22" y="58" width="84" height="12" rx="4" fill="#A86A33"/>'
        f'<circle cx="46" cy="84" r="10" fill="#E8473B" {o}/><circle cx="66" cy="86" r="9" fill="#FFCB2E" {o}/>'
        f'<circle cx="84" cy="83" r="9" fill="#7CC44A" {o}/>'
        f'<path d="M16 30 L112 30 L112 52 L16 52 Z" fill="#FFF8E4" {o}/>{stripes}'
        f'<path d="M16 30 L112 30 L112 52 A9.6 9.6 0 0 1 102.4 61.6 A9.6 9.6 0 0 1 92.8 52 A9.6 9.6 0 0 1 '
        f'73.6 52 A9.6 9.6 0 0 1 54.4 52 A9.6 9.6 0 0 1 35.2 52 A9.6 9.6 0 0 1 16 52 Z" fill="none" {o}/>'
        f'<path d="M24 30 L36 14 L92 14 L104 30 Z" fill="#E8473B" {o}/>', size, size)


def plus(size=64):
    c = size / 2
    return _glyph(f'<path d="M{c} {c - 17} V{c + 17} M{c - 17} {c} H{c + 17}" stroke="{OUT}" stroke-width="17" '
                  f'stroke-linecap="round"/>'
                  f'<path d="M{c} {c - 17} V{c + 17} M{c - 17} {c} H{c + 17}" stroke="#FFFFFF" stroke-width="8" '
                  f'stroke-linecap="round"/>', size)


def ui_images() -> dict:
    """file stem -> PIL image (written to game/art/generated/ui/)."""
    return {
        "btn_round": round_button(128),
        "btn_round_green": round_button(128, "#A6EB6A", "#3FA535"),
        "star": star(160),
        "coin": coin(104),
        "gem": gem(104),
        "bar_back": capsule_back(128, 64),
        "bar_fill": capsule_fill(64, 40),
        "panel": panel(),
        "ico_gear": gear(),
        "ico_note": note(),
        "ico_shop": shop(),
        "ico_plus": plus(),
    }


def sheet(path):
    """Preview of all UI pieces on a grass-green background (for review)."""
    imgs = ui_images()
    w = sum(i.width for i in imgs.values()) + 20 * (len(imgs) + 1)
    h = max(i.height for i in imgs.values()) + 40
    bg = Image.new("RGBA", (w, h), (143, 198, 62, 255))
    x = 20
    for im in imgs.values():
        bg.alpha_composite(im, (x, 20))
        x += im.width + 20
    bg.save(path)


if __name__ == "__main__":
    sheet("/tmp/ui_sheet.png")
