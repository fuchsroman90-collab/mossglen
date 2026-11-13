"""M9.5 progression assets: farmhouse, silo with fill levels, delivery truck, coin crate,
construction sites and the land parcel sign."""
from __future__ import annotations

import math
import random

from .. import kit
from ..kit import mat
from .buildings import _cottage, _shingle_cone, _window, cobbles
from .farm import barrel, crate, hay_bale, wood
from .nature import flowers, moss_tufts

CAM_YAW = math.atan2(kit.TO_CAM.y, kit.TO_CAM.x) + math.pi / 2  # local -Y faces the camera


def _place(builder, loc, parent, rot_z=0.0, scale=1.0):
    o = builder()
    o.location = loc
    o.rotation_euler = (0, 0, rot_z)
    o.scale = (scale, scale, scale)
    o.parent = parent
    return o


# ------------------------------------------------------------------ farmhouse

def farmhouse():
    """Cosy two-storey farmhouse: cream walls, green shutters, red tiled roof, porch, chimney."""
    rng = random.Random(21)
    root = kit.empty("farmhouse")
    cobbles(0.2, -1.05, 1.2, 0.35, rng, root, 18)
    wall = mat("fh_wall", "#F4E6C8", rough=0.75, spec=0.1, edge=0.45, var=0.05, edge_color="#B39C74")
    ridge = _cottage(2.0, 1.45, 1.35, wall, "#C9553E", root, pitch=42)
    trim = mat("fh_trim", "#FFFDF4", rough=0.5, spec=0.2, edge=0.4, edge_color="#B9A48A")
    shutter = mat("fh_shutter", "#4FA65A", rough=0.55, spec=0.2, edge=0.5, edge_color="#245C2C")
    # windows with shutters on the long (-Y) face, upstairs and down
    for x in (-0.6, 0.6):
        for z in (0.55, 1.15):
            _window(x, -0.73, z, "y", root, w=0.32, h=0.34)
            for sx in (-1, 1):
                kit.box((0.1, 0.03, 0.36), shutter, loc=(x + sx * 0.24, -0.76, z), bevel=0.01, parent=root)
    # door + porch roof on the front
    door = wood("fh_door", "#9C5A32")
    kit.box((0.36, 0.05, 0.62), door, loc=(0.0, -0.75, 0.45), bevel=0.02, parent=root)
    kit.sphere(0.025, mat("knob", "#F2C14E", rough=0.3, spec=0.7, metal=0.6), loc=(0.11, -0.79, 0.45), seg=10,
               parent=root)
    post = mat("fh_post", "#FFFDF4", rough=0.5, edge=0.4, edge_color="#B9A48A")
    for x in (-0.55, 0.55):
        kit.cyl(0.035, 0.85, post, loc=(x, -1.18, 0.14), bevel=0.01, verts=12, parent=root)
    porch = mat("fh_porch", "#C9553E", rough=0.55, spec=0.25, edge=0.5, var=0.1)
    kit.box((1.35, 0.55, 0.05), porch, loc=(0.0, -1.0, 1.02), rot=(math.radians(-14), 0, 0), bevel=0.02,
            parent=root)
    deck = wood("fh_deck", "#C48D58")
    kit.box((1.3, 0.5, 0.06), deck, loc=(0, -0.98, 0.17), bevel=0.015, parent=root)
    kit.box((1.3, 0.04, 0.05), trim, loc=(0, -1.22, 0.55), bevel=0.01, parent=root)
    # chimney with a little moss
    brick = mat("fh_brick", "#B5654A", rough=0.8, edge=0.5, var=0.12, edge_color="#6A3020")
    kit.box((0.26, 0.26, 0.7), brick, loc=(0.65, 0.25, ridge - 0.15), bevel=0.02, parent=root)
    kit.box((0.32, 0.32, 0.06), brick, loc=(0.65, 0.25, ridge + 0.22), bevel=0.02, parent=root)
    moss_tufts([(0.55, 0.3, ridge + 0.2)], rng, parent=root, size=0.05)
    # flower boxes, bench, mailbox, barrel
    box_w = wood("fh_box", "#9C5A32")
    for x in (-0.6, 0.6):
        kit.box((0.36, 0.1, 0.08), box_w, loc=(x, -0.79, 0.34), bevel=0.01, parent=root)
        fl = flowers(kind="rose" if x < 0 else "sun", seed=int(x * 10) + 40, count=5, spread=0.12)
        fl.parent = root
        fl.location = (x, -0.8, 0.36)
        fl.scale = (0.6, 0.6, 0.6)
    bench = wood("fh_bench", "#B07547")
    kit.box((0.5, 0.14, 0.04), bench, loc=(-0.95, -1.05, 0.38), bevel=0.01, parent=root)
    for x in (-1.15, -0.75):
        kit.box((0.04, 0.12, 0.2), bench, loc=(x, -1.05, 0.27), bevel=0.005, parent=root)
    _place(barrel, (1.25, -0.95, 0.0), root, scale=0.85)
    mail = mat("mailbox", "#E8473B", rough=0.35, spec=0.5, edge=0.4)
    kit.cyl(0.03, 0.55, wood("mailpost", "#8C5A34"), loc=(1.45, -1.5, 0), verts=8, parent=root)
    kit.box((0.22, 0.14, 0.14), mail, loc=(1.45, -1.5, 0.6), bevel=0.05, parent=root)
    return root


# ------------------------------------------------------------------ silo

def silo(level=0):
    """Tall red silo with a corrugated metal cap. A glass strip shows the grain inside (level 0..3)."""
    root = kit.empty("silo")
    rng = random.Random(5)
    r, h = 0.48, 2.1
    stone = mat("silo_found", "#A59D8B", rough=0.85, edge=0.55, var=0.07)
    kit.cyl(r + 0.08, 0.16, stone, loc=(0, 0, 0), bevel=0.03, verts=32, parent=root)
    red = mat("silo_red", "#D2493A", rough=0.65, spec=0.2, edge=0.45, var=0.06, edge_color="#7A2A22")
    kit.cyl(r, h, red, loc=(0, 0, 0.16), bevel=0.02, verts=40, parent=root)
    band = mat("silo_band", "#FFF4E2", rough=0.5, spec=0.25, edge=0.4, edge_color="#B9A48A")
    for z in (0.5, 1.2, 1.9):
        kit.torus(r + 0.005, 0.025, band, loc=(0, 0, z), parent=root)
    # cap: metal dome with ribs
    metal = mat("silo_metal", "#A9B3BA", rough=0.35, spec=0.6, metal=0.5, edge=0.4, edge_color="#5A646B")
    kit.sphere(r + 0.03, metal, loc=(0, 0, h + 0.16), scale=(1, 1, 0.65), seg=40, parent=root)
    for i in range(16):  # standing seams on the dome
        a = i * math.tau / 16
        kit.torus(r + 0.03, 0.012, metal, loc=(0, 0, h + 0.16), rot=(0, math.radians(90), a), parent=root,
                  scale=(1.0, 1.0, 0.65))
    kit.sphere(0.06, metal, loc=(0, 0, h + 0.16 + (r + 0.03) * 0.65), seg=12, parent=root)
    # glass strip facing the camera with grain behind it
    face = kit.empty("face", rot=(0, 0, CAM_YAW), parent=root)
    frame = mat("silo_frame", "#FFF4E2", rough=0.5, edge=0.4, edge_color="#B9A48A")
    glass = mat("silo_glass", "#4A5E78", rough=0.1, spec=0.9, edge=0.2, coat=0.6)
    top, bot = 1.95, 0.4
    kit.box((0.22, 0.05, top - bot + 0.06), frame, loc=(0, -r + 0.02, (top + bot) / 2), bevel=0.015, parent=face)
    kit.box((0.16, 0.05, top - bot), glass, loc=(0, -r - 0.0, (top + bot) / 2), bevel=0.01, parent=face)
    fill = [0.0, 0.3, 0.65, 0.97][level]
    if fill > 0:
        grain = mat("silo_grain", "#F2C14E", rough=0.6, spec=0.3, edge=0.35, var=0.15, edge_color="#B07A1A")
        gh = (top - bot) * fill
        kit.box((0.155, 0.05, gh), grain, loc=(0, -r - 0.012, bot + gh / 2), bevel=0.008, parent=face)
    # ladder on the side
    ladder = mat("silo_ladder", "#6E7880", rough=0.4, spec=0.5, metal=0.6, edge=0.4)
    side = kit.empty("side", rot=(0, 0, CAM_YAW + math.radians(65)), parent=root)
    for sx in (-0.07, 0.07):
        kit.cyl(0.012, h - 0.2, ladder, loc=(sx, -r - 0.06, 0.3), verts=8, bevel=0.0, parent=side)
    for i in range(12):
        kit.cyl(0.01, 0.14, ladder, loc=(-0.07, -r - 0.06, 0.4 + i * 0.15), rot=(0, math.radians(90), 0), verts=6,
                bevel=0.0, parent=side)
    for p, b in [((0.62, -0.25, 0), hay_bale), ((-0.55, -0.45, 0), crate)]:
        _place(b, p, root, rot_z=rng.uniform(-0.5, 0.5), scale=0.8)
    return root


# ------------------------------------------------------------------ delivery truck

def truck(yaw_deg=0.0):
    """Little vintage delivery truck: red cab, green flatbed with wooden rails. Front points along +X."""
    root = kit.empty("truck", rot=(0, 0, math.radians(yaw_deg)))
    red = mat("truck_red", "#E0453A", rough=0.3, spec=0.6, coat=0.6, edge=0.45, edge_color="#7A2018")
    green = mat("truck_green", "#3FA54A", rough=0.35, spec=0.5, coat=0.5, edge=0.45, edge_color="#1E5A24")
    black = mat("truck_tyre", "#2E2E33", rough=0.6, spec=0.2, edge=0.3)
    chrome = mat("truck_chrome", "#E8EEF2", rough=0.15, spec=0.9, metal=0.8, edge=0.3)
    glass = mat("truck_glass", "#3B4C66", rough=0.1, spec=0.9, edge=0.2, coat=0.6)
    yellow = mat("truck_lamp", "#FFE27A", rough=0.2, spec=0.7, emit=0.4, edge=0.3)
    plank = wood("truck_plank", "#C48D58")
    # chassis + wheels
    kit.box((1.15, 0.5, 0.08), black, loc=(0.0, 0, 0.2), bevel=0.02, parent=root)
    for x in (-0.35, 0.38):
        for y in (-0.27, 0.27):
            kit.cyl(0.15, 0.1, black, loc=(x, y - 0.05 if y > 0 else y + 0.05, 0.15), rot=(math.radians(90), 0, 0),
                    bevel=0.03, verts=24, parent=root)
            kit.cyl(0.07, 0.11, chrome, loc=(x, y - 0.05 if y > 0 else y + 0.05, 0.15),
                    rot=(math.radians(90), 0, 0), bevel=0.01, verts=16, parent=root)
            kit.sphere(0.17, red, loc=(x, y * 1.02, 0.22), scale=(1.15, 0.45, 0.55), seg=20, parent=root)
    # cab: rounded hood + cabin with a curved roof
    kit.box((0.32, 0.46, 0.26), red, loc=(0.42, 0, 0.36), bevel=0.08, parent=root)
    kit.box((0.06, 0.38, 0.2), chrome, loc=(0.6, 0, 0.36), bevel=0.02, parent=root)
    for y in (-0.15, 0.15):
        kit.sphere(0.05, yellow, loc=(0.6, y, 0.48), seg=14, parent=root)
    kit.box((0.36, 0.5, 0.42), red, loc=(0.12, 0, 0.5), bevel=0.07, parent=root)
    kit.box((0.4, 0.54, 0.06), red, loc=(0.12, 0, 0.74), bevel=0.03, parent=root)
    kit.box((0.02, 0.36, 0.17), glass, loc=(0.305, 0, 0.6), bevel=0.01, parent=root)
    for y in (-0.255, 0.255):
        kit.box((0.22, 0.02, 0.15), glass, loc=(0.12, y, 0.6), bevel=0.01, parent=root)
    # flatbed with rails
    kit.box((0.62, 0.56, 0.08), green, loc=(-0.3, 0, 0.3), bevel=0.02, parent=root)
    for y in (-0.27, 0.27):
        kit.box((0.62, 0.04, 0.16), green, loc=(-0.3, y, 0.42), bevel=0.015, parent=root)
        kit.box((0.6, 0.03, 0.04), plank, loc=(-0.3, y, 0.55), bevel=0.01, parent=root)
        for x in (-0.58, -0.3, -0.02):
            kit.box((0.04, 0.035, 0.22), plank, loc=(x, y, 0.47), bevel=0.008, parent=root)
    kit.box((0.04, 0.56, 0.2), green, loc=(-0.6, 0, 0.42), bevel=0.015, parent=root)
    trim = mat("truck_trim", "#F2C14E", rough=0.35, spec=0.5, edge=0.35)
    for y in (-0.295, 0.295):
        kit.box((0.4, 0.005, 0.08), trim, loc=(-0.3, y, 0.42), bevel=0.0, parent=root)
    return root


def coin_crate():
    """Small crate overflowing with gold coins (waits on the returned truck)."""
    root = kit.empty("coin_crate")
    w = wood("cc_wood", "#C48D58")
    kit.box((0.34, 0.26, 0.18), w, loc=(0, 0, 0.09), bevel=0.02, parent=root)
    gold = mat("cc_gold", "#FFD23F", rough=0.25, spec=0.8, metal=0.4, edge=0.5, edge_color="#B07A1A")
    rng = random.Random(3)
    for i in range(16):
        a = rng.uniform(0, math.tau)
        rr = rng.uniform(0, 0.12)
        kit.cyl(0.05, 0.015, gold, loc=(math.cos(a) * rr, math.sin(a) * rr * 0.7, 0.18 + rng.uniform(0, 0.06)),
                rot=(rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0), bevel=0.005, verts=16, parent=root)
    return root


# ------------------------------------------------------------------ construction site

def site(size=3):
    """Construction site: dirt patch, scaffold poles, a tarp-covered frame, planks, bricks and a barrier."""
    rng = random.Random(size * 7)
    root = kit.empty("site")
    s = 0.42 * size
    dirt = mat("site_dirt", "#B88B5A", rough=0.9, edge=0.4, var=0.1)
    kit.box((s * 1.9, s * 1.9, 0.04), dirt, loc=(0, 0, 0.02), bevel=0.02, parent=root)
    pole = wood("site_pole", "#C9905A")
    tarp = mat("site_tarp", "#4E8FD6", rough=0.6, spec=0.15, edge=0.45, var=0.06, edge_color="#1E4A80")
    hgt = 0.45 * size
    for x in (-s * 0.7, s * 0.7):
        for y in (-s * 0.7, s * 0.7):
            kit.box((0.06, 0.06, hgt), pole, loc=(x, y, hgt / 2), bevel=0.01, parent=root)
    for z in (hgt * 0.45, hgt * 0.95):
        for y in (-s * 0.7, s * 0.7):
            kit.box((s * 1.45, 0.05, 0.05), pole, loc=(0, y, z), bevel=0.01, parent=root)
        for x in (-s * 0.7, s * 0.7):
            kit.box((0.05, s * 1.45, 0.05), pole, loc=(x, 0, z), bevel=0.01, parent=root)
    # tarp draped over the back half, like a tent
    kit.box((s * 1.4, s * 0.7, 0.03), tarp, loc=(0, s * 0.32, hgt * 0.98), rot=(math.radians(8), 0, 0),
            bevel=0.02, parent=root)
    kit.box((s * 1.4, 0.03, hgt * 0.9), tarp, loc=(0, s * 0.7, hgt * 0.5), bevel=0.02, parent=root)
    # planks, brick stack, a barrel and a striped barrier in front
    plank = wood("site_plank", "#D9A066")
    for i in range(4):
        kit.box((s * 0.9, 0.12, 0.035), plank, loc=(-s * 0.2, -s * 0.85 + i * 0.01, 0.05 + i * 0.04),
                rot=(0, 0, rng.uniform(-0.08, 0.08)), bevel=0.008, parent=root)
    brick = mat("site_brick", "#C2603F", rough=0.8, edge=0.5, var=0.12, edge_color="#6A3020")
    for i in range(3):
        for j in range(2):
            kit.box((0.16, 0.08, 0.07), brick, loc=(s * 0.55 + j * 0.17, -s * 0.5, 0.06 + i * 0.075), bevel=0.01,
                    parent=root)
    _place(barrel, (-s * 0.75, -s * 0.2, 0.0), root, scale=0.7)
    stripe = mat("site_stripe", "#FFD23F", rough=0.5, edge=0.4)
    red = mat("site_red", "#E0453A", rough=0.5, edge=0.4)
    yaw = kit.empty("bar", loc=(0.0, -s * 1.05, 0), rot=(0, 0, CAM_YAW * 0 + 0.0), parent=root)
    for x in (-s * 0.45, s * 0.45):
        kit.box((0.05, 0.05, 0.3), pole, loc=(x, 0, 0.15), bevel=0.01, parent=yaw)
    for i in range(6):
        kit.box((s * 0.9 / 6, 0.04, 0.08), stripe if i % 2 == 0 else red, loc=(-s * 0.45 + (i + 0.5) * s * 0.15, 0,
                0.27), bevel=0.005, parent=yaw)
    # hammer + sign
    _place(crate, (s * 0.7, s * 0.1, 0.0), root, rot_z=0.3, scale=0.7)
    return root


# ------------------------------------------------------------------ land sign

def sign_parcel():
    """Wooden sign with a rolled-up map and two boundary stakes with rope: 'this land can be bought'."""
    root = kit.empty("sign_parcel")
    post = wood("sp_post", "#8C5A34")
    board = mat("sp_board", "#FFD966", rough=0.5, spec=0.25, edge=0.5, edge_color="#9A6A1A")
    kit.box((0.09, 0.09, 1.0), post, loc=(0, 0, 0.5), bevel=0.02, parent=root)
    b = kit.empty("b", rot=(0, 0, CAM_YAW), parent=root)
    kit.box((0.62, 0.06, 0.42), board, loc=(0, -0.06, 0.85), bevel=0.04, parent=b)
    paper = mat("sp_map", "#F6EBCF", rough=0.7, edge=0.4, edge_color="#A08A5A")
    kit.box((0.36, 0.02, 0.24), paper, loc=(0, -0.1, 0.86), bevel=0.01, parent=b)
    ink = mat("sp_ink", "#4FA65A", rough=0.6, edge=0.3)
    kit.box((0.14, 0.01, 0.1), ink, loc=(-0.05, -0.115, 0.88), bevel=0.01, parent=b)
    red = mat("sp_x", "#E0453A", rough=0.5, edge=0.3)
    kit.box((0.06, 0.01, 0.015), red, loc=(0.08, -0.116, 0.83), rot=(0, 0.7, 0), bevel=0.0, parent=b)
    kit.box((0.06, 0.01, 0.015), red, loc=(0.08, -0.116, 0.83), rot=(0, -0.7, 0), bevel=0.0, parent=b)
    flowers(kind="white", seed=12, count=5, spread=0.14).parent = root
    root.children[-1].location = (0.2, 0.05, 0)
    root.scale = (1.25, 1.25, 1.25)
    return root


def progress_frames():
    return {
        "farmhouse": farmhouse,
        "silo_0": lambda: silo(0),
        "silo_1": lambda: silo(1),
        "silo_2": lambda: silo(2),
        "silo_3": lambda: silo(3),
        "truck_se": lambda: truck(0.0),
        "truck_ne": lambda: truck(90.0),
        "truck_sw": lambda: truck(-90.0),
        "coin_crate": coin_crate,
        "site_big": lambda: site(3),
        "site_small": lambda: site(2),
        "sign_parcel": sign_parcel,
    }
