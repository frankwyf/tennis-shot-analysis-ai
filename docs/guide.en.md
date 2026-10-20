# Technical Guide (English)

This guide explains how the open-source project is structured and how to answer technical questions during interviews or portfolio reviews.

## Architecture

- `src/tennis_shot_analysis/config.py`: runtime configuration (`AnalysisConfig`)
- `src/tennis_shot_analysis/data.py`: synthetic generation + optional BlazePose extraction
- `src/tennis_shot_analysis/metrics.py`: feature engineering and summary metrics
- `src/tennis_shot_analysis/pipeline.py`: orchestration logic
- `src/tennis_shot_analysis/visualize.py`: chart rendering
- `src/tennis_shot_analysis/cli.py`: command-line interface
- `tests/`: lightweight regression tests

## Core metric definitions

- Wrist speed proxy:
  - Computed from normalized landmark displacement over time:
  - $speed_t = \frac{\sqrt{(\Delta x_t)^2 + (\Delta y_t)^2}}{\Delta t_t}$
- Torso rotation proxy:
  - $shoulder\_x - hip\_x$
- Impact proxy frame:
  - The frame with maximum wrist speed.

## Why synthetic mode exists

- It keeps the repository runnable without private assets.
- It enables deterministic tests and reproducible visuals.
- It demonstrates pipeline design independent of model inference.

## Optional real-video mode

Install the optional extra, then pass a local video and a local MediaPipe Pose
Landmarker `.task` model path. The project does not download model weights:

```bash
python -m pip install -e '.[video]'
tennis-shot-demo --source video --input your_clip.mp4 --pose-model /path/to/pose_landmarker.task
```

The video path uses MediaPipe Tasks, validates the reported frame rate, sends
monotonically increasing timestamps, and releases the capture on completion or
error. If no valid landmarks are extracted, reduce the visibility threshold
or use a clearer single-person clip. The legacy `--use-mediapipe-video` and
`--video-path` flags remain available when paired with `--pose-model`.

## Interview-style Q&A points

1. Why package + CLI instead of notebook only?
   - Better testability, versioning, and automation.
2. Why use proxies instead of full biomechanics?
   - Portfolio scope: explainable signals and clean architecture first.
3. How to evolve this project?
   - Add event labeling, temporal smoothing, and model evaluation datasets.
