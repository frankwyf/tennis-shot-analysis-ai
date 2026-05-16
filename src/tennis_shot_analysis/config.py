from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AnalysisConfig:
    use_mediapipe_video: bool = False
    video_path: Path = Path("sample_tennis_video.mp4")
    min_visibility: float = 0.5
    max_frames: int | None = None
    frame_count: int = 80
    duration_s: float = 1.6
