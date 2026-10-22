# Security policy

## Supported versions

Only the latest patch release in the 0.4.x series receives fixes in place.
Older releases remain available for reproducibility; upgrade before reporting
an already-fixed issue. Support follows the latest minor release as the
project evolves. There is no security response-time guarantee.

## Reporting

For a vulnerability, use GitHub's private vulnerability reporting if the
repository offers **Security → Report a vulnerability**. Availability depends
on repository settings; this document does not enable that feature. Otherwise,
use a private contact method listed on the
[maintainer's profile](https://github.com/frankwyf). If none is available, open
a minimal issue requesting private contact without exploit details, credentials,
private video, or personal information. Ordinary correctness bugs can use the
public bug template with synthetic inputs.

Include the affected version, OS/Python, a minimal generated reproduction, and
the expected security impact. Do not upload sensitive assets to demonstrate it.

## Processing boundary

Video and CSV are untrusted inputs. Dependencies such as video decoders and
MediaPipe have their own security and telemetry behavior. Use trusted package
sources and model files, and process only data you are authorized to use. This
application does not isolate or sandbox native decoders. The project itself
does not download model weights or upload input assets.

Development and release workflows use read-only permissions except for the
job publishing a GitHub release. Actions are pinned to commits and reviewed
through dependency update PRs. Release checksums detect accidental artifact
changes; they are not independent signatures or a substitute for trusted
provenance. PyPI publishing is not configured.
