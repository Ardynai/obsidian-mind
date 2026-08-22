"""On-device video pose lane: VideoProcessor pattern + MediaPipe mapping.

Deps-free: sandbox processor, landmark mapping, consent rails, and fusion.
Extra-only MediaPipe/OpenCV tests skip cleanly when the video extra is absent.
"""

from __future__ import annotations

import ast
import os
import tempfile
import unittest
from pathlib import Path

from somatic.consent import ANALYSIS_INSIGHT, DATA_INGESTION, ConsentLedger
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.sensors.field import LIVE_CAMERA_DISCLAIMER, field_snapshot
from somatic.sensors.fusion import fuse_rf_vision
from somatic.sensors.live_consent import LiveSensorConsent, load_live_consent, save_live_consent
from somatic.sensors.live_video import (
    LiveVideoAdapter,
    LiveVideoIngest,
    replace_video_ingest,
    require_live_video,
)
from somatic.sensors.roster import scan_sensor
from somatic.sensors.video_pose import (
    landmarks_to_joints,
    mediapipe_available,
    video_extra_status,
)
from somatic.sensors.video_processor import (
    FORBIDDEN_FRAME_KEYS,
    VideoProcessor,
    sandbox_pose_features,
    strip_frame_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VIDEO_MODULES = (
    REPO_ROOT / "somatic" / "sensors" / "video_processor.py",
    REPO_ROOT / "somatic" / "sensors" / "video_pose.py",
    REPO_ROOT / "somatic" / "sensors" / "live_video.py",
)
BANNED_TOP_LEVEL = {"mediapipe", "cv2", "ultralytics", "YOLO", "yolo"}


def _isolate() -> object:
    tmp = tempfile.TemporaryDirectory()
    keys = (
        "SOMATIC_CONSENT_PATH",
        "SOMATIC_SENSOR_LIVE_PATH",
    )
    previous = {key: os.environ.get(key) for key in keys}

    def restore() -> None:
        replace_video_ingest(None, modality="video")
        replace_video_ingest(None, modality="video3d")
        tmp.cleanup()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    root = Path(tmp.name)
    os.environ["SOMATIC_CONSENT_PATH"] = str(root / "consent.json")
    os.environ["SOMATIC_SENSOR_LIVE_PATH"] = str(root / "sensor-live.json")
    return restore


class _FakePoseExtractor:
    def extract(self, frame: object) -> dict[str, object]:
        del frame
        return {
            "confidence": 0.71,
            "pose3d": {
                "origin": "mediapipe-pose",
                "simulated": False,
                "joints": {
                    "head": [0.51, 0.11, 0.20],
                    "torso": [0.50, 0.40, 0.08],
                    "l_wrist": [0.30, 0.52, 0.06],
                },
            },
        }


def _fake_landmarks() -> list[dict[str, float]]:
    points = [{"x": 0.0, "y": 0.0, "z": 0.0, "visibility": 0.0} for _ in range(33)]
    points[0] = {"x": 0.50, "y": 0.10, "z": 0.20, "visibility": 0.9}
    points[11] = {"x": 0.38, "y": 0.26, "z": 0.10, "visibility": 0.8}
    points[12] = {"x": 0.62, "y": 0.26, "z": 0.10, "visibility": 0.8}
    points[23] = {"x": 0.44, "y": 0.58, "z": 0.06, "visibility": 0.7}
    points[24] = {"x": 0.56, "y": 0.58, "z": 0.06, "visibility": 0.7}
    return points


class VideoProcessorTests(unittest.TestCase):
    def test_sandbox_processor_drops_frame_keys(self) -> None:
        processor = VideoProcessor(simulated=True, seed=2)
        dummy = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [1, 1, 1]]]
        features = processor.process_frame(dummy)
        self.assertTrue(features["simulated"])
        self.assertFalse(features["frames_exported"])
        self.assertFalse(features["webrtc"])
        self.assertIn("head", features["pose3d"]["joints"])
        blob = str(features).lower()
        for key in FORBIDDEN_FRAME_KEYS:
            self.assertNotIn(f"'{key}'", blob)
            self.assertNotIn(f'"{key}"', blob)
        self.assertNotIn(dummy, features.values())

    def test_strip_frame_payload_removes_pixel_keys(self) -> None:
        cleaned = strip_frame_payload(
            {"pose3d": {"joints": {}}, "frames": [1], "raw_frames": [2], "pixels": [3]}
        )
        self.assertEqual(set(cleaned), {"pose3d"})

    def test_injected_extractor_never_keeps_frame(self) -> None:
        processor = VideoProcessor(
            pose_extractor=_FakePoseExtractor(),
            simulated=False,
            modality="video3d",
        )
        features = processor.process_frame([[0, 0, 0]])
        self.assertFalse(features["simulated"])
        self.assertEqual(features["pose3d"]["origin"], "mediapipe-pose")
        self.assertEqual(features["pose3d"]["joints"]["head"], [0.51, 0.11, 0.20])
        self.assertNotIn("frames", features)


class LandmarkMappingTests(unittest.TestCase):
    def test_landmarks_to_joints_derives_torso(self) -> None:
        joints = landmarks_to_joints(_fake_landmarks())
        self.assertEqual(joints["head"], [0.5, 0.1, 0.2])
        self.assertIn("neck", joints)
        self.assertIn("pelvis", joints)
        self.assertIn("torso", joints)
        self.assertEqual(joints["neck"], [0.5, 0.26, 0.1])

    def test_modules_do_not_import_extras_or_agpl_at_top_level(self) -> None:
        for path in VIDEO_MODULES:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.Import):
                    names = {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom):
                    names = {str(node.module).split(".")[0]} if node.module else set()
                else:
                    continue
                overlap = names & BANNED_TOP_LEVEL
                self.assertFalse(overlap, f"{path.name} top-level import {overlap}")
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("import ultralytics", source)
            self.assertNotIn("from ultralytics", source)


class LiveVideoConsentTests(unittest.TestCase):
    def setUp(self) -> None:
        self._restore = _isolate()

    def tearDown(self) -> None:
        self._restore()

    def test_grant_video_requires_subject_consent(self) -> None:
        live = LiveSensorConsent()
        with self.assertRaises(ValueError):
            live.grant("video", subject_consent=False)
        live.grant("video3d", subject_consent=True)
        self.assertTrue(live.is_granted("video3d"))
        self.assertFalse(live.is_granted("video"))

    def test_live_scan_without_grant_is_refused(self) -> None:
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        with self.assertRaises(SensorHardwareDisabled):
            scan_sensor(ledger, "video3d", live=True)
        with self.assertRaises(SensorHardwareDisabled):
            require_live_video(ledger, "video3d")

    def test_live_scan_with_grant_is_features_only(self) -> None:
        live = load_live_consent()
        live.grant("video3d", subject_consent=True)
        save_live_consent(live)
        ingest = LiveVideoIngest(modality="video3d", pose_extractor=_FakePoseExtractor())
        ingest.accept_frame([[1, 2, 3]])
        replace_video_ingest(ingest, modality="video3d")
        try:
            ledger = ConsentLedger()
            ledger.grant(DATA_INGESTION)
            ledger.grant(ANALYSIS_INSIGHT)
            report = scan_sensor(ledger, "video3d", live=True, ticks=1)
            self.assertIn("live-video-pose", report.notes)
            features = report.steps[0].features
            self.assertFalse(features.get("simulated"))
            self.assertFalse(features.get("frames_exported"))
            self.assertEqual(features["pose3d"]["origin"], "mediapipe-pose")
            self.assertNotIn("frames", features)
            self.assertNotIn("raw_frames", features)
        finally:
            replace_video_ingest(None, modality="video3d")

    def test_adapter_waiting_features_have_empty_joints(self) -> None:
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        ingest = LiveVideoIngest(modality="video", pose_extractor=_FakePoseExtractor())
        adapter = LiveVideoAdapter(modality="video", ingest=ingest)
        from somatic.evidence_bus.adapter import HypothesisSpec

        plan = adapter.plan(HypothesisSpec(id="v", statement="pose", domain="sensing"), ledger)
        acquired = adapter.acquire(plan, ledger)
        features = acquired[0].metadata["features"]
        self.assertTrue(features["waiting_for_frames"])
        self.assertEqual(features["pose3d"]["joints"], {})


class FieldAndFusionVideoTests(unittest.TestCase):
    def test_live_camera_snapshot_can_show_skeleton(self) -> None:
        snap = field_snapshot(
            {
                "pose3d": {
                    "origin": "mediapipe-pose",
                    "simulated": False,
                    "joints": {"head": [0.1, 0.2, 0.3], "torso": [0.2, 0.4, 0.1]},
                },
                "confidence": 0.7,
            },
            mode="live",
            modality="video3d",
        )
        self.assertTrue(snap["show_skeleton"])
        self.assertEqual(snap["disclaimer"], LIVE_CAMERA_DISCLAIMER)
        self.assertIn("head", snap["pose3d"]["joints"])
        self.assertFalse(snap["raw_export"])

    def test_csi_live_snapshot_still_omits_skeleton(self) -> None:
        snap = field_snapshot(
            {
                "pose3d": {
                    "origin": "csi",
                    "simulated": False,
                    "joints": {"head": [0.1, 0.2, 0.3]},
                }
            },
            mode="live",
            modality="csi",
        )
        self.assertFalse(snap["show_skeleton"])
        self.assertEqual(snap["pose3d"]["joints"], {})

    def test_fusion_accepts_live_camera_pose(self) -> None:
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        fused = fuse_rf_vision(
            ledger,
            rf_features={"pose3d": {"joints": {}}},
            vision_features={
                "pose3d": {
                    "origin": "mediapipe-pose",
                    "joints": {"head": [0.2, 0.1, 0.3], "torso": [0.2, 0.4, 0.1]},
                }
            },
        )
        self.assertFalse(fused["simulated"])
        self.assertEqual(fused["fused_joints"]["head"], [0.2, 0.1, 0.3])
        self.assertIn("video3d", fused["sources"])

    def test_sandbox_fusion_unchanged(self) -> None:
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        fused = fuse_rf_vision(ledger, seed=4)
        self.assertTrue(fused["simulated"])
        self.assertEqual(set(fused["sources"]), {"csi", "video3d"})
        self.assertIn("torso", fused["fused_joints"])


class VideoExtraSkipTests(unittest.TestCase):
    def test_extra_status_is_lazy(self) -> None:
        status = video_extra_status()
        self.assertEqual(status["extra"], "video")
        self.assertFalse(status["copyleft_pose_backend"])
        self.assertFalse(status["webrtc"])
        self.assertTrue(status["disabled_by_default"])
        self.assertEqual(status["available"], mediapipe_available())

    @unittest.skipUnless(mediapipe_available(), "video extra (mediapipe) not installed")
    def test_mediapipe_extractor_constructs_without_running_camera(self) -> None:
        from somatic.sensors.video_pose import MediaPipePoseExtractor

        extractor = MediaPipePoseExtractor(use_world_landmarks=True)
        self.assertIsNone(extractor._pose)
        extractor.close()


class SandboxFeatureHelperTests(unittest.TestCase):
    def test_sandbox_pose_is_deterministic(self) -> None:
        left = sandbox_pose_features(seed=3)
        right = sandbox_pose_features(seed=3)
        self.assertEqual(left, right)
        self.assertFalse(left["hardware_access"])


if __name__ == "__main__":
    unittest.main()
