# Tennis Shot Analysis AI

BlazePose-oriented tennis motion-analysis workflow intended for notebook-based
experimentation in Google Colab or a local Jupyter environment.

## Current status

The repository contains a minimal public notebook that demonstrates a complete
pose-analysis workflow on **synthetic landmark data**.

It is:

- runnable as-is in a local Jupyter environment or Google Colab
- safe to publish without private video assets
- easy to extend with real BlazePose inference

## Quick start

```bash
# (optional) create a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux

pip install jupyter ipykernel mediapipe
jupyter notebook BlazePose_tennis_shot_analysis.ipynb
```

## Intended workflow

1. Open the notebook in Jupyter or Google Colab.
2. Run the synthetic demo cells to understand the public workflow.
3. To enable real-video inference, install the optional dependencies:

   ```bash
   pip install mediapipe>=0.10.14
   ```

4. Set `USE_MEDIAPIPE_VIDEO = True` in the notebook and point `VIDEO_PATH` to
   a local or Colab-accessible tennis clip.
5. Use a single-player MOV or MP4 clip for real experiments.
6. Prefer a stable camera angle with the full body visible.

## Video preparation guidelines

- Keep videos reasonably short.
- Use one clearly visible subject when possible.
- Prefer MOV or MP4 input.
- Avoid severe occlusion and unstable viewpoints.
- Higher frame rates help with fast actions such as serves.

## License

[BSD 2-Clause](LICENSE)
