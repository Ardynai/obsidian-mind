"""Adversarial corpus for emergency_screen and frame_advisory (CI gate)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from somatic.consent import AI_ADVISORY, ANALYSIS_INSIGHT, ConsentLedger
from somatic.flows.analyze import analyze_user_data
from somatic.safety.core import (
    CRISIS_GUIDANCE,
    CRISIS_GUIDANCE_ES,
    CRISIS_GUIDANCE_FR,
    LANGUAGE_SCOPE,
    AdvisoryFramingError,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "fixtures" / "safety" / "adversarial_corpus.json"
CRISIS_GUIDANCE_BY_LOCALE = {
    "en": CRISIS_GUIDANCE,
    "es": CRISIS_GUIDANCE_ES,
    "fr": CRISIS_GUIDANCE_FR,
}


def _load_cases() -> list[dict]:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    return list(payload["cases"])


class AdversarialCorpusTests(unittest.TestCase):
    def test_corpus_covers_bypass_and_overmatch_families(self):
        kinds = {case["kind"] for case in _load_cases()}
        self.assertGreaterEqual(len(_load_cases()), 20)
        self.assertTrue({"framing_error", "emergency_medical", "emergency_crisis", "pass"} <= kinds)
        ids = [case["id"] for case in _load_cases()]
        self.assertTrue(any(case_id.startswith("es-") for case_id in ids))
        self.assertTrue(any(case_id.startswith("fr-") for case_id in ids))

    def test_language_scope_documents_multi_lexicon_support(self):
        from somatic.safety.core import CRISIS_LINE_POLICY

        payload = json.loads(CORPUS.read_text(encoding="utf-8"))
        self.assertEqual(payload["language_scope"], LANGUAGE_SCOPE)
        self.assertEqual(payload["crisis_line_policy"], CRISIS_LINE_POLICY)

    def test_spanish_red_flags_trigger_with_locale_routing(self):
        medical = emergency_screen("dolor de pecho intenso")
        self.assertTrue(medical.triggered)
        self.assertEqual(medical.kind, "medical")
        self.assertEqual(medical.locale, "es")
        self.assertIn("emergencias", medical.guidance.lower())
        crisis = emergency_screen("estoy pensando en suicidarme")
        self.assertTrue(crisis.triggered)
        self.assertEqual(crisis.kind, "crisis")
        self.assertEqual(crisis.locale, "es")
        self.assertIn("988", crisis.guidance)
        self.assertIn("024", crisis.guidance)
        self.assertIn("3114", crisis.guidance)
        with self.assertRaises(AdvisoryFramingError):
            frame_advisory(
                summary="Tus resultados indican un problema grave confirmado.",
                evidence_grade=EvidenceGrade.LIMITED,
                sources=("corpus",),
                consent_scope=AI_ADVISORY,
            )

    def test_french_red_flags_trigger_with_locale_routing(self):
        medical = emergency_screen("je n'arrive pas à respirer")
        self.assertTrue(medical.triggered)
        self.assertEqual(medical.kind, "medical")
        self.assertEqual(medical.locale, "fr")
        self.assertIn("urgence", medical.guidance.lower())
        crisis = emergency_screen("j'ai des pensées suicidaires")
        self.assertTrue(crisis.triggered)
        self.assertEqual(crisis.kind, "crisis")
        self.assertEqual(crisis.locale, "fr")
        self.assertIn("3114", crisis.guidance)
        with self.assertRaises(AdvisoryFramingError):
            frame_advisory(
                summary="Je vous prescris de la metformine pour ce schéma.",
                evidence_grade=EvidenceGrade.LIMITED,
                sources=("corpus",),
                consent_scope=AI_ADVISORY,
            )

    def test_each_corpus_case(self):
        for case in _load_cases():
            with self.subTest(case_id=case["id"]):
                text = case["text"]
                kind = case["kind"]
                emergency = emergency_screen(text)
                if kind == "emergency_medical":
                    self.assertTrue(emergency.triggered)
                    self.assertEqual(emergency.kind, "medical")
                    self.assertIn(
                        emergency.locale,
                        {"en", "es", "fr"},
                    )
                    self.assertTrue(
                        any(
                            word in emergency.guidance.lower()
                            for word in ("emergency", "emergencia", "urgence")
                        ),
                        emergency.guidance,
                    )
                    continue
                if kind == "emergency_crisis":
                    self.assertTrue(emergency.triggered)
                    self.assertEqual(emergency.kind, "crisis")
                    self.assertIn(
                        emergency.guidance,
                        set(CRISIS_GUIDANCE_BY_LOCALE.values()),
                    )
                    self.assertIn(
                        emergency.guidance,
                        [CRISIS_GUIDANCE_BY_LOCALE[emergency.locale]],
                    )
                    continue
                self.assertFalse(emergency.triggered, emergency.guidance)
                if kind == "framing_error":
                    with self.assertRaises(AdvisoryFramingError):
                        frame_advisory(
                            summary=text,
                            evidence_grade=EvidenceGrade.LIMITED,
                            sources=("corpus",),
                            consent_scope=AI_ADVISORY,
                        )
                elif kind == "pass":
                    result = frame_advisory(
                        summary=text,
                        evidence_grade=EvidenceGrade.LIMITED,
                        sources=("corpus",),
                        consent_scope=AI_ADVISORY,
                    )
                    self.assertEqual(result.summary, text.strip())
                else:
                    self.fail(f"unknown corpus kind: {kind}")

    def test_analyze_does_not_crash_on_benign_metric_names(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        for metric in ("prescribed dose", "things you have logged", "meds you stop taking"):
            with self.subTest(metric=metric):
                report = analyze_user_data(
                    ledger,
                    {metric: [1, 2, 3, 4]},
                    "What patterns stand out?",
                    baselines={metric: [1, 1.2, 1.1, 0.9]},
                )
                self.assertIsInstance(report.notes, tuple)


if __name__ == "__main__":
    unittest.main()
