"""Compatibility runner for Blender 5.2, which uses a changed compositor API."""
from pathlib import Path

source_path = Path(__file__).with_name("build_blender_52_final.py")
source = source_path.read_text(encoding="utf-8").replace("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE")
source = source.split("scene.use_nodes = True", 1)[0]
source += "\nbpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'skeleton_motion.blend'))\nprint('Created', ROOT / 'skeleton_motion.blend')\n"
exec(compile(source, str(source_path), "exec"))
