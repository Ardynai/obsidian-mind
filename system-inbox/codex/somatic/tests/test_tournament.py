import ast
import json
import tempfile
import unittest
from pathlib import Path

from somatic.agents.batch_scorer import LocalMockBatchScorer
from somatic.agents.tournament import _apply_refinement_delta, build_tournament_bracket
from somatic.core.scoring import SCORE_FIELDS, final_score, rank_scored_items
from somatic.mock_runtime import run_mock_workflow
from somatic.workflow_loader import load_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
TOURNAMENT_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-hypothesis-tournament.yaml"
FORBIDDEN_TOURNAMENT_CSI_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
    "report",
    "summary",
    "files",
    "fixtures",
    "fixture_refs",
    "parse_errors",
}
FORBIDDEN_TOURNAMENT_CSI_WORDS = (
    "raw_values",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
    "sample-esp32-csi",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
)
FORBIDDEN_TOURNAMENT_ENVIRONMENT_WORDS = (
    "environment-parsed.csv",
    "environment-mixed.csv",
    "fixture://",
    "fixtures/",
    "source_id",
    "source_ids",
    "provider_payload_body",
    "parser_report_body",
    "parser_summary_body",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "bearer",
)


class HypothesisTournamentTests(unittest.TestCase):
    def test_refinement_delta_ignores_unknown_score_fields(self):
        scores = {
            "evidence_alignment": 80,
            "novelty": 70,
            "feasibility": 75,
            "falsifiability": 78,
            "safety_risk": 10,
            "data_requirements": 72,
            "unexpected": 99,
        }

        refined = _apply_refinement_delta(scores)

        self.assertEqual(set(refined), set(SCORE_FIELDS))
        self.assertNotIn("unexpected", refined)

    def test_bracket_rejects_unsupported_candidate_counts(self):
        with self.assertRaisesRegex(ValueError, "exactly 5"):
            build_tournament_bracket(
                [
                    {
                        "candidate_id": "hyp-a",
                        "final_score": 50,
                    }
                ]
            )

    def test_local_mock_batch_scorer_does_not_reward_safety_risk(self):
        scorer = LocalMockBatchScorer()
        safer = {
            "id": "safer",
            "scores": {
                "evidence_alignment": 70,
                "novelty": 70,
                "feasibility": 70,
                "falsifiability": 70,
                "safety_risk": 5,
                "data_requirements": 70,
            },
        }
        riskier = {
            "id": "riskier",
            "scores": dict(safer["scores"], safety_risk=80),
        }

        result = scorer.compare_pairwise(safer, riskier)

        self.assertEqual(result["winner_id"], "safer")
        self.assertLess(
            result["dimension_scores"]["safer"]["safety_risk"],
            result["dimension_scores"]["riskier"]["safety_risk"],
        )

    def test_final_score_penalizes_safety_risk_and_ranks_descending(self):
        safer_scores = {
            "evidence_alignment": 80,
            "novelty": 70,
            "feasibility": 75,
            "falsifiability": 78,
            "safety_risk": 10,
            "data_requirements": 72,
        }
        riskier_scores = dict(safer_scores, safety_risk=80)

        self.assertEqual(tuple(SCORE_FIELDS), tuple(safer_scores))
        self.assertGreater(final_score(safer_scores), final_score(riskier_scores))

        ranked = rank_scored_items(
            [
                {"id": "riskier", "scores": riskier_scores},
                {"id": "safer", "scores": safer_scores},
            ]
        )

        self.assertEqual([item["id"] for item in ranked], ["safer", "riskier"])
        self.assertEqual([item["rank"] for item in ranked], [1, 2])

    def test_fixture_loads_as_hypothesis_tournament(self):
        workflow = load_workflow(TOURNAMENT_FIXTURE)

        self.assertEqual(workflow["id"], "valid-hypothesis-tournament")
        self.assertEqual(workflow["mode"], "hypothesis-tournament")
        self.assertGreaterEqual(len(workflow["stages"]), 4)

    def test_tournament_run_writes_ranked_artifacts_and_report_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                TOURNAMENT_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-tournament-test",
            )

            required_json = [
                "manifest.json",
                "workflow.json",
                "evidence/evidence.json",
                "artifacts/hypotheses.json",
                "artifacts/candidate_hypotheses.json",
                "artifacts/pairwise_debates.json",
                "artifacts/elo_ratings.json",
                "artifacts/reflection_notes.json",
                "artifacts/review_scores.json",
                "artifacts/tournament_bracket.json",
                "artifacts/team_orchestrator_summary.json",
                "artifacts/csi_evidence_pack.json",
                "artifacts/environment_evidence_pack.json",
                "artifacts/refined_hypotheses.json",
                "artifacts/ranked_hypotheses.json",
                "safety/safety-response.json",
                "next_iteration.json",
            ]
            parsed = {}
            for relative in required_json:
                path = run_dir / relative
                self.assertTrue(path.exists(), relative)
                parsed[relative] = json.loads(path.read_text(encoding="utf-8"))

            candidates = parsed["artifacts/candidate_hypotheses.json"]
            debates = parsed["artifacts/pairwise_debates.json"]
            elo = parsed["artifacts/elo_ratings.json"]
            review_scores = parsed["artifacts/review_scores.json"]
            bracket = parsed["artifacts/tournament_bracket.json"]
            team_summary = parsed["artifacts/team_orchestrator_summary.json"]
            csi_evidence_pack = parsed["artifacts/csi_evidence_pack.json"]
            environment_evidence_pack = parsed["artifacts/environment_evidence_pack.json"]
            refined = parsed["artifacts/refined_hypotheses.json"]
            ranked = parsed["artifacts/ranked_hypotheses.json"]
            mirrored = parsed["artifacts/hypotheses.json"]
            workflow_payload = parsed["workflow.json"]

            self.assertGreaterEqual(len(candidates), 4)
            self.assertEqual(len(debates["matchups"]), 10)
            self.assertEqual(len(elo["ratings"]), len(candidates))
            self.assertEqual(len(review_scores), len(candidates))
            self.assertGreaterEqual(len(bracket["rounds"]), 1)
            self.assertGreaterEqual(len(refined), 2)
            self.assertEqual(ranked, mirrored)
            self.assertEqual([item["rank"] for item in ranked], list(range(1, len(ranked) + 1)))
            self.assertIn("aggregate_score", ranked[0])
            self.assertIn("elo_rating", ranked[0])
            self.assertIn("elo_rank", ranked[0])
            self.assertIn("scoring_note", ranked[0])
            self.assertIn("parent/original candidate", ranked[0]["scoring_note"])
            csi_readiness = team_summary["csi_evidence_scoring_readiness"]
            self.assertEqual(csi_readiness["status"], "partial")
            self.assertTrue(csi_readiness["metadata_only"])
            self.assertFalse(csi_readiness["core_tournament_scores_modified"])
            self.assertFalse(csi_readiness["tournament_rankings_modified"])
            self.assertFalse(csi_readiness["ranking_input"])
            self.assertTrue(csi_readiness["requires_sanitized_replay_metadata"])
            self.assertEqual(csi_readiness["csi_batch_evaluation_contract_version"], 1)
            self.assertEqual(csi_readiness["group_count"], 3)
            self.assertEqual(csi_readiness["evaluated_group_count"], 3)
            self.assertEqual(csi_readiness["rejected_group_count"], 1)
            self.assertEqual(csi_readiness["aggregate_evidence_quality"], 0)
            self.assertEqual(csi_readiness["aggregate_replay_integrity"], 0)
            self.assertEqual(csi_readiness["minimum_group_score"], 0)
            self.assertEqual(csi_readiness["average_group_score"], 59.333)
            self.assertEqual(len(csi_readiness["group_summaries"]), 3)
            self.assertEqual(
                [group["status"] for group in csi_readiness["group_summaries"]],
                ["parsed", "partial", "rejected"],
            )
            self.assertEqual(csi_evidence_pack["status"], "partial")
            self.assertEqual(
                csi_evidence_pack["readiness_status"],
                "partial-sanitized-metadata",
            )
            self.assertEqual(csi_evidence_pack["counts"]["group_count"], 3)
            self.assertEqual(csi_evidence_pack["scores"]["aggregate_evidence_quality"], 0)
            self.assertFalse(csi_evidence_pack["ranking_input"])
            self.assertFalse(csi_evidence_pack["core_tournament_scores_modified"])
            self.assertFalse(csi_evidence_pack["tournament_rankings_modified"])
            self.assertEqual(environment_evidence_pack["status"], "partial")
            self.assertEqual(
                environment_evidence_pack["readiness_status"],
                "partial-sanitized-metadata",
            )
            self.assertEqual(environment_evidence_pack["counts"]["row_count"], 3)
            self.assertEqual(environment_evidence_pack["counts"]["partial_row_count"], 1)
            self.assertEqual(environment_evidence_pack["counts"]["rejected_row_count"], 1)
            self.assertFalse(environment_evidence_pack["ranking_input"])
            self.assertFalse(environment_evidence_pack["core_tournament_scores_modified"])
            self.assertFalse(environment_evidence_pack["tournament_rankings_modified"])
            self.assertEqual(
                team_summary["csi_evidence_pack"]["pack_fingerprint"],
                csi_evidence_pack["pack_fingerprint"],
            )
            self.assertEqual(
                team_summary["environment_evidence_pack"]["pack_fingerprint"],
                environment_evidence_pack["pack_fingerprint"],
            )
            self.assertEqual(
                team_summary["environment_readiness_metadata"]["row_count"],
                3,
            )
            generic_ref = team_summary["sensor_evidence_artifact_refs"]["csi_evidence_pack"]
            environment_generic_ref = team_summary["sensor_evidence_artifact_refs"][
                "environment_evidence_pack"
            ]
            manifest_generic_ref = parsed["manifest.json"]["sensor_evidence_artifact_refs"][
                "csi_evidence_pack"
            ]
            manifest_environment_ref = parsed["manifest.json"]["sensor_evidence_artifact_refs"][
                "environment_evidence_pack"
            ]
            for surface, ref in (
                ("team_summary", generic_ref),
                ("manifest", manifest_generic_ref),
            ):
                with self.subTest(generic_sensor_evidence_ref=surface):
                    self.assertEqual(ref["classification"], "compatible")
                    self.assertEqual(ref["artifact_ref"], "artifacts/csi_evidence_pack.json")
                    self.assertEqual(
                        ref["sha256"], parsed["manifest.json"]["hashes"]["csi_evidence_pack"]
                    )
                    self.assertEqual(ref["pack_fingerprint"], csi_evidence_pack["pack_fingerprint"])
                    self.assertFalse(ref["raw_signal_values_exported"])
            for surface, ref in (
                ("team_summary", environment_generic_ref),
                ("manifest", manifest_environment_ref),
            ):
                with self.subTest(environment_sensor_evidence_ref=surface):
                    self.assertEqual(ref["classification"], "compatible")
                    self.assertEqual(
                        ref["artifact_ref"],
                        "artifacts/environment_evidence_pack.json",
                    )
                    self.assertEqual(
                        ref["sha256"],
                        parsed["manifest.json"]["hashes"]["environment_evidence_pack"],
                    )
                    self.assertEqual(
                        ref["pack_fingerprint"],
                        environment_evidence_pack["pack_fingerprint"],
                    )
            self._assert_csi_readiness_is_sanitized(csi_readiness)
            self._assert_csi_readiness_is_sanitized(csi_evidence_pack)
            self._assert_csi_readiness_is_sanitized(team_summary["csi_evidence_pack"])
            self._assert_environment_readiness_is_sanitized(environment_evidence_pack)
            self._assert_environment_readiness_is_sanitized(
                team_summary["environment_evidence_pack"]
            )
            self._assert_no_tournament_report_leaks(team_summary)
            csi_inputs = [
                item
                for item in workflow_payload["inputs"]
                if item.get("kind") == "csi-replay-evaluation-groups"
            ]
            self.assertEqual(len(csi_inputs), 1)
            self.assertTrue(csi_inputs[0]["refs_sanitized"])
            self.assertEqual(csi_inputs[0]["group_count"], 3)
            self.assertEqual(
                csi_inputs[0]["groups"],
                [
                    {"id": "csi-fixture-group-001", "ref_count": 3},
                    {"id": "csi-fixture-group-002", "ref_count": 2},
                    {"id": "csi-fixture-group-003", "ref_count": 1},
                ],
            )
            self._assert_csi_readiness_is_sanitized(workflow_payload)
            environment_inputs = [
                item
                for item in workflow_payload["inputs"]
                if item.get("kind") == "environment-fixture-rows"
            ]
            self.assertEqual(len(environment_inputs), 1)
            self.assertTrue(environment_inputs[0]["refs_sanitized"])
            self.assertEqual(environment_inputs[0]["ref_count"], 1)
            self.assertNotIn("refs", environment_inputs[0])

            final_scores = [item["final_score"] for item in ranked]
            self.assertEqual(final_scores, sorted(final_scores, reverse=True))
            elo_ratings = [item["rating"] for item in elo["ratings"]]
            self.assertEqual(elo_ratings, sorted(elo_ratings, reverse=True))

            for scored in review_scores:
                self.assertEqual(
                    set(scored["scores"]),
                    {
                        "evidence_alignment",
                        "novelty",
                        "feasibility",
                        "falsifiability",
                        "safety_risk",
                        "data_requirements",
                    },
                )

            for matchup in debates["matchups"]:
                self.assertEqual(len(matchup["candidate_ids"]), 2)
                self.assertIn(matchup["winner_id"], matchup["candidate_ids"])
                self.assertEqual(set(matchup["debate_notes"]), set(matchup["candidate_ids"]))
                for notes in matchup["debate_notes"].values():
                    self.assertIn("pro", notes)
                    self.assertIn("con", notes)

            manifest_artifacts = parsed["manifest.json"]["artifacts"]
            self.assertEqual(
                manifest_artifacts["ranked_hypotheses"],
                "artifacts/ranked_hypotheses.json",
            )
            self.assertEqual(
                manifest_artifacts["csi_evidence_pack"],
                "artifacts/csi_evidence_pack.json",
            )
            self.assertEqual(
                manifest_artifacts["environment_evidence_pack"],
                "artifacts/environment_evidence_pack.json",
            )
            self.assertEqual(
                manifest_artifacts["pairwise_debates"],
                "artifacts/pairwise_debates.json",
            )
            self.assertEqual(
                manifest_artifacts["elo_ratings"],
                "artifacts/elo_ratings.json",
            )
            self.assertTrue(parsed["manifest.json"]["mock"])
            self.assertTrue(parsed["manifest.json"]["offline"])

            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")
            self.assertIn("mock/offline", report)
            self.assertIn("research-only", report)
            self.assertIn("hypothesis-tournament", report)
            self.assertIn("Aggregate Score Ranking", report)
            self.assertIn("Elo Ranking", report)
            self.assertIn("Pairwise Debate Summary", report)
            self.assertIn("CSI Evidence Scoring Readiness", report)
            self.assertIn("CSI Batch Replay Evaluation", report)
            self.assertIn("CSI evidence pack ref", report)
            self.assertIn("Generic sensor evidence ref", report)
            self.assertIn("not medical advice", report.lower())
            self._assert_no_tournament_report_leaks(report)
            self.assertIn("not a real scientific conclusion", report.lower())
            self.assertIn("No external API calls were made.", report)

    def test_elo_ratings_are_deterministic_across_runs(self):
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

            left_elo = json.loads(
                (left / "artifacts" / "elo_ratings.json").read_text(encoding="utf-8")
            )
            right_elo = json.loads(
                (right / "artifacts" / "elo_ratings.json").read_text(encoding="utf-8")
            )

        self.assertEqual(left_elo, right_elo)

    def test_no_network_or_external_api_surfaces_in_tournament_runtime(self):
        forbidden_import_roots = (
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "langgraph",
            "paperqa",
        )
        forbidden_call_names = ("urlopen", "request", "create_connection")
        runtime_files = [
            REPO_ROOT / "somatic" / "agents" / "batch_scorer.py",
            REPO_ROOT / "somatic" / "agents" / "team_orchestrator.py",
            REPO_ROOT / "somatic" / "agents" / "tournament.py",
            REPO_ROOT / "somatic" / "core" / "scoring.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_batch.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_scoring.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_evidence_pack.py",
            REPO_ROOT / "somatic" / "sensors" / "environment.py",
            REPO_ROOT / "somatic" / "sensors" / "environment_evidence_pack.py",
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

    def _assert_csi_readiness_is_sanitized(self, payload):
        self._assert_no_forbidden_csi_readiness_keys(payload)
        self._assert_no_forbidden_csi_readiness_words(payload)
        self._assert_no_absolute_paths(payload)

    def _assert_environment_readiness_is_sanitized(self, payload):
        encoded = (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
        )
        for forbidden in FORBIDDEN_TOURNAMENT_ENVIRONMENT_WORDS:
            with self.subTest(environment_readiness_forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_csi_readiness_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(csi_readiness_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_TOURNAMENT_CSI_KEYS)
                self._assert_no_forbidden_csi_readiness_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_readiness_keys(item)

    def _assert_no_forbidden_csi_readiness_words(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_csi_readiness_words(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_readiness_words(item)
        elif isinstance(payload, str):
            lowered = (
                payload.lower()
                .replace(
                    "real-mode-authorization-missing",
                    "real-mode-gap-missing",
                )
                .replace("not-authorized", "not-runtime-status")
                .replace("authorization_status", "runtime_status")
                .replace(
                    "runtime_authorization_gap_ledger_contract_version",
                    "runtime_gap_ledger_contract_version",
                )
            )
            for word in FORBIDDEN_TOURNAMENT_CSI_WORDS:
                with self.subTest(csi_readiness_forbidden_word=word):
                    self.assertNotIn(word, lowered)

    def _assert_no_absolute_paths(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_absolute_paths(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_absolute_paths(item)
        elif isinstance(payload, str):
            normalized = payload.replace("\\", "/")
            self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), normalized)
            self.assertNotRegex(normalized, r"^[A-Za-z]:/")

    def _assert_no_tournament_report_leaks(self, payload):
        encoded = (
            json.dumps(payload, sort_keys=True).lower()
            if not isinstance(payload, str)
            else payload.lower()
        )
        encoded = (
            encoded.replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
            .replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace(
                "runtime_authorization_gap_ledger_contract_version",
                "runtime_gap_ledger_contract_version",
            )
        )
        for forbidden in (
            "fixture_refs",
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "sample-csi-jsonl",
            "mixed-valid-invalid-csi",
            "unsupported-csi",
            "environment-parsed.csv",
            "environment-mixed.csv",
            "source_id",
            "source_ids",
            "private_ref",
            "private_refs",
            "unsafe_ref",
            "unsafe_refs",
            "source_path",
            "local_path",
            "staging_root",
            "provider_payload_body",
            "parser_report_body",
            "parser_summary_body",
            "api_key",
            "access_token",
            "refresh_token",
            "secret_value",
            "authorization",
            "bearer",
        ):
            with self.subTest(tournament_report_leak=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
