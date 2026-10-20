# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2026-10-20

### Fixed

- Reject invalid landmark frames and timestamps before calculating motion metrics.
- Report clear errors for missing, nonnumeric, or non-finite landmark data.

## [0.2.0] - 2026-05-16

### Added

- Converted the repository from a notebook-only demo into a reusable Python package.
- Added CLI execution via `tennis-shot-demo` and `python -m tennis_shot_analysis`.
- Added tests for synthetic pipeline and metric validation.
- Added multilingual technical guides in English, Chinese, and Japanese.
- Added sanitization guidance for open-source publication.
- Added GitHub contribution and issue/PR templates.
- Added a new package-oriented notebook under `notebooks/`.
- Added a migration guide from notebook workflow to engineered project structure.

### Changed

- Rewrote the main README for portfolio-ready open-source presentation.
- Broadened packaging compatibility for local/offline-friendly setup.
- Expanded ignore rules for common Python build artifacts.

## [0.1.0] - 2026-05-16

### Added

- Initial public notebook demo using synthetic data with optional BlazePose video mode.
