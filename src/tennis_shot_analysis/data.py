import math
from pathlib import Path

import numpy as np
import pandas as pd

POSE_LANDMARK_IDS = {
    "wrist": 16,
    "shoulder": 12,
    "hip": 24,
}


def generate_synthetic_landmarks(frame_count: int = 80, duration_s: float = 1.6) -> pd.DataFrame:
    """Generate a reproducible forehand-like landmark sequence for public demos."""
    time_seconds = np.linspace(0.0, duration_s, frame_count)

    hip_x = np.full(frame_count, 0.50)
    hip_y = np.full(frame_count, 0.78)
    shoulder_x = 0.50 + 0.03 * np.sin(time_seconds * math.pi)
    shoulder_y = np.full(frame_count, 0.42)

    phase = np.linspace(-1.2, 1.2, frame_count)
    wrist_x = 0.30 + 0.42 / (1.0 + np.exp(-5.0 * phase))
    wrist_y = 0.63 - 0.18 * np.exp(-(phase ** 2) * 3.5) + 0.02 * np.sin(time_seconds * 10.0)

    return pd.DataFrame(
        {
            "frame": np.arange(frame_count),
            "time_s": time_seconds,
            "hip_x": hip_x,
            "hip_y": hip_y,
            "shoulder_x": shoulder_x,
            "shoulder_y": shoulder_y,
            "wrist_x": wrist_x,
            "wrist_y": wrist_y,
        }
    )


def extract_blazepose_landmarks(
    video_path: Path,
    min_visibility: float = 0.5,
    max_frames: int | None = None,
) -> pd.DataFrame:
    """Extract selected body landmarks from a local video using MediaPipe BlazePose."""
    try:
        import cv2
    except ImportError as exc:
        raise ImportError("opencv-python is required for video mode.") from exc

    try:
        import mediapipe as mp
    except ImportError as exc:
        raise ImportError("mediapipe is required for video mode.") from exc

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    capture = cv2.VideoCapture(str(video_path))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    rows: list[dict[str, float | int]] = []
    frame_index = 0

    with mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        while True:
            has_frame, frame = capture.read()
            if not has_frame:
                break
            if max_frames is not None and frame_index >= max_frames:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb_frame)

            if result.pose_landmarks is not None:
                landmarks_result = result.pose_landmarks.landmark
                wrist = landmarks_result[POSE_LANDMARK_IDS["wrist"]]
                shoulder = landmarks_result[POSE_LANDMARK_IDS["shoulder"]]
                hip = landmarks_result[POSE_LANDMARK_IDS["hip"]]

                visibility_values = [
                    getattr(wrist, "visibility", 1.0),
                    getattr(shoulder, "visibility", 1.0),
                    getattr(hip, "visibility", 1.0),
                ]
                if min(visibility_values) >= min_visibility:
                    rows.append(
                        {
                            "frame": frame_index,
                            "time_s": frame_index / fps,
                            "hip_x": hip.x,
                            "hip_y": hip.y,
                            "shoulder_x": shoulder.x,
                            "shoulder_y": shoulder.y,
                            "wrist_x": wrist.x,
                            "wrist_y": wrist.y,
                        }
                    )

            frame_index += 1

    capture.release()

    if not rows:
        raise ValueError(
            "No valid pose frames were extracted. Try a clearer clip, lower min_visibility, or verify the video path."
        )

    return pd.DataFrame(rows)
