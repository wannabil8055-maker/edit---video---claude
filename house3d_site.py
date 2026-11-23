"""The five-lot estate rendered into the real site photo (assets/tapak_sebenar/site1.jpg).

Camera matched to the photo by hand (phone main camera, eye height, road vanishing point);
the ground is a shadow catcher and the film is transparent, so each still is laid over the
photo. Overcast, shadowless sky to match the day the photo was taken.

Usage: python3 house3d_site.py OUT_DIR [--res W] [--samples N] [--stage slab|walls|done|all]
Writes OUT_DIR/site_<stage>.png (RGBA, the photo's aspect).
"""
import math
import os
import sys

import bpy

import house3d as H
import house3d_lots as LOTS

scene = H.scene
col = H.col

# ---------------------------------------------------------------- strip what the photo already has
for o in list(col.objects):
    if o.name.split(".")[0] in ("road", "dash", "kerb", "far_tree"):
        bpy.data.objects.remove(o, do_unlink=True)
ground = [o for o in col.objects if o.name == "ground"][0]
# no side boundary walls: from eye level the first one is a long blank wall across the view
# (hidden after every set_frame, which would otherwise show them again)
SIDE_WALLS = [o for o in col.objects if o.name.split(".")[0] in ("bwall", "bcap") and o.dimensions.y > 20]
# driveways stop at the plot front instead of running out over the real road
for o in col.objects:
    if o.name.split(".")[0] == "drive":
        y1 = o.location.y + o.dimensions.y / 2          # back end, near the house
        y0 = float(__import__("os").environ.get("SITE_FRONT", "-17.5"))
        o.scale.y = (y1 - y0) / o.dimensions.y * o.scale.y
        o.location.y = (y0 + y1) / 2
ground.is_shadow_catcher = True
scene.render.film_transparent = True

# ---------------------------------------------------------------- overcast sky
world = scene.world
wn = world.node_tree
wn.nodes.clear()
out = wn.nodes.new("ShaderNodeOutputWorld")
bg = wn.nodes.new("ShaderNodeBackground")
grad = wn.nodes.new("ShaderNodeTexGradient")
tc = wn.nodes.new("ShaderNodeTexCoord")
sep = wn.nodes.new("ShaderNodeSeparateXYZ")
ramp = wn.nodes.new("ShaderNodeValToRGB")
wn.links.new(tc.outputs["Generated"], sep.inputs[0])
wn.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
ramp.color_ramp.elements[0].position = 0.45
ramp.color_ramp.elements[0].color = (0.32, 0.34, 0.3, 1)      # below horizon: wet grass bounce
ramp.color_ramp.elements[1].position = 0.75
ramp.color_ramp.elements[1].color = (0.78, 0.82, 0.88, 1)     # grey cloud cover overhead
wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.6
wn.links.new(bg.outputs[0], out.inputs[0])
H.sun.hide_render = True

# ---------------------------------------------------------------- camera matched to site1.jpg
PHOTO_W, PHOTO_H = 4000, 2252
cam = H.cam
for c in list(cam.constraints):
    cam.constraints.remove(c)
cam.data.sensor_fit = "HORIZONTAL"
cam.data.sensor_width = 36.0
cam.data.lens = float(os.environ.get("SITE_LENS", "24"))
cam.data.dof.use_dof = False
CAM_H = float(os.environ.get("SITE_CAMH", "1.55"))
PITCH = float(os.environ.get("SITE_PITCH", "1.0"))      # degrees up
cam.location = (0, 0, CAM_H)
cam.rotation_euler = (math.radians(90 + PITCH), 0, 0)    # looking along +Y

# road in the photo: heads YAW degrees right of the view axis; its left edge passes (LX, LY)
YAW = math.radians(float(os.environ.get("SITE_YAW", "21")))
LX, LY = float(os.environ.get("SITE_LX", "-3.4")), float(os.environ.get("SITE_LY", "9.3"))
S0 = float(os.environ.get("SITE_S0", "60"))              # how far up the road the estate centre sits
u = (math.sin(YAW), math.cos(YAW))                        # along the road, away from the camera
n = (u[1], -u[0])                                         # to the right of the road
# estate frame: +x along the road, +y away from the road (to its left)
KERB = float(os.environ.get("SITE_FRONT", "-17.5"))     # estate y that sits on the road edge
ox = LX + u[0] * S0 - n[0] * (-KERB) * 1.0
oy = LY + u[1] * S0 - n[1] * (-KERB) * 1.0
# leave the estate where it is and move the camera into its frame instead
# (house3d_lots offsets each lot's root objects, so they must stay unparented)
from mathutils import Matrix
RIG = Matrix.Translation((ox, oy, 0)) @ Matrix.Rotation(math.atan2(u[1], u[0]), 4, "Z")
CAM_M = RIG.inverted() @ (Matrix.Translation((0, 0, CAM_H)) @ Matrix.Rotation(math.radians(90 + PITCH), 4, "X"))


def place_camera():
    cam.matrix_world = CAM_M


place_camera()

LOTS.DELAY[:] = [0.0] * len(LOTS.DELAY)
STAGES = {"slab": 1.6, "walls": 6.3, "done": 11.4}


def show(stage):
    f = int(STAGES[stage] * H.FPS)
    LOTS.set_frame(f)
    scene.frame_set(f)
    for o in SIDE_WALLS:
        o.hide_render = True
    place_camera()                   # LOTS.set_frame moves the camera: put it back on the photo's


def main():
    outd = sys.argv[1]
    os.makedirs(outd, exist_ok=True)
    res = int(sys.argv[sys.argv.index("--res") + 1]) if "--res" in sys.argv else 1000
    samples = int(sys.argv[sys.argv.index("--samples") + 1]) if "--samples" in sys.argv else 32
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "done"
    scene.render.resolution_x = res
    scene.render.resolution_y = round(res * PHOTO_H / PHOTO_W)
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    scene.render.use_persistent_data = False
    scene.render.image_settings.color_mode = "RGBA"
    for st in (STAGES if stage == "all" else [stage]):
        show(st)
        scene.render.filepath = os.path.join(outd, f"site_{st}.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", scene.render.filepath, flush=True)


if __name__ == "__main__":
    main()
