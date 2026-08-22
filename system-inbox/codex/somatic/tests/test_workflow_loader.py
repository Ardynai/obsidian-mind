import unittest
from pathlib import Path

from somatic.workflow_loader import (
    WorkflowValidationError,
    load_mock_provider_metadata,
    load_workflow,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class WorkflowLoaderTests(unittest.TestCase):
    def test_loads_valid_literature_workflow_with_required_fields(self):
        workflow = load_workflow(
            REPO_ROOT / "fixtures" / "workflows" / "valid-literature-only.yaml"
        )

        self.assertEqual(workflow["mode"], "literature-only")
        self.assertEqual(workflow["id"], "valid-literature-only")
        for field in (
            "schema_version",
            "id",
            "title",
            "mode",
            "description",
            "version",
            "status",
            "stages",
            "inputs",
            "providers",
            "artifacts",
            "safety_profile",
            "evidence_requirements",
            "output_packet",
        ):
            self.assertIn(field, workflow)

    def test_rejects_workflow_missing_mode(self):
        with self.assertRaisesRegex(WorkflowValidationError, "mode"):
            load_workflow(REPO_ROOT / "fixtures" / "workflows" / "invalid-missing-mode.yaml")

    def test_loads_mock_provider_metadata_for_referenced_classes(self):
        workflow = load_workflow(
            REPO_ROOT / "fixtures" / "workflows" / "valid-literature-only.yaml"
        )

        providers = load_mock_provider_metadata(workflow, REPO_ROOT)

        self.assertEqual(providers["literature"]["id"], "mock-literature-provider")
        self.assertEqual(providers["report"]["id"], "mock-report-provider")
        self.assertTrue(providers["literature"]["offline_supported"])
        self.assertFalse(providers["report"]["limits"]["network_calls_allowed"])


if __name__ == "__main__":
    unittest.main()
