import ast
import json
import unittest
from pathlib import Path

from somatic.memory.baseline import (
    build_baseline_graph,
    build_personal_profile,
    compare_feature_set_to_baseline,
)
from somatic.memory.intervention import (
    INTERVENTION_CATEGORIES,
    build_intervention_context,
    build_intervention_tag,
    build_mock_intervention_ledger,
    build_response_evaluation_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_FIXTURE_DIR = REPO_ROOT / "fixtures" / "baseline"


class NOf1InterventionTagTests(unittest.TestCase):
    def test_intervention_fixtures_parse_and_keep_boundaries_closed(self):
        for filename in (
            "intervention-tag-placeholder.json",
            "intervention-context-placeholder.json",
            "response-evaluation-plan-placeholder.json",
            "mock-intervention-ledger-placeholder.json",
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
                self.assertFalse(payload["recommendation_generated"])
                self.assertFalse(payload["prescription_generated"])
                self.assertFalse(payload["treatment_recommendation"])
                self.assertFalse(payload["medical_advice"])
                self.assertFalse(payload["emergency_triage"])
                self.assertFalse(payload["real_monitoring"])
                self.assertFalse(payload["real_scheduling"])
                self.assertFalse(payload["notification_automation"])
                self.assertFalse(payload["reminder_automation"])
                self.assertFalse(payload["network_calls"])
                self.assertFalse(payload["database_access"])
                self.assertFalse(payload["external_memory"])

    def test_intervention_tag_generation_is_deterministic(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}

        left = build_intervention_tag(workflow).to_dict()
        right = build_intervention_tag(workflow).to_dict()

        self.assertEqual(left, right)
        self.assertEqual(left["id"], "intervention-tag-placeholder")
        self.assertEqual(left["category"], "rest_placeholder")
        self.assertEqual(left["categories"], list(INTERVENTION_CATEGORIES))
        self.assertFalse(left["recommendation_generated"])
        self.assertFalse(left["prescription_generated"])
        self.assertFalse(left["treatment_recommendation"])
        disabled = {item["category"]: item for item in left["category_statuses"]}
        self.assertTrue(disabled["medication_placeholder_disabled"]["disabled"])
        self.assertTrue(disabled["clinician_review_placeholder"]["disabled"])

    def test_intervention_context_references_existing_n_of_1_artifacts(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        tag = build_intervention_tag(workflow)
        profile = build_personal_profile(workflow)
        graph = build_baseline_graph(profile, workflow)
        comparison = compare_feature_set_to_baseline(self._feature_set(), graph).to_dict()
        context = build_intervention_context(
            workflow=workflow,
            tag=tag,
            sensor_feature_set_payload=self._feature_set(),
            baseline_comparison_payload=comparison,
            personal_profile_payload=profile.to_dict(),
            baseline_graph_payload=graph.to_dict(),
            artifact_hashes={
                "sensor_feature_set": "feature-sha-placeholder",
                "baseline_comparison": "comparison-sha-placeholder",
                "personal_profile": "profile-sha-placeholder",
                "baseline_graph": "graph-sha-placeholder",
            },
        ).to_dict()

        self.assertEqual(context["intervention_tag_id"], tag.id)
        self.assertEqual(
            context["artifact_refs"]["sensor_feature_set"],
            "artifacts/sensor_feature_set.json",
        )
        self.assertEqual(
            context["artifact_refs"]["baseline_comparison"],
            "artifacts/baseline_comparison.json",
        )
        self.assertEqual(
            context["artifact_refs"]["personal_profile"],
            "artifacts/personal_profile.json",
        )
        self.assertEqual(
            context["artifact_refs"]["baseline_graph"],
            "artifacts/baseline_graph.json",
        )
        self.assertEqual(
            context["artifact_hashes"]["baseline_comparison"],
            "comparison-sha-placeholder",
        )
        self.assertFalse(context["recommendation_generated"])
        self.assertFalse(context["real_monitoring"])

    def test_response_evaluation_plan_is_deterministic_and_not_scheduled(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        tag = build_intervention_tag(workflow)
        profile = build_personal_profile(workflow)
        graph = build_baseline_graph(profile, workflow)
        comparison = compare_feature_set_to_baseline(self._feature_set(), graph).to_dict()
        context = build_intervention_context(
            workflow=workflow,
            tag=tag,
            sensor_feature_set_payload=self._feature_set(),
            baseline_comparison_payload=comparison,
            personal_profile_payload=profile.to_dict(),
            baseline_graph_payload=graph.to_dict(),
            artifact_hashes={},
        )

        left = build_response_evaluation_plan(workflow, tag, context, comparison).to_dict()
        right = build_response_evaluation_plan(workflow, tag, context, comparison).to_dict()

        self.assertEqual(left, right)
        self.assertEqual(left["future_comparison_window"], "placeholder-follow-up-window")
        self.assertIn("movement_score", left["metrics_to_recheck"])
        self.assertIn("notes_placeholder", left["metrics_to_recheck"])
        self.assertEqual(left["baseline_categories_to_compare"], list(graph.categories))
        self.assertFalse(left["real_scheduling"])
        self.assertFalse(left["real_monitoring"])
        self.assertFalse(left["notification_automation"])
        self.assertFalse(left["reminder_automation"])
        self.assertFalse(left["recommendation_generated"])
        self.assertFalse(left["prescription_generated"])
        self.assertFalse(left["claim_effectiveness"])

    def test_mock_intervention_ledger_is_local_only_and_non_clinical(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        tag = build_intervention_tag(workflow)
        profile = build_personal_profile(workflow)
        graph = build_baseline_graph(profile, workflow)
        comparison = compare_feature_set_to_baseline(self._feature_set(), graph).to_dict()
        context = build_intervention_context(
            workflow=workflow,
            tag=tag,
            sensor_feature_set_payload=self._feature_set(),
            baseline_comparison_payload=comparison,
            personal_profile_payload=profile.to_dict(),
            baseline_graph_payload=graph.to_dict(),
            artifact_hashes={},
        )
        plan = build_response_evaluation_plan(workflow, tag, context, comparison)
        ledger = build_mock_intervention_ledger(workflow, tag, context, plan).to_dict()

        self.assertEqual(ledger["id"], "mock-intervention-ledger-placeholder")
        self.assertEqual(ledger["entries"][0]["intervention_tag_id"], tag.id)
        self.assertFalse(ledger["real_intervention_performed"])
        self.assertFalse(ledger["database_access"])
        self.assertFalse(ledger["external_memory"])
        self.assertFalse(ledger["medical_advice"])

    def test_intervention_scaffold_adds_no_network_hardware_or_database_imports(self):
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
        path = REPO_ROOT / "somatic" / "memory" / "intervention.py"
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
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
