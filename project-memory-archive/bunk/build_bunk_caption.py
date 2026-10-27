#!/usr/bin/env python3
"""
BUNK キャプション文字数チェック＋組み立てスクリプト

自動化するのは「文字数チェック」と「コピペ用の最終形に組み立てる」ことだけ。
本文（PITCH→TRUTH→FACT→PUNCHLINE）の文章そのものは人が書く。

組み立てルール（Vol.1実測で検証済み）:
  完成キャプション = 日本語本文 + "\n\n---\n\n" + 英語本文 + "\n\n" + ハッシュタグ
  区切り "\n\n---\n\n" は7文字固定。

Vol.3以降の文字数ルール:
  日本語 ≤ 650字
  英語   ≤ 1350字
  ハッシュタグ = 94字固定（11個）
  目標合計 ≤ 2100字（Instagram上限2,200字に対して100字のバッファ）
"""

import json
import sys
from pathlib import Path

SEPARATOR = "\n\n---\n\n"
HASHTAGS_DEFAULT = "#foodhistory #zine #zinester #zinefest #cutandpasteart #outsiderart #ゲルプリント #ジン #ミニコミ #広島 #世界史"

JP_LIMIT = 650
EN_LIMIT = 1350
HASHTAG_LIMIT = 94
TARGET_TOTAL = 2100
HARD_LIMIT = 2200


def build_caption(cfg: dict) -> dict:
    jp_body = cfg["jp_body"].strip("\n")
    en_body = cfg["en_body"].strip("\n")

    hashtags = cfg.get("hashtags", HASHTAGS_DEFAULT)
    category_hashtag = cfg.get("category_hashtag")
    if category_hashtag:
        tags = hashtags.split(" ")
        tags[0] = category_hashtag
        hashtags = " ".join(tags)

    full = jp_body + SEPARATOR + en_body + "\n\n" + hashtags

    jp_len = len(jp_body)
    en_len = len(en_body)
    sep_len = len(SEPARATOR)
    hashtag_len = len(hashtags)
    total_len = len(full)

    warnings = []
    if jp_len > JP_LIMIT:
        warnings.append(f"日本語が上限超過: {jp_len}字 / 上限{JP_LIMIT}字（{jp_len - JP_LIMIT}字オーバー）")
    if en_len > EN_LIMIT:
        warnings.append(f"英語が上限超過: {en_len}字 / 上限{EN_LIMIT}字（{en_len - EN_LIMIT}字オーバー）→ FACT部分を削る")
    if hashtag_len != HASHTAG_LIMIT:
        warnings.append(f"ハッシュタグが規定と異なる: {hashtag_len}字（規定{HASHTAG_LIMIT}字・11個固定）")
    if total_len > HARD_LIMIT:
        warnings.append(f"【危険】Instagram上限2,200字を超過: {total_len}字")
    elif total_len > TARGET_TOTAL:
        warnings.append(f"目標合計{TARGET_TOTAL}字を超過（上限2,200字にはまだ余裕あり）: {total_len}字")

    return {
        "full": full,
        "jp_len": jp_len,
        "en_len": en_len,
        "sep_len": sep_len,
        "hashtag_len": hashtag_len,
        "total_len": total_len,
        "warnings": warnings,
    }


def main():
    if len(sys.argv) != 2:
        print("使い方: python build_bunk_caption.py config_caption.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    result = build_caption(cfg)

    print(f"日本語　: {result['jp_len']}字 / 上限{JP_LIMIT}字")
    print(f"英語　　: {result['en_len']}字 / 上限{EN_LIMIT}字")
    print(f"区切り　: {result['sep_len']}字")
    print(f"ハッシュタグ: {result['hashtag_len']}字")
    print(f"合計　　: {result['total_len']}字 / 目標{TARGET_TOTAL}字 / 上限{HARD_LIMIT}字")
    print()

    if result["warnings"]:
        print("【警告】")
        for w in result["warnings"]:
            print(f"- {w}")
    else:
        print("文字数OK。このまま使える。")

    out_path = config_path.parent / (config_path.stem.replace("config_", "") + "_caption.txt")
    out_path.write_text(result["full"], encoding="utf-8")
    print(f"\n完成キャプションを書き出し: {out_path}")


if __name__ == "__main__":
    main()
