"""Blender 5.2 scene builder for pose_6fps.json."""
from pathlib import Path
import json
import bpy

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "pose_6fps.json").read_text(encoding="utf-8"))
EDGES = (("head","left_shoulder"),("head","right_shoulder"),("left_shoulder","right_shoulder"),
         ("left_shoulder","left_elbow"),("left_elbow","left_wrist"),
         ("right_shoulder","right_elbow"),("right_elbow","right_wrist"),
         ("left_shoulder","left_hip"),("right_shoulder","right_hip"),("left_hip","right_hip"),
         ("left_hip","left_knee"),("left_knee","left_ankle"),("right_hip","right_knee"),("right_knee","right_ankle"))
COLOR = (0.25, 0.95, 1.0, 1.0)

def world(p): return ((p["x"] - .5) * 7, (.5 - p["y"]) * 9, 0)
def constant(idblock):
    ad = idblock.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for key in fc.keyframe_points: key.interpolation = "CONSTANT"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
mat = bpy.data.materials.new("Cyan emission")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
for node in list(nodes): nodes.remove(node)
out = nodes.new("ShaderNodeOutputMaterial")
emit = nodes.new("ShaderNodeEmission")
emit.inputs["Color"].default_value = COLOR
emit.inputs["Strength"].default_value = 12
links.new(emit.outputs["Emission"], out.inputs["Surface"])

frames = DATA["frames"]
template = next(f for f in frames if f)
joints = {}
for name in template:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=.12)
    joint = bpy.context.object
    joint.name = name
    joint.data.materials.append(mat)
    joints[name] = joint

lines = {}
for a, b in EDGES:
    curve = bpy.data.curves.new(a + "_to_" + b, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = .034
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    curve.materials.append(mat)
    obj = bpy.data.objects.new(curve.name, curve)
    bpy.context.collection.objects.link(obj)
    lines[a, b] = obj

last = {}
for number, pose in enumerate(frames, 1):
    if pose: last.update(pose)
    for name, obj in joints.items():
        if name in last:
            obj.location = world(last[name])
            obj.keyframe_insert(data_path="location", frame=number)
    for (a, b), obj in lines.items():
        if a in last and b in last:
            points = obj.data.splines[0].points
            points[0].co = (*world(last[a]), 1)
            points[1].co = (*world(last[b]), 1)
            points[0].keyframe_insert(data_path="co", frame=number)
            points[1].keyframe_insert(data_path="co", frame=number)

for obj in joints.values(): constant(obj)
for obj in lines.values(): constant(obj.data)

bpy.ops.object.camera_add(location=(0, 0, 10))
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 10
bpy.context.scene.camera = camera
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y = 1080, 1920
scene.render.resolution_percentage = 50
scene.render.fps = DATA["fps"]
scene.frame_start, scene.frame_end = 1, len(frames)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "render" / "skeleton_")
scene.world.color = (0, 0, 0)
scene.use_nodes = True
tree = scene.node_tree
tree.nodes.clear()
rl = tree.nodes.new("CompositorNodeRLayers")
glare = tree.nodes.new("CompositorNodeGlare")
glare.glare_type, glare.threshold, glare.size = "FOG_GLOW", .2, 7
comp = tree.nodes.new("CompositorNodeComposite")
tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
tree.links.new(glare.outputs["Image"], comp.inputs["Image"])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "skeleton_motion.blend"))
print("Created:", ROOT / "skeleton_motion.blend")
