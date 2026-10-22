import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from tennis_shot_analysis.config import AnalysisConfig
from tennis_shot_analysis.data import generate_synthetic_landmarks, load_landmarks_csv
from tennis_shot_analysis.pipeline import analyze_landmarks, run_analysis
from tennis_shot_analysis.metrics import compute_metrics
from tennis_shot_analysis.visualize import plot_analysis


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


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"frame_count": 1}, "frame_count"),
        ({"frame_count": 0}, "frame_count"),
        ({"duration_s": 0}, "duration_s"),
        ({"duration_s": float("nan")}, "duration_s"),
        ({"min_visibility": -0.1}, "min_visibility"),
        ({"min_visibility": 1.1}, "min_visibility"),
        ({"max_frames": 0}, "max_frames"),
    ],
)
def test_analysis_config_rejects_invalid_values(kwargs, message):
    with pytest.raises(ValueError, match=message):
        AnalysisConfig(**kwargs)


def test_plot_analysis_supports_non_default_dataframe_index(tmp_path):
    landmarks = run_analysis(AnalysisConfig(frame_count=8))[0]
    landmarks.index = np.arange(20, 28)
    landmarks, summary = compute_metrics(landmarks)

    plot_analysis(landmarks, summary, "test", show=False, save_path=str(tmp_path / "plot.png"))

    assert (tmp_path / "plot.png").is_file()


def test_public_landmark_api_matches_direct_metrics():
    landmarks = generate_synthetic_landmarks(frame_count=12, duration_s=0.8)

    enriched, summary = analyze_landmarks(landmarks)

    assert summary.frame_count == 12
    assert np.isfinite(enriched.select_dtypes(include=np.number).to_numpy()).all()


def test_csv_source_runs_through_same_analysis_pipeline(tmp_path):
    input_path = tmp_path / "landmarks.csv"
    source = generate_synthetic_landmarks(frame_count=16, duration_s=1.1)
    source.to_csv(input_path, index=False)

    landmarks, summary, label = run_analysis(AnalysisConfig(source="csv", input_path=input_path))

    assert summary.frame_count == 16
    assert label == "Landmark CSV: landmarks.csv"
    assert np.isfinite(landmarks.select_dtypes(include=np.number).to_numpy()).all()


def test_csv_cli_runs_successfully(tmp_path):
    repository_root = Path(__file__).resolve().parents[1]
    input_path = tmp_path / "landmarks.csv"
    generate_synthetic_landmarks(frame_count=10, duration_s=0.7).to_csv(input_path, index=False)
    environment = {**os.environ, "MPLBACKEND": "Agg"}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tennis_shot_analysis",
            "--source",
            "csv",
            "--input",
            str(input_path),
            "--no-show",
        ],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert "frame_count" in result.stdout
    assert "impact_source_frame" in result.stdout


def test_csv_cli_reports_invalid_input_without_traceback(tmp_path):
    repository_root = Path(__file__).resolve().parents[1]
    environment = {**os.environ, "MPLBACKEND": "Agg"}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tennis_shot_analysis",
            "--source",
            "csv",
            "--input",
            str(tmp_path / "missing.csv"),
            "--no-show",
        ],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 2
    assert "Landmark CSV file not found" in result.stderr
    assert "Traceback" not in result.stderr


def test_csv_loader_reports_empty_file(tmp_path):
    input_path = tmp_path / "empty.csv"
    input_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not read landmark CSV"):
        load_landmarks_csv(input_path)


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


def test_synthetic_cli_exports_repeatable_csv_and_full_precision_json(tmp_path):
    repository_root = Path(__file__).resolve().parents[1]
    environment = {**os.environ, "MPLBACKEND": "Agg"}
    first_csv = tmp_path / "first" / "landmarks.csv"
    first_json = tmp_path / "first" / "summary.json"
    second_csv = tmp_path / "second" / "landmarks.csv"
    second_json = tmp_path / "second" / "summary.json"

    for landmarks_path, summary_path in ((first_csv, first_json), (second_csv, second_json)):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "tennis_shot_analysis",
                "--no-show",
                "--save-landmarks",
                str(landmarks_path),
                "--save-summary",
                str(summary_path),
            ],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr

    assert first_csv.read_bytes() == second_csv.read_bytes()
    assert first_json.read_bytes() == second_json.read_bytes()
    exported = json.loads(first_json.read_text(encoding="utf-8"))
    assert exported["schema_version"] == 1
    assert exported["source"] == "synthetic"
    assert exported["data_source_label"] == "Synthetic demo sequence"
    assert exported["summary"]["impact_row"] == exported["summary"]["impact_frame"]
    assert "impact_source_frame" in exported["summary"]
    assert "Unnamed: 0" not in load_landmarks_csv(first_csv).columns


def test_cli_reports_summary_output_errors_without_traceback(tmp_path):
    repository_root = Path(__file__).resolve().parents[1]
    blocked_path = tmp_path / "existing-directory"
    blocked_path.mkdir()
    environment = {**os.environ, "MPLBACKEND": "Agg"}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tennis_shot_analysis",
            "--no-show",
            "--save-summary",
            str(blocked_path),
        ],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 2
    assert "Could not write summary JSON" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("prefix", ["", "\ufeff", "\n", " \t\n"])
def test_csv_loader_rejects_duplicate_headers_before_pandas_renames_them(tmp_path, prefix):
    source = tmp_path / "duplicate.csv"
    source.write_text(prefix + 'time_s,"wrist_x",wrist_x\n0,0.2,0.9\n0.1,0.3,0.8\n', encoding="utf-8")
    with pytest.raises(ValueError, match="(?i)duplicate.*wrist_x"):
        load_landmarks_csv(source)


def test_plot_closes_figure_if_saving_fails(tmp_path, monkeypatch):
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    landmarks, summary, label = run_analysis(AnalysisConfig(frame_count=8))
    before = plt.get_fignums()

    def fail_save(*args, **kwargs):
        raise OSError("simulated full disk")

    monkeypatch.setattr(Figure, "savefig", fail_save)
    with pytest.raises(OSError, match="full disk"):
        plot_analysis(landmarks, summary, label, show=False, save_path=str(tmp_path / "figure.png"))
    assert plt.get_fignums() == before
