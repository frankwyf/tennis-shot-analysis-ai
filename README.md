# Tennis Shot Analysis AI

An open-source, portfolio-ready tennis shot analysis project built from a notebook prototype.

This repository provides:

- a reusable Python package in `src/tennis_shot_analysis`
- a CLI workflow for repeatable runs
- lightweight tests for regression safety
- multilingual technical docs
- a retained original notebook for learning and comparison
- a package-oriented notebook under `notebooks/`

## Documentation

- Main technical guide (English): [docs/guide.en.md](docs/guide.en.md)
- 技术说明（中文）: [docs/guide.zh-CN.md](docs/guide.zh-CN.md)
- 技術ガイド（日本語）: [docs/guide.ja.md](docs/guide.ja.md)
- Sanitization checklist: [docs/SANITIZATION.md](docs/SANITIZATION.md)
- Migration guide (English): [docs/migration.en.md](docs/migration.en.md)
- 迁移讲解（中文）: [docs/migration.zh-CN.md](docs/migration.zh-CN.md)

## Repository health

- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Notebook directory overview: [notebooks/README.md](notebooks/README.md)

## Project layout

```text
.
|-- .github/
|   |-- ISSUE_TEMPLATE/
|   `-- PULL_REQUEST_TEMPLATE.md
|-- BlazePose_tennis_shot_analysis.ipynb
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- docs/
|   |-- SANITIZATION.md
|   |-- guide.en.md
|   |-- guide.ja.md
|   |-- guide.zh-CN.md
|   |-- migration.en.md
|   `-- migration.zh-CN.md
|-- notebooks/
|   |-- README.md
|   `-- package_workflow_demo.ipynb
|-- scripts/
|   `-- run_demo.py
|-- src/
|   `-- tennis_shot_analysis/
|       |-- __init__.py
|       |-- __main__.py
|       |-- cli.py
|       |-- config.py
|       |-- data.py
|       |-- metrics.py
|       |-- pipeline.py
|       `-- visualize.py
|-- tests/
|   |-- test_metrics.py
|   `-- test_pipeline.py
|-- pyproject.toml
|-- README.md
|-- requirements-video.txt
`-- requirements.txt
```

## Quick start

On macOS with Python 3.10 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

Run the public synthetic demo:

```bash
tennis-shot-demo --no-show
```

Or with module mode:

```bash
python -m tennis_shot_analysis --no-show
```

## Optional real-video mode

```bash
python -m pip install -e '.[video]'
tennis-shot-demo --use-mediapipe-video --video-path your_clip.mp4
```

Recommended input:

- single-player clip
- stable camera view
- full body visible
- limited occlusion

## Landmark input contract

`compute_metrics()` requires at least two rows with numeric, finite values for
`time_s`, `hip_x`, `hip_y`, `shoulder_x`, `shoulder_y`, `wrist_x`, and `wrist_y`.
Timestamps must be strictly increasing. Irregular positive frame intervals are
supported; wrist speed uses the elapsed time between each pair of rows. The
video extractor omits frames whose selected landmarks are below the configured
visibility threshold.

The reported wrist speed uses normalized 2D image coordinates, and torso
rotation is a simple shoulder/hip coordinate difference. These are demo proxy
metrics, not calibrated physical measurements or scientifically validated
biomechanics.

## Privacy and open-source positioning

This project is sanitized for public sharing:

- no private videos are committed
- no personal, client, or internal identifiers are included
- default workflow uses deterministic synthetic data

See [docs/SANITIZATION.md](docs/SANITIZATION.md) before publishing updates.

## Notebook status

The original notebook is intentionally preserved as:

- a learning baseline
- a reference for migration from exploratory analysis to package architecture

The new notebook in `notebooks/` demonstrates how to consume the packaged code instead of duplicating logic inline.

## Validation

Run the project checks from the repository root:

```bash
pytest
python -m tennis_shot_analysis --no-show
```

## License

[BSD 2-Clause](LICENSE)
