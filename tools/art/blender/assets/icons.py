"""HUD icons and tiny effect sprites, rendered facing the camera."""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Vector

from .. import kit
from ..kit import mat


def _facing_root(name, tilt=0.18):
    """Empty whose local +Z points at the camera (slightly tilted up)."""
    d = (kit.TO_CAM + Vector((0, 0, tilt))).normalized()
    root = kit.empty(name)
    root.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return root


def coin():
    root = _facing_root("coin")
    gold = mat("gold", "#FFC93C", rough=0.25, spec=0.7, metal=0.85, edge=0.45, edge_color="#9A5A10")
    rim = mat("gold_rim", "#F2A92B", rough=0.25, spec=0.7, metal=0.85, edge=0.45, edge_color="#8A4A0C")
    kit.cyl(0.4, 0.1, rim, loc=(0, 0, -0.05), bevel=0.035, verts=48, parent=root)
    kit.cyl(0.32, 0.03, gold, loc=(0, 0, 0.04), bevel=0.012, verts=48, parent=root)
    # embossed leaf: the Mossglen mark
    leaf = kit.sphere(0.15, rim, loc=(0.0, 0.0, 0.075), scale=(0.62, 1.15, 0.22), rot=(0, 0, math.radians(-30)),
                      seg=24, parent=root)
    kit.box((0.025, 0.24, 0.03), gold, loc=(0.0, 0.0, 0.1), rot=(0, 0, math.radians(-30)), bevel=0.01, parent=root)
    return root


def emerald():
    root = _facing_root("emerald", tilt=0.0)
    gem = mat("emerald", "#2FD487", rough=0.08, spec=0.9, edge=0.4, edge_color="#0E6A44", coat=0.6)
    bm = bmesh.new()
    n = 8
    top = [bm.verts.new((math.cos(a) * 0.25, math.sin(a) * 0.25, 0.12)) for a in
           (i / n * 2 * math.pi + math.pi / 8 for i in range(n))]
    mid = [bm.verts.new((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.0)) for a in
           (i / n * 2 * math.pi + math.pi / 8 for i in range(n))]
    tip = bm.verts.new((0, 0, -0.4))
    bm.faces.new(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((mid[i], mid[j], top[j], top[i]))
        bm.faces.new((mid[j], mid[i], tip))
    me = bpy.data.meshes.new("gem")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("gem", me)
    kit.link(o)
    kit.set_mat(o, gem)
    o.parent = root
    # rotate so the table faces the viewer and the point goes down
    o.rotation_euler = (math.radians(-38), 0, 0)
    return root


def star():
    root = _facing_root("star", tilt=0.0)
    m = mat("star", "#FFD84A", rough=0.3, spec=0.6, metal=0.3, edge=0.45, edge_color="#B06A10")
    bm = bmesh.new()
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        r = 0.42 if i % 2 == 0 else 0.19
        pts.append((math.cos(a) * r, math.sin(a) * r))
    fz = [bm.verts.new((x, y, 0.07)) for x, y in pts]
    bz = [bm.verts.new((x, y, -0.07)) for x, y in pts]
    c1 = bm.verts.new((0, 0, 0.14))
    c2 = bm.verts.new((0, 0, -0.1))
    for i in range(10):
        j = (i + 1) % 10
        bm.faces.new((fz[i], fz[j], c1))
        bm.faces.new((bz[j], bz[i], c2))
        bm.faces.new((bz[i], bz[j], fz[j], fz[i]))
    me = bpy.data.meshes.new("star")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("star", me)
    kit.link(o)
    kit.set_mat(o, m)
    o.parent = root
    b = o.modifiers.new("bevel", "BEVEL")
    b.width = 0.03
    b.segments = 3
    return root


def wheat_icon():
    root = _facing_root("wheat_icon", tilt=0.0)
    gold = mat("wheat_gold", "#F2C443", rough=0.55, spec=0.25, edge=0.5, var=0.07, edge_color="#B57A1E")
    stalk = mat("wheat_stalk", "#E3B23C", rough=0.6, spec=0.2, edge=0.45, var=0.06)
    for k, ang in enumerate((-22, 0, 22)):
        a = math.radians(ang)
        stem = kit.empty("s", rot=(0, a, 0), parent=root)
        stem.rotation_euler = (0, 0, a)
        kit.cyl(0.018, 0.5, stalk, loc=(0, -0.3, 0), rot=(math.radians(-90), 0, 0), bevel=0.0, verts=8,
                parent=stem)
        for i in range(5):
            for side in (-1, 1):
                kit.sphere(0.05, gold, loc=(side * 0.04, 0.22 + i * 0.07, 0.01), scale=(0.7, 1.3, 0.7),
                           rot=(0, 0, side * 0.5), seg=12, parent=stem)
        kit.sphere(0.045, gold, loc=(0, 0.58, 0.01), scale=(0.7, 1.4, 0.7), seg=12, parent=stem)
    tie = mat("twine", "#9A6B3A", rough=0.8, edge=0.3)
    kit.torus(0.07, 0.022, tie, loc=(0, -0.05, 0), rot=(math.radians(90), 0, 0), parent=root)
    return root


def fx_leaf():
    root = _facing_root("fx_leaf", tilt=0.0)
    m = mat("fx_leaf", "#7CC44A", rough=0.5, edge=0.4)
    kit.sphere(0.1, m, scale=(0.55, 1.0, 0.18), rot=(0, 0, 0.5), seg=16, parent=root)
    return root


def fx_grain():
    root = _facing_root("fx_grain", tilt=0.0)
    m = mat("wheat_gold", "#F2C443", rough=0.55, spec=0.25, edge=0.5, var=0.07, edge_color="#B57A1E")
    kit.sphere(0.06, m, scale=(0.7, 1.2, 0.7), rot=(0, 0, 0.6), seg=14, parent=root)
    return root


def icon_frames():
    return {
        "icon_coin": coin,
        "icon_emerald": emerald,
        "icon_star": star,
        "icon_wheat": wheat_icon,
        "fx_leaf": fx_leaf,
        "fx_grain": fx_grain,
    }
