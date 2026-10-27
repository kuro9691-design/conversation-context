#!/usr/bin/env python3
"""
BUNK Midjourney プロンプト自動生成スクリプト

Vol.1で確定した「9ショットの型・カメラ言語・共通スタイルブロック・表紙フォーマット」を
そのまま引き継ぎ、新しい巻の被写体（scenes）とタイトルだけ差し替えて .md を生成する。

固定要素（絶対に変更しない）:
  - 9つの役割ごとのカメラ・ショット言語（ROLES の "shot"）
  - 共通スタイルブロック（STYLE_BLOCK）
  - 表紙のレイアウト構造（BUNK上・タイトル中央・VOL右下、コラージュ手法）

可変要素（巻ごとに変える）:
  - volume（巻数）
  - title_jp / title_en（タイトル）
  - scenes（9つの被写体descriptions、英語）
  - cover_scene（表紙の場面描写、英語）

使い方:
  1. config_volN.json を用意する（config_example.json を複製して書き換え）
  2. python generate_bunk_prompts.py config_volN.json
  3. 同じフォルダに BUNK_volN_<slug>_prompts.md が出力される
"""

import json
import re
import sys
from pathlib import Path

ROLES = [
    {"scene_label": "街並み",       "role_jp": "舞台提示",
     "shot": "cinematic establishing wide shot, elevated camera, deep focus"},
    {"scene_label": "外観",         "role_jp": "店の前に立つ",
     "shot": "cinematic medium wide shot, slightly low camera looking toward the entrance"},
    {"scene_label": "起源のもの",    "role_jp": "起源／始まりの物",
     "shot": "cinematic insert close-up, shallow depth of field"},
    {"scene_label": "室内",         "role_jp": "入店。本題",
     "shot": "cinematic wide shot from the doorway, symmetrical one-point perspective, eye-level camera"},
    {"scene_label": "象徴的な物",    "role_jp": "「発明」のポイント",
     "shot": "cinematic extreme close-up insert shot, shallow depth of field"},
    {"scene_label": "現場",         "role_jp": "現場に入る",
     "shot": "cinematic handheld medium shot, tight framing in a narrow space, shallow depth of field"},
    {"scene_label": "人物",         "role_jp": "一人に寄る",
     "shot": "cinematic medium close-up, shallow depth of field, slightly tilted camera"},
    {"scene_label": "クライマックス", "role_jp": "混沌のピーク",
     "shot": "cinematic wide tracking shot from within the room, low camera height, motion in the foreground"},
    {"scene_label": "明け方の無人",  "role_jp": "エピローグ／オチ",
     "shot": "cinematic static wide shot, eye-level camera, soft light from the windows"},
]

STYLE_BLOCK = (
    "1970s underground comix pen-and-ink illustration, dense crosshatching and stippling, "
    "thick uneven hand-inked outlines, limited two-color riso palette of oxidized red and "
    "off-black, visible halftone dots, aged newsprint texture with ink smudges and misregistration"
)

COVER_TEMPLATE = (
    'vintage magazine cover, torn paper collage layout, cut-out lettering pasted at slight angles, '
    'ragged edges and visible paste marks, the word "BUNK" in huge ransom-note cut-out letters '
    'across the top, the title "{title_en}" in pasted cut-out letters across the middle, '
    '"VOL {volume}" in small cut-out letters in the bottom right corner, {cover_scene}, '
    'portrait poster composition, large flat areas of a single colour behind the pasted elements, '
    'uncluttered layout, three or four colours only'
)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "untitled"


def build_md(cfg: dict) -> str:
    volume = cfg["volume"]
    title_jp = cfg["title_jp"]
    title_en = cfg["title_en"]
    scenes = cfg["scenes"]
    cover_scene = cfg["cover_scene"]

    if len(scenes) != 9:
        raise ValueError(f"scenes は9個必要です（{len(scenes)}個でした）")

    lines = []
    lines.append(f"# BUNK Vol.{volume} — {title_jp}｜Midjourney 表紙＋本編9枚\n")
    lines.append(
        "Web版（midjourney.com/imagine）用。`/imagine` 不要、`--ar` `--v` 不要（デフォルト設定に任せる）。\n"
        "被写体＋時代＋映画的ショット＋画風のみ。人物の顔・人数・動作はムードボード側に任せる。\n"
    )
    lines.append("## 本編9枚【Vol.1のショット構成・カメラ言語を継承／変更禁止】\n")
    lines.append("| # | シーン | ショット | 役割 |")
    lines.append("|---|---|---|---|")
    for i, r in enumerate(ROLES, 1):
        lines.append(f"| {i} | {r['scene_label']} | {r['shot'].split(',')[0].strip()} | {r['role_jp']} |")
    lines.append("")
    lines.append(
        "インサート（3・5）は物だけのカット。顔が破綻せず、人物カットの間の息継ぎになる。"
        "最後（9）を無人で締めると9枚が1本の映画として閉じる。\n"
    )
    lines.append("### 共通スタイルブロック\n")
    lines.append("```")
    lines.append(STYLE_BLOCK)
    lines.append("```\n")
    lines.append("---\n")

    for i, (r, subject) in enumerate(zip(ROLES, scenes), 1):
        lines.append(f"## {i}. {r['scene_label']}\n")
        lines.append("```")
        lines.append(f"{subject}, {r['shot']}, {STYLE_BLOCK}")
        lines.append("```\n")

    lines.append("---\n")
    lines.append("## 表紙【Vol.1の確定フォーマットを継承】\n")
    lines.append(
        "本編9枚と同じくムードボードを効かせたまま生成する。"
        "ムードボードが版画の絵柄を担保し、プロンプト側は文字レイアウトとシーンだけを指定する。\n"
    )
    lines.append("```")
    lines.append(COVER_TEMPLATE.format(title_en=title_en, volume=volume, cover_scene=cover_scene))
    lines.append("```\n")
    lines.append("---\n")
    lines.append(
        "真下からの見上げや極端なダッチアングルはAIが破綻しやすい。寄り引き（wide / medium / close-up）とカメラの高さで差をつける。\n"
    )
    lines.append("この設計はスキル `bunk-midjourney-prompts` として保存済み。ROLES/STYLE_BLOCK/表紙フォーマットはVol.1から自動継承（このファイルは generate_bunk_prompts.py で生成）。")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("使い方: python generate_bunk_prompts.py config_volN.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    md = build_md(cfg)

    slug = slugify(cfg["title_en"])
    out_path = config_path.parent / f"BUNK_vol{cfg['volume']}_{slug}_prompts.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"生成完了: {out_path}")


if __name__ == "__main__":
    main()
