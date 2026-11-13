"""Animals: chicken and baby dino. Built per pose, rendered per frame."""
from __future__ import annotations

import math
import random

from mathutils import Matrix, Vector

from .. import kit
from ..kit import mat


# ---------------------------------------------------------------- shared

def eye(head_c: Vector, head_r: float, direction: Vector, r: float, parent, look=None, lid=0.0,
        sclera="#FFFFFF", pupil="#2B1D16", lid_color=None, droop=0.2, brow=None):
    """Cartoon eye on the surface of a head sphere.

    lid: 0 open .. 1 closed (blink).  droop: how far the upper lid hangs over the eye when open
    (gives the cheeky Hay-Day look instead of round googly eyes).  brow: colour of a small eyebrow.
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
    kit.sphere(r, m_white, loc=c, scale=(1.0, 1.0, 1.0), seg=28, parent=parent)
    look = (look if look is not None else kit.TO_CAM).normalized()
    pd = (look * 0.55 + d * 0.45).normalized()
    pc = c + pd * (r * 0.58)
    kit.sphere(r * 0.56, m_pupil, loc=pc, seg=24, parent=parent)
    glint_dir = (pd + kit.LIGHT_DIR * 0.8).normalized()
    kit.sphere(r * 0.2, m_glint, loc=c + glint_dir * (r * 1.0), seg=12, parent=parent)
    kit.sphere(r * 0.09, m_glint, loc=c + (pd - kit.LIGHT_DIR * 0.5).normalized() * (r * 1.0), seg=8, parent=parent)
    t = Vector((0, 0, 1)).cross(d).normalized()
    b = d.cross(t)
    basis = Matrix((t, b, d)).transposed()
    if lid_color is not None and droop > 0.0:
        # upper lid: a flattened shell in skin colour resting on the top of the eye
        lm = mat("lid_" + lid_color, lid_color, rough=0.5, spec=0.25, edge=0.45)
        off = r * (1.0 - 2.0 * droop) + r * 0.62
        kit.sphere(1.0, lm, loc=c + b * off + d * (r * 0.08), scale=(r * 1.12, r * 0.66, r * 1.08),
                   rot=basis.to_euler(), seg=24, parent=parent)
    if brow is not None:
        bm = mat("brow_" + brow, brow, rough=0.6, edge=0.2)
        kit.sphere(1.0, bm, loc=c + b * (r * 1.45) + d * (r * 0.35), scale=(r * 0.85, r * 0.2, r * 0.25),
                   rot=basis.to_euler(), seg=12, parent=parent)


def _rotz(v: Vector, deg: float) -> Vector:
    a = math.radians(deg)
    return Vector((v.x * math.cos(a) - v.y * math.sin(a), v.x * math.sin(a) + v.y * math.cos(a), v.z))


# ---------------------------------------------------------------- chicken

CHICKEN_WHITE = "#FFF8EC"
HEN_PIVOT = 0.24


def chicken(yaw: float, body_z=0.0, body_pitch=0.0, head=(0.0, 0.0), legs=(0.0, 0.0),
            wing=0.0, blink=0.0, squash=0.0):
    """Hen, rebuilt after Roman's "schrecklich" (2026-11-13): upright proud body, S-neck, big head with a
    four-lobed comb, wide two-part beak, wattles, layered wing and tail feathers, sturdy legs.
    Local +X is forward. head: (forward, down) offset; legs: swing angles (right, left)."""
    kit.character_light()
    root = kit.empty("chicken", rot=(0, 0, math.radians(yaw)))
    pz = HEN_PIVOT
    body = kit.empty("body", loc=(0, 0, pz + body_z), rot=(0, math.radians(body_pitch), 0), parent=root)
    s = 1.0 + squash
    white = mat("hen", "#FFFFFF", rough=0.62, spec=0.25, edge=0.6, edge_color="#B8A58E", sss=0.06)
    feather = mat("hen_feather", "#FBF6EE", rough=0.6, spec=0.2, edge=0.65, edge_color="#A8927A")
    hx, hd = head
    head_c = Vector((0.2 + hx, 0.0, 0.52 - hd - pz))
    neck = kit.chain([(0.08, 0, 0.3 - pz), (0.16 + hx * 0.4, 0, 0.38 - hd * 0.4 - pz),
                      (0.19 + hx * 0.8, 0, 0.46 - hd * 0.8 - pz)], [0.12, 0.1, 0.11], steps=5, stiff=2.0)
    hen = kit.to_mesh(kit.blob([
        # round, slightly forward-leaning body with a full breast and raised rump
        {"co": (-0.02, 0.0, 0.24 * s - pz), "r": 0.22, "type": "ELLIPSOID", "size": (1.25, 0.95, 0.9 / s),
         "stiff": 1.8},
        {"co": (0.1, 0.0, 0.27 - pz), "r": 0.15, "stiff": 1.8},
        {"co": (-0.17, 0.0, 0.3 - pz), "r": 0.12, "stiff": 1.8},
        {"co": tuple(head_c), "r": 0.13, "type": "ELLIPSOID", "size": (1.1, 0.95, 1.05), "stiff": 2.2},
    ] + neck, white, name="hen", res=0.01, parent=body))
    surf = kit.Surface([hen])

    # tail: a fan of five pointed feathers, standing up and back
    for i, (rl, pt, ln) in enumerate([(-22, -38, 0.9), (-10, -30, 1.0), (0, -24, 1.08), (10, -30, 1.0),
                                      (22, -38, 0.9)]):
        f = kit.empty("tf", loc=(-0.2, 0, 0.34 - pz), rot=(math.radians(rl), math.radians(pt), 0), parent=body)
        kit.sphere(0.07, feather, loc=(0, 0, 0.1 * ln), scale=(0.6, 0.3, 1.55 * ln), seg=16, parent=f)
    # wings: a shaped oval with three overlapping primary feathers at the back
    for side in (-1, 1):
        wg = kit.empty("wing", loc=(-0.02, side * 0.17, 0.245 - pz),
                       rot=(math.radians(side * (6 + wing * 35)), math.radians(-32), 0), parent=body)
        # teardrop wing: round at the shoulder, tapering to a point that tucks up at the back
        kit.sphere(0.14, feather, loc=(0.02, 0, 0.0), scale=(0.95, 0.26, 0.66), seg=24, parent=wg)
        kit.sphere(0.09, feather, loc=(-0.1, side * -0.01, 0.03), scale=(1.05, 0.22, 0.42),
                   rot=(math.radians(side * -8), math.radians(18), 0), seg=20, parent=wg)

    # comb (four lobes, front ones smaller), wattles and a wide two-part beak
    red = mat("comb", "#F0402F", rough=0.38, spec=0.45, coat=0.25, edge=0.45, edge_color="#8A1A10", sss=0.1)
    # comb: every lobe and the ridge under it is placed on the real head surface (ray cast), so nothing floats
    head_w = kit.world(body, head_c)
    to_local = body.matrix_world.inverted()
    up_w = kit.world(root, (0, 0, 0))

    def on_head(t):
        d = Vector((math.sin(t), 0, math.cos(t)))
        p, _n = surf.toward(head_w, kit.world(root, d) - up_w)
        return (to_local @ p) if p is not None else head_c + d * 0.11

    for deg, r in [(40, 0.044), (18, 0.06), (-4, 0.068), (-26, 0.061), (-48, 0.047)]:
        t = math.radians(deg)
        base = on_head(t)
        nrm = (base - head_c).normalized()
        kit.sphere(r, red, loc=base + nrm * (r * 0.62), scale=(0.75, 0.48, 1.15), rot=(0, t, 0), seg=18,
                   parent=body)
    for k in range(11):
        t = math.radians(50 - k * 10.5)
        base = on_head(t)
        kit.sphere(0.034, red, loc=base, scale=(1.0, 0.55, 0.85), rot=(0, t, 0), seg=12, parent=body)
    for side in (-1, 1):
        kit.sphere(0.034, red, loc=head_c + Vector((0.11, side * 0.022, -0.1)), scale=(0.75, 0.6, 1.35), seg=14,
                   parent=body)
    beak = mat("beak", "#FFC23A", rough=0.3, spec=0.5, coat=0.3, edge=0.45, edge_color="#B06A10")
    # the beak grows out of the head: its base sits well inside the head sphere
    kit.cyl(0.05, 0.135, beak, r2=0.004, loc=head_c + Vector((0.08, 0, -0.008)), rot=(0, math.radians(97), 0),
            bevel=0.0, verts=24, parent=body, scale=(1.0, 1.2, 1.0))
    kit.cyl(0.032, 0.095, beak, r2=0.004, loc=head_c + Vector((0.085, 0, -0.038)), rot=(0, math.radians(80), 0),
            bevel=0.0, verts=18, parent=body, scale=(1.0, 1.1, 1.0))

    # eyes on the head surface, with a lid and a little brow for character
    look = _rotz(kit.TO_CAM, -yaw)
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.55, side * 0.75, 0.3))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        hr = (body.matrix_world.inverted() @ p - head_c).length if p is not None else 0.13
        eye(head_c, hr, dl, 0.052, body, look=look, lid=blink, lid_color="#FFFFFF", droop=0.18)

    # legs: orange, with a little feather "trouser", scaly shin and three toes + spur
    leg = mat("leg", "#FFA63A", rough=0.4, spec=0.35, edge=0.45, edge_color="#B05A10")
    for side, ang in ((-1, legs[0]), (1, legs[1])):
        hip = kit.empty("hip", loc=(0.01, side * 0.08, 0.13 + body_z * 0.5), rot=(0, math.radians(ang), 0),
                        parent=root)
        kit.sphere(0.06, feather, loc=(0, 0, 0.03), scale=(1.0, 0.9, 0.9), seg=14, parent=hip)
        kit.cyl(0.024, 0.12, leg, r2=0.02, loc=(0, 0, -0.125), bevel=0.0, verts=12, parent=hip)
        for toe in (-35, 0, 35):
            a = math.radians(toe)
            kit.sphere(0.024, leg, loc=(0.045 * math.cos(a), 0.045 * math.sin(a), -0.12),
                       scale=(2.2, 0.75, 0.6), rot=(0, 0, a), seg=12, parent=hip)
        kit.sphere(0.016, leg, loc=(-0.035, 0, -0.115), scale=(1.6, 0.8, 0.6), seg=10, parent=hip)
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


# ---------------------------------------------------------------- baby dinos (10 species)

DINO_SKIN = "#7FCF8E"
DINO_BELLY = "#F4E9C8"
DINO_SPOT = "#4E9E63"

# id: skin, spot, edge, neck (0 short .. 1 long), extras
DINOS = {
    "moosaurus": {"skin": "#7FCF8E", "spot": "#4E9E63", "edge": "#2F6E48", "neck": 1.0, "x": ["plates_soft"]},
    "trikeri": {"skin": "#F4B183", "spot": "#D9825A", "edge": "#8A4A2A", "neck": 0.0, "x": ["frill", "horns3"]},
    "stegolino": {"skin": "#B9A6E8", "spot": "#8A72C8", "edge": "#4E3A86", "neck": 0.25, "x": ["plates_big", "tail_spikes"]},
    "ankyknubbel": {"skin": "#C8B98A", "spot": "#9A8A5A", "edge": "#5A4A2A", "neck": 0.0, "x": ["armor", "club"]},
    "parasauri": {"skin": "#8EC8EE", "spot": "#5A9AD0", "edge": "#2A5A8A", "neck": 0.45, "x": ["crest"]},
    "segelruecken": {"skin": "#F4908A", "spot": "#D9605A", "edge": "#8A2A2A", "neck": 0.2, "x": ["sail"]},
    "pachy": {"skin": "#E8D0A0", "spot": "#C8A870", "edge": "#7A5A2A", "neck": 0.3, "x": ["dome"]},
    "stachelchen": {"skin": "#6EC8B8", "spot": "#3A9A8A", "edge": "#1E5A50", "neck": 0.3, "x": ["spikes"]},
    "flauschi": {"skin": "#FFD86A", "spot": "#F2A923", "edge": "#8A5A10", "neck": 0.5, "x": ["fluff"]},
    "brontobeere": {"skin": "#C88AD8", "spot": "#F28AB8", "edge": "#6A2A7A", "neck": 1.3, "x": ["plates_soft"]},
}


def dino(yaw: float, species="moosaurus", neck=0.0, head_tilt=0.0, legs=(0.0, 0.0), body_z=0.0, tail=0.0,
         blink=0.0, squash=0.0):
    """Chibi baby dino. All species share the body; extras (frill, plates, crest ...) make them distinct."""
    sp = DINOS[species]
    nl = sp["neck"]
    root = kit.empty("dino", rot=(0, 0, math.radians(yaw)))
    body = kit.empty("body", loc=(0, 0, body_z), parent=root)
    s = 1.0 + squash
    skin = mat("dino_skin_" + species, sp["skin"], rough=0.5, spec=0.3, edge=0.55, edge_color=sp["edge"], sss=0.06)
    spot = mat("dino_spot_" + species, sp["spot"], rough=0.5, spec=0.25, edge=0.4)
    sw = math.sin(math.radians(neck))
    hz = 0.55 + 0.37 * nl
    hx = 0.36 + 0.06 * (1 - nl)
    tail_len = 1.25 if "club" in sp["x"] else 1.0
    spine = [(-0.64 * tail_len, 0.14 * tail, 0.2), (-0.46, 0.07 * tail, 0.25), (-0.26, 0.0, 0.3), (0.0, 0.0, 0.33 * s),
             (0.2, 0.0, 0.4), (0.28 + 0.02 * nl, 0.03 * sw, 0.45 + 0.1 * nl), (0.33, 0.08 * sw, 0.5 + 0.22 * nl),
             (hx - 0.04, 0.12 * sw, hz - 0.06 - 0.02 * head_tilt)]
    radii = [0.05, 0.1, 0.2, 0.3, 0.24, 0.17 - 0.02 * nl, 0.14 - 0.01 * nl, 0.13]
    elems = kit.chain(spine, radii, steps=7)
    head_c = Vector((hx, 0.12 * sw, hz - 0.02 * head_tilt))
    elems.append({"co": tuple(head_c), "r": 0.24, "type": "ELLIPSOID", "size": (1.15, 0.92, 0.85), "stiff": 2.0})
    elems.append({"co": tuple(head_c + Vector((0.12, 0, -0.03))), "r": 0.17, "stiff": 2.0})
    if "dome" in sp["x"]:
        elems.append({"co": tuple(head_c + Vector((-0.02, 0, 0.12))), "r": 0.2, "stiff": 2.0})
    bo = kit.to_mesh(kit.blob(elems, skin, name="dino", parent=body))
    surf = kit.Surface([bo])
    W = lambda loc: kit.world(body, loc)  # noqa: E731

    def stick(o, p, n):
        kit.place_on(o, p, n)
        o.parent = body
        o.matrix_parent_inverse = body.matrix_world.inverted()
        return o

    def top_point(x, y=0.0):
        return surf.toward(W((x, y, 0.3)), Vector((0, 0, 1)))

    belly = mat("dino_belly", DINO_BELLY, rough=0.6, spec=0.2, edge=0.4, edge_color="#B5A47A")
    p, n = surf.toward(W((0.05, 0, 0.33)), kit.world(root, (0.8, -0.35, -0.45)) - kit.world(root, (0, 0, 0)))
    if p is not None:
        stick(kit.sphere(0.12, belly, scale=(1.0, 1.0, 0.18), seg=20), p - n * 0.012, n)
    rng = __import__("random").Random(len(species))
    for i in range(8):
        a = rng.uniform(0, 2 * math.pi)
        x = rng.uniform(-0.3, 0.2)
        d = kit.world(root, (x * 0.4, math.cos(a) * 0.5, 0.9)) - kit.world(root, (0, 0, 0))
        p, n = surf.toward(W((x, 0, 0.3)), d)
        if p is not None:
            stick(kit.sphere(rng.uniform(0.04, 0.07), spot, scale=(1.0, 1.0, 0.2), seg=16), p - n * 0.008, n)

    x_ = sp["x"]
    # --- back extras
    if "plates_soft" in x_ or "plates_big" in x_:
        big = "plates_big" in x_
        pm = mat("plate_" + species, "#F2A23A" if big else sp["spot"], rough=0.5, spec=0.3, edge=0.45)
        for i, x in enumerate((0.12, -0.04, -0.2, -0.36) if big else (0.1, -0.06, -0.22, -0.38)):
            p, n = top_point(x)
            if p is not None:
                o = kit.sphere((0.1 if big else 0.065) - i * 0.012, pm, scale=(1.0, 0.3, 1.15), seg=16)
                o.location = p + Vector((0, 0, 0.05 if big else 0.02))
                o.rotation_euler = (0, 0, math.radians(yaw))
                o.parent = body
                o.matrix_parent_inverse = body.matrix_world.inverted()
    if "sail" in x_:
        sm = mat("sail_" + species, "#FFC2A0", rough=0.5, edge=0.5, edge_color=sp["edge"])
        for i, x in enumerate((0.15, 0.0, -0.15, -0.3)):
            p, n = top_point(x)
            if p is not None:
                h = 0.16 if i in (1, 2) else 0.11
                o = kit.sphere(h, sm, scale=(0.75, 0.12, 1.0), seg=16)
                o.location = p + Vector((0, 0, h * 0.55))
                o.rotation_euler = (0, 0, math.radians(yaw))
                o.parent = body
                o.matrix_parent_inverse = body.matrix_world.inverted()
    if "spikes" in x_ or "armor" in x_:
        km = mat("spike_" + species, "#FFF0D0" if "spikes" in x_ else sp["spot"], rough=0.4, edge=0.45)
        pts = [(x, y) for x in (0.15, 0.0, -0.15, -0.3) for y in ((-0.12, 0.12) if "armor" in x_ else (0.0,))]
        for x, y in pts:
            p, n = top_point(x, y)
            if p is not None:
                o = kit.cyl(0.035 if "spikes" in x_ else 0.06, 0.09 if "spikes" in x_ else 0.04, km,
                            r2=0.004 if "spikes" in x_ else 0.03, bevel=0.0, verts=10)
                stick(o, p - n * 0.01, n)
    if "fluff" in x_:
        fm = __import__("blender.assets.nature", fromlist=["x"]).foliage_mat("fluff_" + species, "#FFF2B0", sp["spot"],
                                                                             noise_scale=24.0, z0=0.3, z1=1.0)
        nat = __import__("blender.assets.nature", fromlist=["x"])
        for x in (0.1, -0.08, -0.26):
            p, n = top_point(x)
            if p is not None:
                nat.leaf_clump(tuple(p + Vector((0, 0, 0.02))), 0.08, fm, rng, parent=None, squash=0.7)
        nat.leaf_clump(tuple(W(head_c + Vector((-0.05, 0, 0.2)))), 0.08, fm, rng, parent=None, squash=0.8)
    # --- tail extras
    if "club" in x_:
        cm = mat("club_" + species, sp["spot"], rough=0.5, edge=0.45)
        kit.sphere(0.1, cm, loc=(-0.8, 0.14 * tail, 0.2), scale=(1.2, 1.0, 0.75), seg=18, parent=body)
    if "tail_spikes" in x_:
        km = mat("spike_t_" + species, "#FFF0D0", rough=0.4, edge=0.45)
        for y in (-1, 1):
            kit.cyl(0.025, 0.12, km, r2=0.003, loc=(-0.56, 0.12 * tail, 0.24), rot=(y * 0.9, -0.5, 0), bevel=0.0,
                    verts=8, parent=body)
    # --- head extras
    hw = W(head_c)
    if "frill" in x_:
        fr = mat("frill_" + species, "#FFD0A8", rough=0.5, edge=0.5, edge_color=sp["edge"])
        o = kit.sphere(0.24, fr, loc=head_c + Vector((-0.14, 0, 0.1)), scale=(0.25, 1.0, 0.85),
                       rot=(0, math.radians(-25), 0), seg=24, parent=body)
        for k in range(5):
            a = -1.0 + k * 0.5
            kit.sphere(0.035, spot, loc=head_c + Vector((-0.17, math.sin(a) * 0.22, 0.1 + math.cos(a) * 0.19)),
                       seg=10, parent=body)
    if "horns3" in x_:
        hm = mat("horn", "#F4E6C4", rough=0.4, edge=0.35)
        kit.cyl(0.035, 0.11, hm, r2=0.005, loc=head_c + Vector((0.2, 0, 0.06)), rot=(0, 0.6, 0), bevel=0.0, verts=10,
                parent=body)
        for y in (-1, 1):
            kit.cyl(0.03, 0.13, hm, r2=0.004, loc=head_c + Vector((0.02, y * 0.11, 0.15)), rot=(y * -0.3, 0.5, 0),
                    bevel=0.0, verts=10, parent=body)
    if "crest" in x_:
        cm = mat("crest_" + species, "#FFB0C8", rough=0.45, edge=0.5, edge_color=sp["edge"])
        kit.curve_tube([tuple(head_c + Vector((0.0, 0, 0.12))), tuple(head_c + Vector((-0.15, 0, 0.22))),
                        tuple(head_c + Vector((-0.32, 0, 0.24)))], r=0.045, m=cm, parent=body)
    if "dome" in x_:
        for k in range(6):
            a = k / 6 * 2 * math.pi
            kit.sphere(0.03, spot, loc=head_c + Vector((-0.02 + 0.16 * math.cos(a) * 0.6, 0.16 * math.sin(a), 0.2)),
                       seg=10, parent=body)

    cheek = mat("dino_cheek", "#FF9EAA", rough=0.6, edge=0.2)
    look = _rotz(kit.TO_CAM, -yaw)
    for side in (-1, 1):
        dl = Vector((0.72, side * 0.6, 0.32))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            hr = (body.matrix_world.inverted() @ p - head_c).length
            eye(head_c, hr, dl, 0.068, body, look=look, lid=blink, lid_color=sp["skin"])
        dl = Vector((0.65, side * 0.7, -0.15))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            stick(kit.sphere(0.04, cheek, scale=(1.0, 1.0, 0.25), seg=12), p, n)
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
    for species in DINOS:
        for facing, yaw in (("se", 0.0), ("ne", 90.0)):
            for i in range(6):
                w = math.sin(i / 6 * 2 * math.pi)
                out[f"dino_{species}_idle_{facing}_{i}"] = (lambda w=w, i=i, yaw=yaw, sp=species: dino(
                    yaw, sp, neck=10 * w, head_tilt=0.5 + 0.5 * w, tail=0.6 * w, squash=0.015 * w,
                    blink=1.0 if i == 4 else 0.0))
            for i in range(8):
                t = i / 8.0
                sw = math.sin(t * 2 * math.pi)
                out[f"dino_{species}_walk_{facing}_{i}"] = (lambda sw=sw, t=t, yaw=yaw, sp=species: dino(
                    yaw, sp, neck=4 * sw, legs=(22 * sw, -22 * sw),
                    body_z=0.018 * abs(math.cos(t * 2 * math.pi)), tail=-0.8 * sw))
    return out


# ---------------------------------------------------------------- cow

COW_WHITE = "#FFF7EE"
COW_SPOT = "#6E4A33"


def patched_mat(name, base, patch, scale=2.2, cut=0.56, edge_color="#B7A58E"):
    """Hide with flat, organic patches painted into the material (no raised blobs)."""
    import bpy
    key = ("patched", name)
    if key in kit._mats:
        return kit._mats[key]
    m = kit.mat(name, base, rough=0.55, spec=0.22, edge=0.55, edge_color=edge_color, sss=0.04)
    m = m.copy()
    m.name = name + "_p"
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    src = bsdf.inputs["Base Color"].links[0].from_node if bsdf.inputs["Base Color"].is_linked else None
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 1.2
    nz.inputs["Roughness"].default_value = 0.45
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "EASE"
    ramp.color_ramp.elements[0].position = cut - 0.015
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = cut + 0.015
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(ramp.outputs["Color"], mix.inputs["Factor"])
    if src is not None:
        nt.links.new(src.outputs[0], mix.inputs["A"])
    else:
        mix.inputs["A"].default_value = kit.lin(base)
    mix.inputs["B"].default_value = kit.lin(patch)
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    kit._mats[key] = m
    return m


def cow(yaw: float, body_z=0.0, head=(0.0, 0.0), legs=(0.0, 0.0), tail=0.0, blink=0.0, squash=0.0, chew=0.0):
    """Chibi dairy cow, ~0.8 m tall. head: (forward, down) offset.
    Rebuilt in the style of the approved hen: contrast light, parts sit on the real surface (ray cast)."""
    kit.character_light()
    root = kit.empty("cow", rot=(0, 0, math.radians(yaw)))
    body = kit.empty("body", loc=(0, 0, body_z), parent=root)
    s = 1.0 + squash
    hide = patched_mat("cow_hide", "#FFFFFF", COW_SPOT, scale=2.6, cut=0.52)
    hx, hd = head
    head_c = Vector((0.4 + hx, 0.0, 0.72 - hd))
    bo = kit.to_mesh(kit.blob(
        kit.chain([(-0.3, 0, 0.44), (-0.08, 0, 0.47 * s), (0.14, 0, 0.47), (0.27 + hx * 0.5, 0, 0.56 - hd * 0.5)],
                  [0.3, 0.36, 0.33, 0.22], steps=6)
        + [{"co": tuple(head_c), "r": 0.3, "type": "ELLIPSOID", "size": (1.0, 1.0, 0.95), "stiff": 2.0}],
        hide, name="cow", parent=body))
    surf = kit.Surface([bo])
    look = _rotz(kit.TO_CAM, -yaw)

    spot = mat("cow_spot", COW_SPOT, rough=0.55, spec=0.2, edge=0.4)
    # muzzle, nostrils
    pink = mat("cow_muzzle", "#FFB2A6", rough=0.45, spec=0.3, edge=0.5, edge_color="#B0645E")
    hw0 = kit.world(body, head_c)
    to_local = body.matrix_world.inverted()
    o_w = kit.world(root, (0, 0, 0))

    def on_head(d):
        p, _n = surf.toward(hw0, kit.world(root, d) - o_w)
        return (to_local @ p) if p is not None else head_c + Vector(d).normalized() * 0.2

    # big wide muzzle grown out of the face (its centre sits just inside the head surface)
    face = on_head((1.0, 0, -0.35))
    mz = face + Vector((0.06, 0, -0.01))
    kit.sphere(0.165, pink, loc=mz, scale=(0.78, 1.18, 0.82), seg=28, parent=body)
    nos = mat("cow_nostril", "#8A4A44", rough=0.6, edge=0.0)
    for side in (-1, 1):
        kit.sphere(0.026, nos, loc=mz + Vector((0.12, side * 0.065, 0.025)), scale=(0.55, 1, 1.35), seg=12,
                   parent=body)
    # mouth chew: tiny lower lip bob
    kit.sphere(0.06, pink, loc=mz + Vector((0.05, 0, -0.1 - 0.015 * chew)), scale=(1.0, 1.4, 0.5), seg=14, parent=body)
    # eyes
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.6, side * 0.62, 0.42))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            hr = (body.matrix_world.inverted() @ p - head_c).length
            eye(head_c, hr, dl, 0.07, body, look=look, lid=blink, lid_color=COW_WHITE, droop=0.22)
            if blink < 0.5:  # three lashes on the lid edge
                ec = head_c + dl.normalized() * hr
                lash = mat("cow_lash", "#2A1E18", rough=0.5, edge=0.0)
                for k in (-1, 0, 1):
                    kit.cyl(0.006, 0.04, lash, r2=0.002, loc=ec + Vector((0.01, side * 0.02 + k * 0.022, 0.05)),
                            rot=(side * -0.6 + k * 0.4, -0.5, 0), verts=6, bevel=0.0, parent=body)
    # ears and horns
    horn = mat("horn", "#F6E8C8", rough=0.35, spec=0.4, edge=0.45, edge_color="#9A845A")
    for side in (-1, 1):
        ear_p = on_head((-0.15, side * 1.0, 0.35))
        ear = kit.empty("ear", loc=ear_p, rot=(side * 0.35, 0.1, 0), parent=body)
        kit.sphere(0.085, hide, loc=(0, side * 0.07, 0), scale=(0.7, 1.3, 0.42), seg=18, parent=ear)
        kit.sphere(0.05, pink, loc=(0.01, side * 0.08, 0.01), scale=(0.6, 1.05, 0.28), seg=14, parent=ear)
        hp = on_head((-0.1, side * 0.45, 1.0))
        kit.cyl(0.042, 0.16, horn, r2=0.014, loc=hp - (hp - head_c).normalized() * 0.025,
                rot=(side * -0.55, -0.25, 0), bevel=0.0, verts=14, parent=body)
    # brown forelock tuft between the horns
    top = on_head((0.25, 0, 1.0))
    for k, (dx, dy) in enumerate([(0.0, 0.0), (0.02, 0.04), (0.02, -0.04)]):
        kit.sphere(0.05, spot, loc=top + Vector((dx, dy, 0.015)), scale=(1.2, 0.8, 0.55),
                   rot=(0, 0.4, dy * 6), seg=14, parent=body)
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
        kit.blob(kit.chain([(0, 0, 0.0), (0, 0, -0.16), (0, 0, -0.25)], [0.11, 0.09, 0.085], steps=5),
                 hide, name="leg", parent=hip)
        for cy in (-0.022, 0.022):  # cloven hoof
            kit.cyl(0.042, 0.07, hoof, r2=0.038, loc=(0.005, cy, -0.31), bevel=0.015, verts=14, parent=hip,
                    scale=(1.15, 0.75, 1.0))
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
    """Soft cloud wool (smooth puffs read better than a speckled texture)."""
    return mat("wool_soft", "#FFFDF7", rough=0.85, spec=0.12, edge=0.5, edge_color="#B8AE9C", sss=0.12)


def sheep(yaw: float, body_z=0.0, head=(0.0, 0.0), legs=(0.0, 0.0), blink=0.0, squash=0.0):
    """Fluffy chibi sheep, ~0.65 m tall, in the approved hen/cow style: a dense round cloud of wool, a long dark
    face with big lidded eyes, droopy ears and a wool cap that sit on the real surface, dark legs with hooves."""
    import random as _r
    kit.character_light()
    rng = _r.Random(3)
    root = kit.empty("sheep", rot=(0, 0, math.radians(yaw)))
    body = kit.empty("body", loc=(0, 0, body_z), parent=root)
    s = 1.0 + squash
    wool = _wool_mat()
    nature = __import__("blender.assets.nature", fromlist=["x"])
    # a solid core so the cloud never shows gaps, then many puffs over it
    kit.sphere(0.3, wool, loc=(-0.04, 0, 0.45 * s), scale=(1.2, 0.95, 0.85), seg=24, parent=body)
    for x, y, z, r in [(0, 0, 0.6, 0.2), (-0.2, 0.12, 0.5, 0.19), (-0.2, -0.12, 0.5, 0.19), (0.14, 0.13, 0.5, 0.18),
                       (0.14, -0.13, 0.5, 0.18), (-0.06, 0.2, 0.42, 0.17), (-0.06, -0.2, 0.42, 0.17),
                       (-0.32, 0, 0.47, 0.15), (0.2, 0, 0.6, 0.15), (-0.18, 0, 0.64, 0.16), (0.04, 0.16, 0.62, 0.14),
                       (0.04, -0.16, 0.62, 0.14), (-0.12, 0.17, 0.32, 0.13), (-0.12, -0.17, 0.32, 0.13),
                       (0.12, 0.1, 0.33, 0.13), (0.12, -0.1, 0.33, 0.13)]:
        nature.leaf_clump((x, y, z * s), r, wool, rng, parent=body, squash=0.95, bumps=0.14)
    face = mat("sheep_face", "#3E3836", rough=0.55, spec=0.25, edge=0.5, edge_color="#151212")
    hx, hd = head
    head_c = Vector((0.42 + hx, 0, 0.55 - hd))
    ho = kit.to_mesh(kit.blob([{"co": tuple(head_c), "r": 0.19, "type": "ELLIPSOID", "size": (1.2, 0.85, 0.95),
                                "stiff": 2.0},
                               {"co": tuple(head_c + Vector((0.13, 0, -0.06))), "r": 0.12, "stiff": 2.0}],
                              face, name="shead", parent=body))
    surf = kit.Surface([ho])
    hw = kit.world(body, head_c)
    to_local = body.matrix_world.inverted()
    o_w = kit.world(root, (0, 0, 0))

    def on_head(d):
        p, _n = surf.toward(hw, kit.world(root, d) - o_w)
        return (to_local @ p) if p is not None else head_c + Vector(d).normalized() * 0.17

    # wool cap sitting on the top of the head
    cap = on_head((-0.3, 0, 1.0))
    nature.leaf_clump(cap + Vector((0.02, 0, 0.02)), 0.12, wool, rng, parent=body, squash=0.8, bumps=0.14)
    look = _rotz(kit.TO_CAM, -yaw)
    inner = mat("sheep_ear_in", "#D98A8A", rough=0.6, edge=0.3)
    for side in (-1, 1):
        dl = Vector((0.55, side * 0.6, 0.3))
        p, n = surf.toward(hw, kit.world(root, dl) - o_w)
        if p is not None:
            hr = (to_local @ p - head_c).length
            eye(head_c, hr, dl, 0.07, body, look=look, lid=blink, lid_color="#3E3836", droop=0.22)
        ear_p = on_head((-0.2, side * 1.0, 0.25))
        ear = kit.empty("ear", loc=ear_p, rot=(side * 0.55, 0.15, 0), parent=body)
        kit.sphere(0.085, face, loc=(0, side * 0.07, -0.01), scale=(0.55, 1.4, 0.38), seg=16, parent=ear)
        kit.sphere(0.055, inner, loc=(0.012, side * 0.08, -0.005), scale=(0.45, 1.15, 0.25), seg=12, parent=ear)
    nose = on_head((1.0, 0, -0.25))
    nos = mat("sheep_nose", "#1A1414", rough=0.5, edge=0.0)
    for side in (-1, 1):
        kit.sphere(0.018, nos, loc=nose + Vector((0.0, side * 0.035, 0.0)), scale=(0.6, 1.0, 1.3), seg=10,
                   parent=body)
    for (lx, ly, ang) in ((0.14, -0.12, legs[0]), (0.14, 0.12, legs[1]), (-0.2, -0.12, legs[1]),
                          (-0.2, 0.12, legs[0])):
        hip = kit.empty("hip", loc=(lx, ly, 0.27), rot=(0, math.radians(ang), 0), parent=root)
        kit.cyl(0.05, 0.25, face, r2=0.042, loc=(0, 0, -0.25), bevel=0.02, verts=14, parent=hip)
        for cy in (-0.018, 0.018):
            kit.cyl(0.03, 0.05, mat("sheep_hoof", "#1E1A1A", rough=0.4, spec=0.4), r2=0.028,
                    loc=(0.004, cy, -0.27), bevel=0.01, verts=12, parent=hip, scale=(1.15, 0.8, 1.0))
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
    snout_m = mat("pig_snout", "#FF9AA2", rough=0.4, spec=0.35, edge=0.5, edge_color="#A8505C")
    sn = head_c + Vector((0.16, 0, -0.04))
    kit.cyl(0.1, 0.1, snout_m, r2=0.095, loc=sn, rot=(0, math.radians(90), 0), bevel=0.035, verts=28, parent=body)
    nos = mat("pig_nostril", "#8A3442", rough=0.6, edge=0.0)
    for side in (-1, 1):
        kit.sphere(0.024, nos, loc=sn + Vector((0.1, side * 0.038, 0.005)), scale=(0.45, 1, 1.4), seg=10, parent=body)
    # a happy mouth under the snout
    kit.curve_tube([tuple(sn + Vector((0.05, -0.07, -0.085))), tuple(sn + Vector((0.08, 0.0, -0.105))),
                    tuple(sn + Vector((0.05, 0.07, -0.085)))], r=0.008, m=nos, parent=body)
    look = _rotz(kit.TO_CAM, -yaw)
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.62, side * 0.55, 0.42))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        if p is not None:
            hr = (body.matrix_world.inverted() @ p - head_c).length
            eye(head_c, hr, dl, 0.062, body, look=look, lid=blink, lid_color=PIG_PINK, droop=0.22)
        # big floppy ears folding forward
        ear = kit.empty("ear", loc=head_c + Vector((0.0, side * 0.12, 0.15)), rot=(side * -0.35, 1.25, 0),
                        parent=body)
        kit.sphere(0.1, skin, loc=(0.06, 0, 0), scale=(1.0, 0.75, 0.22), seg=16, parent=ear)
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
        hip = kit.empty("hip", loc=(lx, ly, 0.2), rot=(0, math.radians(ang), 0), parent=root)
        kit.cyl(0.075, 0.17, skin, r2=0.06, loc=(0, 0, -0.17), bevel=0.03, verts=16, parent=hip)
        kit.sphere(0.075, skin, loc=(0, 0, 0.0), seg=14, parent=hip)
        kit.cyl(0.062, 0.045, hoof, r2=0.058, loc=(0, 0, -0.2), bevel=0.015, verts=16, parent=hip)
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
