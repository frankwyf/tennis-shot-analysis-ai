from tennis_shot_analysis.config import AnalysisConfig
from tennis_shot_analysis.pipeline import run_analysis


def test_run_analysis_synthetic_produces_expected_columns():
    config = AnalysisConfig(use_mediapipe_video=False, frame_count=40, duration_s=1.2)
    landmarks, summary, label = run_analysis(config)

    expected_columns = {
        "frame",
        "time_s",
        "hip_x",
        "hip_y",
        "shoulder_x",
        "shoulder_y",
        "wrist_x",
        "wrist_y",
        "wrist_speed",
        "torso_rotation_proxy",
    }
    assert expected_columns.issubset(set(landmarks.columns))
    assert summary.frame_count == 40
    assert 0 <= summary.impact_frame < 40
    assert label == "Synthetic demo sequence"
