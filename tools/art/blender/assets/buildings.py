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


def _sack(p, rng, parent, color="#E8D8B0"):
    m = mat("sack", color, rough=0.9, spec=0.05, edge=0.5, edge_color="#8A7350", var=0.05)
    o = kit.sphere(0.16, m, loc=(p[0], p[1], 0.14), scale=(1.0, 0.9, 1.05), seg=20, parent=parent)
    kit.displace(o, strength=0.02, scale=0.08, seed=rng.randrange(100) + 1)
    kit.sphere(0.06, m, loc=(p[0], p[1], 0.31), scale=(1.0, 1.0, 0.7), seg=12, parent=parent)
    kit.torus(0.05, 0.012, mat("twine", "#9A6B3A", rough=0.8, edge=0.3), loc=(p[0], p[1], 0.28), parent=parent)


def _shingle_cone(r, h, z, color, parent, rows=5, moss_rng=None):
    """Conical roof: a smooth cone wrapped in overlapping tile rings."""
    m = mat("shingle_" + color, color, rough=0.6, spec=0.2, edge=0.5, var=0.1)
    base = mat("roofbase_" + color, color, rough=0.6, spec=0.2, edge=0.45)
    kit.cyl(r, h, base, r2=0.02, loc=(0, 0, z), bevel=0.0, verts=32, parent=parent)
    for row in range(rows):
        t = row / rows
        rr = r * (1.0 - t)
        o = kit.torus(rr, 0.045 * (1.0 - t * 0.5), m, loc=(0, 0, z + h * t + 0.02), parent=parent,
                      scale=(1.0, 1.0, 0.7))
    kit.sphere(0.05, base, loc=(0, 0, z + h), seg=12, parent=parent)
    if moss_rng is not None:
        pts = [(math.cos(a) * r * 0.7, math.sin(a) * r * 0.7, z + h * 0.3) for a in
               (moss_rng.uniform(-1.5, 0.3) for _ in range(4))]
        moss_tufts(pts, moss_rng, parent=parent, size=0.06)


def feed_mill():
    """Round stone-and-timber mill. The sails are a separate camera-facing sprite (mill_sails)."""
    rng = random.Random(21)
    root = kit.empty("feed_mill")
    stone = mat("mill_stone", "#ABA391", rough=0.85, spec=0.1, edge=0.55, var=0.07)
    kit.cyl(0.62, 0.45, stone, loc=(0, 0, 0), bevel=0.04, verts=32, parent=root)
    for i in range(22):
        a = i / 22 * 2 * math.pi
        for z in (0.1, 0.3):
            kit.ico(0.075, stone, loc=(math.cos(a + z) * 0.62, math.sin(a + z) * 0.62, z), scale=(1.2, 1.2, 0.75),
                    sub=2, parent=root)
    wood_m = wood("mill_wood", "#C9905A")
    t = kit.cyl(0.52, 1.05, wood_m, r2=0.42, loc=(0, 0, 0.45), bevel=0.02, verts=8, parent=root)
    # timber frame posts on the 8 corners
    dark = wood("mill_beam", "#8C5A34")
    for i in range(8):
        a = i / 8 * 2 * math.pi
        kit.box((0.06, 0.06, 1.06), dark, loc=(math.cos(a) * 0.48, math.sin(a) * 0.48, 0.98),
                rot=(0, 0, a), bevel=0.015, parent=root)
    kit.torus(0.5, 0.035, dark, loc=(0, 0, 0.47), parent=root)
    _shingle_cone(0.68, 0.6, 1.48, "#B4553C", root, moss_rng=rng)
    # door and window facing the camera sides
    door_m = wood("mill_door", "#7A4A2A")
    a = math.atan2(-1, 1)  # towards -Y/+X diagonal (front)
    kit.box((0.06, 0.32, 0.5), door_m, loc=(math.cos(a - 0.5) * 0.6, math.sin(a - 0.5) * 0.6, 0.25),
            rot=(0, 0, a - 0.5), bevel=0.02, parent=root)
    glass = mat("glass", "#3B4C66", rough=0.15, spec=0.8, edge=0.2, coat=0.5)
    white = mat("trim", "#FFF4E2", rough=0.55, spec=0.2, edge=0.4, edge_color="#B9A48A")
    for ang, z in ((a + 0.75, 1.05),):
        kit.cyl(0.11, 0.05, white, loc=(math.cos(ang) * 0.5, math.sin(ang) * 0.5, z),
                rot=(0, math.radians(90), ang), bevel=0.01, verts=20, parent=root)
        kit.cyl(0.08, 0.06, glass, loc=(math.cos(ang) * 0.51, math.sin(ang) * 0.51, z),
                rot=(0, math.radians(90), ang), bevel=0.0, verts=20, parent=root)
    # sail hub (sails themselves are the separate sprite)
    hub = MILL_HUB
    kit.sphere(0.1, dark, loc=hub, seg=16, parent=root)
    kit.cyl(0.05, 0.3, dark, loc=hub - kit.TO_CAM * 0.25, rot=kit.TO_CAM.to_track_quat("Z", "Y").to_euler(),
            bevel=0.0, verts=10, parent=root)
    # props
    for p in ((0.75, -0.55), (0.95, -0.25), (0.6, -0.85)):
        _sack(p, rng, root)
    return root


MILL_HUB = Vector((0.0, 0.0, 1.55)) + Vector((kit.TO_CAM.x, kit.TO_CAM.y, 0)).normalized() * 0.62


def mill_sails():
    """Four sails in a plane facing the camera, centred on the origin (rotated in-game)."""
    root = kit.empty("sails")
    root.rotation_euler = kit.TO_CAM.to_track_quat("Z", "Y").to_euler()
    frame = wood("sail_frame", "#9C6539")
    cloth = mat("sail_cloth", "#FFF4DE", rough=0.8, edge=0.4, edge_color="#B9A48A")
    for k in range(4):
        arm = kit.empty("arm", rot=(0, 0, k * math.pi / 2 + 0.3), parent=root)
        kit.box((0.06, 0.95, 0.04), frame, loc=(0, 0.5, 0), bevel=0.015, parent=arm)
        kit.box((0.22, 0.62, 0.025), cloth, loc=(0.13, 0.6, 0.02), bevel=0.01, parent=arm)
        for j in range(3):
            kit.box((0.24, 0.025, 0.035), frame, loc=(0.13, 0.35 + j * 0.25, 0.03), bevel=0.008, parent=arm)
    kit.sphere(0.09, frame, loc=(0, 0, 0.04), seg=16, parent=root)
    return root


def bakery():
    """Half-timbered bakery with a brick dome oven and a striped awning."""
    rng = random.Random(31)
    root = kit.empty("bakery")
    L, W, H = 1.25, 1.05, 0.95
    plaster = mat("plaster", "#F7E8C9", rough=0.8, spec=0.1, edge=0.45, edge_color="#B59F78")
    beam = wood("bakery_beam", "#8C5A34")
    kit.box((L + 0.08, W + 0.08, 0.14), mat("found", "#A59D8B", rough=0.85, edge=0.55, var=0.07),
            loc=(0, 0, 0.07), bevel=0.03, parent=root)
    kit.box((L, W, H), plaster, loc=(0, 0, 0.14 + H / 2), bevel=0.03, parent=root)
    for x in (-L / 2, 0.0, L / 2):
        kit.box((0.07, 0.04, H), beam, loc=(x, -W / 2 - 0.01, 0.14 + H / 2), bevel=0.012, parent=root)
    for y in (-W / 2, W / 2):
        kit.box((0.04, 0.07, H), beam, loc=(L / 2 + 0.01, y, 0.14 + H / 2), bevel=0.012, parent=root)
    kit.box((L + 0.04, 0.04, 0.07), beam, loc=(0, -W / 2 - 0.01, 0.14 + H * 0.55), bevel=0.01, parent=root)
    # gable roof with red tiles
    tile = mat("tile", "#C9553E", rough=0.55, spec=0.25, edge=0.5, var=0.1, edge_color="#6E2618")
    pitch = math.radians(40)
    over = 0.16
    sl = (W / 2 + over) / math.cos(pitch)
    ridge = 0.14 + H + (W / 2) * math.tan(pitch) + 0.05
    for sy in (-1, 1):
        slab = kit.empty("slab", loc=(0, sy * (sl / 2) * math.cos(pitch), ridge - (sl / 2) * math.sin(pitch)),
                         rot=(pitch if sy < 0 else -pitch, 0, 0), parent=root)
        kit.box((L + 0.3, sl, 0.07), tile, bevel=0.03, parent=slab)
        for r in range(5):
            kit.cyl(0.05, L + 0.3, tile, loc=(-(L + 0.3) / 2, sy * (-sl / 2 + (r + 0.5) * sl / 5), 0.04),
                    rot=(0, math.radians(90), 0), bevel=0.0, verts=12, parent=slab, scale=(1.0, 0.6, 1.0))
    import bmesh
    import bpy
    for sx in (-1, 1):
        bm = bmesh.new()
        x = sx * L / 2
        gh = ridge - 0.05 - 0.14 - H
        v = [bm.verts.new((x, -W / 2, 0.14 + H)), bm.verts.new((x, W / 2, 0.14 + H)),
             bm.verts.new((x, 0, 0.14 + H + gh))]
        bm.faces.new(v if sx > 0 else list(reversed(v)))
        me = bpy.data.meshes.new("gable")
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("gable", me)
        kit.link(o)
        o.parent = root
        kit.set_mat(o, plaster)
        sol = o.modifiers.new("sol", "SOLIDIFY")
        sol.thickness = 0.15
    # chimney with bricks
    brick = mat("brick", "#C7643F", rough=0.8, spec=0.1, edge=0.5, var=0.1, edge_color="#6B2A16")
    kit.box((0.22, 0.22, 0.6), brick, loc=(-0.35, 0.2, ridge + 0.05), bevel=0.02, parent=root)
    kit.box((0.28, 0.28, 0.07), brick, loc=(-0.35, 0.2, ridge + 0.37), bevel=0.02, parent=root)
    # dome oven on the +X side
    oven_c = Vector((L / 2 + 0.38, 0.1, 0.0))
    kit.cyl(0.42, 0.3, brick, loc=oven_c, bevel=0.03, verts=28, parent=root)
    dome = kit.sphere(0.4, mat("oven_clay", "#E7C9A4", rough=0.8, edge=0.5, edge_color="#8D6A44"),
                      loc=oven_c + Vector((0, 0, 0.3)), scale=(1, 1, 0.9), seg=32, parent=root)
    glow = mat("ember", "#FF9A3C", rough=0.5, emit=3.0, edge=0.0)
    ad = Vector((kit.TO_CAM.x, kit.TO_CAM.y, 0)).normalized()
    kit.sphere(0.13, glow, loc=oven_c + ad * 0.36 + Vector((0, 0, 0.38)), scale=(1, 1, 1.1), seg=16, parent=root)
    kit.torus(0.15, 0.04, brick, loc=oven_c + ad * 0.38 + Vector((0, 0, 0.4)),
              rot=ad.to_track_quat("Z", "Y").to_euler(), parent=root)
    # door + window with striped awning on the -Y face
    door_m = wood("bakery_door", "#7A4A2A")
    kit.box((0.32, 0.06, 0.55), door_m, loc=(0.32, -W / 2 - 0.03, 0.14 + 0.275), bevel=0.02, parent=root)
    glass = mat("glass", "#3B4C66", rough=0.15, spec=0.8, edge=0.2, coat=0.5)
    kit.box((0.38, 0.05, 0.3), glass, loc=(-0.25, -W / 2 - 0.02, 0.62), bevel=0.01, parent=root)
    for i in range(6):
        col = "#E8473B" if i % 2 == 0 else "#FFF4E2"
        kit.box((0.085, 0.3, 0.03), mat(f"awning_{col}", col, rough=0.6, edge=0.4), loc=(-0.46 + i * 0.085, -W / 2 - 0.15, 0.86),
                rot=(math.radians(-25), 0, 0), bevel=0.008, parent=root)
    # bread on a little shelf, sacks, bench
    bread = mat("bread", "#E0A04A", rough=0.6, edge=0.5, edge_color="#8A5418", var=0.06)
    kit.box((0.5, 0.18, 0.05), beam, loc=(-0.25, -W / 2 - 0.12, 0.42), bevel=0.01, parent=root)
    for k in range(3):
        kit.sphere(0.06, bread, loc=(-0.4 + k * 0.15, -W / 2 - 0.12, 0.49), scale=(1.3, 0.9, 0.7), seg=14, parent=root)
    _sack((0.9, -0.75), rng, root)
    _sack((0.62, -0.92), rng, root, "#F2E6C8")
    return root


def dairy():
    """Blue plank cottage with a milk-can sign and churns."""
    rng = random.Random(41)
    root = kit.empty("dairy")
    L, W, H = 1.3, 1.05, 0.9
    blue = mat("dairy_wall", "#8EC3E6", rough=0.65, spec=0.15, edge=0.5, var=0.05, edge_color="#2F5F86")
    plank = mat("dairy_plank", "#85BBE0", rough=0.65, spec=0.15, edge=0.5, var=0.08, edge_color="#2F5F86")
    white = mat("trim", "#FFF4E2", rough=0.55, spec=0.2, edge=0.4, edge_color="#B9A48A")
    kit.box((L + 0.08, W + 0.08, 0.14), mat("found", "#A59D8B", rough=0.85, edge=0.55, var=0.07),
            loc=(0, 0, 0.07), bevel=0.03, parent=root)
    kit.box((L, W, H), blue, loc=(0, 0, 0.14 + H / 2), bevel=0.03, parent=root)
    for i in range(8):
        x = -L / 2 + (i + 0.5) * L / 8
        kit.box((L / 8 - 0.02, 0.025, H - 0.05), plank, loc=(x, -W / 2 - 0.01, 0.14 + H / 2), bevel=0.008, parent=root)
    for i in range(6):
        y = -W / 2 + (i + 0.5) * W / 6
        kit.box((0.025, W / 6 - 0.02, H - 0.05), plank, loc=(L / 2 + 0.01, y, 0.14 + H / 2), bevel=0.008, parent=root)
    for x, y in ((L / 2, -W / 2), (-L / 2, -W / 2), (L / 2, W / 2)):
        kit.box((0.07, 0.07, H + 0.02), white, loc=(x, y, 0.14 + H / 2), bevel=0.015, parent=root)
    # roof (hip-ish: a flattened box with bevel) in slate
    slate = mat("roof", "#5B7184", rough=0.6, spec=0.2, edge=0.45, var=0.07, edge_color="#2C3A4A")
    kit.box((L + 0.3, W + 0.3, 0.12), slate, loc=(0, 0, 0.14 + H + 0.06), bevel=0.05, parent=root)
    o = kit.cyl(0.62, 0.38, slate, r2=0.2, loc=(0, 0, 0.14 + H + 0.1), bevel=0.0, verts=4, parent=root,
                rot=(0, 0, math.radians(45)), scale=(1.12, 0.92, 1.0))
    # big milk can sign on the roof
    can_m = mat("can", "#DDE3EA", rough=0.25, spec=0.6, metal=0.7, edge=0.4)
    top = 0.14 + H + 0.48
    kit.cyl(0.13, 0.22, can_m, loc=(0, 0, top), bevel=0.02, verts=20, parent=root)
    kit.cyl(0.08, 0.1, can_m, r2=0.06, loc=(0, 0, top + 0.22), bevel=0.01, verts=20, parent=root)
    kit.cyl(0.07, 0.04, white, loc=(0, 0, top + 0.32), bevel=0.01, verts=20, parent=root)
    # door + windows
    kit.box((0.32, 0.06, 0.55), wood("dairy_door", "#FFF4E2"), loc=(-0.25, -W / 2 - 0.03, 0.14 + 0.275), bevel=0.02,
            parent=root)
    glass = mat("glass", "#3B4C66", rough=0.15, spec=0.8, edge=0.2, coat=0.5)
    for y in (-0.22, 0.25):
        kit.box((0.05, 0.3, 0.3), white, loc=(L / 2 + 0.03, y, 0.62), bevel=0.01, parent=root)
        kit.box((0.05, 0.22, 0.22), glass, loc=(L / 2 + 0.045, y, 0.62), bevel=0.01, parent=root)
    kit.box((0.36, 0.05, 0.3), white, loc=(0.3, -W / 2 - 0.03, 0.62), bevel=0.01, parent=root)
    kit.box((0.28, 0.05, 0.22), glass, loc=(0.3, -W / 2 - 0.045, 0.62), bevel=0.01, parent=root)
    # milk cans and a churn as props
    for p in ((0.85, -0.6), (1.0, -0.35)):
        kit.cyl(0.11, 0.3, can_m, loc=(p[0], p[1], 0), bevel=0.02, verts=18, parent=root)
        kit.cyl(0.06, 0.08, can_m, r2=0.05, loc=(p[0], p[1], 0.3), bevel=0.01, verts=16, parent=root)
    churn = wood("churn", "#B47A48")
    kit.cyl(0.12, 0.34, churn, r2=0.09, loc=(0.6, -0.9, 0), bevel=0.02, verts=16, parent=root)
    kit.cyl(0.015, 0.25, churn, loc=(0.6, -0.9, 0.3), bevel=0.0, verts=8, parent=root)
    flowers(kind="white", seed=44, count=8, spread=0.15).parent = root
    root.children[-1].location = (-0.8, -0.75, 0)
    return root


def order_board():
    """Wooden notice board with pinned order notes and a small shingle roof."""
    root = kit.empty("order_board")
    w = wood("board_wood", "#B07547")
    post = wood("board_post", "#8C5A34")
    paper = mat("note", "#FFF8E8", rough=0.8, edge=0.35, edge_color="#B5A07A", var=0.04)
    pin = mat("pin", "#E8473B", rough=0.3, spec=0.5, edge=0.3)
    yaw = math.atan2(kit.TO_CAM.y, kit.TO_CAM.x) + math.pi / 2  # local -Y (the notes) faces the camera
    board = kit.empty("board", rot=(0, 0, yaw), parent=root)
    for x in (-0.45, 0.45):
        kit.box((0.08, 0.08, 1.2), post, loc=(x, 0, 0.6), bevel=0.02, parent=board)
    kit.box((0.95, 0.06, 0.6), w, loc=(0, 0, 0.75), bevel=0.02, parent=board)
    kit.box((1.0, 0.07, 0.06), post, loc=(0, -0.01, 1.07), bevel=0.015, parent=board)
    kit.box((1.0, 0.07, 0.06), post, loc=(0, -0.01, 0.44), bevel=0.015, parent=board)
    for i, (x, z, r) in enumerate([(-0.28, 0.82, 0.08), (0.0, 0.76, -0.06), (0.28, 0.84, 0.05), (-0.12, 0.6, 0.1),
                                    (0.18, 0.58, -0.08)]):
        kit.box((0.2, 0.012, 0.18), paper, loc=(x, -0.04, z), rot=(0, r, 0), bevel=0.004, parent=board)
        kit.sphere(0.018, pin, loc=(x, -0.05, z + 0.07), seg=8, parent=board)
    roof = mat("tile", "#C9553E", rough=0.55, spec=0.25, edge=0.5, var=0.1, edge_color="#6E2618")
    kit.box((1.2, 0.4, 0.05), roof, loc=(0, -0.08, 1.24), rot=(math.radians(-20), 0, 0), bevel=0.02, parent=board)
    basket = wood("basket", "#D49A5A")
    kit.cyl(0.16, 0.14, basket, r2=0.19, loc=(0.6, -0.25, 0), bevel=0.02, verts=18, parent=board)
    apple = mat("apple", "#E83B3B", rough=0.3, spec=0.5, edge=0.4, coat=0.3)
    for k in range(4):
        kit.sphere(0.055, apple, loc=(0.55 + (k % 2) * 0.09, -0.22 - (k // 2) * 0.08, 0.16), seg=12, parent=board)
    flowers(kind="rose", seed=61, count=7, spread=0.14).parent = board
    board.children[-1].location = (-0.62, -0.25, 0)
    return root


def building_frames():
    return {
        "barn": barn,
        "feed_mill": feed_mill,
        "mill_sails": mill_sails,
        "bakery": bakery,
        "dairy": dairy,
        "order_board": order_board,
    }
