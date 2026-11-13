"""Blender toolkit for Mossglen sprites.

Everything here runs inside Blender's Python (`pip install bpy`).
One sprite frame = build objects -> fit camera -> render object pass
(+ optional shadow pass) -> PNGs that post.py turns into the final sprite.

Conventions
- 1 grid tile = 1 m x 1 m. Grid x -> world +X, grid y -> world -Y.
- Fixed dimetric 2:1 camera (30 deg elevation, 45 deg yaw), orthographic.
- 2x resolution: one tile diamond is 256 x 128 px.
- The sprite anchor is where the world origin (0, 0, 0) lands in the image.
- "Forward" of a model is local +X. yaw 0 faces screen down-right (SE),
  yaw 90 faces screen up-right (NE).
"""
from __future__ import annotations

import math
import random

import bpy
from mathutils import Euler, Matrix, Vector

PPM = 256.0 / math.sqrt(2.0)  # pixels per metre on screen (2x resolution)
CAM_ROT = Euler((math.radians(60.0), 0.0, math.radians(45.0)))
R = Vector((math.sqrt(0.5), math.sqrt(0.5), 0.0))           # screen right
U = Vector((-0.5 * math.sqrt(0.5), 0.5 * math.sqrt(0.5), math.sqrt(0.75)))  # screen up
F = U.cross(R)  # view direction, into the screen
TO_CAM = -F

# Light: from the upper left of the screen, slightly in front, fairly high.
LIGHT_DIR = (-0.7 * R + 0.45 * Vector((TO_CAM.x, TO_CAM.y, 0.0)).normalized()
             + Vector((0.0, 0.0, 1.9))).normalized()

STAGE = "stage"


# ---------------------------------------------------------------- colour

def lin(hex_color: str) -> tuple:
    """sRGB hex -> linear RGBA tuple."""
    h = hex_color.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


# ---------------------------------------------------------------- scene

def reset(samples: int = 48) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()  # factory reset deleted all materials
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 6
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 2
    cy.transparent_max_bounces = 4
    cy.filter_width = 1.1
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "8"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.threads_mode = "AUTO"

    stage = bpy.data.collections.new(STAGE)
    sc.collection.children.link(stage)

    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.clip_start = 0.1
    cam.clip_end = 400.0
    co = bpy.data.objects.new("cam", cam)
    co.rotation_euler = CAM_ROT
    sc.collection.objects.link(co)
    sc.camera = co

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.6
    sun.angle = math.radians(14.0)
    sun.color = (1.0, 0.95, 0.86)
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (-LIGHT_DIR).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(so)

    # Sky fill from above (cool), grass bounce from below (green).
    w = bpy.data.worlds.new("world")
    sc.world = w
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.30, 0.42, 0.12, 1.0)
    ramp.color_ramp.elements[1].position = 0.62
    ramp.color_ramp.elements[1].color = (0.66, 0.78, 0.95, 1.0)
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -1.0
    mr.inputs["From Max"].default_value = 1.0
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs[0])

    # Shadow catcher ground plane (only visible in the shadow pass).
    bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0, 0, 0))
    g = bpy.context.active_object
    g.name = "ground"
    g.is_shadow_catcher = True
    g.hide_render = True
    for c in g.users_collection:
        c.objects.unlink(g)
    sc.collection.objects.link(g)


def stage() -> bpy.types.Collection:
    return bpy.data.collections[STAGE]


def clear_stage() -> None:
    for o in list(stage().objects):
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.MetaBall):
                bpy.data.metaballs.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)


def link(o: bpy.types.Object) -> bpy.types.Object:
    for c in list(o.users_collection):
        c.objects.unlink(o)
    stage().objects.link(o)
    return o


# ---------------------------------------------------------------- materials

_mats: dict = {}


def mat(name: str, color: str, rough: float = 0.6, spec: float = 0.25, edge: float = 0.35,
        var: float = 0.0, coat: float = 0.0, metal: float = 0.0, emit: float = 0.0,
        edge_color: str | None = None, sss: float = 0.0) -> bpy.types.Material:
    """Stylised principled material.

    edge  - darkens the colour towards grazing angles (soft cartoon rim).
    var   - per-object random brightness/hue jitter (planks, bricks, leaves).
    """
    key = (name, color, rough, spec, edge, var, coat, metal, emit, edge_color, sss)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    base = lin(color)
    col_socket = None

    rgb = nt.nodes.new("ShaderNodeRGB")
    rgb.outputs[0].default_value = base
    col_socket = rgb.outputs[0]

    if var > 0.0:
        info = nt.nodes.new("ShaderNodeObjectInfo")
        hsv = nt.nodes.new("ShaderNodeHueSaturation")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["To Min"].default_value = 1.0 - var
        mr.inputs["To Max"].default_value = 1.0 + var
        nt.links.new(info.outputs["Random"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], hsv.inputs["Value"])
        mr2 = nt.nodes.new("ShaderNodeMapRange")
        mr2.inputs["To Min"].default_value = 0.5 - var * 0.06
        mr2.inputs["To Max"].default_value = 0.5 + var * 0.06
        nt.links.new(info.outputs["Random"], mr2.inputs["Value"])
        nt.links.new(mr2.outputs["Result"], hsv.inputs["Hue"])
        nt.links.new(col_socket, hsv.inputs["Color"])
        col_socket = hsv.outputs["Color"]

    if edge > 0.0:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.45
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.25
        ramp.color_ramp.elements[1].position = 0.95
        nt.links.new(lw.outputs["Facing"], ramp.inputs["Fac"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        dark = lin(edge_color) if edge_color else tuple(c * 0.42 for c in base[:3]) + (1.0,)
        if edge_color is None:
            mix.blend_type = "MIX"
        mix.inputs[7].default_value = dark
        fac = nt.nodes.new("ShaderNodeMath")
        fac.operation = "MULTIPLY"
        fac.inputs[1].default_value = edge
        nt.links.new(ramp.outputs["Color"], fac.inputs[0])
        nt.links.new(fac.outputs[0], mix.inputs[0])
        nt.links.new(col_socket, mix.inputs[6])
        col_socket = mix.outputs[2]

    nt.links.new(col_socket, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = spec
    bsdf.inputs["Metallic"].default_value = metal
    if coat > 0.0:
        bsdf.inputs["Coat Weight"].default_value = coat
        bsdf.inputs["Coat Roughness"].default_value = 0.15
    if emit > 0.0:
        nt.links.new(col_socket, bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emit
    if sss > 0.0:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = (0.4, 0.2, 0.1)
        bsdf.inputs["Subsurface Scale"].default_value = 0.05
    _mats[key] = m
    return m


def set_mat(o: bpy.types.Object, m: bpy.types.Material) -> bpy.types.Object:
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


# ---------------------------------------------------------------- shapes

def _finish(o, m=None, smooth=True, loc=None, rot=None, scale=None, parent=None):
    link(o)
    if loc is not None:
        o.location = loc
    if rot is not None:
        o.rotation_euler = rot
    if scale is not None:
        o.scale = scale
    if m is not None:
        set_mat(o, m)
    if smooth and o.type == "MESH":
        for p in o.data.polygons:
            p.use_smooth = True
    if parent is not None:
        o.parent = parent
    return o


def empty(name="root", loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    link(o)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    return o


def sphere(r=0.5, m=None, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), seg=32, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=max(8, seg // 2))
    return _finish(bpy.context.active_object, m, True, loc, rot, scale, parent)


def ico(r=0.5, m=None, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), sub=2, parent=None, smooth=True):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=sub)
    return _finish(bpy.context.active_object, m, smooth, loc, rot, scale, parent)


def box(size=(1, 1, 1), m=None, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.04, seg=3, parent=None):
    """Rounded box. size is full extent; loc is the centre."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = min(bevel, min(size) * 0.49)
        b.segments = seg
        b.limit_method = "NONE"
        b.harden_normals = True
    return _finish(o, m, bevel > 0, loc, rot, None, parent)


def cyl(r=0.5, h=1.0, m=None, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.02, verts=24, r2=None,
        parent=None, scale=(1, 1, 1)):
    """Cylinder (or cone when r2 is given) standing on loc (base at loc.z)."""
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, vertices=verts)
    o = bpy.context.active_object
    for v in o.data.vertices:
        v.co.z += h / 2.0
    if bevel > 0:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 3
        b.limit_method = "ANGLE"
        b.harden_normals = True
    _finish(o, m, True, loc, rot, scale, parent)
    if bevel <= 0:
        smooth_by_angle(o, 50)
    return o


def smooth_by_angle(o, deg=40):
    es = o.modifiers.new("split", "EDGE_SPLIT")
    es.split_angle = math.radians(deg)
    return o


def torus(R_=0.5, r=0.1, m=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R_, minor_radius=r, major_segments=40, minor_segments=14)
    return _finish(bpy.context.active_object, m, True, loc, rot, scale, parent)


def blob(elements, m, name="blob", res=0.012, threshold=0.6, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Metaball blob. elements: list of dicts {co, r, type, size, rot, neg, stiff}.

    Different blob() calls never merge (each gets a unique family name).
    """
    mb = bpy.data.metaballs.new(name)
    mb.resolution = res * 2
    mb.render_resolution = res
    mb.threshold = threshold
    for e in elements:
        el = mb.elements.new()
        el.type = e.get("type", "BALL")
        el.co = e["co"]
        el.radius = e["r"]
        el.stiffness = e.get("stiff", 2.0)
        if "size" in e:
            el.size_x, el.size_y, el.size_z = e["size"]
        if "rot" in e:
            el.rotation = Euler(e["rot"]).to_quaternion()
        el.use_negative = e.get("neg", False)
    mb.materials.append(m)
    fam = f"{name}{random.randrange(10**8)}"
    o = bpy.data.objects.new(fam, mb)
    link(o)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    return o


def to_mesh(o):
    """Convert a metaball/curve object to a real mesh (needed for modifiers)."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    n = bpy.data.objects.new(o.name + "_m", me)
    link(n)
    n.matrix_world = o.matrix_world.copy()
    for p in me.polygons:
        p.use_smooth = True
    data = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    if isinstance(data, bpy.types.MetaBall) and data.users == 0:
        bpy.data.metaballs.remove(data)
    return n


def displace(o, strength=0.05, scale=0.3, kind="CLOUDS", seed=0, mid=0.5):
    tex = bpy.data.textures.new(f"disp{seed}", kind)
    if kind == "CLOUDS":
        tex.noise_scale = scale
    elif kind == "VORONOI":
        tex.noise_scale = scale
    d = o.modifiers.new("disp", "DISPLACE")
    d.texture = tex
    d.strength = strength
    d.mid_level = mid
    d.texture_coords = "GLOBAL" if seed == 0 else "OBJECT"
    return o


def subsurf(o, levels=2):
    s = o.modifiers.new("sub", "SUBSURF")
    s.levels = levels
    s.render_levels = levels
    return o


def curve_tube(points, r=0.03, m=None, parent=None, res=6):
    cd = bpy.data.curves.new("tube", "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth = r
    cd.bevel_resolution = 3
    cd.resolution_u = res
    sp = cd.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new("tube", cd)
    link(o)
    if m is not None:
        cd.materials.append(m)
    if parent is not None:
        o.parent = parent
    return o


# ---------------------------------------------------------------- render

def _world_points():
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in stage().objects:
        if o.type not in {"MESH", "META", "CURVE"} or o.hide_render:
            continue
        ev = o.evaluated_get(dg)
        try:
            me = ev.to_mesh()
        except RuntimeError:
            continue
        if me is None:
            continue
        mw = ev.matrix_world
        step = max(1, len(me.vertices) // 4000)
        for v in me.vertices[::step]:
            pts.append(mw @ v.co)
        ev.to_mesh_clear()
    return pts


def fit_and_render(path_obj: str, path_shadow: str | None, pad: int = 6) -> dict:
    """Fit the ortho camera tightly around the stage, render, return anchor."""
    sc = bpy.context.scene
    pts = _world_points()
    if not pts:
        raise RuntimeError("empty stage")
    proj = []
    for p in pts:
        proj.append((p.dot(R), p.dot(U)))
        if path_shadow and p.z > 0.0:
            g = p - LIGHT_DIR * (p.z / LIGHT_DIR.z)
            proj.append((g.dot(R), g.dot(U)))
    proj.append((0.0, 0.0))
    xs = [a for a, _ in proj]
    ys = [b for _, b in proj]
    extra = 16 if path_shadow else 0
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    w = int(math.ceil((x1 - x0) * PPM)) + 2 * (pad + extra)
    h = int(math.ceil((y1 - y0) * PPM)) + 2 * (pad + extra)
    w += w % 2
    h += h % 2
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    # snap so that the anchor lands exactly on a pixel corner
    ax = round(w / 2.0 - cx * PPM)
    ay = round(h / 2.0 + cy * PPM)
    cx = (w / 2.0 - ax) / PPM
    cy = (ay - h / 2.0) / PPM

    cam = sc.camera
    cam.location = cx * R + cy * U - F * 100.0
    cam.data.ortho_scale = max(w, h) / PPM
    cam.data.sensor_fit = "AUTO"
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100

    ground = bpy.data.objects["ground"]
    ground.hide_render = True
    sc.render.filepath = path_obj
    bpy.ops.render.render(write_still=True)

    if path_shadow:
        ground.hide_render = False
        hidden = []
        for o in stage().objects:
            if o.type in {"MESH", "META", "CURVE"}:
                hidden.append((o, o.visible_camera))
                o.visible_camera = False
        old = sc.cycles.samples
        sc.cycles.samples = max(16, old // 2)
        sc.render.filepath = path_shadow
        bpy.ops.render.render(write_still=True)
        sc.cycles.samples = old
        for o, v in hidden:
            o.visible_camera = v
        ground.hide_render = True
    return {"w": w, "h": h, "ax": ax, "ay": ay}


# ---------------------------------------------------------------- organic helpers

def chain(points, radii, steps=6, stiff=2.0):
    """Metaball elements densely interpolated along a polyline (Catmull-Rom).

    Gives smooth merged tubes (necks, tails, legs) instead of bead strings.
    """
    pts = [Vector(p) for p in points]
    n = len(pts)
    out = []

    def cr(p0, p1, p2, p3, t):
        return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                      + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)

    for i in range(n - 1):
        p0 = pts[max(0, i - 1)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(n - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            out.append({"co": tuple(cr(p0, p1, p2, p3, t)), "r": radii[i] + (radii[i + 1] - radii[i]) * t,
                        "stiff": stiff})
    out.append({"co": tuple(pts[-1]), "r": radii[-1], "stiff": stiff})
    return out


class Surface:
    """Ray casting against meshes in world space (for placing eyes, spots, moss)."""

    def __init__(self, objs):
        from mathutils.bvhtree import BVHTree
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        verts, polys = [], []
        for o in objs:
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            base = len(verts)
            mw = ev.matrix_world
            verts.extend(mw @ v.co for v in me.vertices)
            polys.extend([base + i for i in p.vertices] for p in me.polygons)
            ev.to_mesh_clear()
        self.tree = BVHTree.FromPolygons(verts, polys)

    def hit(self, origin, direction):
        """First hit from origin along direction -> (point, normal) or (None, None)."""
        loc, nor, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, nor

    def toward(self, center, direction, dist=3.0):
        """Surface point seen from outside along direction, aiming at center."""
        d = Vector(direction).normalized()
        return self.hit(Vector(center) + d * dist, -d)


def world(o, local):
    """Local point of object o -> world (after a view layer update)."""
    bpy.context.view_layer.update()
    return o.matrix_world @ Vector(local)


def place_on(o, point, normal, parent=None):
    """Orient object o so its local +Z follows normal, at point (world space)."""
    q = Vector(normal).to_track_quat("Z", "Y")
    m = Matrix.Translation(point) @ q.to_matrix().to_4x4()
    if parent is not None:
        bpy.context.view_layer.update()
        m = parent.matrix_world.inverted() @ m
        o.parent = parent
    o.matrix_world = m if parent is None else parent.matrix_world @ m
    return o
