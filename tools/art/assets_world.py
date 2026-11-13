"""Crops, nature, buildings, animals and fences."""
import math

import palette as P
from svgkit import Canvas, iso, face, mix, lerp, OUTLINE_W

FIELD_H = 6  # soil bed height, crops sit on top


# ---------------- crops ----------------

def _crop_spots():
    spots = [(gx, gy) for gx in (-0.26, 0.0, 0.26) for gy in (-0.26, 0.0, 0.26)]
    spots.sort(key=lambda p: p[0] + p[1])
    return [iso(gx, gy, FIELD_H) for gx, gy in spots]


def _stroke2(c, d, col, w):
    """Path with outline: thick dark stroke then coloured stroke."""
    c.raw(f'<path d="{d}" fill="none" stroke="{P.outline}" stroke-width="{w + 2.6}" stroke-linecap="round"/>')
    c.raw(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')


def wheat(stage: int) -> Canvas:
    c = Canvas(150, 120, 75, 70, seed=30 + stage)
    for i, (x, y) in enumerate(_crop_spots()):
        j = c.rng.uniform(-2, 2)
        x += j
        if stage == 0:
            for dx in (-4, 0, 4):
                c.ellipse(x + dx, y + c.rng.uniform(-1, 1), 2.2, 1.4, P.soil_dark, stroke=None)
                c.ellipse(x + dx - 0.5, y - 0.6, 0.9, 0.5, P.cream, stroke=None, opacity=0.7)
        elif stage == 1:
            c.ellipse(x - 3.5, y - 4, 4.5, 2.2, P.leaf_light, sw=1.8, rot=-35)
            c.ellipse(x + 3.5, y - 4.5, 4.5, 2.2, P.leaf, sw=1.8, rot=35)
            c.line((x, y), (x, y - 3), stroke=P.leaf_dark, sw=1.8)
        elif stage == 2:
            h = c.rng.uniform(15, 19)
            for k, ang in enumerate((-26, -9, 8, 24)):
                tx = x + math.sin(math.radians(ang)) * h
                ty = y - math.cos(math.radians(ang)) * h
                col = P.leaf if k % 2 else P.leaf_light
                _stroke2(c, f"M{x:.1f},{y:.1f} Q{x + ang * 0.12:.1f},{y - h * 0.6:.1f} {tx:.1f},{ty:.1f}", col, 2.6)
        else:
            h = c.rng.uniform(24, 29)
            heads = []
            for ang in (-22, -10, 0, 11, 23):
                a = math.radians(ang + c.rng.uniform(-3, 3))
                tx = x + math.sin(a) * h
                ty = y - math.cos(a) * h
                _stroke2(c, f"M{x:.1f},{y:.1f} L{tx:.1f},{ty:.1f}", P.wheat_dark, 1.8)
                heads.append((tx, ty - 4, math.degrees(a)))
            for tx, ty, rot in heads:
                c.ellipse(tx, ty, 3.4, 7.5, P.outline, stroke=None, rot=rot)
            for tx, ty, rot in heads:
                c.ellipse(tx, ty, 2.2, 6.2, P.wheat, stroke=None, rot=rot)
                c.ellipse(tx - 0.8, ty - 2, 0.9, 2.6, P.cream, stroke=None, opacity=0.7, rot=rot)
    return c


# ---------------- nature ----------------

def tree_oak(variant=0) -> Canvas:
    c = Canvas(220, 260, 110, 220, seed=50 + variant)
    c.shadow(4, 2, 52, 20)
    # trunk with root flare
    c.path("M-11,0 C-9,-20 -9,-50 -7,-78 L7,-78 C9,-50 9,-20 11,0 C6,4 -6,4 -11,0 Z",
           c.linear([(0, P.wood_light), (1, P.wood_dark)], -11, 0, 11, 0))
    c.line((-2, -12), (-1, -40), stroke=P.wood_dark, sw=1.6, opacity=0.7)
    rng = c.rng
    circles = [(0, -120, 46), (-36, -98, 32), (36, -100, 33), (-22, -140, 30), (24, -142, 30),
               (0, -88, 34), (-44, -122, 24), (44, -124, 24)]
    circles = [(x + rng.uniform(-3, 3), y + rng.uniform(-3, 3), r) for x, y, r in circles]
    fill = c.radial([(0, P.leaf_light), (0.55, P.leaf), (1, P.leaf_dark)], -26, -150, 105, -30, -158)
    c.blob(circles, fill)
    # leaf clusters (painted texture)
    for _ in range(14):
        x, y = rng.uniform(-48, 48), rng.uniform(-160, -80)
        if (x / 52) ** 2 + ((y + 118) / 46) ** 2 < 0.8:
            c.path(f"M{x - 5:.1f},{y:.1f} Q{x:.1f},{y + 5:.1f} {x + 5:.1f},{y:.1f}", "none",
                   stroke=P.leaf_dark, sw=1.6, opacity=0.55)
    for x, y, r in ((-22, -145, 9), (-8, -152, 6), (-36, -128, 5)):
        c.circle(x, y, r, P.leaf_light, stroke=None, opacity=0.55)
    if variant == 1:  # apple tree
        for x, y in ((-20, -110), (18, -126), (30, -96), (-30, -132), (4, -96), (-6, -138)):
            c.circle(x, y, 5, P.berry, sw=2)
            c.circle(x - 1.6, y - 1.6, 1.6, P.cream, stroke=None, opacity=0.8)
    return c


def tree_pine() -> Canvas:
    c = Canvas(180, 280, 90, 240, seed=61)
    c.shadow(2, 2, 40, 16)
    c.rect(-7, -40, 14, 42, 4, c.linear([(0, P.wood_light), (1, P.wood_dark)], -7, 0, 7, 0))
    layers = [(-30, 52, 46), (-75, 44, 44), (-118, 34, 40), (-156, 22, 34)]
    for y, w, h in layers:
        d = (f"M{-w},{y} Q{-w * 0.55},{y - h * 0.45} 0,{y - h} Q{w * 0.55},{y - h * 0.45} {w},{y} "
             f"Q0,{y + 12} {-w},{y} Z")
        c.path(d, c.linear([(0, P.leaf_light), (0.45, P.pine), (1, P.pine_dark)], -w, y - h, w, y))
        c.path(f"M{-w * 0.6},{y - 4} Q0,{y + 5} {w * 0.6},{y - 4}", "none", stroke=P.pine_dark, sw=1.6, opacity=0.6)
    c.circle(-8, -150, 4, P.leaf_light, stroke=None, opacity=0.6)
    return c


def bush(berries=False) -> Canvas:
    c = Canvas(120, 90, 60, 70, seed=70 + berries)
    c.shadow(2, 1, 34, 12)
    circles = [(-16, -14, 16), (14, -14, 17), (0, -24, 18), (-26, -6, 10), (26, -6, 11), (0, -8, 18)]
    c.blob(circles, c.radial([(0, P.leaf_light), (0.6, P.leaf), (1, P.leaf_dark)], -14, -36, 50))
    c.circle(-10, -30, 5, P.leaf_light, stroke=None, opacity=0.55)
    if berries:
        for x, y in ((-14, -14), (10, -22), (18, -8), (-2, -10), (-22, -4), (4, -30)):
            c.circle(x, y, 3.6, P.berry, sw=1.8)
            c.circle(x - 1, y - 1.2, 1.1, P.cream, stroke=None)
    return c


def rock() -> Canvas:
    c = Canvas(100, 70, 50, 52, seed=81)
    c.shadow(2, 0, 30, 10)
    c.path("M-26,0 C-30,-14 -18,-28 -2,-28 C16,-30 30,-16 26,0 C14,6 -14,6 -26,0 Z",
           c.radial([(0, P.cream_dark), (0.5, P.stone), (1, P.stone_dark)], -10, -24, 44))
    c.moss_tuft(-6, -26, 1.1)
    c.moss_tuft(12, -22, 0.8)
    return c


# ---------------- buildings ----------------

def barn() -> Canvas:
    c = Canvas(460, 420, 230, 330, seed=90)
    a, b = 2.5, 2.1      # footprint in tiles (ridge runs along grid X)
    H, R, o = 78, 58, 0.16
    eave_drop = R * o / (b / 2)

    c.shadow(8, 8, 170, 66, 0.18)

    # foundation stones
    fh = 12
    c.poly([iso(-a / 2, b / 2, 0), iso(a / 2, b / 2, 0), iso(a / 2, b / 2, fh), iso(-a / 2, b / 2, fh)], P.stone)
    c.poly([iso(a / 2, b / 2, 0), iso(a / 2, -b / 2, 0), iso(a / 2, -b / 2, fh), iso(a / 2, b / 2, fh)], P.stone_dark)

    # back roof slope (thin sliver above the ridge)
    ridge_l, ridge_r = iso(-a / 2 - o, 0, H + R), iso(a / 2 + o, 0, H + R)
    back_r, back_l = iso(a / 2 + o, -b / 2 - o, H - eave_drop), iso(-a / 2 - o, -b / 2 - o, H - eave_drop)
    c.poly([ridge_l, ridge_r, back_r, back_l], P.roof_dark)

    # long wall (lit side)
    lw = [iso(-a / 2, b / 2, fh), iso(a / 2, b / 2, fh), iso(a / 2, b / 2, H), iso(-a / 2, b / 2, H)]
    c.poly(lw, c.linear([(0, P.barn), (1, P.barn_side)], lw[0][0], 0, lw[1][0], 0))
    # gable wall (shadow side) incl. triangle
    gw = [iso(a / 2, b / 2, fh), iso(a / 2, -b / 2, fh), iso(a / 2, -b / 2, H), iso(a / 2, 0, H + R), iso(a / 2, b / 2, H)]
    c.poly(gw, P.barn_dark)

    # vertical planks
    for i in range(1, 12):
        u = -a / 2 + a * i / 12
        c.line(iso(u, b / 2, fh + 1), iso(u, b / 2, H - 1), stroke=P.barn_dark, sw=1.4, opacity=0.55)
    for i in range(1, 8):
        v = -b / 2 + b * i / 8
        top = H + R * (1 - abs(v) / (b / 2)) - 2
        c.line(iso(a / 2, v, fh + 1), iso(a / 2, v, top), stroke=P.outline, sw=1.2, opacity=0.25)

    # windows on long wall
    origin = iso(0, b / 2, 0)
    du = (iso(1, 0)[0], iso(1, 0)[1])
    dv = (0, -1)
    for cu in (-0.72, 0.18):
        frame = face(origin, du, dv, cu - 0.2, cu + 0.2, 26, 56)
        c.poly(frame, P.cream, sw=2.5)
        glass = face(origin, du, dv, cu - 0.15, cu + 0.15, 30, 52)
        c.poly(glass, c.linear([(0, mix(P.glass, P.sky, 0.5)), (1, P.glass)], 0, glass[2][1], 0, glass[0][1]), sw=1.5)
        mid = face(origin, du, dv, cu, cu, 30, 52)
        c.line(mid[0], mid[3], stroke=P.cream, sw=2.2)
        midh = face(origin, du, dv, cu - 0.15, cu + 0.15, 41, 41)
        c.line(midh[0], midh[1], stroke=P.cream, sw=2.2)
        # flower box
        box = face(origin, du, dv, cu - 0.22, cu + 0.22, 20, 26)
        c.poly(box, P.wood, sw=2)
        for k in range(5):
            p = lerp(box[3], box[2], (k + 0.5) / 5)
            c.circle(p[0], p[1] - 2, 3, [P.flower_pink, P.flower_white, P.flower_yellow][k % 3], sw=1.5)

    # big door on gable side
    g_origin = iso(a / 2, 0, 0)
    gdu = (iso(0, 1)[0], iso(0, 1)[1])
    door = face(g_origin, gdu, dv, -0.42, 0.42, fh, 54)
    c.poly(door, P.wood, sw=2.5)
    for k in range(1, 6):
        p0, p1 = lerp(door[0], door[1], k / 6), lerp(door[3], door[2], k / 6)
        c.line(p0, p1, stroke=P.wood_dark, sw=1.2, opacity=0.7)
    c.polyline([door[0], door[1], door[2], door[3], door[0]], stroke=P.cream, sw=4)
    c.line(door[0], door[2], stroke=P.cream, sw=4)
    c.line(door[1], door[3], stroke=P.cream, sw=4)
    mid0, mid1 = lerp(door[0], door[3], 1), lerp(door[0], door[1], 0.5)
    c.line(lerp(door[0], door[1], 0.5), lerp(door[3], door[2], 0.5), stroke=P.outline, sw=1.6)
    # hay loft
    loft = face(g_origin, gdu, dv, -0.17, 0.17, 72, 98)
    c.poly(loft, P.outline, sw=2)
    inner = face(g_origin, gdu, dv, -0.13, 0.13, 74, 94)
    c.poly(inner, P.wheat, stroke=None)
    for k in range(4):
        p = lerp(inner[0], inner[1], (k + 0.5) / 4)
        c.line((p[0], p[1] - 2), (p[0] + 2, p[1] - 9), stroke=P.wheat_dark, sw=1.4)
    c.polyline([loft[0], loft[1], loft[2], loft[3], loft[0]], stroke=P.cream, sw=3)

    # corner trims
    for p0, p1 in ((iso(-a / 2, b / 2, fh), iso(-a / 2, b / 2, H)), (iso(a / 2, b / 2, fh), iso(a / 2, b / 2, H)),
                   (iso(a / 2, -b / 2, fh), iso(a / 2, -b / 2, H))):
        c.line(p0, p1, stroke=P.outline, sw=7)
        c.line(p0, p1, stroke=P.cream, sw=4.2)

    # front roof slope
    eave_l, eave_r = iso(-a / 2 - o, b / 2 + o, H - eave_drop), iso(a / 2 + o, b / 2 + o, H - eave_drop)
    th = 7
    c.poly([eave_l, eave_r, (eave_r[0], eave_r[1] + th), (eave_l[0], eave_l[1] + th)], P.roof_dark)
    c.poly([ridge_l, ridge_r, eave_r, eave_l],
           c.linear([(0, mix(P.roof, P.cream, 0.15)), (1, P.roof)], 0, ridge_l[1], 0, eave_l[1]))
    # shingle rows
    rows = 6
    for r in range(1, rows):
        t = r / rows
        p0, p1 = lerp(ridge_l, eave_l, t), lerp(ridge_r, eave_r, t)
        c.line(p0, p1, stroke=P.roof_dark, sw=1.8, opacity=0.8)
        n = 14
        for k in range(n):
            q = lerp(p0, p1, (k + (0.5 if r % 2 else 0.0)) / n)
            q2 = lerp(lerp(ridge_l, eave_l, t - 1 / rows), lerp(ridge_r, eave_r, t - 1 / rows),
                      (k + (0.5 if r % 2 else 0.0)) / n)
            c.line(q, lerp(q, q2, 0.75), stroke=P.roof_dark, sw=1.2, opacity=0.45)
    # gable fascia boards
    for p0, p1 in ((ridge_r, eave_r), (ridge_r, back_r)):
        c.line(p0, p1, stroke=P.outline, sw=9)
        c.line(p0, p1, stroke=P.cream, sw=5.5)
    # ridge cap with moss
    c.line(ridge_l, ridge_r, stroke=P.outline, sw=9)
    c.line(ridge_l, ridge_r, stroke=P.roof_dark, sw=5.5)
    for t in (0.12, 0.33, 0.7):
        p = lerp(ridge_l, ridge_r, t)
        c.moss_tuft(p[0], p[1] + 1, 1.3)
    for t, s in ((0.2, 0.7), (0.55, 0.85), (0.85, 0.6)):
        p = lerp(lerp(ridge_l, eave_l, s), lerp(ridge_r, eave_r, s), t)
        c.moss_tuft(p[0], p[1], 1.0)
    # weather vane rooster silhouette
    tip = lerp(ridge_l, ridge_r, 0.5)
    c.line(tip, (tip[0], tip[1] - 26), stroke=P.outline, sw=2.5)
    c.path(f"M{tip[0] - 9},{tip[1] - 26} q4,-9 11,-7 l2,-5 l3,5 q4,2 2,7 z", P.gold, sw=2)
    return c


# ---------------- animals ----------------

def chicken(frame=0) -> Canvas:
    c = Canvas(90, 90, 45, 70, seed=95)
    c.shadow(0, 0, 15, 5, 0.25)
    # legs
    lift = 2 if frame == 1 else 0
    for x, dy in ((-4, 0), (4, lift)):
        c.line((x, -9), (x, -dy), stroke=P.outline, sw=4.2)
        c.line((x, -9), (x, -dy), stroke=P.beak, sw=2.2)
        c.line((x - 2, -dy), (x + 3, -dy), stroke=P.beak, sw=2)
    body = c.radial([(0, "#FFFFFF"), (0.5, P.chick_body), (1, P.chick_shade)], -6, -30, 26)
    # tail
    c.path("M-14,-20 Q-26,-30 -20,-40 Q-12,-34 -8,-26 Z", P.chick_shade, sw=2.6)
    c.ellipse(0, -21, 16, 13, body)
    # head
    c.circle(10, -36, 10, body)
    # comb
    c.blob([(6, -46, 3.4), (10, -48, 3.8), (14, -46, 3.2)], P.comb, ow=2.4)
    # beak & wattle
    c.path("M19,-37 L25,-34 L19,-31 Z", P.beak, sw=2)
    c.ellipse(18, -28, 2.2, 3, P.comb, sw=1.8)
    # eye
    c.circle(13, -38, 2.4, P.outline, stroke=None)
    c.circle(13.8, -38.8, 0.9, "#FFFFFF", stroke=None)
    # cheek
    c.ellipse(9, -33, 2.6, 1.6, P.flower_pink, stroke=None, opacity=0.7)
    # wing
    c.path("M-8,-24 Q0,-30 6,-22 Q2,-13 -8,-16 Z", P.chick_shade, sw=2)
    return c


# ---------------- fences ----------------

def fence(axis: str) -> Canvas:
    """One-tile fence segment along grid X ('x') or Y ('y'), anchor = segment centre."""
    c = Canvas(150, 110, 75, 70, seed=97)
    d = (0.5, 0) if axis == "x" else (0, 0.5)
    p0, p1 = iso(-d[0], -d[1]), iso(d[0], d[1])
    for hgt in (10, 21):
        a, b = (p0[0], p0[1] - hgt), (p1[0], p1[1] - hgt)
        c.line(a, b, stroke=P.outline, sw=7.5)
        c.line(a, b, stroke=P.wood_light if hgt == 21 else P.wood, sw=4.5)
    for i, p in enumerate((p0, p1)):
        c.rect(p[0] - 4.5, p[1] - 30, 9, 31, 3.5, c.linear([(0, P.wood_light), (1, P.wood_dark)], p[0] - 4.5, 0, p[0] + 4.5, 0), sw=2.6)
        c.ellipse(p[0], p[1] - 30, 4.5, 2.2, P.wood_light, sw=1.8)
    c.moss_tuft(p0[0], p0[1] - 31, 0.7)
    return c
