import ast
import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
ROBIN_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-robin-loop.yaml"
LITERATURE_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-literature-only.yaml"
TOURNAMENT_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-hypothesis-tournament.yaml"
ROBIN_ARTIFACTS = (
    "artifacts/crow_literature_context.json",
    "artifacts/falcon_measurement_plan.json",
    "artifacts/raw_evidence.json",
    "artifacts/finch_analysis.json",
    "artifacts/structured_verdict.json",
    "artifacts/robin_loop_summary.json",
)


class RobinLoopTests(unittest.TestCase):
    def test_robin_loop_run_writes_artifacts_and_report_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                ROBIN_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-robin-test",
            )

            parsed = {}
            for relative in ROBIN_ARTIFACTS:
                path = run_dir / relative
                self.assertTrue(path.exists(), relative)
                parsed[relative] = json.loads(path.read_text(encoding="utf-8"))

            context = parsed["artifacts/crow_literature_context.json"]
            plan = parsed["artifacts/falcon_measurement_plan.json"]
            raw = parsed["artifacts/raw_evidence.json"]
            analysis = parsed["artifacts/finch_analysis.json"]
            verdict = parsed["artifacts/structured_verdict.json"]
            summary = parsed["artifacts/robin_loop_summary.json"]
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")

            self.assertEqual(context["agent_role"], "Crow")
            self.assertGreaterEqual(len(context["records"]), 2)
            self.assertEqual(plan["agent_role"], "Falcon")
            self.assertEqual(
                [source["modality"] for source in plan["measurement_plan"]["sources"]],
                ["literature", "sim", "wetlab"],
            )
            self.assertEqual(
                [item["source"]["modality"] for item in raw["records"]],
                ["literature", "sim", "wetlab"],
            )
            self.assertEqual(analysis["agent_role"], "Finch")
            self.assertEqual(verdict["agent_role"], "Finch")
            self.assertEqual(verdict["structured_verdict"]["confidence"], "low")
            self.assertEqual(summary["loop_shape"], "crow-falcon-sandbox-finch-verdict-next")
            self.assertEqual(summary["next_iteration"]["recommended_mode"], "mock-local-repeat")
            self.assertEqual(
                manifest["artifacts"]["structured_verdict"], "artifacts/structured_verdict.json"
            )

            for expected in (
                "mock/offline/research-only",
                "Crow Context Summary",
                "Falcon Measurement Plan Summary",
                "Finch Verdict Summary",
                "Evidence Limitations",
                "Safety Summary",
                "Next-Step Recommendations",
                "not medical advice",
                "not a real scientific conclusion",
            ):
                with self.subTest(expected=expected):
                    self.assertIn(expected, report)

    def test_robin_raw_evidence_and_verdict_are_deterministic_across_runs(self):
        with tempfile.TemporaryDirectory() as left_tmp, tempfile.TemporaryDirectory() as right_tmp:
            left = run_mock_workflow(
                ROBIN_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(left_tmp),
                run_id="run-left",
            )
            right = run_mock_workflow(
                ROBIN_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(right_tmp),
                run_id="run-right",
            )

            for relative in (
                "artifacts/raw_evidence.json",
                "artifacts/structured_verdict.json",
            ):
                with self.subTest(relative=relative):
                    left_payload = json.loads((left / relative).read_text(encoding="utf-8"))
                    right_payload = json.loads((right / relative).read_text(encoding="utf-8"))
                    self.assertEqual(left_payload, right_payload)

    def test_baseline_workflows_still_run(self):
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

            self.assertTrue((literature / "artifacts" / "hypotheses.json").exists())
            self.assertTrue((tournament / "artifacts" / "team_orchestrator_summary.json").exists())

    def test_no_network_or_external_api_surfaces_in_robin_runtime(self):
        forbidden_import_roots = (
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "langgraph",
            "paperqa",
            "futurehouse",
            "scientific_agent_skills",
            "autoscientists",
        )
        forbidden_call_names = ("urlopen", "request", "create_connection")
        runtime_files = [
            REPO_ROOT / "somatic" / "agents" / "crow.py",
            REPO_ROOT / "somatic" / "agents" / "falcon.py",
            REPO_ROOT / "somatic" / "agents" / "finch.py",
            REPO_ROOT / "somatic" / "simulator" / "sandbox_source.py",
            REPO_ROOT / "somatic" / "mock_runtime.py",
        ]

        for path in runtime_files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = [alias.name.split(".")[0] for alias in node.names]
                    for module in imported:
                        with self.subTest(path=path.name, module=module):
                            self.assertNotIn(module, forbidden_import_roots)
                if isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module.split(".")[0]
                    with self.subTest(path=path.name, module=module):
                        self.assertNotIn(module, forbidden_import_roots)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    with self.subTest(path=path.name, call=node.func.id):
                        self.assertNotIn(node.func.id, forbidden_call_names)


if __name__ == "__main__":
    unittest.main()
