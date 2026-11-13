"""Fields, crops, fences and small farm props."""
from __future__ import annotations

import math
import random

from mathutils import Vector

from .. import kit
from ..kit import mat
from .nature import foliage_mat, leaf_clump, moss_tufts  # noqa: F401

FIELD_TOP = 0.1


def wood(name="wood", color="#B87C4B"):
    return mat(name, color, rough=0.75, spec=0.15, edge=0.5, var=0.09)


def field():
    root = kit.empty("field")
    soil = mat("soil", "#7E4E2E", rough=0.95, spec=0.05, edge=0.45)
    ridge = mat("soil_ridge", "#9A6238", rough=0.95, spec=0.05, edge=0.45, var=0.05)
    kit.box((0.92, 0.92, FIELD_TOP), soil, loc=(0, 0, FIELD_TOP / 2), bevel=0.045, parent=root)
    for i in range(4):
        y = -0.33 + i * 0.22
        o = kit.cyl(0.055, 0.84, ridge, loc=(-0.42, y, FIELD_TOP - 0.02), rot=(0, math.radians(90), 0),
                    bevel=0.0, verts=16, parent=root, scale=(0.7, 1.0, 1.0))
        kit.displace(o, strength=0.015, scale=0.05, seed=i + 1)
    return root


def _blade(m, base, height, lean_dir, lean, width=0.014, parent=None):
    rot = (lean_dir.y * -lean, lean_dir.x * lean, math.atan2(lean_dir.y, lean_dir.x))
    return kit.cyl(width, height, m, r2=0.002, loc=base, rot=rot, bevel=0.0, verts=6,
                   parent=parent, scale=(1.0, 0.45, 1.0))


def wheat(stage: int, seed=7):
    """stage 0 sprout, 1 young, 2 green, 3 ripe golden."""
    rng = random.Random(seed + stage)
    root = kit.empty("wheat")
    green = mat("wheat_green", "#7CC44A", rough=0.6, spec=0.2, edge=0.45, var=0.08, sss=0.1)
    gold = mat("wheat_gold", "#F2C443", rough=0.55, spec=0.25, edge=0.5, var=0.07, edge_color="#B57A1E")
    stalk_gold = mat("wheat_stalk", "#E3B23C", rough=0.6, spec=0.2, edge=0.45, var=0.06)
    grid = 3 if stage < 3 else 4
    step = 0.78 / grid
    for gx in range(grid):
        for gy in range(grid):
            cx = -0.39 + step * (gx + 0.5) + rng.uniform(-0.03, 0.03)
            cy = -0.39 + step * (gy + 0.5) + rng.uniform(-0.03, 0.03)
            base = Vector((cx, cy, FIELD_TOP - 0.01))
            if stage == 0:
                for k in range(3):
                    a = k / 3 * 2 * math.pi + rng.random()
                    _blade(green, base, 0.07, Vector((math.cos(a), math.sin(a), 0)), 0.5, 0.012, root)
            elif stage == 1:
                for k in range(5):
                    a = k / 5 * 2 * math.pi + rng.random()
                    _blade(green, base, rng.uniform(0.13, 0.18), Vector((math.cos(a), math.sin(a), 0)),
                           0.35, 0.016, root)
            else:
                n = 6 if stage == 2 else 7
                h0 = 0.3 if stage == 2 else 0.36
                for k in range(n):
                    a = rng.uniform(0, 2 * math.pi)
                    r = rng.uniform(0.0, 0.05)
                    p = base + Vector((math.cos(a) * r, math.sin(a) * r, 0))
                    h = h0 * rng.uniform(0.85, 1.1)
                    lean = rng.uniform(0.05, 0.22)
                    d = Vector((math.cos(a), math.sin(a), 0))
                    m_stalk = green if stage == 2 else stalk_gold
                    kit.cyl(0.008, h, m_stalk, loc=p, rot=(d.y * -lean, d.x * lean, 0), bevel=0.0, verts=6,
                            parent=root)
                    tip = p + Vector((d.x * math.sin(lean), d.y * math.sin(lean), math.cos(lean))) * h
                    ear_m = green if stage == 2 else gold
                    kit.sphere(0.028 if stage == 3 else 0.022, ear_m, loc=tip, scale=(1.0, 1.0, 2.6),
                               rot=(d.y * -lean, d.x * lean, 0), seg=12, parent=root)
                # a few leaves at the base
                for k in range(3):
                    a = rng.uniform(0, 2 * math.pi)
                    _blade(green if stage == 2 else stalk_gold, base, 0.14, Vector((math.cos(a), math.sin(a), 0)),
                           0.6, 0.016, root)
    return root


def _grid(n, jitter, rng):
    step = 0.78 / n
    for gx in range(n):
        for gy in range(n):
            yield Vector((-0.39 + step * (gx + 0.5) + rng.uniform(-jitter, jitter),
                          -0.39 + step * (gy + 0.5) + rng.uniform(-jitter, jitter), FIELD_TOP - 0.01))


def _sprouts(root, rng, n, green):
    for base in _grid(n, 0.03, rng):
        for k in range(3):
            a = k / 3 * 2 * math.pi + rng.random()
            _blade(green, base, 0.07, Vector((math.cos(a), math.sin(a), 0)), 0.5, 0.012, root)


def corn(stage: int, seed=21):
    rng = random.Random(seed + stage)
    root = kit.empty("corn")
    green = mat("corn_green", "#6DBB45", rough=0.6, spec=0.2, edge=0.45, var=0.08, sss=0.1)
    if stage == 0:
        _sprouts(root, rng, 2, green)
        return root
    husk = mat("corn_husk", "#9BD66A", rough=0.6, edge=0.45, var=0.06)
    kern = mat("corn_kernel", "#FFD23F", rough=0.45, spec=0.35, edge=0.5, edge_color="#C98A10")
    tassel = mat("corn_tassel", "#E6C46A", rough=0.7, edge=0.4)
    h = {1: 0.2, 2: 0.48, 3: 0.56}[stage]
    for base in _grid(2, 0.04, rng):
        kit.cyl(0.022, h, green, loc=base, bevel=0.0, verts=8, parent=root)
        for k in range(5 if stage > 1 else 3):
            a = k * 2.4 + rng.random()
            z = base.z + h * (0.15 + 0.17 * k)
            d = Vector((math.cos(a), math.sin(a), 0))
            _blade(green, base + Vector((0, 0, z - base.z)), h * 0.55, d, 0.9, 0.03, root)
        if stage == 3:
            a = rng.uniform(0, 6.28)
            d = Vector((math.cos(a), math.sin(a), 0))
            p = base + Vector((d.x * 0.05, d.y * 0.05, h * 0.55))
            kit.sphere(0.045, kern, loc=p, scale=(1.0, 1.0, 2.3), rot=(d.y * -0.35, d.x * 0.35, 0), seg=14, parent=root)
            for side in (-1, 1):
                kit.sphere(0.04, husk, loc=p + Vector((d.y * side * 0.025, -d.x * side * 0.025, -0.04)),
                           scale=(0.6, 0.6, 2.4), rot=(d.y * -0.35, d.x * 0.35, 0), seg=12, parent=root)
            for k in range(4):
                a2 = k * 1.57 + rng.random()
                _blade(tassel, base + Vector((0, 0, h)), 0.09, Vector((math.cos(a2), math.sin(a2), 0)), 0.7, 0.01, root)
    return root


def carrot(stage: int, seed=31):
    rng = random.Random(seed + stage)
    root = kit.empty("carrot")
    green = mat("carrot_green", "#5FB43C", rough=0.6, spec=0.2, edge=0.45, var=0.1, sss=0.1)
    if stage == 0:
        _sprouts(root, rng, 3, green)
        return root
    orange = mat("carrot", "#FF8A2B", rough=0.45, spec=0.35, edge=0.5, edge_color="#B4501A")
    fm = foliage_mat("carrot_top", "#8FD455", "#2F8A2C",
                                                                          noise_scale=26.0, z0=0.1, z1=0.4)
    for base in _grid(3, 0.03, rng):
        n = {1: 5, 2: 9, 3: 10}[stage]
        h = {1: 0.11, 2: 0.17, 3: 0.19}[stage]
        for k in range(n):
            a = k / n * 2 * math.pi + rng.random() * 0.5
            d = Vector((math.cos(a), math.sin(a), 0))
            lean = rng.uniform(0.25, 0.6)
            _blade(green, base, h * rng.uniform(0.85, 1.1), d, lean, 0.011, root)
            if stage >= 2:
                # feathery leaflets along the upper half of each stem
                for j in range(3):
                    t = 0.55 + j * 0.17
                    p = base + Vector((d.x * math.sin(lean), d.y * math.sin(lean), math.cos(lean))) * h * t
                    kit.sphere(0.016, fm, loc=p, scale=(1.4, 0.7, 0.45), rot=(0, 0, a + (j % 2) * 0.8), seg=8,
                               parent=root)
        if stage == 3:
            kit.cyl(0.04, 0.05, orange, loc=base + Vector((0, 0, -0.02)), r2=0.03, bevel=0.0, verts=14, parent=root)
    return root


def tomato(stage: int, seed=41):
    rng = random.Random(seed + stage)
    root = kit.empty("tomato")
    green = mat("tomato_green", "#5DAE3C", rough=0.6, spec=0.2, edge=0.45, var=0.08)
    if stage == 0:
        _sprouts(root, rng, 2, green)
        return root
    fm = foliage_mat("tomato_leaf", "#7FC948", "#2D7A2C",
                                                                          noise_scale=16.0, z0=0.1, z1=0.6)
    stake = wood("stake", "#B98654")
    red = mat("tomato", "#F0402F", rough=0.25, spec=0.6, edge=0.45, coat=0.4, edge_color="#8A1A10")
    flower = mat("tomato_flower", "#FFE04A", rough=0.5, edge=0.3)
    for base in _grid(2, 0.03, rng):
        h = {1: 0.16, 2: 0.36, 3: 0.4}[stage]
        if stage >= 2:
            kit.box((0.025, 0.025, h + 0.08), stake, loc=base + Vector((0.07, -0.07, (h + 0.08) / 2)), bevel=0.008,
                    parent=root)
        spots = [(0, 0, h * 0.45, 0.09), (0.04, 0.03, h * 0.75, 0.08), (-0.04, -0.02, h * 0.85, 0.07)]
        if stage == 1:
            spots = [(0, 0, h * 0.6, 0.075)]
        for x, y, z, r in spots:
            leaf_clump(base + Vector((x, y, z)), r * (1.0 if stage > 1 else 0.9), fm, rng, parent=root, squash=0.9)
        if stage == 2:
            for k in range(4):
                a = rng.uniform(0, 6.28)
                kit.sphere(0.018, flower, loc=base + Vector((math.cos(a) * 0.08, math.sin(a) * 0.08,
                           h * rng.uniform(0.5, 0.95))), seg=8, parent=root)
        if stage == 3:
            for k in range(6):
                a = rng.uniform(-1.6, 1.6) + math.atan2(kit.TO_CAM.y, kit.TO_CAM.x)
                p = base + Vector((math.cos(a) * 0.085, math.sin(a) * 0.085, h * rng.uniform(0.3, 0.9)))
                kit.sphere(0.04, red, loc=p, scale=(1.0, 1.0, 0.88), seg=16, parent=root)
    return root


def strawberry(stage: int, seed=51):
    rng = random.Random(seed + stage)
    root = kit.empty("strawberry")
    green = mat("straw_green", "#5DAE3C", rough=0.6, spec=0.2, edge=0.45, var=0.08)
    if stage == 0:
        _sprouts(root, rng, 3, green)
        return root
    fm = foliage_mat("strawberry_leaf", "#86CC4A", "#2D7A2C",
                                                                          noise_scale=18.0, z0=0.1, z1=0.3)
    red = mat("strawberry", "#F2384A", rough=0.3, spec=0.5, edge=0.45, coat=0.3, edge_color="#8A1222")
    seedm = mat("straw_seed", "#FFE38A", rough=0.5, edge=0.0)
    white = mat("straw_flower", "#FFFFFF", rough=0.5, edge=0.3)
    for base in _grid(3, 0.02, rng):
        r = {1: 0.055, 2: 0.075, 3: 0.08}[stage]
        leaf_clump(base + Vector((0, 0, r * 0.6)), r, fm, rng, parent=root, squash=0.7)
        if stage == 2 and rng.random() < 0.7:
            a = rng.uniform(0, 6.28)
            c = base + Vector((math.cos(a) * r * 0.8, math.sin(a) * r * 0.8, r * 1.0))
            for j in range(5):
                b = j / 5 * 6.28
                kit.sphere(0.012, white, loc=c + Vector((math.cos(b) * 0.014, math.sin(b) * 0.014, 0)),
                           scale=(1, 1, 0.5), seg=8, parent=root)
            kit.sphere(0.008, mat("flower_center", "#FFB830", rough=0.6, edge=0.3), loc=c + Vector((0, 0, 0.004)),
                       seg=8, parent=root)
        if stage == 3:
            a = rng.uniform(-1.4, 1.4) + math.atan2(kit.TO_CAM.y, kit.TO_CAM.x)
            p = base + Vector((math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, 0.03))
            kit.cyl(0.026, 0.05, red, loc=p + Vector((0, 0, -0.04)), r2=0.006, rot=(math.pi, 0, 0), bevel=0.0,
                    verts=14, parent=root)
            kit.sphere(0.027, red, loc=p + Vector((0, 0, -0.012)), scale=(1, 1, 0.7), seg=14, parent=root)
            for j in range(3):
                b = j * 2.1 + a
                kit.sphere(0.004, seedm, loc=p + Vector((math.cos(b) * 0.024, math.sin(b) * 0.024, -0.02)),
                           seg=6, parent=root)
    return root


def fence(axis="x", moss=True, seed=3):
    """One fence segment, one tile long, centred on the origin."""
    rng = random.Random(seed)
    root = kit.empty("fence", rot=(0, 0, 0 if axis == "x" else math.radians(90)))
    w = wood("fence_wood", "#B07547")
    post = wood("fence_post", "#9C6539")
    for x in (-0.5, 0.5):
        kit.box((0.09, 0.09, 0.42), post, loc=(x, 0, 0.21), bevel=0.025, parent=root)
        kit.sphere(0.052, post, loc=(x, 0, 0.42), scale=(1.0, 1.0, 0.6), seg=14, parent=root)
    for z in (0.17, 0.32):
        o = kit.box((1.0, 0.045, 0.075), w, loc=(0, 0, z), bevel=0.018, parent=root)
        o.rotation_euler = (0, rng.uniform(-0.02, 0.02), 0)
    if moss:
        moss_tufts([(-0.5, 0, 0.46), (-0.47, 0.03, 0.44)], rng, parent=root, size=0.05)
    return root


def straw_mat():
    """Straw: base material plus fine stretched noise bump (pressed stalks)."""
    m = mat("straw", "#EDC65A", rough=0.9, spec=0.1, edge=0.55, edge_color="#B98A2C", var=0.05)
    nt = m.node_tree
    if any(n.type == "BUMP" for n in nt.nodes):
        return m
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (6.0, 6.0, 60.0)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 4.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.55
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def hay_bale(seed=1):
    root = kit.empty("hay")
    straw = straw_mat()
    o = kit.box((0.52, 0.36, 0.3), straw, loc=(0, 0, 0.15), bevel=0.06, parent=root)
    kit.displace(o, strength=0.01, scale=0.02, seed=seed)
    twine = mat("twine", "#9A6B3A", rough=0.8, edge=0.3)
    for x in (-0.13, 0.13):
        kit.box((0.035, 0.375, 0.315), twine, loc=(x, 0, 0.15), bevel=0.015, parent=root)
    return root


def barrel():
    root = kit.empty("barrel")
    staves = wood("barrel_wood", "#A8683C")
    o = kit.cyl(0.2, 0.46, staves, loc=(0, 0, 0), bevel=0.02, verts=16, parent=root)
    kit.subsurf(o, 1)
    o.scale = (1.0, 1.0, 1.0)
    metal = mat("iron", "#7C7F86", rough=0.35, spec=0.6, metal=0.6, edge=0.4)
    for z in (0.08, 0.38):
        kit.torus(0.205, 0.016, metal, loc=(0, 0, z), parent=root)
    kit.cyl(0.18, 0.02, mat("barrel_top", "#C08A55", rough=0.7, edge=0.3), loc=(0, 0, 0.445), bevel=0.0,
            parent=root)
    return root


def crate():
    root = kit.empty("crate")
    w = wood("crate_wood", "#C48D58")
    kit.box((0.42, 0.42, 0.34), w, loc=(0, 0, 0.17), bevel=0.02, parent=root)
    dark = wood("crate_band", "#8F5A33")
    for z in (0.05, 0.29):
        kit.box((0.44, 0.44, 0.05), dark, loc=(0, 0, z), bevel=0.012, parent=root)
    return root


def trough():
    root = kit.empty("trough")
    w = wood("trough_wood", "#A86E40")
    kit.box((0.7, 0.32, 0.18), w, loc=(0, 0, 0.13), bevel=0.03, parent=root)
    for x in (-0.3, 0.3):
        kit.box((0.06, 0.3, 0.06), w, loc=(x, 0, 0.03), bevel=0.015, parent=root)
    grain = mat("grain", "#F0CB62", rough=0.9, edge=0.3, var=0.1)
    rng = random.Random(4)
    for i in range(28):
        kit.sphere(0.022, grain, loc=(rng.uniform(-0.28, 0.28), rng.uniform(-0.1, 0.1), 0.22), seg=8,
                   parent=root)
    return root


def farm_frames():
    out = {
        "field": field,
        "fence_x": lambda: fence("x", seed=3),
        "fence_y": lambda: fence("y", seed=4),
        "hay": hay_bale,
        "barrel": barrel,
        "crate": crate,
        "trough": trough,
    }
    for s in range(4):
        out[f"wheat_{s}"] = (lambda s=s: wheat(s))
        out[f"corn_{s}"] = (lambda s=s: corn(s))
        out[f"carrot_{s}"] = (lambda s=s: carrot(s))
        out[f"tomato_{s}"] = (lambda s=s: tomato(s))
        out[f"strawberry_{s}"] = (lambda s=s: strawberry(s))
    return out
