import pandas as pd

from .config import AnalysisConfig
from .data import extract_blazepose_landmarks, generate_synthetic_landmarks, load_landmarks_csv
from .metrics import AnalysisSummary, compute_metrics


def run_analysis(config: AnalysisConfig) -> tuple[pd.DataFrame, AnalysisSummary, str]:
    if config.source == "video":
        video_path = config.input_path or config.video_path
        raw_landmarks = extract_blazepose_landmarks(
            video_path,
            min_visibility=config.min_visibility,
            max_frames=config.max_frames,
        )
        data_source_label = f"MediaPipe video: {video_path.name}"
    elif config.source == "csv":
        if config.input_path is None:
            raise ValueError("input_path is required when source is 'csv'.")
        raw_landmarks = load_landmarks_csv(config.input_path)
        data_source_label = f"Landmark CSV: {config.input_path.name}"
    else:
        raw_landmarks = generate_synthetic_landmarks(
            frame_count=config.frame_count,
            duration_s=config.duration_s,
        )
        data_source_label = "Synthetic demo sequence"

    landmarks, summary = compute_metrics(raw_landmarks)
    return landmarks, summary, data_source_label


def analyze_landmarks(landmarks: pd.DataFrame) -> tuple[pd.DataFrame, AnalysisSummary]:
    """Validate a canonical landmark sequence and calculate tennis proxy metrics."""
    return compute_metrics(landmarks)
