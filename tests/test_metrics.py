import pandas as pd

from tennis_shot_analysis.metrics import compute_metrics


def test_compute_metrics_requires_multiple_frames():
    one_row = pd.DataFrame(
        {
            "frame": [0],
            "time_s": [0.0],
            "hip_x": [0.5],
            "hip_y": [0.78],
            "shoulder_x": [0.5],
            "shoulder_y": [0.42],
            "wrist_x": [0.4],
            "wrist_y": [0.6],
        }
    )

    try:
        compute_metrics(one_row)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "At least two frames" in str(exc)
