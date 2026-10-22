# Governance

This project is maintained by [frankwyf](https://github.com/frankwyf). It is an
alpha research/engineering tool with no promise of scientific validity or an
operational support service.

Changes normally arrive through pull requests. The maintainer decides scope,
reviews compatibility and evidence, and merges after CI passes. Changes to
public input schemas, metric meanings, dependencies, or model behavior should
first explain the problem and acceptance criteria in an issue or PR. Community
feedback informs the decision; there is currently no steering committee.

A version tag identifies a release from reviewed `master` history. Published
tags and artifacts are not moved or replaced to hide failures; corrections
ship as a new patch release. See [RELEASING.md](docs/RELEASING.md).

During 0.x, preserve existing APIs where practical, retain documented aliases,
and explain incompatible behavior in the changelog. Current safety changes
may reject inputs or file combinations that previously caused ambiguous
results. A future 1.0 requires the gates in [ROADMAP.md](docs/ROADMAP.md).

Maintainers and contributors follow the conduct expectations in
[CONTRIBUTING.md](CONTRIBUTING.md). Ownership and review rules can evolve through
an ordinary public PR. No contributor is required to share personal videos or
purchase hardware or services to participate.
