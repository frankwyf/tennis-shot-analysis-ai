from dataclasses import dataclass

import numpy as np
import pandas as pd

REQUIRED_LANDMARK_COLUMNS = (
    "time_s",
    "hip_x",
    "hip_y",
    "shoulder_x",
    "shoulder_y",
    "wrist_x",
    "wrist_y",
)


@dataclass(slots=True)
class AnalysisSummary:
    frame_count: int
    # Legacy name retained for compatibility; this is a zero-based row position.
    impact_frame: int
    impact_time_s: float
    peak_wrist_speed_norm_units: float
    mean_torso_rotation_proxy: float
    impact_source_frame: int | None = None

    def to_dict(self) -> dict[str, int | float | None]:
        """Return an unrounded, JSON-compatible summary of the analyzed sequence."""
        return {
            "frame_count": self.frame_count,
            "impact_row": self.impact_frame,
            "impact_frame": self.impact_frame,
            "impact_source_frame": self.impact_source_frame,
            "impact_time_s": self.impact_time_s,
            "peak_wrist_speed_norm_units": self.peak_wrist_speed_norm_units,
            "mean_torso_rotation_proxy": self.mean_torso_rotation_proxy,
        }

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "frame_count": self.frame_count,
                "impact_frame": self.impact_frame,
                "impact_row": self.impact_frame,
                "impact_source_frame": self.impact_source_frame,
                "impact_time_s": round(self.impact_time_s, 3),
                "peak_wrist_speed_norm_units": round(self.peak_wrist_speed_norm_units, 3),
                "mean_torso_rotation_proxy": round(self.mean_torso_rotation_proxy, 4),
            }
        )


def _validate_landmarks(landmarks: pd.DataFrame) -> dict[str, np.ndarray]:
    if not isinstance(landmarks, pd.DataFrame):
        raise TypeError("landmarks must be a pandas DataFrame.")

    if len(landmarks) < 2:
        raise ValueError("At least two frames are required to compute speed metrics.")

    missing_columns = [column for column in REQUIRED_LANDMARK_COLUMNS if column not in landmarks]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Landmark data is missing required columns: {missing}.")

    non_numeric_columns = [
        column
        for column in REQUIRED_LANDMARK_COLUMNS
        if not pd.api.types.is_numeric_dtype(landmarks[column].dtype)
        or pd.api.types.is_complex_dtype(landmarks[column].dtype)
    ]
    if non_numeric_columns:
        columns = ", ".join(non_numeric_columns)
        raise ValueError(f"Landmark columns must be numeric; invalid columns: {columns}.")

    if "frame" in landmarks and (
        not pd.api.types.is_numeric_dtype(landmarks["frame"].dtype)
        or pd.api.types.is_complex_dtype(landmarks["frame"].dtype)
    ):
        raise ValueError("frame column must contain numeric source frame numbers.")

    values = {
        column: landmarks[column].to_numpy(dtype=np.float64, na_value=np.nan)
        for column in REQUIRED_LANDMARK_COLUMNS
    }
    if "frame" in landmarks:
        values["frame"] = landmarks["frame"].to_numpy(dtype=np.float64, na_value=np.nan)
    non_finite_values = []
    for column, column_values in values.items():
        invalid_positions = np.flatnonzero(~np.isfinite(column_values))
        if invalid_positions.size:
            positions = ", ".join(str(int(position)) for position in invalid_positions[:5])
            non_finite_values.append(f"{column} at row position(s) {positions}")
    if non_finite_values:
        details = "; ".join(non_finite_values)
        raise ValueError(f"Non-finite values in required landmark data: {details}.")

    if "frame" in values:
        source_frames = values["frame"]
        valid_frame_numbers = (
            (source_frames >= 0)
            & (source_frames == np.floor(source_frames))
            & (np.diff(source_frames, prepend=source_frames[0]) > 0)
        )
        valid_frame_numbers[0] = source_frames[0] >= 0 and source_frames[0] == np.floor(source_frames[0])
        if not valid_frame_numbers.all():
            raise ValueError(
                "frame must contain non-negative, strictly increasing integer source frame numbers."
            )

    with np.errstate(over="ignore", invalid="ignore"):
        time_deltas = np.diff(values["time_s"])
    if not np.isfinite(time_deltas).all():
        raise ValueError("Timestamp intervals must be finite.")

    non_increasing_positions = np.flatnonzero(time_deltas <= 0) + 1
    if non_increasing_positions.size:
        positions = ", ".join(str(int(position)) for position in non_increasing_positions[:5])
        raise ValueError(
            "time_s must be strictly increasing; invalid interval before row "
            f"position(s) {positions}."
        )

    return values


def compute_metrics(landmarks: pd.DataFrame) -> tuple[pd.DataFrame, AnalysisSummary]:
    values = _validate_landmarks(landmarks)

    enriched = landmarks.copy()
    time_deltas = np.diff(values["time_s"])
    elapsed_s = np.concatenate(([time_deltas[0]], time_deltas))

    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        dx = np.diff(values["wrist_x"], prepend=values["wrist_x"][0])
        dy = np.diff(values["wrist_y"], prepend=values["wrist_y"][0])
        wrist_speed = np.hypot(dx, dy) / elapsed_s
        torso_rotation_proxy = values["shoulder_x"] - values["hip_x"]

    if not np.isfinite(wrist_speed).all():
        invalid_positions = np.flatnonzero(~np.isfinite(wrist_speed))
        positions = ", ".join(str(int(position)) for position in invalid_positions[:5])
        raise ValueError(
            "Computed wrist_speed contains non-finite values at row position(s) "
            f"{positions}; check coordinate magnitudes and timestamp intervals."
        )
    if not np.isfinite(torso_rotation_proxy).all():
        invalid_positions = np.flatnonzero(~np.isfinite(torso_rotation_proxy))
        positions = ", ".join(str(int(position)) for position in invalid_positions[:5])
        raise ValueError(
            "Computed torso_rotation_proxy contains non-finite values at row "
            f"position(s) {positions}; check coordinate magnitudes."
        )

    enriched["wrist_speed"] = wrist_speed
    enriched["torso_rotation_proxy"] = torso_rotation_proxy

    impact_row = int(np.argmax(wrist_speed))
    impact_time = float(values["time_s"][impact_row])
    peak_speed = float(wrist_speed[impact_row])
    impact_source_frame = int(values["frame"][impact_row]) if "frame" in values else None

    summary = AnalysisSummary(
        frame_count=int(len(enriched)),
        impact_frame=impact_row,
        impact_time_s=impact_time,
        peak_wrist_speed_norm_units=peak_speed,
        mean_torso_rotation_proxy=float(enriched["torso_rotation_proxy"].mean()),
        impact_source_frame=impact_source_frame,
    )
    return enriched, summary
