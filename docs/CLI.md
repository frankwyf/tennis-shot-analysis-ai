# API, CLI, and output contracts

## Python API

```python
from tennis_shot_analysis import AnalysisConfig, AnalysisSummary, analyze_landmarks, run_analysis, __version__

enriched, summary, label = run_analysis(AnalysisConfig(frame_count=80, duration_s=1.6))
# Or: enriched, summary = analyze_landmarks(a_pandas_dataframe)
print(summary.to_dict())
```

`analyze_landmarks` validates one sequence and returns a copied DataFrame with
`wrist_speed` and `torso_rotation_proxy` plus an `AnalysisSummary`. It does not
modify the input. `run_analysis` loads the configured source before calling
the same metric path. Required columns, time ordering, and frame numbering are
described in the [README](../README.md#bring-your-landmarks).

Column labels must be unique. The CSV loader checks the original header before
pandas can silently rename duplicate labels. Finite coordinates outside [0, 1]
are accepted (e.g. off-image landmarks); callers must keep a consistent
coordinate convention. No automatic interpolation or smoothing is performed.

`__version__` comes from the installed distribution metadata. Install the
package before using it; an unpackaged source import returns `0+unknown` if no
installed metadata exists. Regenerate build metadata after changing the version.

## CLI

Both `tennis-shot-demo` and `python -m tennis_shot_analysis` use the same parser.
Run `--help` for all options and `--version` for the installed version.

| Option | Behavior |
| --- | --- |
| `--source synthetic` | Default generated input, no model or video needed |
| `--source csv --input PATH` | Canonical landmark CSV |
| `--source video --input PATH --pose-model PATH` | Optional Tasks path with local assets |
| `--no-plot` | Skip plot creation and Matplotlib imports entirely |
| `--no-show` | Render with the Agg backend without a GUI window |
| `--save-landmarks PATH` | Enriched CSV, no DataFrame index column |
| `--save-summary PATH` | Full precision JSON, schema version 1 |
| `--save-figure PATH` | Save a plot, creating parent directories |

`--no-plot` cannot be combined with `--save-figure`. `--no-show` can save a
figure and is the choice for headless rendering. Matplotlib remains a core
installation dependency for backward compatibility, even when no plot is used.
Legacy video flags remain documented aliases; a local pose model is still required.

Exit code **0** means success (including help/version). Exit code **2** means
an invalid argument, invalid input, missing optional dependency, or expected
file/plot error, reported without a traceback. Unexpected programming failures
retain a traceback. Standard output is a human-readable table; scripts should
consume `--save-summary`, not parse the rounded table.

Output files must be distinct and cannot alias any input/model through relative
paths, symlinks, or hardlinks. This is checked before analysis or output writes.
Other existing output files can be overwritten. Exports are individual file
writes, not a multi-file transaction: a later failure can leave earlier exports.
Use a fresh output directory per run and avoid concurrent writers to the same
paths. Atomic run bundles and explicit resume semantics are roadmap work.

## JSON schema version 1

```json
{
  "schema_version": 1,
  "source": "synthetic",
  "data_source_label": "Synthetic demo sequence",
  "summary": {
    "frame_count": 80,
    "impact_row": 40,
    "impact_frame": 40,
    "impact_source_frame": 40,
    "impact_time_s": 0.810126582278481,
    "peak_wrist_speed_norm_units": 0.7876575702903655,
    "mean_torso_rotation_proxy": 0.003892753916799873
  }
}
```

Numbers above are from the reference synthetic run; small floating-point
differences across environments are possible.
`impact_frame` is the compatibility alias of zero-based **analyzed row position**
`impact_row`. `impact_source_frame` is an integer source frame, or `null` when
there was no `frame` column. Gaps in source frames do not change row positions.
Consumers must check `schema_version`; a structural breaking change requires
a schema increment. Future optional keys should not break tolerant readers.
No timestamp or machine-specific absolute path is embedded in synthetic exports,
so repeated runs in a fixed environment remain comparable.
