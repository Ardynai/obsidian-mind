import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = REPO_ROOT / "fixtures" / "sensors" / "csi" / "csi-reference-inventory.json"


class WifiCsiReferenceInventoryTests(unittest.TestCase):
    def test_inventory_parses_and_includes_each_target_repo(self):
        inventory = self._read_inventory()

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["phase"], "8A")
        self.assertEqual(
            inventory["staging_root"],
            "C:\\AI\\external-sources\\somatic\\wifi-csi",
        )
        self.assertTrue(inventory["source_staging_git_clone_performed"])
        self.assertTrue(inventory["does_not_require_external_repos_in_ci"])

        by_repo = {entry["repo"]: entry for entry in inventory["references"]}
        self.assertEqual(
            set(by_repo),
            {
                "NTUMARS/Awesome-WiFi-CSI-Sensing",
                "thu4n/ESP32-WiFi-Sensing",
                "MaliosDark/wifi-3d-fusion",
                "ruvnet/RuView",
            },
        )

    def test_staged_entries_include_path_commit_license_and_safe_use_notes(self):
        inventory = self._read_inventory()

        for entry in inventory["references"]:
            if entry["status"] != "staged_reference":
                continue
            with self.subTest(repo=entry["repo"]):
                self.assertTrue(entry["local_path"])
                self.assertTrue(entry["remote_url"].startswith("https://github.com/"))
                self.assertRegex(entry["commit"], r"^[0-9a-f]{40}$")
                self.assertIn("license", entry)
                self.assertIn("identifier", entry["license"])
                self.assertTrue(entry["purpose"])
                self.assertGreaterEqual(len(entry["hardware_assumptions"]), 1)
                self.assertGreaterEqual(len(entry["supported_capture_path"]), 1)
                self.assertGreaterEqual(len(entry["data_formats"]), 1)
                self.assertGreaterEqual(len(entry["dependencies"]), 1)
                self.assertGreaterEqual(len(entry["useful_method_ideas"]), 1)
                self.assertGreaterEqual(len(entry["somatic_should_not_adopt"]), 1)
                self.assertGreaterEqual(len(entry["privacy_security_cautions"]), 1)
                self.assertTrue(entry["no_runtime_execution"])
                self.assertTrue(entry["no_hardware_access"])
                self.assertTrue(entry["no_dependency_install"])
                self.assertTrue(entry["no_source_vendoring"])
                self.assertIsNone(entry["failure_reason"])

    def test_license_caveats_are_explicit(self):
        inventory = self._read_inventory()
        by_repo = {entry["repo"]: entry for entry in inventory["references"]}

        self.assertEqual(
            by_repo["NTUMARS/Awesome-WiFi-CSI-Sensing"]["license"]["identifier"],
            "MIT",
        )
        self.assertEqual(
            by_repo["thu4n/ESP32-WiFi-Sensing"]["license"]["identifier"],
            "license-unclear",
        )
        self.assertIn(
            "Nested esp32-csi-tool/LICENSE is MIT",
            by_repo["thu4n/ESP32-WiFi-Sensing"]["license"]["notes"],
        )
        self.assertEqual(
            by_repo["MaliosDark/wifi-3d-fusion"]["license"]["identifier"],
            "requires-review",
        )
        self.assertIn(
            "README badge says GPL-2.0",
            by_repo["MaliosDark/wifi-3d-fusion"]["license"]["notes"],
        )

    def test_ruview_entry_is_conditional_reference_only_and_not_staged(self):
        inventory = self._read_inventory()
        by_repo = {entry["repo"]: entry for entry in inventory["references"]}
        ruview = by_repo["ruvnet/RuView"]

        self.assertEqual(ruview["status"], "conditional-reference-only")
        self.assertIsNone(ruview["local_path"])
        self.assertIsNone(ruview["commit"])
        self.assertNotIn("remote_url", ruview)
        self.assertIsNone(ruview["failure_reason"])
        self.assertTrue(ruview["reference_only"])
        self.assertTrue(ruview["reassessable"])
        self.assertIn("Do not use as an implementation source.", ruview["somatic_should_not_adopt"])
        self.assertIn("earlier-overclaims", ruview["warning_history"])
        self.assertIn("incompatible-model-loading-concerns", ruview["warning_history"])
        self.assertIn("unverified-deployment-claims", ruview["warning_history"])
        self.assertTrue(ruview["v2_reassessment"]["rust_workspace_reported"])
        self.assertTrue(ruview["v2_reassessment"]["wifi_densepose_crates_reported"])
        self.assertTrue(ruview["v2_reassessment"]["temporal_embedding_metric_reported"])
        self.assertFalse(ruview["v2_reassessment"]["downstream_accuracy_validated"])
        self.assertFalse(ruview["v2_reassessment"]["deployment_claims_verified"])
        self.assertTrue(ruview["no_runtime_execution"])
        self.assertTrue(ruview["no_hardware_access"])
        self.assertTrue(ruview["no_dependency_install"])
        self.assertTrue(ruview["no_source_vendoring"])

    def test_booth_first_source_adapter_boundary_is_metadata_only(self):
        inventory = self._read_inventory()
        adapter = inventory["source_adapter_boundary"]
        booth = inventory["booth_first_planning_profile"]

        self.assertEqual(adapter["adapter_kind"], "metadata-wifi-csi-source-adapter")
        self.assertEqual(adapter["adapter_contract_version"], 1)
        self.assertTrue(adapter["metadata_only"])
        self.assertTrue(adapter["reference_only"])
        self.assertTrue(adapter["offline"])
        self.assertTrue(adapter["fixture_backed"])
        for flag in (
            "hardware_access",
            "packet_capture",
            "monitor_mode",
            "wifi_network_probing",
            "network_calls",
            "esp32_flashing",
            "router_ap_control",
            "mqtt_udp_listener",
            "smart_home_bridge",
            "model_download",
            "model_execution",
            "vitals_inference",
            "diagnosis",
            "treatment",
            "emergency_triage",
            "medical_or_clinical_claim",
            "raw_signal_export",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(adapter[flag])

        self.assertEqual(booth["profile"], "booth-first-single-subject-v1")
        self.assertTrue(booth["single_subject"])
        self.assertEqual(booth["space"], "small-controlled-booth")
        self.assertEqual(booth["future_topology"], "fixed-ap-plus-4-to-6-receiver-nodes")
        self.assertEqual(booth["preferred_radio_family"], "esp32-s3")
        self.assertEqual(booth["empty_booth_baseline"], "planned-reference-concept")
        self.assertEqual(booth["room_adaptation_logic"], "skipped")
        self.assertIn("phase-variance", booth["research_note_labels"])
        self.assertIn("conjugation", booth["research_note_labels"])
        self.assertIn("temporal-embedding", booth["research_note_labels"])

    def test_inventory_policy_records_no_runtime_or_hardware_actions(self):
        inventory = self._read_inventory()
        policy = inventory["policy"]
        sensitive = set(inventory["sensitive_data_classes"])

        for flag in (
            "read_only_source_inspection",
            "git_clone_or_fetch_only",
            "no_runtime_execution",
            "no_hardware_access",
            "no_dependency_install",
            "no_package_managers_run",
            "no_wifi_adapter_access",
            "no_packet_capture",
            "no_monitor_mode",
            "no_serial_capture",
            "no_sd_card_read_write",
            "no_mqtt_or_udp_listener",
            "no_esp32_or_router_tools",
            "no_model_download",
            "no_model_execution",
            "no_home_automation_bridge",
            "no_vitals_inference",
            "no_external_apis_except_git_clone_fetch",
            "no_source_vendoring",
            "no_medical_or_clinical_claims",
        ):
            with self.subTest(flag=flag):
                self.assertTrue(policy[flag])

        self.assertIn("pcap", sensitive)
        self.assertIn("ReID sequences", sensitive)
        self.assertIn("pose outputs", sensitive)
        self.assertIn("all potentially affected people", inventory["future_real_mode_consent"])

    def test_inventory_does_not_require_external_repos_for_ci(self):
        inventory = self._read_inventory()

        for entry in inventory["references"]:
            with self.subTest(repo=entry["repo"]):
                self.assertIn("local_path", entry)
                self.assertNotIn("external_package_imported", entry)
                self.assertNotIn("import_check", entry)
                # CI validates recorded metadata only; it must not stat the staged path.
                self.assertIsInstance(entry["local_path"], (str, type(None)))

    def test_existing_workflow_modes_still_run_in_temp_output(self):
        workflow_names = (
            "valid-literature-only.yaml",
            "valid-hypothesis-tournament.yaml",
            "valid-robin-loop.yaml",
            "valid-in-silico-screening.yaml",
            "valid-n-of-1.yaml",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output_root = Path(tmpdir)
            for workflow_name in workflow_names:
                with self.subTest(workflow=workflow_name):
                    run_dir = run_mock_workflow(
                        REPO_ROOT / "fixtures" / "workflows" / workflow_name,
                        repo_root=REPO_ROOT,
                        output_root=output_root,
                        run_id=f"test-phase8a-{workflow_name.removesuffix('.yaml')}",
                    )
                    self.assertTrue((run_dir / "manifest.json").exists())

    def test_fabric_signed_pack_check_still_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "somatic",
                "fabric",
                "check",
                "fixtures/fabric/crypto/signed-code-pack.json",
                "--keyring",
                "fixtures/fabric/crypto/keyring-signed.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        output = result.stdout + result.stderr
        expected = 0 if CRYPTO_AVAILABLE else 1
        self.assertEqual(result.returncode, expected, output)
        if CRYPTO_AVAILABLE:
            self.assertIn("Fabric check: valid signed-code-pack.json", result.stdout)
            self.assertIn("crypto: publisher threshold verified", result.stdout)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())
            self.assertIn("failing closed", output.lower())
            self.assertIn("optional fabric extra", output.lower())

    @staticmethod
    def _read_inventory():
        return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
