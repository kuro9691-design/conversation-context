# 点と線の人物 — Blender試作

このフォルダは、人物動画を **6fps の発光する点と線のアニメーション** にするための試作です。

## できること

1. `extract_pose.py` が動画から頭・肩・肘・手首・腰・膝・足首の位置を読み取り、`pose_6fps.json` を作る。
2. Blender で `build_skeleton.py` を実行すると、点と線の人物、黒背景、発光、6fpsのレンダー設定を作る。

## 一度だけ準備

Python に次を入れます。

```powershell
py -m pip install mediapipe opencv-python
```

## 実行

素材動画へのパスを指定します。

```powershell
py extract_pose.py "C:\Users\user\Pictures\Screenshots\レコーディング 2026-09-08 225942.mp4"
```

完了後、Blender を開いて「Scripting」画面から `build_skeleton.py` を開き、Run Script を押します。

完成したシーンは `skeleton_motion.blend` としてこのフォルダに保存され、レンダーは `render/` に連番PNGで出力されます。

## 見た目の調整

`build_skeleton.py` 冒頭の `STYLE` で色、線の太さ、点の大きさを変更できます。フレーム補間は `CONSTANT` なので、6fpsのカクカクした動きになります。
