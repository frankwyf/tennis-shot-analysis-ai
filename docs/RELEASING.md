# Release procedure

Releases are GitHub Releases with a wheel, source distribution, and `SHA256SUMS`.
PyPI publishing is not configured. Use the repository's project-local environment;
on macOS configure [external SSD storage](MACOS.md) before installing or building.

## Prepare a release PR

1. Check current `master` and preserve unrelated local changes.
2. Update `project.version` in `pyproject.toml`, the dated changelog, supported
   version policy, docs/examples, and any compatibility notes.
3. Run regression tests, `pip check`, the headless synthetic CLI, and build
   source/wheel distributions. Review the whole diff and generated metadata.
4. Install the wheel into an environment and execute
   `scripts/check_distribution.py` with the expected version and an explicitly
   chosen output directory. It rejects editable/source imports and verifies
   version, license metadata, console entry point, JSON/CSV, and a saved figure.
5. Open the PR, wait for every CI job (including minimum dependencies, Windows,
   macOS optional video, and clean-wheel validation), then merge.

For the local SSD reference machine, reuse `<repo>/.venv`; do not create another
project environment on the internal disk. Build to `artifacts/.../dist`, install
the wheel with `--no-deps` into the existing environment, run the verification
from a non-source working directory, then restore the editable install. CI uses
a fresh environment on the disposable hosted runner to test dependency resolution.

Example after configuring environment/cache paths:

```bash
python -m build --no-isolation --outdir artifacts/release/dist
python -m pip install --force-reinstall --no-deps artifacts/release/dist/*.whl
python scripts/check_distribution.py --expected-version 0.4.0 --work-dir artifacts/release/wheel-smoke
python -m pip install --no-deps --no-build-isolation -e .
```

`--no-isolation` is for a prepared local environment with the declared build
requirements already installed. CI uses normal isolated builds. Rebuild local
metadata after a version change: stale ignored `src/*.egg-info` can otherwise
shadow installed metadata when running directly from source.

## Tag and monitor

After the merge and its `master` CI complete successfully:

```bash
git switch master
git pull --ff-only origin master
git tag -a v0.4.0 -m "v0.4.0"
git push origin v0.4.0
```

The release workflow verifies the tag/version and ancestry in `master`, runs
core tests and a headless demo, builds distributions, verifies the installed
wheel in a clean environment, and generates SHA-256 checksums. Only then does
a separate job with `contents: write` check the downloaded checksums and create
the release with its attachments.

Confirm the workflow conclusion, published tag target, wheel/source names,
checksums attachment, and download links. The optional CI smoke uses fake
inference; release notes must not claim real-model evaluation from that result.

On a pre-publication infrastructure failure, inspect logs before retrying.
Never move published tags or overwrite published assets. A defective published
release requires a new patch version and a documented correction. If a tag
cannot pass its checks, fix through a PR and use a new version/tag. Keep failed
workflow history so the cause and resolution remain visible.

## Verify a download

Place the release files and `SHA256SUMS` in one directory, then run:

```bash
# macOS
shasum -a 256 -c SHA256SUMS
# Linux
sha256sum --check SHA256SUMS
```

A checksum verifies content integrity relative to the published checksum list;
it does not authenticate a compromised publisher. Action references are pinned
to reviewed commits; Dependabot proposes updates through PRs.
