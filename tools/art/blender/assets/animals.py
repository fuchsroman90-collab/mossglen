"""Animals: chicken and baby dino. Built per pose, rendered per frame."""
from __future__ import annotations

import math

from mathutils import Matrix, Vector

from .. import kit
from ..kit import mat


# ---------------------------------------------------------------- shared

def eye(head_c: Vector, head_r: float, direction: Vector, r: float, parent, look=None, lid=0.0,
        sclera="#FFFFFF", pupil="#2B1D16", lid_color=None):
    """Cartoon eye on the surface of a head sphere.

    lid: 0 open .. 1 closed (blink).
    """
    d = direction.normalized()
    c = head_c + d * (head_r - r * 0.62)
    m_white = mat("eye_white", sclera, rough=0.25, spec=0.5, edge=0.25)
    m_pupil = mat("eye_pupil", pupil, rough=0.12, spec=0.8, edge=0.0)
    m_glint = mat("eye_glint", "#FFFFFF", rough=0.5, spec=0.0, edge=0.0, emit=1.5)
    if lid >= 0.95:
        # closed eye: skin-coloured bulge with a dark lash line
        t = Vector((0, 0, 1)).cross(d).normalized()
        b = d.cross(t)
        basis = Matrix((t, b, d)).transposed()
        kit.sphere(r, mat("lid", lid_color or "#F3E7D5", edge=0.3), loc=c, seg=20, parent=parent)
        kit.sphere(1.0, mat("lash", "#3A2A20", rough=0.5, edge=0.0), loc=c + d * (r * 0.72) - b * (r * 0.1),
                   scale=(r * 0.75, r * 0.13, r * 0.4), rot=basis.to_euler(), seg=16, parent=parent)
        return
    kit.sphere(r, m_white, loc=c, seg=24, parent=parent)
    look = (look if look is not None else kit.TO_CAM).normalized()
    pd = (look * 0.55 + d * 0.45).normalized()
    pc = c + pd * (r * 0.6)
    kit.sphere(r * 0.52, m_pupil, loc=pc, seg=20, parent=parent)
    glint_dir = (pd + kit.LIGHT_DIR * 0.8).normalized()
    kit.sphere(r * 0.17, m_glint, loc=c + glint_dir * (r * 0.98), seg=12, parent=parent)


def _rotz(v: Vector, deg: float) -> Vector:
    a = math.radians(deg)
    return Vector((v.x * math.cos(a) - v.y * math.sin(a), v.x * math.sin(a) + v.y * math.cos(a), v.z))


# ---------------------------------------------------------------- chicken

CHICKEN_WHITE = "#FFF8EC"
HEN_PIVOT = 0.24


def chicken(yaw: float, body_z=0.0, body_pitch=0.0, head=(0.0, 0.0), legs=(0.0, 0.0),
            wing=0.0, blink=0.0, squash=0.0):
    """Plump chibi hen, ~0.5 m tall. Local +X is forward.

    head: (forward, down) offset of the head in metres.
    legs: swing angle in degrees for (right, left) leg.
    """
    root = kit.empty("chicken", rot=(0, 0, math.radians(yaw)))
    pz = HEN_PIVOT
    body = kit.empty("body", loc=(0, 0, pz + body_z), rot=(0, math.radians(body_pitch), 0), parent=root)
    s = 1.0 + squash
    m_body = mat("hen", CHICKEN_WHITE, rough=0.7, spec=0.15, edge=0.55, edge_color="#B9A68C", sss=0.05)
    hx, hd = head
    head_c = Vector((0.15 + hx, 0.0, 0.46 - hd - pz))
    kit.blob([
        {"co": (-0.01, 0.0, 0.25 * s - pz), "r": 0.25, "type": "ELLIPSOID", "size": (1.08, 0.88, 0.86 / s), "stiff": 1.6},
        {"co": (0.09, 0.0, 0.27 - pz), "r": 0.17, "stiff": 1.6},
        {"co": (0.11 + hx * 0.5, 0.0, 0.36 - hd * 0.5 - pz), "r": 0.15, "stiff": 1.4},
        {"co": tuple(head_c), "r": 0.165, "stiff": 1.8},
        # tail fan, tilted back
        {"co": (-0.17, 0.0, 0.35 - pz), "r": 0.16, "type": "ELLIPSOID", "size": (0.55, 0.62, 1.0),
         "rot": (0, math.radians(-38), 0), "stiff": 1.5},
        {"co": (-0.2, 0.05, 0.42 - pz), "r": 0.08, "stiff": 2.0},
        {"co": (-0.2, -0.05, 0.42 - pz), "r": 0.08, "stiff": 2.0},
    ], m_body, name="hen", parent=body)

    # wings: flat ovals hugging the body sides (separate family -> soft crease)
    m_wing = mat("hen_wing", "#F6E9D3", rough=0.7, spec=0.15, edge=0.6, edge_color="#B09A7D")
    for side in (-1, 1):
        kit.blob([
            {"co": (-0.03, side * 0.13, 0.27 - pz), "r": 0.15, "type": "ELLIPSOID", "size": (1.0, 0.32, 0.62),
             "rot": (math.radians(side * (8 + wing * 30)), math.radians(-14), 0), "stiff": 2.0},
        ], m_wing, name="wing", parent=body)

    # comb and wattle
    m_red = mat("comb", "#E5483B", rough=0.45, spec=0.35, edge=0.4, sss=0.1)
    for dx, dz, r in [(0.055, 0.12, 0.048), (0.0, 0.145, 0.056), (-0.055, 0.12, 0.046)]:
        kit.sphere(r, m_red, loc=head_c + Vector((dx, 0, dz)), scale=(0.9, 0.55, 1.0), seg=16, parent=body)
    kit.sphere(0.036, m_red, loc=head_c + Vector((0.13, 0.0, -0.075)), scale=(0.8, 0.6, 1.25), seg=16, parent=body)

    # beak
    m_beak = mat("beak", "#F8B630", rough=0.35, spec=0.4, edge=0.35)
    kit.cyl(0.042, 0.075, m_beak, loc=head_c + Vector((0.145, 0, -0.005)), rot=(0, math.radians(90), 0),
            r2=0.006, bevel=0.0, verts=16, parent=body)

    # eyes
    look = _rotz(kit.TO_CAM, -yaw)
    for side in (-1, 1):
        d = Vector((0.82, side * 0.5, 0.25))
        eye(head_c, 0.165, d, 0.05, body, look=look, lid=blink, lid_color=CHICKEN_WHITE)

    # legs (short, chibi)
    m_leg = mat("leg", "#F39B2E", rough=0.45, spec=0.3, edge=0.35)
    for side, ang in ((-1, legs[0]), (1, legs[1])):
        hip = kit.empty("hip", loc=(0.01, side * 0.075, 0.10 + body_z * 0.5), rot=(0, math.radians(ang), 0),
                        parent=root)
        kit.cyl(0.02, 0.11, m_leg, loc=(0, 0, -0.10), bevel=0.0, verts=10, parent=hip)
        for toe in (-32, 0, 32):
            a = math.radians(toe)
            kit.sphere(0.022, m_leg, loc=(0.035 * math.cos(a), 0.035 * math.sin(a), -0.095),
                       scale=(2.0, 0.8, 0.6), rot=(0, 0, a), seg=12, parent=hip)
    return root


def chicken_frames():
    """name -> builder for all chicken animation frames."""
    out = {}
    for facing, yaw in (("se", 0.0), ("ne", 90.0)):
        for i in range(6):  # idle: breathe + one blink
            t = i / 6.0
            out[f"chicken_idle_{facing}_{i}"] = (lambda t=t, yaw=yaw, i=i: chicken(
                yaw, body_z=0.006 * math.sin(t * 2 * math.pi), squash=0.02 * math.sin(t * 2 * math.pi),
                head=(0.0, 0.006 * math.sin(t * 2 * math.pi)), blink=1.0 if i == 4 else 0.0))
        for i in range(8):  # walk cycle
            t = i / 8.0
            sw = math.sin(t * 2 * math.pi)
            out[f"chicken_walk_{facing}_{i}"] = (lambda sw=sw, t=t, yaw=yaw: chicken(
                yaw, body_z=0.02 * abs(math.cos(t * 2 * math.pi)), body_pitch=4.0,
                head=(0.035 * math.sin(t * 4 * math.pi), 0.0), legs=(28 * sw, -28 * sw),
                wing=0.15 * abs(sw)))
        for i, (fw, dn, pitch) in enumerate([(0.02, 0.03, 6), (0.05, 0.10, 16), (0.07, 0.15, 24),
                                             (0.05, 0.10, 16), (0.02, 0.03, 6), (0.0, 0.0, 0)]):
            out[f"chicken_peck_{facing}_{i}"] = (lambda fw=fw, dn=dn, pitch=pitch, yaw=yaw: chicken(
                yaw, body_pitch=pitch, head=(fw, dn)))
    return out


# ---------------------------------------------------------------- baby dino

DINO_SKIN = "#7FCF8E"
DINO_BELLY = "#F4E9C8"
DINO_SPOT = "#4E9E63"


def dino(yaw: float, neck=0.0, head_tilt=0.0, legs=(0.0, 0.0), body_z=0.0, tail=0.0, blink=0.0, squash=0.0):
    """Chibi baby long-neck ('Moosaurus'), ~0.8 m tall. Local +X is forward.

    neck: sideways sway in degrees, legs: swing angles for the two diagonal leg pairs.
    """
    root = kit.empty("dino", rot=(0, 0, math.radians(yaw)))
    body = kit.empty("body", loc=(0, 0, body_z), parent=root)
    s = 1.0 + squash
    skin = mat("dino_skin", DINO_SKIN, rough=0.5, spec=0.3, edge=0.55, edge_color="#2F6E48", sss=0.06)
    sw = math.sin(math.radians(neck))
    spine = [(-0.64, 0.14 * tail, 0.2), (-0.46, 0.07 * tail, 0.25), (-0.26, 0.0, 0.3), (0.0, 0.0, 0.33 * s),
             (0.2, 0.0, 0.4), (0.3, 0.03 * sw, 0.55), (0.35, 0.08 * sw, 0.72),
             (0.38, 0.12 * sw, 0.86 - 0.02 * head_tilt)]
    radii = [0.05, 0.1, 0.2, 0.3, 0.24, 0.15, 0.13, 0.13]
    elems = kit.chain(spine, radii, steps=7)
    head_c = Vector((0.42, 0.12 * sw, 0.92 - 0.02 * head_tilt))
    elems.append({"co": tuple(head_c), "r": 0.24, "type": "ELLIPSOID", "size": (1.15, 0.92, 0.85), "stiff": 2.0})
    elems.append({"co": tuple(head_c + Vector((0.12, 0, -0.03))), "r": 0.17, "stiff": 2.0})
    bo = kit.to_mesh(kit.blob(elems, skin, name="dino", parent=body))
    surf = kit.Surface([bo])

    # belly patch and spots placed on the real surface
    belly = mat("dino_belly", DINO_BELLY, rough=0.6, spec=0.2, edge=0.4, edge_color="#B5A47A")
    spot = mat("dino_spot", DINO_SPOT, rough=0.5, spec=0.25, edge=0.4)
    c_body = kit.world(body, (0.05, 0, 0.33))
    for d, r in (((0.8, -0.35, -0.45), 0.12),):
        p, n = surf.toward(c_body, kit.world(root, d) - kit.world(root, (0, 0, 0)))
        if p is not None:
            o = kit.sphere(r, belly, scale=(1.0, 1.0, 0.18), seg=20)
            kit.place_on(o, p - n * 0.012, n)
            o.parent = body
            o.matrix_parent_inverse = body.matrix_world.inverted()
    rng = __import__("random").Random(5)
    for i in range(9):
        a = rng.uniform(0, 2 * math.pi)
        x = rng.uniform(-0.3, 0.2)
        d = kit.world(root, (x * 0.4, math.cos(a) * 0.5, 0.9)) - kit.world(root, (0, 0, 0))
        p, n = surf.toward(kit.world(body, (x, 0, 0.3)), d)
        if p is not None:
            o = kit.sphere(rng.uniform(0.04, 0.07), spot, scale=(1.0, 1.0, 0.2), seg=16)
            kit.place_on(o, p - n * 0.008, n)
            o.parent = body
            o.matrix_parent_inverse = body.matrix_world.inverted()
    # soft back plates along the spine
    for i, x in enumerate((0.1, -0.06, -0.22, -0.38)):
        p, n = surf.toward(kit.world(body, (x, 0, 0.3)), Vector((0, 0, 1)))
        if p is not None:
            o = kit.sphere(0.065 - i * 0.01, spot, scale=(1.0, 0.32, 1.1), seg=16)
            o.location = p + Vector((0, 0, 0.02))
            o.rotation_euler = (0, 0, math.radians(yaw))
            o.parent = body
            o.matrix_parent_inverse = body.matrix_world.inverted()

    # eyes, cheeks, nostrils via the head surface
    look = _rotz(kit.TO_CAM, -yaw)
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.72, side * 0.6, 0.32))
        dw = kit.world(root, dl) - kit.world(root, (0, 0, 0))
        p, n = surf.toward(hw, dw)
        if p is not None:
            eye_r = 0.068
            hit_local = body.matrix_world.inverted() @ p
            hr = (hit_local - head_c).length
            eye(head_c, hr, dl, eye_r, body, look=look, lid=blink, lid_color=DINO_SKIN)
    cheek = mat("dino_cheek", "#FF9EAA", rough=0.6, edge=0.2)
    for side in (-1, 1):
        dl = Vector((0.65, side * 0.7, -0.15))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            o = kit.sphere(0.04, cheek, scale=(1.0, 1.0, 0.25), seg=12)
            kit.place_on(o, p, n)
            o.parent = body
            o.matrix_parent_inverse = body.matrix_world.inverted()
    nos = mat("dino_nostril", "#2F6E48", rough=0.6, edge=0.0)
    for side in (-1, 1):
        p, n = surf.toward(hw, kit.world(root, (1.0, side * 0.22, 0.25)) - kit.world(root, (0, 0, 0)))
        if p is not None:
            o = kit.sphere(0.014, nos, seg=8)
            o.location = p
            o.parent = body
            o.matrix_parent_inverse = body.matrix_world.inverted()

    # stubby legs (separate blobs so they can swing), wide feet with nails
    nail = mat("dino_nail", "#F7EEDB", rough=0.4, edge=0.3)
    for (lx, ly, ang) in ((0.17, -0.15, legs[0]), (0.17, 0.15, legs[1]), (-0.19, -0.15, legs[1]),
                          (-0.19, 0.15, legs[0])):
        hip = kit.empty("hip", loc=(lx, ly, 0.24), rot=(0, math.radians(ang), 0), parent=root)
        kit.blob(kit.chain([(0, 0, 0.02), (0, 0, -0.12), (0.01, 0, -0.2)], [0.13, 0.11, 0.115], steps=5),
                 skin, name="leg", parent=hip)
        for t in (-0.04, 0.0, 0.04):
            kit.sphere(0.022, nail, loc=(0.075, t, -0.225), scale=(1.0, 1.0, 0.65), seg=10, parent=hip)
    return root


def dino_frames():
    out = {}
    for facing, yaw in (("se", 0.0), ("ne", 90.0)):
        for i in range(8):
            t = i / 8.0
            w = math.sin(t * 2 * math.pi)
            out[f"dino_idle_{facing}_{i}"] = (lambda w=w, i=i, yaw=yaw: dino(
                yaw, neck=10 * w, head_tilt=0.5 + 0.5 * w, tail=0.6 * w, squash=0.015 * w,
                blink=1.0 if i == 5 else 0.0))
        for i in range(8):
            t = i / 8.0
            sw = math.sin(t * 2 * math.pi)
            out[f"dino_walk_{facing}_{i}"] = (lambda sw=sw, t=t, yaw=yaw: dino(
                yaw, neck=4 * sw, legs=(22 * sw, -22 * sw), body_z=0.018 * abs(math.cos(t * 2 * math.pi)),
                tail=-0.8 * sw))
    return out


# ---------------------------------------------------------------- cow

COW_WHITE = "#FFF7EE"
COW_SPOT = "#6E4A33"


def cow(yaw: float, body_z=0.0, head=(0.0, 0.0), legs=(0.0, 0.0), tail=0.0, blink=0.0, squash=0.0, chew=0.0):
    """Chibi dairy cow, ~0.8 m tall. head: (forward, down) offset."""
    root = kit.empty("cow", rot=(0, 0, math.radians(yaw)))
    body = kit.empty("body", loc=(0, 0, body_z), parent=root)
    s = 1.0 + squash
    hide = mat("cow_hide", COW_WHITE, rough=0.6, spec=0.2, edge=0.55, edge_color="#B7A58E", sss=0.04)
    hx, hd = head
    head_c = Vector((0.43 + hx, 0.0, 0.6 - hd))
    bo = kit.to_mesh(kit.blob(
        kit.chain([(-0.36, 0, 0.42), (-0.1, 0, 0.45 * s), (0.18, 0, 0.45), (0.3 + hx * 0.5, 0, 0.5 - hd * 0.5)],
                  [0.26, 0.33, 0.3, 0.2], steps=6)
        + [{"co": tuple(head_c), "r": 0.25, "type": "ELLIPSOID", "size": (1.0, 1.0, 0.95), "stiff": 2.0}],
        hide, name="cow", parent=body))
    surf = kit.Surface([bo])
    look = _rotz(kit.TO_CAM, -yaw)

    # brown patches projected onto the hide
    spot = mat("cow_spot", COW_SPOT, rough=0.55, spec=0.2, edge=0.4)
    rng = __import__("random").Random(8)
    for x, side, z in [(-0.25, -1, 0.55), (0.05, -1, 0.6), (-0.15, 1, 0.62), (0.15, 1, 0.5), (-0.38, -1, 0.4),
                       (-0.05, 0, 0.78)]:
        d = kit.world(root, (x * 0.3, side * 1.0, 0.6 if side else 1.0)) - kit.world(root, (0, 0, 0))
        p, n = surf.toward(kit.world(body, (x, 0, 0.45)), d)
        if p is not None:
            o = kit.sphere(rng.uniform(0.09, 0.13), spot, scale=(1.3, 1.0, 0.12), seg=18)
            kit.place_on(o, p - n * 0.008, n)
            o.parent = body
            o.matrix_parent_inverse = body.matrix_world.inverted()
    # muzzle, nostrils
    pink = mat("cow_muzzle", "#FFB9AE", rough=0.5, spec=0.25, edge=0.45, edge_color="#B9706A")
    mz = head_c + Vector((0.16, 0, -0.08))
    kit.sphere(0.16, pink, loc=mz, scale=(0.75, 1.15, 0.8), seg=24, parent=body)
    nos = mat("cow_nostril", "#8A4A44", rough=0.6, edge=0.0)
    for side in (-1, 1):
        kit.sphere(0.022, nos, loc=mz + Vector((0.11, side * 0.06, 0.02)), scale=(0.6, 1, 1.3), seg=10, parent=body)
    # mouth chew: tiny lower lip bob
    kit.sphere(0.06, pink, loc=mz + Vector((0.05, 0, -0.1 - 0.015 * chew)), scale=(1.0, 1.4, 0.5), seg=14, parent=body)
    # eyes
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.6, side * 0.62, 0.42))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            hr = (body.matrix_world.inverted() @ p - head_c).length
            eye(head_c, hr, dl, 0.065, body, look=look, lid=blink, lid_color=COW_WHITE)
    # ears and horns
    for side in (-1, 1):
        kit.sphere(0.07, hide, loc=head_c + Vector((-0.05, side * 0.2, 0.05)), scale=(0.7, 1.25, 0.45),
                   rot=(side * 0.35, 0, 0), seg=16, parent=body)
        kit.sphere(0.04, pink, loc=head_c + Vector((-0.04, side * 0.22, 0.05)), scale=(0.6, 1.0, 0.3),
                   rot=(side * 0.35, 0, 0), seg=12, parent=body)
        kit.cyl(0.028, 0.08, mat("horn", "#F4E6C4", rough=0.4, edge=0.35), r2=0.012,
                loc=head_c + Vector((-0.04, side * 0.1, 0.13)), rot=(side * -0.45, -0.2, 0), bevel=0.0, verts=10,
                parent=body)
    # bell
    gold = mat("bell", "#F6C23A", rough=0.25, metal=0.8, spec=0.6, edge=0.4)
    bell_p = Vector((0.36, 0, 0.36))
    kit.sphere(0.035, mat("collar", "#C0392B", rough=0.6, edge=0.3), loc=bell_p + Vector((0, 0, 0.06)), seg=12,
               parent=body)
    kit.cyl(0.05, 0.07, gold, r2=0.03, loc=bell_p - Vector((0, 0, 0.03)), bevel=0.01, verts=14, parent=body)
    # udder
    kit.sphere(0.08, pink, loc=(-0.12, 0, 0.17), scale=(1.1, 1.0, 0.7), seg=16, parent=body)
    # tail with tuft
    tail_m = hide
    a = math.radians(25 * tail)
    tp = Vector((-0.6, 0.12 * math.sin(a), 0.3))
    kit.curve_tube([(-0.5, 0, 0.55), (-0.6, 0.05 * math.sin(a), 0.45), tuple(tp)], r=0.018, m=tail_m, parent=body)
    kit.sphere(0.04, spot, loc=tp, scale=(1, 1, 1.4), seg=12, parent=body)
    # legs
    hoof = mat("hoof", "#4A3426", rough=0.5, edge=0.3)
    for (lx, ly, ang) in ((0.2, -0.15, legs[0]), (0.2, 0.15, legs[1]), (-0.28, -0.15, legs[1]),
                          (-0.28, 0.15, legs[0])):
        hip = kit.empty("hip", loc=(lx, ly, 0.3), rot=(0, math.radians(ang), 0), parent=root)
        kit.blob(kit.chain([(0, 0, 0.0), (0, 0, -0.18), (0, 0, -0.24)], [0.1, 0.085, 0.085], steps=5),
                 hide, name="leg", parent=hip)
        kit.cyl(0.07, 0.06, hoof, loc=(0, 0, -0.3), bevel=0.015, verts=14, parent=hip)
    return root


def cow_frames():
    out = {}
    for facing, yaw in (("se", 0.0), ("ne", 90.0)):
        for i in range(6):
            t = i / 6.0
            w = math.sin(t * 2 * math.pi)
            out[f"cow_idle_{facing}_{i}"] = (lambda w=w, i=i, yaw=yaw: cow(
                yaw, squash=0.012 * w, tail=w, head=(0.0, 0.01 * w), blink=1.0 if i == 4 else 0.0))
        for i in range(8):
            t = i / 8.0
            sw = math.sin(t * 2 * math.pi)
            out[f"cow_walk_{facing}_{i}"] = (lambda sw=sw, t=t, yaw=yaw: cow(
                yaw, legs=(20 * sw, -20 * sw), body_z=0.015 * abs(math.cos(t * 2 * math.pi)), tail=-0.6 * sw,
                head=(0.0, 0.015 * abs(sw))))
        for i, (fw, dn, ch) in enumerate([(0.03, 0.1, 0), (0.06, 0.22, 0), (0.07, 0.3, 1), (0.07, 0.3, 0),
                                          (0.07, 0.3, 1), (0.03, 0.12, 0)]):
            out[f"cow_eat_{facing}_{i}"] = (lambda fw=fw, dn=dn, ch=ch, yaw=yaw: cow(yaw, head=(fw, dn), chew=ch))
    return out


# ---------------------------------------------------------------- sheep

def _wool_mat():
    return __import__("blender.assets.nature", fromlist=["x"]).foliage_mat(
        "wool", "#FFFDF6", "#D9D0C0", noise_scale=22.0, z0=0.1, z1=0.7, rough=0.9)


def sheep(yaw: float, body_z=0.0, head=(0.0, 0.0), legs=(0.0, 0.0), blink=0.0, squash=0.0):
    """Fluffy chibi sheep, ~0.65 m tall. Wool = many bumpy puffs, dark face and legs."""
    import random as _r
    rng = _r.Random(3)
    root = kit.empty("sheep", rot=(0, 0, math.radians(yaw)))
    body = kit.empty("body", loc=(0, 0, body_z), parent=root)
    s = 1.0 + squash
    wool = _wool_mat()
    nature = __import__("blender.assets.nature", fromlist=["x"])
    for x, y, z, r in [(0, 0, 0.42, 0.27), (-0.18, 0.08, 0.4, 0.2), (-0.18, -0.08, 0.4, 0.2), (0.16, 0.0, 0.44, 0.2),
                       (0.02, 0.14, 0.5, 0.16), (0.02, -0.14, 0.5, 0.16), (-0.08, 0, 0.58, 0.17), (-0.3, 0, 0.44, 0.13)]:
        nature.leaf_clump((x, y, z * s), r, wool, rng, parent=body, squash=0.95, bumps=0.28)
    face = mat("sheep_face", "#4C4645", rough=0.6, spec=0.2, edge=0.45, edge_color="#1E1A1A")
    hx, hd = head
    head_c = Vector((0.32 + hx, 0, 0.5 - hd))
    ho = kit.to_mesh(kit.blob([{"co": tuple(head_c), "r": 0.17, "type": "ELLIPSOID", "size": (1.15, 0.85, 0.9)},
                               {"co": tuple(head_c + Vector((0.1, 0, -0.05))), "r": 0.11}], face, name="shead",
                              parent=body))
    surf = kit.Surface([ho])
    nature.leaf_clump(head_c + Vector((-0.04, 0, 0.11)), 0.1, wool, rng, parent=body, squash=0.8)  # wool cap
    look = _rotz(kit.TO_CAM, -yaw)
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.65, side * 0.6, 0.25))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            hr = (body.matrix_world.inverted() @ p - head_c).length
            eye(head_c, hr, dl, 0.055, body, look=look, lid=blink, lid_color="#4C4645")
        kit.sphere(0.06, face, loc=head_c + Vector((-0.04, side * 0.17, 0.0)), scale=(0.6, 1.5, 0.4),
                   rot=(side * -0.3, 0, 0), seg=14, parent=body)
    kit.sphere(0.025, mat("sheep_nose", "#2A2424", rough=0.5, edge=0.0), loc=head_c + Vector((0.2, 0, -0.04)),
               scale=(0.6, 1.2, 0.7), seg=10, parent=body)
    for (lx, ly, ang) in ((0.14, -0.1, legs[0]), (0.14, 0.1, legs[1]), (-0.18, -0.1, legs[1]), (-0.18, 0.1, legs[0])):
        hip = kit.empty("hip", loc=(lx, ly, 0.25), rot=(0, math.radians(ang), 0), parent=root)
        kit.cyl(0.035, 0.24, face, loc=(0, 0, -0.24), bevel=0.0, verts=10, parent=hip)
    return root


def sheep_frames():
    out = {}
    for facing, yaw in (("se", 0.0), ("ne", 90.0)):
        for i in range(6):
            w = math.sin(i / 6 * 2 * math.pi)
            out[f"sheep_idle_{facing}_{i}"] = (lambda w=w, i=i, yaw=yaw: sheep(
                yaw, squash=0.02 * w, head=(0.0, 0.01 * w), blink=1.0 if i == 3 else 0.0))
        for i in range(8):
            t = i / 8
            sw = math.sin(t * 2 * math.pi)
            out[f"sheep_walk_{facing}_{i}"] = (lambda sw=sw, t=t, yaw=yaw: sheep(
                yaw, legs=(24 * sw, -24 * sw), body_z=0.02 * abs(math.cos(t * 2 * math.pi))))
        for i, (fw, dn) in enumerate([(0.02, 0.08), (0.05, 0.2), (0.06, 0.27), (0.06, 0.25), (0.06, 0.27),
                                      (0.02, 0.1)]):
            out[f"sheep_eat_{facing}_{i}"] = (lambda fw=fw, dn=dn, yaw=yaw: sheep(yaw, head=(fw, dn)))
    return out


# ---------------------------------------------------------------- pig

PIG_PINK = "#FFB3B5"


def pig(yaw: float, body_z=0.0, head=(0.0, 0.0), legs=(0.0, 0.0), blink=0.0, squash=0.0):
    """Round chibi pig, ~0.55 m tall. Sniffs for truffles."""
    root = kit.empty("pig", rot=(0, 0, math.radians(yaw)))
    body = kit.empty("body", loc=(0, 0, body_z), parent=root)
    s = 1.0 + squash
    skin = mat("pig_skin", PIG_PINK, rough=0.5, spec=0.25, edge=0.55, edge_color="#B05A66", sss=0.08)
    hx, hd = head
    head_c = Vector((0.3 + hx, 0, 0.4 - hd))
    bo = kit.to_mesh(kit.blob(
        kit.chain([(-0.22, 0, 0.32), (0.0, 0, 0.34 * s), (0.18 + hx * 0.5, 0, 0.36 - hd * 0.5)],
                  [0.22, 0.27, 0.22], steps=6)
        + [{"co": tuple(head_c), "r": 0.22, "type": "ELLIPSOID", "size": (0.95, 1.0, 0.95), "stiff": 2.0}],
        skin, name="pig", parent=body))
    surf = kit.Surface([bo])
    snout_m = mat("pig_snout", "#FF9AA2", rough=0.45, spec=0.3, edge=0.5, edge_color="#A8505C")
    sn = head_c + Vector((0.17, 0, -0.03))
    kit.cyl(0.075, 0.06, snout_m, loc=sn, rot=(0, math.radians(90), 0), bevel=0.02, verts=20, parent=body)
    nos = mat("pig_nostril", "#B0505C", rough=0.6, edge=0.0)
    for side in (-1, 1):
        kit.sphere(0.016, nos, loc=sn + Vector((0.062, side * 0.028, 0)), scale=(0.5, 1, 1.3), seg=8, parent=body)
    look = _rotz(kit.TO_CAM, -yaw)
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.62, side * 0.55, 0.42))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            hr = (body.matrix_world.inverted() @ p - head_c).length
            eye(head_c, hr, dl, 0.052, body, look=look, lid=blink, lid_color=PIG_PINK)
        # floppy ears
        kit.sphere(0.075, skin, loc=head_c + Vector((-0.02, side * 0.12, 0.12)), scale=(0.9, 0.7, 0.3),
                   rot=(side * 0.45, 0.45, 0), seg=14, parent=body)
        kit.sphere(0.035, mat("pig_cheek", "#FF8A96", rough=0.6, edge=0.2),
                   loc=head_c + Vector((0.1, side * 0.12, -0.06)), scale=(1, 1, 0.5), seg=10, parent=body)
    # curly tail
    pts = [(-0.33, 0, 0.36)]
    for k in range(1, 7):
        a = k * 1.1
        pts.append((-0.39 - 0.022 * math.sin(a), 0.028 * math.cos(a), 0.38 + k * 0.01))
    kit.curve_tube(pts, r=0.013, m=skin, parent=body)
    hoof = mat("pig_hoof", "#C77882", rough=0.5, edge=0.3)
    for (lx, ly, ang) in ((0.14, -0.12, legs[0]), (0.14, 0.12, legs[1]), (-0.16, -0.12, legs[1]),
                          (-0.16, 0.12, legs[0])):
        hip = kit.empty("hip", loc=(lx, ly, 0.17), rot=(0, math.radians(ang), 0), parent=root)
        kit.cyl(0.055, 0.15, skin, loc=(0, 0, -0.15), bevel=0.02, verts=12, parent=hip)
        kit.cyl(0.056, 0.035, hoof, loc=(0, 0, -0.17), bevel=0.01, verts=12, parent=hip)
    return root


def pig_frames():
    out = {}
    for facing, yaw in (("se", 0.0), ("ne", 90.0)):
        for i in range(6):
            w = math.sin(i / 6 * 2 * math.pi)
            out[f"pig_idle_{facing}_{i}"] = (lambda w=w, i=i, yaw=yaw: pig(
                yaw, squash=0.025 * w, blink=1.0 if i == 2 else 0.0))
        for i in range(8):
            t = i / 8
            sw = math.sin(t * 2 * math.pi)
            out[f"pig_walk_{facing}_{i}"] = (lambda sw=sw, t=t, yaw=yaw: pig(
                yaw, legs=(26 * sw, -26 * sw), body_z=0.02 * abs(math.cos(t * 2 * math.pi))))
        for i, (fw, dn) in enumerate([(0.02, 0.05), (0.05, 0.13), (0.06, 0.17), (0.07, 0.15), (0.06, 0.17),
                                      (0.02, 0.06)]):
            out[f"pig_eat_{facing}_{i}"] = (lambda fw=fw, dn=dn, yaw=yaw: pig(yaw, head=(fw, dn)))
    return out
