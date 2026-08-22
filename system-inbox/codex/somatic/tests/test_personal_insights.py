"""Tests for the consent-gated personal insights engine."""

from __future__ import annotations

import ast
import tomllib
import unittest
from pathlib import Path

from somatic.consent import ANALYSIS_INSIGHT, ConsentLedger
from somatic.insights import (
    ReferenceRange,
    grade_metric,
    summarize_series,
)
from somatic.safety.core import (
    INFORMATIONAL_NOTICE,
    ConsentRequiredError,
    EvidenceGrade,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = REPO_ROOT / "somatic" / "insights" / "engine.py"


class PersonalInsightsEngineTests(unittest.TestCase):
    def test_requires_analysis_insight_consent(self):
        ledger = ConsentLedger()
        reference = ReferenceRange(
            metric="resting_hr",
            low=50.0,
            high=90.0,
            unit="bpm",
            source="user-provided-clinician-note",
        )
        with self.assertRaises(ConsentRequiredError):
            grade_metric(ledger, "resting_hr", 95, reference=reference)
        with self.assertRaises(ConsentRequiredError):
            summarize_series(ledger, "resting_hr", [60, 62, 70])

    def test_classifies_provided_reference_range(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        reference = ReferenceRange(
            metric="glucose_mg_dl",
            low=70.0,
            high=100.0,
            unit="mg/dL",
            source="user-supplied-lab-printout",
        )
        above = grade_metric(ledger, "glucose_mg_dl", 120, reference=reference)
        below = grade_metric(ledger, "glucose_mg_dl", 60, reference=reference)
        within = grade_metric(ledger, "glucose_mg_dl", 85, reference=reference)

        self.assertIn("above the reference range you provided", above.summary.lower())
        self.assertIn("below the reference range you provided", below.summary.lower())
        self.assertIn("within the reference range you provided", within.summary.lower())
        for result in (above, below, within):
            self.assertEqual(result.informational_notice, INFORMATIONAL_NOTICE)
            self.assertEqual(result.consent_scope, ANALYSIS_INSIGHT.id)
            self.assertEqual(result.evidence_grade, EvidenceGrade.PRELIMINARY)

    def test_flags_baseline_deviation_outlier(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        baseline = [70, 72, 71, 69, 70, 73, 71, 70]
        result = grade_metric(
            ledger,
            "resting_hr",
            95,
            baseline_values=baseline,
        )
        self.assertIn("sd", result.summary.lower())
        self.assertIn("95", result.summary)
        self.assertIn("above your own", result.summary.lower())
        self.assertIn("licensed professional", result.summary.lower())
        self.assertEqual(result.informational_notice, INFORMATIONAL_NOTICE)
        self.assertIn(
            result.evidence_grade,
            {EvidenceGrade.LIMITED, EvidenceGrade.MODERATE},
        )

    def test_summarize_series_detects_rising_trend(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        result = summarize_series(
            ledger,
            "steps",
            [1000, 1200, 1500, 1800, 2200, 2600],
        )
        self.assertIn("rising", result.summary.lower())
        self.assertIn("latest 2600", result.summary)
        self.assertEqual(result.informational_notice, INFORMATIONAL_NOTICE)
        self.assertEqual(result.consent_scope, ANALYSIS_INSIGHT.id)
        self.assertIn(
            result.evidence_grade,
            {EvidenceGrade.LIMITED, EvidenceGrade.MODERATE},
        )

    def test_small_n_z_score_is_annotated(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        result = grade_metric(
            ledger,
            "resting_hr",
            80,
            baseline_values=[70, 72, 71],
        )
        self.assertIn("80", result.summary)
        self.assertIn("small personal series", result.summary.lower())

    def test_every_result_carries_informational_notice(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        reference = ReferenceRange(
            metric="sleep_hours",
            low=6.0,
            high=9.0,
            unit="hours",
            source="user-goal-setting",
        )
        results = [
            grade_metric(ledger, "sleep_hours", 7.5, reference=reference),
            grade_metric(
                ledger,
                "sleep_hours",
                5.0,
                reference=reference,
                baseline_values=[7.0, 7.2, 6.8, 7.1, 7.0],
            ),
            summarize_series(ledger, "sleep_hours", [7.0, 6.8, 6.5, 6.2, 6.0]),
        ]
        for result in results:
            with self.subTest(summary=result.summary[:40]):
                self.assertEqual(result.informational_notice, INFORMATIONAL_NOTICE)

    def test_reference_range_requires_caller_supplied_bounds(self):
        with self.assertRaises(TypeError):
            ReferenceRange(metric="hr", unit="bpm", source="x")  # type: ignore[call-arg]
        with self.assertRaises(ValueError):
            ReferenceRange(metric="hr", low=90, high=50, unit="bpm", source="user")
        with self.assertRaises(ValueError):
            ReferenceRange(metric="", low=1, high=2, unit="u", source="user")
        with self.assertRaises(ValueError):
            ReferenceRange(metric="hr", low=1, high=2, unit="u", source="")

    def test_engine_has_no_hardcoded_medical_normals(self):
        source = ENGINE_PATH.read_text(encoding="utf-8")
        lowered = source.lower()
        forbidden_fragments = (
            "normal range",
            "population normal",
            "clinical normal",
            "standard medical",
            "who guideline",
            "aha guideline",
            "lab normal",
        )
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, lowered)

        # No module-level numeric "normal" constants that look like medical defaults.
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "normal" in target.id.lower():
                        self.fail(f"unexpected normal-like constant: {target.id}")

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
