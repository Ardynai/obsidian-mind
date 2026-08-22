"""Evidence Bus sandbox loop: all modalities, consent, emergency, no hardware."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import ANALYSIS_INSIGHT, ConsentLedger
from somatic.evidence_bus import EVIDENCE_MODALITIES, run_evidence_loop, sandbox_adapters
from somatic.evidence_bus.adapter import HypothesisSpec
from somatic.safety.core import ConsentRequiredError

REPO_ROOT = Path(__file__).resolve().parents[1]


def _isolate():
    tmp = tempfile.TemporaryDirectory()
    previous = os.environ.get("SOMATIC_CONSENT_PATH")

    def restore() -> None:
        tmp.cleanup()
        if previous is None:
            os.environ.pop("SOMATIC_CONSENT_PATH", None)
        else:
            os.environ["SOMATIC_CONSENT_PATH"] = previous

    os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp.name) / "consent.json")
    return restore


class EvidenceBusLoopTests(unittest.TestCase):
    def test_requires_analysis_insight(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            run_evidence_loop(
                ledger,
                HypothesisSpec(id="h1", statement="sandbox trend only"),
            )

    def test_all_modalities_are_sandbox_and_hashed(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = run_evidence_loop(
            ledger,
            HypothesisSpec(id="h-all", statement="sandbox multi-sensor observation"),
            seed=1,
        )
        self.assertFalse(report.emergency_triggered)
        modalities = {step.modality for step in report.steps}
        self.assertEqual(modalities, set(EVIDENCE_MODALITIES))
        for step in report.steps:
            self.assertEqual(len(step.sha256), 64)
            self.assertTrue(step.features.get("simulated"))
            self.assertFalse(step.features.get("hardware_access"))
            self.assertEqual(step.cost.dollars, 0.0)
            self.assertFalse(step.cost.hardware_required)
        self.assertIn("sandbox", report.verdict.summary.lower())

    def test_emergency_short_circuits_without_acquire(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = run_evidence_loop(
            ledger,
            HypothesisSpec(id="er", statement="sudden chest pain while resting"),
        )
        self.assertTrue(report.emergency_triggered)
        self.assertEqual(report.steps, ())
        self.assertIn("emergency", report.verdict.summary.lower())

    def test_cli_bus_run_and_missing_consent(self):
        restore = _isolate()
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                denied = main(["bus", "run", "--hypothesis", "sandbox observation"])
            self.assertEqual(denied, 2)
            self.assertIn("analysis-insight consent required", err.getvalue())
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "bus",
                        "run",
                        "--hypothesis",
                        "sandbox observation of local fixture trends",
                        "--modalities",
                        "csi,wearable",
                        "--grant",
                        "analysis-insight",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("Evidence Bus", out.getvalue())
            self.assertIn("csi:", out.getvalue())
        finally:
            restore()

    def test_adapters_cover_catalog(self):
        self.assertEqual(set(sandbox_adapters()), set(EVIDENCE_MODALITIES))

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])

    def test_doctor_reports_masterplan_sandbox_status(self):
        from tests.doctor_fixture import DOCTOR_RESULT

        exit_code, output = DOCTOR_RESULT
        self.assertEqual(exit_code, 0)
        self.assertIn("Master-plan Evidence Bus:", output)
        self.assertIn("Master-plan sensor roster:", output)
        self.assertIn("hardware closed", output.lower())
        lowered = output.lower()
        for forbidden in ("bluetooth_mac", "serial_number", "raw_acoustic", "fixtures/sensors"):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
