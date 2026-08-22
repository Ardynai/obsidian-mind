"""Sandbox Field snapshot, live CSI UDP ingest, and privacy rails."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from somatic.bridge.serialize import RAW_SENSOR_KEYS
from somatic.consent import ANALYSIS_INSIGHT, DATA_INGESTION, ConsentLedger
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled, _features_for
from somatic.sensors.field import SANDBOX_DISCLAIMER, field_snapshot
from somatic.sensors.fusion import fuse_csi_units
from somatic.sensors.live_consent import (
    LiveSensorConsent,
    load_live_consent,
    save_live_consent,
)
from somatic.sensors.live_csi import (
    LiveCsiIngest,
    LoopbackBindError,
    default_bind_host,
    default_udp_port,
    is_loopback_bind,
    open_serial_transport,
    replace_ingest,
)
from somatic.sensors.live_store import erase_csi_features, load_csi_features
from somatic.sensors.pose_model import infer_pose, pose_model_status
from somatic.sensors.roster import scan_sensor


def _isolate() -> object:
    tmp = tempfile.TemporaryDirectory()
    keys = (
        "SOMATIC_CONSENT_PATH",
        "SOMATIC_SENSOR_LIVE_PATH",
        "SOMATIC_CSI_FEATURES_PATH",
        "SOMATIC_CSI_UDP_HOST",
        "SOMATIC_CSI_UDP_PORT",
        "SOMATIC_CSI_POSE_MODEL",
        "SOMATIC_CSI_POSE_WEIGHTS",
    )
    previous = {key: os.environ.get(key) for key in keys}

    def restore() -> None:
        replace_ingest(None)
        tmp.cleanup()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    root = Path(tmp.name)
    os.environ["SOMATIC_CONSENT_PATH"] = str(root / "consent.json")
    os.environ["SOMATIC_SENSOR_LIVE_PATH"] = str(root / "sensor-live.json")
    os.environ["SOMATIC_CSI_FEATURES_PATH"] = str(root / "csi-features.json")
    os.environ.pop("SOMATIC_CSI_UDP_HOST", None)
    os.environ.pop("SOMATIC_CSI_POSE_MODEL", None)
    os.environ.pop("SOMATIC_CSI_POSE_WEIGHTS", None)
    return restore


def _blob(payload: object) -> str:
    return json.dumps(payload, default=str).lower()


def _assert_no_raw(test: unittest.TestCase, payload: object) -> None:
    blob = _blob(payload)
    for key in RAW_SENSOR_KEYS:
        test.assertNotIn(f'"{key}"', blob)


class FieldSnapshotTests(unittest.TestCase):
    def test_sandbox_snapshot_renders_existing_pose_and_envelope(self) -> None:
        features = _features_for("csi", seed=3, objective="field")
        snap = field_snapshot(features, mode="sandbox", modality="csi", tick=2)
        self.assertEqual(snap["disclaimer"], SANDBOX_DISCLAIMER)
        self.assertTrue(snap["show_skeleton"])
        self.assertIn("head", snap["pose3d"]["joints"])
        self.assertIn("torso", snap["pose3d"]["joints"])
        self.assertTrue(snap["envelope"])
        self.assertTrue(snap["occupancy_row"])
        self.assertTrue(snap["features_only"])
        self.assertFalse(snap["raw_export"])
        _assert_no_raw(self, snap)

    def test_live_snapshot_omits_skeleton(self) -> None:
        fake_pose = {"origin": "csi", "simulated": False, "joints": {"head": [0.1, 0.2, 0.3]}}
        snap = field_snapshot(
            {
                "pose3d": fake_pose,
                "envelope": [0.1, 0.2, 0.1],
                "occupancy_row": [0.2, 0.4, 0.3],
                "breathing_rate_per_min": 14.0,
                "motion_energy": 0.05,
                "presence": True,
            },
            mode="live",
            modality="csi",
        )
        self.assertFalse(snap["show_skeleton"])
        self.assertEqual(snap["pose3d"]["joints"], {})
        self.assertIn("Part 4", snap["pose3d"]["note"])
        _assert_no_raw(self, snap)


class LiveCsiIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._restore = _isolate()
        self.ingest = LiveCsiIngest(host="127.0.0.1", port=0, persist=True)
        self.ingest.start()
        replace_ingest(self.ingest)

    def tearDown(self) -> None:
        self._restore()

    def test_off_loopback_bind_is_refused(self) -> None:
        with self.assertRaises(LoopbackBindError):
            LiveCsiIngest(host="0.0.0.0", port=0)
        os.environ["SOMATIC_CSI_UDP_HOST"] = "8.8.8.8"
        with self.assertRaises(LoopbackBindError):
            default_bind_host()

    def test_udp_loopback_derives_features_without_raw_keys(self) -> None:
        packet = {
            "v": 1,
            "ts": 1.0,
            "unit_id": "esp32-a",
            "rssi": -42,
            "amp": [0.2, 0.8, 0.4, 0.5, 0.3, 0.6],
            "phase": [0.1, -0.2, 0.0, 0.3, -0.1, 0.2],
        }
        self.ingest.send_loopback(json.dumps(packet))
        for _ in range(40):
            if self.ingest.latest() is not None:
                break
            self.ingest._stop.wait(0.05)
        latest = self.ingest.latest()
        self.assertIsNotNone(latest)
        assert latest is not None
        self.assertEqual(latest["unit_id"], "esp32-a")
        self.assertTrue(latest["occupancy_row"])
        self.assertTrue(latest["envelope"])
        self.assertTrue(latest.get("pose3d_omitted"))
        _assert_no_raw(self, latest)
        stored = load_csi_features()
        self.assertTrue(stored)
        _assert_no_raw(self, stored[-1])

    def test_iq_packet_is_converted_and_iq_is_dropped(self) -> None:
        features = self.ingest.ingest_line(
            'CSI_DATA,frame-1,0.2,esp32-b,-50,"[1 0 2 0 3 -1 4 0]",lab'
        )
        self.assertIsNotNone(features)
        assert features is not None
        self.assertTrue(features["occupancy_row"])
        blob = _blob(features)
        self.assertNotIn('"iq"', blob)
        self.assertNotIn('"csi_data"', blob)
        _assert_no_raw(self, features)

    def test_live_scan_without_grant_is_refused(self) -> None:
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        with self.assertRaises(SensorHardwareDisabled):
            scan_sensor(ledger, "csi", live=True)
        with self.assertRaises(SensorHardwareDisabled):
            scan_sensor(ledger, "video", live=True)

    def test_live_scan_with_grant_reads_loopback_features(self) -> None:
        live = load_live_consent()
        live.grant("csi", subject_consent=True)
        save_live_consent(live)
        self.ingest.ingest_line(
            json.dumps({"v": 1, "ts": 2, "unit_id": "esp32-a", "amp": [0.4, 0.5, 0.6, 0.2]})
        )
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        report = scan_sensor(ledger, "csi", live=True, ticks=1)
        self.assertIn("live-csi-udp", report.notes)
        features = report.steps[0].features
        self.assertFalse(features.get("simulated"))
        self.assertNotIn("pose3d", features)
        _assert_no_raw(self, features)

    def test_subject_consent_is_required_to_grant(self) -> None:
        live = LiveSensorConsent()
        with self.assertRaises(ValueError):
            live.grant("csi", subject_consent=False)

    def test_erase_clears_stored_features(self) -> None:
        self.ingest.ingest_line(
            json.dumps({"v": 1, "ts": 3, "unit_id": "esp32-a", "amp": [0.3, 0.4]})
        )
        self.assertTrue(load_csi_features())
        erase_csi_features()
        self.assertEqual(load_csi_features(), ())

    def test_non_loopback_sender_is_dropped(self) -> None:
        self.assertFalse(is_loopback_bind("8.8.8.8"))
        self.assertFalse(is_loopback_bind("0.0.0.0"))
        before_drop = self.ingest.packets_dropped
        before_accept = self.ingest.packets_accepted
        self.ingest._handle_datagram(
            json.dumps({"v": 1, "amp": [0.5, 0.4, 0.3, 0.2]}).encode("utf-8"),
            ("8.8.8.8", 9),
        )
        self.assertEqual(self.ingest.packets_dropped, before_drop + 1)
        self.assertEqual(self.ingest.packets_accepted, before_accept)
        self.assertIsNone(self.ingest.latest())

    def test_oversize_datagram_is_dropped(self) -> None:
        from somatic.sensors.live_csi import MAX_PACKET_BYTES

        before = self.ingest.packets_dropped
        self.ingest._handle_datagram(b"x" * (MAX_PACKET_BYTES + 1), ("127.0.0.1", 9))
        self.assertEqual(self.ingest.packets_dropped, before + 1)

    def test_ephemeral_udp_port_is_allowed(self) -> None:
        os.environ["SOMATIC_CSI_UDP_PORT"] = "0"
        self.assertEqual(default_udp_port(), 0)

    def test_serial_extra_is_lazy(self) -> None:
        try:
            import serial  # noqa: F401
        except ImportError:
            with self.assertRaises(SensorHardwareDisabled):
                open_serial_transport("COM9")
            return
        self.assertTrue(True)

    def test_pose_model_stays_off(self) -> None:
        status = pose_model_status()
        self.assertTrue(status["founder_gated"])
        self.assertFalse(status["enabled"])
        pose = infer_pose({"occupancy_row": [0.1, 0.2]})
        self.assertEqual(pose["joints"], {})
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        fused = fuse_csi_units(
            ledger,
            [
                {"unit_id": "a", "occupancy_row": [0.2, 0.4]},
                {"unit_id": "b", "occupancy_row": [0.4, 0.6]},
            ],
        )
        self.assertEqual(fused["fused_occupancy_row"], [0.3, 0.5])
        self.assertEqual(fused["pose3d"]["joints"], {})
        _assert_no_raw(self, fused)


class LiveCsiConsentFuseTests(unittest.TestCase):
    def setUp(self) -> None:
        self._restore = _isolate()

    def tearDown(self) -> None:
        self._restore()

    def test_fuse_without_consent_fails(self) -> None:
        from somatic.safety.core import ConsentRequiredError

        with self.assertRaises(ConsentRequiredError):
            fuse_csi_units(ConsentLedger(), [{"occupancy_row": [1.0]}])


if __name__ == "__main__":
    unittest.main()
