"""Tests for the consent-gated end-to-end analyze flow and CLI."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import AI_ADVISORY, ANALYSIS_INSIGHT, ConsentLedger
from somatic.flows.analyze import AnalysisReport, analyze_user_data
from somatic.insights import ReferenceRange
from somatic.safety.core import INFORMATIONAL_NOTICE, EvidenceGrade

REPO_ROOT = Path(__file__).resolve().parents[1]


class AnalyzeFlowTests(unittest.TestCase):
    def test_emergency_input_short_circuits(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        ledger.grant(AI_ADVISORY)
        report = analyze_user_data(
            ledger,
            {"resting_hr": 72},
            "I have sudden chest pain — what should I do?",
            references={
                "resting_hr": {
                    "low": 50,
                    "high": 90,
                    "unit": "bpm",
                    "source": "user-provided",
                }
            },
            model_config=None,
        )
        self.assertIsInstance(report, AnalysisReport)
        self.assertEqual(len(report.results), 1)
        self.assertIn("emergency", report.results[0].summary.lower())
        self.assertEqual(report.results[0].evidence_grade, EvidenceGrade.NONE)
        self.assertTrue(any("emergency" in note.lower() for note in report.notes))

    def test_insights_run_when_analysis_insight_granted(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        reference = ReferenceRange(
            metric="glucose_mg_dl",
            low=70.0,
            high=100.0,
            unit="mg/dL",
            source="user-supplied-lab-printout",
        )
        report = analyze_user_data(
            ledger,
            {"glucose_mg_dl": 120},
            "How does this reading compare?",
            references={"glucose_mg_dl": reference},
        )
        self.assertGreaterEqual(len(report.results), 1)
        joined = " ".join(result.summary for result in report.results).lower()
        self.assertIn("above the reference range you provided", joined)
        for result in report.results:
            self.assertEqual(result.informational_notice, INFORMATIONAL_NOTICE)
        self.assertTrue(any("AI read skipped" in note for note in report.notes))

    def test_insights_skipped_without_consent_no_raise(self):
        ledger = ConsentLedger()
        report = analyze_user_data(
            ledger,
            {"glucose_mg_dl": 120},
            "How does this reading compare?",
            references={
                "glucose_mg_dl": {
                    "low": 70,
                    "high": 100,
                    "unit": "mg/dL",
                    "source": "user-supplied",
                }
            },
        )
        self.assertEqual(report.results, ())
        self.assertIn("insights skipped: consent not granted", report.notes)
        self.assertIn("AI read skipped: consent not granted", report.notes)

    def test_ai_read_skipped_without_model_config(self):
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        report = analyze_user_data(
            ledger,
            {"sleep_hours": 7.0},
            "Any patterns?",
            model_config=None,
        )
        self.assertEqual(report.results, ())
        self.assertIn("AI read skipped: no model_config provided", report.notes)

    def test_aggregation_returns_results_and_notes(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = analyze_user_data(
            ledger,
            {"steps": [1000, 1200, 1500, 1800]},
            "What is the trend?",
            baselines={"steps": [900, 950, 1000, 1050]},
        )
        self.assertGreaterEqual(len(report.results), 1)
        self.assertTrue(report.notes)
        payload = report.to_dict()
        self.assertEqual(len(payload["results"]), len(report.results))
        self.assertEqual(payload["notes"], list(report.notes))
        self.assertTrue(payload["generated_at"])

    def test_cli_analyze_prints_report_from_temp_packet(self):
        packet = {"resting_hr": 95}
        references = {
            "resting_hr": {
                "low": 50,
                "high": 90,
                "unit": "bpm",
                "source": "user-provided-clinician-note",
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "packet.json"
            refs_path = Path(tmp) / "refs.json"
            data_path.write_text(json.dumps(packet), encoding="utf-8")
            refs_path.write_text(json.dumps(references), encoding="utf-8")
            previous = os.environ.get("SOMATIC_CONSENT_PATH")
            os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp) / "consent.json")
            buffer = io.StringIO()
            try:
                with contextlib.redirect_stdout(buffer):
                    exit_code = main(
                        [
                            "analyze",
                            "--data",
                            str(data_path),
                            "--references",
                            str(refs_path),
                            "--grant",
                            "analysis-insight",
                            "--question",
                            "How does my resting heart rate look?",
                        ]
                    )
            finally:
                if previous is None:
                    os.environ.pop("SOMATIC_CONSENT_PATH", None)
                else:
                    os.environ["SOMATIC_CONSENT_PATH"] = previous
            output = buffer.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("granting: analysis-insight", output)
        self.assertIn("Somatic analyze report", output)
        self.assertIn("evidence_grade=", output)
        self.assertIn("informational_notice:", output)
        self.assertIn("professional_routing:", output)
        self.assertIn("reference range you provided", output.lower())

    def test_cli_malformed_data_and_references_print_a_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "packet.json"
            refs_path = Path(tmp) / "refs.json"
            data_path.write_text("{not-json", encoding="utf-8")
            refs_path.write_text('{"ok": true}', encoding="utf-8")
            previous = os.environ.get("SOMATIC_CONSENT_PATH")
            os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp) / "consent.json")
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    code = main(
                        [
                            "analyze",
                            "--data",
                            str(data_path),
                            "--references",
                            str(refs_path),
                            "--grant",
                            "analysis-insight",
                            "--question",
                            "How does my resting heart rate look?",
                        ]
                    )
            finally:
                if previous is None:
                    os.environ.pop("SOMATIC_CONSENT_PATH", None)
                else:
                    os.environ["SOMATIC_CONSENT_PATH"] = previous
        self.assertEqual(code, 2)
        stderr = err.getvalue()
        self.assertIn("analyze: could not read --data:", stderr)
        self.assertNotIn("Traceback", stderr)

        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "packet.json"
            refs_path = Path(tmp) / "refs.json"
            data_path.write_text(json.dumps({"resting_hr": 70}), encoding="utf-8")
            refs_path.write_bytes(b"\xff\xfe not-utf8")
            previous = os.environ.get("SOMATIC_CONSENT_PATH")
            os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp) / "consent.json")
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    code = main(
                        [
                            "analyze",
                            "--data",
                            str(data_path),
                            "--references",
                            str(refs_path),
                            "--grant",
                            "analysis-insight",
                            "--question",
                            "How does my resting heart rate look?",
                        ]
                    )
            finally:
                if previous is None:
                    os.environ.pop("SOMATIC_CONSENT_PATH", None)
                else:
                    os.environ["SOMATIC_CONSENT_PATH"] = previous
        self.assertEqual(code, 2)
        stderr = err.getvalue()
        self.assertIn("analyze: could not read --references:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_malformed_reference_and_na_values_surface_notes(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = analyze_user_data(
            ledger,
            {"glucose_mg_dl": [100, "n/a", 110]},
            "How does this reading compare?",
            references={
                "glucose_mg_dl": {
                    "min": 70,
                    "max": 100,
                    "unit": "mg/dL",
                    "source": "typo",
                }
            },
        )
        joined_notes = " ".join(report.notes)
        self.assertIn("min/max", joined_notes.lower())
        self.assertIn("dropped", joined_notes.lower())

    def test_cli_rejects_model_key_argv(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "packet.json"
            data_path.write_text(json.dumps({"resting_hr": 70}), encoding="utf-8")
            previous = os.environ.get("SOMATIC_CONSENT_PATH")
            os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp) / "consent.json")
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    code = main(
                        [
                            "analyze",
                            "--data",
                            str(data_path),
                            "--model-url",
                            "http://127.0.0.1:9",
                            "--model",
                            "test",
                            "--model-key",
                            "secret-from-argv",
                        ]
                    )
            finally:
                if previous is None:
                    os.environ.pop("SOMATIC_CONSENT_PATH", None)
                else:
                    os.environ["SOMATIC_CONSENT_PATH"] = previous
        self.assertEqual(code, 2)
        self.assertIn("SOMATIC_ADVISORY_MODEL_KEY", err.getvalue())

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
