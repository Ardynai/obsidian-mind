"""Tests for the consent catalog, ledger, and safety core."""

from __future__ import annotations

import json
import unittest

from somatic.consent import (
    AI_ADVISORY,
    ANALYSIS_INSIGHT,
    AUTONOMOUS_RESEARCH,
    CONSENT_SCOPES,
    DATA_INGESTION,
    PROACTIVE_SUGGESTIONS,
    PROFESSIONAL_SHARING,
    REMEDY_LIBRARY,
    ConsentLedger,
)
from somatic.safety.core import (
    INFORMATIONAL_NOTICE,
    AdvisoryFramingError,
    AdvisoryResult,
    ConsentRequiredError,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
    require_consent,
)


class ConsentScopeCatalogTests(unittest.TestCase):
    def test_catalog_contains_required_scopes(self):
        ids = {scope.id for scope in CONSENT_SCOPES}
        self.assertEqual(
            ids,
            {
                DATA_INGESTION.id,
                ANALYSIS_INSIGHT.id,
                AI_ADVISORY.id,
                AUTONOMOUS_RESEARCH.id,
                PROACTIVE_SUGGESTIONS.id,
                PROFESSIONAL_SHARING.id,
                REMEDY_LIBRARY.id,
            },
        )

    def test_scopes_default_off(self):
        ledger = ConsentLedger()
        for scope in CONSENT_SCOPES:
            with self.subTest(scope=scope.id):
                self.assertFalse(ledger.is_granted(scope))
        self.assertEqual(ledger.granted_scopes(), ())


class ConsentLedgerTests(unittest.TestCase):
    def test_grant_revoke_is_granted(self):
        ledger = ConsentLedger()
        self.assertFalse(ledger.is_granted(AI_ADVISORY))
        ledger.grant(AI_ADVISORY, actor="user")
        self.assertTrue(ledger.is_granted(AI_ADVISORY))
        self.assertEqual(ledger.granted_scopes(), (AI_ADVISORY,))
        ledger.revoke(AI_ADVISORY)
        self.assertFalse(ledger.is_granted(AI_ADVISORY))
        self.assertEqual(ledger.granted_scopes(), ())

    def test_round_trip_to_dict_from_dict(self):
        ledger = ConsentLedger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        ledger.revoke(DATA_INGESTION)
        payload = ledger.to_dict()
        encoded = json.dumps(payload)
        restored = ConsentLedger.from_dict(json.loads(encoded))
        self.assertFalse(restored.is_granted(DATA_INGESTION))
        self.assertTrue(restored.is_granted(ANALYSIS_INSIGHT))
        self.assertEqual(restored.to_dict()["grants"], payload["grants"])
        self.assertEqual(len(restored.to_dict()["events"]), len(payload["events"]))

    def test_purge_user_data_clears_grants_and_events(self):
        ledger = ConsentLedger()
        ledger.grant(REMEDY_LIBRARY)
        ledger.purge_user_data()
        self.assertEqual(ledger.granted_scopes(), ())
        self.assertEqual(ledger.to_dict()["events"], [])
        self.assertEqual(ledger.to_dict()["grants"], {})


class RequireConsentTests(unittest.TestCase):
    def test_raises_when_ungranted(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError) as ctx:
            require_consent(ledger, AI_ADVISORY)
        self.assertEqual(ctx.exception.scope_id, AI_ADVISORY.id)

    def test_passes_when_granted(self):
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        self.assertIsNone(require_consent(ledger, AI_ADVISORY))


class EmergencyScreenTests(unittest.TestCase):
    def test_triggers_on_red_flag_text(self):
        for text in (
            "Sudden chest pain while resting",
            "Difficulty breathing after exercise",
            "Possible stroke with facial droop",
            "Suicidal thoughts tonight",
            "Signs of anaphylaxis after food",
            "Severe bleeding that will not stop",
        ):
            with self.subTest(text=text):
                result = emergency_screen(text)
                self.assertTrue(result.triggered)
                self.assertIn("emergency", result.guidance.lower())

    def test_does_not_trigger_on_benign_text(self):
        result = emergency_screen(
            "Resting heart-rate trends look steadier this week than last week."
        )
        self.assertFalse(result.triggered)
        self.assertEqual(result.guidance, "")


class FrameAdvisoryTests(unittest.TestCase):
    def test_attaches_notice_grade_and_routing(self):
        result = frame_advisory(
            summary="Sleep duration correlates with next-day energy ratings in your log.",
            evidence_grade=EvidenceGrade.MODERATE,
            sources=("local-sleep-log", "local-energy-ratings"),
            consent_scope=AI_ADVISORY,
        )
        self.assertIsInstance(result, AdvisoryResult)
        self.assertEqual(result.evidence_grade, EvidenceGrade.MODERATE)
        self.assertEqual(result.informational_notice, INFORMATIONAL_NOTICE)
        self.assertIn("licensed", result.professional_routing.lower())
        self.assertEqual(result.consent_scope, AI_ADVISORY.id)
        self.assertEqual(result.sources, ("local-sleep-log", "local-energy-ratings"))

    def test_raises_on_authoritative_diagnosis_phrasing(self):
        for summary in (
            "You have diabetes based on these readings.",
            "You were diagnosed with hypertension yesterday.",
            "Take 500 mg of ibuprofen every six hours.",
            "I prescribe metformin for this pattern.",
            "Stop taking your current medication immediately.",
            "Diagnosis: type 2 diabetes.",
            "Take 12 mg.",
        ):
            with self.subTest(summary=summary):
                with self.assertRaises(AdvisoryFramingError):
                    frame_advisory(
                        summary=summary,
                        evidence_grade=EvidenceGrade.LIMITED,
                        sources=("fixture",),
                        consent_scope=AI_ADVISORY,
                    )

    def test_advisory_result_to_dict_round_trip_shape(self):
        result = frame_advisory(
            summary="Hydration notes appear lower on high-activity days.",
            evidence_grade=EvidenceGrade.PRELIMINARY,
            sources=("hydration-log",),
            consent_scope=ANALYSIS_INSIGHT,
        )
        payload = result.to_dict()
        self.assertEqual(payload["summary"], result.summary)
        self.assertEqual(payload["evidence_grade"], EvidenceGrade.PRELIMINARY)
        self.assertEqual(payload["sources"], ["hydration-log"])
        self.assertEqual(payload["informational_notice"], INFORMATIONAL_NOTICE)
        self.assertEqual(payload["consent_scope"], ANALYSIS_INSIGHT.id)
        self.assertEqual(
            set(payload),
            {
                "summary",
                "evidence_grade",
                "sources",
                "professional_routing",
                "informational_notice",
                "consent_scope",
            },
        )


if __name__ == "__main__":
    unittest.main()
