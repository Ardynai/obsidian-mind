import ast
import json
import tempfile
import unittest
from pathlib import Path

from somatic.agents.team_orchestrator import run_team_orchestrator
from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
TOURNAMENT_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-hypothesis-tournament.yaml"
TEAM_ARTIFACTS = (
    "artifacts/team_roster.json",
    "artifacts/team_critiques.json",
    "artifacts/shared_blackboard.json",
    "artifacts/evidence_budget.json",
    "artifacts/reorganization_log.json",
    "artifacts/team_orchestrator_summary.json",
)


class TeamOrchestratorTests(unittest.TestCase):
    def test_team_orchestrator_artifacts_exist_and_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                TOURNAMENT_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-team-test",
            )

            parsed = {}
            for relative in TEAM_ARTIFACTS:
                path = run_dir / relative
                self.assertTrue(path.exists(), relative)
                parsed[relative] = json.loads(path.read_text(encoding="utf-8"))

            roster = parsed["artifacts/team_roster.json"]
            critiques = parsed["artifacts/team_critiques.json"]
            blackboard = parsed["artifacts/shared_blackboard.json"]
            budget = parsed["artifacts/evidence_budget.json"]
            reorg = parsed["artifacts/reorganization_log.json"]
            summary = parsed["artifacts/team_orchestrator_summary.json"]

            self.assertEqual(
                [team["role"] for team in roster["teams"]],
                [
                    "GeneratorTeam",
                    "FalsifierTeam",
                    "EvidenceTeam",
                    "SafetyTeam",
                    "SynthesisTeam",
                ],
            )
            for team in roster["teams"]:
                self.assertIn("team_id", team)
                self.assertIn("focus_hypothesis_ids", team)
                self.assertIn("critique_goals", team)
                self.assertIn("evidence_requests", team)
                self.assertIn("risk_flags", team)
                self.assertIn("decision", team)
                self.assertEqual(team["lifecycle_stage"], "formed-for-offline-review")
                self.assertGreater(team["confidence_estimate"]["score"], 0)
                self.assertLessEqual(team["confidence_estimate"]["score"], 1)
                self.assertEqual(
                    team["critique_gate"]["result"],
                    "passed-before-evidence-budget",
                )
                self.assertFalse(team["stall_status"]["is_stalled"])
                self.assertEqual(
                    team["blackboard_contribution"]["event_type"],
                    "team_contribution",
                )
                self.assertEqual(
                    team["evidence_spend_decision"]["decision"],
                    "allow-mock-budget-only",
                )
                self.assertFalse(team["reorganization_trigger"]["triggered"])
                self.assertTrue(team["next_team_action"])
                self.assertTrue(team["future_provider_hook"]["reference_only"])
                self.assertFalse(team["future_provider_hook"]["runtime_enabled"])

            self.assertEqual(len(critiques["critiques"]), len(roster["teams"]))
            for critique in critiques["critiques"]:
                self.assertEqual(
                    critique["critique_gate_result"]["result"],
                    "passed-before-evidence-budget",
                )
                self.assertIn("confidence_estimate", critique)
                self.assertIn("stall_status", critique)
                self.assertIn("next_team_action", critique)
            event_types = [event["event_type"] for event in blackboard["events"]]
            self.assertLess(event_types.index("critique"), event_types.index("evidence_budget"))
            self.assertEqual(event_types.count("team_contribution"), len(roster["teams"]))
            evidence_budget_index = event_types.index("evidence_budget")
            for index, event_type in enumerate(event_types):
                if event_type == "team_contribution":
                    self.assertLess(index, evidence_budget_index)
            self.assertTrue(budget["mock"])
            self.assertTrue(budget["offline"])
            self.assertGreater(budget["total_points"], 0)
            for allocation in budget["allocations"]:
                self.assertTrue(allocation["critique_gate_passed"])
                self.assertEqual(
                    allocation["evidence_spend_decision"]["decision"],
                    "allow-mock-budget-only",
                )
            self.assertEqual(len(reorg["events"]), 1)
            self.assertIn(
                reorg["events"][0]["event_type"], {"merge", "reassignment", "no_reorganization"}
            )
            self.assertFalse(reorg["events"][0]["trigger"]["triggered"])
            self.assertEqual(reorg["events"][0]["stall_summary"]["stalled_team_ids"], [])
            self.assertEqual(summary["team_count"], len(roster["teams"]))
            self.assertTrue(summary["future_hook"]["runtime_enabled"] is False)
            self.assertEqual(
                set(summary["team_lifecycle_stages"].values()),
                {"formed-for-offline-review"},
            )
            self.assertEqual(len(summary["confidence_estimates"]), len(roster["teams"]))
            self.assertTrue(summary["critique_gate"]["passed"])
            self.assertEqual(summary["stall_summary"]["stalled_team_ids"], [])
            self.assertFalse(summary["reorganization_trigger"]["triggered"])
            self.assertEqual(len(summary["next_team_actions"]), len(roster["teams"]))
            self.assertTrue(summary["future_provider_hook"]["reference_only"])
            self.assertEqual(
                summary["future_provider_hook"]["license_status"],
                "unresolved-no-license-file-found",
            )

            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")
            self.assertIn("Team Formation Summary", report)
            self.assertIn("Critique Gate Summary", report)
            self.assertIn("Reorganization And Stall Summary", report)
            self.assertIn("AutoScientists Reference Boundary", report)

    def test_team_orchestrator_outputs_are_deterministic_across_runs(self):
        with tempfile.TemporaryDirectory() as left_tmp, tempfile.TemporaryDirectory() as right_tmp:
            left = run_mock_workflow(
                TOURNAMENT_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(left_tmp),
                run_id="run-left",
            )
            right = run_mock_workflow(
                TOURNAMENT_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(right_tmp),
                run_id="run-right",
            )

            for relative in TEAM_ARTIFACTS:
                with self.subTest(relative=relative):
                    left_payload = json.loads((left / relative).read_text(encoding="utf-8"))
                    right_payload = json.loads((right / relative).read_text(encoding="utf-8"))
                    self.assertEqual(left_payload, right_payload)

    def test_direct_team_orchestrator_scaffold_is_mock_offline(self):
        result = run_team_orchestrator(
            ranked_hypotheses=[
                {"id": "hyp-a-r1", "parent_id": "hyp-a", "rank": 1},
                {"id": "hyp-b-r1", "parent_id": "hyp-b", "rank": 2},
            ],
            reflection_notes=[],
            refined_hypotheses=[],
            pairwise_debates={"matchups": []},
            elo_ratings={"ratings": []},
        )

        self.assertTrue(result["team_orchestrator_summary"]["mock"])
        self.assertTrue(result["team_orchestrator_summary"]["offline"])
        self.assertEqual(
            result["team_orchestrator_summary"]["orchestrator_status"], "scaffold-only"
        )

    def test_no_network_or_external_api_surfaces_in_team_runtime(self):
        forbidden_import_roots = (
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "langgraph",
            "paperqa",
        )
        runtime_files = [
            REPO_ROOT / "somatic" / "agents" / "team_orchestrator.py",
            REPO_ROOT / "somatic" / "agents" / "tournament.py",
            REPO_ROOT / "somatic" / "agents" / "batch_scorer.py",
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


if __name__ == "__main__":
    unittest.main()
