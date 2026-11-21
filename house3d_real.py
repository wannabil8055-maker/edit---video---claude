"""Versi realistik animasi 3D: same house & timeline as house3d.py, but with an HDRI sky,
photo-scanned PBR textures, 3D grass, real trees/shrubs and potted plants (Poly Haven, CC0).

Usage: python3 house3d_real.py OUT_DIR [--frames f ...] [--res 720] [--samples 32] [--no-persist]
Run fetch_assets.py first to download ./assets3d/.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

import house3d as H

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.join(HERE, "assets3d")
FT, P = H.FT, H.P
scene = H.scene
random.seed(11)

scene.cycles.max_bounces = 6
scene.cycles.diffuse_bounces = 3
scene.cycles.glossy_bounces = 3
scene.cycles.transmission_bounces = 4
scene.cycles.transparent_max_bounces = 8
scene.cycles.adaptive_threshold = 0.03
scene.cycles.blur_glossy = 1.0
scene.cycles.sample_clamp_indirect = 8.0
try:
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Base Contrast"
    scene.view_settings.exposure = 0.0
except Exception:
    pass


# ---------------------------------------------------------------- per-face planar UVs in world metres
def autouv(ob):
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active
    mw = ob.matrix_world
    Z = Vector((0, 0, 1))
    for poly in me.polygons:
        n = (mw.to_3x3() @ poly.normal).normalized()
        e = Z.cross(n)
        if e.length < 1e-4:
            e = Vector((1, 0, 0))
        e.normalize()
        s = n.cross(e).normalized()
        for li in poly.loop_indices:
            v = mw @ me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (v.dot(e), v.dot(s))


# ---------------------------------------------------------------- PBR material rebuild (in place)
def tex_path(name, m):
    for ext in ("jpg", "png", "exr"):
        p = os.path.join(A3, "tex", name, f"{m}.{ext}")
        if os.path.exists(p):
            return p
    return None


def pbr(mat, texname, size=1.0, tint=None, tint_mix=1.0, rough_add=0.0, normal_s=1.0, bump_s=0.0, coords="UV"):
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs[0], out.inputs[0])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / size, 1 / size, 1 / size)
    nt.links.new(tc.outputs[coords], mp.inputs["Vector"])

    def img(m, color=False):
        p = tex_path(texname, m)
        if not p:
            return None
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(p, check_existing=True)
        if not color:
            n.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    d = img("Diffuse", True)
    col = d.outputs["Color"]
    if tint:
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = tint_mix
        nt.links.new(col, mix.inputs[6])
        mix.inputs[7].default_value = (*tint, 1)
        col = mix.outputs[2]
    nt.links.new(col, b.inputs["Base Color"])
    r = img("Rough")
    if r:
        if rough_add:
            ma = nt.nodes.new("ShaderNodeMath")
            ma.operation = "ADD"
            ma.use_clamp = True
            ma.inputs[1].default_value = rough_add
            nt.links.new(r.outputs["Color"], ma.inputs[0])
            nt.links.new(ma.outputs[0], b.inputs["Roughness"])
        else:
            nt.links.new(r.outputs["Color"], b.inputs["Roughness"])
    nrm = img("nor_gl")
    normal_out = None
    if nrm:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = normal_s
        nt.links.new(nrm.outputs["Color"], nm.inputs["Color"])
        normal_out = nm.outputs["Normal"]
    disp = img("Displacement") if bump_s else None
    if disp:
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump_s
        bp.inputs["Distance"].default_value = 0.02
        nt.links.new(disp.outputs["Color"], bp.inputs["Height"])
        if normal_out:
            nt.links.new(normal_out, bp.inputs["Normal"])
        normal_out = bp.outputs["Normal"]
    if normal_out:
        nt.links.new(normal_out, b.inputs["Normal"])
    return b


pbr(H.M_ROOF, "grey_roof_tiles_02", size=1.6, tint=(0.16, 0.22, 0.42), normal_s=1.4, bump_s=0.6)
pbr(H.M_WALL, "painted_plaster_wall", size=2.0, tint=(1.0, 1.0, 0.98), tint_mix=0.0, normal_s=0.5)
_wb = H.M_WALL.node_tree.nodes["Principled BSDF"]
# brighten plaster to near-white while keeping its texture
for n in H.M_WALL.node_tree.nodes:
    if n.type == "TEX_IMAGE" and n.image and n.image.colorspace_settings.name != "Non-Color":
        g = H.M_WALL.node_tree.nodes.new("ShaderNodeBrightContrast")
        g.inputs["Bright"].default_value = 0.35
        g.inputs["Contrast"].default_value = -0.4
        H.M_WALL.node_tree.links.new(n.outputs["Color"], g.inputs["Color"])
        H.M_WALL.node_tree.links.new(g.outputs["Color"], _wb.inputs["Base Color"])
pbr(H.M_STONE, "stacked_stone_wall", size=1.2, tint=(0.8, 0.95, 1.4), normal_s=1.6, bump_s=0.8)
pbr(H.M_CONC, "brushed_concrete", size=3.0, tint=(1.0, 1.0, 1.0), tint_mix=0.0, normal_s=0.6)
pbr(H.M_STEP, "brushed_concrete", size=1.5, normal_s=0.5)
pbr(H.M_GRASS, "aerial_grass_rock", size=9.0, tint=(0.42, 0.75, 0.25), normal_s=0.8)

_gn = H.M_GRASS.node_tree
_gbsdf = _gn.nodes["Principled BSDF"]
_src = _gbsdf.inputs["Base Color"].links[0].from_socket
_nz = _gn.nodes.new("ShaderNodeTexNoise")
_nz.inputs["Scale"].default_value = 0.04
_nz.inputs["Detail"].default_value = 3.0
_ramp = _gn.nodes.new("ShaderNodeValToRGB")
_ramp.color_ramp.elements[0].color = (0.55, 0.75, 0.45, 1)
_ramp.color_ramp.elements[1].color = (1.0, 1.05, 0.85, 1)
_gn.links.new(_nz.outputs["Fac"], _ramp.inputs["Fac"])
_mx = _gn.nodes.new("ShaderNodeMix")
_mx.data_type = "RGBA"
_mx.blend_type = "MULTIPLY"
_mx.inputs["Factor"].default_value = 1.0
_gn.links.new(_src, _mx.inputs[6])
_gn.links.new(_ramp.outputs["Color"], _mx.inputs[7])
_gn.links.new(_mx.outputs[2], _gbsdf.inputs["Base Color"])

# glass: clear, slightly teal, reflective; dark interior behind it
gb = H.M_GLASS.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value = (0.55, 0.85, 0.8, 1)
gb.inputs["Roughness"].default_value = 0.02
gb.inputs["Transmission Weight"].default_value = 1.0
gb.inputs["IOR"].default_value = 1.5
H.M_FRAME.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.055, 0.065, 1)
H.M_FRAME.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.6
H.M_FRAME.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
H.M_NAVY.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.04, 0.075, 1)
M_SOFFIT = H.mat("soffit", (0.85, 0.85, 0.83), 0.6)
M_INTERIOR = H.mat("interior", (0.55, 0.52, 0.48), 0.8)

# slab top: floor plan that turns into porch/terrace tiles once the walls are up
plan_mat = H.M_PLAN
pn = plan_mat.node_tree
pb = pn.nodes["Principled BSDF"]
plan_img = [n for n in pn.nodes if n.type == "TEX_IMAGE"][0]
tile_tc = pn.nodes.new("ShaderNodeTexCoord")
tile_map = pn.nodes.new("ShaderNodeMapping")
tile_map.inputs["Scale"].default_value = (0.9, 0.9, 0.9)
pn.links.new(tile_tc.outputs["Object"], tile_map.inputs["Vector"])
tile_img = pn.nodes.new("ShaderNodeTexImage")
tile_img.image = bpy.data.images.load(tex_path("floor_tiles_06", "Diffuse"), check_existing=True)
pn.links.new(tile_map.outputs["Vector"], tile_img.inputs["Vector"])
plan_mix = pn.nodes.new("ShaderNodeMix")
plan_mix.data_type = "RGBA"
pn.links.new(plan_img.outputs["Color"], plan_mix.inputs[6])
pn.links.new(tile_img.outputs["Color"], plan_mix.inputs[7])
pn.links.new(plan_mix.outputs[2], pb.inputs["Base Color"])
plan_mix.inputs["Factor"].default_value = 0.0

# ---------------------------------------------------------------- geometry polish
for ob in list(H.col.objects):
    if ob.type != "MESH":
        continue
    if ob.name.startswith(("slab",)):
        continue
    autouv(ob)

# roofs: white soffit underneath, navy fascia on the rim
for r in [H.roof_main, H.roof_g1, H.roof_g2, H.dormer[1]]:
    r.data.materials.append(M_SOFFIT)
    r.data.materials.append(H.M_NAVY)
    mod = r.modifiers["solid"]
    mod.thickness = 0.22
    mod.material_offset = 1
    mod.material_offset_rim = 2
    mod.use_rim = True

# a dim interior floor so windows don't look into concrete-plan white
ix0, iy0 = P(0.2, 0.2)
ix1, iy1 = P(38.8, 37.8)
interior = H.box("interior_floor", (ix0 + ix1) / 2, (iy0 + iy1) / 2, H.PLINTH + 0.01, ix1 - ix0, iy0 - iy1, 0.01, M_INTERIOR)
interior.hide_render = True

# boundary wall (white with navy coping) around the sides and back, like the renders
M_BW = H.M_WALL
bw_parts = []
for (x0, y0, x1, y1) in [(-13, 13, 13, 13.2), (-13, -16, -12.8, 13), (12.8, -16, 13, 13)]:
    o = H.box("bwall", (x0 + x1) / 2, (y0 + y1) / 2, 0, abs(x1 - x0), abs(y1 - y0), 1.6, M_BW)
    c = H.box("bcap", (x0 + x1) / 2, (y0 + y1) / 2, 1.6, abs(x1 - x0) + 0.08, abs(y1 - y0) + 0.08, 0.1, H.M_NAVY)
    autouv(o)
    bw_parts += [o, c]
for x in range(-12, 13, 3):
    for (yy, xx) in [(13.1, x)]:
        p = H.box("bpost", xx, yy, 0, 0.3, 0.3, 1.85, M_BW)
        autouv(p)
        bw_parts.append(p)

# ---------------------------------------------------------------- remove the toy plants
for p in list(H.plants):
    for ch in list(p.children):
        bpy.data.objects.remove(ch, do_unlink=True)
    bpy.data.objects.remove(p, do_unlink=True)
H.plants.clear()

# ---------------------------------------------------------------- import Poly Haven models
lib_col = bpy.data.collections.new("library")
scene.collection.children.link(lib_col)
lib_layer = bpy.context.view_layer.layer_collection.children["library"]
lib_layer.exclude = True     # source objects not rendered directly


def load_objects(asset, names_filter):
    path = os.path.join(A3, "models", asset, f"{asset}.blend")
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if names_filter(n)]
    objs = [o for o in dst.objects if o is not None]
    c = bpy.data.collections.new(f"src_{asset}")
    lib_col.children.link(c)
    for o in objs:
        o.parent = None
        o.location = (0, 0, 0)
        c.objects.link(o)
    return c, objs


def instance(collection, loc, rot_z=0.0, scale=1.0, name="inst"):
    e = bpy.data.objects.new(name, None)
    e.instance_type = "COLLECTION"
    e.instance_collection = collection
    e.location = loc
    e.rotation_euler = (0, 0, rot_z)
    e.scale = (scale,) * 3
    H.col.objects.link(e)
    return e


def single_collections(asset, names_filter):
    """One collection per variant object (so each can be instanced alone)."""
    _, objs = load_objects(asset, names_filter)
    out = []
    for o in objs:
        c = bpy.data.collections.new(f"v_{o.name}")
        lib_col.children.link(c)
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        c.objects.link(o)
        out.append(c)
    return out


trees = {a: single_collections(a, lambda n, a=a: n == f"{a}_LOD1")[0]
         for a in ("island_tree_01", "island_tree_02", "island_tree_03", "tree_small_02")}
shrubs = []
for a, lod in (("shrub_02", "LOD1"), ("shrub_04", "LOD1"), ("shrub_01", "LOD1")):
    shrubs += single_collections(a, lambda n, lod=lod: n.endswith(lod))
pot_c, _ = load_objects("potted_plant_02", lambda n: True)
fern_c = single_collections("fern_02", lambda n: True)
grass_c, grass_objs = load_objects("grass_medium_01", lambda n: n.endswith("_LOD1") and "geonodes" not in n)
grass2_c, grass2_objs = load_objects("grass_bermuda_01", lambda n: n.startswith("grass_bermuda_01_") and "geometry" not in n
                                    and "dead" not in n and "flattened" not in n)
for o in grass2_objs:
    grass_c.objects.link(o)

plants = []
# tropical trees around the plot
for (x, y, a, s) in [(-10.5, 9.0, "island_tree_01", 1.5), (10.8, 10.0, "island_tree_02", 1.6),
                     (-9.5, -3.5, "island_tree_03", 1.25), (11.0, -1.5, "island_tree_01", 1.3),
                     (-4.0, 11.5, "island_tree_02", 1.35), (5.5, 11.8, "island_tree_03", 1.5),
                     (-11.5, -12.5, "tree_small_02", 1.2), (11.5, -12.0, "tree_small_02", 1.1),
                     (-22, 20, "island_tree_01", 1.8), (24, 18, "island_tree_03", 1.7), (2, 26, "island_tree_02", 1.9),
                     (-26, -4, "island_tree_02", 1.6), (27, -6, "island_tree_01", 1.7)]:
    instance(trees[a], (x, y, 0), random.uniform(0, 6.28), s, "tree")     # trees are on site from the start
# shrubs along the front of the house and the sides
fy = P(0, 39.6)[1] - 0.6
for k, x in enumerate([-5.6, -4.3, -2.9, 0.9, 2.2, 3.6, 5.0]):
    plants.append(instance(random.choice(shrubs), (x, fy - random.uniform(0, 0.3), 0), random.uniform(0, 6.28),
                           random.uniform(0.6, 0.85), "shrub"))
for y in (-3.5, -1.0, 1.5, 4.0):
    plants.append(instance(random.choice(shrubs), (P(41.5, 0)[0], y, 0), random.uniform(0, 6.28), 0.7, "shrub"))
for (x, y) in [(-7.5, -12), (-7.5, -9), (7.6, -12), (7.6, -9), (-12, -14.5), (12, -14.5)]:
    plants.append(instance(random.choice(fern_c), (x, y, 0), random.uniform(0, 6.28), 1.2, "fern"))
# potted plants at the two porch steps
for (px, py) in [(17.2, 38.6), (21.8, 38.6), (5.2, 38.6), (8.8, 38.6)]:
    X, Y = P(px, py)
    plants.append(instance(pot_c, (X, Y - 0.15, H.PLINTH), random.uniform(0, 6.28), 1.0, "pot"))

for k in range(320):
    ang = random.uniform(0, 6.283)
    rad = random.uniform(30, 75) if k < 200 else random.uniform(75, 140)
    a = random.choice(["island_tree_01", "island_tree_02", "island_tree_03", "tree_small_02"])
    instance(trees[a], (rad * math.cos(ang), rad * math.sin(ang), 0), random.uniform(0, 6.28),
             random.uniform(1.8, 2.8) * (1.0 if k < 200 else 1.6), "far_tree")

H.plants.extend(plants)

# ---------------------------------------------------------------- 3D lawn (geometry nodes scatter)
lawn_me = bpy.data.meshes.new("lawn")
import bmesh
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=60, y_segments=60, size=15.0)
bm.to_mesh(lawn_me)
bm.free()
lawn = bpy.data.objects.new("lawn", lawn_me)
lawn.location = (0, -1.5, 0.005)
H.col.objects.link(lawn)
lawn.data.materials.append(H.M_GRASS)
autouv(lawn)
dens = lawn_me.attributes.new("dens", "FLOAT", "POINT")
sx0, sy0 = P(-2.6, -1.3)
sx1, sy1 = P(40.5, 39.2)
dx0, dx1 = P(14.5, 0)[0] - 0.2, P(24.5, 0)[0] + 0.2
for v in lawn_me.vertices:
    w = lawn.matrix_world @ v.co
    d = 1.0
    if sx0 - 0.3 < w.x < sx1 + 0.3 and sy1 - 0.3 < w.y < sy0 + 0.3:
        d = 0.0
    if dx0 < w.x < dx1 and w.y < sy1:
        d = 0.0
    if abs(w.x) > 12.6 or w.y > 12.9:
        d = 0.0
    dens.data[v.index].value = d

ng = bpy.data.node_groups.new("scatter_grass", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
N = ng.nodes
gi = N.new("NodeGroupInput")
go = N.new("NodeGroupOutput")
dist = N.new("GeometryNodeDistributePointsOnFaces")
dist.distribute_method = "RANDOM"
mul = N.new("ShaderNodeMath")
mul.operation = "MULTIPLY"
mul.inputs[1].default_value = 160.0      # grass clumps per m^2
na = N.new("GeometryNodeInputNamedAttribute")
na.data_type = "FLOAT"
na.inputs["Name"].default_value = "dens"
ci = N.new("GeometryNodeCollectionInfo")
ci.inputs["Collection"].default_value = grass_c
ci.inputs["Separate Children"].default_value = True
ci.inputs["Reset Children"].default_value = True
iop = N.new("GeometryNodeInstanceOnPoints")
iop.inputs["Pick Instance"].default_value = True
rr = N.new("FunctionNodeRandomValue")
rr.data_type = "FLOAT_VECTOR"
rr.inputs["Min"].default_value = (0, 0, 0)
rr.inputs["Max"].default_value = (0, 0, 6.283)
rs = N.new("FunctionNodeRandomValue")
rs.data_type = "FLOAT"
rs.inputs["Min"].default_value = 0.8
rs.inputs["Max"].default_value = 1.6
join = N.new("GeometryNodeJoinGeometry")
L = ng.links
L.new(gi.outputs[0], dist.inputs["Mesh"])
L.new(na.outputs["Attribute"], mul.inputs[0])
L.new(mul.outputs[0], dist.inputs["Density"])
L.new(dist.outputs["Points"], iop.inputs["Points"])
L.new(ci.outputs[0], iop.inputs["Instance"])
L.new(rr.outputs["Value"], iop.inputs["Rotation"])
L.new(rs.outputs["Value"], iop.inputs["Scale"])
L.new(gi.outputs[0], join.inputs[0])
L.new(iop.outputs[0], join.inputs[0])
L.new(join.outputs[0], go.inputs[0])
gmod = lawn.modifiers.new("grass", "NODES")
gmod.node_group = ng

# ---------------------------------------------------------------- HDRI world, aligned so the sun lights the facade
world = scene.world
wn = world.node_tree
wn.nodes.clear()
wout = wn.nodes.new("ShaderNodeOutputWorld")
wbg = wn.nodes.new("ShaderNodeBackground")
wbg.inputs["Strength"].default_value = 1.0
env = wn.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(os.path.join(A3, "hdri", "kloofendal_48d_partly_cloudy_puresky.hdr"))
wtc = wn.nodes.new("ShaderNodeTexCoord")
wmp = wn.nodes.new("ShaderNodeMapping")
wn.links.new(wtc.outputs["Generated"], wmp.inputs["Vector"])
wn.links.new(wmp.outputs["Vector"], env.inputs["Vector"])
wn.links.new(env.outputs["Color"], wbg.inputs["Color"])
wn.links.new(wbg.outputs[0], wout.inputs[0])


def hdri_sun_dir(img):
    import numpy as np
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    lum = px[..., 0] * 0.2126 + px[..., 1] * 0.7152 + px[..., 2] * 0.0722
    y, x = np.unravel_index(np.argmax(lum), lum.shape)
    u, v = (x + 0.5) / w, (y + 0.5) / h
    phi = (u - 0.5) * 2 * math.pi           # atan2(dir.y, -dir.x)
    el = (v - 0.5) * math.pi
    return math.atan2(math.sin(phi), -math.cos(phi)), el


sun_az, sun_el = hdri_sun_dir(env.image)
target_az = math.atan2(-math.cos(math.radians(30)), math.sin(math.radians(30)))   # front-right
wmp.inputs["Rotation"].default_value = (0, 0, sun_az - target_az)
print(f"HDRI sun elevation {math.degrees(sun_el):.1f} deg")
# the sun lamp from house3d.py is replaced by the HDRI sun, but keep a soft fill
H.sun.data.energy = 0.0
H.sun.hide_render = True

# subtle depth of field
H.cam.data.dof.use_dof = True
H.cam.data.dof.focus_object = H.target
H.cam.data.dof.aperture_fstop = 8.0

_orig_set_frame = H.set_frame


def set_frame(f):
    _orig_set_frame(f)
    t = f / H.FPS
    plan_mix.inputs["Factor"].default_value = H.ease((t - 5.0) / 1.5)
    interior.hide_render = t < 6.3
    for p in bw_parts:
        p.hide_render = False


H.set_frame = set_frame

if __name__ == "__main__":
    if "--samples" not in sys.argv:
        sys.argv += ["--samples", "32"]
    H.main()
