"""Trees, bushes, rocks, flowers. Leafy look from many displaced leaf clumps."""
from __future__ import annotations

import math
import random

import bpy
from mathutils import Vector

from .. import kit
from ..kit import lin, mat


def foliage_mat(name, light, dark, noise_scale=7.0, rough=0.75, z0=0.6, z1=2.0):
    """Leaf material: speckled light/dark mix + top light, dark rim."""
    key = ("foliage", name)
    if key in kit._mats:
        return kit._mats[key]
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexVoronoi")
    noise.inputs["Scale"].default_value = noise_scale
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = lin(light)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = lin(dark)
    ramp.color_ramp.interpolation = "EASE"
    nt.links.new(noise.outputs["Distance"], ramp.inputs["Fac"])
    # darker towards the bottom of the plant (world height)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    hz = nt.nodes.new("ShaderNodeMapRange")
    hz.inputs["From Min"].default_value = z0
    hz.inputs["From Max"].default_value = z1
    hz.inputs["To Min"].default_value = 0.55
    hz.inputs["To Max"].default_value = 1.08
    nt.links.new(sep.outputs["Z"], hz.inputs["Value"])
    grad = nt.nodes.new("ShaderNodeMath")
    grad.operation = "MULTIPLY"
    # per-object jitter
    info = nt.nodes.new("ShaderNodeObjectInfo")
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.88
    mr.inputs["To Max"].default_value = 1.12
    nt.links.new(info.outputs["Random"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], grad.inputs[0])
    nt.links.new(hz.outputs["Result"], grad.inputs[1])
    nt.links.new(grad.outputs[0], hsv.inputs["Value"])
    nt.links.new(ramp.outputs["Color"], hsv.inputs["Color"])
    # dark rim
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[7].default_value = (0.35, 0.45, 0.3, 1.0)
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "MULTIPLY"
    fr.inputs[1].default_value = 0.6
    nt.links.new(lw.outputs["Facing"], fr.inputs[0])
    nt.links.new(fr.outputs[0], mix.inputs[0])
    nt.links.new(hsv.outputs["Color"], mix.inputs[6])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    # every voronoi cell bulges like a leaf
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.75
    bump.inputs["Distance"].default_value = 0.05
    nt.links.new(noise.outputs["Distance"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = 0.2
    bsdf.inputs["Subsurface Weight"].default_value = 0.08
    bsdf.inputs["Subsurface Radius"].default_value = (0.3, 0.6, 0.2)
    bsdf.inputs["Subsurface Scale"].default_value = 0.1
    kit._mats[key] = m
    return m


LEAF = ("#93CF3C", "#2C7A2C")
LEAF_AUTUMN = ("#FFC84A", "#D9752A")
PINE = ("#6DBE6A", "#1F6A44")


def leaf_clump(c, r, m, rng, parent=None, squash=0.85, bumps=0.22):
    """A leafy ball: subdivided sphere with voronoi bumps."""
    o = kit.ico(r, m, loc=c, scale=(1.0, 1.0, squash), sub=4, parent=parent,
                rot=(rng.random(), rng.random(), rng.random()))
    tex = bpy.data.textures.new("leafbumps", "VORONOI")
    tex.noise_scale = r * 0.55
    tex.distance_metric = "DISTANCE_SQUARED"
    d = o.modifiers.new("disp", "DISPLACE")
    d.texture = tex
    d.strength = -r * bumps * 1.3
    d.mid_level = 0.0
    d.texture_coords = "OBJECT"
    return o


def bark_mat():
    return mat("bark", "#8A5A3A", rough=0.85, spec=0.1, edge=0.5, var=0.06)


def trunk(h, r0, r1, parent=None, lean=(0, 0)):
    m = bark_mat()
    t = kit.cyl(r0, h, m, r2=r1, bevel=0.0, verts=20, parent=parent, rot=(lean[0], lean[1], 0))
    # root flare
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        kit.sphere(r0 * 0.7, m, loc=(math.cos(a) * r0 * 0.8, math.sin(a) * r0 * 0.8, 0.02),
                   scale=(1.6, 0.8, 0.5), rot=(0, 0, a), seg=14, parent=parent)
    return t


def oak(seed=1, colors=LEAF, height=1.7, width=1.0, apples=False):
    rng = random.Random(seed)
    root = kit.empty("oak")
    trunk(height * 0.62, 0.13 * width, 0.08 * width, parent=root)
    # a couple of branches
    m_bark = bark_mat()
    for a in (0.6, 2.6):
        kit.cyl(0.05, 0.45, m_bark, r2=0.03, bevel=0.0, verts=10, parent=root,
                loc=(0, 0, height * 0.42), rot=(math.cos(a) * 0.7, math.sin(a) * 0.7, 0))
    fm = foliage_mat(f"leaf_{colors[0]}", *colors)
    cz = height * 0.82
    clumps = [(0, 0, cz + 0.18, 0.55)]
    n = 7
    for i in range(n):
        a = i / n * 2 * math.pi + rng.uniform(-0.3, 0.3)
        rr = rng.uniform(0.38, 0.52) * width
        clumps.append((math.cos(a) * 0.48 * width, math.sin(a) * 0.48 * width,
                       cz + rng.uniform(-0.12, 0.12), rr))
    for i in range(3):
        a = rng.uniform(0, 2 * math.pi)
        clumps.append((math.cos(a) * 0.22, math.sin(a) * 0.22, cz + 0.42, rng.uniform(0.32, 0.4) * width))
    for x, y, z, r in clumps:
        leaf_clump((x, y, z), r, fm, rng, parent=root)
    if apples:
        m_apple = mat("apple", "#E83B3B", rough=0.3, spec=0.5, edge=0.4, coat=0.3)
        for i in range(14):
            x, y, z, r = clumps[1 + i % (len(clumps) - 1)]
            a = rng.uniform(0, 2 * math.pi)
            e = rng.uniform(-0.2, 0.6)
            d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
            if d.dot(kit.TO_CAM) < -0.1:
                d = -d
            p = Vector((x, y, z)) + d * (r * 0.86)
            kit.sphere(0.065, m_apple, loc=p, seg=16, parent=root)
    return root


def star_tier(r, h, points, m, parent, z, twist, droop=0.12):
    """Cone whose bottom rim is star shaped with drooping tips (one pine layer)."""
    import bmesh
    bm = bmesh.new()
    n = points * 2
    top = bm.verts.new((0, 0, h))
    ring = []
    for i in range(n):
        a = i / n * 2 * math.pi + twist
        rr = r if i % 2 == 0 else r * 0.62
        dz = -droop if i % 2 == 0 else 0.04
        ring.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, dz)))
    mid = bm.verts.new((0, 0, 0.08))
    for i in range(n):
        bm.faces.new((ring[i], ring[(i + 1) % n], top))
        bm.faces.new((ring[(i + 1) % n], ring[i], mid))
    me = bpy.data.meshes.new("tier")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("tier", me)
    kit.link(o)
    o.location = (0, 0, z)
    o.parent = parent
    kit.set_mat(o, m)
    for p in me.polygons:
        p.use_smooth = True
    kit.subsurf(o, 2)
    tex = bpy.data.textures.new("pinebumps", "VORONOI")
    tex.noise_scale = 0.09
    d = o.modifiers.new("disp", "DISPLACE")
    d.texture = tex
    d.strength = -0.035
    d.mid_level = 0.0
    d.texture_coords = "OBJECT"
    return o


def pine(seed=2, height=2.3):
    rng = random.Random(seed)
    root = kit.empty("pine")
    trunk(0.5, 0.1, 0.07, parent=root)
    fm = foliage_mat("pine", *PINE, noise_scale=11.0, z0=0.3, z1=height)
    tiers = 4
    for i in range(tiers):
        t = i / (tiers - 1)
        r = 0.74 - 0.46 * t
        z = 0.42 + i * (height - 0.75) / tiers
        h = 0.85 - 0.25 * t
        star_tier(r, h, 9, fm, root, z, rng.random() * 6)
    return root


def bush(seed=3, berries=False, scale=1.0, colors=LEAF):
    rng = random.Random(seed)
    root = kit.empty("bush")
    fm = foliage_mat(f"leaf_{colors[0]}", *colors)
    spots = [(0, 0, 0.26, 0.3), (0.22, -0.08, 0.2, 0.22), (-0.2, 0.06, 0.2, 0.22),
             (0.04, 0.2, 0.2, 0.22), (-0.04, -0.2, 0.18, 0.2)]
    for x, y, z, r in spots:
        leaf_clump((x * scale, y * scale, z * scale), r * scale, fm, rng, parent=root, squash=0.9)
    if berries:
        m_b = mat("berry", "#C43A6A", rough=0.25, spec=0.6, edge=0.35, coat=0.4)
        for i in range(16):
            x, y, z, r = spots[i % len(spots)]
            a = rng.uniform(-1.2, 1.2) + math.atan2(kit.TO_CAM.y, kit.TO_CAM.x)
            e = rng.uniform(-0.1, 0.9)
            d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
            p = Vector((x, y, z)) * scale + d * (r * scale * 0.88)
            kit.sphere(0.04, m_b, loc=p, seg=12, parent=root)
    return root


def moss_tufts(points, rng, parent=None, size=0.06):
    fm = foliage_mat("moss", "#8CC444", "#3F7E2A", noise_scale=34.0, z0=0.0, z1=0.4)
    for p in points:
        leaf_clump(p, size * rng.uniform(0.7, 1.2), fm, rng, parent=parent, squash=0.4, bumps=0.25)


def rock(seed=4, size=0.5):
    rng = random.Random(seed)
    root = kit.empty("rock")
    m = mat("stone", "#9F977F", rough=0.8, spec=0.15, edge=0.6, var=0.05)
    o = kit.ico(size * 0.5, m, loc=(0, 0, size * 0.18), scale=(1.15, 0.95, 0.65), sub=4, parent=root)
    kit.displace(o, strength=size * 0.18, scale=0.35, seed=seed)
    o2 = kit.ico(size * 0.3, m, loc=(size * 0.38, -size * 0.2, size * 0.08), scale=(1.1, 1.0, 0.7), sub=3,
                 parent=root)
    kit.displace(o2, strength=size * 0.1, scale=0.3, seed=seed + 1)
    pts = []
    for i in range(9):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.0, size * 0.3)
        top = size * 0.18 + size * 0.325 * math.sqrt(max(0.0, 1.0 - (r / (size * 0.55)) ** 2))
        pts.append((math.cos(a) * r - size * 0.05, math.sin(a) * r + size * 0.05, top + size * 0.02))
    moss_tufts(pts, rng, parent=root, size=size * 0.16)
    return root


FLOWER_COLORS = {
    "lavender": ("#9B7BE0", "#6F52C2"),
    "sun": ("#FFD23F", "#F29E1F"),
    "rose": ("#FF8FB3", "#E0507F"),
    "white": ("#FFFFFF", "#E8E4F0"),
}


def flowers(kind="lavender", seed=5, count=26, spread=0.42):
    """A small flower patch (decoration), ~1 tile."""
    rng = random.Random(seed)
    root = kit.empty("flowers")
    stem_m = mat("stem", "#5DA83A", rough=0.7, edge=0.4)
    fm = foliage_mat("leaf_low", "#9AD24A", "#4A9632", noise_scale=14.0, z0=0.0, z1=0.3)
    for i in range(9):
        leaf_clump((rng.uniform(-spread, spread) * 0.9, rng.uniform(-spread, spread) * 0.9, 0.05),
                   rng.uniform(0.11, 0.16), fm, rng, parent=root, squash=0.7)
    c1, c2 = FLOWER_COLORS[kind]
    pm = mat(f"petal_{kind}", c1, rough=0.55, spec=0.2, edge=0.35, var=0.06, sss=0.1)
    cm = mat("flower_center", "#FFB830" if kind != "sun" else "#8A4B1E", rough=0.6, edge=0.3)
    for i in range(count):
        x = rng.uniform(-spread, spread)
        y = rng.uniform(-spread, spread)
        h = rng.uniform(0.14, 0.24)
        kit.cyl(0.008, h, stem_m, loc=(x, y, 0), bevel=0.0, verts=6, parent=root)
        if kind == "lavender":
            for j in range(5):
                kit.sphere(0.026 - j * 0.003, pm, loc=(x, y, h + j * 0.028), scale=(1, 1, 1.3), seg=10,
                           parent=root)
        else:
            top = Vector((x, y, h))
            for j in range(5):
                a = j / 5 * 2 * math.pi
                kit.sphere(0.03, pm, loc=top + Vector((math.cos(a) * 0.032, math.sin(a) * 0.032, 0)),
                           scale=(1.2, 1.2, 0.45), seg=10, parent=root)
            kit.sphere(0.022, cm, loc=top + Vector((0, 0, 0.01)), seg=10, parent=root)
    return root


def fern_frond(base, length, yaw, droop, m, parent, width=0.05):
    """Curved fern frond: a bent tube with leaflet pairs."""
    pts = []
    for k in range(5):
        t = k / 4
        r = length * t
        z = length * (0.9 * t - droop * t * t)
        pts.append((base[0] + math.cos(yaw) * r, base[1] + math.sin(yaw) * r, base[2] + z))
    kit.curve_tube(pts, r=0.01, m=m, parent=parent)
    n = 8
    for k in range(1, n + 1):
        t = k / (n + 0.5)
        r = length * t
        z = length * (0.9 * t - droop * t * t)
        c = Vector((base[0] + math.cos(yaw) * r, base[1] + math.sin(yaw) * r, base[2] + z))
        wl = width * (1.5 - t * 0.9)
        for side in (-1, 1):
            a = yaw + side * 1.15
            kit.sphere(wl, m, loc=c + Vector((math.cos(a), math.sin(a), 0)) * wl * 0.9,
                       scale=(1.9, 0.75, 0.3), rot=(0, 0, a), seg=10, parent=parent)


def fern(seed=91, scale=1.0, n=9):
    rng = random.Random(seed)
    root = kit.empty("fern")
    m = mat("fern", "#5DB33C", rough=0.6, spec=0.2, edge=0.45, var=0.08, sss=0.1)
    for k in range(n):
        yaw = k / n * 2 * math.pi + rng.uniform(-0.2, 0.2)
        fern_frond((0, 0, 0.02), rng.uniform(0.45, 0.6) * scale, yaw + 0.0, rng.uniform(0.35, 0.6), m, root,
                   width=0.05 * scale)
    for k in range(4):
        yaw = k / 4 * 2 * math.pi + 0.4
        fern_frond((0, 0, 0.02), 0.4 * scale, yaw, 0.15, m, root, width=0.045 * scale)
    return root


def cycad(seed=92, height=0.9):
    rng = random.Random(seed)
    root = kit.empty("cycad")
    bark = mat("cycad_bark", "#8A6A4A", rough=0.85, edge=0.5, var=0.06)
    for k in range(7):
        kit.cyl(0.16 - k * 0.008, height / 7 + 0.02, bark, loc=(0, 0, k * height / 7), bevel=0.02, verts=14,
                parent=root, rot=(0, 0, k * 0.4))
    m = mat("cycad_leaf", "#4E9E3A", rough=0.6, spec=0.2, edge=0.45, var=0.08)
    for k in range(10):
        yaw = k / 10 * 2 * math.pi + rng.uniform(-0.15, 0.15)
        fern_frond((0, 0, height), rng.uniform(0.6, 0.8), yaw, 0.9, m, root, width=0.055)
    return root


def grass_tuft(seed=95, n=46, height=0.36):
    """Placeable grass tuft: a fan of bent blades, darker at the foot, bright tips."""
    rng = random.Random(seed)
    root = kit.empty("grass_tuft")
    dark = mat("tuft_dark", "#3F9A34", rough=0.6, spec=0.15, edge=0.4, var=0.06, sss=0.1)
    light = mat("tuft_light", "#8EDB4A", rough=0.55, spec=0.2, edge=0.45, var=0.08, sss=0.15)
    for k in range(n):
        yaw = rng.uniform(0, 2 * math.pi)
        lean = rng.uniform(0.05, 0.42)
        h = height * rng.uniform(0.55, 1.0) * (1.0 - lean * 0.5)
        r0 = rng.uniform(0.0, 0.1)
        base = (math.cos(yaw) * r0, math.sin(yaw) * r0, 0.0)
        pts = []
        for j in range(5):
            t = j / 4
            out = lean * h * (t ** 1.8) * 1.6
            pts.append((base[0] + math.cos(yaw) * out, base[1] + math.sin(yaw) * out, h * (t - 0.18 * t * t)))
        kit.curve_tube(pts, r=rng.uniform(0.007, 0.011), m=light if rng.random() < 0.45 else dark, parent=root)
    return root


def pumpkin(seed=96, size=0.24, pile=False):
    """Fat ribbed pumpkin with a curled stem; pile=True adds two small ones."""
    rng = random.Random(seed)
    root = kit.empty("pumpkin")
    skin = mat("pumpkin", "#F28A1E", rough=0.45, spec=0.3, edge=0.5, var=0.05)
    stem = mat("pumpkin_stem", "#6E8A3A", rough=0.7, edge=0.4)

    def one(c, r):
        for k in range(8):
            a = k / 8 * 2 * math.pi
            kit.sphere(r * 0.52, skin, loc=(c[0] + math.cos(a) * r * 0.5, c[1] + math.sin(a) * r * 0.5, c[2] + r * 0.62),
                       scale=(1.0, 1.0, 1.25), parent=root)
        kit.sphere(r * 0.6, skin, loc=(c[0], c[1], c[2] + r * 0.62), scale=(1, 1, 1.0), parent=root)
        kit.curve_tube([(c[0], c[1], c[2] + r * 1.15), (c[0] + r * 0.05, c[1], c[2] + r * 1.45),
                        (c[0] + r * 0.22, c[1] + r * 0.05, c[2] + r * 1.6)], r=r * 0.1, m=stem, parent=root)

    one((0, 0, 0), size)
    if pile:
        one((size * 1.25, -size * 0.5, 0), size * 0.7)
        one((-size * 0.9, -size * 0.95, 0), size * 0.55)
    return root


def hay_bale(seed=97, stack=1):
    """Square golden straw bale with two twine straps; stack=3 builds a little pyramid."""
    rng = random.Random(seed)
    root = kit.empty("hay_bale")
    straw = mat("bale", "#F2C230", rough=0.85, edge=0.55, var=0.12)
    twine = mat("bale_twine", "#B5722A", rough=0.7, edge=0.4)
    tip = mat("bale_tip", "#FFE27A", rough=0.8, edge=0.3)

    def one(c, yaw=0.0):
        w, d, h = 0.62, 0.4, 0.36
        b = kit.box((w, d, h), straw, loc=(c[0], c[1], c[2] + h / 2), rot=(0, 0, yaw), bevel=0.06, parent=root)
        for sx in (-0.17, 0.17):
            kit.box((0.035, d + 0.02, h + 0.02), twine,
                    loc=(c[0] + math.cos(yaw) * sx, c[1] + math.sin(yaw) * sx, c[2] + h / 2), rot=(0, 0, yaw),
                    bevel=0.01, parent=root)
        for k in range(14):
            x = rng.uniform(-w / 2, w / 2) * 0.9
            y = rng.uniform(-d / 2, d / 2) * 0.9
            px = c[0] + math.cos(yaw) * x - math.sin(yaw) * y
            py = c[1] + math.sin(yaw) * x + math.cos(yaw) * y
            kit.curve_tube([(px, py, c[2] + h - 0.01), (px + rng.uniform(-0.05, 0.05), py + rng.uniform(-0.05, 0.05),
                            c[2] + h + rng.uniform(0.03, 0.07))], r=0.008, m=tip, parent=root)
        return b

    if stack >= 3:
        one((-0.33, 0, 0), 0.05)
        one((0.33, 0.02, 0), -0.06)
        one((0, 0.0, 0.36), 0.12)
    else:
        one((0, 0, 0), 0.0)
    return root


def _wood(name, color):
    return mat(name, color, rough=0.8, spec=0.15, edge=0.5, var=0.07)


def scarecrow():
    root = kit.empty("scarecrow")
    w = _wood("sc_wood", "#9C6539")
    kit.cyl(0.035, 1.25, w, loc=(0, 0, 0), parent=root, verts=12)
    kit.box((0.9, 0.06, 0.06), w, loc=(0, 0, 0.82), bevel=0.02, parent=root)
    shirt = mat("sc_shirt", "#D9483A", rough=0.8, edge=0.5, var=0.06)
    kit.box((0.42, 0.2, 0.46), shirt, loc=(0, 0, 0.68), bevel=0.08, parent=root)
    for sx in (-1, 1):
        kit.box((0.26, 0.15, 0.15), shirt, loc=(sx * 0.3, 0, 0.82), bevel=0.05, parent=root)
        for k in range(5):
            kit.curve_tube([(sx * 0.44, 0, 0.82), (sx * (0.52 + 0.01 * k), (k - 2) * 0.03, 0.78 - 0.02 * k)], r=0.012,
                           m=mat("sc_straw", "#F2C230", rough=0.9, edge=0.4), parent=root)
    kit.box((0.36, 0.17, 0.1), mat("sc_patch", "#3E7FC4", rough=0.8, edge=0.4), loc=(0, 0, 0.47), bevel=0.03, parent=root)
    sack = mat("sc_sack", "#E9CF9A", rough=0.9, edge=0.5, var=0.05)
    kit.sphere(0.19, sack, loc=(0, 0, 1.08), scale=(1, 0.95, 1.05), parent=root)
    hat = mat("sc_hat", "#7A4A24", rough=0.85, edge=0.5)
    kit.cyl(0.3, 0.035, hat, loc=(0, 0, 1.2), parent=root)
    kit.cyl(0.17, 0.2, hat, loc=(0, 0, 1.22), r2=0.11, parent=root)
    eye = mat("sc_eye", "#3A2A1A", rough=0.4)
    d = kit.TO_CAM.normalized()
    side = Vector((-d.y, d.x, 0)).normalized()
    for sx in (-1, 1):
        kit.sphere(0.028, eye, loc=Vector((0, 0, 1.1)) + d * 0.18 + side * sx * 0.07, seg=10, parent=root)
    kit.sphere(0.035, mat("sc_nose", "#F28A1E", rough=0.5), loc=Vector((0, 0, 1.05)) + d * 0.2, seg=10, parent=root)
    return root


def bench():
    root = kit.empty("bench")
    w = _wood("bench_wood", "#C98A52")
    leg = _wood("bench_leg", "#7A4A24")
    for k in range(3):
        kit.box((0.86, 0.1, 0.035), w, loc=(0, -0.11 + k * 0.11, 0.26), bevel=0.012, parent=root)
    for k in range(2):
        kit.box((0.86, 0.035, 0.1), w, loc=(0, 0.17, 0.4 + k * 0.13), bevel=0.012, parent=root)
    for sx in (-0.36, 0.36):
        kit.box((0.05, 0.3, 0.25), leg, loc=(sx, 0, 0.125), bevel=0.015, parent=root)
        kit.box((0.05, 0.05, 0.36), leg, loc=(sx, 0.17, 0.4), bevel=0.015, parent=root)
    return root


def lantern():
    root = kit.empty("lantern")
    iron = mat("lamp_iron", "#3E4A52", rough=0.5, spec=0.4, edge=0.5, metal=0.4)
    kit.cyl(0.09, 0.06, iron, loc=(0, 0, 0), parent=root)
    kit.cyl(0.03, 0.95, iron, loc=(0, 0, 0.05), parent=root, verts=12)
    kit.box((0.2, 0.2, 0.04), iron, loc=(0, 0, 1.0), bevel=0.01, parent=root)
    kit.box((0.15, 0.15, 0.2), mat("lamp_glass", "#FFE27A", rough=0.3, emit=1.6, edge=0.2), loc=(0, 0, 1.12),
            bevel=0.02, parent=root)
    kit.cyl(0.16, 0.12, iron, loc=(0, 0, 1.22), r2=0.03, parent=root, verts=4, rot=(0, 0, math.radians(45)))
    return root


def picket(axis="x"):
    root = kit.empty("picket", rot=(0, 0, 0 if axis == "x" else math.radians(90)))
    w = mat("picket", "#FAF6EC", rough=0.6, spec=0.2, edge=0.5, edge_color="#B9B4A6")
    for z in (0.14, 0.3):
        kit.box((1.0, 0.03, 0.05), w, loc=(0, 0.02, z), bevel=0.01, parent=root)
    for k in range(6):
        x = -0.42 + k * 0.168
        kit.box((0.085, 0.03, 0.4), w, loc=(x, 0, 0.2), bevel=0.012, parent=root)
        kit.cyl(0.06, 0.07, w, loc=(x, 0, 0.4), r2=0.005, verts=4, rot=(0, 0, math.radians(45)), parent=root,
                scale=(1, 0.36, 1))
    return root


def hedge(seed=71):
    rng = random.Random(seed)
    root = kit.empty("hedge")
    fm = foliage_mat("hedge_leaf", "#7CC43A", "#2C7A2C")
    for x in (-0.3, 0.0, 0.3):
        for y in (-0.12, 0.12):
            leaf_clump((x, y, 0.2), 0.24, fm, rng, parent=root, squash=1.0, bumps=0.16)
            leaf_clump((x + 0.05, y, 0.42), 0.2, fm, rng, parent=root, squash=0.9, bumps=0.16)
    return root


def signpost():
    root = kit.empty("signpost")
    w = _wood("sign_wood", "#9C6539")
    pl = _wood("sign_plank", "#E2B87A")
    kit.cyl(0.04, 0.95, w, loc=(0, 0, 0), parent=root, verts=12)
    for z, r, dx in ((0.78, 0.12, 0.12), (0.58, -0.1, -0.1)):
        kit.box((0.5, 0.04, 0.15), pl, loc=(dx, -0.045, z), rot=(0, r, 0), bevel=0.015, parent=root)
    return root


def milk_cans():
    root = kit.empty("milk_cans")
    steel = mat("can_steel", "#C9D2DA", rough=0.3, spec=0.6, edge=0.5, metal=0.6)
    for x, y, sc in ((-0.14, 0.0, 1.0), (0.16, -0.08, 0.85)):
        kit.cyl(0.13 * sc, 0.3 * sc, steel, loc=(x, y, 0), parent=root)
        kit.cyl(0.13 * sc, 0.1 * sc, steel, loc=(x, y, 0.3 * sc), r2=0.075 * sc, parent=root)
        kit.cyl(0.075 * sc, 0.08 * sc, steel, loc=(x, y, 0.4 * sc), parent=root)
        kit.cyl(0.095 * sc, 0.03 * sc, steel, loc=(x, y, 0.48 * sc), parent=root)
    return root


def leaf_pile(seed=72):
    rng = random.Random(seed)
    root = kit.empty("leaf_pile")
    cols = ["#F28A1E", "#E0453A", "#FFC84A", "#C8641E"]
    ms = [mat(f"pile_{c}", c, rough=0.7, edge=0.45, var=0.08) for c in cols]
    for k in range(70):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, 0.36) ** 0.8
        z = max(0.02, 0.24 * (1 - (r / 0.36) ** 1.5)) + rng.uniform(-0.02, 0.03)
        kit.sphere(0.07, ms[k % 4], loc=(math.cos(a) * r, math.sin(a) * r, z), scale=(1.3, 0.8, 0.22),
                   rot=(rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(0, 3)), seg=8, parent=root)
    return root


def dead_tree(seed=73):
    rng = random.Random(seed)
    root = kit.empty("dead_tree")
    bark = mat("dead_bark", "#7B6A5C", rough=0.9, edge=0.55, var=0.08)
    kit.cyl(0.13, 0.75, bark, loc=(0, 0, 0), r2=0.08, parent=root, verts=14)
    for k in range(6):
        a = k / 6 * 2 * math.pi + rng.uniform(-0.3, 0.3)
        l = rng.uniform(0.35, 0.6)
        z0 = rng.uniform(0.45, 0.75)
        mid = (math.cos(a) * l * 0.55, math.sin(a) * l * 0.55, z0 + l * 0.5)
        tip = (math.cos(a + 0.3) * l, math.sin(a + 0.3) * l, z0 + l * 1.05)
        kit.curve_tube([(0, 0, z0), mid, tip], r=0.035, m=bark, parent=root)
        kit.curve_tube([mid, (mid[0] + math.cos(a - 0.9) * 0.2, mid[1] + math.sin(a - 0.9) * 0.2, mid[2] + 0.22)],
                       r=0.018, m=bark, parent=root)
    return root


def stepping_stones(seed=74):
    rng = random.Random(seed)
    root = kit.empty("stepping_stones")
    st = mat("step_stone", "#C9C2B4", rough=0.85, edge=0.5, var=0.1)
    for x, y, r in ((-0.22, 0.12, 0.2), (0.2, 0.18, 0.17), (0.05, -0.2, 0.21), (-0.3, -0.22, 0.12), (0.34, -0.12, 0.13)):
        kit.sphere(r, st, loc=(x, y, 0.012), scale=(1.0, rng.uniform(0.75, 0.95), 0.16), rot=(0, 0, rng.uniform(0, 3)),
                   seg=16, parent=root)
    return root


def log_pile():
    root = kit.empty("log_pile")
    bark = mat("log_bark", "#8A5A34", rough=0.9, edge=0.5, var=0.08)
    cut = mat("log_cut", "#F0D29A", rough=0.8, edge=0.3)
    for x, z in ((-0.2, 0.1), (0.0, 0.1), (0.2, 0.1), (-0.1, 0.27), (0.1, 0.27), (0.0, 0.44)):
        kit.cyl(0.1, 0.6, bark, loc=(x, -0.3, z), rot=(math.radians(-90), 0, 0), parent=root, verts=14)
        kit.cyl(0.085, 0.612, cut, loc=(x, -0.306, z), rot=(math.radians(-90), 0, 0), parent=root, verts=14, bevel=0.0)
    return root


def mine():
    """Mine entrance: mossy rock mound with a timber portal, dark tunnel, rails and an ore cart."""
    rng = random.Random(81)
    d = Vector((kit.TO_CAM.x, kit.TO_CAM.y, 0)).normalized()
    ang = math.atan2(d.y, d.x) + math.radians(38)
    root = kit.empty("mine", rot=(0, 0, ang + math.pi / 2))
    stone = mat("mine_rock", "#B9A98C", rough=0.85, spec=0.1, edge=0.6, var=0.07)
    stone2 = mat("mine_rock2", "#D6C7A6", rough=0.85, spec=0.1, edge=0.55, var=0.06)
    for i, (x, y, r, h) in enumerate(((0, 0.25, 0.95, 1.05), (-0.6, 0.3, 0.62, 0.7), (0.62, 0.38, 0.66, 0.8), (0.1, 0.8, 0.7, 0.8),
                                      (-0.25, 0.55, 0.5, 1.2), (0.4, 0.1, 0.4, 0.95))):
        # low-subdivision rocks keep hard, chiselled facets
        o = kit.ico(r, stone2 if i % 2 else stone, loc=(x, y, h * 0.42), scale=(1.0, 0.9, h / r * 0.95), sub=1,
                    parent=root)
        o.rotation_euler = (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), rng.uniform(0, 3))
    grass = mat("mine_grass", "#6FAE38", rough=0.8, spec=0.05, edge=0.35, var=0.12)
    grass2 = mat("mine_grass2", "#8CC44A", rough=0.8, spec=0.05, edge=0.3, var=0.1)
    # mossy grass cap: many small overlapping lumps instead of flat discs
    for k in range(34):
        a = rng.uniform(0, 6.28)
        rr = rng.uniform(0, 0.62) ** 0.7 * 0.62
        x, y = math.cos(a) * rr * 1.1, 0.42 + math.sin(a) * rr * 0.75
        z = 1.06 - rr * 0.55 + rng.uniform(-0.03, 0.03)
        kit.sphere(rng.uniform(0.13, 0.2), grass2 if k % 3 == 0 else grass, loc=(x, y, z), scale=(1, 1, 0.6), seg=10,
                   parent=root)
    for k in range(16):
        a = rng.uniform(0, 6.28)
        rr = rng.uniform(0.05, 0.5)
        kit.cyl(0.013, 0.17, grass2, loc=(math.cos(a) * rr, 0.42 + math.sin(a) * rr * 0.7, 1.08 - rr * 0.45), r2=0.002,
                rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0), verts=5, bevel=0.0, parent=root)
    w = _wood("mine_wood", "#8A5A34")
    dark = mat("mine_dark", "#1E1410", rough=1.0, spec=0.0, edge=0.0)
    kit.box((0.62, 0.5, 0.74), dark, loc=(0, -0.42, 0.37), bevel=0.02, parent=root)
    for sx in (-0.36, 0.36):
        kit.box((0.12, 0.14, 0.86), w, loc=(sx, -0.7, 0.43), bevel=0.03, parent=root)
    kit.box((0.98, 0.16, 0.14), w, loc=(0, -0.7, 0.9), bevel=0.03, parent=root)
    kit.box((0.5, 0.05, 0.2), _wood("mine_sign", "#E2B87A"), loc=(0, -0.79, 0.9), bevel=0.02, parent=root)
    iron = mat("mine_rail", "#6A737A", rough=0.4, spec=0.5, edge=0.5, metal=0.5)
    for sx in (-0.16, 0.16):
        kit.box((0.035, 0.9, 0.035), iron, loc=(sx, -1.0, 0.03), bevel=0.01, parent=root)
    for k in range(5):
        kit.box((0.5, 0.07, 0.03), w, loc=(0, -0.62 - k * 0.19, 0.012), bevel=0.01, parent=root)
    cart = mat("mine_cart", "#5E6A72", rough=0.5, spec=0.4, edge=0.5, metal=0.3)
    kit.box((0.42, 0.34, 0.22), cart, loc=(0, -1.15, 0.2), bevel=0.04, parent=root)
    gold = mat("mine_gold", "#FFD23F", rough=0.3, spec=0.7, edge=0.4, metal=0.6)
    for k in range(7):
        kit.ico(0.07, gold, loc=(rng.uniform(-0.13, 0.13), -1.15 + rng.uniform(-0.1, 0.1), 0.33 + rng.uniform(0, 0.05)),
                sub=1, parent=root)
    for sx in (-0.2, 0.2):
        for sy in (-1.27, -1.03):
            kit.cyl(0.06, 0.03, iron, loc=(sx, sy, 0.06), rot=(0, math.radians(90), 0), parent=root, verts=12)
    return root


def nature_frames():
    return {
        "mine": mine,
        "scarecrow": scarecrow, "bench": bench, "lantern": lantern,
        "picket_x": lambda: picket("x"), "picket_y": lambda: picket("y"),
        "hedge": hedge, "signpost": signpost, "milk_cans": milk_cans, "leaf_pile": leaf_pile,
        "dead_tree": dead_tree, "stepping_stones": stepping_stones, "log_pile": log_pile,
        "grass_tuft": lambda: grass_tuft(95),
        "grass_tuft_b": lambda: grass_tuft(98, n=64, height=0.46),
        "pumpkin": lambda: pumpkin(96),
        "pumpkin_pile": lambda: pumpkin(99, pile=True),
        "hay_bale": lambda: hay_bale(97),
        "hay_bale_stack": lambda: hay_bale(100, stack=3),
        "tree_oak": lambda: oak(seed=11),
        "tree_oak_b": lambda: oak(seed=12, height=1.9, width=1.1),
        "tree_autumn": lambda: oak(seed=13, colors=LEAF_AUTUMN),
        "tree_apple": lambda: oak(seed=14, height=1.45, width=0.85, apples=True),
        "tree_pine": lambda: pine(seed=21),
        "tree_pine_b": lambda: pine(seed=22, height=2.8),
        "bush": lambda: bush(seed=31),
        "bush_berry": lambda: bush(seed=32, berries=True),
        "rock": lambda: rock(seed=41),
        "rock_small": lambda: rock(seed=42, size=0.32),
        "flowers_lavender": lambda: flowers("lavender", seed=51),
        "flowers_sun": lambda: flowers("sun", seed=52, count=20),
        "flowers_rose": lambda: flowers("rose", seed=53, count=20),
        "flowers_white": lambda: flowers("white", seed=54, count=22),
        "fern_big": lambda: fern(91, 1.4, 11),
        "cycad": lambda: cycad(92),
        "cycad_b": lambda: cycad(93, 1.25),
    }
