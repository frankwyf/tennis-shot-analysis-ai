# macOS and external SSD development

Use an already installed native Python (3.12 is the reference), and keep this
checkout, its `.venv`, downloads, temporary files, outputs, and model caches on
your chosen external SSD. Do not use global pip installs or an internal-disk
fallback. The core pipeline does not need MediaPipe, OpenCV, a camera, or models.

## Verify before installation

From the checkout on the external volume:

```bash
pwd -P
sw_vers
uname -m
python3 --version
diskutil info /Volumes/YOUR_SSD
mount
df -h / /Volumes/YOUR_SSD
git status --short --branch
```

Confirm the actual backing device and mount, not just the directory name. Check
that `.venv` is physically on that device. If the volume is absent or paths
resolve to internal storage, stop. If `diskutil` cannot access DiskManagement
in a restricted execution environment, record that limitation and inspect the
actual mount/device and filesystem with `mount` and `df`; never assume success.

## Redirect the executing process's caches

Edit the volume name below only after confirming the SSD is mounted. Set these
in the same shell that will run pip, Python, tests, and builds:

```bash
export TENNIS_DEV_STORAGE="/Volumes/YOUR_SSD/development-storage"
export UV_CACHE_DIR="$TENNIS_DEV_STORAGE/uv/cache"
export UV_PYTHON_INSTALL_DIR="$TENNIS_DEV_STORAGE/uv/python"
export UV_PYTHON_BIN_DIR="$TENNIS_DEV_STORAGE/uv/python-bin"
export UV_TOOL_DIR="$TENNIS_DEV_STORAGE/uv/tools"
export UV_TOOL_BIN_DIR="$TENNIS_DEV_STORAGE/uv/tool-bin"
export PIP_CACHE_DIR="$TENNIS_DEV_STORAGE/pip"
export XDG_CACHE_HOME="$TENNIS_DEV_STORAGE/xdg/cache"
export XDG_DATA_HOME="$TENNIS_DEV_STORAGE/xdg/data"
export TMPDIR="$TENNIS_DEV_STORAGE/tmp/tennis-shot-analysis-ai"
export HF_HOME="$TENNIS_DEV_STORAGE/models/huggingface"
export TORCH_HOME="$TENNIS_DEV_STORAGE/models/torch"
export MPLCONFIGDIR="$TENNIS_DEV_STORAGE/matplotlib"
export PLAYWRIGHT_BROWSERS_PATH="$TENNIS_DEV_STORAGE/playwright"
export MPLBACKEND=Agg
mkdir -p "$UV_CACHE_DIR" "$UV_PYTHON_INSTALL_DIR" "$UV_PYTHON_BIN_DIR" \
  "$UV_TOOL_DIR" "$UV_TOOL_BIN_DIR" "$PIP_CACHE_DIR" "$XDG_CACHE_HOME" \
  "$XDG_DATA_HOME" "$TMPDIR" "$HF_HOME" "$TORCH_HOME" \
  "$MPLCONFIGDIR" "$PLAYWRIGHT_BROWSERS_PATH"
```

Use `df -h` on every resulting path and the repository `.venv` to verify they
share the external device before proceeding. Reuse existing tools; do not
install Rosetta, replace Python, or add global toolchains to bypass a wheel
compatibility issue. macOS and existing applications may still write small
system caches outside these controls.

## Core validation and storage accounting

```bash
python3 -m venv .venv  # only if absent, inside the external checkout
source .venv/bin/activate
python -m pip install -e '.[dev,release]'
python -m pip check
python -m pytest --basetemp artifacts/pytest-tmp -o cache_dir=artifacts/pytest-cache
python -m tennis_shot_analysis --no-plot --save-summary artifacts/summary.json
du -sh . .venv artifacts "$TENNIS_DEV_STORAGE"
df -h / /Volumes/YOUR_SSD
```

Keep outputs in ignored `artifacts/`; use a dedicated work directory for each
validation. Review before cleaning anything. Shared caches may serve other
projects and must not be deleted automatically.

## Optional video validation

Inspect wheel tags with `python -m pip debug --verbose` and estimate download
size from package metadata before installing. A binary-only resolver probe is:

```bash
python -m pip install --dry-run --only-binary=:all: 'mediapipe>=0.10.21,<2'
```

A dry run can still download metadata/wheels and prepare build metadata; it
must use the same external cache/temp configuration. Once compatible downloads
are acceptable, install `.[video]`, run `pip check`, import `cv2` and
`mediapipe.tasks.python.vision`, and run `tests/test_video_runtime.py`. This
writes/reads a tiny generated MJPG video with fake inference. Do not download
models or use personal footage for this check. Record slow or failed downloads
and stop that step rather than silently changing storage or architecture.

If a compatible model is explicitly supplied for this project, a separate
opt-in test can evaluate it locally without copying/uploading it. Always report
package installation, codec operations, Tasks imports, and actual inference as
four separate outcomes. See [validation evidence](VALIDATION.md).
