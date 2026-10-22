# Contributing

Focused bug fixes, documentation, platform reports, and data-adapter proposals
are welcome. Keep the synthetic path usable without optional video dependencies.
Read [governance](GOVERNANCE.md) and the [roadmap](docs/ROADMAP.md) before proposing
large features. Describe the user problem and a measurable acceptance criterion.

## Environment

Use a project-local `.venv`. On macOS with an external SSD, first follow
[the storage checklist](docs/MACOS.md); environments, downloads, temporary files,
plots, and model caches must stay on that SSD. Never install project packages
globally or replace the system Python.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,release]'
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev,release]'
```

Optional video dependencies are installed only with `.[video]`, or
`.[dev,video]` for its tests. Inspect binary wheel compatibility and download
size first. Do not install multiple OpenCV distributions; they all own `cv2`.
The maintainer's tested core reference snapshot is
`constraints/reference-py312-macos-arm64.txt`; it is a version snapshot, not a
portable lock file or a security guarantee. The separate minimum constraints
file probes the supported dependency floors in CI.

## A focused change

1. Branch from current `master`; preserve other people's uncommitted changes.
2. Reproduce a bug before fixing it. Add behavior tests with independent
   expectations, not copies of the implementation.
3. Run `python -m pytest` and `python -m pip check`.
4. Exercise the changed CLI/API path. Keep examples and docs in sync.
5. Open a PR explaining the trigger, resulting behavior, validation, and limits.
6. Wait for every applicable CI job before merging. Do not tag a failing commit.

Fast local checks:

```bash
python -m pytest
python -m tennis_shot_analysis --no-plot --save-summary artifacts/summary.json
python -m tennis_shot_analysis --no-show --save-figure artifacts/figures/analysis.png
python -m pip check
```

`tests/test_video.py` uses fake dependencies. `tests/test_video_runtime.py` needs
the optional packages and real OpenCV codecs, but substitutes fake inference.
It skips when optional modules are unavailable; the optional CI job separately
requires successful imports so that missing dependencies cannot silently pass.
Neither test suite needs a camera, a real model, or a person's video.

## Compatibility and science

Preserve the existing 2D proxy definitions and JSON schema unless a change is
explicitly versioned and documented. Do not call peak wrist motion a measured
ball-contact event. Explain coordinate conventions, missing data, and validation
limits for new adapters. Propose schema changes before adding new coordinate
systems or left/right body selection.

Prefer readable Python and small modules over plugin frameworks. Notebook
learning references should continue to work with the public API. Maintainers
release only the latest supported 0.x minor line; consult [SECURITY.md](SECURITY.md).

## Public data and conduct

Use generated or explicitly licensed public test data. Do not commit videos,
models, credentials, personal identifiers, or internal datasets. Redact absolute
paths and secrets from logs. Review [SANITIZATION.md](docs/SANITIZATION.md).

Discuss ideas respectfully, give reproducible feedback, and avoid harassment,
personal attacks, discrimination, or publishing other people's private data.
The maintainer may remove harmful content and limit participation. Contact the
repository owner through an available private contact method on their
[GitHub profile](https://github.com/frankwyf) for conduct concerns; request a
private channel without sensitive details if one is unavailable.
