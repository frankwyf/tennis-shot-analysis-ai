"""Verify an installed wheel without pytest or imports from the source checkout.

Run using the Python interpreter where the wheel was installed. The caller
chooses the work directory so generated CSV, JSON, and PNG stay on its disk.
"""

import argparse
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

import tennis_shot_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    work_dir = args.work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    distribution = importlib.metadata.distribution("tennis-shot-analysis-ai")
    assert distribution.version == args.expected_version, distribution.version
    assert tennis_shot_analysis.__version__ == args.expected_version
    package_file = Path(tennis_shot_analysis.__file__).resolve()
    assert any(str(file) == "tennis_shot_analysis/__init__.py" for file in distribution.files or [])
    assert package_file == distribution.locate_file("tennis_shot_analysis/__init__.py").resolve(), package_file
    assert distribution.metadata["License-Expression"] == "BSD-2-Clause"

    executable = shutil.which("tennis-shot-demo", path=str(Path(sys.executable).parent))
    assert executable, "Installed console entry point not found next to Python"
    environment = {**os.environ, "MPLBACKEND": "Agg", "PYTHONPATH": ""}
    for command in ([sys.executable, "-m", "tennis_shot_analysis"], [executable]):
        version = subprocess.run(
            [*command, "--version"], cwd=work_dir, env=environment,
            text=True, capture_output=True, check=True, timeout=60,
        )
        assert args.expected_version in version.stdout, version.stdout

    subprocess.run(
        [executable, "--no-plot", "--save-landmarks", "landmarks.csv", "--save-summary", "summary.json"],
        cwd=work_dir, env=environment, check=True, timeout=60,
    )
    document = json.loads((work_dir / "summary.json").read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    assert document["source"] == "synthetic"
    assert document["summary"]["frame_count"] == 80
    assert all(math.isfinite(value) for value in document["summary"].values() if value is not None)
    subprocess.run(
        [executable, "--source", "csv", "--input", "landmarks.csv", "--no-show",
         "--save-figure", "figures/analysis.png"],
        cwd=work_dir, env=environment, check=True, timeout=60,
    )
    assert (work_dir / "figures" / "analysis.png").read_bytes().startswith(b"\x89PNG")
    print(f"Installed wheel verified: {distribution.version} at {package_file}")


if __name__ == "__main__":
    main()
