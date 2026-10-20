import os
from pathlib import Path
import subprocess
import sys

import numpy as np

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
    assert np.isfinite(landmarks.select_dtypes(include=np.number).to_numpy()).all()


def test_run_analysis_synthetic_is_repeatable():
    config = AnalysisConfig(use_mediapipe_video=False, frame_count=40, duration_s=1.2)

    first_landmarks, first_summary, first_label = run_analysis(config)
    second_landmarks, second_summary, second_label = run_analysis(config)

    assert first_landmarks.equals(second_landmarks)
    assert first_summary == second_summary
    assert first_label == second_label


def test_cli_synthetic_no_show_exits_successfully():
    repository_root = Path(__file__).resolve().parents[1]
    environment = {**os.environ, "MPLBACKEND": "Agg"}

    result = subprocess.run(
        [sys.executable, "-m", "tennis_shot_analysis", "--no-show"],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert "frame_count" in result.stdout
