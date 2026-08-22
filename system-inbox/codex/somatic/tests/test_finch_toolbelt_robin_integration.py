import ast
import importlib
import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
ROBIN_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-robin-loop.yaml"
LITERATURE_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-literature-only.yaml"
TOURNAMENT_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-hypothesis-tournament.yaml"


class FinchToolbeltRobinIntegrationTests(unittest.TestCase):
    def test_robin_loop_writes_finch_toolbelt_artifacts_and_report_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                ROBIN_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-phase5d-robin-test",
            )

            expected_artifacts = {
                "finch_toolbelt_summary": "artifacts/finch_toolbelt_summary.json",
                "table_profile": "artifacts/table_profile.json",
                "dose_response_summary": "artifacts/dose_response_summary.json",
                "analysis_provenance": "artifacts/analysis_provenance.json",
            }
            parsed = {}
            for key, relative in expected_artifacts.items():
                path = run_dir / relative
                self.assertTrue(path.exists(), relative)
                parsed[key] = json.loads(path.read_text(encoding="utf-8"))

            summary = parsed["finch_toolbelt_summary"]
            profile = parsed["table_profile"]
            dose = parsed["dose_response_summary"]
            provenance = parsed["analysis_provenance"]
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")

            self.assertEqual(summary["agent_role"], "Finch")
            self.assertEqual(summary["toolbelt_status"], "standard-library-local")
            self.assertEqual(summary["table_count"], 2)
            self.assertTrue(summary["dose_response_available"])
            self.assertEqual(profile["table_count"], 2)
            self.assertEqual(profile["tables"][0]["row_count"], 4)
            self.assertEqual(dose["trend_direction"], "increasing")
            self.assertEqual(dose["baseline_vs_highest_delta"], 15.0)
            self.assertEqual(provenance["network_calls"], False)
            self.assertEqual(
                manifest["artifacts"]["finch_toolbelt_summary"],
                "artifacts/finch_toolbelt_summary.json",
            )
            self.assertEqual(
                manifest["artifacts"]["analysis_provenance"], "artifacts/analysis_provenance.json"
            )

            for expected in (
                "Finch Toolbelt Summary",
                "Table Profile Summary",
                "Dose-Response Summary",
                "Analysis Provenance",
                "standard-library local analysis only",
                "not medical advice",
                "not a real scientific conclusion",
            ):
                with self.subTest(expected=expected):
                    self.assertIn(expected, report)

    def test_existing_workflows_and_provider_scaffolds_still_work(self):
        importlib.import_module("somatic.providers.paperqa2")
        importlib.import_module("somatic.providers.scientific_agent_skills")

        with tempfile.TemporaryDirectory() as tmp:
            literature = run_mock_workflow(
                LITERATURE_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp) / "literature",
                run_id="run-literature",
            )
            tournament = run_mock_workflow(
                TOURNAMENT_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp) / "tournament",
                run_id="run-tournament",
            )
            robin = run_mock_workflow(
                ROBIN_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp) / "robin",
                run_id="run-robin",
            )

            self.assertTrue((literature / "artifacts" / "hypotheses.json").exists())
            self.assertTrue((tournament / "artifacts" / "ranked_hypotheses.json").exists())
            self.assertTrue((robin / "artifacts" / "finch_toolbelt_summary.json").exists())

    def test_new_robin_toolbelt_runtime_has_no_network_or_external_api_surfaces(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "paperqa",
            "scientific_agent_skills",
            "pandas",
            "numpy",
            "scipy",
        }
        runtime_files = [
            REPO_ROOT / "somatic" / "analysis" / "__init__.py",
            REPO_ROOT / "somatic" / "analysis" / "tables.py",
            REPO_ROOT / "somatic" / "analysis" / "statistics.py",
            REPO_ROOT / "somatic" / "analysis" / "dose_response.py",
            REPO_ROOT / "somatic" / "analysis" / "provenance.py",
            REPO_ROOT / "somatic" / "agents" / "finch_toolbelt.py",
            REPO_ROOT / "somatic" / "agents" / "finch.py",
            REPO_ROOT / "somatic" / "mock_runtime.py",
        ]

        for path in runtime_files:
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        self.assertNotIn(node.module.split(".")[0], forbidden_import_roots)


if __name__ == "__main__":
    unittest.main()
