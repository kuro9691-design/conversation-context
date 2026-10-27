#!/usr/bin/env python3
"""
BUNK 画像ファイル整理スクリプト（manifest方式・旧版）

2026年8月以降は generate_bunk_sorter.py（ドラッグ&ドロップ式の専用HTMLツールを
毎回生成する方式）に置き換え済み。こちらは記録として残してあるだけで、
通常はgenerate_bunk_sorter.pyを使う。

Midjourneyでダウンロードした画像（ファイル名がバラバラ）を、
巻数・シーン番号にもとづいた分かりやすい名前にリネームし、
BUNK_volN/ フォルダにまとめてコピーする。
"""

import json
import shutil
import sys
from pathlib import Path

SCENE_SLUGS = {
    0: "cover",
    1: "street",
    2: "exterior",
    3: "origin-object",
    4: "interior",
    5: "symbolic-object",
    6: "workspace",
    7: "person",
    8: "climax",
    9: "dawn-empty",
}


def main():
    if len(sys.argv) != 2:
        print("使い方: python file_bunk_images.py manifest_volN.json")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    cfg = json.loads(manifest_path.read_text(encoding="utf-8"))

    volume = cfg["volume"]
    source_dir = Path(cfg["source_dir"])
    files = cfg["files"]

    out_dir = manifest_path.parent / f"BUNK_vol{volume}"
    out_dir.mkdir(exist_ok=True)

    results = []
    errors = []

    for original_name, scene_num in files.items():
        src = source_dir / original_name
        if not src.exists():
            errors.append(f"見つからない: {src}")
            continue
        if scene_num not in SCENE_SLUGS:
            errors.append(f"不正なシーン番号 {scene_num}（{original_name}）→ 0-9のみ有効")
            continue

        ext = src.suffix
        slug = SCENE_SLUGS[scene_num]
        new_name = f"vol{volume}_{scene_num:02d}_{slug}{ext}"
        dst = out_dir / new_name

        shutil.copy2(src, dst)
        results.append((original_name, new_name))

    print(f"整理先: {out_dir}\n")
    if results:
        print("完了:")
        for orig, new in sorted(results, key=lambda x: x[1]):
            print(f"  {orig}  →  {new}")

    missing = set(SCENE_SLUGS) - {files[k] for k in files if files[k] in SCENE_SLUGS}
    if missing:
        print(f"\n未指定のシーン番号: {sorted(missing)}（表紙含む10枚揃っているか確認）")

    if errors:
        print("\nエラー:")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
