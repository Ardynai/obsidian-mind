import unittest

from somatic.evidence_bus import (
    EVIDENCE_MODALITIES,
    EvidenceSource,
    MeasurementPlan,
    RawEvidence,
    StructuredVerdict,
)


class EvidenceBusTests(unittest.TestCase):
    def test_declares_master_plan_modalities(self):
        self.assertEqual(
            EVIDENCE_MODALITIES,
            {
                "sim",
                "wetlab",
                "csi",
                "video",
                "video3d",
                "thermal",
                "audio",
                "wearable",
                "environmental",
                "literature",
            },
        )

    def test_dataclasses_are_lightweight_contracts(self):
        source = EvidenceSource(
            id="src-literature",
            modality="literature",
            provider_ref="mock-literature-provider",
            description="Fixture source",
        )
        plan = MeasurementPlan(
            id="plan-001",
            sources=[source],
            objective="Collect offline fixture evidence.",
        )
        raw = RawEvidence(
            id="raw-001",
            source=source,
            payload_ref="fixture://evidence/sample",
            sha256="a" * 64,
        )
        verdict = StructuredVerdict(
            id="verdict-001",
            raw_evidence_refs=[raw.id],
            summary="Fixture verdict.",
            confidence="low",
        )

        self.assertEqual(plan.sources[0].modality, "literature")
        self.assertEqual(raw.source.id, "src-literature")
        self.assertEqual(verdict.raw_evidence_refs, ["raw-001"])

    def test_rejects_unknown_modality(self):
        with self.assertRaises(ValueError):
            EvidenceSource(
                id="src-unknown",
                modality="unsupported",
                provider_ref="mock",
                description="Invalid source",
            )


if __name__ == "__main__":
    unittest.main()
