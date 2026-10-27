"""MediaPipe Tasks edition: extract a video pose at 6 frames per second.

Usage:
  py extract_pose_tasks.py "C:\\path\\to\\video.mp4" pose_landmarker_heavy.task
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

FPS = 6
JOINTS = {
    "head": 0,
    "left_shoulder": 11, "right_shoulder": 12,
    "left_elbow": 13, "right_elbow": 14,
    "left_wrist": 15, "right_wrist": 16,
    "left_hip": 23, "right_hip": 24,
    "left_knee": 25, "right_knee": 26,
    "left_ankle": 27, "right_ankle": 28,
}


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("動画ファイルと pose_landmarker_heavy.task を指定してください。")
    video, model = map(lambda x: Path(x).resolve(), sys.argv[1:])
    capture = cv2.VideoCapture(str(video))
    source_fps = capture.get(cv2.CAP_PROP_FPS)
    if source_fps <= 0:
        raise SystemExit("動画のフレームレートを取得できませんでした。")
    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    frame_number = 0
    next_sample = 0.0
    frames = []
    detector = vision.PoseLandmarker.create_from_options(options)
    try:
        while True:
            ok, bgr = capture.read()
            if not ok:
                break
            if frame_number + 0.001 < next_sample:
                frame_number += 1
                continue
            next_sample += source_fps / FPS
            frame_number += 1
            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB),
            )
            result = detector.detect_for_video(image, round((frame_number - 1) / source_fps * 1000))
            pose = {}
            if result.pose_landmarks:
                for name, index in JOINTS.items():
                    landmark = result.pose_landmarks[0][index]
                    pose[name] = {"x": round(landmark.x, 6), "y": round(landmark.y, 6), "visibility": round(landmark.visibility, 6)}
            frames.append(pose)
    finally:
        detector.close()
        capture.release()
    output = Path(__file__).with_name("pose_6fps.json")
    output.write_text(json.dumps({"fps": FPS, "frames": frames}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{output}: {len(frames)} frames, {sum(bool(x) for x in frames)} detected")


if __name__ == "__main__":
    main()
