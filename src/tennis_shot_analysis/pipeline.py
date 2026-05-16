from .config import AnalysisConfig
from .data import extract_blazepose_landmarks, generate_synthetic_landmarks
from .metrics import AnalysisSummary, compute_metrics


def run_analysis(config: AnalysisConfig):
    if config.use_mediapipe_video:
        raw_landmarks = extract_blazepose_landmarks(
            config.video_path,
            min_visibility=config.min_visibility,
            max_frames=config.max_frames,
        )
        data_source_label = f"MediaPipe video: {config.video_path.name}"
    else:
        raw_landmarks = generate_synthetic_landmarks(
            frame_count=config.frame_count,
            duration_s=config.duration_s,
        )
        data_source_label = "Synthetic demo sequence"

    landmarks, summary = compute_metrics(raw_landmarks)
    return landmarks, summary, data_source_label
