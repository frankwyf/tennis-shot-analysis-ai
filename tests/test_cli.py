"""Public CLI behavior, including protection of user-supplied input files."""

import importlib.metadata
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tennis_shot_analysis.data import generate_synthetic_landmarks


def run_cli(*arguments, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "tennis_shot_analysis", *map(str, arguments)],
        cwd=cwd,
        env={**os.environ, "MPLBACKEND": "Agg"},
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_version_matches_installed_distribution():
    result = run_cli("--version")
    assert result.returncode == 0, result.stderr
    assert importlib.metadata.version("tennis-shot-analysis-ai") in result.stdout


def test_no_plot_runs_without_importing_matplotlib():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import runpy, sys; sys.modules['matplotlib'] = None; "
            "sys.argv = ['tennis-shot-demo', '--no-plot']; "
            "runpy.run_module('tennis_shot_analysis', run_name='__main__')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "peak_wrist_speed_norm_units" in result.stdout


def test_no_plot_cannot_silently_ignore_requested_figure(tmp_path):
    figure = tmp_path / "figure.png"
    result = run_cli("--no-plot", "--save-figure", figure)
    assert result.returncode == 2
    assert "--no-plot cannot be combined with --save-figure" in result.stderr
    assert not figure.exists()


def test_figure_output_creates_parent_directories(tmp_path):
    figure = tmp_path / "nested" / "figure.png"
    result = run_cli("--no-show", "--save-figure", figure)
    assert result.returncode == 0, result.stderr
    assert figure.read_bytes().startswith(b"\x89PNG")


def test_figure_output_errors_are_actionable(tmp_path):
    result = run_cli("--no-show", "--save-figure", tmp_path)
    assert result.returncode == 2
    assert "figure" in result.stderr.lower()
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("output_flag", ["--save-landmarks", "--save-summary", "--save-figure"])
def test_cli_cannot_overwrite_its_csv_input(tmp_path, output_flag):
    source = tmp_path / "input.csv"
    generate_synthetic_landmarks().to_csv(source, index=False)
    original = source.read_bytes()
    result = run_cli("--source", "csv", "--input", source, "--no-show", output_flag, source)
    assert result.returncode == 2
    assert "must not overwrite an input" in result.stderr
    assert "Traceback" not in result.stderr
    assert source.read_bytes() == original


@pytest.mark.parametrize("link_type", ["hardlink", "symlink"])
def test_cli_protects_input_through_filesystem_aliases(tmp_path, link_type):
    source = tmp_path / "input.csv"
    generate_synthetic_landmarks().to_csv(source, index=False)
    alias = tmp_path / "alias.csv"
    try:
        if link_type == "hardlink":
            os.link(source, alias)
        else:
            alias.symlink_to(source)
    except OSError as exc:
        pytest.skip(f"Filesystem does not support {link_type}: {exc}")
    original = source.read_bytes()
    result = run_cli(
        "--source", "csv", "--input", source, "--no-show", "--save-summary", alias
    )
    assert result.returncode == 2
    assert source.read_bytes() == original


def test_cli_rejects_colliding_outputs_before_writing(tmp_path):
    output = tmp_path / "result.csv"
    result = run_cli("--no-show", "--save-summary", output, "--save-landmarks", output)
    assert result.returncode == 2
    assert "distinct" in result.stderr.lower()
    assert not output.exists()


def test_cli_cannot_overwrite_its_pose_model(tmp_path):
    model = tmp_path / "user-supplied.task"
    model.write_bytes(b"model must survive preflight")
    result = run_cli(
        "--source", "video", "--input", tmp_path / "missing.mp4",
        "--pose-model", model, "--save-summary", model, "--no-show",
    )
    assert result.returncode == 2
    assert "input" in result.stderr.lower() or "model" in result.stderr.lower()
    assert "Video file not found" not in result.stderr
    assert model.read_bytes() == b"model must survive preflight"


def test_documented_csv_example_has_independently_calculable_metrics(tmp_path):
    example = Path(__file__).resolve().parents[1] / "examples" / "landmarks.csv"
    output = tmp_path / "summary.json"
    result = run_cli("--source", "csv", "--input", example, "--no-plot", "--save-summary", output)
    assert result.returncode == 0, result.stderr
    summary = json.loads(output.read_text(encoding="utf-8"))["summary"]
    assert summary["frame_count"] == 3
    assert summary["impact_row"] == summary["impact_source_frame"] == 1
    assert summary["peak_wrist_speed_norm_units"] == pytest.approx(math.hypot(0.1, 0.05) / 0.1)
    assert summary["mean_torso_rotation_proxy"] == pytest.approx((0 + 0.02 + 0.03) / 3)
