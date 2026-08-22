import json
import unittest
from pathlib import Path

from somatic.providers.biomodel import (
    BiomodelPlan,
    BiomodelRequest,
    BiomodelResult,
    biomodel_result_to_evidence_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class BiomodelProviderBoundaryTests(unittest.TestCase):
    def test_biomodel_plan_result_and_evidence_mapping_are_serializable(self):
        request = BiomodelRequest(
            objective="Plan a local biomodel run.",
            target_refs=("target://protein-ligand",),
            input_artifact_refs=("fixture://input.yaml",),
            constraints={"allow_network": False},
        )
        plan = BiomodelPlan(
            id="plan-001",
            provider_id="mock-biomodel",
            request_id="request-001",
            objective=request.objective,
            status="planned-not-executed",
            model_family="mock-family",
            model_version="mock-v1",
            blocked_actions=("download model", "call network"),
        )
        result = BiomodelResult(
            id="result-001",
            status="mock-planned-not-executed",
            artifact_refs=("mock://result.json",),
            evidence_refs=("mock://evidence",),
            limitations=("No real prediction was executed.",),
            metadata={"sha256": "a" * 64, "mock": True, "runtime_execution": False},
        )

        record = biomodel_result_to_evidence_record(
            request,
            result,
            provider_id="mock-biomodel",
        )

        self.assertEqual(plan.to_dict()["status"], "planned-not-executed")
        self.assertEqual(record.raw_evidence.source.modality, "sim")
        self.assertEqual(record.raw_evidence.source.metadata["submodality"], "biomodel")
        self.assertFalse(record.raw_evidence.metadata["runtime_execution"])
        self.assertFalse(record.raw_evidence.metadata["model_downloads"])
        self.assertFalse(record.raw_evidence.metadata["msa_server"])
        self.assertFalse(record.raw_evidence.metadata["network_calls"])
        self.assertFalse(record.raw_evidence.metadata["gpu_execution"])
        self.assertEqual(record.structured_verdict.confidence, "not-applicable")
        json.dumps(record.to_dict(), sort_keys=True)

    def test_biomodel_fixtures_parse_and_stay_metadata_only(self):
        fixture_names = (
            "biomodel-request-placeholder.json",
            "biomodel-plan-placeholder.json",
            "biomodel-result-placeholder.json",
        )

        for fixture_name in fixture_names:
            with self.subTest(fixture_name=fixture_name):
                payload = json.loads(
                    (REPO_ROOT / "fixtures" / "biomodel" / fixture_name).read_text(encoding="utf-8")
                )

                metadata = payload.get("metadata", payload)
                self.assertFalse(metadata.get("runtime_execution", False))
                self.assertFalse(metadata.get("model_downloads", False))
                self.assertFalse(metadata.get("network_calls", False))
                self.assertFalse(metadata.get("gpu_execution", False))


if __name__ == "__main__":
    unittest.main()
