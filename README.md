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
|-- examples/
|   |-- README.md
|   `-- package_workflow_demo.ipynb
|-- tools/
|   `-- run_demo.py
|-- src/tennis_shot_analysis/
|   |-- __init__.py
|   |-- __main__.py
|   |-- cli.py
|   |-- config.py
|   |-- data.py
|   |-- metrics.py
|   |-- pipeline.py
|   `-- visualize.py
|-- tests/
|   |-- test_metrics.py
|   `-- test_pipeline.py
|-- pyproject.toml
|-- README.md
|-- requirements-video.txt
`-- requirements.txt
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
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
pip install -e .[video]
tennis-shot-demo --use-mediapipe-video --video-path your_clip.mp4
```

Recommended input:

- single-player clip
- stable camera view
- full body visible
- limited occlusion

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

## Validation status

Validated locally in the repository virtual environment on 2026-05-16:

- `pip install -e .[dev]`
- `pytest`
- `python -m tennis_shot_analysis --no-show`

## Screenshots

Here are some screenshots to showcase the project:

### CLI Output
![CLI Output](docs/images/cli_output.png)

### Notebook Visualization
![Notebook Visualization](docs/images/notebook_visualization.png)

### Project Structure
![Project Structure](docs/images/project_structure.png)

## License

[BSD 2-Clause](LICENSE)
