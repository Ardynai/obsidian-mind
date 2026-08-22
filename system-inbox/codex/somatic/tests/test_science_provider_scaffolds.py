import ast
import importlib
import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_MODULES = (
    "somatic.providers",
    "somatic.providers.literature",
    "somatic.providers.paperqa2",
    "somatic.providers.robin",
    "somatic.providers.science_skills",
    "somatic.providers.scientific_agent_skills",
    "somatic.providers.biomodel",
    "somatic.providers.boltz",
    "somatic.providers.team_orchestration",
)
PLACEHOLDER_FIXTURES = (
    "paperqa2-provider-placeholder.json",
    "scientific-agent-skills-provider-placeholder.json",
    "finch-extras-provider-placeholder.json",
    "robin-provider-placeholder.json",
    "aviary-provider-placeholder.json",
    "ldp-provider-placeholder.json",
    "autoscientists-provider-placeholder.json",
    "boltz2-provider-placeholder.json",
)


class ScienceProviderScaffoldTests(unittest.TestCase):
    def test_provider_placeholder_fixtures_parse_and_stay_disabled(self):
        for fixture_name in PLACEHOLDER_FIXTURES:
            with self.subTest(fixture_name=fixture_name):
                payload = json.loads(
                    (REPO_ROOT / "fixtures" / "providers" / fixture_name).read_text(
                        encoding="utf-8"
                    )
                )

                self.assertFalse(payload["external_runtime_enabled"])
                self.assertIn("local_repo_inspected", payload)
                if payload["local_repo_inspected"]:
                    self.assertTrue(payload["local_path"])
                    self.assertRegex(payload.get("inspected_commit", ""), r"^[0-9a-f]{40}$")
                self.assertEqual(payload["auth"]["type"], "none")
                self.assertEqual(payload["auth"]["secrets_required"], [])
                self.assertFalse(payload["limits"]["network_calls_allowed"])
                self.assertFalse(payload["limits"]["runtime_import_allowed"])
                self.assertFalse(payload["limits"]["basic_install_dependency"])
                self.assertGreaterEqual(len(payload["capabilities"]), 1)

    def test_provider_modules_import_without_external_dependencies(self):
        for module_name in PROVIDER_MODULES:
            with self.subTest(module_name=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_no_external_network_or_api_surfaces_are_introduced(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "paperqa",
            "futurehouse",
            "scientific_agent_skills",
            "autoscientists",
            "aviary",
            "ldp",
            "boltz",
        }
        forbidden_call_names = {"urlopen", "request", "create_connection"}
        provider_files = [
            REPO_ROOT / "somatic" / "providers" / "__init__.py",
            REPO_ROOT / "somatic" / "providers" / "literature.py",
            REPO_ROOT / "somatic" / "providers" / "paperqa2.py",
            REPO_ROOT / "somatic" / "providers" / "robin.py",
            REPO_ROOT / "somatic" / "providers" / "science_skills.py",
            REPO_ROOT / "somatic" / "providers" / "scientific_agent_skills.py",
            REPO_ROOT / "somatic" / "providers" / "biomodel.py",
            REPO_ROOT / "somatic" / "providers" / "boltz.py",
            REPO_ROOT / "somatic" / "providers" / "team_orchestration.py",
        ]

        for path in provider_files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = {alias.name.split(".")[0] for alias in node.names}
                    self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    module = node.module.split(".")[0]
                    self.assertNotIn(module, forbidden_import_roots)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden_call_names)

    def test_existing_workflows_still_run(self):
        fixtures = (
            "valid-literature-only.yaml",
            "valid-hypothesis-tournament.yaml",
            "valid-robin-loop.yaml",
        )
        with tempfile.TemporaryDirectory() as tmp:
            for fixture_name in fixtures:
                with self.subTest(fixture_name=fixture_name):
                    run_dir = run_mock_workflow(
                        REPO_ROOT / "fixtures" / "workflows" / fixture_name,
                        repo_root=REPO_ROOT,
                        output_root=Path(tmp) / fixture_name,
                        run_id=f"run-{fixture_name.removesuffix('.yaml')}",
                    )
                    self.assertTrue((run_dir / "manifest.json").exists())
                    self.assertTrue((run_dir / "artifacts" / "hypotheses.json").exists())


if __name__ == "__main__":
    unittest.main()
