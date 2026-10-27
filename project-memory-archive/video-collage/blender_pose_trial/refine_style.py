"""Create a slimmer, cyan version of the generated skeleton scene."""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "skeleton_motion.blend"
OUTPUT = ROOT / "skeleton_motion_refined.blend"

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))

for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        obj.scale = (0.55, 0.55, 0.55)
    elif obj.type == "CURVE":
        obj.data.bevel_depth = 0.018

for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    for node in material.node_tree.nodes:
        if node.type == "EMISSION":
            node.inputs["Color"].default_value = (0.02, 0.70, 1.0, 1.0)
            node.inputs["Strength"].default_value = 1.5

world = bpy.context.scene.world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
background.inputs["Strength"].default_value = 0.0

camera = bpy.context.scene.camera
camera.data.ortho_scale = 7.6
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
print("Created", OUTPUT)
