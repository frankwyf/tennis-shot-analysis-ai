import csv
import math
from collections import Counter
from itertools import chain
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


def load_landmarks_csv(csv_path: Path) -> pd.DataFrame:
    """Load canonical landmark columns from a user-provided CSV file."""
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Landmark CSV file not found: {csv_path}")

    try:
        with csv_path.open(encoding="utf-8-sig", newline="") as source:
            # Match pandas' blank-line handling without losing quoted headers.
            first_line = next((line for line in source if line.strip()), "")
            header = next(csv.reader(chain([first_line], source)), [])
            duplicates = [name for name, count in Counter(header).items() if count > 1]
            if duplicates:
                raise ValueError(f"Landmark CSV header has duplicate columns: {', '.join(duplicates)}.")
            source.seek(0)
            return pd.read_csv(source)
    except (OSError, UnicodeDecodeError, csv.Error, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        raise ValueError(f"Could not read landmark CSV file '{csv_path}': {exc}") from exc


def extract_blazepose_landmarks(
    video_path: Path,
    pose_model_path: Path | None,
    min_visibility: float = 0.5,
    max_frames: int | None = None,
) -> pd.DataFrame:
    """Extract selected pose landmarks from a local video with MediaPipe Tasks.

    The model bundle is supplied by the caller and is never downloaded by this
    function. Frame timestamps passed to MediaPipe are monotonically increasing
    milliseconds derived from the video's reported frame rate.
    """
    if pose_model_path is None:
        raise ValueError("pose_model_path is required; provide a local MediaPipe Pose Landmarker model.")
    video_path = Path(video_path)
    pose_model_path = Path(pose_model_path)
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not pose_model_path.is_file():
        raise FileNotFoundError(f"MediaPipe pose model file not found: {pose_model_path}")
    if isinstance(min_visibility, bool) or not isinstance(min_visibility, (int, float)):
        raise ValueError("min_visibility must be a finite number from 0 to 1.")
    if not math.isfinite(min_visibility) or not 0 <= min_visibility <= 1:
        raise ValueError("min_visibility must be a finite number from 0 to 1.")
    if max_frames is not None and (
        isinstance(max_frames, bool) or not isinstance(max_frames, int) or max_frames < 1
    ):
        raise ValueError("max_frames must be a positive integer when provided.")

    try:
        import cv2
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision
    except ImportError as exc:
        raise ImportError(
            "Video mode requires the optional dependencies. Install them with: "
            "python -m pip install '.[video]'"
        ) from exc

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        capture.release()
        raise ValueError(f"Could not open video file: {video_path}")

    rows: list[dict[str, float | int]] = []
    try:
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError(
                f"Video reports an invalid frame rate ({fps!r}); use a video with a readable positive FPS."
            )

        options = vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(pose_model_path)),
            running_mode=vision.RunningMode.VIDEO,
        )
        try:
            landmarker_context = vision.PoseLandmarker.create_from_options(options)
        except (RuntimeError, ValueError) as exc:
            raise ValueError(
                "Could not initialize MediaPipe Pose Landmarker; verify that "
                f"'{pose_model_path}' is a compatible local .task model: {exc}"
            ) from exc
        with landmarker_context as landmarker:
            frame_index = 0
            previous_timestamp_ms = -1
            while max_frames is None or frame_index < max_frames:
                has_frame, frame = capture.read()
                if not has_frame:
                    break

                time_s = frame_index / fps
                timestamp_ms = max(previous_timestamp_ms + 1, int(round(time_s * 1000)))
                previous_timestamp_ms = timestamp_ms
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                try:
                    result = landmarker.detect_for_video(image, timestamp_ms)
                except (RuntimeError, ValueError) as exc:
                    raise ValueError(
                        f"MediaPipe pose inference failed at frame {frame_index}: {exc}"
                    ) from exc

                poses = getattr(result, "pose_landmarks", None)
                if poses:
                    landmarks_result = poses[0]
                    wrist = landmarks_result[POSE_LANDMARK_IDS["wrist"]]
                    shoulder = landmarks_result[POSE_LANDMARK_IDS["shoulder"]]
                    hip = landmarks_result[POSE_LANDMARK_IDS["hip"]]

                    visibility_values = [
                        getattr(wrist, "visibility", 1.0),
                        getattr(shoulder, "visibility", 1.0),
                        getattr(hip, "visibility", 1.0),
                    ]
                    if all(
                        isinstance(value, (int, float))
                        and math.isfinite(value)
                        and value >= min_visibility
                        for value in visibility_values
                    ):
                        rows.append(
                            {
                                "frame": frame_index,
                                "time_s": time_s,
                                "hip_x": hip.x,
                                "hip_y": hip.y,
                                "shoulder_x": shoulder.x,
                                "shoulder_y": shoulder.y,
                                "wrist_x": wrist.x,
                                "wrist_y": wrist.y,
                            }
                        )
                frame_index += 1
    finally:
        capture.release()

    if not rows:
        raise ValueError(
            "No valid pose frames were extracted. Try a clearer clip, lower min_visibility, or verify the video path."
        )

    return pd.DataFrame(rows)
