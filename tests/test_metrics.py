import numpy as np
import pandas as pd
import pytest

from tennis_shot_analysis.metrics import compute_metrics


def make_landmarks() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time_s": [0.0, 0.1, 0.4],
            "hip_x": [0.5, 0.5, 0.5],
            "hip_y": [0.78, 0.78, 0.78],
            "shoulder_x": [0.5, 0.52, 0.53],
            "shoulder_y": [0.42, 0.42, 0.42],
            "wrist_x": [0.4, 0.5, 0.7],
            "wrist_y": [0.6, 0.6, 0.6],
        }
    )


def test_compute_metrics_requires_multiple_frames():
    with pytest.raises(ValueError, match="At least two frames"):
        compute_metrics(make_landmarks().iloc[:1])


@pytest.mark.parametrize(
    "timestamps",
    [
        [0.0, 0.0, 0.4],
        [0.0, 0.4, 0.3],
    ],
    ids=["duplicate", "decreasing"],
)
def test_compute_metrics_rejects_non_increasing_timestamps(timestamps):
    landmarks = make_landmarks()
    landmarks["time_s"] = timestamps

    with pytest.raises(ValueError, match="time_s must be strictly increasing"):
        compute_metrics(landmarks)


@pytest.mark.parametrize("bad_value", [np.nan, np.inf, -np.inf])
def test_compute_metrics_rejects_non_finite_timestamps(bad_value):
    landmarks = make_landmarks()
    landmarks.loc[1, "time_s"] = bad_value

    with pytest.raises(ValueError, match="(?i)non-finite.*time_s"):
        compute_metrics(landmarks)


@pytest.mark.parametrize("bad_value", [np.nan, np.inf, -np.inf])
def test_compute_metrics_rejects_non_finite_landmarks(bad_value):
    landmarks = make_landmarks()
    landmarks.loc[1, "wrist_x"] = bad_value

    with pytest.raises(ValueError, match="(?i)non-finite.*wrist_x"):
        compute_metrics(landmarks)


def test_compute_metrics_rejects_missing_landmark_columns():
    landmarks = make_landmarks().drop(columns="wrist_y")

    with pytest.raises(ValueError, match="missing required columns.*wrist_y"):
        compute_metrics(landmarks)


def test_compute_metrics_rejects_non_numeric_columns():
    landmarks = make_landmarks()
    landmarks["time_s"] = ["0.0", "0.1", "0.4"]

    with pytest.raises(ValueError, match="must be numeric.*time_s"):
        compute_metrics(landmarks)


def test_compute_metrics_supports_irregular_positive_intervals():
    landmarks = make_landmarks()
    enriched, _ = compute_metrics(landmarks)

    assert np.allclose(enriched["wrist_speed"].to_numpy(), [0.0, 1.0, 2.0 / 3.0])


def test_impact_frame_is_row_position_not_dataframe_index_label():
    landmarks = make_landmarks()
    landmarks.index = [10, 20, 30]

    _, summary = compute_metrics(landmarks)

    assert summary.impact_frame == 1
    assert summary.impact_time_s == pytest.approx(0.1)


def test_summary_maps_peak_speed_row_to_source_frame_number():
    landmarks = make_landmarks()
    landmarks["frame"] = [100, 104, 111]

    _, summary = compute_metrics(landmarks)

    assert summary.impact_frame == 1
    assert summary.impact_source_frame == 104


@pytest.mark.parametrize("frames", [[0, 0, 2], [0, 3, 2], [0, 1.5, 2]])
def test_compute_metrics_rejects_invalid_source_frame_numbers(frames):
    landmarks = make_landmarks()
    landmarks["frame"] = frames

    with pytest.raises(ValueError, match="frame.*strictly increasing integer"):
        compute_metrics(landmarks)


def test_compute_metrics_rejects_non_finite_derived_speed():
    landmarks = make_landmarks().iloc[:2].copy()
    landmarks["wrist_x"] = [-1e308, 1e308]

    with pytest.raises(ValueError, match="wrist_speed.*non-finite"):
        compute_metrics(landmarks)
