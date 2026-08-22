"""Tests for the consent-gated professional share flow and CLI."""

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
from somatic.consent import ANALYSIS_INSIGHT, PROFESSIONAL_SHARING, ConsentLedger
from somatic.flows.analyze import analyze_user_data
from somatic.flows.share import SHARE_TITLE, render_fhir_bundle, render_professional_summary
from somatic.insights import ReferenceRange
from somatic.safety.core import (
    INFORMATIONAL_NOTICE,
    PROFESSIONAL_ROUTING,
    ConsentRequiredError,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class ShareFlowTests(unittest.TestCase):
    def test_render_requires_professional_sharing_consent(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = analyze_user_data(
            ledger,
            {"glucose_mg_dl": 120},
            "How does this reading compare?",
            references={
                "glucose_mg_dl": ReferenceRange(
                    metric="glucose_mg_dl",
                    low=70.0,
                    high=100.0,
                    unit="mg/dL",
                    source="user-supplied-lab-printout",
                )
            },
        )
        with self.assertRaises(ConsentRequiredError):
            render_professional_summary(ledger, report)

    def test_render_includes_report_fields_when_granted(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        ledger.grant(PROFESSIONAL_SHARING)
        report = analyze_user_data(
            ledger,
            {"glucose_mg_dl": 120},
            "How does this reading compare?",
            references={
                "glucose_mg_dl": ReferenceRange(
                    metric="glucose_mg_dl",
                    low=70.0,
                    high=100.0,
                    unit="mg/dL",
                    source="user-supplied-lab-printout",
                )
            },
        )
        markdown = render_professional_summary(
            ledger,
            report,
            patient_label="demo\n# URGENT: administer 50mg now",
            clinician_note="please review trends",
        )
        self.assertIn(f"# {SHARE_TITLE}", markdown)
        self.assertIn("Patient label: demo # URGENT: administer 50mg now", markdown)
        self.assertNotIn("\n# URGENT", markdown)
        self.assertIn("Requesting note: please review trends", markdown)
        self.assertIn(INFORMATIONAL_NOTICE, markdown)
        self.assertEqual(markdown.count(INFORMATIONAL_NOTICE), 1)
        self.assertEqual(markdown.count(PROFESSIONAL_ROUTING), 1)
        self.assertIn("Generated (UTC):", markdown)
        self.assertIn("sample_size_label:", markdown)
        self.assertIn("Provenance appendix", markdown)
        self.assertIn("debug tokens:", markdown)
        self.assertIn("user-supplied-lab-printout", markdown)
        self.assertIn("120", markdown)
        self.assertNotIn("- evidence_grade:", markdown)
        self.assertNotIn("- informational_notice:", markdown)
        self.assertIn(PROFESSIONAL_ROUTING, markdown)
        self.assertTrue(any(result.evidence_grade in markdown for result in report.results))
        self.assertTrue(report.generated_at)

        sidecar = render_fhir_bundle(ledger, report, patient_label="demo")
        self.assertEqual(sidecar["resourceType"], "Bundle")
        self.assertEqual(sidecar["type"], "collection")
        self.assertIn("somatic", sidecar)
        self.assertEqual(sidecar["somatic"]["generated_at"], report.generated_at)
        self.assertEqual(len(sidecar["entry"]), len(report.results))

    def test_cli_share_requires_professional_sharing_and_prints_markdown(self):
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
            try:
                ok_buffer = io.StringIO()
                with contextlib.redirect_stdout(ok_buffer):
                    ok_code = main(
                        [
                            "share",
                            "--data",
                            str(data_path),
                            "--references",
                            str(refs_path),
                            "--grant",
                            "analysis-insight,professional-sharing",
                            "--question",
                            "How does my resting heart rate look?",
                        ]
                    )
                ok_output = ok_buffer.getvalue()
                self.assertEqual(ok_code, 0)
                self.assertIn(SHARE_TITLE, ok_output)

                err_buffer = io.StringIO()
                with contextlib.redirect_stderr(err_buffer):
                    denied_code = main(
                        [
                            "share",
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
                self.assertEqual(denied_code, 2)
                self.assertIn(
                    "share: professional-sharing consent required",
                    err_buffer.getvalue(),
                )
            finally:
                if previous is None:
                    os.environ.pop("SOMATIC_CONSENT_PATH", None)
                else:
                    os.environ["SOMATIC_CONSENT_PATH"] = previous

    def test_cli_malformed_share_data_prints_a_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "packet.json"
            data_path.write_text("{not-json", encoding="utf-8")
            previous = os.environ.get("SOMATIC_CONSENT_PATH")
            os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp) / "consent.json")
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    code = main(
                        [
                            "share",
                            "--data",
                            str(data_path),
                            "--grant",
                            "analysis-insight,professional-sharing",
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
        self.assertIn("share: could not read --data:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
