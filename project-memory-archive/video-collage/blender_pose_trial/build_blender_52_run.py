"""Run the Blender 5.2 builder with the renderer enum used by this installation."""
from pathlib import Path

source_path = Path(__file__).with_name("build_blender_52_final.py")
source = source_path.read_text(encoding="utf-8").replace("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE")
exec(compile(source, str(source_path), "exec"))
