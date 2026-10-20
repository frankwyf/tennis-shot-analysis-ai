from types import SimpleNamespace

import pytest
import numpy as np

from tennis_shot_analysis.data import extract_blazepose_landmarks


def test_local_video_backend_and_mediapipe_tasks_integration(tmp_path, monkeypatch):
    cv2 = pytest.importorskip("cv2", reason="Install the video extra to run this integration check")
    mp = pytest.importorskip(
        "mediapipe", reason="Install the video extra to run this integration check"
    )
    from mediapipe.tasks.python import vision

    video_path = tmp_path / "generated-smoke-video.avi"
    model_path = tmp_path / "test-only-empty-model.task"
    model_path.touch()

    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        30.0,
        (64, 48),
    )
    assert writer.isOpened(), "OpenCV could not create a small synthetic smoke-test video"
    for frame_number in range(3):
        writer.write(np.full((48, 64, 3), frame_number * 40, dtype=np.uint8))
    writer.release()

    real_video_capture = cv2.VideoCapture
    captures = []

    def record_capture(path):
        capture = real_video_capture(path)
        captures.append(capture)
        return capture

    monkeypatch.setattr(cv2, "VideoCapture", record_capture)

    class FakeLandmarker:
        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def detect_for_video(self, image, timestamp_ms):
            assert image.image_format == mp.ImageFormat.SRGB
            assert isinstance(timestamp_ms, int)
            landmarks = [SimpleNamespace(x=0.5, y=0.4, visibility=0.9) for _ in range(25)]
            return SimpleNamespace(pose_landmarks=[landmarks])

    class FakePoseLandmarker:
        @staticmethod
        def create_from_options(options):
            assert options.running_mode == vision.RunningMode.VIDEO
            return FakeLandmarker()

    monkeypatch.setattr(vision, "PoseLandmarker", FakePoseLandmarker)

    landmarks = extract_blazepose_landmarks(video_path, model_path)

    assert landmarks["frame"].tolist() == [0, 1, 2]
    assert landmarks["time_s"].tolist() == pytest.approx([0.0, 1 / 30, 2 / 30], abs=0.002)
    assert captures and not captures[0].isOpened()
