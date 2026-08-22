"""Sensor roster sandbox live-scan, privacy rails, and RF↔vision fusion."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import ANALYSIS_INSIGHT, DATA_INGESTION, ConsentLedger
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.sensors import LIVE_SENSOR_INTEGRATION_IMPLEMENTED
from somatic.sensors.fusion import fuse_rf_vision
from somatic.sensors.roster import SENSOR_ROSTER_MODALITIES, list_sensor_lanes, scan_sensor


def _isolate():
    tmp = tempfile.TemporaryDirectory()
    keys = (
        "SOMATIC_CONSENT_PATH",
        "SOMATIC_SENSOR_LIVE_PATH",
        "SOMATIC_CSI_FEATURES_PATH",
    )
    previous = {key: os.environ.get(key) for key in keys}

    def restore() -> None:
        tmp.cleanup()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp.name) / "consent.json")
    os.environ["SOMATIC_SENSOR_LIVE_PATH"] = str(Path(tmp.name) / "sensor-live.json")
    os.environ["SOMATIC_CSI_FEATURES_PATH"] = str(Path(tmp.name) / "csi-features.json")
    return restore


class SensorRosterTests(unittest.TestCase):
    def test_live_hardware_flag_stays_false(self):
        self.assertFalse(LIVE_SENSOR_INTEGRATION_IMPLEMENTED)
        for lane in list_sensor_lanes():
            self.assertFalse(lane.live_hardware)
            self.assertTrue(lane.sandbox_default)

    def test_live_scan_is_refused(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        with self.assertRaises(SensorHardwareDisabled):
            scan_sensor(ledger, "csi", live=True)

    def test_sandbox_scan_covers_roster(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        for modality in SENSOR_ROSTER_MODALITIES:
            with self.subTest(modality=modality):
                report = scan_sensor(ledger, modality, ticks=2, seed=3)
                self.assertFalse(report.emergency_triggered)
                self.assertEqual(len(report.steps), 2)
                self.assertTrue(all(step.modality == modality for step in report.steps))
                self.assertIn("hardware-closed", report.notes)

    def test_fusion_averages_simulated_joints(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        fused = fuse_rf_vision(ledger, seed=4)
        self.assertTrue(fused["simulated"])
        self.assertFalse(fused["hardware_access"])
        self.assertEqual(set(fused["sources"]), {"csi", "video3d"})
        self.assertIn("torso", fused["fused_joints"])

    def test_cli_list_scan_fuse_and_live_refuse(self):
        restore = _isolate()
        try:
            listed = io.StringIO()
            with contextlib.redirect_stdout(listed):
                self.assertEqual(main(["sensor-roster", "list"]), 0)
            self.assertIn("csi:", listed.getvalue())
            self.assertIn("video3d:", listed.getvalue())
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                live = main(
                    [
                        "sensor-roster",
                        "scan",
                        "--modality",
                        "csi",
                        "--live",
                        "--grant",
                        "data-ingestion,analysis-insight",
                    ]
                )
            self.assertEqual(live, 2)
            self.assertIn("off by default", err.getvalue().lower())
            grant_err = io.StringIO()
            with contextlib.redirect_stderr(grant_err):
                grant_code = main(["sensor-roster", "live-grant"])
            self.assertEqual(grant_code, 2)
            self.assertIn("subject consent", grant_err.getvalue().lower())
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "sensor-roster",
                        "fuse",
                        "--grant",
                        "data-ingestion,analysis-insight",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("rf_vision", out.getvalue())
        finally:
            restore()


if __name__ == "__main__":
    unittest.main()
