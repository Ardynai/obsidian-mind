"""Tests for consent-gated CSV / Apple Health ingestion and timestamped packets."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path

from somatic.cli import main
from somatic.consent import ANALYSIS_INSIGHT, DATA_INGESTION, PROFESSIONAL_SHARING, ConsentLedger
from somatic.flows.analyze import analyze_user_data
from somatic.flows.share import render_professional_summary
from somatic.ingest import (
    ingest_apple_health,
    ingest_apple_health_xml,
    ingest_csv,
    ingest_csv_text,
    load_readings,
    normalize_observed_at,
)
from somatic.ingest.packet import reading_from_dict
from somatic.ingest.store import append_readings
from somatic.safety.core import ConsentRequiredError

REPO_ROOT = Path(__file__).resolve().parents[1]

APPLE_HEALTH_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<HealthData>
  <Record type="HKQuantityTypeIdentifierHeartRate" unit="count/min"
          value="72" startDate="2026-05-01 08:00:00 -0500"/>
  <Record type="HKQuantityTypeIdentifierStepCount" unit="count"
          value="1000" startDate="2026-05-01 09:00:00 -0500"/>
  <Record type="HKCategoryTypeIdentifierSleepAnalysis"
          value="HKCategoryValueSleepAnalysisAsleep"
          startDate="2026-05-01 00:00:00 -0500"/>
</HealthData>
"""


def _isolate_ingest_env():
    tmp = tempfile.TemporaryDirectory()
    consent_path = str(Path(tmp.name) / "consent.json")
    ingest_path = str(Path(tmp.name) / "readings.json")
    experiment_path = str(Path(tmp.name) / "experiments.json")
    previous_consent = os.environ.get("SOMATIC_CONSENT_PATH")
    previous_ingest = os.environ.get("SOMATIC_INGEST_PATH")
    previous_experiment = os.environ.get("SOMATIC_EXPERIMENT_PATH")

    def restore() -> None:
        tmp.cleanup()
        if previous_consent is None:
            os.environ.pop("SOMATIC_CONSENT_PATH", None)
        else:
            os.environ["SOMATIC_CONSENT_PATH"] = previous_consent
        if previous_ingest is None:
            os.environ.pop("SOMATIC_INGEST_PATH", None)
        else:
            os.environ["SOMATIC_INGEST_PATH"] = previous_ingest
        if previous_experiment is None:
            os.environ.pop("SOMATIC_EXPERIMENT_PATH", None)
        else:
            os.environ["SOMATIC_EXPERIMENT_PATH"] = previous_experiment

    os.environ["SOMATIC_CONSENT_PATH"] = consent_path
    os.environ["SOMATIC_INGEST_PATH"] = ingest_path
    os.environ["SOMATIC_EXPERIMENT_PATH"] = experiment_path
    return Path(tmp.name), restore


class IngestPacketTests(unittest.TestCase):
    def test_csv_requires_data_ingestion_consent(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            ingest_csv_text(
                ledger,
                "metric,value,observed_at\nresting_hr,72,2026-05-01T08:00:00Z\n",
            )

    def test_csv_parses_timestamped_readings(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        packet = ingest_csv_text(
            ledger,
            "metric,value,observed_at,unit,source\n"
            "resting_hr,72,2026-05-01T08:00:00Z,bpm,watch\n"
            "resting_hr,80,2026-05-02,bpm,watch\n",
        )
        self.assertEqual(packet.source_kind, "csv")
        self.assertEqual(len(packet.readings), 2)
        self.assertEqual(packet.readings[0].observed_at, "2026-05-01T08:00:00Z")
        self.assertEqual(packet.readings[1].observed_at, "2026-05-02T00:00:00Z")
        analyze_packet = packet.to_analyze_packet()
        self.assertEqual(len(analyze_packet["resting_hr"]), 2)
        self.assertEqual(analyze_packet["resting_hr"][0]["value"], 72.0)

    def test_csv_missing_header_fails_loud(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        with self.assertRaises(ValueError) as raised:
            ingest_csv_text(ledger, "resting_hr,72,2026-05-01\n")
        self.assertIn("metric,value,observed_at", str(raised.exception))

    def test_csv_skips_bad_rows_but_keeps_good_ones(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        packet = ingest_csv_text(
            ledger,
            "metric,value,observed_at\n"
            "resting_hr,not-a-number,2026-05-01T08:00:00Z\n"
            "resting_hr,70,2026-05-01T09:00:00Z\n",
        )
        self.assertEqual(len(packet.readings), 1)
        self.assertTrue(packet.notes)

    def test_csv_skips_nan_and_inf(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        packet = ingest_csv_text(
            ledger,
            "metric,value,observed_at\n"
            "resting_hr,nan,2026-05-01T08:00:00Z\n"
            "resting_hr,inf,2026-05-01T09:00:00Z\n"
            "resting_hr,70,2026-05-01T10:00:00Z\n",
        )
        self.assertEqual(len(packet.readings), 1)
        self.assertEqual(packet.readings[0].value, 70.0)
        joined = " ".join(packet.notes).lower()
        self.assertIn("finite", joined)

    def test_csv_notes_mixed_units_but_not_blank_vs_one_unit(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        mixed = ingest_csv_text(
            ledger,
            "metric,value,observed_at,unit\n"
            "glucose,120,2026-05-01T08:00:00Z,mg/dL\n"
            "glucose,6.7,2026-05-01T09:00:00Z,mmol/L\n",
        )
        self.assertEqual(len(mixed.readings), 2)
        self.assertTrue(any("mixed units" in note for note in mixed.notes))
        blank = ingest_csv_text(
            ledger,
            "metric,value,observed_at,unit\n"
            "resting_hr,72,2026-05-01T08:00:00Z,bpm\n"
            "resting_hr,70,2026-05-01T09:00:00Z,\n",
        )
        self.assertFalse(any("mixed units" in note for note in blank.notes))

    def test_reading_from_dict_rejects_nan(self):
        with self.assertRaises(ValueError):
            reading_from_dict(
                {
                    "metric": "resting_hr",
                    "value": float("nan"),
                    "observed_at": "2026-05-01T08:00:00Z",
                }
            )

    def test_store_rejects_nan_reading_payload(self):
        _root, restore = _isolate_ingest_env()
        try:
            path = Path(os.environ["SOMATIC_INGEST_PATH"])
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "readings": [
                            {
                                "metric": "resting_hr",
                                "value": float("nan"),
                                "observed_at": "2026-05-01T08:00:00Z",
                                "unit": "bpm",
                                "source": "csv",
                            }
                        ],
                    },
                    allow_nan=True,
                ),
                encoding="utf-8",
            )
            self.assertEqual(load_readings(), ())
        finally:
            restore()

    def test_apple_health_maps_quantity_records_and_skips_categories(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        packet = ingest_apple_health_xml(ledger, APPLE_HEALTH_XML)
        metrics = {reading.metric for reading in packet.readings}
        self.assertEqual(metrics, {"heart_rate", "steps"})
        self.assertTrue(any("skipped" in note for note in packet.notes))
        heart = [reading for reading in packet.readings if reading.metric == "heart_rate"][0]
        self.assertEqual(heart.value, 72.0)
        self.assertEqual(heart.observed_at, "2026-05-01T13:00:00Z")
        self.assertEqual(heart.unit, "count/min")

    def test_apple_health_skips_non_finite_values(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        xml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<HealthData>
  <Record type="HKQuantityTypeIdentifierHeartRate" unit="count/min"
          value="inf" startDate="2026-05-01 08:00:00 -0500"/>
  <Record type="HKQuantityTypeIdentifierHeartRate" unit="count/min"
          value="72" startDate="2026-05-01 09:00:00 -0500"/>
</HealthData>
"""
        packet = ingest_apple_health_xml(ledger, xml_text)
        self.assertEqual(len(packet.readings), 1)
        self.assertEqual(packet.readings[0].value, 72.0)
        self.assertTrue(any("skipped" in note for note in packet.notes))

    def test_apple_health_zip_reads_export_xml(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "export.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("apple_health_export/export.xml", APPLE_HEALTH_XML)
            packet = ingest_apple_health(ledger, zip_path)
        self.assertEqual(len(packet.readings), 2)

    def test_apple_health_non_zip_named_zip_raises_value_error(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "export.zip"
            zip_path.write_text("not a zip archive", encoding="utf-8")
            with self.assertRaises(ValueError) as raised:
                ingest_apple_health(ledger, zip_path)
        self.assertIn("not a valid zip", str(raised.exception).lower())

    def test_cli_apple_health_non_zip_prints_a_note(self):
        root, restore = _isolate_ingest_env()
        try:
            zip_path = root / "export.zip"
            zip_path.write_text("not a zip archive", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = main(
                    [
                        "ingest",
                        "apple-health",
                        "--file",
                        str(zip_path),
                        "--grant",
                        "data-ingestion",
                    ]
                )
            self.assertEqual(code, 2)
            stderr = err.getvalue()
            self.assertIn("ingest:", stderr)
            self.assertNotIn("Traceback", stderr)
        finally:
            restore()

    def test_store_invalid_payload_loads_empty(self):
        _root, restore = _isolate_ingest_env()
        try:
            path = Path(os.environ["SOMATIC_INGEST_PATH"])
            path.write_text('{"schema_version": true, "readings": []}', encoding="utf-8")
            self.assertEqual(load_readings(), ())
        finally:
            restore()

    def test_non_utf8_readings_file_loads_empty(self):
        _root, restore = _isolate_ingest_env()
        try:
            path = Path(os.environ["SOMATIC_INGEST_PATH"])
            path.write_bytes(b"\xff\xfe not-utf8 \xa9")
            self.assertEqual(load_readings(), ())
        finally:
            restore()

    def test_consent_erase_deletes_readings_store(self):
        _root, restore = _isolate_ingest_env()
        try:
            ledger = ConsentLedger()
            ledger.grant(DATA_INGESTION)
            packet = ingest_csv_text(
                ledger,
                "metric,value,observed_at\nresting_hr,72,2026-05-01T08:00:00Z\n",
            )
            append_readings(packet.readings)
            self.assertEqual(len(load_readings()), 1)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(["consent", "erase"])
            self.assertEqual(code, 0)
            self.assertEqual(load_readings(), ())
            self.assertFalse(Path(os.environ["SOMATIC_INGEST_PATH"]).exists())
        finally:
            restore()

    def test_analyze_and_share_surface_observation_dates(self):
        ingest_ledger = ConsentLedger()
        ingest_ledger.grant(DATA_INGESTION)
        packet = ingest_csv_text(
            ingest_ledger,
            "metric,value,observed_at,unit\nglucose_mg_dl,120,2026-05-01T08:00:00Z,mg/dL\n",
        )
        analyze_ledger = ConsentLedger()
        analyze_ledger.grant(ANALYSIS_INSIGHT)
        report = analyze_user_data(
            analyze_ledger,
            packet.to_dict(),
            "How does this reading compare?",
            references={
                "glucose_mg_dl": {
                    "low": 70,
                    "high": 100,
                    "unit": "mg/dL",
                    "source": "user-supplied-lab-printout",
                }
            },
        )
        joined = " ".join(result.summary for result in report.results)
        self.assertIn("2026-05-01T08:00:00Z", joined)
        analyze_ledger.grant(PROFESSIONAL_SHARING)
        markdown = render_professional_summary(analyze_ledger, report)
        self.assertIn("observed:", markdown.lower())
        self.assertIn("2026-05-01T08:00:00Z", markdown)

    def test_cli_ingest_csv_requires_consent_and_writes_packet(self):
        root, restore = _isolate_ingest_env()
        try:
            csv_path = root / "readings.csv"
            csv_path.write_text(
                "metric,value,observed_at\nresting_hr,72,2026-05-01T08:00:00Z\n",
                encoding="utf-8",
            )
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                denied = main(["ingest", "csv", "--file", str(csv_path)])
            self.assertEqual(denied, 2)
            self.assertIn("data-ingestion consent required", err.getvalue())

            out_path = root / "packet.json"
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = main(
                    [
                        "ingest",
                        "csv",
                        "--file",
                        str(csv_path),
                        "--out",
                        str(out_path),
                        "--save",
                        "--grant",
                        "data-ingestion",
                    ]
                )
            self.assertEqual(code, 0)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "somatic.packet.v1")
            self.assertEqual(len(payload["readings"]), 1)
            self.assertEqual(len(load_readings()), 1)
            status = io.StringIO()
            with contextlib.redirect_stdout(status):
                self.assertEqual(main(["ingest", "status"]), 0)
            self.assertIn("readings: 1", status.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["ingest", "erase"]), 0)
            self.assertEqual(load_readings(), ())
        finally:
            restore()

    def test_normalize_observed_at_rejects_empty(self):
        with self.assertRaises(ValueError):
            normalize_observed_at("  ")

    def test_ingest_csv_file_path(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            path.write_text(
                "metric,value,observed_at\nsteps,1000,2026-05-01T12:00:00Z\n",
                encoding="utf-8",
            )
            packet = ingest_csv(ledger, path)
        self.assertEqual(packet.readings[0].metric, "steps")

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
