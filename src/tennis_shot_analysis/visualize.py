from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .metrics import AnalysisSummary


def plot_analysis(
    landmarks: pd.DataFrame,
    summary: AnalysisSummary,
    data_source_label: str,
    show: bool = True,
    save_path: str | None = None,
) -> None:
    """Plot the proxy metrics, creating output parents and closing owned figures."""
    with plt.style.context("seaborn-v0_8-whitegrid"):
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        try:
            axes[0].plot(landmarks["wrist_x"], landmarks["wrist_y"], color="#c44e52", linewidth=2)
            axes[0].scatter(
                landmarks.iloc[summary.impact_frame]["wrist_x"],
                landmarks.iloc[summary.impact_frame]["wrist_y"],
                color="#4c72b0",
                s=80,
                label="Peak speed frame",
            )
            axes[0].invert_yaxis()
            axes[0].set_title(f"{data_source_label}: wrist trajectory")
            axes[0].set_xlabel("Normalized x")
            axes[0].set_ylabel("Normalized y")
            axes[0].legend()

            axes[1].plot(landmarks["time_s"], landmarks["wrist_speed"], color="#55a868", linewidth=2)
            axes[1].axvline(summary.impact_time_s, color="#4c72b0", linestyle="--", label="Impact proxy")
            axes[1].set_title(f"{data_source_label}: wrist speed over time")
            axes[1].set_xlabel("Time (s)")
            axes[1].set_ylabel("Speed (normalized units / s)")
            axes[1].legend()

            fig.tight_layout()
            if save_path:
                output = Path(save_path)
                if output.is_dir():
                    raise IsADirectoryError(f"Figure output is a directory: {output}")
                output.parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(output, dpi=200)
            if show:
                plt.show()
        finally:
            plt.close(fig)
