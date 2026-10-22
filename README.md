# Tennis Shot Analysis AI

[![CI](https://github.com/frankwyf/tennis-shot-analysis-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/frankwyf/tennis-shot-analysis-ai/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/frankwyf/tennis-shot-analysis-ai)](https://github.com/frankwyf/tennis-shot-analysis-ai/releases)
[![License: BSD-2-Clause](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](LICENSE)

A small Python library and CLI for reproducible **2D tennis motion proxy analysis**.
Start with deterministic synthetic landmarks, bring a canonical CSV, or opt into
MediaPipe Tasks for a local video and a user-supplied model.

The project is in **alpha (0.x)**. It is useful for learning, testing pose-data
pipelines, and exploratory analysis. The metrics are not calibrated biomechanics,
ball-contact detection, coaching assessments, or medical measurements. See the
[metric definitions and limitations](docs/METRICS.md).

## Start here

Python 3.10–3.13 is covered by the core CI matrix. Python 3.12 is the reference
macOS environment. Core CI includes Linux, macOS, Windows, and a Python 3.10 job
using the numerical dependencies' declared lower bounds. Optional video has a
separate macOS job. The live badge links to the actual results.

**If using an external SSD on macOS, configure and verify storage before installing:**
[macOS and external SSD setup](docs/MACOS.md). Keep the checkout and `.venv` on
that volume; stop if it is unavailable.

```bash
git clone https://github.com/frankwyf/tennis-shot-analysis-ai.git
cd tennis-shot-analysis-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .

# No GUI or plotting imports; no video dependencies or model required.
python -m tennis_shot_analysis --no-plot \
  --save-landmarks artifacts/landmarks.csv \
  --save-summary artifacts/summary.json
```

On Windows, create the environment with `py -3.12 -m venv .venv` and activate
with `.venv\Scripts\Activate.ps1`. Other commands use the same `python` entry point.

The 80-frame default demo produces a peak at analyzed row/source frame 40.
Printed numbers are rounded; JSON preserves the computed float precision.
Generate a plot without opening a window:

```bash
tennis-shot-demo --no-show --save-figure artifacts/figures/analysis.png
tennis-shot-demo --version
```

To use a built distribution, download the wheel from
[GitHub Releases](https://github.com/frankwyf/tennis-shot-analysis-ai/releases),
verify it against the accompanying `SHA256SUMS`, and install it with the Python
in your project environment. Releases currently target GitHub; PyPI publication
is not configured.

## Bring your landmarks

```bash
tennis-shot-demo --source csv --input examples/landmarks.csv --no-plot
```

The example is generated data, not a person's recording. Canonical input has at
least two rows and unique column names:

```text
frame,time_s,hip_x,hip_y,shoulder_x,shoulder_y,wrist_x,wrist_y
0,0.0,0.5,0.78,0.5,0.42,0.3,0.6
1,0.1,0.5,0.78,0.52,0.42,0.4,0.55
2,0.2,0.5,0.78,0.53,0.42,0.45,0.53
```

Required values are numeric and finite; `time_s` increases strictly. Irregular
positive intervals are accepted. `frame` is optional and, when present, holds
non-negative, strictly increasing integer source-frame numbers. Duplicate CSV
headers are rejected before pandas can rename them. Extra uniquely named
columns are preserved. See [API and output contracts](docs/CLI.md).

```python
import pandas as pd
from tennis_shot_analysis import AnalysisSummary, analyze_landmarks

landmarks = pd.read_csv("examples/landmarks.csv")
enriched, summary = analyze_landmarks(landmarks)
print(summary.to_dict())
```

This table interface can accept output from other pose estimators when the
coordinate and time conventions match. It currently analyzes one sequence of
wrist/shoulder/hip landmarks; automatic handedness, multiple people, 3D metrics,
and arbitrary sport-specific measures are not implemented.

## Optional local-video mode

```bash
python -m pip install -e '.[video]'
tennis-shot-demo --source video --input your_clip.mp4 \
  --pose-model /path/to/pose_landmarker.task --no-show
```

Use a clip you have permission to process and a locally supplied compatible
Pose Landmarker `.task` model. No weights are downloaded automatically. The
extractor selects the first detected person's **right** wrist, shoulder, and
hip, rejects low-visibility frames, and derives time from the reported FPS.
Variable frame-rate presentation timestamps are not supported.

Wheel availability varies by Python, OS, and architecture. Check it before
installation; use only one OpenCV distribution in an environment. The video
extra lets MediaPipe choose its OpenCV dependency. `requirements.txt` installs
core only; `requirements-video.txt` selects the same video extra.

The optional CI smoke check uses real OpenCV encoding/decoding and real Tasks
imports, with a **fake landmarker**. It verifies integration without a model;
it does not validate real pose inference. On the reference Apple Silicon Mac,
video-wheel downloads were stopped for low throughput; local video inference
remains unverified. See [validation evidence](docs/VALIDATION.md).

## Develop and contribute

```bash
python -m pip install -e '.[dev,release]'
python -m pytest
python -m build
```

The package lives in `src/tennis_shot_analysis`; regression tests are in `tests/`.
The [original notebook](BlazePose_tennis_shot_analysis.ipynb) and
[package notebook](notebooks/package_workflow_demo.ipynb) remain learning references.

- [Contributing](CONTRIBUTING.md), [governance](GOVERNANCE.md), [security policy](SECURITY.md)
- [Detailed upgrade roadmap](docs/ROADMAP.md) and [release procedure](docs/RELEASING.md)
- Technical guides: [English](docs/guide.en.md), [中文](docs/guide.zh-CN.md), [日本語](docs/guide.ja.md)
- [Changelog](CHANGELOG.md), [sanitization checklist](docs/SANITIZATION.md), [notebook migration](docs/migration.en.md)

CLI exports must use distinct paths and cannot overwrite input/model files,
including aliases through symlinks or hardlinks. Existing unrelated output
files can be replaced, so select an output directory deliberately. All output
parents are created automatically. [BSD 2-Clause license](LICENSE).
