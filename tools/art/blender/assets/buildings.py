"""Buildings. Each sits on its own ground pad with small props (like the references)."""
from __future__ import annotations

import math
import random

from mathutils import Vector

from .. import kit
from ..kit import mat
from .farm import barrel, hay_bale, wood
from .nature import bush, flowers, moss_tufts


def pad(size_x, size_y, color="#D8B57A", loc=(0, 0, 0), parent=None):
    m = mat("pad", color, rough=0.95, spec=0.05, edge=0.25, var=0.0)
    o = kit.box((size_x, size_y, 0.04), m, loc=(loc[0], loc[1], 0.02), bevel=0.019, parent=parent)
    return o


def cobbles(cx, cy, sx, sy, rng, parent, count=40):
    m = mat("cobble", "#C9BFAA", rough=0.85, spec=0.1, edge=0.55, var=0.08)
    for _ in range(count):
        x = cx + rng.uniform(-sx / 2, sx / 2)
        y = cy + rng.uniform(-sy / 2, sy / 2)
        o = kit.ico(rng.uniform(0.06, 0.1), m, loc=(x, y, 0.035), scale=(1.2, 1.0, 0.35), sub=2, parent=parent,
                    rot=(0, 0, rng.uniform(0, 3)))


def barn():
    """Mossglen barn: red planks, white trim, slate roof with moss, round hayloft window.

    Footprint about 3 x 3 tiles. Ridge runs along world X, doors on the +X gable.
    """
    rng = random.Random(9)
    root = kit.empty("barn")
    L, W, H = 2.3, 1.9, 1.35       # wall box (x length, y width, height)
    base = 0.22
    cobbles(1.55, -0.1, 0.6, 1.6, rng, root, 26)

    # stone foundation
    stone = mat("found", "#A59D8B", rough=0.85, spec=0.1, edge=0.55, var=0.07)
    kit.box((L + 0.12, W + 0.12, base), stone, loc=(0, 0, base / 2), bevel=0.05, parent=root)
    for i in range(18):
        t = i / 18
        for side in (0, 1):
            if side == 0:
                p = (-L / 2 + t * L + 0.06, -W / 2 - 0.06, base * 0.5)
                sc = (1.3, 0.5, 0.8)
            else:
                p = (L / 2 + 0.06, -W / 2 + t * W + 0.06, base * 0.5)
                sc = (0.5, 1.3, 0.8)
            kit.ico(0.07, stone, loc=p, scale=sc, sub=2, parent=root)

    # walls
    red = mat("barn_red", "#D2493A", rough=0.7, spec=0.15, edge=0.45, var=0.07, edge_color="#7A2A22")
    kit.box((L, W, H), red, loc=(0, 0, base + H / 2), bevel=0.03, parent=root)
    plank = mat("barn_plank", "#C94234", rough=0.7, spec=0.15, edge=0.45, var=0.1, edge_color="#7A2A22")
    n = int(L / 0.19)
    for i in range(n):  # long side planks (-Y face)
        x = -L / 2 + (i + 0.5) * L / n
        kit.box((L / n - 0.025, 0.03, H - 0.06), plank, loc=(x, -W / 2 - 0.012, base + H / 2), bevel=0.01,
                parent=root)
    n2 = int(W / 0.19)
    for i in range(n2):  # gable end planks (+X face)
        y = -W / 2 + (i + 0.5) * W / n2
        kit.box((0.03, W / n2 - 0.025, H - 0.06), plank, loc=(L / 2 + 0.012, y, base + H / 2), bevel=0.01,
                parent=root)

    # gable triangle (both ends)
    roof_pitch = math.radians(38)
    gh = (W / 2) * math.tan(roof_pitch)
    import bmesh
    import bpy
    for sx in (-1, 1):
        bm = bmesh.new()
        x = sx * L / 2
        v = [bm.verts.new((x, -W / 2, base + H)), bm.verts.new((x, W / 2, base + H)),
             bm.verts.new((x, 0, base + H + gh))]
        v2 = [bm.verts.new((x - sx * 0.2, p.co.y, p.co.z)) for p in v]
        bm.faces.new(v if sx > 0 else list(reversed(v)))
        bm.faces.new(v2 if sx < 0 else list(reversed(v2)))
        for i in range(3):
            a, b = v[i], v[(i + 1) % 3]
            c, d = v2[(i + 1) % 3], v2[i]
            bm.faces.new((a, b, c, d) if sx < 0 else (d, c, b, a))
        me = bpy.data.meshes.new("gable")
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("gable", me)
        kit.link(o)
        o.parent = root
        kit.set_mat(o, red)

    # white trim: corner boards, eave line, door frame
    white = mat("trim", "#FFF4E2", rough=0.55, spec=0.2, edge=0.4, edge_color="#B9A48A")
    for x, y in ((L / 2, -W / 2), (-L / 2, -W / 2), (L / 2, W / 2)):
        kit.box((0.09, 0.09, H + 0.04), white, loc=(x, y, base + H / 2), bevel=0.02, parent=root)
    kit.box((L + 0.1, 0.07, 0.08), white, loc=(0, -W / 2 - 0.02, base + H), bevel=0.02, parent=root)

    # doors on +X gable
    door = mat("door", "#A9352B", rough=0.7, edge=0.45, var=0.05)
    dx = L / 2 + 0.035
    dw, dh = 0.95, 0.95
    kit.box((0.06, dw + 0.12, dh + 0.08), white, loc=(dx, 0, base + dh / 2 + 0.02), bevel=0.02, parent=root)
    for sy in (-1, 1):
        cy = sy * dw / 4
        kit.box((0.07, dw / 2 - 0.03, dh - 0.02), door, loc=(dx + 0.01, cy, base + dh / 2 + 0.01), bevel=0.015,
                parent=root)
        # X brace
        diag = math.atan2(dh - 0.1, dw / 2 - 0.1)
        for s2 in (-1, 1):
            kit.box((0.04, 0.05, math.hypot(dh - 0.1, dw / 2 - 0.1)), white,
                    loc=(dx + 0.05, cy, base + dh / 2 + 0.01), rot=(s2 * (math.pi / 2 - diag), 0, 0), bevel=0.012,
                    parent=root)
        kit.box((0.04, dw / 2 - 0.06, 0.05), white, loc=(dx + 0.05, cy, base + dh - 0.04), bevel=0.012,
                parent=root)
        kit.box((0.04, dw / 2 - 0.06, 0.05), white, loc=(dx + 0.05, cy, base + 0.06), bevel=0.012, parent=root)

    # round hayloft window in the gable
    glass = mat("glass", "#3B4C66", rough=0.15, spec=0.8, edge=0.2, coat=0.5)
    wz = base + H + gh * 0.42
    kit.torus(0.2, 0.045, white, loc=(L / 2 + 0.03, 0, wz), rot=(0, math.radians(90), 0), parent=root)
    kit.cyl(0.19, 0.03, glass, loc=(L / 2 + 0.005, 0, wz), rot=(0, math.radians(90), 0), bevel=0.0, parent=root)
    kit.box((0.03, 0.03, 0.38), white, loc=(L / 2 + 0.03, 0, wz), bevel=0.0, parent=root)
    kit.box((0.03, 0.38, 0.03), white, loc=(L / 2 + 0.03, 0, wz), bevel=0.0, parent=root)

    # side windows with flower boxes (-Y face)
    for x in (-0.55, 0.45):
        wy = -W / 2 - 0.03
        z = base + 0.78
        kit.box((0.46, 0.05, 0.46), white, loc=(x, wy, z), bevel=0.02, parent=root)
        kit.box((0.36, 0.05, 0.36), glass, loc=(x, wy - 0.01, z), bevel=0.01, parent=root)
        kit.box((0.03, 0.06, 0.36), white, loc=(x, wy - 0.015, z), bevel=0.0, parent=root)
        kit.box((0.36, 0.06, 0.03), white, loc=(x, wy - 0.015, z), bevel=0.0, parent=root)
        box_m = wood("flowerbox", "#8E5733")
        kit.box((0.5, 0.14, 0.1), box_m, loc=(x, wy - 0.08, z - 0.3), bevel=0.02, parent=root)
        pm = mat("petal_pink", "#FF8FB3", rough=0.5, edge=0.35, var=0.08)
        pm2 = mat("petal_yel", "#FFD23F", rough=0.5, edge=0.35, var=0.08)
        lm = mat("box_leaf", "#6FB83F", rough=0.7, edge=0.4, var=0.1)
        for k in range(7):
            px = x - 0.2 + k * 0.066
            kit.sphere(0.045, lm, loc=(px, wy - 0.09, z - 0.23), seg=10, parent=root)
            kit.sphere(0.03, pm if k % 2 else pm2, loc=(px, wy - 0.11, z - 0.2), seg=10, parent=root)

    # roof slabs with shingles
    slate = mat("roof", "#5B7184", rough=0.6, spec=0.2, edge=0.45, var=0.07, edge_color="#2C3A4A")
    shingle = mat("shingle", "#647C90", rough=0.6, spec=0.2, edge=0.5, var=0.12, edge_color="#2C3A4A")
    over = 0.22
    slope_len = (W / 2 + over) / math.cos(roof_pitch)
    rl = L + 2 * over
    ridge_z = base + H + gh + 0.05
    for sy in (-1, 1):
        tilt = roof_pitch if sy < 0 else -roof_pitch  # edge towards the ridge is the high one
        cy = sy * (slope_len / 2) * math.cos(roof_pitch)
        cz = ridge_z - (slope_len / 2) * math.sin(roof_pitch)
        slab = kit.empty("slab", loc=(0, cy, cz), rot=(tilt, 0, 0), parent=root)
        kit.box((rl, slope_len, 0.1), slate, loc=(0, 0, 0), bevel=0.04, parent=slab)
        rows, cols = 7, 15
        for r in range(rows):
            for c in range(cols):
                off = 0.5 if r % 2 else 0.0
                x = -rl / 2 + (c + 0.5 + off) * rl / cols
                if x > rl / 2 - 0.05:
                    continue
                y = sy * (-slope_len / 2 + (r + 0.6) * slope_len / rows)
                kit.box((rl / cols - 0.02, slope_len / rows + 0.04, 0.05), shingle,
                        loc=(x, y, 0.065 + 0.0 * r), rot=(sy * 0.08, 0, 0), bevel=0.018, seg=2, parent=slab)
    # ridge cap
    kit.cyl(0.08, rl + 0.04, slate, loc=(-rl / 2 - 0.02, 0, ridge_z + 0.02), rot=(0, math.radians(90), 0),
            bevel=0.0, verts=16, parent=root)
    # moss on roof: along the ridge and lower eave
    pts = []
    for i in range(16):
        x = rng.uniform(-rl / 2 + 0.1, rl / 2 - 0.1)
        pts.append((x, rng.uniform(-0.06, 0.06), ridge_z + 0.07))
    pts = pts[::2]
    for i in range(6):
        x = rng.uniform(-rl / 2 + 0.2, rl / 2 - 0.2)
        t = rng.uniform(0.75, 0.95)
        d = t * slope_len
        pts.append((x, -d * math.cos(roof_pitch), ridge_z - d * math.sin(roof_pitch) + 0.12))
    moss_tufts(pts, rng, parent=root, size=0.075)

    # weather vane
    iron = mat("vane", "#4E5560", rough=0.35, spec=0.5, metal=0.7, edge=0.3)
    kit.cyl(0.015, 0.45, iron, loc=(0.6, 0, ridge_z), bevel=0.0, verts=8, parent=root)
    kit.box((0.32, 0.02, 0.09), iron, loc=(0.6, 0, ridge_z + 0.38), bevel=0.01, parent=root)
    kit.sphere(0.035, mat("vane_gold", "#F2C443", rough=0.3, metal=0.6, edge=0.3), loc=(0.6, 0, ridge_z + 0.47),
               seg=12, parent=root)

    # props on the pad
    for p, rot in (((1.65, -1.25), 0.3), ((1.15, -1.38), -0.2)):
        h = hay_bale()
        h.location = (p[0], p[1], 0.04)
        h.rotation_euler = (0, 0, rot)
        h.parent = root
    hb = hay_bale()
    hb.location = (1.42, -1.3, 0.34)
    hb.rotation_euler = (0, 0, 0.05)
    hb.parent = root
    b = barrel()
    b.location = (1.7, 0.95, 0.04)
    b.parent = root
    bu = bush(seed=77, scale=0.8)
    bu.location = (-1.2, -1.25, 0.0)
    bu.parent = root
    return root


def building_frames():
    return {"barn": barn}
