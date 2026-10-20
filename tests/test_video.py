import sys
import types
from dataclasses import dataclass
from pathlib import Path

import pytest

from tennis_shot_analysis.config import AnalysisConfig
from tennis_shot_analysis.data import extract_blazepose_landmarks


@dataclass
class FakeLandmark:
    x: float = 0.5
    y: float = 0.4
    visibility: float = 0.9


class FakeCapture:
    def __init__(self, fps=30.0, frames=3, opened=True):
        self.fps = fps
        self.frames = list(range(frames))
        self.opened = opened
        self.read_count = 0
        self.released = False

    def isOpened(self):
        return self.opened

    def get(self, _property):
        return self.fps

    def read(self):
        self.read_count += 1
        if not self.frames:
            return False, None
        return True, self.frames.pop(0)

    def release(self):
        self.released = True


class FakeLandmarker:
    def __init__(self, result_factory=None):
        self.timestamps = []
        self.result_factory = result_factory or (lambda _frame: [[FakeLandmark() for _ in range(25)]])

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def detect_for_video(self, image, timestamp_ms):
        self.timestamps.append(timestamp_ms)
        return types.SimpleNamespace(pose_landmarks=self.result_factory(image.data))


def _install_fake_video_modules(monkeypatch, capture, landmarker):
    cv2 = types.ModuleType("cv2")
    cv2.CAP_PROP_FPS = 5
    cv2.COLOR_BGR2RGB = 6
    cv2.VideoCapture = lambda _path: capture
    cv2.cvtColor = lambda frame, _conversion: frame

    mediapipe = types.ModuleType("mediapipe")
    mediapipe.ImageFormat = types.SimpleNamespace(SRGB="srgb")
    mediapipe.Image = lambda image_format, data: types.SimpleNamespace(
        image_format=image_format, data=data
    )

    tasks = types.ModuleType("mediapipe.tasks")
    python_api = types.ModuleType("mediapipe.tasks.python")
    vision = types.ModuleType("mediapipe.tasks.python.vision")
    python_api.BaseOptions = lambda model_asset_path: types.SimpleNamespace(
        model_asset_path=model_asset_path
    )
    vision.RunningMode = types.SimpleNamespace(VIDEO="video")
    vision.PoseLandmarkerOptions = lambda **kwargs: types.SimpleNamespace(**kwargs)
    vision.PoseLandmarker = types.SimpleNamespace(
        create_from_options=lambda _options: landmarker
    )
    tasks.python = python_api
    python_api.vision = vision

    monkeypatch.setitem(sys.modules, "cv2", cv2)
    monkeypatch.setitem(sys.modules, "mediapipe", mediapipe)
    monkeypatch.setitem(sys.modules, "mediapipe.tasks", tasks)
    monkeypatch.setitem(sys.modules, "mediapipe.tasks.python", python_api)
    monkeypatch.setitem(sys.modules, "mediapipe.tasks.python.vision", vision)


def _touch_video_and_model(tmp_path):
    video_path = tmp_path / "synthetic.mp4"
    model_path = tmp_path / "pose_landmarker.task"
    video_path.touch()
    model_path.touch()
    return video_path, model_path


def test_video_extraction_uses_tasks_timestamps_and_releases_capture(tmp_path, monkeypatch):
    video_path, model_path = _touch_video_and_model(tmp_path)
    capture = FakeCapture(fps=30.0, frames=3)
    landmarker = FakeLandmarker()
    _install_fake_video_modules(monkeypatch, capture, landmarker)

    landmarks = extract_blazepose_landmarks(video_path, model_path)

    assert landmarks["frame"].tolist() == [0, 1, 2]
    assert landmarks["time_s"].tolist() == pytest.approx([0.0, 1 / 30, 2 / 30])
    assert landmarker.timestamps == [0, 33, 67]
    assert capture.released


def test_video_extraction_limits_frames_and_keeps_task_timestamps_increasing(
    tmp_path, monkeypatch
):
    video_path, model_path = _touch_video_and_model(tmp_path)
    capture = FakeCapture(fps=2000.0, frames=4)
    landmarker = FakeLandmarker()
    _install_fake_video_modules(monkeypatch, capture, landmarker)

    landmarks = extract_blazepose_landmarks(video_path, model_path, max_frames=3)

    assert len(landmarks) == 3
    assert landmarker.timestamps == [0, 1, 2]
    assert capture.read_count == 3
    assert capture.released


@pytest.mark.parametrize("fps", [0, float("nan"), float("inf"), -30])
def test_video_extraction_rejects_invalid_fps_and_releases_capture(
    tmp_path, monkeypatch, fps
):
    video_path, model_path = _touch_video_and_model(tmp_path)
    capture = FakeCapture(fps=fps)
    _install_fake_video_modules(monkeypatch, capture, FakeLandmarker())

    with pytest.raises(ValueError, match="invalid frame rate"):
        extract_blazepose_landmarks(video_path, model_path)

    assert capture.released


def test_video_extraction_skips_low_visibility_frames(tmp_path, monkeypatch):
    video_path, model_path = _touch_video_and_model(tmp_path)
    capture = FakeCapture(fps=25.0, frames=2)

    def result_factory(frame):
        landmarks = [FakeLandmark() for _ in range(25)]
        if frame == 0:
            landmarks[16].visibility = 0.1
        return [landmarks]

    landmarker = FakeLandmarker(result_factory)
    _install_fake_video_modules(monkeypatch, capture, landmarker)

    landmarks = extract_blazepose_landmarks(video_path, model_path, min_visibility=0.5)

    assert landmarks["frame"].tolist() == [1]
    assert capture.released


def test_video_extraction_errors_when_no_usable_pose_is_found(tmp_path, monkeypatch):
    video_path, model_path = _touch_video_and_model(tmp_path)
    capture = FakeCapture(fps=25.0, frames=2)
    landmarker = FakeLandmarker(lambda _frame: [])
    _install_fake_video_modules(monkeypatch, capture, landmarker)

    with pytest.raises(ValueError, match="No valid pose frames were extracted"):
        extract_blazepose_landmarks(video_path, model_path)

    assert capture.released


def test_video_extraction_reports_unreadable_video(tmp_path, monkeypatch):
    video_path, model_path = _touch_video_and_model(tmp_path)
    capture = FakeCapture(opened=False)
    _install_fake_video_modules(monkeypatch, capture, FakeLandmarker())

    with pytest.raises(ValueError, match="Could not open video file"):
        extract_blazepose_landmarks(video_path, model_path)

    assert capture.released


def test_video_extraction_rejects_missing_model_before_importing_optional_dependencies(
    tmp_path
):
    video_path = tmp_path / "synthetic.mp4"
    video_path.touch()

    with pytest.raises(FileNotFoundError, match="pose model file not found"):
        extract_blazepose_landmarks(video_path, tmp_path / "missing.task")

    with pytest.raises(ValueError, match="pose_model_path is required"):
        extract_blazepose_landmarks(video_path, None)


def test_video_config_requires_explicit_model_path(tmp_path):
    with pytest.raises(ValueError, match="pose_model_path is required"):
        AnalysisConfig(source="video", input_path=tmp_path / "video.mp4")

    config = AnalysisConfig(
        source="video",
        input_path=tmp_path / "video.mp4",
        pose_model_path=tmp_path / "pose.task",
    )
    assert config.pose_model_path == Path(tmp_path / "pose.task")
