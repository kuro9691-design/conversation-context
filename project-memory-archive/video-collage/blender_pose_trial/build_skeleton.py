"""Build a low-FPS glowing point-and-line person in Blender.

Open this file in Blender's Scripting workspace and click Run Script.
Run extract_pose.py first so pose_6fps.json exists next to this file.
"""
from __future__ import annotations

import json
from pathlib import Path

import bpy

STYLE = {
    "point_size": 0.12,
    "line_width": 0.034,
    "glow_color": (0.25, 0.95, 1.0, 1.0),
    "strength": 8.0,
    "camera_scale": 10.0,
}
CONNECTIONS = (
    ("head", "left_shoulder"), ("head", "right_shoulder"),
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
)


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "pose_6fps.json"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.curves, bpy.data.meshes, bpy.data.materials):
        for block in datablocks:
            if block.users == 0:
                datablocks.remove(block)


def glow_material():
    material = bpy.data.materials.new("Skeleton Glow")
    material.use_nodes = True
    emission = material.node_tree.nodes.get("Principled BSDF")
    emission.inputs["Base Color"].default_value = STYLE["glow_color"]
    emission.inputs["Emission Color"].default_value = STYLE["glow_color"]
    emission.inputs["Emission Strength"].default_value = STYLE["strength"]
    return material


def to_world(joint):
    # MediaPipe uses normalized image coordinates with y down; Blender y is up.
    return ((joint["x"] - 0.5) * 7.0, (0.5 - joint["y"]) * 9.0, 0.0)


def set_constant_interpolation(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return
    for fcurve in obj.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "CONSTANT"


def make_joint(name, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=STYLE["point_size"])
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def make_line(name, material):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = STYLE["line_width"]
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    curve.materials.append(material)
    return obj


def add_camera():
    bpy.ops.object.camera_add(location=(0, 0, 10))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = STYLE["camera_scale"]
    bpy.context.scene.camera = camera


def configure_scene(fps, total_frames):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 50
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(ROOT / "render" / "skeleton_")
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.world.color = (0, 0, 0)
    scene.render.film_transparent = False
    # Eevee bloom is unavailable in recent Blender releases; compositor glare is stable.
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    render = tree.nodes.new("CompositorNodeRLayers")
    glare = tree.nodes.new("CompositorNodeGlare")
    glare.glare_type = "FOG_GLOW"
    glare.quality = "HIGH"
    glare.threshold = 0.2
    glare.size = 7
    composite = tree.nodes.new("CompositorNodeComposite")
    tree.links.new(render.outputs["Image"], glare.inputs["Image"])
    tree.links.new(glare.outputs["Image"], composite.inputs["Image"])


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"{DATA_PATH.name} がありません。先に extract_pose.py を実行してください。")
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    frames = data["frames"]
    if not any(frames):
        raise RuntimeError("人物を検出できたフレームがありません。人物が大きく映る動画を使ってください。")

    clear_scene()
    material = glow_material()
    configure_scene(data["fps"], len(frames))
    add_camera()
    joints = {name: make_joint(name, material) for name in frames[0] or next(frame for frame in frames if frame)}
    lines = {pair: make_line(f"{pair[0]}__{pair[1]}", material) for pair in CONNECTIONS}

    last_known = {}
    for frame_no, pose in enumerate(frames, start=1):
        if pose:
            last_known.update(pose)
        for name, obj in joints.items():
            if name not in last_known:
                obj.hide_render = True
                continue
            obj.hide_render = False
            obj.location = to_world(last_known[name])
            obj.keyframe_insert(data_path="location", frame=frame_no)
        for (a, b), line in lines.items():
            if a not in last_known or b not in last_known:
                line.hide_render = True
                continue
            line.hide_render = False
            points = line.data.splines[0].points
            points[0].co = (*to_world(last_known[a]), 1.0)
            points[1].co = (*to_world(last_known[b]), 1.0)
            points[0].keyframe_insert(data_path="co", frame=frame_no)
            points[1].keyframe_insert(data_path="co", frame=frame_no)

    for obj in [*joints.values(), *lines.values()]:
        set_constant_interpolation(obj)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "skeleton_motion.blend"))
    print("Created skeleton_motion.blend")


main()
