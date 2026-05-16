import argparse
from pathlib import Path

from .config import AnalysisConfig
from .pipeline import run_analysis
from .visualize import plot_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run tennis shot analysis demo")
    parser.add_argument("--use-mediapipe-video", action="store_true", help="Enable real video mode")
    parser.add_argument("--video-path", type=Path, default=Path("sample_tennis_video.mp4"), help="Path to local video")
    parser.add_argument("--min-visibility", type=float, default=0.5, help="Minimum landmark visibility")
    parser.add_argument("--max-frames", type=int, default=None, help="Optional frame limit")
    parser.add_argument("--frame-count", type=int, default=80, help="Synthetic frame count")
    parser.add_argument("--duration-s", type=float, default=1.6, help="Synthetic duration (seconds)")
    parser.add_argument("--save-figure", type=Path, default=None, help="Optional output image path")
    parser.add_argument("--no-show", action="store_true", help="Do not open matplotlib window")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = AnalysisConfig(
        use_mediapipe_video=args.use_mediapipe_video,
        video_path=args.video_path,
        min_visibility=args.min_visibility,
        max_frames=args.max_frames,
        frame_count=args.frame_count,
        duration_s=args.duration_s,
    )

    landmarks, summary, label = run_analysis(config)
    plot_analysis(
        landmarks,
        summary,
        data_source_label=label,
        show=not args.no_show,
        save_path=str(args.save_figure) if args.save_figure else None,
    )
    print(summary.to_series().to_string())


if __name__ == "__main__":
    main()
