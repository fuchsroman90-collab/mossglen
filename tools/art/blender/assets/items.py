"""3D item icons (Roman: icons must look like rendered objects, see brain/references/img/hd_item_icons_3d.png).

Every frame is named "uiitem_<id>"; build.py exports them to game/art/generated/ui/item_<id>.png
(outlined, fitted into a square) instead of packing them into the world atlas.
"""
from __future__ import annotations

import math
import random

from mathutils import Vector

from .. import kit
from ..kit import mat

SIZE = 1.5  # every icon is scaled so its largest side is this many units


def _norm(root):
    """Scale the icon so all icons come out the same size."""
    import bpy
    bpy.context.view_layer.update()
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in root.children_recursive:
        if o.type not in {"MESH", "META", "CURVE"}:
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    k = SIZE / max(hi - lo)
    root.scale = root.scale * k
    return root


def _root(name, yaw=0.0, tilt=0.0):
    return kit.empty(name, rot=(math.radians(tilt), 0, math.radians(yaw)))


def _lean(name, k=0.75, yaw=0.0):
    """Root whose +Z leans towards the camera (k = 1: faces it), for flat things like maps and coils."""
    d = (Vector((0, 0, 1)) * (1.0 - k) + kit.TO_CAM.normalized() * k).normalized()
    root = kit.empty(name)
    q = d.to_track_quat("Z", "Y")
    root.rotation_mode = "QUATERNION"
    from mathutils import Quaternion
    root.rotation_quaternion = q @ Quaternion((0, 0, 1), math.radians(yaw))
    return root


def _front(root, z=0.0):
    """Child empty whose local -Y faces the camera (for labels)."""
    yaw = math.atan2(kit.TO_CAM.y, kit.TO_CAM.x) + math.pi / 2
    return kit.empty("front", loc=(0, 0, z), rot=(0, 0, yaw), parent=root)


def _wood(name, c):
    return mat(name, c, rough=0.7, spec=0.15, edge=0.5, var=0.06)


def _metal(name="steel", c="#C9D3DA"):
    return mat(name, c, rough=0.25, spec=0.7, metal=0.7, edge=0.4, edge_color="#5A646B")


def _glossy(name, c, edge_c=None):
    return mat(name, c, rough=0.3, spec=0.55, coat=0.4, edge=0.45, edge_color=edge_c)


# ------------------------------------------------------------------ crops

def wheat():
    root = _root("wheat", yaw=20)
    stalk = mat("w_stalk", "#E8B53A", rough=0.6, edge=0.4)
    ear = mat("w_ear", "#FFD24A", rough=0.5, spec=0.3, edge=0.45, edge_color="#B07A1A", var=0.08)
    band = mat("w_band", "#B36A2E", rough=0.6, edge=0.4)
    rng = random.Random(1)
    for i in range(7):
        a = (i - 3) * 0.13
        st = kit.empty("st", rot=(0, a, rng.uniform(-0.3, 0.3)), parent=root)
        kit.cyl(0.018, 0.9, stalk, loc=(0, 0, 0), verts=8, bevel=0.0, parent=st)
        for j in range(5):
            for sd in (-1, 1):
                kit.sphere(0.045, ear, loc=(sd * 0.028, 0, 0.72 + j * 0.06), scale=(0.7, 0.7, 1.4),
                           rot=(0, sd * 0.4, 0), seg=10, parent=st)
    kit.cyl(0.11, 0.1, band, loc=(0, 0, 0.3), verts=20, bevel=0.02, parent=root)
    return _norm(root)


def corn():
    root = _root("corn", yaw=-30, tilt=60)
    kern = mat("c_kern", "#FFD23F", rough=0.35, spec=0.4, edge=0.45, edge_color="#C08A10", var=0.06)
    husk = mat("c_husk", "#8CCB5A", rough=0.55, spec=0.2, edge=0.45, edge_color="#3E7A24")
    kit.sphere(0.18, kern, loc=(0, 0, 0.45), scale=(1, 1, 2.6), seg=24, parent=root)
    for i in range(12):
        a = i * math.tau / 12
        for k in range(6):
            kit.sphere(0.045, kern, loc=(math.cos(a) * 0.15, math.sin(a) * 0.15, 0.12 + k * 0.11), seg=8,
                       parent=root)
    for i, a in enumerate((0.0, 2.1, 4.2)):
        leaf = kit.empty("h", rot=(0.35, 0, a), parent=root)
        kit.sphere(0.13, husk, loc=(0.12, 0, 0.25), scale=(0.35, 1.0, 2.6), seg=16, parent=leaf)
    return _norm(root)


def carrot():
    root = _root("carrot", yaw=10, tilt=70)
    orange = mat("ca_or", "#F07A2A", rough=0.45, spec=0.35, edge=0.45, edge_color="#A0400C")
    green = mat("ca_gr", "#5DB33C", rough=0.55, edge=0.4)
    kit.cyl(0.16, 0.8, orange, r2=0.02, loc=(0, 0, -0.8), rot=(0, 0, 0), verts=24, bevel=0.03, parent=root)
    root.children[-1].rotation_euler = (math.pi, 0, 0)
    root.children[-1].location = (0, 0, 0)
    for k in range(5):
        kit.torus(0.13 - k * 0.022, 0.008, mat("ca_ring", "#D9621E", rough=0.5), loc=(0, 0, -0.12 - k * 0.13),
                  parent=root)
    for a in (-0.4, 0.0, 0.4):
        kit.cyl(0.03, 0.4, green, r2=0.01, loc=(0, 0, 0.0), rot=(a, 0.2 * a, 0), verts=8, bevel=0.0, parent=root)
    return _norm(root)


def tomato():
    root = _root("tomato")
    red = _glossy("to_red", "#E8402E", "#8A1A10")
    green = mat("to_gr", "#4FA03A", rough=0.5, edge=0.4)
    kit.sphere(0.42, red, loc=(0, 0, 0.36), scale=(1, 1, 0.85), seg=32, parent=root)
    for i in range(5):
        a = i * math.tau / 5
        kit.sphere(0.09, green, loc=(math.cos(a) * 0.1, math.sin(a) * 0.1, 0.71), scale=(1.8, 0.6, 0.3),
                   rot=(0, 0, a), seg=12, parent=root)
    kit.cyl(0.025, 0.12, green, loc=(0, 0, 0.7), verts=8, parent=root)
    return _norm(root)


def strawberry():
    root = _root("strawberry", tilt=-10)
    red = _glossy("sb_red", "#E8384A", "#8A1020")
    seed = mat("sb_seed", "#FFE07A", rough=0.4, spec=0.4)
    green = mat("sb_gr", "#4FA03A", rough=0.5, edge=0.4)
    kit.sphere(0.38, red, loc=(0, 0, 0.45), scale=(1, 1, 1.15), seg=32, parent=root)
    kit.cyl(0.3, 0.45, red, r2=0.04, loc=(0, 0, 0.05), verts=32, bevel=0.1, parent=root)
    root.children[-1].rotation_euler = (math.pi, 0, 0)
    root.children[-1].location = (0, 0, 0.42)
    rng = random.Random(4)
    for i in range(26):
        a = rng.uniform(0, math.tau)
        z = rng.uniform(0.05, 0.75)
        r = 0.38 * min(1.0, 0.25 + z * 1.4) if z < 0.45 else 0.38 * math.sqrt(max(0.0, 1 - ((z - 0.45) / 0.44) ** 2))
        kit.sphere(0.022, seed, loc=(math.cos(a) * r, math.sin(a) * r, z), scale=(1, 1, 1.4), seg=6, parent=root)
    for i in range(6):
        a = i * math.tau / 6
        kit.sphere(0.1, green, loc=(math.cos(a) * 0.14, math.sin(a) * 0.14, 0.88), scale=(1.8, 0.6, 0.25),
                   rot=(0, 0, a), seg=12, parent=root)
    return _norm(root)


def fern():
    root = _root("fern", yaw=15)
    green = mat("fe_gr", "#4FB050", rough=0.5, spec=0.2, edge=0.45, edge_color="#1E5A24", var=0.08)
    for i, a in enumerate((-0.6, -0.2, 0.2, 0.6)):
        fr = kit.empty("f", rot=(0, a, i * 0.4), parent=root)
        kit.cyl(0.012, 0.85, green, verts=6, bevel=0.0, parent=fr)
        for k in range(8):
            for sd in (-1, 1):
                L = 0.16 * (1.0 - k / 10)
                kit.sphere(L, green, loc=(sd * L * 0.9, 0, 0.12 + k * 0.09), scale=(1.0, 0.25, 0.28),
                           rot=(0, sd * -0.4, 0), seg=10, parent=fr)
    return _norm(root)


# ------------------------------------------------------------------ goods

def sack(label="#FFCF3A", grain="#F2B21E"):
    root = _root("sack")
    cloth = mat("sk_cloth", "#E8D3A8", rough=0.85, edge=0.5, var=0.04, edge_color="#9A7A4A")
    lab = mat("sk_lab_" + label, label, rough=0.6, edge=0.4)
    gr = mat("sk_gr_" + grain, grain, rough=0.6, spec=0.2, edge=0.4, var=0.1)
    kit.sphere(0.42, cloth, loc=(0, 0, 0.42), scale=(1, 0.85, 1.05), seg=32, parent=root)
    kit.cyl(0.32, 0.12, cloth, loc=(0, 0, 0.78), verts=24, bevel=0.04, parent=root)
    kit.torus(0.3, 0.035, mat("sk_rope", "#B9925A", rough=0.8), loc=(0, 0, 0.82), parent=root)
    kit.sphere(0.27, gr, loc=(0, 0, 0.9), scale=(1, 1, 0.35), seg=20, parent=root)
    kit.box((0.46, 0.06, 0.26), lab, loc=(0, -0.36, 0.42), rot=(0.12, 0, 0), bevel=0.05, parent=_front(root))
    return _norm(root)


def egg(color="#FFF4E2", spot=None, big=False):
    root = _root("egg", tilt=-14)
    shell = _glossy("egg_" + color, color, "#9A7A4A")
    kit.sphere(0.36, shell, loc=(0, 0, 0.45), scale=(0.82, 0.82, 1.1), seg=32, parent=root)
    if spot:
        sp = mat("egg_sp_" + spot, spot, rough=0.4, spec=0.3)
        rng = random.Random(len(color) + len(spot))
        for i in range(10 if big else 7):
            a = rng.uniform(-1.4, 1.4) - math.pi / 2
            z = rng.uniform(0.2, 0.75)
            r = 0.295 * math.sqrt(max(0.0, 1 - ((z - 0.45) / 0.4) ** 2))
            kit.sphere(rng.uniform(0.035, 0.06), sp, loc=(math.cos(a) * r, math.sin(a) * r, z), scale=(1, 0.4, 1),
                       rot=(0, 0, a), seg=10, parent=root)
    if big:
        nest = mat("egg_straw", "#E8C26A", rough=0.8, var=0.1)
        kit.torus(0.3, 0.08, nest, loc=(0, 0, 0.12), parent=root, scale=(1, 1, 0.6))
    return _norm(root)


def jar(fill, lid="#E8473B"):
    root = _root("jar")
    glass = mat("jar_glass", "#EAF4F7", rough=0.08, spec=0.8, edge=0.3, coat=0.6)
    f = _glossy("jar_f_" + fill, fill)
    kit.cyl(0.3, 0.55, f, loc=(0, 0, 0.02), verts=32, bevel=0.06, parent=root)
    kit.cyl(0.33, 0.6, glass, loc=(0, 0, 0.0), verts=32, bevel=0.08, parent=root)
    root.children[-1].hide_render = True  # opaque look: just the filled jar with a rim
    kit.cyl(0.34, 0.14, _glossy("jar_lid_" + lid, lid), loc=(0, 0, 0.56), verts=32, bevel=0.04, parent=root)
    kit.box((0.36, 0.04, 0.22), mat("jar_lab", "#FFF6E6", rough=0.6, edge=0.4), loc=(0, -0.29, 0.28),
            bevel=0.03, parent=_front(root))
    cloth = mat("jar_cloth", "#FFFFFF", rough=0.7, edge=0.4)
    kit.sphere(0.36, cloth, loc=(0, 0, 0.69), scale=(1, 1, 0.18), seg=20, parent=root)
    return _norm(root)


def bottle(color="#D9301E", cap="#5DB33C"):
    root = _root("bottle")
    g = _glossy("bt_" + color, color)
    kit.cyl(0.24, 0.55, g, loc=(0, 0, 0), verts=32, bevel=0.1, parent=root)
    kit.cyl(0.24, 0.3, g, r2=0.1, loc=(0, 0, 0.5), verts=32, bevel=0.0, parent=root)
    kit.cyl(0.1, 0.18, g, loc=(0, 0, 0.78), verts=24, bevel=0.03, parent=root)
    kit.cyl(0.12, 0.1, _glossy("bt_cap_" + cap, cap), loc=(0, 0, 0.94), verts=24, bevel=0.03, parent=root)
    kit.box((0.34, 0.04, 0.2), mat("bt_lab", "#FFF6E6", rough=0.6, edge=0.4), loc=(0, -0.235, 0.26),
            bevel=0.03, parent=_front(root))
    return _norm(root)


def milk():
    root = _root("milk")
    glass = _glossy("mk_glass", "#FFFFFF", "#9AAAB8")
    kit.cyl(0.25, 0.6, glass, loc=(0, 0, 0), verts=32, bevel=0.08, parent=root)
    kit.cyl(0.25, 0.25, glass, r2=0.13, loc=(0, 0, 0.55), verts=32, bevel=0.0, parent=root)
    kit.cyl(0.14, 0.08, _glossy("mk_cap", "#4E8FD6"), loc=(0, 0, 0.8), verts=24, bevel=0.03, parent=root)
    kit.box((0.36, 0.04, 0.16), mat("mk_lab", "#4E8FD6", rough=0.5, edge=0.4), loc=(0, -0.245, 0.3), bevel=0.03,
            parent=_front(root))
    return _norm(root)


def bread(color="#D9963E", top="#B5652A", square=False):
    root = _root("bread", yaw=25)
    crust = mat("br_" + color, color, rough=0.6, spec=0.25, edge=0.5, var=0.05, edge_color="#7A3A10")
    dark = mat("br_top_" + top, top, rough=0.55, spec=0.3, edge=0.5)
    if square:
        kit.box((0.8, 0.55, 0.42), crust, loc=(0, 0, 0.21), bevel=0.12, parent=root)
        kit.box((0.72, 0.48, 0.06), dark, loc=(0, 0, 0.43), bevel=0.03, parent=root)
    else:
        kit.sphere(0.45, crust, loc=(0, 0, 0.25), scale=(1.3, 0.85, 0.7), seg=32, parent=root)
        for x in (-0.25, 0.0, 0.25):
            kit.box((0.06, 0.4, 0.03), dark, loc=(x, 0, 0.55), rot=(0, 0.25, 0.4), bevel=0.02, parent=root)
    return _norm(root)


def cake(cream="#FFF4E2", deco="#F07A2A", layers="#E8B06A"):
    root = _root("cake", yaw=-20)
    plate = mat("ck_plate", "#FFFFFF", rough=0.3, spec=0.4, edge=0.3)
    kit.cyl(0.55, 0.05, plate, loc=(0, 0, 0), verts=32, bevel=0.02, parent=root)
    kit.cyl(0.42, 0.35, mat("ck_l_" + layers, layers, rough=0.6, edge=0.45), loc=(0, 0, 0.05), verts=32,
            bevel=0.05, parent=root)
    kit.cyl(0.43, 0.08, _glossy("ck_c_" + cream, cream), loc=(0, 0, 0.38), verts=32, bevel=0.04, parent=root)
    d = _glossy("ck_d_" + deco, deco)
    for i in range(6):
        a = i * math.tau / 6
        kit.sphere(0.07, d, loc=(math.cos(a) * 0.28, math.sin(a) * 0.28, 0.5), scale=(1, 1, 1.4), seg=12,
                   parent=root)
    return _norm(root)


def pancakes():
    root = _root("pancakes", yaw=-20)
    plate = mat("pk_plate", "#FFFFFF", rough=0.3, spec=0.4, edge=0.3)
    cake_m = mat("pk_cake", "#E8A85A", rough=0.55, spec=0.25, edge=0.5, edge_color="#8A4A1A")
    syrup = _glossy("pk_syrup", "#B5652A")
    kit.cyl(0.55, 0.05, plate, loc=(0, 0, 0), verts=32, bevel=0.02, parent=root)
    for i in range(5):
        kit.cyl(0.4 - i * 0.01, 0.09, cake_m, loc=(0, 0, 0.05 + i * 0.09), verts=32, bevel=0.035, parent=root)
    kit.cyl(0.36, 0.04, syrup, loc=(0, 0, 0.5), verts=32, bevel=0.02, parent=root)
    kit.box((0.18, 0.14, 0.1), mat("pk_butter", "#FFE680", rough=0.4, spec=0.3, edge=0.4), loc=(0, 0, 0.58),
            bevel=0.03, parent=root)
    return _norm(root)


def cheese():
    root = _root("cheese", yaw=30)
    c = mat("ch_c", "#FFD45A", rough=0.45, spec=0.3, edge=0.5, edge_color="#B07A10")
    import bmesh
    import bpy
    bm = bmesh.new()
    pts = [(0, 0), (0.9, -0.25), (0.9, 0.25)]
    lo = [bm.verts.new((x - 0.4, y, 0)) for x, y in pts]
    hi = [bm.verts.new((x - 0.4, y, 0.45)) for x, y in pts]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    me = bpy.data.meshes.new("cheese")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("cheese", me)
    kit.link(o)
    kit.set_mat(o, c)
    o.parent = root
    bev = o.modifiers.new("b", "BEVEL")
    bev.width = 0.04
    bev.segments = 3
    hole = mat("ch_h", "#E8B02A", rough=0.5)
    for p in [(0.25, -0.2, 0.25), (0.35, 0.1, 0.46), (0.1, -0.09, 0.3), (0.42, -0.24, 0.12)]:
        kit.sphere(0.06, hole, loc=p, scale=(1, 0.5, 1), seg=12, parent=root)
    return _norm(root)


def butter():
    root = _root("butter", yaw=-25)
    plate = mat("bu_plate", "#E8F0F4", rough=0.3, spec=0.4, edge=0.3)
    kit.cyl(0.55, 0.05, plate, loc=(0, 0, 0), verts=32, bevel=0.02, parent=root, scale=(1.2, 0.85, 1))
    kit.box((0.7, 0.4, 0.3), mat("bu_b", "#FFE680", rough=0.35, spec=0.35, edge=0.45, edge_color="#C0A030"),
            loc=(0, 0, 0.2), bevel=0.05, parent=root)
    return _norm(root)


def cream():
    root = _root("cream", yaw=-15)
    bowl = _glossy("cr_bowl", "#8EC8EE", "#2A6A9A")
    kit.cyl(0.42, 0.35, bowl, r2=0.3, loc=(0, 0, 0.35), verts=32, bevel=0.03, parent=root)
    root.children[-1].rotation_euler = (math.pi, 0, 0)
    kit.sphere(0.4, mat("cr_c", "#FFFDF4", rough=0.35, spec=0.3, edge=0.35), loc=(0, 0, 0.36),
               scale=(1, 1, 0.45), seg=24, parent=root)
    kit.cyl(0.08, 0.15, mat("cr_tip", "#FFFDF4", rough=0.35), r2=0.0, loc=(0, 0, 0.5), verts=16, parent=root)
    return _norm(root)


def wool():
    root = _root("wool")
    w = mat("wo_w", "#FFFDF6", rough=0.8, spec=0.1, edge=0.45, edge_color="#B8AE98")
    rng = random.Random(3)
    for i in range(14):
        a = rng.uniform(0, math.tau)
        z = rng.uniform(0.2, 0.7)
        kit.sphere(rng.uniform(0.18, 0.26), w, loc=(math.cos(a) * 0.25, math.sin(a) * 0.25, z), seg=16,
                   parent=root)
    return _norm(root)


def truffle():
    root = _root("truffle")
    t = mat("tr_t", "#5A3A2A", rough=0.75, spec=0.15, edge=0.45, edge_color="#2A1A10", var=0.05)
    rng = random.Random(7)
    kit.sphere(0.4, t, loc=(0, 0, 0.35), scale=(1.1, 1, 0.85), seg=24, parent=root)
    for i in range(18):
        a = rng.uniform(0, math.tau)
        z = rng.uniform(0.15, 0.6)
        kit.sphere(rng.uniform(0.07, 0.12), t, loc=(math.cos(a) * 0.36, math.sin(a) * 0.32, z), seg=10,
                   parent=root)
    return _norm(root)


def honey_pot():
    root = _root("honey", yaw=-15)
    pot = _glossy("hp_pot", "#F2B02A", "#8A5A10")
    kit.sphere(0.4, pot, loc=(0, 0, 0.38), scale=(1, 1, 0.95), seg=32, parent=root)
    kit.cyl(0.25, 0.12, pot, loc=(0, 0, 0.72), verts=32, bevel=0.03, parent=root)
    kit.cyl(0.28, 0.07, _glossy("hp_lid", "#C98C2A"), loc=(0, 0, 0.82), verts=32, bevel=0.03, parent=root)
    for z in (0.3, 0.5):
        kit.torus(0.39, 0.025, _glossy("hp_band", "#E8902A"), loc=(0, 0, z), parent=root)
    drip = _glossy("hp_drip", "#FFC93C")
    kit.sphere(0.06, drip, loc=(0.1, -0.33, 0.62), scale=(1, 0.6, 1.6), seg=10, parent=root)
    return _norm(root)


def fabric(c="#E86A8A", stripe="#FFFFFF"):
    root = _root("cloth", yaw=-25)
    m = mat("fa_" + c, c, rough=0.75, spec=0.1, edge=0.5, var=0.05)
    s = mat("fa_s_" + stripe, stripe, rough=0.75, edge=0.4)
    for i in range(3):
        kit.box((0.8, 0.55, 0.12), m, loc=(0, 0, 0.07 + i * 0.13), rot=(0, 0, (i - 1) * 0.07), bevel=0.05,
                parent=root)
        kit.box((0.82, 0.06, 0.13), s, loc=(0, -0.12, 0.07 + i * 0.13), rot=(0, 0, (i - 1) * 0.07), bevel=0.02,
                parent=root)
    return _norm(root)


def scarf():
    root = _lean("scarf", 0.35, yaw=20)
    a = mat("sc_a", "#E8473B", rough=0.75, edge=0.5, edge_color="#7A1A10")
    b = mat("sc_b", "#FFF4E2", rough=0.75, edge=0.4)
    kit.torus(0.3, 0.13, a, loc=(0, 0, 0.2), parent=root, scale=(1, 0.85, 0.9))
    for i, x in enumerate((-0.1, 0.12)):
        end = kit.empty("e", loc=(x, -0.2, 0.15), rot=(0.25, 0, (i - 0.5) * 0.4), parent=root)
        for k in range(4):
            kit.box((0.2, 0.06, 0.1), a if k % 2 == 0 else b, loc=(0, -0.05 * k, -0.1 * k), bevel=0.025, parent=end)
        for f in range(4):
            kit.box((0.025, 0.02, 0.1), b, loc=(-0.075 + f * 0.05, -0.2, -0.45), bevel=0.005, parent=end)
    return _norm(root)


def popcorn(butter_=False):
    root = _root("popcorn", yaw=-15)
    red = _glossy("pc_red", "#E8473B")
    white = _glossy("pc_white", "#FFFDF4")
    for i in range(12):
        a = i * math.tau / 12
        st = kit.empty("s", rot=(0, 0, a), parent=root)
        kit.box((0.2, 0.06, 0.7), red if i % 2 == 0 else white, loc=(0.3, 0, 0.35), rot=(0, -0.14, 0),
                bevel=0.012, parent=st)
    kit.cyl(0.26, 0.68, red, r2=0.34, loc=(0, 0, 0.01), verts=24, bevel=0.0, parent=root)
    pop = mat("pc_pop", "#FFE680" if butter_ else "#FFFAE8", rough=0.6, spec=0.2, edge=0.45, edge_color="#B89A50")
    rng = random.Random(5)
    for i in range(22):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 0.32)
        kit.sphere(rng.uniform(0.08, 0.11), pop, loc=(math.cos(a) * r, math.sin(a) * r, 0.72 + rng.uniform(0, 0.18)),
                   seg=10, parent=root)
    return _norm(root)


def candle(c="#FFF4E2", band=None):
    root = _root("candle", yaw=-15)
    wax = mat("cd_" + c, c, rough=0.4, spec=0.3, edge=0.4, sss=0.2)
    kit.cyl(0.22, 0.75, wax, loc=(0, 0, 0), verts=32, bevel=0.04, parent=root)
    kit.sphere(0.05, wax, loc=(0.18, -0.12, 0.66), scale=(1, 1, 2.0), seg=10, parent=root)
    kit.cyl(0.012, 0.1, mat("cd_wick", "#3A2A20"), loc=(0, 0, 0.75), verts=6, parent=root)
    kit.sphere(0.07, mat("cd_flame", "#FFC93C", emit=1.5, rough=0.2), loc=(0, 0, 0.92), scale=(1, 1, 1.8), seg=12,
               parent=root)
    if band:
        kit.torus(0.225, 0.04, _glossy("cd_band_" + band, band), loc=(0, 0, 0.3), parent=root)
    kit.cyl(0.32, 0.06, _metal("cd_dish", "#F2C14E"), loc=(0, 0, -0.04), verts=32, bevel=0.02, parent=root)
    return _norm(root)


def fossil():
    root = _root("fossil", yaw=-20)
    stone = mat("fo_stone", "#C9B99A", rough=0.85, edge=0.5, var=0.06, edge_color="#7A6A4A")
    bone = mat("fo_bone", "#FFF6E0", rough=0.5, spec=0.3, edge=0.45, edge_color="#9A8A6A")
    kit.sphere(0.5, stone, loc=(0, 0, 0.15), scale=(1.2, 1.0, 0.4), seg=24, parent=root)
    kit.cyl(0.05, 0.7, bone, loc=(-0.35, 0, 0.32), rot=(0, math.radians(90), 0.3), verts=12, parent=root)
    for x in (-0.35, 0.33):
        for y in (-0.05, 0.05):
            kit.sphere(0.075, bone, loc=(x, y + (x * 0.3), 0.33), seg=12, parent=root)
    return _norm(root)


def amber():
    root = _root("amber", yaw=10)
    a = mat("am_a", "#F29A2A", rough=0.08, spec=0.9, coat=0.8, edge=0.4, edge_color="#8A4A0A", sss=0.4)
    kit.ico(0.42, a, loc=(0, 0, 0.35), scale=(1.1, 0.9, 0.85), sub=1, parent=root, smooth=False)
    kit.sphere(0.06, mat("am_bug", "#4A2A1A", rough=0.5), loc=(0.05, -0.2, 0.4), scale=(1.6, 1, 0.8), seg=10,
               parent=root)
    return _norm(root)


# ------------------------------------------------------------------ tools and materials

def axe():
    root = _root("axe", yaw=20, tilt=-55)
    kit.cyl(0.045, 1.1, _wood("ax_h", "#C48D58"), loc=(0, 0, -0.55), verts=12, bevel=0.02, parent=root)
    head = _metal("ax_m")
    kit.box((0.22, 0.14, 0.22), head, loc=(0.06, 0, 0.47), bevel=0.04, parent=root)
    kit.box((0.26, 0.07, 0.42), head, loc=(0.26, 0, 0.47), bevel=0.03, parent=root)
    kit.box((0.05, 0.075, 0.44), _metal("ax_edge", "#F4F8FB"), loc=(0.39, 0, 0.47), bevel=0.02, parent=root)
    return _norm(root)


def saw():
    root = _root("saw", yaw=-30, tilt=-60)
    kit.box((0.9, 0.025, 0.28), _metal("sw_m"), loc=(0.25, 0, 0), bevel=0.01, parent=root)
    tooth = _metal("sw_t", "#AEB8BF")
    for i in range(12):
        kit.cyl(0.04, 0.06, tooth, r2=0.0, loc=(-0.15 + i * 0.075, 0, -0.17), rot=(math.pi, 0, 0), verts=4,
                bevel=0.0, parent=root)
    h = _glossy("sw_h", "#E0453A")
    kit.box((0.3, 0.07, 0.36), h, loc=(-0.32, 0, 0.04), bevel=0.06, parent=root)
    kit.box((0.14, 0.09, 0.14), mat("sw_hole", "#3A1A10"), loc=(-0.32, 0, 0.07), bevel=0.04, parent=root)
    return _norm(root)


def shovel():
    root = _root("shovel", yaw=10, tilt=-50)
    kit.cyl(0.04, 1.0, _wood("sh_h", "#C48D58"), loc=(0, 0, 0.0), verts=12, bevel=0.02, parent=root)
    kit.box((0.28, 0.06, 0.06), _wood("sh_grip", "#B07547"), loc=(0, 0, 1.0), bevel=0.02, parent=root)
    blade = _metal("sh_b")
    kit.sphere(0.2, blade, loc=(0, 0, -0.12), scale=(1.0, 0.18, 1.4), seg=24, parent=root)
    return _norm(root)


def dynamite():
    root = _root("dynamite", yaw=-20)
    red = _glossy("dy_r", "#E0453A", "#7A1A10")
    for x, y in [(-0.17, 0), (0.0, 0.05), (0.17, 0), (-0.08, -0.15), (0.09, -0.15)]:
        kit.cyl(0.11, 0.8, red, loc=(x, y, 0), verts=24, bevel=0.03, parent=root)
    for z in (0.2, 0.6):
        kit.torus(0.27, 0.035, mat("dy_band", "#F2C14E", rough=0.5), loc=(0, -0.05, z), parent=root,
                  scale=(1, 0.75, 1))
    kit.curve_tube([(0, 0.05, 0.8), (0.05, 0.05, 0.95), (0.18, 0.05, 1.02)], r=0.02,
                   m=mat("dy_fuse", "#E2C48A", rough=0.8), parent=root)
    kit.sphere(0.06, mat("dy_spark", "#FFD23F", emit=2.0), loc=(0.2, 0.05, 1.03), seg=10, parent=root)
    return _norm(root)


def stake():
    root = _root("stake", yaw=15, tilt=-20)
    w = _wood("st_w", "#C48D58")
    kit.box((0.16, 0.16, 0.9), w, loc=(0, 0, 0.45), bevel=0.02, parent=root)
    kit.cyl(0.11, 0.25, w, r2=0.0, loc=(0, 0, 0.0), rot=(math.pi, 0, 0), verts=4, bevel=0.0, parent=root)
    root.children[-1].rotation_euler = (math.pi, 0, math.pi / 4)
    kit.box((0.18, 0.18, 0.14), _glossy("st_red", "#E0453A"), loc=(0, 0, 0.82), bevel=0.03, parent=root)
    flag = mat("st_flag", "#FFD23F", rough=0.6, edge=0.4)
    kit.box((0.3, 0.02, 0.18), flag, loc=(0.18, 0, 0.75), bevel=0.01, parent=root)
    return _norm(root)


def land_map():
    root = _lean("land_map", 0.7, yaw=-10)
    paper = mat("lm_p", "#F6EBCF", rough=0.7, edge=0.45, edge_color="#A08A5A")
    kit.box((0.9, 0.62, 0.02), paper, loc=(0, 0, 0), bevel=0.01, parent=root)
    for x in (-0.47, 0.47):
        kit.cyl(0.06, 0.66, paper, loc=(x, -0.33, 0.03), rot=(-math.pi / 2, 0, 0), verts=16, bevel=0.01, parent=root)
    green = mat("lm_g", "#7FCF6E", rough=0.6)
    kit.sphere(0.18, green, loc=(-0.15, 0.05, 0.015), scale=(1.3, 1, 0.05), seg=16, parent=root)
    kit.sphere(0.12, mat("lm_b", "#7FC0E8", rough=0.5), loc=(0.2, -0.1, 0.016), scale=(1.4, 1, 0.05), seg=16,
               parent=root)
    red = mat("lm_x", "#E0453A", rough=0.5)
    for r in (0.7, -0.7):
        kit.box((0.14, 0.03, 0.02), red, loc=(0.25, 0.15, 0.02), rot=(0, 0, r), bevel=0.0, parent=root)
    return _norm(root)


def tape():
    root = _lean("tape", 0.85)
    kit.cyl(0.4, 0.2, _glossy("tp_case", "#FFD23F", "#8A6A10"), loc=(0, 0, 0), verts=32, bevel=0.05, parent=root)
    kit.cyl(0.14, 0.22, _metal("tp_hub", "#AEB8BF"), loc=(0, 0, -0.01), verts=24, bevel=0.02, parent=root)
    kit.box((0.5, 0.12, 0.02), mat("tp_band", "#FFF4E2", rough=0.5, edge=0.4), loc=(0.6, -0.25, 0.1), bevel=0.0,
            parent=root)
    return _norm(root)


def bolt():
    root = _root("rivet", yaw=20, tilt=-65)
    m = _metal("bo_m")
    kit.cyl(0.3, 0.2, m, loc=(0, 0, 0.5), verts=6, bevel=0.03, parent=root)
    kit.cyl(0.14, 0.55, m, loc=(0, 0, 0.0), verts=16, bevel=0.02, parent=root)
    for k in range(6):
        kit.torus(0.14, 0.02, m, loc=(0, 0, 0.05 + k * 0.08), parent=root)
    return _norm(root)


def planks():
    root = _root("plank", yaw=-25)
    for i, c in enumerate(("#C48D58", "#D9A066", "#B07547")):
        kit.box((1.1, 0.24, 0.08), _wood("pl_" + c, c), loc=(0, (i - 1) * 0.06, 0.04 + i * 0.09),
                rot=(0, 0, (i - 1) * 0.15), bevel=0.02, parent=root)
    return _norm(root)


def rope():
    root = _lean("rope", 0.7)
    r = mat("ro_r", "#E2C48A", rough=0.85, edge=0.45, edge_color="#8A6A3A", var=0.05)
    for i in range(4):
        kit.torus(0.38 - i * 0.07, 0.07, r, loc=(0, 0, i * 0.02), parent=root)
    kit.curve_tube([(0.38, 0, 0), (0.55, -0.15, -0.05), (0.6, -0.4, -0.08)], r=0.06, m=r, parent=root)
    return _norm(root)


def nail():
    root = _root("nail", yaw=20, tilt=-40)
    m = _metal("na_m")
    kit.cyl(0.075, 0.8, m, loc=(0, 0, 0.0), verts=16, bevel=0.01, parent=root)
    kit.cyl(0.22, 0.07, m, loc=(0, 0, 0.8), verts=24, bevel=0.025, parent=root)
    tip = kit.cyl(0.075, 0.16, m, r2=0.0, loc=(0, 0, 0.0), verts=16, bevel=0.0, parent=root)
    tip.rotation_euler = (math.pi, 0, 0)
    return _norm(root)


def hinge():
    root = _root("hinge", tilt=-25)
    f = _front(root)
    m = _metal("hi_m", "#AEB8BF")
    for sx in (-1, 1):
        kit.box((0.4, 0.05, 0.5), m, loc=(sx * 0.24, 0, 0.25), bevel=0.03, parent=f)
        for z in (0.12, 0.38):
            kit.cyl(0.045, 0.03, mat("hi_screw", "#6E7880", rough=0.4, metal=0.6), loc=(sx * 0.26, -0.03, z),
                    rot=(math.pi / 2, 0, 0), verts=12, parent=f)
    kit.cyl(0.07, 0.55, _metal("hi_pin", "#8E989F"), loc=(0, 0, -0.02), verts=16, bevel=0.02, parent=f)
    return _norm(root)


def paint():
    root = _root("paint")
    tin = _metal("pa_tin", "#C9D3DA")
    kit.cyl(0.36, 0.6, tin, loc=(0, 0, 0), verts=32, bevel=0.03, parent=root)
    kit.cyl(0.33, 0.04, _glossy("pa_p", "#4FA65A"), loc=(0, 0, 0.58), verts=32, bevel=0.01, parent=root)
    kit.sphere(0.07, _glossy("pa_drip", "#4FA65A"), loc=(0.2, -0.3, 0.45), scale=(1, 0.5, 2.0), seg=10,
               parent=root)
    kit.box((0.5, 0.03, 0.3), mat("pa_lab", "#FFF4E2", rough=0.6), loc=(0, -0.355, 0.28), bevel=0.02,
            parent=_front(root))
    kit.curve_tube([(-0.36, 0, 0.55), (-0.2, 0, 0.95), (0.2, 0, 0.95), (0.36, 0, 0.55)], r=0.02,
                   m=_metal("pa_handle", "#8E989F"), parent=root)
    return _norm(root)


DINO_EGGS = {
    "moosaurus": ("#7FCF8E", "#4E9E63"), "trikeri": ("#F4B183", "#D9825A"), "stegolino": ("#B9A6E8", "#8A72C8"),
    "ankyknubbel": ("#C8B98A", "#9A8A5A"), "parasauri": ("#8EC8EE", "#5A9AD0"), "segelruecken": ("#F4908A", "#D9605A"),
    "pachy": ("#E8D0A0", "#C8A870"), "stachelchen": ("#6EC8B8", "#3A9A8A"), "flauschi": ("#FFD86A", "#F2A923"),
    "brontobeere": ("#C88AD8", "#F28AB8"),
}


def item_frames():
    f = {
        "wheat": wheat, "corn": corn, "carrot": carrot, "tomato": tomato, "strawberry": strawberry, "fern": fern,
        "feed_chicken": lambda: sack("#FFCF3A", "#F2B21E"), "feed_cow": lambda: sack("#6EB4F0", "#E8C26A"),
        "feed_sheep": lambda: sack("#8CCB5A", "#C9A060"), "feed_pig": lambda: sack("#F4A0B8", "#D9963E"),
        "egg": lambda: egg("#FFF0D8"), "milk": milk, "bread": bread,
        "corn_bread": lambda: bread("#F2C14E", "#D99A2A", square=True), "carrot_cake": cake,
        "cream": cream, "butter": butter, "cheese": cheese, "wool": wool, "truffle": truffle,
        "honey": honey_pot, "strawberry_jam": lambda: jar("#E8384A"), "honey_jam": lambda: jar("#F07A2A", "#F2A923"),
        "cloth": fabric, "scarf": scarf, "popcorn": popcorn, "butter_popcorn": lambda: popcorn(True),
        "tomato_sauce": bottle, "truffle_sauce": lambda: bottle("#8A5A3A", "#3E8E5A"),
        "candle": candle, "festive_candle": lambda: candle("#E8473B", "#FFD23F"),
        "amber_candle": lambda: candle("#F29A2A", "#8A4A0A"),
        "fossil": fossil, "amber": amber, "primeval_egg": lambda: egg("#BFE4A0", "#5A9A4A", big=True),
        "giant_pancake": pancakes,
        "axe": axe, "saw": saw, "dynamite": dynamite, "shovel": shovel, "stake": stake, "land_map": land_map,
        "tape": tape, "rivet": bolt, "plank": planks, "rope": rope, "nail": nail, "hinge": hinge, "paint": paint,
    }
    for sp, (a, b) in DINO_EGGS.items():
        f["egg_" + sp] = (lambda a=a, b=b: egg(a, b))
    return {"uiitem_" + k: v for k, v in f.items()}
