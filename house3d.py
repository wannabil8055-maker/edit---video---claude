"""Animasi 3D rumah: pelan lantai -> dinding naik -> tingkap -> bumbung -> drone orbit.

Builds the house in Blender (bpy) from the floor plan dimensions (39' x 38')
and renders a frame sequence with Cycles.

Usage: python3 house3d.py OUT_DIR [--frames f1 f2 ...] [--res 720] [--samples 24]
Frames are numbered from 0 at 24 fps; the sequence lasts SEQ seconds.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FT = 0.3048
FPS = 24
SEQ = 14.5                   # seconds of 3D animation
NF = int(SEQ * FPS)

PLINTH = 0.45                # floor slab height (m)
WALL_H = 10 * FT             # wall height (m)
WALL_T = 0.5 * FT


def P(x, y):
    """Plan feet (origin back-left, y down towards the front) -> Blender metres."""
    return ((x - 19.5) * FT, (19.0 - y) * FT)


# ---------------------------------------------------------------- easing
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def back(t, s=1.8):
    t = clamp(t)
    t -= 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def bounce(t):
    t = clamp(t)
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


# ---------------------------------------------------------------- scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.render.fps = FPS
scene.render.use_persistent_data = True
scene.cycles.max_bounces = 4
scene.cycles.diffuse_bounces = 2
scene.cycles.glossy_bounces = 2
scene.cycles.transmission_bounces = 2
scene.cycles.transparent_max_bounces = 2
scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.04
try:
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Punchy"
    scene.view_settings.exposure = -0.9
except Exception:
    pass

col = bpy.data.collections.new("house")
scene.collection.children.link(col)


def mat(name, color, rough=0.6, metal=0.0, spec=0.5, emit=None, emit_s=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_s
    return m


def add_bump(m, kind, scale, strength, extra=None):
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if kind == "wave":
        tex = nt.nodes.new("ShaderNodeTexWave")
        tex.inputs["Scale"].default_value = scale
        tex.wave_type = "BANDS"
        if extra:
            tex.bands_direction = extra
    elif kind == "brick":
        tex = nt.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Scale"].default_value = scale
    else:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    out = tex.outputs["Fac"] if "Fac" in tex.outputs else tex.outputs[0]
    nt.links.new(out, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return tex


M_WALL = mat("wall", (0.86, 0.86, 0.84), 0.55)
M_NAVY = mat("navy", (0.025, 0.035, 0.07), 0.45)
M_ROOF = mat("roof", (0.018, 0.026, 0.065), 0.35, spec=0.6)
add_bump(M_ROOF, "wave", 6.0, 0.35, "Y")
M_STONE = mat("stone", (0.05, 0.07, 0.14), 0.7)
add_bump(M_STONE, "brick", 14.0, 0.6)
M_FRAME = mat("frame", (0.03, 0.035, 0.045), 0.35)
M_GLASS = mat("glass", (0.02, 0.16, 0.15), 0.06, spec=1.0)
M_DOOR = mat("door", (0.03, 0.04, 0.07), 0.4)
M_GRASS = mat("grass", (0.09, 0.22, 0.04), 0.9, spec=0.2)
M_CONC = mat("concrete", (0.6, 0.6, 0.58), 0.8)
M_STEP = mat("step", (0.5, 0.5, 0.52), 0.5)
M_BUSH = mat("bush", (0.04, 0.16, 0.03), 0.8, spec=0.2)
M_TRUNK = mat("trunk", (0.12, 0.08, 0.05), 0.9)
M_TREE = mat("tree", (0.05, 0.14, 0.04), 0.85, spec=0.2)
M_GABLE = mat("gable", (0.88, 0.88, 0.86), 0.5)
add_bump(M_GABLE, "wave", 9.0, 0.25, "X")

# grass colour variation
_nt = M_GRASS.node_tree
_noise = _nt.nodes.new("ShaderNodeTexNoise")
_noise.inputs["Scale"].default_value = 0.15
_ramp = _nt.nodes.new("ShaderNodeValToRGB")
_ramp.color_ramp.elements[0].color = (0.06, 0.16, 0.03, 1)
_ramp.color_ramp.elements[1].color = (0.14, 0.28, 0.05, 1)
_nt.links.new(_noise.outputs["Fac"], _ramp.inputs["Fac"])
_nt.links.new(_ramp.outputs["Color"], _nt.nodes["Principled BSDF"].inputs["Base Color"])
_gn = _nt.nodes.new("ShaderNodeTexNoise")
_gn.inputs["Scale"].default_value = 90.0
_gn.inputs["Detail"].default_value = 6.0
_gb = _nt.nodes.new("ShaderNodeBump")
_gb.inputs["Strength"].default_value = 0.6
_nt.links.new(_gn.outputs["Fac"], _gb.inputs["Height"])
_nt.links.new(_gb.outputs["Normal"], _nt.nodes["Principled BSDF"].inputs["Normal"])

# floor plan texture on the slab top
M_PLAN = mat("plan", (1, 1, 1), 0.6)
_img = bpy.data.images.load(os.path.join(HERE, "assets", "pelan_crop.png"))
_tx = M_PLAN.node_tree.nodes.new("ShaderNodeTexImage")
_tx.image = _img
M_PLAN.node_tree.links.new(_tx.outputs["Color"], M_PLAN.node_tree.nodes["Principled BSDF"].inputs["Base Color"])


def box(name, cx, cy, z0, sx, sy, sz, m, parent_col=col):
    """Axis-aligned box, origin at the bottom centre (so scale.z grows it up)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.z += 0.5
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = (cx, cy, z0)
    ob.data.materials.append(m)
    parent_col.objects.link(ob)
    return ob


# ---------------------------------------------------------------- ground & site
ground = box("ground", 0, 0, -0.2, 4000, 4000, 0.2, M_GRASS)
fx0, fy0 = P(14.5, 38.5)
fx1, fy1 = P(24.5, 38.5)
drive = box("drive", (fx0 + fx1) / 2, fy0 - 9, 0.0, 10 * FT * 1.6, 18, 0.03, M_CONC)

# slab with the plan texture on top (plan crop spans x -2.27..40.15 ft, y -0.98..38.8 ft)
sx0, sy0 = P(-2.27, -0.98)
sx1, sy1 = P(40.15, 38.8)
slab = box("slab", (sx0 + sx1) / 2, (sy0 + sy1) / 2, 0, sx1 - sx0, sy0 - sy1, PLINTH, M_CONC)
slab.data.materials.append(M_PLAN)
me = slab.data
uv = me.uv_layers.new()
for poly in me.polygons:
    if poly.normal.z > 0.9:
        poly.material_index = 1
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (v.x / (sx1 - sx0) + 0.5, v.y / (sy0 - sy1) + 0.5)

# ---------------------------------------------------------------- walls
EXT = [(8.9, 0), (34.1, 0), (34.1, 2.8), (39, 2.8), (39, 38), (25.9, 38), (25.9, 33.9),
       (14, 33.9), (14, 30.1), (3, 30.1), (3, 17.2), (0, 17.2), (0, 2.8), (8.9, 2.8)]
INT = [((14, 0), (14, 10)), ((23.9, 0), (23.9, 10)), ((14, 10), (21.5, 10)), ((23.2, 10), (34.1, 10)),
       ((8.9, 2.8), (8.9, 7.1)), ((8.9, 7.1), (12.2, 7.1)), ((34.1, 2.8), (34.1, 10)), ((34.1, 10), (36.0, 10)),
       ((28, 11.8), (28, 19.8)), ((28, 19.8), (39, 19.8)), ((31.1, 19.8), (31.1, 24.8)),
       ((25.9, 24.8), (37.0, 24.8)), ((25.9, 26.8), (25.9, 33.9)), ((3, 17.2), (14, 17.2)),
       ((14, 17.2), (14, 19.5))]

walls = []          # (object, rise order 0..1)


def wall(a, b, ext=True):
    (x1, y1), (x2, y2) = a, b
    (X1, Y1), (X2, Y2) = P(x1, y1), P(x2, y2)
    t = WALL_T
    if abs(Y1 - Y2) < 1e-6:
        ob = box("wall", (X1 + X2) / 2, Y1, PLINTH, abs(X2 - X1) + t, t, WALL_H, M_WALL)
    else:
        ob = box("wall", X1, (Y1 + Y2) / 2, PLINTH, t, abs(Y2 - Y1) + t, WALL_H, M_WALL)
    parts = [ob]
    if ext:   # navy skirting band
        if abs(Y1 - Y2) < 1e-6:
            sk = box("skirt", (X1 + X2) / 2, Y1, PLINTH, abs(X2 - X1) + t + 0.04, t + 0.04, 1.4 * FT, M_NAVY)
        else:
            sk = box("skirt", X1, (Y1 + Y2) / 2, PLINTH, t + 0.04, abs(Y2 - Y1) + t + 0.04, 1.4 * FT, M_NAVY)
        parts.append(sk)
        # navy band at the top of the wall
        if abs(Y1 - Y2) < 1e-6:
            tb = box("band", (X1 + X2) / 2, Y1, PLINTH + WALL_H - 0.35, abs(X2 - X1) + t + 0.04, t + 0.04, 0.12, M_NAVY)
        else:
            tb = box("band", X1, (Y1 + Y2) / 2, PLINTH + WALL_H - 0.35, t + 0.04, abs(Y2 - Y1) + t + 0.04, 0.12, M_NAVY)
        parts.append(tb)
    return parts


for i in range(len(EXT)):
    a, b = EXT[i], EXT[(i + 1) % len(EXT)]
    walls.append(wall(a, b, True))
for a, b in INT:
    walls.append(wall(a, b, False))

# stone cladding on the master bedroom front and right gable front
cx0, cy = P(25.9, 38)
cx1, _ = P(39, 38)
stone = box("stone", (cx0 + cx1) / 2, cy - WALL_T / 2 - 0.03, PLINTH + 1.4 * FT, cx1 - cx0 + 0.1, 0.06, WALL_H - 1.4 * FT - 0.4, M_STONE)

# ---------------------------------------------------------------- openings (windows / doors)
# (wall axis 'x' for walls running along x at plan y, 'y' for walls along y at plan x), pos, centre, w, h, sill
OPEN = [
    ("x", 38.0, 32.5, 6.0, 5.5, 2.8, "win"), ("x", 33.9, 17.2, 3.2, 7.4, 0.0, "door"),
    ("x", 33.9, 21.8, 5.5, 7.0, 0.0, "win"), ("x", 30.1, 8.5, 5.0, 5.0, 3.0, "win"),
    ("y", 39.0, 6.4, 2.0, 2.0, 5.5, "win"), ("y", 39.0, 15.0, 4.0, 5.0, 3.0, "win"),
    ("y", 39.0, 22.3, 2.0, 2.0, 5.5, "win"), ("y", 39.0, 31.0, 4.0, 5.0, 3.0, "win"),
    ("y", 0.0, 10.0, 4.0, 4.0, 3.5, "win"), ("y", 3.0, 23.5, 4.0, 5.0, 3.0, "win"),
    ("x", 0.0, 19.0, 4.0, 4.0, 4.0, "win"), ("x", 0.0, 29.0, 4.0, 4.0, 4.0, "win"),
    ("x", 0.0, 11.5, 2.0, 2.0, 5.5, "win"), ("x", 2.8, 4.5, 3.0, 3.0, 4.5, "win"),
    ("x", 2.8, 36.5, 2.0, 2.0, 5.5, "win"),
]
openings = []
for ax, pos, c, w, h, sill, kind in OPEN:
    if ax == "x":
        X, Y = P(c, pos)
        sx, sy = w * FT, WALL_T + 0.1
        gx, gy = (w - 0.45) * FT, WALL_T + 0.16
    else:
        X, Y = P(pos, c)
        sx, sy = WALL_T + 0.1, w * FT
        gx, gy = WALL_T + 0.16, (w - 0.45) * FT
    z0 = PLINTH + sill * FT
    fr = box(kind + "_frame", X, Y, z0, sx, sy, h * FT, M_FRAME)
    inner = box(kind + "_glass", X, Y, z0 + 0.22 * FT, gx, gy, (h - 0.45) * FT, M_DOOR if kind == "door" else M_GLASS)
    inner.parent = fr
    inner.location = (0, 0, 0.22 * FT)
    if kind == "win":   # mullions
        if ax == "x":
            mb = box("mull", 0, 0, 0, 0.05, gy + 0.02, (h - 0.45) * FT, M_FRAME)
        else:
            mb = box("mull", 0, 0, 0, gx + 0.02, 0.05, (h - 0.45) * FT, M_FRAME)
        mb.parent = fr
        mb.location = (0, 0, 0.22 * FT)
    openings.append(fr)

# porch columns (navy stone) and front steps
columns = []
for (x, y) in [(0.4, 37.6), (14.0, 37.6), (25.9, 37.6)]:
    X, Y = P(x, y)
    c1 = box("col", X, Y, PLINTH, 0.42, 0.42, WALL_H, M_STONE)
    cap = box("cap", 0, 0, 0, 0.5, 0.5, 0.18, M_NAVY)
    cap.parent = c1
    cap.location = (0, 0, WALL_H - 0.5)
    columns.append(c1)
steps = []
for k in range(3):
    X, Y = P(19.5, 38.8)
    steps.append(box("step", X, Y - k * 0.28 - 0.1, 0, 3.0, 0.3 + 0.0, PLINTH - k * 0.15, M_STEP))
    X2, Y2 = P(7.0, 38.8)
    steps.append(box("step", X2, Y2 - k * 0.28 - 0.1, 0, 2.4, 0.3, PLINTH - k * 0.15, M_STEP))

# ---------------------------------------------------------------- roof
EAVE = PLINTH + WALL_H
PITCH = 0.72


def mesh_obj(name, verts, faces, m, solid=0.12):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(m)
    col.objects.link(ob)
    if solid:
        mod = ob.modifiers.new("solid", "SOLIDIFY")
        mod.thickness = solid
        mod.offset = 1.0
    return ob


def hip_roof(x0, y0, x1, y1, z):
    X0, Y0 = P(x0, y1)
    X1, Y1 = P(x1, y0)      # Y1 > Y0 (back)
    w, d = X1 - X0, Y1 - Y0
    h = PITCH * min(w, d) / 2
    if w >= d:
        r0 = (X0 + d / 2, (Y0 + Y1) / 2, z + h)
        r1 = (X1 - d / 2, (Y0 + Y1) / 2, z + h)
    else:
        r0 = ((X0 + X1) / 2, Y0 + w / 2, z + h)
        r1 = ((X0 + X1) / 2, Y1 - w / 2, z + h)
    v = [(X0, Y0, z), (X1, Y0, z), (X1, Y1, z), (X0, Y1, z), r0, r1]
    if w >= d:
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (3, 0, 4), (1, 2, 5)]
    else:
        f = [(0, 1, 4), (2, 3, 5), (3, 0, 4, 5), (1, 2, 5, 4)]
    return v, f


def gable(x0, x1, yfront, yback, z, name):
    X0, Yf = P(x0, yfront)
    X1, Yb = P(x1, yback)
    h = PITCH * (X1 - X0) / 2
    xm = (X0 + X1) / 2
    z += 0.08
    v = [(X0, Yf, z), (xm, Yf, z + h), (X1, Yf, z), (X0, Yb, z), (xm, Yb, z + h), (X1, Yb, z)]
    f = [(0, 1, 4, 3), (1, 2, 5, 4)]
    roof = mesh_obj(name, v, f, M_ROOF)
    # white boarded gable face, set back under the overhang
    inset = 0.35
    gv = [(X0 + inset, Yf + inset, z - 0.02), (xm, Yf + inset, z + h - inset * 0.9), (X1 - inset, Yf + inset, z - 0.02)]
    face = mesh_obj(name + "_face", gv, [(0, 1, 2)], M_GABLE, solid=0.05)
    face.parent = roof
    face.matrix_parent_inverse = roof.matrix_world.inverted()
    # navy fascia boards along the gable edges
    for (a, b) in ((0, 1), (1, 2)):
        pa, pb = Vector(v[a]), Vector(v[b])
        mid = (pa + pb) / 2
        length = (pb - pa).length
        fb = box(name + "_fascia", 0, 0, 0, length, 0.06, 0.22, M_NAVY)
        fb.location = (mid.x, mid.y - 0.03, mid.z - 0.12)
        fb.rotation_euler = (0, -math.atan2(pb.z - pa.z, pb.x - pa.x), 0)
        fb.parent = roof
        fb.matrix_parent_inverse = roof.matrix_world.inverted()
    return roof


rv, rf = hip_roof(-1.6, -1.6, 40.6, 39.6, EAVE)
roof_main = mesh_obj("roof_main", rv, rf, M_ROOF)
roof_g1 = gable(-1.9, 15.0, 39.9, 29.0, EAVE, "gable_left")
roof_g2 = gable(25.0, 40.9, 39.9, 29.0, EAVE, "gable_right")
# dormer on the front slope
dX, dY = P(19.5, 33.0)
dh = EAVE + PITCH * 6.6 * FT
dormer_body = box("dormer", dX, dY + 0.3, dh - 0.5, 1.7, 1.4, 1.2, M_WALL)
dv = [(dX - 1.05, dY - 0.45, dh + 0.7), (dX, dY - 0.45, dh + 1.45), (dX + 1.05, dY - 0.45, dh + 0.7),
      (dX - 1.05, dY + 1.2, dh + 0.7), (dX, dY + 1.2, dh + 1.45), (dX + 1.05, dY + 1.2, dh + 0.7)]
dormer_roof = mesh_obj("dormer_roof", dv, [(0, 1, 4, 3), (1, 2, 5, 4)], M_ROOF, solid=0.08)
dwin = box("dormer_win", dX, dY - 0.42, dh - 0.25, 0.9, 0.06, 0.8, M_GLASS)
gface = mesh_obj("dormer_face", [(dX - 0.85, dY - 0.38, dh + 0.62), (dX, dY - 0.38, dh + 1.3), (dX + 0.85, dY - 0.38, dh + 0.62)],
                 [(0, 1, 2)], M_GABLE, solid=0.03)
dormer = [dormer_body, dormer_roof, dwin, gface]
roofs = [roof_main, roof_g1, roof_g2]

# ---------------------------------------------------------------- plants
import random
random.seed(4)
plants = []


def bush(x, y, r):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(x, y, r * 0.8))
    ob = bpy.context.active_object
    for c in ob.users_collection:
        c.objects.unlink(ob)
    col.objects.link(ob)
    ob.data.materials.append(M_BUSH)
    for v in ob.data.vertices:
        v.co *= 1 + random.uniform(-0.12, 0.12)
    bpy.ops.object.shade_smooth() if False else None
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def tree(x, y, h):
    t = box("trunk", x, y, 0, 0.35, 0.35, h * 0.45, M_TRUNK)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=h * 0.32, location=(x, y, h * 0.7))
    ob = bpy.context.active_object
    for c in ob.users_collection:
        c.objects.unlink(ob)
    col.objects.link(ob)
    ob.data.materials.append(M_TREE)
    for v in ob.data.vertices:
        v.co.x += random.uniform(-0.3, 0.3)
        v.co.y += random.uniform(-0.3, 0.3)
        v.co.z += random.uniform(-0.3, 0.3)
    for p in ob.data.polygons:
        p.use_smooth = True
    ob.parent = t
    ob.matrix_parent_inverse = t.matrix_world.inverted()
    return t


for x in (-4.5, -3.0, 1.0, 2.6, 5.4, 6.8):
    X, Y = P(0, 40.5)
    plants.append(bush(x, Y - random.uniform(0, 0.4), random.uniform(0.35, 0.5)))
for y in (-3.0, 0.5, 4.0):
    plants.append(bush(P(42, 0)[0], y, random.uniform(0.4, 0.55)))
for (x, y, h) in [(-11, 9, 9), (-13, -2, 7.5), (12, 11, 10), (14, 1, 8), (-6, 14, 8.5), (5, 15, 9.5), (17, -8, 7), (-16, -10, 8)]:
    plants.append(tree(x, y, h))

# ---------------------------------------------------------------- world, sun, camera
world = bpy.data.worlds.new("world")
scene.world = world
world.use_nodes = True
wn = world.node_tree
sky = wn.nodes.new("ShaderNodeTexSky")
for st in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING", "HOSEK_WILKIE"):
    try:
        sky.sky_type = st
        break
    except Exception:
        continue
try:
    sky.sun_elevation = math.radians(28)
    sky.sun_rotation = math.radians(215)
    sky.altitude = 100
except Exception:
    pass
bg = wn.nodes["Background"]
bg.inputs["Strength"].default_value = 0.22
wn.links.new(sky.outputs["Color"], bg.inputs["Color"])

sun_d = bpy.data.lights.new("sun", "SUN")
sun_d.energy = 2.6
sun_d.angle = math.radians(2.5)
sun_d.color = (1.0, 0.93, 0.82)
sun = bpy.data.objects.new("sun", sun_d)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(62), 0, math.radians(215 - 180))

cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 22
cam_d.sensor_fit = "AUTO"
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
scene.camera = cam
target = bpy.data.objects.new("target", None)
scene.collection.objects.link(target)
tc = cam.constraints.new("TRACK_TO")
tc.target = target
tc.track_axis = "TRACK_NEGATIVE_Z"
tc.up_axis = "UP_Y"


# ---------------------------------------------------------------- animation (per frame)
def lerp(a, b, k):
    return a + (b - a) * k


def set_frame(f):
    t = f / FPS
    # slab + plan appear 0..1.2
    k = ease(t / 1.0)
    slab.scale.z = max(0.001, k)
    # walls rise 2.0 .. 5.0 (exterior first, interior staggered)
    nW = len(walls)
    for i, parts in enumerate(walls):
        st = 2.0 + 2.2 * i / nW
        kz = back((t - st) / 0.8, 1.2)
        for p in parts:
            p.scale.z = max(0.001, kz)
            p.hide_render = kz <= 0.002
    stone.scale.z = max(0.001, ease((t - 4.4) / 0.6))
    stone.hide_render = t < 4.4
    # windows / doors pop 5.0 .. 6.5
    for i, o in enumerate(openings):
        ks = back((t - 5.0 - 1.2 * i / len(openings)) / 0.4, 2.0)
        o.scale = (max(0.001, ks),) * 3
        o.hide_render = ks <= 0.002
        for ch in o.children:
            ch.hide_render = o.hide_render
    for i, c1 in enumerate(columns):
        kz = back((t - 5.2 - 0.2 * i) / 0.6, 1.2)
        c1.scale.z = max(0.001, kz)
        c1.hide_render = kz <= 0.002
        for ch in c1.children:
            ch.hide_render = c1.hide_render
    for s in steps:
        s.scale.z = max(0.001, ease((t - 5.6) / 0.5))
        s.hide_render = t < 5.6
    # roofs drop from the sky with a bounce 6.5 .. 8.0
    for i, r in enumerate(roofs):
        st = 6.4 + 0.35 * i
        kk = bounce((t - st) / 1.0)
        r.location.z = (1 - kk) * 14
        hide = t < st - 0.05
        r.hide_render = hide
        for ch in r.children:
            ch.hide_render = hide
    for o in dormer:                     # dormer appears once the main roof has landed
        o.hide_render = t < 7.45
    # plants grow 7.6 .. 9.0
    for i, p in enumerate(plants):
        kp = back((t - 7.4 - 1.4 * i / len(plants)) / 0.5, 1.6)
        p.scale = (max(0.001, kp),) * 3
        p.hide_render = kp <= 0.002
        for ch in p.children:
            ch.hide_render = p.hide_render

    # camera: top-down -> aerial 3/4 orbit -> eye-level front
    keys = [  # time, azimuth deg (0 = front), polar deg (0 = straight down), distance, target z
        (0.0, 150, 3, 23, 0.5),
        (2.0, 140, 8, 22, 0.8),
        (5.0, 85, 42, 21, 1.5),
        (7.5, 40, 58, 24, 2.5),
        (10.5, -20, 66, 21, 2.2),
        (14.5, -8, 84, 15.5, 2.2),
    ]
    for j in range(len(keys) - 1):
        if keys[j][0] <= t <= keys[j + 1][0] or j == len(keys) - 2:
            a, b = keys[j], keys[j + 1]
            kk = ease_io((t - a[0]) / (b[0] - a[0]))
            break
    az = math.radians(lerp(a[1], b[1], kk))
    po = math.radians(lerp(a[2], b[2], kk))
    d = lerp(a[3], b[3], kk)
    tz = lerp(a[4], b[4], kk)
    target.location = (0, -0.6, tz)
    cam.location = (d * math.sin(po) * math.sin(az), -d * math.sin(po) * math.cos(az) - 0.6, tz + d * math.cos(po))


# ---------------------------------------------------------------- render
def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = 720
    samples = 24
    if "--res" in sys.argv:
        res = int(sys.argv[sys.argv.index("--res") + 1])
    if "--samples" in sys.argv:
        samples = int(sys.argv[sys.argv.index("--samples") + 1])
    scene.render.resolution_x = res
    scene.render.resolution_y = int(res * 16 / 9)
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    if "--no-persist" in sys.argv:      # persistent data occasionally leaves stale shading
        scene.render.use_persistent_data = False
    if "--frames" in sys.argv:
        frames = [int(x) for x in sys.argv[sys.argv.index("--frames") + 1:] if x.lstrip("-").isdigit()]
    else:
        start = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 0
        end = int(sys.argv[sys.argv.index("--end") + 1]) if "--end" in sys.argv else NF
        step = int(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 1
        frames = range(start, end, step)
    import time
    for f in frames:
        path = os.path.join(out, f"{f:04d}.png")
        if os.path.exists(path) and "--force" not in sys.argv:
            continue
        set_frame(f)
        scene.frame_set(f)
        scene.render.filepath = path
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"frame {f} {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
