# Metric card and measurement limits

## Intended use

Explore reproducible data processing, plotting, and simple motion signals from
one sequence of 2D image landmarks. Compare runs with matching coordinate/time
conventions. The synthetic sequence demonstrates engineering behavior; it is
not a ground-truth motion capture dataset or evidence of prediction accuracy.

## Definitions (unchanged in v0.4.0)

| Output | Definition | Interpretation |
| --- | --- | --- |
| `wrist_speed` | `hypot(x[t]-x[t-1], y[t]-y[t-1]) / (time[t]-time[t-1])` | Image-coordinate units per second; first row is 0 |
| `torso_rotation_proxy` | `shoulder_x - hip_x` | Horizontal landmark offset, not an angle |
| `impact_row` / `impact_frame` | First row attaining maximum wrist speed | Peak-motion indicator, not detected racket/ball contact |
| `impact_source_frame` | Source frame at that row if supplied | Nullable source identifier |
| `mean_torso_rotation_proxy` | Arithmetic mean of the row offsets | Unweighted by time intervals |

The video path selects the first returned pose and right wrist (16), right
shoulder (12), and right hip (24). It uses nominal reported FPS, not container
presentation timestamps. Low-visibility frames are omitted. Speed across a gap
therefore uses displacement over the full elapsed interval; it is not a
reconstruction of the missed motion or an instantaneous velocity estimate.

## Assumptions and failure modes

- Coordinates must share one image-coordinate convention; normalized x and y
  have different pixel scales when aspect ratio differs. No perspective,
  lens-distortion, body-size, or camera-motion correction is applied.
- 2D projection loses depth. Different views, crops, subjects, handedness,
  estimators, or frame rates can change results without a real motion change.
- Noise, occlusion, person switching, and missed frames can move the peak.
  A visibility threshold is not an uncertainty calibration.
- No model-based event labels, labeled evaluation set, accuracy score, 3D
  reconstruction, calibrated m/s, or clinically meaningful interpretation is
  provided. No model is trained by this project.

## Requirements before stronger claims

Introduce consented/licensed evaluation clips, independent event annotations,
a declared coordinate system, camera calibration where needed, and predefined
error metrics and confidence intervals. Evaluate across views and conditions,
include failure examples, and distinguish model errors from pipeline errors.
See the staged [roadmap](ROADMAP.md); never relabel the existing proxies as
validated physical measurements merely by renaming a field.
