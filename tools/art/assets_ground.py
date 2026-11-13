"""Ground tiles (TileMap cells) and field/soil decorations."""
import palette as P
from svgkit import Canvas, iso, TILE_W, TILE_H, mix

CELL_W, CELL_H = TILE_W + 4, TILE_H + 4  # 1-2 px overlap hides seams between tiles


def _diamond(hw=TILE_W / 2 + 1, hh=TILE_H / 2 + 0.5):
    return [(0, -hh), (hw, 0), (0, hh), (-hw, 0)]


def _inside(x, y, mx=54, my=25):
    return abs(x) / mx + abs(y) / my <= 1.0


def _scatter(c, n, mx=54, my=25):
    out = []
    while len(out) < n:
        x = c.rng.uniform(-mx, mx)
        y = c.rng.uniform(-my, my)
        if _inside(x, y, mx, my):
            out.append((x, y))
    return out


def _tuft(c, x, y, col=P.grass_dark, s=1.0):
    c.polyline([(x - 4 * s, y - 5 * s), (x - 1 * s, y), (x, y - 7 * s), (x + 1.5 * s, y), (x + 4.5 * s, y - 4.5 * s)],
               stroke=col, sw=1.6)


def _flower(c, x, y, petal):
    for dx, dy in ((-2.2, 0), (2.2, 0), (0, -1.6), (0, 1.6)):
        c.circle(x + dx, y + dy, 1.9, petal, stroke=None)
    c.circle(x, y, 1.3, P.flower_yellow, stroke=None)


def grass_tile(variant: int) -> Canvas:
    c = Canvas(CELL_W, CELL_H, CELL_W / 2, CELL_H / 2, seed=100 + variant)
    c.poly(_diamond(), P.grass, stroke=None)
    # soft light/dark patches give a painted feel without visible tile edges
    for _ in range(3 + variant):
        x, y = _scatter(c, 1, 40, 16)[0]
        col = P.grass_light if c.rng.random() < 0.6 else P.grass_dark
        c.ellipse(x, y, c.rng.uniform(10, 20), c.rng.uniform(4, 8), col, stroke=None, opacity=0.18)
    tufts = [1, 3, 1, 2][variant % 4]
    for x, y in _scatter(c, tufts):
        _tuft(c, x, y, s=c.rng.uniform(0.8, 1.15))
    if variant == 2:
        for x, y in _scatter(c, 3, 46, 20):
            _flower(c, x, y, c.rng.choice([P.flower_white, P.flower_pink]))
    if variant == 3:
        x, y = _scatter(c, 1, 30, 12)[0]
        c.ellipse(x, y, 4, 2.6, P.stone, sw=1.5)
        c.ellipse(x - 1, y - 0.8, 1.6, 0.9, P.cream, stroke=None, opacity=0.6)
    return c


def path_tile(variant: int) -> Canvas:
    c = Canvas(CELL_W, CELL_H, CELL_W / 2, CELL_H / 2, seed=200 + variant)
    c.poly(_diamond(), P.path, stroke=None)
    for _ in range(4):
        x, y = _scatter(c, 1, 40, 16)[0]
        c.ellipse(x, y, c.rng.uniform(8, 16), c.rng.uniform(3, 6), P.path_dark, stroke=None, opacity=0.25)
    for x, y in _scatter(c, 2 + variant * 2):
        r = c.rng.uniform(1.8, 3.2)
        c.ellipse(x, y, r * 1.4, r, P.path_dark, stroke=None, opacity=0.8)
        c.ellipse(x - 0.6, y - 0.6, r * 0.6, r * 0.4, P.cream, stroke=None, opacity=0.6)
    return c


GROUND_TILES = [("grass_0", lambda: grass_tile(0)), ("grass_1", lambda: grass_tile(1)),
                ("grass_2", lambda: grass_tile(2)), ("grass_3", lambda: grass_tile(3)),
                ("path_0", lambda: path_tile(0)), ("path_1", lambda: path_tile(1))]


# ---------------- field (raised soil bed) ----------------

def field() -> Canvas:
    c = Canvas(150, 100, 75, 50, seed=7)
    s = 0.44  # half size in tiles (slightly smaller than a tile -> grass border)
    h = 6
    top = [iso(-s, -s, h), iso(s, -s, h), iso(s, s, h), iso(-s, s, h)]
    left = [iso(-s, s, 0), iso(s, s, 0), iso(s, s, h), iso(-s, s, h)]
    right = [iso(s, s, 0), iso(s, -s, 0), iso(s, -s, h), iso(s, s, h)]
    c.shadow(0, 6, 62, 22, 0.15)
    c.poly(left, P.soil_dark)
    c.poly(right, mix(P.soil_dark, P.outline, 0.25))
    c.poly(top, c.radial([(0, P.soil_light), (1, P.soil)], -20, -12, 70))
    # furrows parallel to the grid X axis
    for t in (-0.25, 0.0, 0.25):
        a, b = iso(-s + 0.06, t, h), iso(s - 0.06, t, h)
        c.line((a[0], a[1] + 1.2), (b[0], b[1] + 1.2), stroke=P.soil_light, sw=2.2, opacity=0.8)
        c.line(a, b, stroke=P.soil_dark, sw=2.6)
    return c
