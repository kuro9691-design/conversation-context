"""Extract a person's pose from a video at a deliberately low frame rate.

Usage:
    py extract_pose.py "C:\path\to\source.mp4"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp

TARGET_FPS = 6
LANDMARKS = {
    "head": 0,
    "left_shoulder": 11, "right_shoulder": 12,
    "left_elbow": 13, "right_elbow": 14,
    "left_wrist": 15, "right_wrist": 16,
    "left_hip": 23, "right_hip": 24,
    "left_knee": 25, "right_knee": 26,
    "left_ankle": 27, "right_ankle": 28,
}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("動画ファイルを1つ指定してください。")
    video_path = Path(sys.argv[1]).expanduser().resolve()
    if not video_path.is_file():
        raise SystemExit(f"動画が見つかりません: {video_path}")

    capture = cv2.VideoCapture(str(video_path))
    source_fps = capture.get(cv2.CAP_PROP_FPS)
    if source_fps <= 0:
        raise SystemExit("動画のフレームレートを取得できませんでした。")
    interval = source_fps / TARGET_FPS
    frame_index = 0
    next_sample = 0.0
    frames = []

    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_index + 0.001 < next_sample:
                frame_index += 1
                continue
            next_sample += interval
            frame_index += 1

            result = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            joints = {}
            if result.pose_landmarks:
                for name, index in LANDMARKS.items():
                    landmark = result.pose_landmarks.landmark[index]
                    joints[name] = {
                        "x": round(landmark.x, 6),
                        "y": round(landmark.y, 6),
                        "visibility": round(landmark.visibility, 6),
                    }
            frames.append(joints)
    finally:
        pose.close()
        capture.release()

    output = Path(__file__).with_name("pose_6fps.json")
    output.write_text(json.dumps({"fps": TARGET_FPS, "frames": frames}, ensure_ascii=False, indent=2), encoding="utf-8")
    detected = sum(bool(frame) for frame in frames)
    print(f"{output.name}: {len(frames)} frames / {detected} frames with a detected pose")


if __name__ == "__main__":
    main()
