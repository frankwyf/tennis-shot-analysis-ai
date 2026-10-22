# Upgrade roadmap

The goal is a maintainable open-source analysis tool with inspectable evidence.
A version number or more algorithms alone does not establish maturity. Each
stage below has a bounded outcome and a release gate.

## v0.4 — reliable open-source foundations (this release)

- Keep core installation independent of MediaPipe and avoid competing OpenCV packages.
- Reject ambiguous duplicate column labels consistently at CSV/API boundaries.
- Protect input/model files from CLI exports and require distinct output paths.
- Support batch execution without plotting imports, explicit installed version
  reporting, and reliable nested plot outputs with Figure cleanup on errors.
- Exercise Linux/macOS/Windows, current core libraries, and declared numerical
  dependency floors. Treat optional video as a separate gate.
- Build source/wheel artifacts, install the wheel in a clean CI environment,
  exercise its actual console script outside source, and publish checksums.
- Document contribution/review rules, support/security boundaries, input/output
  contracts, proxy definitions, and an external SSD workflow.

Release gate: regression tests, core and optional CI jobs, installed-wheel
smoke, package/tag consistency, and release checksum verification all pass.
Local optional video and real inference remain separate unverified capabilities
until demonstrated; a fake landmarker never counts as a model evaluation.

## v0.5 — reproducible runs and batch inputs (next priority)

Outcome: analyze a folder of canonical CSV sequences without manually running
one command per file, with recoverable per-sequence failures.

1. Design a versioned run manifest: package/dependency versions, sanitized
   configuration, source fingerprint, coordinate convention, and quality counts.
   Define privacy controls before storing hashes or filenames.
2. Add isolated output directories and atomic publication of a completed run
   bundle. Define overwrite/resume semantics explicitly.
3. Add batch CSV analysis with a deterministic ordering, per-input status, and
   a nonzero overall exit status when any requested input fails.
4. Add user-facing validation-only reports that can explain issues without
   silently dropping or repairing data.

Gate: repeated runs compare reproducibly; corrupt input cannot alter other
runs; interrupted writes do not present partial bundles as completed; a batch
with mixed valid/invalid sequences reports each outcome correctly.

## v0.6 — adapters and body-side generalization

Outcome: accept different pose estimators through explicit data adapters while
keeping the metric engine independent of MediaPipe.

1. Propose schema v2 with coordinate space/units, body side, source frame/PTS,
   estimator provenance, visibility/missingness conventions, and optional
   dimensions. Do not mix image coordinates and world coordinates implicitly.
2. Add a left/right selection with tests against asymmetric generated fixtures.
3. Introduce adapters only for formats with documented semantics and sample
   data that can legally ship with the project. A small protocol is enough;
   defer plugin discovery and external services until there are real consumers.
4. Preserve schema v1 ingestion and document migration; keep generic ingestion
   separate from tennis-specific interpretations.

Gate: adapters map equivalent input to equivalent canonical output, correctly
preserve frame identity and side, reject incompatible coordinate systems, and
leave the current proxy formulas unchanged unless separately evaluated.

## v0.7 — evaluated local video

Outcome: establish what the video path actually does on supported machines.

1. Complete binary-wheel installation and native codec/Tasks import checks on
   reference Apple Silicon hardware with acceptable download throughput.
2. With explicit model/asset authorization, evaluate a locally supplied model
   on generated inputs and consented/licensed public clips. Record model digest,
   license, settings, decoded frame count, timestamps, and expected failure modes.
3. Add a variable frame-rate PTS strategy before claiming support for it.
4. Create an opt-in, model-dependent validation suite separate from default CI;
   never put weights, private clips, camera permissions, or uploads in core CI.
5. Evaluate labeled peak/event timing with independent annotations. Report
   errors by camera view, visibility, and clip conditions; retain proxy labels.

Gate: a published evaluation protocol, reproducible asset instructions without
bundled private media, explicit licenses, independently defined expected results,
and measured failure cases. Passing imports alone is insufficient.

## 1.0 decision

Require stable public schemas/API and exit codes, documented deprecations,
platform support evidence, migration instructions, contributor/release ownership,
and installed-distribution gates that have remained reliable across releases.
Decide whether PyPI publication is useful only after package-name ownership and
trusted publishing are configured. Adopt an evaluation-backed scope statement;
1.0 need not promise biomechanics or coaching validity.

Priority is P0 correctness and input/output safety, P1 reproducibility and usable
interfaces, P2 evaluated generalization. Web services, live camera workflows,
training infrastructure, and LLM/chat features have no current requirement and
are outside this roadmap. Each milestone should be proposed as focused PRs
with its acceptance criteria before implementation.
