import ast
import json
import unittest
from pathlib import Path

from somatic.providers.team_orchestration import (
    AutoScientistsRuntimeNotEnabledError,
    AutoScientistsTeamOrchestrationProvider,
    AutoScientistsTeamOrchestrationProviderConfig,
    TeamOrchestrationRequest,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = REPO_ROOT / "fixtures" / "providers" / "autoscientists-provider-placeholder.json"
PROVIDER_MODULE = REPO_ROOT / "somatic" / "providers" / "team_orchestration.py"


class TeamOrchestrationProviderScaffoldTests(unittest.TestCase):
    def test_autoscientists_provider_is_reference_only_and_fake_backed(self):
        provider = AutoScientistsTeamOrchestrationProvider()
        request = TeamOrchestrationRequest(
            hypothesis_refs=("hyp-a-r1", "hyp-b-r1"),
            evidence_refs=("evidence-fixture-001",),
            requested_roles=("GeneratorTeam", "FalsifierTeam"),
        )

        plan = provider.plan(request)
        summary = provider.summarize(plan)

        self.assertEqual(provider.provider_id, "autoscientists-reference")
        self.assertTrue(provider.offline_supported)
        self.assertTrue(summary["reference_only"])
        self.assertTrue(summary["fake_backed"])
        self.assertFalse(summary["runtime_enabled"])
        self.assertFalse(summary["runtime_import_allowed"])
        self.assertEqual(summary["license_status"], "unresolved-no-license-file-found")
        self.assertEqual(
            plan.metadata["inspected_commit"], "c71a92343b9a488ed10134be805845b9473ad18f"
        )
        self.assertEqual(plan.metadata["mode"], "mock")
        self.assertGreaterEqual(len(plan.team_members), 2)
        self.assertIn("critique-before-evidence", plan.critique_steps)

    def test_autoscientists_provider_rejects_live_execution(self):
        with self.assertRaises(AutoScientistsRuntimeNotEnabledError):
            AutoScientistsTeamOrchestrationProvider(
                AutoScientistsTeamOrchestrationProviderConfig(
                    enabled=True,
                    mode="real",
                    allow_runtime_execution=True,
                )
            ).plan(TeamOrchestrationRequest(hypothesis_refs=("hyp-a-r1",)))

    def test_provider_placeholder_records_disabled_license_boundary(self):
        payload = json.loads(PLACEHOLDER.read_text(encoding="utf-8"))

        self.assertTrue(payload["reference_only"])
        self.assertTrue(payload["fake_backed"])
        self.assertTrue(payload["disabled_by_default"])
        self.assertFalse(payload["external_runtime_enabled"])
        self.assertEqual(
            payload["license_status"]["status"],
            "unresolved-no-license-file-found",
        )
        self.assertFalse(payload["limits"]["network_calls_allowed"])
        self.assertFalse(payload["limits"]["runtime_import_allowed"])
        self.assertFalse(payload["limits"]["live_execution_allowed"])
        self.assertFalse(payload["limits"]["basic_install_dependency"])

    def test_provider_scaffold_has_no_network_or_external_runtime_imports(self):
        forbidden_import_roots = (
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "langgraph",
            "clawinstitute",
        )
        tree = ast.parse(PROVIDER_MODULE.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name.split(".")[0] for alias in node.names]
                for module in imported:
                    with self.subTest(module=module):
                        self.assertNotIn(module, forbidden_import_roots)
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module.split(".")[0]
                with self.subTest(module=module):
                    self.assertNotIn(module, forbidden_import_roots)


if __name__ == "__main__":
    unittest.main()
