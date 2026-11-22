"""Five-lot version of the realistic house scene: five plots side by side along a
road, each house built one after another, camera flies from top-down over the row
to a low aerial view down the street.

Usage: python3 house3d_lots.py OUT_DIR [--frames ...|--start --end --step] [--res N] [--samples N]
       [--force] [--no-persist]
Needs ./assets3d (python3 fetch_assets.py).
"""
import math
import random
import sys

import bpy

import house3d as H
import house3d_real as R

random.seed(11)
LOT_W = 16.0                                   # plot 16 m x 29 m = ~5,000 sq ft
HALF = LOT_W / 2
N_LOTS = 5
OFFS = [(i - (N_LOTS - 1) / 2) * LOT_W for i in range(N_LOTS)]   # x offset of each plot
DELAY = [0.0, 0.35, 0.7, 1.05, 1.4]            # build start per plot (s), left -> right
SEQ = 11.5
H.NF = int(SEQ * H.FPS)

col = H.col
# ---------------------------------------------------------------- clear what does not fit the row
for o in list(col.objects):
    n = o.name
    if n.startswith("far_tree") or (n.startswith("tree") and (abs(o.location.x) > 7.0 or o.location.y > 12.5)):
        bpy.data.objects.remove(o, do_unlink=True)
    elif n.startswith("fern") and abs(o.location.x) > 9:
        o.location.x = 6.8 if o.location.x > 0 else -6.8
        o.location.y = -18.0

# ---------------------------------------------------------------- narrower plot: boundary walls at +-HALF
for p in R.bw_parts:
    bpy.data.objects.remove(p, do_unlink=True)
R.bw_parts.clear()
for (x0, y0, x1, y1) in [(-HALF, 13, HALF, 13.2), (-HALF, -16, -HALF + 0.2, 13), (HALF - 0.2, -16, HALF, 13)]:
    o = H.box("bwall", (x0 + x1) / 2, (y0 + y1) / 2, 0, abs(x1 - x0), abs(y1 - y0), 1.6, H.M_WALL)
    c = H.box("bcap", (x0 + x1) / 2, (y0 + y1) / 2, 1.6, abs(x1 - x0) + 0.08, abs(y1 - y0) + 0.08, 0.1, H.M_NAVY)
    R.autouv(o)
    R.bw_parts += [o, c]
for x in range(-6, 7, 3):
    p = H.box("bpost", x, 13.1, 0, 0.3, 0.3, 1.85, H.M_WALL)
    R.autouv(p)
    R.bw_parts.append(p)
# lawn: squeeze the mesh to the plot width and re-mask the grass scatter
lawn = R.lawn
for v in lawn.data.vertices:
    v.co.x *= (LOT_W + 0.4) / 30.0
R.autouv(lawn)
for v in lawn.data.vertices:
    w = lawn.matrix_world @ v.co
    if abs(w.x) > HALF - 0.35:
        R.dens.data[v.index].value = 0.0

# ---------------------------------------------------------------- copy the plot for the other lots
skip = {"ground"}
src = [o for o in col.objects if o.name.split(".")[0] not in skip]
lots = []          # per lot: list of (original, copy)
for i, off in enumerate(OFFS):
    if off == 0:
        lots.append([(o, o) for o in src])
        continue
    m = {}
    for o in src:
        c = o.copy()                     # linked duplicate (shares mesh data)
        col.objects.link(c)
        m[o] = c
    for o, c in m.items():
        if o.parent in m:
            c.parent = m[o.parent]
            c.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        if o.name.startswith("tree"):    # vary the trees between plots
            c.rotation_euler.z = random.uniform(0, 6.28)
    lots.append(list(m.items()))
CENTER = OFFS.index(0)

# the plan/tiles material is shared, keep it on the slowest plot's timing
# ---------------------------------------------------------------- road in front of the plots
road = H.box("road", 0, -27.2, 0.0, 400, 7.0, 0.04, H.M_CONC)
R.autouv(road)
M_ROAD = H.mat("asphalt", (0.05, 0.05, 0.055), 0.85)
R.pbr(M_ROAD, "brushed_concrete", 3.0, (0.12, 0.12, 0.13), 0.85, 0.15, 0.6, 0.0)
road.data.materials.clear()
road.data.materials.append(M_ROAD)
M_PAINT = H.mat("paint", (0.85, 0.85, 0.8), 0.6)
for k in range(-40, 41):                       # dashed centre line
    H.box("dash", k * 5.0, -27.2, 0.041, 2.4, 0.15, 0.005, M_PAINT)
for s in (-23.6, -30.8):                       # kerbs
    H.box("kerb", 0, s, 0.0, 400, 0.25, 0.12, H.M_STEP)

# ---------------------------------------------------------------- surroundings: trees around the estate
for k in range(700):
    while True:
        x = random.uniform(-220, 220)
        y = random.uniform(-220, 220)
        if not (-48 < x < 48 and -36 < y < 18):
            break
    a = random.choice(["island_tree_01", "island_tree_02", "island_tree_03", "tree_small_02"])
    R.instance(R.trees[a], (x, y, 0), random.uniform(0, 6.28), random.uniform(2.0, 3.2), "far_tree")
for k in range(40):                            # a few trees across the road
    x = random.uniform(-90, 90)
    y = random.uniform(-48, -34)
    a = random.choice(["island_tree_01", "island_tree_02", "island_tree_03"])
    R.instance(R.trees[a], (x, y, 0), random.uniform(0, 6.28), random.uniform(1.5, 2.2), "far_tree")

# dense tropical tree belt hugging the estate so the bare ground plane is not seen
for k in range(420):
    while True:
        x = random.uniform(-80, 80)
        y = random.uniform(-70, 60)
        inside = -44 < x < 44 and -33 < y < 15
        if not inside and abs(x) < 44 + 30 and -33 - 30 < y < 15 + 30:
            break
    a = random.choice(["island_tree_01", "island_tree_02", "island_tree_03", "tree_small_02"])
    R.instance(R.trees[a], (x, y, 0), random.uniform(0, 6.28), random.uniform(1.6, 2.6), "far_tree")
# ground outside the plots: darker, richer grass than the bare texture
gm = H.M_GRASS.copy()
for n in gm.node_tree.nodes:
    if n.type == "VALTORGB":
        for el in n.color_ramp.elements:
            el.color = (el.color[0] * 0.6, el.color[1] * 0.7, el.color[2] * 0.45, 1)
ground = [o for o in col.objects if o.name == "ground"][0]
ground.data.materials[0] = gm

H.cam.data.dof.use_dof = False
H.cam.data.clip_end = 1000

# ---------------------------------------------------------------- animation
_base = H.set_frame


def lerp(a, b, k):
    return a + (b - a) * k


CAM = [  # time, azimuth deg (0 = front/road side), polar deg (0 = down), distance, target x, target z
    (0.0, 90, 2, 62, 0, 0),
    (2.0, 88, 8, 58, 0, 0),
    (5.0, 70, 40, 52, -3, 1),
    (8.5, 62, 62, 62, -2, 2),
    (11.5, 56, 75, 60, 12, 2.5),
]


def set_frame(f):
    t = f / H.FPS
    for i, pairs in enumerate(lots):
        _base(f - DELAY[i] * H.FPS)
        off = OFFS[i]
        for o, c in pairs:
            loc = o.location.copy()
            if c.parent is None and c is not o:
                loc.x += off
                if o.name.startswith("lawn"):
                    loc.z += 0.002 * i
            c.location = loc
            c.scale = o.scale
            c.hide_render = o.hide_render
    _base(f - DELAY[CENTER] * H.FPS)           # leave the originals on their own timing
    R.plan_mix.inputs["Factor"].default_value = H.ease((t - 5.0 - DELAY[-1]) / 1.5)
    # camera
    for j in range(len(CAM) - 1):
        if CAM[j][0] <= t <= CAM[j + 1][0] or j == len(CAM) - 2:
            a, b = CAM[j], CAM[j + 1]
            kk = H.ease_io(H.clamp((t - a[0]) / (b[0] - a[0])))
            break
    az = math.radians(lerp(a[1], b[1], kk))
    po = math.radians(lerp(a[2], b[2], kk))
    d = lerp(a[3], b[3], kk)
    tx = lerp(a[4], b[4], kk)
    tz = lerp(a[5], b[5], kk)
    H.target.location = (tx, -2.0, tz)
    H.cam.location = (tx + d * math.sin(po) * math.sin(az), -2.0 - d * math.sin(po) * math.cos(az),
                      tz + d * math.cos(po))


H.set_frame = set_frame

if __name__ == "__main__":
    if "--samples" not in sys.argv:
        sys.argv += ["--samples", "16"]
    H.main()
