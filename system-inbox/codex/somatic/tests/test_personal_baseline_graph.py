import ast
import json
import unittest
from pathlib import Path

from somatic.memory.baseline import (
    BASELINE_CATEGORIES,
    INSUFFICIENT_DATA,
    OUTSIDE_BASELINE,
    WITHIN_BASELINE,
    BaselinePrivacyBoundary,
    build_baseline_graph,
    build_personal_profile,
    compare_feature_set_to_baseline,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_FIXTURE_DIR = REPO_ROOT / "fixtures" / "baseline"


class PersonalBaselineGraphTests(unittest.TestCase):
    def test_baseline_modules_import_without_optional_dependencies(self):
        import somatic.memory.baseline
        import somatic.memory.profile

        self.assertEqual(somatic.memory.baseline.BASELINE_CATEGORIES, BASELINE_CATEGORIES)
        self.assertTrue(somatic.memory.profile.build_personal_profile({"id": "x"}).mock)

    def test_baseline_fixtures_parse_and_keep_privacy_flags_closed(self):
        for filename in (
            "personal-profile-placeholder.json",
            "baseline-privacy-boundary-placeholder.json",
            "baseline-graph-placeholder.json",
            "baseline-comparison-placeholder.json",
        ):
            with self.subTest(filename=filename):
                payload = self._read_json(BASELINE_FIXTURE_DIR / filename)
                self.assertEqual(payload["schema_version"], 1)
                self.assertTrue(payload["mock"])
                self.assertTrue(payload["offline"])
                self.assertTrue(payload["research_only"])
                self.assertTrue(payload["sandbox_only"])
                self.assertTrue(payload["fake_backed"])
                self.assertFalse(payload["real_health_data_loaded"])
                self.assertFalse(payload["real_profile_storage"])
                self.assertFalse(payload["personal_data_exported"])
                self.assertFalse(payload["network_calls"])
                self.assertFalse(payload["database_access"])
                self.assertFalse(payload["diagnosis"])
                self.assertFalse(payload["treatment_recommendation"])
                self.assertFalse(payload["emergency_triage"])
                self.assertFalse(payload["real_monitoring"])
                self.assertFalse(payload["clinical_interpretation"])

    def test_builds_placeholder_profile_and_graph_categories(self):
        workflow = {"id": "valid-n-of-1"}
        profile = build_personal_profile(workflow)
        graph = build_baseline_graph(profile, workflow)

        self.assertEqual(profile.id, "personal-profile-placeholder")
        self.assertEqual(graph.profile_id, profile.id)
        self.assertEqual(graph.categories, BASELINE_CATEGORIES)
        self.assertEqual([metric.category for metric in graph.metrics], list(BASELINE_CATEGORIES))
        self.assertIsInstance(graph.privacy_boundary, BaselinePrivacyBoundary)
        self.assertFalse(graph.privacy_boundary.real_health_data_loaded)
        self.assertFalse(graph.privacy_boundary.database_access)

    def test_baseline_comparison_is_deterministic_with_all_statuses(self):
        workflow = {"id": "valid-n-of-1"}
        profile = build_personal_profile(workflow)
        graph = build_baseline_graph(profile, workflow)

        left = compare_feature_set_to_baseline(self._feature_set(), graph).to_dict()
        right = compare_feature_set_to_baseline(self._feature_set(), graph).to_dict()

        self.assertEqual(left, right)
        self.assertEqual(left["comparison_status"], OUTSIDE_BASELINE)
        self.assertEqual(
            left["status_counts"],
            {
                WITHIN_BASELINE: 5,
                OUTSIDE_BASELINE: 1,
                INSUFFICIENT_DATA: 1,
            },
        )
        by_category = {result["category"]: result for result in left["results"]}
        self.assertEqual(by_category["respiratory_rate"]["status"], WITHIN_BASELINE)
        self.assertEqual(by_category["movement_score"]["status"], OUTSIDE_BASELINE)
        self.assertEqual(by_category["notes_placeholder"]["status"], INSUFFICIENT_DATA)
        self.assertEqual(by_category["movement_score"]["deviation"], 0.03)

    def test_inside_outside_and_insufficient_are_mechanical_only(self):
        workflow = {"id": "valid-n-of-1"}
        profile = build_personal_profile(workflow)
        graph = build_baseline_graph(profile, workflow)

        inside_feature_set = self._feature_set(movement_score=0.1)
        inside = compare_feature_set_to_baseline(inside_feature_set, graph).to_dict()
        inside_by_category = {result["category"]: result for result in inside["results"]}
        self.assertEqual(inside_by_category["movement_score"]["status"], WITHIN_BASELINE)
        self.assertEqual(inside["comparison_status"], INSUFFICIENT_DATA)

        outside_feature_set = self._feature_set(respiratory_rate=22)
        outside = compare_feature_set_to_baseline(outside_feature_set, graph).to_dict()
        outside_by_category = {result["category"]: result for result in outside["results"]}
        self.assertEqual(outside_by_category["respiratory_rate"]["status"], OUTSIDE_BASELINE)

        missing = self._feature_set()
        missing["features"].pop("respiratory_rate")
        insufficient = compare_feature_set_to_baseline(missing, graph).to_dict()
        insufficient_by_category = {
            result["category"]: result for result in insufficient["results"]
        }
        self.assertEqual(
            insufficient_by_category["respiratory_rate"]["status"],
            INSUFFICIENT_DATA,
        )
        for result in insufficient["results"]:
            note = result["deviation_note"].lower()
            self.assertNotIn("abnormal", note)
            self.assertNotIn("condition", note)
            self.assertNotIn("treat", note)
            self.assertNotIn("diagnos", note)

    def test_baseline_scaffold_adds_no_network_hardware_or_database_imports(self):
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
        }
        for path in (
            REPO_ROOT / "somatic" / "memory" / "baseline.py",
            REPO_ROOT / "somatic" / "memory" / "profile.py",
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
    def _feature_set(**overrides):
        features = {
            "respiratory_rate": overrides.get("respiratory_rate", 14),
            "movement_score": overrides.get("movement_score", 0.18),
            "posture_state": "upright-placeholder",
            "sleep_state_estimate": "awake-placeholder",
            "environmental_context_placeholder": "room-context-placeholder",
        }
        return {
            "schema_version": 1,
            "id": "sensor-feature-set-n-of-1-sandbox",
            "features": features,
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
