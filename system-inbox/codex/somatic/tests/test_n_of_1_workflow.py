import ast
import contextlib
import hashlib
import io
import json
import re
import tempfile
import textwrap
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.mock_runtime import run_mock_workflow
from somatic.workflow_loader import load_mock_provider_metadata, load_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "fixtures" / "workflows"
NOF1_FIXTURE = WORKFLOW_DIR / "valid-n-of-1.yaml"
NOF1_PACKET_INPUT_ARTIFACTS = (
    "sensor_stream_plan",
    "sensor_observations",
    "sensor_feature_set",
    "csi_parser_report",
    "csi_parsed_summary",
    "csi_evidence_pack",
    "environment_evidence_pack",
    "sensor_evidence_record",
    "n_of_1_baseline_placeholder",
    "personal_profile",
    "baseline_graph",
    "baseline_comparison",
    "intervention_tag",
    "intervention_context",
    "response_evaluation_plan",
    "mock_intervention_ledger",
    "follow_up_observation_window",
    "follow_up_sensor_snapshot",
    "response_comparison",
    "response_evaluation_summary",
    "n_of_1_summary",
)
NOF1_ARTIFACTS = NOF1_PACKET_INPUT_ARTIFACTS + (
    "n_of_1_report_packet",
    "n_of_1_fabric_pack_plan",
)
FORBIDDEN_CSI_REPORT_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
}
FORBIDDEN_CSI_REPORT_WORDS = (
    "raw_values",
    "samples",
    "imag",
    "amplitude",
    "rssi",
    "source_id",
    "source_ids",
)


class NOf1WorkflowTests(unittest.TestCase):
    def test_fixture_loads_with_fake_backed_sensor_provider_metadata(self):
        workflow = load_workflow(NOF1_FIXTURE)
        providers = load_mock_provider_metadata(workflow, REPO_ROOT)

        self.assertEqual(workflow["mode"], "n-of-1")
        self.assertFalse(workflow["safety_profile"]["external_actions_allowed"])
        self.assertIn("sensor", providers)
        self.assertEqual(providers["sensor"]["id"], "mock-sensor-provider")
        self.assertIn("n-of-1", providers["sensor"]["modes_supported"])
        self.assertTrue(providers["sensor"]["mock"]["fake_backed"])
        self.assertFalse(providers["sensor"]["limits"]["live_sensor_access_allowed"])
        self.assertFalse(providers["sensor"]["limits"]["network_calls_allowed"])
        self.assertFalse(providers["sensor"]["limits"]["real_monitoring_allowed"])
        self.assertEqual(providers["sensor"]["auth"]["secrets_required"], [])
        for input_item in workflow["inputs"]:
            ref = input_item.get("ref", "")
            if ref.startswith("fixture://"):
                relative = ref.removeprefix("fixture://")
                self.assertTrue((REPO_ROOT / "fixtures" / relative).exists(), ref)

    def test_n_of_1_csi_parser_artifacts_are_stage_declared(self):
        workflow = load_workflow(NOF1_FIXTURE)
        artifact_ids = {artifact["id"] for artifact in workflow["artifacts"]}
        stage_output_ids = {
            output for stage in workflow["stages"] for output in stage.get("outputs", [])
        }

        for artifact_name in NOF1_ARTIFACTS:
            with self.subTest(artifact_name=artifact_name):
                self.assertIn(artifact_name, artifact_ids)
                self.assertIn(artifact_name, stage_output_ids)

        sensor_stage = next(
            stage for stage in workflow["stages"] if stage["id"] == "emit-sandbox-observations"
        )
        self.assertIn("csi_parser_fixtures", sensor_stage["inputs"])
        self.assertIn("csi_parser_report", sensor_stage["outputs"])
        self.assertIn("csi_parsed_summary", sensor_stage["outputs"])
        self.assertIn("csi_evidence_pack", sensor_stage["outputs"])
        self.assertIn("environment_evidence_pack", sensor_stage["outputs"])

    def test_n_of_1_workflow_writes_sensor_artifacts_and_report_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                NOF1_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-n-of-1-test",
            )

            manifest = self._read_json(run_dir / "manifest.json")
            workflow_artifact = self._read_json(run_dir / "workflow.json")
            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")

            self.assertEqual(manifest["mode"], "n-of-1")
            provider_ids = {provider["provider_id"] for provider in manifest["providers"]}
            self.assertIn("mock-sensor-provider", provider_ids)
            for artifact_name in NOF1_ARTIFACTS:
                with self.subTest(artifact_name=artifact_name):
                    self.assertIn(artifact_name, manifest["artifacts"])
                    self.assertIn(artifact_name, manifest["hashes"])
                    artifact_path = run_dir / manifest["artifacts"][artifact_name]
                    self.assertTrue(artifact_path.exists())
                    payload = self._read_json(artifact_path)
                    self.assertEqual(payload["schema_version"], 1)
                    self.assertTrue(payload["mock"])
                    self.assertTrue(payload["offline"])
                    self.assertTrue(payload["research_only"])
                    self.assertFalse(payload["live_sensor_access"])
                    self.assertFalse(payload["network_calls"])
                    if artifact_name != "environment_evidence_pack":
                        self.assertFalse(payload["diagnosis"])
                        self.assertFalse(payload["treatment_recommendation"])
                        self.assertFalse(payload["emergency_triage"])
                        self.assertFalse(payload["real_monitoring"])
                    self._assert_no_forbidden_csi_artifact_keys(payload)
                    self._assert_no_forbidden_csi_artifact_words(
                        payload,
                        allow_general_sample_text=True,
                    )
                    self._assert_no_absolute_paths(payload)
                    self.assertEqual(manifest["hashes"][artifact_name], self._sha256(artifact_path))

            plan = self._read_json(run_dir / "artifacts" / "sensor_stream_plan.json")
            observations = self._read_json(run_dir / "artifacts" / "sensor_observations.json")
            feature_set = self._read_json(run_dir / "artifacts" / "sensor_feature_set.json")
            csi_parser_report = self._read_json(run_dir / "artifacts" / "csi_parser_report.json")
            csi_parsed_summary = self._read_json(run_dir / "artifacts" / "csi_parsed_summary.json")
            csi_evidence_pack = self._read_json(run_dir / "artifacts" / "csi_evidence_pack.json")
            environment_evidence_pack = self._read_json(
                run_dir / "artifacts" / "environment_evidence_pack.json"
            )
            evidence_record = self._read_json(run_dir / "artifacts" / "sensor_evidence_record.json")
            baseline = self._read_json(run_dir / "artifacts" / "n_of_1_baseline_placeholder.json")
            personal_profile = self._read_json(run_dir / "artifacts" / "personal_profile.json")
            baseline_graph = self._read_json(run_dir / "artifacts" / "baseline_graph.json")
            baseline_comparison = self._read_json(
                run_dir / "artifacts" / "baseline_comparison.json"
            )
            intervention_tag = self._read_json(run_dir / "artifacts" / "intervention_tag.json")
            intervention_context = self._read_json(
                run_dir / "artifacts" / "intervention_context.json"
            )
            response_plan = self._read_json(run_dir / "artifacts" / "response_evaluation_plan.json")
            intervention_ledger = self._read_json(
                run_dir / "artifacts" / "mock_intervention_ledger.json"
            )
            follow_up_window = self._read_json(
                run_dir / "artifacts" / "follow_up_observation_window.json"
            )
            follow_up_snapshot = self._read_json(
                run_dir / "artifacts" / "follow_up_sensor_snapshot.json"
            )
            response_comparison = self._read_json(
                run_dir / "artifacts" / "response_comparison.json"
            )
            response_evaluation_summary = self._read_json(
                run_dir / "artifacts" / "response_evaluation_summary.json"
            )
            summary = self._read_json(run_dir / "artifacts" / "n_of_1_summary.json")
            report_packet = self._read_json(run_dir / "artifacts" / "n_of_1_report_packet.json")
            fabric_pack_plan = self._read_json(
                run_dir / "artifacts" / "n_of_1_fabric_pack_plan.json"
            )

            self.assertEqual(plan["provider_id"], "sandbox-sensor-provider")
            self.assertIn("environmental", plan["modalities"])
            self.assertEqual(len(observations["observations"]), 6)
            self.assertEqual(feature_set["features"]["respiratory_rate"], 14)
            self.assertEqual(feature_set["features"]["movement_score"], 0.18)
            self.assertEqual(
                feature_set["features"]["audio_event_placeholder"],
                "none-observed-placeholder",
            )
            csi_metadata = feature_set["metadata"]["csi"]
            self.assertTrue(csi_metadata["planning_only"])
            self.assertEqual(
                csi_metadata["feature_set"]["features"]["motion_score"],
                0.18,
            )
            self.assertEqual(
                csi_metadata["feature_set"]["features"]["heart_rate_placeholder"],
                "not-estimated-placeholder",
            )
            self.assertFalse(csi_metadata["feature_set"]["hardware_access"])
            self.assertFalse(csi_metadata["feature_set"]["packet_capture"])
            self.assertFalse(csi_metadata["feature_set"]["wifi_network_probing"])
            self.assertFalse(csi_metadata["feature_set"]["monitor_mode"])
            self.assertEqual(
                csi_metadata["parser_capabilities"]["parser_id"],
                "somatic-csi-fixture-parser-v1",
            )
            self.assertEqual(
                csi_metadata["reference_inventory_ref"],
                "csi-reference-inventory-v1",
            )
            self.assertEqual(csi_parser_report["status"], "parsed")
            self.assertEqual(
                csi_parser_report["parser_id"],
                "somatic-csi-fixture-parser-v1",
            )
            self.assertEqual(csi_parser_report["fixture_count"], 3)
            self.assertEqual(csi_parser_report["frame_count"], 6)
            self.assertEqual(csi_parser_report["sample_count"], 14)
            self.assertEqual(
                csi_parser_report["replay_provider"]["mode"],
                "fixture-replay",
            )
            self.assertFalse(csi_parser_report["hardware_access"])
            self.assertFalse(csi_parser_report["network_calls"])
            self.assertFalse(csi_parser_report["packet_capture"])
            self.assertFalse(csi_parser_report["serial_access"])
            self.assertFalse(csi_parser_report["medical_or_clinical_claim"])
            csi_evidence_scoring = csi_parser_report["csi_evidence_scoring"]
            self.assertEqual(csi_evidence_scoring["status"], "parsed")
            self.assertEqual(csi_evidence_scoring["score"], 100)
            self.assertEqual(csi_evidence_scoring["evidence_quality"], 100)
            self.assertEqual(csi_evidence_scoring["replay_integrity"], 100)
            self.assertEqual(
                csi_evidence_scoring["status_counts"],
                {"parsed": 3, "partial": 0, "rejected": 0},
            )
            self.assertEqual(
                csi_parsed_summary["csi_evidence_scoring"],
                csi_evidence_scoring,
            )
            self.assertEqual(csi_parsed_summary["status"], "parsed")
            self.assertEqual(csi_parsed_summary["fixture_count"], 3)
            self.assertEqual(csi_parsed_summary["frame_count"], 6)
            self.assertEqual(csi_parsed_summary["sample_count"], 14)
            self.assertIn("csi-csv-fixture", csi_parsed_summary["source_formats"])
            self.assertIn("csi-tabular-fixture", csi_parsed_summary["source_formats"])
            self.assertIn("csi-jsonl-fixture", csi_parsed_summary["source_formats"])
            self.assertEqual(csi_evidence_pack["status"], "parsed")
            self.assertEqual(csi_evidence_pack["readiness_status"], "ready-with-sanitized-metadata")
            self.assertEqual(csi_evidence_pack["evidence_pack_contract_version"], 1)
            self.assertEqual(csi_evidence_pack["counts"]["fixture_count"], 3)
            self.assertEqual(csi_evidence_pack["counts"]["frame_count"], 6)
            self.assertEqual(csi_evidence_pack["counts"]["sample_count"], 14)
            self.assertEqual(csi_evidence_pack["scores"]["evidence_quality"], 100)
            self.assertEqual(csi_evidence_pack["scores"]["replay_integrity"], 100)
            self.assertEqual(len(csi_evidence_pack["pack_fingerprint"]), 64)
            self.assertFalse(csi_evidence_pack["ranking_input"])
            self.assertFalse(csi_evidence_pack["core_tournament_scores_modified"])
            self.assertEqual(environment_evidence_pack["status"], "parsed")
            self.assertEqual(
                environment_evidence_pack["readiness_status"],
                "ready-with-sanitized-metadata",
            )
            self.assertEqual(environment_evidence_pack["contract_version"], 1)
            self.assertEqual(environment_evidence_pack["provider_kind"], "environment-fixture")
            self.assertEqual(
                environment_evidence_pack["evidence_kind"],
                "environment-tabular-evidence-pack",
            )
            self.assertEqual(environment_evidence_pack["counts"]["row_count"], 3)
            self.assertEqual(environment_evidence_pack["counts"]["parsed_row_count"], 3)
            self.assertEqual(environment_evidence_pack["scores"]["evidence_quality"], 93)
            self.assertFalse(environment_evidence_pack["ranking_input"])
            self.assertFalse(environment_evidence_pack["core_tournament_scores_modified"])
            self.assertFalse(environment_evidence_pack["tournament_rankings_modified"])
            encoded_csi_summary = json.dumps(csi_parsed_summary, sort_keys=True)
            for forbidden_key in (
                "raw_values",
                "samples",
                "real",
                "imag",
                "amplitude",
                "phase",
                "rssi",
            ):
                with self.subTest(csi_summary_forbidden_key=forbidden_key):
                    self.assertNotIn(f'"{forbidden_key}":', encoded_csi_summary)
            for artifact_name, payload in (
                ("manifest", manifest),
                ("workflow", workflow_artifact),
                ("csi_parser_report", csi_parser_report),
                ("csi_parsed_summary", csi_parsed_summary),
                ("csi_evidence_pack", csi_evidence_pack),
                ("environment_evidence_pack", environment_evidence_pack),
                ("n_of_1_summary", summary),
                ("n_of_1_report_packet", report_packet),
                ("n_of_1_fabric_pack_plan", fabric_pack_plan),
            ):
                with self.subTest(csi_artifact_privacy=artifact_name):
                    self._assert_no_forbidden_csi_artifact_keys(payload)
                    self._assert_no_forbidden_csi_artifact_words(payload)
                    self._assert_no_absolute_paths(payload)
            self._assert_no_forbidden_csi_text(report)
            self._assert_no_absolute_paths(report)
            for surface_name, payload in (
                ("summary", summary),
                ("report_packet", report_packet),
                ("fabric_plan", fabric_pack_plan),
            ):
                with self.subTest(no_private_report_plan_leak=surface_name):
                    self._assert_no_report_or_fabric_plan_leaks(payload)
            self._assert_no_report_or_fabric_plan_leaks(report)
            environment_inputs = [
                item
                for item in workflow_artifact["inputs"]
                if item.get("kind") == "environment-fixture-rows"
            ]
            self.assertEqual(len(environment_inputs), 1)
            self.assertTrue(environment_inputs[0]["refs_sanitized"])
            self.assertEqual(environment_inputs[0]["ref_count"], 1)
            self.assertNotIn("refs", environment_inputs[0])
            self.assertNotIn(
                "environment-parsed.csv",
                json.dumps(workflow_artifact, sort_keys=True).lower(),
            )
            csi_inputs = [
                item
                for item in workflow_artifact["inputs"]
                if item.get("kind") == "csi-parser-fixtures"
            ]
            self.assertEqual(len(csi_inputs), 1)
            self.assertTrue(csi_inputs[0]["refs_sanitized"])
            self.assertEqual(csi_inputs[0]["ref_count"], 3)
            self.assertEqual(csi_inputs[0]["provider_id"], "wifi-csi")
            self.assertNotIn("refs", csi_inputs[0])
            workflow_text = json.dumps(workflow_artifact, sort_keys=True).lower()
            for forbidden_ref in (
                "sample-esp32-csi",
                "csi-tabular-fixture.csv",
                "sample-csi-jsonl",
            ):
                with self.subTest(sanitized_csi_workflow_ref=forbidden_ref):
                    self.assertNotIn(forbidden_ref, workflow_text)
            self.assertEqual(
                evidence_record["raw_evidence"]["payload_ref"],
                "artifacts/sensor_feature_set.json",
            )
            self.assertEqual(
                evidence_record["raw_evidence"]["sha256"],
                self._sha256(run_dir / evidence_record["raw_evidence"]["payload_ref"]),
            )
            self.assertEqual(
                evidence_record["metadata"]["csi"]["feature_set_sha256"],
                self._sha256(run_dir / evidence_record["raw_evidence"]["payload_ref"]),
            )
            self.assertEqual(
                evidence_record["metadata"]["csi"]["evidence_scoring"],
                csi_evidence_scoring,
            )
            self.assertEqual(
                evidence_record["raw_evidence"]["metadata"]["csi"]["feature_set_sha256"],
                self._sha256(run_dir / evidence_record["raw_evidence"]["payload_ref"]),
            )
            self.assertEqual(
                evidence_record["raw_evidence"]["metadata"]["csi"]["evidence_scoring"],
                csi_evidence_scoring,
            )
            self.assertEqual(
                evidence_record["structured_verdict"]["metadata"]["csi"]["evidence_scoring"],
                csi_evidence_scoring,
            )
            self.assertEqual(
                evidence_record["metadata"]["csi"]["ruview_dependency"],
                "conditional-reference-only",
            )
            self.assertEqual(
                evidence_record["metadata"]["csi"]["ruview_reference"]["status"],
                "conditional-reference-only",
            )
            self.assertEqual(
                evidence_record["metadata"]["csi"]["booth_planning_profile"]["profile"],
                "booth-first-single-subject-v1",
            )
            self.assertEqual(
                evidence_record["metadata"]["csi"]["source_adapter_output_validation"][
                    "classification"
                ],
                "compatible",
            )
            self.assertEqual(
                evidence_record["structured_verdict"]["confidence"],
                "not-applicable",
            )
            self.assertEqual(baseline["baseline_collection"], "not-performed")
            self.assertFalse(baseline["real_health_data_loaded"])
            self.assertFalse(baseline["real_profile_storage"])
            self.assertEqual(personal_profile["id"], "personal-profile-placeholder")
            self.assertFalse(personal_profile["real_health_data_loaded"])
            self.assertFalse(personal_profile["real_profile_storage"])
            self.assertEqual(baseline_graph["id"], "baseline-graph-placeholder")
            self.assertEqual(baseline_graph["profile_id"], personal_profile["id"])
            self.assertEqual(
                baseline_graph["categories"],
                [
                    "respiratory_rate",
                    "movement_score",
                    "sleep_state_estimate",
                    "posture_state",
                    "csi_confidence",
                    "environmental_context",
                    "notes_placeholder",
                ],
            )
            self.assertEqual(
                baseline_comparison["status_counts"],
                {
                    "within_baseline": 5,
                    "outside_baseline": 1,
                    "insufficient_data": 1,
                },
            )
            comparison_by_category = {
                result["category"]: result for result in baseline_comparison["results"]
            }
            self.assertEqual(
                comparison_by_category["movement_score"]["status"],
                "outside_baseline",
            )
            self.assertEqual(
                comparison_by_category["notes_placeholder"]["status"],
                "insufficient_data",
            )
            self.assertEqual(
                baseline_comparison["artifact_hashes"]["sensor_feature_set"],
                self._sha256(run_dir / "artifacts" / "sensor_feature_set.json"),
            )
            self.assertEqual(
                baseline_comparison["artifact_hashes"]["baseline_graph"],
                self._sha256(run_dir / "artifacts" / "baseline_graph.json"),
            )
            self.assertEqual(intervention_tag["id"], "intervention-tag-placeholder")
            self.assertEqual(intervention_tag["category"], "rest_placeholder")
            disabled_categories = {
                item["category"]: item for item in intervention_tag["category_statuses"]
            }
            self.assertTrue(disabled_categories["medication_placeholder_disabled"]["disabled"])
            self.assertTrue(disabled_categories["clinician_review_placeholder"]["disabled"])
            self.assertEqual(
                intervention_context["artifact_refs"]["sensor_feature_set"],
                "artifacts/sensor_feature_set.json",
            )
            self.assertEqual(
                intervention_context["artifact_refs"]["baseline_comparison"],
                "artifacts/baseline_comparison.json",
            )
            self.assertEqual(
                intervention_context["artifact_refs"]["personal_profile"],
                "artifacts/personal_profile.json",
            )
            self.assertEqual(
                intervention_context["artifact_refs"]["baseline_graph"],
                "artifacts/baseline_graph.json",
            )
            self.assertIn("movement_score", response_plan["metrics_to_recheck"])
            self.assertFalse(response_plan["real_scheduling"])
            self.assertFalse(response_plan["notification_automation"])
            self.assertFalse(response_plan["reminder_automation"])
            self.assertFalse(response_plan["real_monitoring"])
            self.assertFalse(response_plan["recommendation_generated"])
            self.assertFalse(response_plan["prescription_generated"])
            self.assertFalse(response_plan["claim_effectiveness"])
            self.assertEqual(
                intervention_ledger["entries"][0]["intervention_tag_id"],
                intervention_tag["id"],
            )
            self.assertFalse(intervention_ledger["real_intervention_performed"])
            self.assertFalse(intervention_ledger["database_access"])
            self.assertEqual(follow_up_window["id"], "follow-up-observation-window-placeholder")
            self.assertEqual(follow_up_window["source_plan_id"], response_plan["id"])
            self.assertFalse(follow_up_window["real_scheduling"])
            self.assertFalse(follow_up_window["real_monitoring"])
            self.assertFalse(follow_up_window["reminder_automation"])
            self.assertEqual(follow_up_snapshot["id"], "follow-up-sensor-snapshot-placeholder")
            self.assertEqual(follow_up_snapshot["window_id"], follow_up_window["id"])
            self.assertEqual(follow_up_snapshot["source_feature_set_id"], feature_set["id"])
            self.assertEqual(follow_up_snapshot["features"]["movement_score"], 0.14)
            self.assertFalse(follow_up_snapshot["live_sensor_access"])
            self.assertFalse(follow_up_snapshot["hardware_access"])
            self.assertEqual(response_comparison["id"], "response-comparison-placeholder")
            self.assertEqual(
                response_comparison["artifact_refs"]["sensor_feature_set"],
                "artifacts/sensor_feature_set.json",
            )
            self.assertEqual(
                response_comparison["artifact_refs"]["baseline_comparison"],
                "artifacts/baseline_comparison.json",
            )
            self.assertEqual(
                response_comparison["artifact_refs"]["intervention_tag"],
                "artifacts/intervention_tag.json",
            )
            self.assertEqual(
                response_comparison["artifact_refs"]["response_evaluation_plan"],
                "artifacts/response_evaluation_plan.json",
            )
            self.assertEqual(
                response_comparison["artifact_refs"]["personal_profile"],
                "artifacts/personal_profile.json",
            )
            self.assertEqual(
                response_comparison["artifact_refs"]["baseline_graph"],
                "artifacts/baseline_graph.json",
            )
            for artifact_name in (
                "sensor_feature_set",
                "baseline_comparison",
                "intervention_tag",
                "response_evaluation_plan",
                "personal_profile",
                "baseline_graph",
            ):
                with self.subTest(response_hash=artifact_name):
                    self.assertEqual(
                        response_comparison["artifact_hashes"][artifact_name],
                        self._sha256(run_dir / "artifacts" / f"{artifact_name}.json"),
                    )
            response_by_category = {
                result["category"]: result for result in response_comparison["results"]
            }
            allowed_response_labels = {
                "toward_baseline",
                "away_from_baseline",
                "unchanged",
                "insufficient_data",
            }
            self.assertTrue(
                {result["trend_label"] for result in response_comparison["results"]}.issubset(
                    allowed_response_labels
                )
            )
            self.assertEqual(
                response_by_category["movement_score"]["trend_label"],
                "toward_baseline",
            )
            self.assertEqual(
                response_by_category["notes_placeholder"]["trend_label"],
                "insufficient_data",
            )
            self.assertFalse(response_comparison["effectiveness_claim"])
            self.assertFalse(response_comparison["recommendation_generated"])
            self.assertEqual(
                response_evaluation_summary["id"],
                "response-evaluation-summary-placeholder",
            )
            self.assertEqual(
                response_evaluation_summary["response_comparison_id"],
                response_comparison["id"],
            )
            self.assertEqual(response_evaluation_summary["trend_counts"]["toward_baseline"], 1)
            self.assertEqual(response_evaluation_summary["trend_counts"]["insufficient_data"], 1)
            self.assertFalse(response_evaluation_summary["effectiveness_claim"])
            self.assertFalse(response_evaluation_summary["claim_effectiveness"])
            self.assertFalse(response_evaluation_summary["recommendation_generated"])
            self.assertFalse(response_evaluation_summary["prescription_generated"])
            self.assertFalse(response_evaluation_summary["medical_advice"])
            self.assertFalse(response_evaluation_summary["real_monitoring"])
            self.assertFalse(response_evaluation_summary["real_scheduling"])
            self.assertTrue(summary["fake_backed_sensor_planning_only"])
            self.assertTrue(summary["fake_backed_local_baseline"])
            self.assertTrue(summary["fake_backed_intervention_tags"])
            self.assertTrue(summary["fake_backed_follow_up_generation"])
            self.assertTrue(summary["response_evaluation_planning_only"])
            self.assertTrue(summary["no_effectiveness_claim"])
            self.assertTrue(summary["sandbox_only"])
            self.assertFalse(summary["personal_data_exported"])
            self.assertFalse(summary["personal_health_data_exported"])
            self.assertFalse(summary["real_health_data_loaded"])
            self.assertFalse(summary["real_profile_storage"])
            self.assertTrue(summary["baseline_graph_local_only"])
            self.assertTrue(summary["baseline_comparison_planning_only"])
            self.assertFalse(summary["raw_sensor_data_collected"])
            self.assertFalse(summary["csi_capture"])
            self.assertTrue(summary["csi_planning_only"])
            self.assertEqual(
                summary["csi_parser_metadata"]["parser_id"],
                "somatic-csi-fixture-parser-v1",
            )
            self.assertEqual(
                summary["csi_parser_metadata"]["artifact_refs"]["report"],
                "artifacts/csi_parser_report.json",
            )
            self.assertEqual(
                summary["csi_parser_metadata"]["artifact_refs"]["summary"],
                "artifacts/csi_parsed_summary.json",
            )
            self.assertEqual(summary["csi_parser_metadata"]["sample_count"], 14)
            self.assertFalse(summary["csi_parser_metadata"]["network_calls"])
            self.assertFalse(summary["wifi_csi_capture"])
            self.assertFalse(summary["packet_capture"])
            self.assertFalse(summary["wifi_network_probing"])
            self.assertFalse(summary["monitor_mode"])
            self.assertFalse(summary["esp32_access"])
            self.assertFalse(summary["rtl8812au_access"])
            self.assertFalse(summary["router_access"])
            self.assertFalse(summary["driver_access"])
            self.assertFalse(summary["raw_rf_data_collected"])
            self.assertFalse(summary["raw_csi_data_collected"])
            self.assertFalse(summary["raw_rf_data_exported"])
            self.assertFalse(summary["raw_csi_data_exported"])
            self.assertFalse(summary["camera_capture"])
            self.assertFalse(summary["audio_capture"])
            self.assertFalse(summary["wearable_capture"])
            self.assertFalse(summary["ble_access"])
            self.assertFalse(summary["wifi_device_access"])
            self.assertFalse(summary["thermal_capture"])
            self.assertFalse(summary["clinical_interpretation"])
            self.assertEqual(summary["personal_profile_id"], personal_profile["id"])
            self.assertEqual(summary["baseline_graph_id"], baseline_graph["id"])
            self.assertEqual(
                summary["baseline_comparison_id"],
                baseline_comparison["id"],
            )
            self.assertEqual(
                summary["baseline_comparison_summary"]["status_by_category"]["movement_score"],
                "outside_baseline",
            )
            self.assertEqual(
                summary["baseline_comparison_summary"]["status_by_category"]["notes_placeholder"],
                "insufficient_data",
            )
            self.assertEqual(summary["intervention_tag_id"], intervention_tag["id"])
            self.assertEqual(
                summary["intervention_context_id"],
                intervention_context["id"],
            )
            self.assertEqual(
                summary["response_evaluation_plan_id"],
                response_plan["id"],
            )
            self.assertEqual(
                summary["mock_intervention_ledger_id"],
                intervention_ledger["id"],
            )
            self.assertEqual(
                summary["follow_up_observation_window_id"],
                follow_up_window["id"],
            )
            self.assertEqual(
                summary["follow_up_sensor_snapshot_id"],
                follow_up_snapshot["id"],
            )
            self.assertEqual(
                summary["response_comparison_id"],
                response_comparison["id"],
            )
            self.assertEqual(
                summary["response_evaluation_summary_id"],
                response_evaluation_summary["id"],
            )
            self.assertFalse(summary["intervention_summary"]["recommendation_generated"])
            self.assertFalse(summary["intervention_summary"]["prescription_generated"])
            self.assertFalse(summary["intervention_summary"]["claim_effectiveness"])
            self.assertFalse(summary["intervention_summary"]["real_scheduling"])
            self.assertFalse(summary["intervention_summary"]["reminder_automation"])
            self.assertEqual(
                summary["response_trend_summary"]["status_by_category"]["movement_score"],
                "toward_baseline",
            )
            self.assertEqual(
                summary["response_trend_summary"]["status_by_category"]["notes_placeholder"],
                "insufficient_data",
            )
            self.assertIn("toward_baseline", summary["response_trend_status_vocabulary"])
            self.assertFalse(summary["response_trend_summary"]["effectiveness_claim"])
            self.assertFalse(summary["response_trend_summary"]["medical_advice"])
            self.assertEqual(
                summary["csi_metadata"]["reference_inventory_ref"],
                "csi-reference-inventory-v1",
            )
            self.assertEqual(
                summary["artifact_hashes"]["csi_parser_report"],
                self._sha256(run_dir / "artifacts" / "csi_parser_report.json"),
            )
            self.assertEqual(
                summary["artifact_hashes"]["csi_parsed_summary"],
                self._sha256(run_dir / "artifacts" / "csi_parsed_summary.json"),
            )
            self.assertEqual(
                summary["artifact_hashes"]["csi_evidence_pack"],
                self._sha256(run_dir / "artifacts" / "csi_evidence_pack.json"),
            )
            self.assertEqual(
                summary["csi_evidence_scoring_metadata"],
                csi_evidence_scoring,
            )
            self.assertEqual(
                summary["csi_evidence_pack_metadata"]["pack_fingerprint"],
                csi_evidence_pack["pack_fingerprint"],
            )
            self.assertEqual(
                summary["csi_evidence_pack_metadata"]["artifact_sha256"],
                self._sha256(run_dir / "artifacts" / "csi_evidence_pack.json"),
            )
            self.assertEqual(
                summary["artifact_hashes"]["environment_evidence_pack"],
                self._sha256(run_dir / "artifacts" / "environment_evidence_pack.json"),
            )
            self.assertEqual(
                summary["environment_evidence_pack_metadata"]["pack_fingerprint"],
                environment_evidence_pack["pack_fingerprint"],
            )
            self.assertEqual(
                summary["environment_evidence_pack_metadata"]["artifact_sha256"],
                self._sha256(run_dir / "artifacts" / "environment_evidence_pack.json"),
            )
            self.assertEqual(summary["environment_readiness_metadata"]["row_count"], 3)
            for surface, refs in (
                ("manifest", manifest["sensor_evidence_artifact_refs"]),
                ("summary", summary["sensor_evidence_artifact_refs"]),
                ("report_packet", report_packet["sensor_evidence_artifact_refs"]),
                ("fabric_plan", fabric_pack_plan["sensor_evidence_artifact_refs"]),
            ):
                with self.subTest(generic_sensor_evidence_ref=surface):
                    generic_ref = refs["csi_evidence_pack"]
                    self.assertEqual(generic_ref["classification"], "compatible")
                    self.assertTrue(generic_ref["present"])
                    self.assertEqual(
                        generic_ref["artifact_ref"],
                        "artifacts/csi_evidence_pack.json",
                    )
                    self.assertEqual(
                        generic_ref["sha256"],
                        self._sha256(run_dir / "artifacts" / "csi_evidence_pack.json"),
                    )
                    self.assertEqual(
                        generic_ref["pack_fingerprint"],
                        csi_evidence_pack["pack_fingerprint"],
                    )
                    self.assertFalse(generic_ref["raw_signal_values_exported"])
                    environment_ref = refs["environment_evidence_pack"]
                    self.assertEqual(environment_ref["classification"], "compatible")
                    self.assertTrue(environment_ref["present"])
                    self.assertEqual(
                        environment_ref["artifact_ref"],
                        "artifacts/environment_evidence_pack.json",
                    )
                    self.assertEqual(
                        environment_ref["sha256"],
                        self._sha256(run_dir / "artifacts" / "environment_evidence_pack.json"),
                    )
                    self.assertEqual(
                        environment_ref["pack_fingerprint"],
                        environment_evidence_pack["pack_fingerprint"],
                    )
            self.assertEqual(
                fabric_pack_plan["planned_sensor_evidence_artifact_ids"],
                ["csi_evidence_pack", "environment_evidence_pack"],
            )
            self.assertEqual(
                summary["csi_parser_metadata"]["artifact_refs"]["evidence_pack"],
                "artifacts/csi_evidence_pack.json",
            )
            self.assertNotIn("fixture_refs", summary["csi_parser_metadata"])
            self.assertEqual(
                summary["csi_parser_metadata"]["evidence_scoring"],
                csi_evidence_scoring,
            )
            self.assertIn(
                "heart_rate_placeholder",
                summary["csi_metadata"]["mapped_feature_names"],
            )
            self.assertEqual(
                summary["csi_metadata"]["ruview_dependency"],
                "conditional-reference-only",
            )
            self.assertEqual(
                summary["csi_metadata"]["ruview_reference"]["status"],
                "conditional-reference-only",
            )
            self.assertFalse(
                summary["csi_metadata"]["ruview_reference"]["v2_reassessment"][
                    "downstream_accuracy_validated"
                ]
            )
            self.assertFalse(
                summary["csi_metadata"]["ruview_reference"]["v2_reassessment"][
                    "deployment_claims_verified"
                ]
            )
            self.assertEqual(
                summary["csi_metadata"]["booth_planning_profile"]["profile"],
                "booth-first-single-subject-v1",
            )
            self.assertEqual(
                summary["csi_metadata"]["booth_planning_profile"]["future_topology"],
                "fixed-ap-plus-4-to-6-receiver-nodes",
            )
            self.assertEqual(
                summary["csi_metadata"]["source_adapter_status"]["adapter_kind"],
                "metadata-wifi-csi-source-adapter",
            )
            self.assertEqual(
                summary["csi_metadata"]["source_adapter_output_validation"]["classification"],
                "compatible",
            )
            self.assertFalse(summary["csi_metadata"]["source_adapter_status"]["model_download"])
            self.assertFalse(summary["csi_metadata"]["source_adapter_status"]["model_execution"])
            self.assertFalse(summary["csi_metadata"]["source_adapter_status"]["vitals_inference"])
            self.assertEqual(report_packet["id"], "n-of-1-report-packet")
            self.assertEqual(report_packet["run_id"], "run-n-of-1-test")
            self.assertEqual(report_packet["workflow_mode"], "n-of-1")
            self.assertEqual(
                report_packet["artifact_count"],
                len(NOF1_PACKET_INPUT_ARTIFACTS),
            )
            self.assertTrue(report_packet["packet_complete"])
            self.assertEqual(report_packet["packet_status"], "complete")
            self.assertEqual(report_packet["missing_artifacts"], [])
            self.assertFalse(report_packet["medical_record"])
            self.assertFalse(report_packet["advice_generated"])
            self.assertFalse(report_packet["effectiveness_claim"])
            self.assertFalse(report_packet["real_monitoring"])
            self.assertFalse(report_packet["real_scheduling"])
            self.assertEqual(
                [stage["stage"] for stage in report_packet["loop_stages"]],
                [
                    "observation",
                    "baseline",
                    "intervention_tag",
                    "follow_up",
                    "response_comparison",
                ],
            )
            packet_refs = report_packet["artifact_refs"]
            self.assertEqual(set(packet_refs), set(NOF1_PACKET_INPUT_ARTIFACTS))
            for artifact_name in NOF1_PACKET_INPUT_ARTIFACTS:
                with self.subTest(report_packet_ref=artifact_name):
                    artifact_path = run_dir / "artifacts" / f"{artifact_name}.json"
                    self.assertTrue(packet_refs[artifact_name]["present"])
                    self.assertEqual(
                        packet_refs[artifact_name]["relative_path"],
                        f"artifacts/{artifact_name}.json",
                    )
                    self.assertEqual(
                        packet_refs[artifact_name]["sha256"],
                        self._sha256(artifact_path),
                    )
                    self.assertEqual(
                        report_packet["artifact_hashes"][artifact_name],
                        self._sha256(artifact_path),
                    )
            packet_flags = report_packet["safety_boundary_flags"]
            for flag in (
                "fake_backed",
                "no_hardware",
                "no_real_health_data",
                "no_diagnosis",
                "no_treatment",
                "no_recommendation",
                "no_prescription",
                "no_emergency_triage",
                "no_effectiveness_claim",
                "no_monitoring",
                "no_scheduling",
            ):
                with self.subTest(packet_flag=flag):
                    self.assertTrue(packet_flags[flag])
            self.assertEqual(fabric_pack_plan["id"], "n-of-1-fabric-pack-plan")
            self.assertEqual(fabric_pack_plan["run_id"], "run-n-of-1-test")
            self.assertEqual(fabric_pack_plan["class"], "data")
            self.assertEqual(fabric_pack_plan["suggested_type"], "document")
            self.assertEqual(
                fabric_pack_plan["report_packet_ref"],
                "artifacts/n_of_1_report_packet.json",
            )
            self.assertEqual(
                fabric_pack_plan["report_packet_sha256"],
                self._sha256(run_dir / "artifacts" / "n_of_1_report_packet.json"),
            )
            self.assertEqual(
                fabric_pack_plan["artifact_hashes"],
                report_packet["artifact_hashes"],
            )
            self.assertTrue(fabric_pack_plan["planning_only"])
            self.assertTrue(fabric_pack_plan["private_only_by_default"])
            self.assertFalse(fabric_pack_plan["seedable"])
            self.assertFalse(fabric_pack_plan["publishing_enabled"])
            self.assertFalse(fabric_pack_plan["signing_enabled"])
            self.assertFalse(fabric_pack_plan["catalog_publication_enabled"])
            self.assertFalse(fabric_pack_plan["transport_enabled"])
            self.assertFalse(fabric_pack_plan["magnet_uri_created"])
            self.assertFalse(fabric_pack_plan["webseed_created"])
            self.assertFalse(fabric_pack_plan["contains_code"])
            self.assertFalse(fabric_pack_plan["contains_executable_files"])
            self.assertEqual(fabric_pack_plan["executable_files"], [])
            self.assertFalse(fabric_pack_plan["personal_health_data_exported"])
            self.assertFalse(fabric_pack_plan["raw_real_health_data_allowed"])
            file_plans = {
                file_plan["id"]: file_plan for file_plan in fabric_pack_plan["file_plans"]
            }
            self.assertIn("n_of_1_report_packet", file_plans)
            self.assertEqual(
                file_plans["n_of_1_report_packet"]["path"],
                "artifacts/n_of_1_report_packet.json",
            )
            self.assertEqual(
                file_plans["n_of_1_report_packet"]["sha256"],
                self._sha256(run_dir / "artifacts" / "n_of_1_report_packet.json"),
            )
            for artifact_name in NOF1_PACKET_INPUT_ARTIFACTS:
                with self.subTest(fabric_plan_ref=artifact_name):
                    self.assertIn(artifact_name, file_plans)
                    self.assertEqual(
                        file_plans[artifact_name]["path"],
                        f"artifacts/{artifact_name}.json",
                    )
                    self.assertEqual(
                        file_plans[artifact_name]["sha256"],
                        report_packet["artifact_hashes"][artifact_name],
                    )
            self.assertFalse(file_plans["csi_parser_report"]["include_in_candidate"])
            self.assertFalse(file_plans["csi_parsed_summary"]["include_in_candidate"])
            self.assertTrue(file_plans["csi_evidence_pack"]["include_in_candidate"])
            self.assertTrue(file_plans["environment_evidence_pack"]["include_in_candidate"])

            boundary_phrases = (
                "fake-backed sensor planning only",
                "mock/offline",
                "research-only",
                "sandbox-only",
                "no real hardware access",
                "no live sensor access",
                "no csi/camera/audio/wearable capture",
                "no wifi csi packet capture",
                "no esp32, rtl8812au, router, adapter, or driver access",
                "raw rf/csi data is local-first and private by default",
                "raw rf/csi data collected: false",
                "csi parser report",
                "csi_parsed_summary.json",
                "csi evidence pack",
                "csi_evidence_pack.json",
                "csi evidence quality score",
                "csi replay integrity score",
                "local fake/sample fixtures only",
                "no serial, mqtt, udp, pcap, monitor mode, or live capture",
                "ruview dependency: `conditional-reference-only`",
                "ruview reference status: `conditional-reference-only`",
                "csi source adapter validation: `compatible`",
                "booth-first profile: `booth-first-single-subject-v1`",
                "booth future topology: `fixed-ap-plus-4-to-6-receiver-nodes`",
                "booth research notes: phase-variance, conjugation, temporal-embedding",
                "personal baseline planning",
                "baseline comparison results",
                "fake-backed local baseline",
                "no real health data",
                "no real profile storage",
                "within_baseline",
                "outside_baseline",
                "insufficient_data",
                "explicit local storage consent",
                "data-locality review",
                "mock intervention tag summary",
                "response evaluation plan summary",
                "follow-up observation window summary",
                "response comparison summary",
                "response evaluation summary",
                "n-of-1 report packet",
                "n_of_1_report_packet.json",
                "n-of-1 fabric pack plan",
                "n_of_1_fabric_pack_plan.json",
                "private-only",
                "no fabric signing, catalog publication, transport, magnet, webseed, "
                "seeding, upload, install, or execution",
                "no real personal data export",
                "artifact count/hash summary",
                "loop-stage summary",
                "strict boundary summary",
                "packet is not a medical record",
                "hashes are for reproducibility/provenance only",
                "no recommendation",
                "no prescription",
                "no effectiveness claim",
                "no intervention effectiveness is claimed",
                "fixture trend labels only",
                "medication placeholder disabled",
                "clinician review placeholder disabled",
                "no reminders, automation, or scheduling",
                "no network calls",
                "no real monitoring",
                "no diagnosis, treatment, or emergency triage",
                "not medical advice",
                "explicit user consent",
                "local-first privacy policy",
                "safety review",
            )
            for phrase in boundary_phrases:
                with self.subTest(phrase=phrase):
                    self.assertIn(phrase.lower(), report.lower())

    def test_n_of_1_artifacts_are_deterministic_across_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            left = run_mock_workflow(
                NOF1_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-n-of-1-left",
            )
            right = run_mock_workflow(
                NOF1_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-n-of-1-right",
            )

            for artifact_name in NOF1_ARTIFACTS:
                with self.subTest(artifact_name=artifact_name):
                    left_payload = self._read_json(left / "artifacts" / f"{artifact_name}.json")
                    right_payload = self._read_json(right / "artifacts" / f"{artifact_name}.json")
                    if artifact_name == "n_of_1_report_packet":
                        for payload in (left_payload, right_payload):
                            payload.pop("run_id", None)
                            payload.pop("generated_at", None)
                        self.assertEqual(left_payload, right_payload)
                    elif artifact_name == "n_of_1_fabric_pack_plan":
                        for payload in (left_payload, right_payload):
                            payload.pop("run_id", None)
                            payload.pop("generated_at", None)
                            payload.pop("source_run_dir", None)
                            payload.pop("report_packet_sha256", None)
                            for file_plan in payload["file_plans"]:
                                if file_plan["id"] == "n_of_1_report_packet":
                                    file_plan.pop("sha256", None)
                        self.assertEqual(left_payload, right_payload)
                    else:
                        self.assertEqual(left_payload, right_payload)
                        self.assertEqual(
                            self._sha256(left / "artifacts" / f"{artifact_name}.json"),
                            self._sha256(right / "artifacts" / f"{artifact_name}.json"),
                        )

    def test_existing_workflows_and_fabric_check_still_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected_mode_artifacts = {
                "valid-literature-only.yaml": ("hypotheses",),
                "valid-hypothesis-tournament.yaml": ("ranked_hypotheses", "team_roster"),
                "valid-robin-loop.yaml": ("robin_loop_summary", "structured_verdict"),
                "valid-in-silico-screening.yaml": ("in_silico_summary", "biomodel_plan"),
            }
            for fixture_name, artifact_names in expected_mode_artifacts.items():
                with self.subTest(fixture_name=fixture_name):
                    run_dir = run_mock_workflow(
                        WORKFLOW_DIR / fixture_name,
                        repo_root=REPO_ROOT,
                        output_root=Path(tmp),
                        run_id=f"run-{fixture_name.removesuffix('.yaml')}",
                    )
                    manifest = self._read_json(run_dir / "manifest.json")
                    for artifact_name in artifact_names:
                        self.assertIn(artifact_name, manifest["artifacts"])
                        self.assertTrue((run_dir / manifest["artifacts"][artifact_name]).exists())

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
            self.assertIn("Fabric check: valid signed-code-pack.json", output)
            self.assertIn("crypto: publisher threshold verified", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())
            self.assertIn("failing closed", output.lower())
            self.assertIn("optional fabric extra", output.lower())

    def test_rejects_n_of_1_workflow_with_live_capture_enabled(self):
        unsafe_workflow = textwrap.dedent(
            """
            schema_version: 1
            id: unsafe-n-of-1
            title: Unsafe N-of-1 Fixture
            mode: n-of-1
            description: Unsafe fixture that tries to enable live capture.
            version: 0.7.0
            status: fixture
            stages: []
            inputs: []
            providers:
              - ref: sensor
                class: sensor
                capabilities:
                  - sensor.sandbox.observe
                required: true
                constraints:
                  offline_required: true
                  mock_only: true
                  fake_backed: true
                  research_only: true
                  allow_live_capture: true
            artifacts: []
            safety_profile:
              risk_class: low
              domain: sensor-research
              human_review_required: true
              external_actions_allowed: false
              real_lab_action_requires_approval: false
              clinical_safety_gate_required: false
              code_pack_quarantine_required: false
            evidence_requirements:
              min_records: 1
            output_packet:
              kind: report-packet
              review_state: human-review-required
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe-n-of-1.yaml"
            path.write_text(unsafe_workflow, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "allow_live_capture"):
                run_mock_workflow(
                    path,
                    repo_root=REPO_ROOT,
                    output_root=Path(tmp),
                    run_id="run-unsafe-n-of-1",
                )

    def test_rejects_n_of_1_workflow_missing_required_sandbox_constraints(self):
        unsafe_workflow = textwrap.dedent(
            """
            schema_version: 1
            id: unsafe-n-of-1-missing-sandbox-flags
            title: Unsafe N-of-1 Missing Sandbox Flags
            mode: n-of-1
            description: Unsafe fixture that omits required sandbox flags.
            version: 0.7.0
            status: fixture
            stages: []
            inputs: []
            providers:
              - ref: sensor
                class: sensor
                capabilities:
                  - sensor.sandbox.observe
                required: true
                constraints:
                  offline_required: true
            artifacts: []
            safety_profile:
              risk_class: low
              domain: sensor-research
              human_review_required: true
              external_actions_allowed: false
              real_lab_action_requires_approval: false
              clinical_safety_gate_required: false
              code_pack_quarantine_required: false
            evidence_requirements:
              min_records: 1
            output_packet:
              kind: report-packet
              review_state: human-review-required
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe-n-of-1-missing-sandbox-flags.yaml"
            path.write_text(unsafe_workflow, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "mock_only"):
                run_mock_workflow(
                    path,
                    repo_root=REPO_ROOT,
                    output_root=Path(tmp),
                    run_id="run-unsafe-n-of-1-missing-sandbox-flags",
                )

    def test_phase7a_docs_and_fixtures_contain_required_boundary_language(self):
        required_phrases = (
            "fake-backed",
            "no hardware",
            "no diagnosis",
            "no emergency triage",
            "real sensor mode requires explicit",
            "fake-backed local baseline",
            "no real health data",
            "explicit local storage consent",
            "data-locality review",
            "mock intervention",
            "no prescription",
            "no recommendation",
            "no reminders",
            "no effectiveness claim",
            "no real monitoring",
            "local-first privacy",
            "safety review",
        )
        for path in (
            REPO_ROOT / "docs" / "sensor-provider-boundary.md",
            REPO_ROOT / "docs" / "n-of-1-workflow.md",
            REPO_ROOT / "docs" / "sensor-privacy-boundary.md",
            REPO_ROOT / "docs" / "personal-baseline-graph.md",
            REPO_ROOT / "docs" / "baseline-privacy-boundary.md",
            REPO_ROOT / "docs" / "n-of-1-intervention-tags.md",
            REPO_ROOT / "docs" / "n-of-1-response-evaluation.md",
            REPO_ROOT / "docs" / "n-of-1-report-packet.md",
            REPO_ROOT / "docs" / "n-of-1-fabric-pack-plan.md",
            NOF1_FIXTURE,
        ):
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=path.name):
                for phrase in required_phrases:
                    self.assertIn(phrase, text)

    def test_n_of_1_runtime_adds_no_network_or_hardware_import_surfaces(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "anthropic",
            "websocket",
            "aiohttp",
            "httpx",
            "supabase",
            "psycopg2",
            "asyncpg",
            "sqlite3",
            "sqlalchemy",
            "pymongo",
            "firebase_admin",
            "boto3",
            "azure",
            "google",
            "scapy",
            "pyshark",
            "pcapy",
            "dpkt",
            "wifi",
            "cv2",
            "mediapipe",
            "pyaudio",
            "sounddevice",
            "librosa",
            "bleak",
            "bluetooth",
            "serial",
            "usb",
            "pyusb",
            "numpy",
            "scipy",
            "pandas",
            "neurokit2",
            "apscheduler",
            "schedule",
            "celery",
            "rq",
            "redis",
            "twilio",
            "smtplib",
        }
        forbidden_call_names = {
            "urlopen",
            "urlretrieve",
            "request",
            "create_connection",
            "sniff",
            "pcap",
            "set_monitor_mode",
            "VideoCapture",
            "InputStream",
            "Microphone",
            "scan",
            "connect",
            "connect_db",
            "execute",
            "cursor",
            "download",
            "schedule",
            "add_job",
            "send_notification",
            "notify",
            "remind",
            "start_monitoring",
            "prescribe",
        }
        for path in (
            REPO_ROOT / "somatic" / "mock_runtime.py",
            REPO_ROOT / "somatic" / "memory" / "baseline.py",
            REPO_ROOT / "somatic" / "memory" / "profile.py",
            REPO_ROOT / "somatic" / "memory" / "intervention.py",
            REPO_ROOT / "somatic" / "memory" / "response_evaluation.py",
            REPO_ROOT / "somatic" / "reports" / "n_of_1_packet.py",
            REPO_ROOT / "somatic" / "reports" / "n_of_1_fabric_plan.py",
            REPO_ROOT / "somatic" / "providers" / "sensors.py",
            REPO_ROOT / "somatic" / "sensors" / "csi.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_formats.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_parser.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_batch.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_scoring.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_evidence_pack.py",
            REPO_ROOT / "somatic" / "sensors" / "environment.py",
            REPO_ROOT / "somatic" / "sensors" / "environment_evidence_pack.py",
            REPO_ROOT / "somatic" / "sensors" / "sandbox.py",
        ):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        module = node.module.split(".")[0]
                        self.assertNotIn(module, forbidden_import_roots)
                    if isinstance(node, ast.Call):
                        name = (
                            node.func.id
                            if isinstance(node.func, ast.Name)
                            else getattr(node.func, "attr", None)
                        )
                        self.assertNotIn(name, forbidden_call_names)

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def _sha256(path):
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _assert_no_forbidden_csi_artifact_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(csi_artifact_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_CSI_REPORT_KEYS)
                self._assert_no_forbidden_csi_artifact_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_artifact_keys(item)

    def _assert_no_forbidden_csi_artifact_words(
        self,
        payload,
        *,
        allow_general_sample_text=False,
    ):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_csi_artifact_words(
                    value,
                    allow_general_sample_text=allow_general_sample_text,
                )
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_artifact_words(
                    item,
                    allow_general_sample_text=allow_general_sample_text,
                )
        elif isinstance(payload, str):
            self._assert_no_forbidden_csi_text(
                payload,
                allow_general_sample_text=allow_general_sample_text,
            )

    def _assert_no_forbidden_csi_text(self, text, *, allow_general_sample_text=False):
        lowered = (
            text.lower()
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
        forbidden_words = (
            tuple(word for word in FORBIDDEN_CSI_REPORT_WORDS if word != "samples")
            if allow_general_sample_text
            else FORBIDDEN_CSI_REPORT_WORDS
        )
        for word in forbidden_words:
            with self.subTest(csi_artifact_forbidden_word=word):
                self.assertIsNone(
                    re.search(
                        rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])",
                        lowered,
                    )
                )

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

    def _assert_no_report_or_fabric_plan_leaks(self, payload):
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
            "provider_payload",
            "provider_payload_body",
            "parser_report_payload",
            "parser_report_body",
            "parsed_summary_payload",
            "parser_summary_body",
            "api_key",
            "access_token",
            "refresh_token",
            "secret_value",
            "authorization",
            "bearer",
        ):
            with self.subTest(report_plan_leak=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
