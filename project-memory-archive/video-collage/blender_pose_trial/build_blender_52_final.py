"""Build the 6fps point-and-line animation in Blender 5.2."""
from pathlib import Path
import json
import bpy

ROOT = Path(__file__).resolve().parent
frames = json.loads((ROOT / "pose_6fps.json").read_text(encoding="utf-8"))["frames"]
FPS = 6
COLOR = (0.25, 0.95, 1.0, 1.0)
EDGES = (("head","left_shoulder"),("head","right_shoulder"),("left_shoulder","right_shoulder"),
         ("left_shoulder","left_elbow"),("left_elbow","left_wrist"),("right_shoulder","right_elbow"),("right_elbow","right_wrist"),
         ("left_shoulder","left_hip"),("right_shoulder","right_hip"),("left_hip","right_hip"),
         ("left_hip","left_knee"),("left_knee","left_ankle"),("right_hip","right_knee"),("right_knee","right_ankle"))

def pos(point): return ((point["x"] - .5) * 7, (.5 - point["y"]) * 9, 0)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
mat = bpy.data.materials.new("Cyan glow")
mat.use_nodes = True
n, l = mat.node_tree.nodes, mat.node_tree.links
for item in list(n): n.remove(item)
out, emission = n.new("ShaderNodeOutputMaterial"), n.new("ShaderNodeEmission")
emission.inputs["Color"].default_value, emission.inputs["Strength"].default_value = COLOR, 12
l.new(emission.outputs["Emission"], out.inputs["Surface"])

first_pose = next(frame for frame in frames if frame)
joints = {}
for name in first_pose:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=.12)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    joints[name] = obj
lines = {}
for a, b in EDGES:
    curve = bpy.data.curves.new(f"{a}_{b}", "CURVE")
    curve.dimensions, curve.bevel_depth, curve.bevel_resolution = "3D", .034, 3
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    curve.materials.append(mat)
    obj = bpy.data.objects.new(curve.name, curve)
    bpy.context.collection.objects.link(obj)
    lines[a, b] = obj

latest = {}
for frame_no, pose in enumerate(frames, 1):
    if pose: latest.update(pose)
    for name, obj in joints.items():
        if name in latest:
            obj.location = pos(latest[name])
            obj.keyframe_insert(data_path="location", frame=frame_no)
    for (a, b), obj in lines.items():
        if a in latest and b in latest:
            points = obj.data.splines[0].points
            points[0].co, points[1].co = (*pos(latest[a]), 1), (*pos(latest[b]), 1)
            points[0].keyframe_insert(data_path="co", frame=frame_no)
            points[1].keyframe_insert(data_path="co", frame=frame_no)

bpy.ops.object.camera_add(location=(0, 0, 10))
cam = bpy.context.object
cam.data.type, cam.data.ortho_scale = "ORTHO", 10
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1080, 1920, 50
scene.render.fps, scene.frame_start, scene.frame_end = FPS, 1, len(frames)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "render" / "skeleton_")
scene.world.color = (0, 0, 0)
scene.use_nodes = True
tree = scene.node_tree
tree.nodes.clear()
render, glare, comp = tree.nodes.new("CompositorNodeRLayers"), tree.nodes.new("CompositorNodeGlare"), tree.nodes.new("CompositorNodeComposite")
glare.glare_type, glare.threshold, glare.size = "FOG_GLOW", .2, 7
tree.links.new(render.outputs["Image"], glare.inputs["Image"])
tree.links.new(glare.outputs["Image"], comp.inputs["Image"])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "skeleton_motion.blend"))
print("Created", ROOT / "skeleton_motion.blend")
