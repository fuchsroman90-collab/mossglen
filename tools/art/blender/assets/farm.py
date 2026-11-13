"""Fields, crops, fences and small farm props."""
from __future__ import annotations

import math
import random

from mathutils import Vector

from .. import kit
from ..kit import mat
from .nature import foliage_mat, leaf_clump, moss_tufts

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
    return out
