"""Village (Mossbrook): NPCs as chibi animal folk, restorable buildings, plaza props."""
from __future__ import annotations

import math
import random

from mathutils import Vector

from .. import kit
from ..kit import mat
from .animals import _rotz, eye
from .buildings import _cottage, _shingle_cone, _window, dock
from .farm import barrel, crate, hay_bale, wood
from .nature import bush, flowers

NPC = {
    "brumm": {"fur": "#9A6A44", "face": "#E8C9A0", "ear": "round", "shirt": "#FFF4E2", "extra": ["apron", "cap"]},
    "lotte": {"fur": "#8A6A50", "face": "#F0DCC0", "ear": "small", "shirt": "#FFD23F", "extra": ["raincoat", "sou"]},
    "fenna": {"fur": "#E8C08A", "face": "#FFF0D8", "ear": "huge", "shirt": "#7FA85A", "extra": ["glasses", "hat"]},
    "pip": {"fur": "#B8B0A8", "face": "#F2ECE6", "ear": "mouse", "shirt": "#5B9BD5", "extra": ["scarf", "bag"]},
}


def npc(name: str, breathe=0.0, blink=0.0, wave=0.0):
    """Chibi animal-folk villager, ~0.95 m tall, facing the camera (3/4)."""
    d = NPC[name]
    yaw = -20.0
    root = kit.empty(name, rot=(0, 0, math.radians(yaw)))
    fur = mat("npc_fur_" + name, d["fur"], rough=0.6, spec=0.2, edge=0.55, edge_color="#3A2A1E", sss=0.05)
    face = mat("npc_face_" + name, d["face"], rough=0.6, spec=0.2, edge=0.45)
    shirt = mat("npc_shirt_" + name, d["shirt"], rough=0.7, spec=0.15, edge=0.5)
    s = 1.0 + breathe
    # body (shirt) and legs
    kit.blob([{"co": (0, 0, 0.33 * s), "r": 0.26, "type": "ELLIPSOID", "size": (0.85, 0.95, 1.05)},
              {"co": (0, 0, 0.2), "r": 0.23}], shirt, name="torso", parent=root)
    for y in (-0.08, 0.08):
        kit.cyl(0.055, 0.14, fur, loc=(0, y, 0.0), bevel=0.02, verts=12, parent=root)
        kit.sphere(0.07, fur, loc=(0.03, y, 0.02), scale=(1.3, 1.0, 0.6), seg=12, parent=root)
    # head
    head_c = Vector((0.02, 0, 0.72 + breathe * 0.3))
    ho = kit.to_mesh(kit.blob([{"co": tuple(head_c), "r": 0.3, "type": "ELLIPSOID", "size": (0.95, 1.0, 0.92)}],
                              fur, name="head", parent=root))
    surf = kit.Surface([ho])
    hw = kit.world(root, head_c)
    look = _rotz(kit.TO_CAM, -yaw)
    # muzzle
    mz = head_c + Vector((0.2, 0, -0.08))
    kit.sphere(0.11, face, loc=mz, scale=(0.8, 1.1, 0.75), seg=18, parent=root)
    kit.sphere(0.035, mat("npc_nose", "#3A2420", rough=0.3, spec=0.5, edge=0.0), loc=mz + Vector((0.09, 0, 0.03)),
               scale=(0.8, 1.2, 0.8), seg=12, parent=root)
    for side in (-1, 1):
        dl = Vector((0.72, side * 0.55, 0.22))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            hr = (root.matrix_world.inverted() @ p - head_c).length
            eye(head_c, hr, dl, 0.06, root, look=look, lid=blink, lid_color=d["fur"])
        kit.sphere(0.035, mat("npc_cheek", "#FF9EAA", rough=0.6, edge=0.2),
                   loc=head_c + Vector((0.2, side * 0.17, -0.06)), scale=(0.6, 1, 0.6), seg=10, parent=root)
    # ears
    inner = mat("npc_ear_in", "#FFB9C0", rough=0.6, edge=0.3)
    for side in (-1, 1):
        if d["ear"] == "round":
            kit.sphere(0.09, fur, loc=head_c + Vector((-0.02, side * 0.22, 0.2)), scale=(0.5, 1, 1), seg=14, parent=root)
            kit.sphere(0.055, inner, loc=head_c + Vector((0.02, side * 0.22, 0.2)), scale=(0.3, 1, 1), seg=12, parent=root)
        elif d["ear"] == "small":
            kit.sphere(0.05, fur, loc=head_c + Vector((-0.04, side * 0.24, 0.14)), scale=(0.6, 1, 0.9), seg=12, parent=root)
        elif d["ear"] == "huge":
            kit.sphere(0.16, fur, loc=head_c + Vector((-0.04, side * 0.24, 0.32)), scale=(0.25, 0.8, 1.5),
                       rot=(side * -0.45, 0, 0), seg=18, parent=root)
            kit.sphere(0.12, inner, loc=head_c + Vector((-0.0, side * 0.24, 0.32)), scale=(0.15, 0.65, 1.3),
                       rot=(side * -0.45, 0, 0), seg=16, parent=root)
        else:  # mouse
            kit.sphere(0.15, fur, loc=head_c + Vector((-0.04, side * 0.26, 0.22)), scale=(0.3, 1, 1), seg=18, parent=root)
            kit.sphere(0.11, inner, loc=head_c + Vector((0.0, side * 0.26, 0.22)), scale=(0.2, 1, 1), seg=16, parent=root)
    # arms (one waving)
    for side, up in ((-1, 0.0), (1, wave)):
        sh = kit.empty("sh", loc=(0, side * 0.24, 0.45), rot=(side * -(0.4 + up * 1.8), 0, 0), parent=root)
        kit.blob(kit.chain([(0, 0, 0), (0.03, 0, -0.14)], [0.07, 0.065], steps=4), shirt, name="arm", parent=sh)
        kit.sphere(0.06, fur, loc=(0.04, 0, -0.2), seg=12, parent=sh)
    ex = d["extra"]
    if "apron" in ex:
        kit.box((0.04, 0.32, 0.34), mat("apron", "#FFFFFF", rough=0.8, edge=0.4), loc=(0.2, 0, 0.27), rot=(0, -0.15, 0),
                bevel=0.02, parent=root)
    if "cap" in ex:
        kit.cyl(0.2, 0.12, mat("cap", "#FFFFFF", rough=0.8, edge=0.4), loc=head_c + Vector((-0.02, 0, 0.18)),
                bevel=0.05, verts=20, parent=root)
        kit.sphere(0.2, mat("cap", "#FFFFFF", rough=0.8, edge=0.4), loc=head_c + Vector((-0.04, 0, 0.33)),
                   scale=(1, 1, 0.55), seg=20, parent=root)
    if "raincoat" in ex:
        kit.blob([{"co": (0, 0, 0.32), "r": 0.29, "type": "ELLIPSOID", "size": (0.9, 1.0, 1.0)}],
                 mat("coat", "#FFD23F", rough=0.35, spec=0.4, edge=0.5, edge_color="#8A6A10"), name="coat", parent=root)
    if "sou" in ex:
        hat = mat("sou", "#FFD23F", rough=0.35, spec=0.4, edge=0.5, edge_color="#8A6A10")
        kit.cyl(0.3, 0.03, hat, loc=head_c + Vector((-0.04, 0, 0.18)), rot=(0, -0.25, 0), bevel=0.01, verts=24,
                parent=root)
        kit.sphere(0.2, hat, loc=head_c + Vector((-0.05, 0, 0.22)), scale=(1, 1, 0.6), seg=20, parent=root)
    if "glasses" in ex:
        rim = mat("glasses", "#4A3A2E", rough=0.3, metal=0.5, edge=0.2)
        for side in (-1, 1):
            kit.torus(0.06, 0.012, rim, loc=head_c + Vector((0.235, side * 0.1, 0.03)), rot=(0, math.radians(90), 0),
                      parent=root)
    if "hat" in ex:
        hat = mat("hat", "#C8A060", rough=0.7, edge=0.5)
        kit.cyl(0.3, 0.025, hat, loc=head_c + Vector((-0.03, 0, 0.24)), bevel=0.01, verts=24, parent=root)
        kit.cyl(0.17, 0.12, hat, r2=0.15, loc=head_c + Vector((-0.03, 0, 0.25)), bevel=0.03, verts=20, parent=root)
    if "scarf" in ex:
        kit.torus(0.17, 0.05, mat("scarf", "#E8473B", rough=0.8, edge=0.45), loc=(0.02, 0, 0.52), parent=root)
    if "bag" in ex:
        kit.box((0.18, 0.08, 0.16), wood("bag", "#B07547"), loc=(0.0, -0.27, 0.25), bevel=0.03, parent=root)
    # tail
    if name == "brumm":
        kit.sphere(0.06, fur, loc=(-0.24, 0, 0.18), seg=12, parent=root)
    elif name == "pip":
        kit.curve_tube([(-0.22, 0, 0.12), (-0.35, 0.05, 0.08), (-0.45, 0.12, 0.15)], r=0.015, m=inner, parent=root)
    elif name == "fenna":
        kit.blob(kit.chain([(-0.22, 0, 0.2), (-0.38, 0.05, 0.15), (-0.48, 0.1, 0.2)], [0.08, 0.1, 0.07], steps=4),
                 fur, name="tail", parent=root)
    elif name == "lotte":
        kit.blob(kit.chain([(-0.2, 0, 0.1), (-0.4, 0.05, 0.04)], [0.08, 0.04], steps=4), fur, name="tail", parent=root)
    return root


def npc_frames():
    out = {}
    for name in NPC:
        for i in range(6):
            w = math.sin(i / 6 * 2 * math.pi)
            out[f"npc_{name}_{i}"] = (lambda w=w, i=i, n=name: npc(n, breathe=0.015 * w, blink=1.0 if i == 3 else 0.0,
                                                                   wave=0.0))
        for i in range(4):
            out[f"npc_{name}_wave_{i}"] = (lambda i=i, n=name: npc(n, wave=0.6 + 0.4 * math.sin(i / 4 * 2 * math.pi)))
    return out


# ---------------------------------------------------------------- buildings

def _rocks(root, rng, n=8, r=0.9):
    stone = mat("stone", "#9F977F", rough=0.8, spec=0.15, edge=0.6, var=0.05)
    for i in range(n):
        a = i / n * 2 * math.pi + rng.uniform(-0.2, 0.2)
        o = kit.ico(rng.uniform(0.12, 0.22), stone, loc=(math.cos(a) * r, math.sin(a) * r, 0.05), scale=(1.2, 1, 0.7),
                    sub=3, parent=root)
        kit.displace(o, strength=0.03, scale=0.1, seed=i + 1)


def lighthouse(restored=True):
    rng = random.Random(71)
    root = kit.empty("lighthouse")
    _rocks(root, rng, 10, 0.75)
    white = mat("lh_white", "#FFF8EC", rough=0.6, edge=0.5, edge_color="#9A8A70")
    red = mat("lh_red", "#E0503F", rough=0.55, edge=0.5, edge_color="#7A2218")
    h = 2.4 if restored else 1.1
    seg = 6 if restored else 3
    for i in range(seg):
        t0 = i / 6
        r0 = 0.55 - 0.18 * t0
        r1 = 0.55 - 0.18 * (i + 1) / 6
        kit.cyl(r0, 0.4, white if i % 2 == 0 else red, r2=r1, loc=(0, 0, i * 0.4), bevel=0.0, verts=28, parent=root)
    door = wood("door", "#7A4A2A")
    ad = Vector((kit.TO_CAM.x, kit.TO_CAM.y, 0)).normalized()
    a = math.atan2(ad.y, ad.x)
    kit.box((0.06, 0.26, 0.42), door, loc=(ad.x * 0.54, ad.y * 0.54, 0.22), rot=(0, 0, a), bevel=0.02, parent=root)
    if restored:
        dark = mat("lh_dark", "#3E4A5A", rough=0.4, metal=0.4, edge=0.4)
        kit.cyl(0.48, 0.06, dark, loc=(0, 0, h), bevel=0.01, verts=28, parent=root)
        for k in range(12):
            b = k / 12 * 2 * math.pi
            kit.cyl(0.012, 0.18, dark, loc=(math.cos(b) * 0.46, math.sin(b) * 0.46, h + 0.06), bevel=0.0, verts=6,
                    parent=root)
        kit.torus(0.46, 0.015, dark, loc=(0, 0, h + 0.24), parent=root)
        glass = mat("lh_light", "#FFE58A", rough=0.3, emit=2.5, edge=0.0)
        kit.cyl(0.26, 0.38, glass, loc=(0, 0, h + 0.06), bevel=0.02, verts=20, parent=root)
        _shingle_cone(0.36, 0.32, h + 0.44, "#E0503F", root, rows=3)
    else:
        planks = wood("scaffold", "#B07547")
        for x in (-0.6, 0.6):
            for y in (-0.6, 0.6):
                kit.box((0.05, 0.05, 1.5), planks, loc=(x, y, 0.75), bevel=0.01, parent=root)
        for z in (0.6, 1.2):
            kit.box((1.25, 0.05, 0.05), planks, loc=(0, -0.6, z), bevel=0.01, parent=root)
            kit.box((0.05, 1.25, 0.05), planks, loc=(0.6, 0, z), bevel=0.01, parent=root)
    return root


def museum(restored=True):
    rng = random.Random(72)
    root = kit.empty("museum")
    stone = mat("museum_stone", "#E8DCC4", rough=0.7, edge=0.5, edge_color="#8A7A5A")
    found = mat("found", "#A59D8B", rough=0.85, edge=0.55, var=0.07)
    kit.box((2.0, 1.5, 0.12), found, loc=(0, 0, 0.06), bevel=0.03, parent=root)
    for i in range(3):
        kit.box((2.0 - i * 0.08, 0.2, 0.08), found, loc=(0, -0.84 - i * 0.12, 0.04 + 0.0), bevel=0.02, parent=root)
    if restored:
        kit.box((1.7, 1.15, 1.0), stone, loc=(0, 0.1, 0.62), bevel=0.03, parent=root)
        for x in (-0.6, -0.2, 0.2, 0.6):
            kit.cyl(0.08, 0.95, stone, loc=(x, -0.58, 0.12), bevel=0.02, verts=16, parent=root)
            kit.box((0.2, 0.2, 0.06), stone, loc=(x, -0.58, 1.09), bevel=0.01, parent=root)
        kit.box((1.8, 1.4, 0.1), stone, loc=(0, -0.05, 1.17), bevel=0.03, parent=root)
        dome = mat("museum_dome", "#6E9E8A", rough=0.4, metal=0.5, spec=0.4, edge=0.45)
        kit.sphere(0.5, dome, loc=(0, 0.1, 1.22), scale=(1, 1, 0.75), seg=28, parent=root)
        kit.sphere(0.07, mat("vane_gold", "#F2C443", rough=0.3, metal=0.6, edge=0.3), loc=(0, 0.1, 1.62), seg=12,
                   parent=root)
        door = wood("museum_door", "#7A4A2A")
        kit.box((0.36, 0.05, 0.6), door, loc=(0, -0.48, 0.42), bevel=0.02, parent=root)
        bone = mat("bone", "#F6EEDC", rough=0.5, edge=0.45, edge_color="#9A8A6A")
        kit.cyl(0.03, 0.4, bone, loc=(-0.2, -0.56, 1.0), rot=(0, math.radians(90), 0), bevel=0.0, verts=8, parent=root)
        for x in (-0.2, 0.2):
            for z in (-0.035, 0.035):
                kit.sphere(0.04, bone, loc=(x, -0.56, 1.0 + z), seg=8, parent=root)
    else:
        _ruin_walls(root, 1.7, 1.15, stone, rng)
    return root


def _ruin_walls(root, L, W, wall, rng):
    for i in range(10):
        t = i / 10
        h = rng.uniform(0.15, 0.6)
        kit.box((L / 10 - 0.02, 0.15, h), wall, loc=(-L / 2 + (t + 0.05) * L, -W / 2, 0.12 + h / 2), bevel=0.02,
                parent=root)
    for i in range(7):
        h = rng.uniform(0.2, 0.7)
        kit.box((0.15, W / 7 - 0.02, h), wall, loc=(L / 2, -W / 2 + (i + 0.5) * W / 7, 0.12 + h / 2), bevel=0.02,
                parent=root)
    planks = wood("scaffold", "#B07547")
    for k in range(5):
        kit.box((0.9, 0.12, 0.04), planks, loc=(-0.2 + rng.uniform(-0.1, 0.1), 0.1 + k * 0.03, 0.14 + k * 0.045),
                rot=(0, 0, rng.uniform(-0.3, 0.3)), bevel=0.01, parent=root)
    sign = wood("sign_board", "#C9905A")
    kit.box((0.05, 0.05, 0.6), wood("sign_post", "#8C5A34"), loc=(L / 2 + 0.3, -W / 2 - 0.2, 0.3), bevel=0.01,
            parent=root)
    kit.box((0.04, 0.4, 0.26), sign, loc=(L / 2 + 0.33, -W / 2 - 0.2, 0.55), bevel=0.01, parent=root)
    kit.box((0.05, 0.34, 0.06), mat("stripe_y", "#FFD23F", rough=0.6, edge=0.3), loc=(L / 2 + 0.36, -W / 2 - 0.2, 0.6),
            bevel=0.005, parent=root)


def market(restored=True):
    rng = random.Random(73)
    root = kit.empty("market")
    if not restored:
        _ruin_walls(root, 1.6, 1.2, wood("ruin_wood", "#B07547"), rng)
        return root
    post = wood("stall_post", "#8C5A34")
    counter = wood("stall_counter", "#C48D58")
    colors = [("#E8473B", "#FFF4E2"), ("#5B9BD5", "#FFF4E2"), ("#7CC44A", "#FFF4E2")]
    for i, (x, y) in enumerate([(-0.55, -0.2), (0.55, -0.35), (0.0, 0.55)]):
        kit.box((0.75, 0.45, 0.4), counter, loc=(x, y, 0.2), bevel=0.03, parent=root)
        for dx in (-0.33, 0.33):
            kit.cyl(0.025, 0.95, post, loc=(x + dx, y + 0.2, 0), bevel=0.0, verts=8, parent=root)
        c1, c2 = colors[i]
        for k in range(6):
            kit.box((0.14, 0.6, 0.03), mat("awn_" + (c1 if k % 2 == 0 else c2), c1 if k % 2 == 0 else c2, rough=0.6,
                                            edge=0.4), loc=(x - 0.35 + k * 0.14, y, 0.98), rot=(math.radians(-15), 0, 0),
                    bevel=0.008, parent=root)
        goods = [("tomato", "#F0402F"), ("corn_kernel", "#FFD23F"), ("carrot", "#FF8A2B"), ("apple", "#E83B3B"),
                 ("berry", "#C43A6A")]
        for k in range(8):
            g = goods[(i * 3 + k) % len(goods)]
            kit.sphere(0.06, mat(g[0], g[1], rough=0.4, spec=0.4, edge=0.45), loc=(x - 0.27 + (k % 4) * 0.18,
                       y - 0.1 + (k // 4) * 0.14, 0.45), seg=10, parent=root)
    b = barrel()
    b.location = (1.05, 0.4, 0)
    b.parent = root
    c = crate()
    c.location = (-1.0, 0.45, 0)
    c.parent = root
    return root


def cafe(restored=True):
    rng = random.Random(74)
    root = kit.empty("cafe")
    wall = mat("cafe_wall", "#FFE0C8", rough=0.75, edge=0.5, edge_color="#A8785A")
    if not restored:
        _ruin_walls(root, 1.3, 1.05, wall, rng)
        return root
    ridge = _cottage(1.3, 1.05, 0.9, wall, "#3E7AB0", root)
    _window(-0.3, -0.525, 0.62, "y", root, w=0.36)
    _window(0.65, 0.0, 0.62, "x", root)
    kit.box((0.3, 0.06, 0.52), wood("door", "#7A4A2A"), loc=(0.3, -0.555, 0.4), bevel=0.02, parent=root)
    # terrace: tables with umbrellas
    for x, y in ((0.95, -0.75), (-0.2, -1.05)):
        kit.cyl(0.2, 0.03, wood("table", "#FFF4E2"), loc=(x, y, 0.4), bevel=0.01, verts=20, parent=root)
        kit.cyl(0.03, 0.4, wood("table_leg", "#8C5A34"), loc=(x, y, 0), bevel=0.0, verts=8, parent=root)
        kit.cyl(0.015, 0.9, wood("table_leg", "#8C5A34"), loc=(x, y, 0.4), bevel=0.0, verts=8, parent=root)
        kit.cyl(0.42, 0.2, mat("umbrella", "#E8473B", rough=0.6, edge=0.5), r2=0.03, loc=(x, y, 1.1), bevel=0.0,
                verts=12, parent=root)
        kit.cyl(0.05, 0.06, mat("cup", "#FFFFFF", rough=0.4, edge=0.4), loc=(x + 0.06, y, 0.43), bevel=0.01, verts=12,
                parent=root)
        for a in (0.0, 3.14):
            kit.box((0.18, 0.18, 0.04), wood("chair", "#C48D58"), loc=(x + math.cos(a) * 0.35, y + math.sin(a) * 0.35,
                    0.24), bevel=0.01, parent=root)
    # cup sign on the roof
    kit.cyl(0.13, 0.18, mat("cup", "#FFFFFF", rough=0.4, edge=0.4), loc=(0, 0, ridge + 0.05), r2=0.1, bevel=0.02,
            verts=18, parent=root)
    kit.torus(0.06, 0.02, mat("cup", "#FFFFFF", rough=0.4, edge=0.4), loc=(0.15, 0, ridge + 0.14),
              rot=(math.radians(90), 0, 0), parent=root)
    return root


def library(restored=True):
    rng = random.Random(75)
    root = kit.empty("library")
    wall = mat("lib_wall", "#C9D8E8", rough=0.75, edge=0.5, edge_color="#5A6A8A")
    if not restored:
        _ruin_walls(root, 1.1, 1.0, wall, rng)
        return root
    found = mat("found", "#A59D8B", rough=0.85, edge=0.55, var=0.07)
    kit.box((1.18, 1.08, 0.14), found, loc=(0, 0, 0.07), bevel=0.03, parent=root)
    kit.box((1.1, 1.0, 1.5), wall, loc=(0, 0, 0.89), bevel=0.03, parent=root)
    _shingle_cone(0.95, 0.7, 1.62, "#5B4A8C", root, rows=4)
    for z in (0.55, 1.15):
        _window(-0.25, -0.5, z, "y", root, w=0.26, h=0.3)
        _window(0.55, 0.15, z, "x", root, w=0.26, h=0.3)
    kit.box((0.3, 0.06, 0.5), wood("door", "#7A4A2A"), loc=(0.25, -0.53, 0.39), bevel=0.02, parent=root)
    book_cols = ["#E8473B", "#5B9BD5", "#FFD23F", "#7CC44A"]
    for k, c in enumerate(book_cols):
        kit.box((0.06, 0.18, 0.24), mat("book_" + c, c, rough=0.6, edge=0.4), loc=(0.75 + k * 0.07, -0.6, 0.12),
                rot=(0, 0, rng.uniform(-0.1, 0.1)), bevel=0.01, parent=root)
    return root


def fountain():
    root = kit.empty("fountain")
    stone = mat("museum_stone", "#E8DCC4", rough=0.7, edge=0.5, edge_color="#8A7A5A")
    water = mat("fountain_water", "#6FC8E0", rough=0.1, spec=0.7, edge=0.2, emit=0.15)
    kit.cyl(0.75, 0.3, stone, loc=(0, 0, 0), bevel=0.04, verts=32, parent=root)
    kit.cyl(0.66, 0.02, water, loc=(0, 0, 0.27), bevel=0.0, verts=32, parent=root)
    kit.cyl(0.12, 0.6, stone, loc=(0, 0, 0.25), bevel=0.02, verts=16, parent=root)
    kit.cyl(0.35, 0.1, stone, loc=(0, 0, 0.8), bevel=0.03, verts=24, parent=root)
    kit.cyl(0.29, 0.02, water, loc=(0, 0, 0.88), bevel=0.0, verts=24, parent=root)
    kit.sphere(0.1, water, loc=(0, 0, 1.0), scale=(1, 1, 1.6), seg=14, parent=root)
    moss = __import__("blender.assets.nature", fromlist=["x"])
    moss.moss_tufts([(0.6, 0.3, 0.3), (-0.5, 0.4, 0.3), (0.2, 0.7, 0.3)], random.Random(3), parent=root, size=0.08)
    return root


def rowboat():
    root = kit.empty("boat")
    hull = mat("boat_hull", "#5B9BD5", rough=0.5, edge=0.5, edge_color="#2A4A7A")
    inner = wood("boat_in", "#C08A55")
    o = kit.sphere(0.5, hull, loc=(0, 0, 0.12), scale=(1.6, 0.75, 0.42), seg=28, parent=root)
    kit.sphere(0.46, inner, loc=(0, 0, 0.2), scale=(1.5, 0.66, 0.3), seg=28, parent=root)
    for x in (-0.3, 0.25):
        kit.box((0.1, 0.62, 0.04), wood("seat", "#9C6539"), loc=(x, 0, 0.22), bevel=0.01, parent=root)
    kit.cyl(0.02, 1.1, wood("oar", "#B07547"), loc=(0.0, 0.42, 0.2), rot=(0, math.radians(90), 0.3), bevel=0.0,
            verts=8, parent=root)
    return root


def village_frames():
    out = npc_frames()
    for name, fn in (("lighthouse", lighthouse), ("museum", museum), ("market", market), ("cafe", cafe),
                     ("library", library)):
        out[f"{name}"] = (lambda fn=fn: fn(True))
        out[f"{name}_ruin"] = (lambda fn=fn: fn(False))
    out["fountain"] = fountain
    out["rowboat"] = rowboat
    out["dock_sea"] = lambda: dock(-90.0)
    return out
