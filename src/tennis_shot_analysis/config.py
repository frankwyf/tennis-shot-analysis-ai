from dataclasses import dataclass
import math
from pathlib import Path


@dataclass(slots=True)
class AnalysisConfig:
    use_mediapipe_video: bool = False
    video_path: Path = Path("sample_tennis_video.mp4")
    min_visibility: float = 0.5
    max_frames: int | None = None
    frame_count: int = 80
    duration_s: float = 1.6

    def __post_init__(self) -> None:
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
