import argparse
import json
from pathlib import Path

from .config import AnalysisConfig
from .pipeline import run_analysis
from .visualize import plot_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run tennis shot analysis demo")
    parser.add_argument("--source", choices=("synthetic", "csv", "video"), default="synthetic")
    parser.add_argument("--input", type=Path, default=None, help="Landmark CSV or local video path")
    parser.add_argument(
        "--use-mediapipe-video",
        action="store_true",
        help="Deprecated alias for --source video",
    )
    parser.add_argument(
        "--video-path",
        type=Path,
        default=Path("sample_tennis_video.mp4"),
        help="Legacy video path; prefer --source video --input PATH",
    )
    parser.add_argument(
        "--pose-model",
        type=Path,
        default=None,
        help="Path to a local MediaPipe Pose Landmarker .task model (never downloaded automatically)",
    )
    parser.add_argument("--min-visibility", type=float, default=0.5, help="Minimum landmark visibility")
    parser.add_argument("--max-frames", type=int, default=None, help="Optional frame limit")
    parser.add_argument("--frame-count", type=int, default=80, help="Synthetic frame count")
    parser.add_argument("--duration-s", type=float, default=1.6, help="Synthetic duration (seconds)")
    parser.add_argument("--save-figure", type=Path, default=None, help="Optional output image path")
    parser.add_argument(
        "--save-landmarks",
        type=Path,
        default=None,
        help="Optional CSV path for the analyzed landmarks and derived metrics",
    )
    parser.add_argument(
        "--save-summary",
        type=Path,
        default=None,
        help="Optional JSON path for a versioned, machine-readable analysis summary",
    )
    parser.add_argument("--no-show", action="store_true", help="Do not open matplotlib window")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    source = "video" if args.use_mediapipe_video else args.source
    if args.use_mediapipe_video and args.source not in {"synthetic", "video"}:
        parser.error("--use-mediapipe-video cannot be combined with --source csv.")
    input_path = args.input
    if source == "video" and input_path is None:
        input_path = args.video_path

    try:
        config = AnalysisConfig(
            source=source,
            input_path=input_path,
            use_mediapipe_video=args.use_mediapipe_video,
            video_path=args.video_path,
            pose_model_path=args.pose_model,
            min_visibility=args.min_visibility,
            max_frames=args.max_frames,
            frame_count=args.frame_count,
            duration_s=args.duration_s,
        )

        landmarks, summary, label = run_analysis(config)
        if args.save_landmarks:
            try:
                args.save_landmarks.parent.mkdir(parents=True, exist_ok=True)
                landmarks.to_csv(args.save_landmarks, index=False)
            except OSError as exc:
                parser.error(f"Could not write landmark CSV to {args.save_landmarks}: {exc}")
        if args.save_summary:
            summary_document = {
                "schema_version": 1,
                "source": config.source,
                "data_source_label": label,
                "summary": summary.to_dict(),
            }
            try:
                args.save_summary.parent.mkdir(parents=True, exist_ok=True)
                args.save_summary.write_text(
                    json.dumps(summary_document, indent=2, sort_keys=True, allow_nan=False) + "\n",
                    encoding="utf-8",
                )
            except (OSError, ValueError) as exc:
                parser.error(f"Could not write summary JSON to {args.save_summary}: {exc}")
        plot_analysis(
            landmarks,
            summary,
            data_source_label=label,
            show=not args.no_show,
            save_path=str(args.save_figure) if args.save_figure else None,
        )
    except (FileNotFoundError, ImportError, ValueError) as exc:
        parser.error(str(exc))
    print(summary.to_series().to_string())


if __name__ == "__main__":
    main()
