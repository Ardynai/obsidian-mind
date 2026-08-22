"""Autonomous-science harness: consent, biosecurity, belief, falsifier."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import ANALYSIS_INSIGHT, AUTONOMOUS_RESEARCH, ConsentLedger
from somatic.safety.core import ConsentRequiredError
from somatic.science.belief import BeliefLedger
from somatic.science.biosecurity import screen_biosecurity
from somatic.science.harness import run_science_loop


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


class ScienceHarnessTests(unittest.TestCase):
    def test_requires_autonomous_research(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            run_science_loop(ledger, "sandbox ranking of local hypotheses")

    def test_requires_analysis_insight_as_well(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        with self.assertRaises(ConsentRequiredError):
            run_science_loop(ledger, "sandbox ranking of local hypotheses")

    def test_biosecurity_refuses_concern_names(self):
        hit = screen_biosecurity("plan a ricin pathway")
        self.assertTrue(hit.blocked)
        self.assertEqual(hit.matched, "ricin")
        miss = screen_biosecurity("sandbox ranking of provenance checks")
        self.assertFalse(miss.blocked)

    def test_science_loop_updates_belief_and_proposes_next(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        ledger.grant(ANALYSIS_INSIGHT)
        report = run_science_loop(ledger, "sandbox ranking of local provenance hypotheses", seed=2)
        self.assertEqual(report.blocked, "")
        self.assertTrue(report.ranked_hypothesis_id)
        self.assertIn(report.ranked_hypothesis_id, report.belief)
        self.assertGreater(report.belief[report.ranked_hypothesis_id]["updates"], 0)
        self.assertTrue(report.next_measurement.get("modality"))
        self.assertEqual(report.next_measurement.get("dollars"), 0.0)
        self.assertFalse(report.next_measurement.get("hardware_required"))

    def test_emergency_and_biosecurity_block_before_spend(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        ledger.grant(ANALYSIS_INSIGHT)
        er = run_science_loop(ledger, "sudden chest pain while resting")
        self.assertEqual(er.blocked, "emergency")
        bio = run_science_loop(ledger, "synthesize ricin in sandbox")
        self.assertEqual(bio.blocked, "biosecurity")

    def test_belief_entropy_drops_after_updates(self):
        ledger_belief = BeliefLedger()
        prior = ledger_belief.prior("h").entropy()
        ledger_belief.update("h", support=True, weight=2.0)
        self.assertLess(ledger_belief.prior("h").entropy(), prior)

    def test_cli_science_run(self):
        restore = _isolate()
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "science",
                        "run",
                        "--goal",
                        "sandbox ranking of local provenance hypotheses",
                        "--grant",
                        "autonomous-research,analysis-insight",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("science harness", out.getvalue().lower())
        finally:
            restore()


if __name__ == "__main__":
    unittest.main()
