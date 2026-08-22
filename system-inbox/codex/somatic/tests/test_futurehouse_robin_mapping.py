import ast
import contextlib
import importlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_DIR = REPO_ROOT / "fixtures" / "providers"
WORKFLOW_DIR = REPO_ROOT / "fixtures" / "workflows"


class FutureHouseRobinMappingTests(unittest.TestCase):
    def test_source_inspection_and_mapping_docs_exist(self):
        expected_docs = {
            "docs/robin-source-inspection.md": [
                "Apache-2.0",
                "Edison",
                "Crow",
                "Falcon",
                "Finch",
            ],
            "docs/aviary-source-inspection.md": [
                "Apache-2.0",
                "Environment",
                "Message",
                "ToolRequestMessage",
            ],
            "docs/ldp-source-inspection.md": [
                "Apache-2.0",
                "Agent",
                "RolloutManager",
                "compute_graph",
            ],
            "docs/futurehouse-robin-mapping.md": [
                "Crow",
                "Somatic literature providers",
                "Aviary-like environments",
                "LDP-like agent",
                "not used by Somatic core",
            ],
        }
        for relative, phrases in expected_docs.items():
            with self.subTest(relative=relative):
                text = (REPO_ROOT / relative).read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, text)

    def test_futurehouse_provider_fixtures_are_reference_only(self):
        expected = {
            "robin-provider-placeholder.json": (
                "C:\\AI\\external-sources\\somatic\\robin",
                "4a5cce310f3bc7663a67117db88af43b84733ffe",
            ),
            "aviary-provider-placeholder.json": (
                "C:\\AI\\external-sources\\somatic\\aviary",
                "826577f332a02ec2f5883cdb042fb12f14b4c7b3",
            ),
            "ldp-provider-placeholder.json": (
                "C:\\AI\\external-sources\\somatic\\ldp",
                "d49850ff3addb8369df062d345ea99991b7b200c",
            ),
        }
        for fixture_name, (source_path, commit) in expected.items():
            with self.subTest(fixture_name=fixture_name):
                payload = json.loads((PROVIDER_DIR / fixture_name).read_text(encoding="utf-8"))
                self.assertTrue(payload["reference_only"])
                self.assertTrue(payload["fake_backed"])
                self.assertTrue(payload["disabled_by_default"])
                self.assertEqual(payload["license"]["identifier"], "Apache-2.0")
                self.assertEqual(payload["local_path"], source_path)
                self.assertEqual(payload["inspected_commit"], commit)
                self.assertFalse(payload["external_runtime_enabled"])
                self.assertFalse(payload["limits"]["network_calls_allowed"])
                self.assertFalse(payload["limits"]["runtime_import_allowed"])
                self.assertFalse(payload["limits"]["live_execution_allowed"])
                self.assertFalse(payload["limits"]["basic_install_dependency"])

    def test_robin_provider_scaffold_imports_and_fails_closed_for_runtime(self):
        module = importlib.import_module("somatic.providers.robin")
        provider = module.RobinProvider()
        request = module.RobinPlanRequest(
            workflow_id="valid-robin-loop",
            goal="map local Robin loop boundary",
            evidence_refs=("evidence-fixture-001",),
        )

        plan = provider.plan(request)
        summary = provider.summarize(plan)

        self.assertEqual(provider.provider_id, "futurehouse-robin-reference")
        self.assertTrue(summary["reference_only"])
        self.assertTrue(summary["fake_backed"])
        self.assertFalse(summary["runtime_enabled"])
        self.assertEqual(summary["licenses"]["robin"], "Apache-2.0")
        self.assertEqual(plan.crow["maps_to"], "LiteratureProvider")
        self.assertEqual(plan.falcon["maps_to"], "MeasurementPlan")
        self.assertEqual(plan.finch["maps_to"], "StructuredVerdict")
        self.assertIn("Aviary", plan.environment["reference"])
        self.assertIn("LDP", plan.learning_process["reference"])

        with self.assertRaises(module.RobinRuntimeNotEnabledError):
            module.RobinProvider(
                module.RobinProviderConfig(enabled=True, mode="real", allow_runtime_execution=True)
            ).plan(request)

    def test_robin_provider_scaffold_has_no_network_or_external_imports(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "anthropic",
            "edison_client",
            "paperqa",
            "aviary",
            "ldp",
            "robin",
        }
        provider_file = REPO_ROOT / "somatic" / "providers" / "robin.py"
        tree = ast.parse(provider_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                self.assertTrue(imported.isdisjoint(forbidden_import_roots))
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                self.assertNotIn(node.module.split(".")[0], forbidden_import_roots)

    def test_existing_workflows_and_fabric_check_still_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            for fixture_name in (
                "valid-literature-only.yaml",
                "valid-hypothesis-tournament.yaml",
                "valid-robin-loop.yaml",
            ):
                with self.subTest(fixture_name=fixture_name):
                    run_dir = run_mock_workflow(
                        WORKFLOW_DIR / fixture_name,
                        repo_root=REPO_ROOT,
                        output_root=Path(tmp) / fixture_name,
                        run_id=f"run-phase5f-{fixture_name.removesuffix('.yaml')}",
                    )
                    self.assertTrue((run_dir / "manifest.json").exists())
                    self.assertTrue((run_dir / "artifacts" / "hypotheses.json").exists())
                    if fixture_name == "valid-robin-loop.yaml":
                        self.assertTrue(
                            (run_dir / "artifacts" / "finch_toolbelt_summary.json").exists()
                        )
                        self.assertTrue(
                            (run_dir / "artifacts" / "structured_verdict.json").exists()
                        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "signed-code-pack.json"),
                    "--keyring",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "keyring-signed.json"),
                ]
            )
        output = stdout.getvalue()
        expected = 0 if CRYPTO_AVAILABLE else 1
        self.assertEqual(exit_code, expected, output)
        if CRYPTO_AVAILABLE:
            self.assertIn("valid signed-code-pack.json", output)
            self.assertIn("crypto: publisher threshold verified", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())
            self.assertIn("failing closed", output.lower())
            self.assertIn("optional fabric extra", output.lower())

    def test_existing_provider_scaffolds_remain_import_only(self):
        modules = (
            "somatic.providers.paperqa2",
            "somatic.providers.scientific_agent_skills",
            "somatic.providers.team_orchestration",
        )
        for module_name in modules:
            with self.subTest(module_name=module_name):
                self.assertIsNotNone(importlib.import_module(module_name))


if __name__ == "__main__":
    unittest.main()
