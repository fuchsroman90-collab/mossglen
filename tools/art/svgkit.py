"""Small SVG building kit shared by all Mossglen assets.

Every asset draws into a Canvas whose origin (0, 0) is the sprite anchor
(ground contact point). The build step renders the SVG, crops the empty
border and stores the anchor so the game can place the sprite correctly.
"""
from __future__ import annotations

import math
import random

import palette as P

TILE_W = 128
TILE_H = 64
OUTLINE_W = 3.0
DETAIL_W = 1.5


def iso(gx: float, gy: float, h: float = 0.0) -> tuple[float, float]:
    """Grid units (tiles) + height (px) -> screen offset from the anchor."""
    return ((gx - gy) * TILE_W / 2, (gx + gy) * TILE_H / 2 - h)


def pts(points) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def mix(c1: str, c2: str, t: float) -> str:
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


class Canvas:
    def __init__(self, width: int, height: int, anchor_x: float, anchor_y: float, seed: int = 1):
        self.w = width
        self.h = height
        self.ax = anchor_x
        self.ay = anchor_y
        self.defs: list[str] = []
        self.body: list[str] = []
        self._ids = 0
        self.rng = random.Random(seed)

    # ---------- defs ----------
    def _id(self, prefix: str) -> str:
        self._ids += 1
        return f"{prefix}{self._ids}"

    def radial(self, stops, cx, cy, r, fx=None, fy=None) -> str:
        """Radial gradient in anchor space. stops = [(offset, colour), ...]."""
        gid = self._id("rg")
        fx = cx if fx is None else fx
        fy = cy if fy is None else fy
        s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        self.defs.append(
            f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx:.1f}" cy="{cy:.1f}" '
            f'r="{r:.1f}" fx="{fx:.1f}" fy="{fy:.1f}">{s}</radialGradient>')
        return f"url(#{gid})"

    def linear(self, stops, x1, y1, x2, y2) -> str:
        gid = self._id("lg")
        s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        self.defs.append(
            f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}">{s}</linearGradient>')
        return f"url(#{gid})"

    # ---------- primitives ----------
    def raw(self, s: str):
        self.body.append(s)

    @staticmethod
    def _style(fill, stroke, sw, opacity=1.0, extra=""):
        st = f'fill="{fill}"'
        if stroke:
            st += f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'
        if opacity < 1:
            st += f' opacity="{opacity:.3f}"'
        return st + extra

    def poly(self, points, fill, stroke=P.outline, sw=OUTLINE_W, opacity=1.0):
        self.body.append(f'<polygon points="{pts(points)}" {self._style(fill, stroke, sw, opacity)}/>')

    def line(self, a, b, stroke=P.outline, sw=DETAIL_W, opacity=1.0):
        self.body.append(
            f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
            f'{self._style("none", stroke, sw, opacity)}/>')

    def polyline(self, points, stroke=P.outline, sw=DETAIL_W, opacity=1.0):
        self.body.append(f'<polyline points="{pts(points)}" {self._style("none", stroke, sw, opacity)}/>')

    def path(self, d, fill, stroke=P.outline, sw=OUTLINE_W, opacity=1.0):
        self.body.append(f'<path d="{d}" {self._style(fill, stroke, sw, opacity)}/>')

    def circle(self, x, y, r, fill, stroke=P.outline, sw=OUTLINE_W, opacity=1.0):
        self.body.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" {self._style(fill, stroke, sw, opacity)}/>')

    def ellipse(self, x, y, rx, ry, fill, stroke=P.outline, sw=OUTLINE_W, opacity=1.0, rot=0.0):
        tr = f' transform="rotate({rot:.1f} {x:.2f} {y:.2f})"' if rot else ""
        self.body.append(
            f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
            f'{self._style(fill, stroke, sw, opacity)}{tr}/>')

    def rect(self, x, y, w, h, rx, fill, stroke=P.outline, sw=OUTLINE_W, opacity=1.0):
        self.body.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx:.2f}" '
            f'{self._style(fill, stroke, sw, opacity)}/>')

    # ---------- style helpers ----------
    def shadow(self, x, y, rx, ry, alpha=0.22):
        self.body.append(
            f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{P.shadow}" opacity="{alpha}"/>')

    def blob(self, circles, fill, ow=OUTLINE_W):
        """Union of circles with a single outer outline (outline pass, then fill pass)."""
        for x, y, r in circles:
            self.circle(x, y, r + ow / 2, P.outline, stroke=None)
        for x, y, r in circles:
            self.circle(x, y, r, fill, stroke=None)

    def moss_tuft(self, x, y, size=1.0):
        """Signature Mossglen moss cushion."""
        s = size
        circles = [(x - 5 * s, y, 4.5 * s), (x, y - 3 * s, 5.5 * s), (x + 5 * s, y, 4.2 * s)]
        self.blob(circles, P.moss, ow=2.0)
        self.circle(x - 1.5 * s, y - 4.5 * s, 2.2 * s, P.moss_light, stroke=None, opacity=0.9)

    # ---------- output ----------
    def svg(self) -> str:
        body = "".join(self.body)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}"><defs>{"".join(self.defs)}</defs>'
                f'<g transform="translate({self.ax} {self.ay})">{body}</g></svg>')


def face(origin, du, dv, u0, u1, v0, v1):
    """Quad on a plane: origin + u*du + v*dv for the given ranges."""
    def p(u, v):
        return (origin[0] + du[0] * u + dv[0] * v, origin[1] + du[1] * u + dv[1] * v)
    return [p(u0, v0), p(u1, v0), p(u1, v1), p(u0, v1)]


def star(cx, cy, r_out, r_in, n=5, rot=-90):
    out = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out
