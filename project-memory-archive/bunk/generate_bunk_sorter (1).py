#!/usr/bin/env python3
"""
BUNK 画像振り分けツール自動生成スクリプト

毎回ドロップダウンで並び順を選び直すのは手間・間違いのもとなので、
その回に決めた並び順を config に書いて渡すと、その並び順専用の
振り分けツール（.html）を生成する。生成されたツールはドロップダウン無し、
枠を見て画像をドラッグするだけで正しいファイル名で保存し直される。

表紙（cover）は常に0番目固定。1〜9番目の並び順だけを毎回決める。

使い方:
  1. sorter_config_example.json を複製し、volume と order（9つのスラッグを
     好きな順で並べたリスト）を書く
  2. python generate_bunk_sorter.py sorter_config_volN.json
  3. 同じフォルダに bunk_sorter_volN.html が出力される。それを開いて使う
"""

import json
import sys
from pathlib import Path

# 役割の部品（種類・スラッグは固定。並べる順番だけ回ごとに自由に変える）
ROLES = {
    "cover":           "表紙",
    "street":          "街並み（舞台提示・引き）",
    "exterior":        "外観（対象に近づく）",
    "origin-object":   "起源のもの（インサート・物）",
    "interior":        "室内（本題・ワンポイント）",
    "symbolic-object": "象徴的な物（極寄りインサート）",
    "workspace":       "現場（手持ち風ミディアム）",
    "person":          "人物（一人に寄る）",
    "climax":          "クライマックス（低いワイド）",
    "dawn-empty":      "無人（固定ワイド・締め）",
}

BODY_SLUGS = set(ROLES.keys()) - {"cover"}

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>BUNK Vol.{volume} 画像振り分けツール</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", sans-serif; max-width: 720px; margin: 24px auto; padding: 0 16px; color: #222; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  p.note {{ color: #666; font-size: 13px; line-height: 1.6; }}
  .zone {{ display: flex; align-items: center; gap: 12px; border: 2px dashed #ccc; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; transition: background 0.15s, border-color 0.15s; cursor: pointer; }}
  .zone.dragover {{ background: #eef6ff; border-color: #4a90d9; }}
  .zone.done {{ border-style: solid; border-color: #4caf50; background: #f2fbf2; }}
  .pos {{ font-weight: 600; font-size: 14px; width: 56px; text-align: center; color: #555; flex-shrink: 0; }}
  .thumb {{ width: 44px; height: 44px; object-fit: cover; border-radius: 6px; display: none; border: 1px solid #ddd; flex-shrink: 0; }}
  .label {{ flex: 1; }}
  .label .jp {{ font-size: 14px; font-weight: 500; }}
  .label .fname {{ font-size: 11px; color: #888; font-family: monospace; }}
  .status {{ font-size: 12px; color: #4caf50; display: none; white-space: nowrap; }}
  input[type=file] {{ display: none; }}
  #progress {{ font-size: 13px; color: #666; margin-top: 12px; }}
</style>
</head>
<body>

<h1>BUNK Vol.{volume} 画像振り分けツール</h1>
<p class="note">
  この回用に並び順を固定済みです。選ぶ操作は不要、画像を見て合う枠にドラッグ＆ドロップ（またはタップして選択）するだけです。<br>
  Chromeの設定で「ダウンロード前に保存先を確認する」をオンにしておくと確実です。
</p>

<div id="zones"></div>
<div id="progress">0 / {total} 完了</div>

<script>
const ZONES = {zones_json};
const zonesEl = document.getElementById("zones");
const progressEl = document.getElementById("progress");
let doneCount = 0;

ZONES.forEach((z, i) => {{
  const zone = document.createElement("div");
  zone.className = "zone";
  zone.innerHTML = `
    <div class="pos">${{z.posLabel}}</div>
    <img class="thumb" alt="">
    <div class="label">
      <div class="jp">${{z.jp}}</div>
      <div class="fname">${{z.filename}}</div>
    </div>
    <div class="status">保存済み ✓</div>
    <input type="file" accept="image/*">
  `;
  const fileInput = zone.querySelector('input[type="file"]');
  const thumb = zone.querySelector(".thumb");
  const status = zone.querySelector(".status");

  zone.addEventListener("click", () => fileInput.click());
  zone.addEventListener("dragover", (e) => {{ e.preventDefault(); zone.classList.add("dragover"); }});
  zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
  zone.addEventListener("drop", (e) => {{
    e.preventDefault();
    zone.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0], zone, z, thumb, status);
  }});
  fileInput.addEventListener("change", () => {{
    if (fileInput.files.length) handleFile(fileInput.files[0], zone, z, thumb, status);
  }});
  zonesEl.appendChild(zone);
}});

function handleFile(file, zone, z, thumb, status) {{
  const ext = (file.name.split(".").pop() || "png").toLowerCase();
  const targetName = z.filename.replace(/\\.\\w+$/, "") + "." + ext;

  const url = URL.createObjectURL(file);
  thumb.src = url;
  thumb.style.display = "block";

  const a = document.createElement("a");
  a.href = url;
  a.download = targetName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  if (!zone.classList.contains("done")) {{
    doneCount++;
    zone.classList.add("done");
  }}
  status.style.display = "inline";
  progressEl.textContent = `${{doneCount}} / {total} 完了`;
}}
</script>

</body>
</html>
"""


def main():
    if len(sys.argv) != 2:
        print("使い方: python generate_bunk_sorter.py sorter_config_volN.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    volume = cfg["volume"]
    order = cfg["order"]  # 9つのスラッグを、載せたい順に並べたリスト（表紙は含めない）

    if len(order) != 9:
        raise ValueError(f"order は9個必要です（{len(order)}個でした）")
    if set(order) != BODY_SLUGS:
        missing = BODY_SLUGS - set(order)
        extra = set(order) - BODY_SLUGS
        raise ValueError(f"order の中身が不正です。不足: {missing} 余分: {extra}")

    full_order = ["cover"] + order  # 表紙は常に0番目固定

    zones = []
    for position, slug in enumerate(full_order):
        pos_label = "表紙" if position == 0 else f"{position}枚目"
        # ファイル名は「表紙」ラベルと通し番号だけ。役割スラッグは入れない
        # （役割名まで入れると、間違えて保存したときに同名で上書きされず
        #  別名(1)で残ってしまい紛らわしいため。役割はUI上の日本語ラベルで確認する）
        filename = f"vol{volume}_00_cover.png" if position == 0 else f"vol{volume}_{position:02d}.png"
        zones.append({
            "posLabel": pos_label,
            "jp": ROLES[slug],
            "filename": filename,
        })

    html = TEMPLATE.format(
        volume=volume,
        total=len(full_order),
        zones_json=json.dumps(zones, ensure_ascii=False),
    )

    out_path = config_path.parent / f"bunk_sorter_vol{volume}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"生成完了: {out_path}")
    print("この回の並び順:")
    for position, slug in enumerate(full_order):
        print(f"  {position}: {ROLES[slug]} ({slug})")


if __name__ == "__main__":
    main()
