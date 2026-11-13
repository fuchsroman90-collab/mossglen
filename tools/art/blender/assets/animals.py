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


def feather_mat(name, light="#FFFFFF", dark="#E4DACB", scale=55.0, bump=0.25, stretch=(1.0, 1.0, 2.2)):
    """Feathery surface: soft scale pattern in colour and bump, a little greyer towards the belly."""
    import bpy
    key = ("feather", name)
    if key in kit._mats:
        return kit._mats[key]
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = stretch
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "F1"
    vor.inputs["Scale"].default_value = scale
    nt.links.new(mp.outputs["Vector"], vor.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = kit.lin(light)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = kit.lin(dark)
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.02
    nt.links.new(vor.outputs["Distance"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    bsdf.inputs["Subsurface Weight"].default_value = 0.05
    kit._mats[key] = m
    return m


def chicken(yaw: float, body_z=0.0, body_pitch=0.0, head=(0.0, 0.0), legs=(0.0, 0.0),
            wing=0.0, blink=0.0, squash=0.0):
    """Hen, rebuilt after Roman's feedback ("schrecklich", then "besser aber noch unnatürlich", 2026-11-13):
    natural bird proportions - egg-shaped body, slim neck with hackle feathers, small head with side eyes and an
    orange iris, curved beak, layered wing and sickle tail feathers, scaly legs with claws; feathery surface.
    Local +X is forward. head: (forward, down) offset; legs: swing angles (right, left)."""
    kit.character_light()
    root = kit.empty("chicken", rot=(0, 0, math.radians(yaw)))
    pz = HEN_PIVOT
    body = kit.empty("body", loc=(0, 0, pz + body_z), rot=(0, math.radians(body_pitch), 0), parent=root)
    s = 1.0 + squash
    plume = feather_mat("hen_plume")
    quill = feather_mat("hen_quill", "#FCF8F1", "#D9CCB8", scale=28.0, bump=0.35, stretch=(3.0, 1.0, 1.0))
    hx, hd = head
    head_c = Vector((0.21 + hx, 0.0, 0.53 - hd - pz))
    neck = kit.chain([(0.09, 0, 0.3 - pz), (0.17 + hx * 0.4, 0, 0.39 - hd * 0.4 - pz),
                      (0.2 + hx * 0.85, 0, 0.47 - hd * 0.85 - pz)], [0.105, 0.075, 0.08], steps=6, stiff=2.0)
    hen = kit.to_mesh(kit.blob([
        # egg-shaped body: deep breast, back rising to the tail
        {"co": (-0.02, 0.0, 0.24 * s - pz), "r": 0.21, "type": "ELLIPSOID", "size": (1.3, 0.92, 0.88 / s),
         "stiff": 1.8},
        {"co": (0.1, 0.0, 0.25 - pz), "r": 0.14, "stiff": 1.8},
        {"co": (-0.16, 0.0, 0.31 - pz), "r": 0.11, "stiff": 1.8},
        {"co": tuple(head_c), "r": 0.1, "type": "ELLIPSOID", "size": (1.25, 0.9, 0.95), "stiff": 2.2},
    ] + neck, plume, name="hen", res=0.009, parent=body))
    surf = kit.Surface([hen])

    # hackles: pointed neck feathers flowing down over the shoulders
    rng = random.Random(11)
    for i in range(14):
        a = -2.3 + i * (4.6 / 13)
        base = Vector((0.13 + hx * 0.5, 0, 0.36 - hd * 0.5 - pz)) + Vector((math.cos(a) * 0.035, math.sin(a) * 0.07, 0))
        fe = kit.empty("hk", loc=base, rot=(math.sin(a) * 0.6, math.radians(-120 + rng.uniform(-8, 8)), 0),
                       parent=body)
        kit.sphere(0.04, quill, loc=(0, 0, 0.05), scale=(0.55, 0.32, 1.8), seg=12, parent=fe)

    # tail: sickle feathers of different lengths, curving up and back
    for rl, pt, ln in [(-18, -22, 0.85), (-9, -15, 1.0), (0, -8, 1.15), (9, -15, 1.0), (18, -22, 0.85)]:
        f = kit.empty("tf", loc=(-0.21, 0, 0.33 - pz), rot=(math.radians(rl), math.radians(pt), 0), parent=body)
        kit.sphere(0.05, quill, loc=(0, 0, 0.08 * ln), scale=(0.75, 0.22, 1.7 * ln), seg=16, parent=f)
        tip = kit.empty("tip", loc=(0, 0, 0.15 * ln), rot=(0, math.radians(-35), 0), parent=f)
        kit.sphere(0.04, quill, loc=(0, 0, 0.05 * ln), scale=(0.7, 0.2, 1.5 * ln), seg=14, parent=tip)

    # wings: rounded covert + four primaries layered towards the back
    for side in (-1, 1):
        wg = kit.empty("wing", loc=(0.0, side * 0.165, 0.27 - pz),
                       rot=(math.radians(side * (5 + wing * 35)), math.radians(-10), 0), parent=body)
        kit.sphere(0.13, plume, loc=(0.02, 0, 0.0), scale=(0.95, 0.24, 0.6), seg=24, parent=wg)
        for k in range(4):
            kit.sphere(0.05, quill, loc=(-0.07 - k * 0.025, side * (0.004 + k * 0.003), -0.02 + k * 0.018),
                       scale=(1.5, 0.16, 0.42), rot=(0, math.radians(-12 - k * 4), 0), seg=14, parent=wg)

    # comb (a single serrated blade), wattles, curved beak
    red = mat("comb", "#E63A2C", rough=0.45, spec=0.35, coat=0.15, edge=0.45, edge_color="#8A1A10", sss=0.15)
    for dx, dz, r in [(0.06, 0.075, 0.03), (0.03, 0.095, 0.036), (-0.005, 0.1, 0.038), (-0.04, 0.09, 0.034),
                      (-0.07, 0.07, 0.026)]:
        kit.sphere(r, red, loc=head_c + Vector((dx, 0, dz)), scale=(0.8, 0.38, 1.15), seg=16, parent=body)
    kit.sphere(0.05, red, loc=head_c + Vector((0.0, 0, 0.065)), scale=(1.6, 0.35, 0.5), seg=16, parent=body)
    for side in (-1, 1):
        kit.sphere(0.026, red, loc=head_c + Vector((0.085, side * 0.016, -0.075)), scale=(0.7, 0.5, 1.4), seg=14,
                   parent=body)
        kit.sphere(0.018, red, loc=head_c + Vector((0.0, side * 0.075, -0.02)), scale=(0.6, 0.4, 1.0), seg=10,
                   parent=body)  # ear lobe
    beak = mat("beak", "#F7B43A", rough=0.35, spec=0.45, coat=0.2, edge=0.5, edge_color="#A0601A")
    kit.cyl(0.03, 0.075, beak, r2=0.003, loc=head_c + Vector((0.105, 0, 0.0)), rot=(0, math.radians(104), 0),
            bevel=0.0, verts=18, parent=body, scale=(1.0, 0.9, 1.0))
    kit.cyl(0.02, 0.05, beak, r2=0.003, loc=head_c + Vector((0.1, 0, -0.022)), rot=(0, math.radians(82), 0),
            bevel=0.0, verts=14, parent=body)

    # bird eyes on the sides of the head: orange iris, black pupil, a soft lid
    look = _rotz(kit.TO_CAM, -yaw)
    hw = kit.world(body, head_c)
    for side in (-1, 1):
        dl = Vector((0.35, side * 0.9, 0.22))
        p, n = surf.toward(hw, kit.world(root, dl) - kit.world(root, (0, 0, 0)))
        hr = (body.matrix_world.inverted() @ p - head_c).length if p is not None else 0.1
        eye(head_c, hr, dl, 0.03, body, look=look, lid=blink, lid_color="#F4EEE6", droop=0.1,
            sclera="#F59A2E", pupil="#14100C")

    # legs: yellow, scaly, with a feather "trouser", three long toes with claws and a spur
    leg = feather_mat("hen_leg", "#F7B23A", "#D98A20", scale=70.0, bump=0.3, stretch=(1.0, 1.0, 3.0))
    claw = mat("claw", "#5A4A3A", rough=0.4, spec=0.4)
    for side, ang in ((-1, legs[0]), (1, legs[1])):
        hip = kit.empty("hip", loc=(0.01, side * 0.075, 0.13 + body_z * 0.5), rot=(0, math.radians(ang), 0),
                        parent=root)
        kit.sphere(0.055, plume, loc=(0, 0, 0.03), scale=(1.1, 0.85, 1.0), seg=16, parent=hip)
        kit.cyl(0.017, 0.12, leg, r2=0.014, loc=(0, 0, -0.125), bevel=0.0, verts=12, parent=hip)
        for toe in (-32, 0, 32):
            a = math.radians(toe)
            kit.sphere(0.016, leg, loc=(0.05 * math.cos(a), 0.05 * math.sin(a), -0.12),
                       scale=(3.2, 0.75, 0.6), rot=(0, 0, a), seg=12, parent=hip)
            kit.sphere(0.008, claw, loc=(0.1 * math.cos(a), 0.1 * math.sin(a), -0.122), scale=(1.6, 0.8, 0.7),
                       rot=(0, 0, a), seg=8, parent=hip)
        kit.sphere(0.012, leg, loc=(-0.04, 0, -0.118), scale=(2.0, 0.8, 0.6), seg=10, parent=hip)
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
            eye(head_c, hr, dl, 0.066, body, look=look, lid=blink, lid_color="#4C4645", droop=0.24)
        kit.sphere(0.075, face, loc=head_c + Vector((-0.04, side * 0.2, 0.01)), scale=(0.55, 1.6, 0.4),
                   rot=(side * -0.35, 0, 0), seg=14, parent=body)
        kit.sphere(0.05, mat("sheep_ear_in", "#E89A9A", rough=0.6), loc=head_c + Vector((-0.02, side * 0.21, 0.012)),
                   scale=(0.4, 1.2, 0.2), rot=(side * -0.35, 0, 0), seg=12, parent=body)
    kit.sphere(0.025, mat("sheep_nose", "#2A2424", rough=0.5, edge=0.0), loc=head_c + Vector((0.2, 0, -0.04)),
               scale=(0.6, 1.2, 0.7), seg=10, parent=body)
    for (lx, ly, ang) in ((0.14, -0.1, legs[0]), (0.14, 0.1, legs[1]), (-0.18, -0.1, legs[1]), (-0.18, 0.1, legs[0])):
        hip = kit.empty("hip", loc=(lx, ly, 0.27), rot=(0, math.radians(ang), 0), parent=root)
        kit.cyl(0.05, 0.25, face, r2=0.042, loc=(0, 0, -0.25), bevel=0.02, verts=14, parent=hip)
        kit.cyl(0.05, 0.05, mat("sheep_hoof", "#2A2424", rough=0.4, spec=0.4), r2=0.046, loc=(0, 0, -0.27),
                bevel=0.012, verts=14, parent=hip)
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
