# v0.4.0 validation record

Recorded 2026-10-22. This page records **local** evidence; live hosted CI results
are on [GitHub Actions](https://github.com/frankwyf/tennis-shot-analysis-ai/actions).
Release validation runs again on the tagged commit before publication.

## Reference environment

- macOS 27.0.1 (26A434), Apple Silicon `arm64`, CPython 3.12.9.
- Repository and existing `.venv` on a mounted APFS external SSD, about 1.5 TiB free.
- `diskutil info` could not access DiskManagement in the execution environment.
  `mount`, `df`, and a physical device check confirmed the external mount and
  that the repository, `.venv`, cache and temporary directories were on it.
- All pip/uv, XDG, temporary, Matplotlib, and model-cache environment variables
  were redirected and checked in the executing process. No global installation,
  architecture emulation, camera, model download, or private video was used.
- NumPy 2.5.4, pandas 3.0.6, Matplotlib 3.11.2, pytest 9.1.1,
  build 1.6.1, setuptools 84.2.0, wheel 0.48.0.
- Full core/dev/release version snapshot: [reference constraints](../constraints/reference-py312-macos-arm64.txt).
  It describes this environment, not a portable lock file.

## Before and after

The original suite produced **48 passed, 1 skipped**. Before fixes, new tests
reproduced input-file overwrites, output-path collisions, figure directory/error
handling, leaked figures after failed saves, and ambiguous duplicate columns.
New feature checks also failed before version/no-plot support was implemented.
A follow-up CSV test reproduced duplicate-header detection being bypassed by a
leading whitespace-only line; this was corrected to match pandas' blank-line
handling while retaining quoted-header parsing.

The final full suite produced **67 passed, 1 skipped**, exit **0**. The skipped
case is `test_local_video_backend_and_mediapipe_tasks_integration`, because
`cv2` is not installed locally. Existing timestamp, visibility and capture
release tests remain unchanged.

The core requirements resolver probe previously requested MediaPipe despite
being a default install path. After removing optional packages from that file,
the same offline dry run succeeds using the installed core dependencies.
A stale ignored source `.egg-info` reported an older version during the first
local run; rebuilding the distribution regenerated that metadata. No runtime
version is hardcoded separately from the installed distribution.

## Commands and results

The following used the existing SSD `.venv`, configured as in [MACOS.md](MACOS.md).
`VALIDATION` denotes an ignored directory under the external checkout's
`artifacts/`; exact local device names and personal paths are omitted here.

| Command | Exit / result |
| --- | --- |
| `python -m pip install --no-deps --no-build-isolation --disable-pip-version-check -e .` | 0; reuse installed build/runtime dependencies |
| `python -m pip check` | 0; no broken requirements |
| `python -m pip install --dry-run --no-index --no-build-isolation --disable-pip-version-check -r requirements.txt` | 0 after fix; no video dependency requested |
| `python -m pytest -q --tb=short --junitxml="$VALIDATION/tests.xml" -o cache_dir="$VALIDATION/pytest-cache" --basetemp "$VALIDATION/regression-final"` | 0; 67 passed, 1 skipped |
| `python -m tennis_shot_analysis --no-plot --save-summary "$VALIDATION/batch/summary.json" --save-landmarks "$VALIDATION/batch/landmarks.csv"` | 0; finite deterministic summary/CSV |
| `python -m tennis_shot_analysis --no-show --save-figure "$VALIDATION/synthetic/figures/analysis.png" --save-summary "$VALIDATION/synthetic/summary.json" --save-landmarks "$VALIDATION/synthetic/landmarks.csv"` | 0; nested PNG and exports created |
| `python -m build --no-isolation --outdir "$VALIDATION/dist"` | 0; sdist and wheel built |
| `python -m pip install --force-reinstall --no-deps "$VALIDATION/dist/tennis_shot_analysis_ai-0.4.0-py3-none-any.whl"` | 0; installed into existing `.venv` |
| `python scripts/check_distribution.py --expected-version 0.4.0 --work-dir "$VALIDATION/installed-smoke"` | 0; verified actual site-packages import, entry point, metadata, CSV, JSON, PNG |
| Restore editable install, then `python -m pip check` | 0; development environment restored |

Reference synthetic result: 80 rows, peak row/source frame 40,
`impact_time_s=0.810126582278481`,
`peak_wrist_speed_norm_units=0.7876575702903655`,
`mean_torso_rotation_proxy=0.003892753916799873`.

## Video evidence boundaries

| Capability | Local Apple Silicon result | Hosted optional CI gate |
| --- | --- | --- |
| Native optional package installation | Not completed; previous downloads stopped for low throughput | Install `.[dev,video]` and run `pip check` |
| OpenCV synthetic video encode/decode | Unverified locally | Real MJPG writer/capture |
| MediaPipe Tasks import | Unverified locally | Required real API import before tests |
| Actual pose-model inference | Unverified; no project-supplied model present | Not tested; FakeLandmarker only |

These are separate claims. Successful core tests or codec/API checks do not
establish pose-model correctness, event-detection accuracy, or real biomechanics.
See the [metric card](METRICS.md) and [next validation stage](ROADMAP.md).
