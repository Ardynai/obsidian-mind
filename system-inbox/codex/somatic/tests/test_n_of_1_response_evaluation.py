import ast
import json
import unittest
from pathlib import Path

from somatic.memory.baseline import (
    build_baseline_graph,
    build_personal_profile,
    compare_feature_set_to_baseline,
)
from somatic.memory.intervention import load_fake_intervention_plan
from somatic.memory.response_evaluation import (
    RESPONSE_TREND_STATUSES,
    build_follow_up_observation_window,
    build_follow_up_sensor_snapshot,
    build_response_comparison,
    build_response_evaluation_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_FIXTURE_DIR = REPO_ROOT / "fixtures" / "baseline"


class NOf1ResponseEvaluationTests(unittest.TestCase):
    def test_response_evaluation_fixtures_parse_and_keep_boundaries_closed(self):
        for filename in (
            "follow-up-observation-window-placeholder.json",
            "follow-up-sensor-snapshot-placeholder.json",
            "response-comparison-placeholder.json",
            "response-evaluation-summary-placeholder.json",
        ):
            with self.subTest(filename=filename):
                payload = self._read_json(BASELINE_FIXTURE_DIR / filename)
                self.assertEqual(payload["schema_version"], 1)
                self.assertTrue(payload["mock"])
                self.assertTrue(payload["offline"])
                self.assertTrue(payload["research_only"])
                self.assertTrue(payload["sandbox_only"])
                self.assertTrue(payload["fake_backed"])
                self.assertTrue(payload["local_only"])
                self.assertFalse(payload["effectiveness_claim"])
                self.assertFalse(payload["claim_effectiveness"])
                self.assertFalse(payload["recommendation_generated"])
                self.assertFalse(payload["prescription_generated"])
                self.assertFalse(payload["treatment_recommendation"])
                self.assertFalse(payload["medical_advice"])
                self.assertFalse(payload["real_monitoring"])
                self.assertFalse(payload["real_scheduling"])
                self.assertFalse(payload["notification_automation"])
                self.assertFalse(payload["reminder_automation"])
                self.assertFalse(payload["network_calls"])
                self.assertFalse(payload["database_access"])
                self.assertFalse(payload["external_memory"])

    def test_response_evaluation_fixtures_match_deterministic_builder_contract(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        payloads = self._payloads(workflow)
        comparison = build_response_comparison(
            workflow=workflow,
            follow_up_snapshot=payloads["follow_up_snapshot"],
            sensor_feature_set_payload=payloads["feature_set"],
            baseline_comparison_payload=payloads["baseline_comparison"],
            intervention_tag_payload=payloads["intervention_tag"],
            response_evaluation_plan_payload=payloads["response_plan"],
            personal_profile_payload=payloads["profile"],
            baseline_graph_payload=payloads["baseline_graph"],
            artifact_hashes=self._placeholder_hashes(),
        )
        summary = build_response_evaluation_summary(
            workflow=workflow,
            follow_up_window=payloads["follow_up_window"],
            follow_up_snapshot=payloads["follow_up_snapshot"],
            response_comparison=comparison,
        )

        expected = {
            "follow-up-observation-window-placeholder.json": payloads["follow_up_window"].to_dict(),
            "follow-up-sensor-snapshot-placeholder.json": payloads["follow_up_snapshot"].to_dict(),
            "response-comparison-placeholder.json": comparison.to_dict(),
            "response-evaluation-summary-placeholder.json": summary.to_dict(),
        }
        for filename, expected_payload in expected.items():
            with self.subTest(filename=filename):
                fixture_payload = self._read_json(BASELINE_FIXTURE_DIR / filename)
                self.assertEqual(fixture_payload, self._with_schema(expected_payload))

    def test_follow_up_generation_is_deterministic_and_local_only(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        response_plan = self._response_plan_payload(workflow)

        left_window = build_follow_up_observation_window(workflow, response_plan).to_dict()
        right_window = build_follow_up_observation_window(workflow, response_plan).to_dict()
        self.assertEqual(left_window, right_window)
        self.assertEqual(left_window["id"], "follow-up-observation-window-placeholder")
        self.assertEqual(left_window["source_plan_id"], response_plan["id"])
        self.assertFalse(left_window["real_scheduling"])
        self.assertFalse(left_window["real_monitoring"])
        self.assertFalse(left_window["reminder_automation"])

        left_snapshot = build_follow_up_sensor_snapshot(
            workflow,
            build_follow_up_observation_window(workflow, response_plan),
            self._feature_set(),
        ).to_dict()
        right_snapshot = build_follow_up_sensor_snapshot(
            workflow,
            build_follow_up_observation_window(workflow, response_plan),
            self._feature_set(),
        ).to_dict()
        self.assertEqual(left_snapshot, right_snapshot)
        self.assertEqual(left_snapshot["id"], "follow-up-sensor-snapshot-placeholder")
        self.assertEqual(left_snapshot["features"]["movement_score"], 0.14)
        self.assertEqual(left_snapshot["source_feature_set_id"], self._feature_set()["id"])
        self.assertFalse(left_snapshot["live_sensor_access"])
        self.assertFalse(left_snapshot["hardware_access"])

    def test_response_comparison_references_expected_artifacts_and_labels(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        payloads = self._payloads(workflow)
        comparison = build_response_comparison(
            workflow=workflow,
            follow_up_snapshot=payloads["follow_up_snapshot"],
            sensor_feature_set_payload=payloads["feature_set"],
            baseline_comparison_payload=payloads["baseline_comparison"],
            intervention_tag_payload=payloads["intervention_tag"],
            response_evaluation_plan_payload=payloads["response_plan"],
            personal_profile_payload=payloads["profile"],
            baseline_graph_payload=payloads["baseline_graph"],
            artifact_hashes={
                "sensor_feature_set": "feature-sha-placeholder",
                "baseline_comparison": "comparison-sha-placeholder",
                "intervention_tag": "tag-sha-placeholder",
                "response_evaluation_plan": "plan-sha-placeholder",
                "personal_profile": "profile-sha-placeholder",
                "baseline_graph": "graph-sha-placeholder",
            },
        ).to_dict()

        self.assertEqual(comparison["id"], "response-comparison-placeholder")
        self.assertEqual(
            comparison["artifact_refs"]["sensor_feature_set"],
            "artifacts/sensor_feature_set.json",
        )
        self.assertEqual(
            comparison["artifact_refs"]["baseline_comparison"],
            "artifacts/baseline_comparison.json",
        )
        self.assertEqual(
            comparison["artifact_refs"]["intervention_tag"],
            "artifacts/intervention_tag.json",
        )
        self.assertEqual(
            comparison["artifact_refs"]["response_evaluation_plan"],
            "artifacts/response_evaluation_plan.json",
        )
        self.assertEqual(
            comparison["artifact_refs"]["personal_profile"],
            "artifacts/personal_profile.json",
        )
        self.assertEqual(
            comparison["artifact_refs"]["baseline_graph"],
            "artifacts/baseline_graph.json",
        )
        self.assertEqual(
            comparison["artifact_hashes"]["response_evaluation_plan"],
            "plan-sha-placeholder",
        )
        labels = {result["trend_label"] for result in comparison["results"]}
        self.assertTrue(labels.issubset(set(RESPONSE_TREND_STATUSES)))
        self.assertIn("toward_baseline", labels)
        self.assertIn("unchanged", labels)
        self.assertIn("insufficient_data", labels)
        movement = {result["category"]: result for result in comparison["results"]}[
            "movement_score"
        ]
        self.assertEqual(movement["trend_label"], "toward_baseline")
        self.assertFalse(comparison["effectiveness_claim"])
        self.assertFalse(comparison["recommendation_generated"])

    def test_response_evaluation_summary_is_non_clinical_and_deterministic(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        payloads = self._payloads(workflow)
        comparison = build_response_comparison(
            workflow=workflow,
            follow_up_snapshot=payloads["follow_up_snapshot"],
            sensor_feature_set_payload=payloads["feature_set"],
            baseline_comparison_payload=payloads["baseline_comparison"],
            intervention_tag_payload=payloads["intervention_tag"],
            response_evaluation_plan_payload=payloads["response_plan"],
            personal_profile_payload=payloads["profile"],
            baseline_graph_payload=payloads["baseline_graph"],
            artifact_hashes={},
        )

        left = build_response_evaluation_summary(
            workflow=workflow,
            follow_up_window=payloads["follow_up_window"],
            follow_up_snapshot=payloads["follow_up_snapshot"],
            response_comparison=comparison,
        ).to_dict()
        right = build_response_evaluation_summary(
            workflow=workflow,
            follow_up_window=payloads["follow_up_window"],
            follow_up_snapshot=payloads["follow_up_snapshot"],
            response_comparison=comparison,
        ).to_dict()

        self.assertEqual(left, right)
        self.assertEqual(left["id"], "response-evaluation-summary-placeholder")
        self.assertEqual(left["response_comparison_id"], comparison.id)
        self.assertEqual(left["trend_counts"]["toward_baseline"], 1)
        self.assertEqual(left["trend_counts"]["insufficient_data"], 1)
        self.assertFalse(left["effectiveness_claim"])
        self.assertFalse(left["claim_effectiveness"])
        self.assertFalse(left["recommendation_generated"])
        self.assertFalse(left["prescription_generated"])
        self.assertFalse(left["medical_advice"])
        self.assertFalse(left["real_monitoring"])
        self.assertFalse(left["real_scheduling"])

    def test_response_evaluation_scaffold_adds_no_network_hardware_database_or_scheduling_imports(
        self,
    ):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "websocket",
            "aiohttp",
            "httpx",
            "openai",
            "anthropic",
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
            "bleak",
            "bluetooth",
            "serial",
            "usb",
            "pyusb",
            "cv2",
            "mediapipe",
            "pyaudio",
            "sounddevice",
            "librosa",
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
            "connect",
            "send",
            "recv",
            "sniff",
            "pcap",
            "set_monitor_mode",
            "scan",
            "download",
            "VideoCapture",
            "InputStream",
            "Microphone",
            "connect_db",
            "execute",
            "cursor",
            "schedule",
            "add_job",
            "send_notification",
            "notify",
            "remind",
            "start_monitoring",
            "prescribe",
        }
        path = REPO_ROOT / "somatic" / "memory" / "response_evaluation.py"
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

    def _payloads(self, workflow):
        profile = build_personal_profile(workflow)
        baseline_graph = build_baseline_graph(profile, workflow)
        feature_set = self._feature_set()
        baseline_comparison = compare_feature_set_to_baseline(feature_set, baseline_graph).to_dict()
        tag, context, response_plan, _ledger = load_fake_intervention_plan(
            workflow=workflow,
            sensor_feature_set_payload=feature_set,
            baseline_comparison_payload=baseline_comparison,
            personal_profile_payload=profile.to_dict(),
            baseline_graph_payload=baseline_graph.to_dict(),
            artifact_hashes={},
        )
        follow_up_window = build_follow_up_observation_window(workflow, response_plan.to_dict())
        follow_up_snapshot = build_follow_up_sensor_snapshot(
            workflow, follow_up_window, feature_set
        )
        return {
            "feature_set": feature_set,
            "baseline_comparison": baseline_comparison,
            "profile": profile.to_dict(),
            "baseline_graph": baseline_graph.to_dict(),
            "intervention_tag": tag.to_dict(),
            "intervention_context": context.to_dict(),
            "response_plan": response_plan.to_dict(),
            "follow_up_window": follow_up_window,
            "follow_up_snapshot": follow_up_snapshot,
        }

    def _response_plan_payload(self, workflow):
        return self._payloads(workflow)["response_plan"]

    @staticmethod
    def _feature_set():
        return {
            "schema_version": 1,
            "id": "sensor-feature-set-n-of-1-sandbox",
            "features": {
                "respiratory_rate": 14,
                "movement_score": 0.18,
                "posture_state": "upright-placeholder",
                "sleep_state_estimate": "awake-placeholder",
                "environmental_context_placeholder": "room-context-placeholder",
                "audio_event_placeholder": "none-observed-placeholder",
            },
            "metadata": {
                "csi": {
                    "feature_set": {
                        "features": {
                            "confidence": "not-applicable",
                        },
                    },
                },
            },
        }

    @staticmethod
    def _placeholder_hashes():
        return {
            "sensor_feature_set": "placeholder-sha256",
            "baseline_comparison": "placeholder-sha256",
            "intervention_tag": "placeholder-sha256",
            "response_evaluation_plan": "placeholder-sha256",
            "personal_profile": "placeholder-sha256",
            "baseline_graph": "placeholder-sha256",
        }

    @staticmethod
    def _with_schema(payload):
        return {"schema_version": 1, **payload}

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
