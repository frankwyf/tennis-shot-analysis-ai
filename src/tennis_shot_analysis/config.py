import math
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(slots=True)
class AnalysisConfig:
    source: Literal["synthetic", "csv", "video"] = "synthetic"
    input_path: Path | None = None
    use_mediapipe_video: bool = False
    video_path: Path = Path("sample_tennis_video.mp4")
    pose_model_path: Path | None = None
    min_visibility: float = 0.5
    max_frames: int | None = None
    frame_count: int = 80
    duration_s: float = 1.6

    def __post_init__(self) -> None:
        if self.source not in {"synthetic", "csv", "video"}:
            raise ValueError("source must be one of: synthetic, csv, video.")
        if isinstance(self.frame_count, bool) or not isinstance(self.frame_count, int) or self.frame_count < 2:
            raise ValueError("frame_count must be an integer greater than or equal to 2.")
        if isinstance(self.duration_s, bool) or not isinstance(self.duration_s, (int, float)):
            raise ValueError("duration_s must be a finite positive number.")
        if not math.isfinite(self.duration_s) or self.duration_s <= 0:
            raise ValueError("duration_s must be a finite positive number.")
        if isinstance(self.min_visibility, bool) or not isinstance(self.min_visibility, (int, float)):
            raise ValueError("min_visibility must be a finite number from 0 to 1.")
        if not math.isfinite(self.min_visibility) or not 0 <= self.min_visibility <= 1:
            raise ValueError("min_visibility must be a finite number from 0 to 1.")
        if self.max_frames is not None and (
            isinstance(self.max_frames, bool)
            or not isinstance(self.max_frames, int)
            or self.max_frames < 1
        ):
            raise ValueError("max_frames must be a positive integer when provided.")
        self.video_path = Path(self.video_path)
        if self.input_path is not None:
            self.input_path = Path(self.input_path)
        if self.pose_model_path is not None:
            self.pose_model_path = Path(self.pose_model_path)

        if self.use_mediapipe_video:
            if self.source not in {"synthetic", "video"}:
                raise ValueError("use_mediapipe_video cannot be combined with a non-video source.")
            self.source = "video"
        if self.source == "video" and self.input_path is None:
            self.input_path = self.video_path
        if self.source == "video" and self.pose_model_path is None:
            raise ValueError(
                "pose_model_path is required for video analysis; provide a local MediaPipe Pose Landmarker model."
            )
        if self.source == "csv" and self.input_path is None:
            raise ValueError("input_path is required when source is 'csv'.")
