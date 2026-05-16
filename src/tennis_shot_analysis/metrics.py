from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class AnalysisSummary:
    frame_count: int
    impact_frame: int
    impact_time_s: float
    peak_wrist_speed_norm_units: float
    mean_torso_rotation_proxy: float

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "frame_count": self.frame_count,
                "impact_frame": self.impact_frame,
                "impact_time_s": round(self.impact_time_s, 3),
                "peak_wrist_speed_norm_units": round(self.peak_wrist_speed_norm_units, 3),
                "mean_torso_rotation_proxy": round(self.mean_torso_rotation_proxy, 4),
            }
        )


def compute_metrics(landmarks: pd.DataFrame) -> tuple[pd.DataFrame, AnalysisSummary]:
    if len(landmarks) < 2:
        raise ValueError("At least two frames are required to compute speed metrics.")

    enriched = landmarks.copy()
    dt = enriched["time_s"].diff().fillna(enriched["time_s"].iloc[1] - enriched["time_s"].iloc[0])
    dx = enriched["wrist_x"].diff().fillna(0.0)
    dy = enriched["wrist_y"].diff().fillna(0.0)

    enriched["wrist_speed"] = np.sqrt(dx ** 2 + dy ** 2) / dt
    enriched["torso_rotation_proxy"] = enriched["shoulder_x"] - enriched["hip_x"]

    impact_frame = int(enriched["wrist_speed"].idxmax())
    impact_time = float(enriched.loc[impact_frame, "time_s"])
    peak_speed = float(enriched.loc[impact_frame, "wrist_speed"])

    summary = AnalysisSummary(
        frame_count=int(len(enriched)),
        impact_frame=impact_frame,
        impact_time_s=impact_time,
        peak_wrist_speed_norm_units=peak_speed,
        mean_torso_rotation_proxy=float(enriched["torso_rotation_proxy"].mean()),
    )
    return enriched, summary
