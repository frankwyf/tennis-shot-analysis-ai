# From Notebook to Package: Migration Guide

This document explains how the repository evolved from a single exploratory notebook into a portfolio-ready engineering project.

## Why migrate at all?

A notebook is excellent for exploration, but it becomes fragile when a project needs:

- repeatable execution
- dependency management
- automated tests
- clearer public documentation
- reusability outside Jupyter

The migration in this repository keeps the learning value of the original notebook while moving stable logic into modules.

## What changed conceptually

### Stage 1: notebook-owned logic

In the original workflow, the notebook directly owned:

- configuration values
- synthetic data generation
- optional BlazePose extraction
- metric computation
- charting

This is convenient for experimentation, but all responsibilities are mixed in one file.

### Stage 2: package-owned logic

The refactored project moves those responsibilities into dedicated modules:

- `config.py`: runtime parameters
- `data.py`: data acquisition and synthetic generation
- `metrics.py`: feature engineering and summary outputs
- `pipeline.py`: high-level orchestration
- `visualize.py`: plotting
- `cli.py`: command-line usage

The notebook becomes a consumer of the package rather than the owner of all behavior.

## Mapping notebook sections to modules

### Imports and setup

Notebook imports were split into:

- package runtime dependencies in `pyproject.toml`
- local module imports inside the package
- notebook-only usage through high-level package APIs

### Runtime flags

Notebook variables such as `USE_MEDIAPIPE_VIDEO`, `VIDEO_PATH`, and `MIN_VISIBILITY` became structured configuration inside `AnalysisConfig`.

This improves:

- readability
- default handling
- testability
- CLI interoperability

### Synthetic sequence generation

The synthetic forehand-like motion was extracted into `generate_synthetic_landmarks()` in `data.py`.

Benefits:

- deterministic public demo path
- isolated function-level testing
- reuse by notebook, CLI, and future services

### Real-video extraction

The video branch became `extract_blazepose_landmarks()` and uses MediaPipe
Tasks with an explicit local `.task` model path. This avoids automatic model
downloads and gives frame processing a documented timestamp and cleanup path.

This matters because optional dependencies and file checks belong in a dedicated boundary, not scattered through notebooks.

### Metric calculation

The wrist-speed and torso-rotation proxy logic moved into `compute_metrics()`.

Benefits:

- metrics can be tested without plotting
- logic can be reused by scripts and applications
- future metrics can be added without rewriting notebook cells

### Visualization

Plot creation moved into `plot_analysis()`.

This separates analysis from rendering and makes headless validation easier.

## Why a CLI was added

The CLI is important for engineering maturity.

It allows the same pipeline to run:

- without Jupyter
- in CI-like workflows
- from a single documented command
- with explicit runtime parameters

That is why the repository now supports:

```bash
python -m tennis_shot_analysis --no-show
```

and:

```bash
tennis-shot-demo --no-show
```

## Why tests were added

Notebook outputs are visual and interactive, which makes regressions harder to detect.

The tests in this repository verify:

- the synthetic pipeline returns the expected schema
- metric computation fails correctly on insufficient data

These are intentionally small but valuable checks. They protect the public demo path without over-engineering the project.

## Why keep the original notebook?

Keeping the original notebook is useful because it shows the project history.

It lets reviewers and learners see:

- how exploratory code looked before refactoring
- how responsibilities were separated
- what engineering improvements were made

That is often more persuasive in a portfolio than showing only the final polished structure.

## How to explain this in interviews

A concise explanation is:

1. The original notebook proved the analysis idea.
2. The refactor extracted stable logic into modules.
3. The repository gained CLI execution, tests, docs, and sanitization safeguards.
4. The result is easier to maintain, publish, and discuss technically.

## Next migration steps if you want to keep growing the project

- Add sample output images generated during CI or release workflows.
- Add a small benchmark dataset manifest format.
- Add temporal smoothing or shot-phase segmentation.
- Add a web demo or API layer on top of the package.
