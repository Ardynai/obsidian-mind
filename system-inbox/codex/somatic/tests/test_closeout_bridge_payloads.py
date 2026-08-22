"""Bridge payload additions from the closeout: encryption flag, grant flags, passthrough."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path


class BridgePayloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        keys = (
            "SOMATIC_CONSENT_PATH",
            "SOMATIC_INGEST_PATH",
            "SOMATIC_EXPERIMENT_PATH",
            "SOMATIC_SENSOR_LIVE_PATH",
            "SOMATIC_CSI_FEATURES_PATH",
            "SOMATIC_AUDIO_FEATURES_PATH",
            "SOMATIC_ENCRYPT_STORES",
        )
        self._previous = {key: os.environ.get(key) for key in keys}
        base = Path(self._tmp.name)
        os.environ["SOMATIC_CONSENT_PATH"] = str(base / "consent.json")
        os.environ["SOMATIC_INGEST_PATH"] = str(base / "readings.json")
        os.environ["SOMATIC_EXPERIMENT_PATH"] = str(base / "experiments.json")
        os.environ["SOMATIC_SENSOR_LIVE_PATH"] = str(base / "sensor-live.json")
        os.environ["SOMATIC_CSI_FEATURES_PATH"] = str(base / "csi-features.json")
        os.environ["SOMATIC_AUDIO_FEATURES_PATH"] = str(base / "audio-features.json")
        os.environ.pop("SOMATIC_ENCRYPT_STORES", None)

    def tearDown(self) -> None:
        for key, value in self._previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self._tmp.cleanup()

    def test_privacy_exposes_encryption_flag_and_all_grant_flags(self) -> None:
        from somatic.bridge import api as bridge

        payload: dict = bridge.dispatch("GET", "/api/privacy", None)
        self.assertFalse(payload["encryption_at_rest"])
        self.assertEqual(payload["encryption_flag"], "SOMATIC_ENCRYPT_STORES")
        for modality in ("csi", "audio", "video", "video3d"):
            self.assertIn(f"{modality}_live_granted", payload)
        os.environ["SOMATIC_ENCRYPT_STORES"] = "1"
        try:
            payload = bridge.dispatch("GET", "/api/privacy", None)
            self.assertTrue(payload["encryption_at_rest"])
        finally:
            os.environ.pop("SOMATIC_ENCRYPT_STORES", None)

    def test_status_includes_encryption_and_language_scope(self) -> None:
        from somatic.bridge import api as bridge
        from somatic.safety.core import LANGUAGE_SCOPE

        status: dict = bridge.dispatch("GET", "/api/status", None)
        self.assertFalse(status["encryption_at_rest"])
        self.assertEqual(status["emergency_self_test"]["language_scope"], LANGUAGE_SCOPE)

    def test_sensors_lists_audio_grant_flag_and_pose_model(self) -> None:
        from somatic.bridge import api as bridge

        sensors: dict = bridge.dispatch("GET", "/api/sensors", None)
        self.assertIn("audio_live_granted", sensors)
        self.assertIsInstance(sensors["pose_model"], dict)
        lanes = {lane["modality"]: lane for lane in sensors["lanes"]}
        self.assertFalse(lanes["audio"]["live_granted"])

    def test_field_snapshot_carries_audio_passthrough_keys(self) -> None:
        ledger_path = os.environ["SOMATIC_CONSENT_PATH"]
        from somatic.consent.ledger import ConsentLedger
        from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
        from somatic.consent.store import save_ledger

        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        save_ledger(ledger, Path(ledger_path))
        from somatic.sensors.field import field_snapshot

        snapshot = field_snapshot(
            {
                "envelope": [0.1, 0.2],
                "breathing_rate_per_min": 13.0,
                "cough_event_count": 2,
                "speech_activity_ratio": 0.42,
            },
            mode="sandbox",
            modality="audio",
            tick=1,
        )
        self.assertEqual(snapshot["cough_event_count"], 2)
        self.assertEqual(snapshot["speech_activity_ratio"], 0.42)


if __name__ == "__main__":
    unittest.main()
