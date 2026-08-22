import ast
import importlib
import json
import unittest
from pathlib import Path

from somatic.sensors.csi import (
    CSI_FAKE_FEATURES,
    build_csi_capture_plan,
    build_csi_feature_plan,
    build_csi_feature_set,
    build_csi_reference_inventory,
)
from somatic.sensors.csi_adapter import (
    fixture_csi_source_adapter_output,
    validate_csi_source_adapter_output,
    wifi_csi_source_adapter_status,
)
from somatic.sensors.csi_formats import CSI_PARSER_CAPABILITIES
from somatic.workflow_loader import load_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
CSI_FIXTURE_DIR = REPO_ROOT / "fixtures" / "sensors" / "csi"


class WifiCsiScaffoldTests(unittest.TestCase):
    def test_csi_module_imports_without_optional_dependencies(self):
        module = importlib.import_module("somatic.sensors.csi")

        self.assertTrue(hasattr(module, "CsiCapturePlan"))
        self.assertTrue(hasattr(module, "CsiFeatureSet"))
        self.assertTrue(hasattr(module, "build_csi_feature_set"))
        adapter_module = importlib.import_module("somatic.sensors.csi_adapter")
        self.assertTrue(hasattr(adapter_module, "validate_csi_source_adapter_output"))

    def test_fake_csi_feature_set_is_deterministic_and_disabled(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        left_capture = build_csi_capture_plan(workflow)
        right_capture = build_csi_capture_plan(workflow)
        left_plan = build_csi_feature_plan(left_capture)
        right_plan = build_csi_feature_plan(right_capture)
        left = build_csi_feature_set(left_capture, left_plan)
        right = build_csi_feature_set(right_capture, right_plan)

        self.assertEqual(left_capture.to_dict(), right_capture.to_dict())
        self.assertEqual(left_plan.to_dict(), right_plan.to_dict())
        self.assertEqual(left.to_dict(), right.to_dict())
        self.assertEqual(left.features, CSI_FAKE_FEATURES)
        self.assertEqual(left.features["respiratory_rate"], 14)
        self.assertEqual(left.features["motion_score"], 0.18)
        self.assertEqual(left.features["confidence"], "not-applicable")
        self.assertFalse(left.hardware_access)
        self.assertFalse(left.packet_capture)
        self.assertFalse(left.wifi_network_probing)
        self.assertFalse(left.monitor_mode)
        self.assertFalse(left.network_calls)
        self.assertFalse(left.raw_rf_data_collected)
        self.assertFalse(left.raw_csi_data_collected)
        self.assertFalse(left.clinical_interpretation)

    def test_csi_fixtures_parse_and_preserve_boundaries(self):
        fixture_names = (
            "csi-capture-plan-placeholder.json",
            "csi-feature-set-placeholder.json",
            "csi-hardware-profile-placeholder.json",
            "csi-privacy-boundary-placeholder.json",
        )
        for fixture_name in fixture_names:
            with self.subTest(fixture_name=fixture_name):
                payload = self._read_json(CSI_FIXTURE_DIR / fixture_name)
                self.assertEqual(payload["schema_version"], 1)
                self.assertTrue(payload["mock"])
                self.assertTrue(payload["offline"])
                self.assertTrue(payload["research_only"])

        capture_plan = self._read_json(CSI_FIXTURE_DIR / "csi-capture-plan-placeholder.json")
        feature_set = self._read_json(CSI_FIXTURE_DIR / "csi-feature-set-placeholder.json")
        hardware = self._read_json(CSI_FIXTURE_DIR / "csi-hardware-profile-placeholder.json")
        privacy = self._read_json(CSI_FIXTURE_DIR / "csi-privacy-boundary-placeholder.json")

        for payload in (capture_plan, feature_set, hardware):
            self.assertFalse(payload["hardware_access"])
            self.assertFalse(payload["packet_capture"])
            self.assertFalse(payload["wifi_network_probing"])
            self.assertFalse(payload["monitor_mode"])
        self.assertFalse(capture_plan["network_calls"])
        self.assertFalse(feature_set["network_calls"])
        self.assertFalse(feature_set["raw_rf_data_collected"])
        self.assertFalse(feature_set["raw_csi_data_collected"])
        self.assertFalse(feature_set["clinical_interpretation"])
        self.assertEqual(feature_set["features"], CSI_FAKE_FEATURES)
        self.assertFalse(privacy["raw_rf_data_leaves_machine"])
        self.assertFalse(privacy["raw_csi_data_leaves_machine"])
        self.assertFalse(privacy["export_allowed"])
        self.assertFalse(privacy["clinical_interpretation_allowed"])

    def test_reference_inventory_helper_records_phase8a_staging_and_ruview_reassessment(self):
        fixture_inventory = self._read_json(CSI_FIXTURE_DIR / "csi-reference-inventory.json")
        helper_inventory = build_csi_reference_inventory()

        self.assertEqual(helper_inventory, fixture_inventory)
        self.assertEqual(fixture_inventory["phase"], "8A")
        self.assertEqual(
            CSI_PARSER_CAPABILITIES["parser_id"],
            "somatic-csi-fixture-parser-v1",
        )
        self.assertEqual(helper_inventory["phase"], fixture_inventory["phase"])
        self.assertTrue(fixture_inventory["policy"]["no_runtime_execution"])
        self.assertTrue(helper_inventory["policy"]["no_runtime_execution"])
        by_repo = {item["repo"]: item for item in fixture_inventory["references"]}
        for ref in (
            "NTUMARS/Awesome-WiFi-CSI-Sensing",
            "thu4n/ESP32-WiFi-Sensing",
            "MaliosDark/wifi-3d-fusion",
        ):
            self.assertEqual(by_repo[ref]["status"], "staged_reference")
            self.assertRegex(by_repo[ref]["commit"], r"^[0-9a-f]{40}$")
            self.assertTrue(by_repo[ref]["local_path"])
            self.assertTrue(by_repo[ref]["no_runtime_execution"])
            self.assertTrue(by_repo[ref]["no_hardware_access"])
            self.assertTrue(by_repo[ref]["no_dependency_install"])
            self.assertTrue(by_repo[ref]["no_source_vendoring"])

        ruview = by_repo["ruvnet/RuView"]
        self.assertEqual(ruview["status"], "conditional-reference-only")
        self.assertTrue(ruview["reference_only"])
        self.assertTrue(ruview["reassessable"])
        self.assertTrue(ruview["no_runtime_execution"])
        self.assertTrue(ruview["no_source_vendoring"])
        self.assertFalse(ruview["v2_reassessment"]["downstream_accuracy_validated"])
        self.assertFalse(ruview["v2_reassessment"]["deployment_claims_verified"])

        adapter_status = wifi_csi_source_adapter_status()
        adapter_validation = validate_csi_source_adapter_output(fixture_csi_source_adapter_output())
        self.assertEqual(adapter_status["adapter_kind"], "metadata-wifi-csi-source-adapter")
        self.assertEqual(adapter_validation.classification, "compatible")
        self.assertEqual(
            fixture_inventory["booth_first_planning_profile"]["profile"],
            "booth-first-single-subject-v1",
        )

    def test_wifi_csi_workflow_fixture_is_planning_only(self):
        workflow = load_workflow(
            REPO_ROOT / "fixtures" / "workflows" / "valid-wifi-csi-observation.yaml"
        )
        provider_fixture = self._read_json(
            REPO_ROOT / "fixtures" / "providers" / "mock-sensor-provider.json"
        )
        sensor_provider = next(
            provider for provider in workflow["providers"] if provider["class"] == "sensor"
        )
        constraints = sensor_provider["constraints"]

        self.assertEqual(workflow["mode"], "wifi-csi-observation")
        self.assertIn("wifi-csi.plan", sensor_provider["capabilities"])
        self.assertIn("wifi-csi.summarize", sensor_provider["capabilities"])
        self.assertTrue(constraints["offline_required"])
        self.assertTrue(constraints["mock_only"])
        self.assertTrue(constraints["fake_backed"])
        self.assertFalse(constraints["allow_live_capture"])
        self.assertFalse(constraints["allow_wifi_csi_capture"])
        self.assertFalse(constraints["allow_packet_capture"])
        self.assertFalse(constraints["allow_wifi_network_probing"])
        self.assertFalse(constraints["allow_monitor_mode"])
        self.assertFalse(constraints["allow_driver_access"])
        self.assertFalse(constraints["allow_raw_rf_collection"])
        self.assertFalse(constraints["allow_raw_rf_export"])
        self.assertFalse(constraints["allow_raw_csi_collection"])
        self.assertFalse(constraints["allow_raw_csi_export"])
        self.assertFalse(constraints["allow_hardware_access"])
        self.assertFalse(constraints["allow_network_calls"])
        self.assertIn(
            "csi-planning-placeholder", workflow["evidence_requirements"]["accepted_source_types"]
        )
        self.assertIn("csi-planning-placeholder", provider_fixture["evidence_emitted"])
        self.assertNotIn("csi-stream", provider_fixture["evidence_emitted"])

    def test_wifi_csi_docs_state_boundaries(self):
        required_phrases = (
            "fake-backed",
            "disabled by default",
            "does not access wifi hardware",
            "no esp32",
            "rtl8812au",
            "monitor mode",
            "packet capture",
            "local fake/sample fixtures only",
            "no serial",
            "no mqtt",
            "no udp",
            "no vital-sign inference",
            "wifi device probing",
            "raw rf/csi data is local-first and private by default",
            "clinical interpretation",
            "ruview",
            "conditional reference-only",
            "booth-first",
            "single-subject",
            "esp32-s3",
            "empty-booth baseline",
        )
        doc_paths = (
            REPO_ROOT / "docs" / "wifi-csi-scaffold.md",
            REPO_ROOT / "docs" / "wifi-csi-data-formats.md",
            REPO_ROOT / "docs" / "wifi-csi-parser.md",
            REPO_ROOT / "docs" / "wifi-csi-source-staging.md",
            REPO_ROOT / "docs" / "wifi-csi-reference-map.md",
            REPO_ROOT / "docs" / "sensor-provider-boundary.md",
            REPO_ROOT / "docs" / "sensor-privacy-boundary.md",
            REPO_ROOT / "docs" / "n-of-1-workflow.md",
        )
        combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in doc_paths)
        for phrase in required_phrases:
            self.assertIn(phrase, combined)
        for path in doc_paths:
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=path.name):
                self.assertIn("wifi csi", text)

    def test_csi_scaffold_adds_no_network_hardware_or_optional_import_surfaces(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
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
            "neurokit2",
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
            "open",
            "scan",
            "connect",
            "download",
        }
        for path in (
            REPO_ROOT / "somatic" / "sensors" / "csi.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_adapter.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_formats.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_parser.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_scoring.py",
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


if __name__ == "__main__":
    unittest.main()
