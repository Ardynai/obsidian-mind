import copy
import json
import unittest

from somatic.evidence.document_adapter import document_fixture_adapter_status
from somatic.safety.adapter_readiness import REAL_MODE_REQUIRED_GATES
from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_DOCUMENT_REQUIRED_CONTRACTS,
    PHASE11_REAL_MODE_CONTRACT_SPEC_KIND,
    PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
    PHASE11_REAL_MODE_CONTRACT_STATUS,
    PHASE11_RF_BOOTH_REQUIRED_CONTRACTS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_contract_status_summary,
    phase11_document_ingestion_contract_spec,
    phase11_real_mode_contract_bundle,
    phase11_wifi_csi_rf_booth_contract_spec,
    validate_phase11_contract_spec,
)
from somatic.sensors.csi_adapter import wifi_csi_source_adapter_status

FORBIDDEN_SPEC_TERMS = (
    "document-parsed.json",
    "document-mixed.json",
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "fixture://",
    "fixtures/",
    "https://",
    "http://",
    "example.invalid",
    "c:/",
    "source_id",
    "source_ids",
    "device_id",
    "device_ids",
    "router_id",
    "api_key",
    "access_token",
    "secret_value",
    "authorization",
    "password",
    "raw_document_text",
    "raw_csi",
    "raw_rf",
    "raw_values",
    "model_body",
    "model weights",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase11AContractSpecPlanningSurfaceTests(unittest.TestCase):
    def test_document_ingestion_spec_is_contract_only(self):
        spec = phase11_document_ingestion_contract_spec()
        result = validate_phase11_contract_spec(spec)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(spec["contract_spec_version"], PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION)
        self.assertEqual(spec["contract_spec_kind"], PHASE11_REAL_MODE_CONTRACT_SPEC_KIND)
        self.assertEqual(spec["domain"], PHASE11_DOCUMENT_DOMAIN)
        self.assertEqual(spec["status"], PHASE11_REAL_MODE_CONTRACT_STATUS)
        self.assertEqual(spec["required_contracts"], list(PHASE11_DOCUMENT_REQUIRED_CONTRACTS))
        self.assertTrue(spec["planning_only"])
        self.assertTrue(spec["metadata_only"])
        self.assertEqual(spec["runtime_stage"], "not-implemented")
        self.assertFalse(spec["execution_permitted"])
        self.assertFalse(spec["real_mode_runtime_enabled"])
        self.assertEqual(spec["readiness_gate"]["status"], "blocked-fixture-reference-only")
        self.assertEqual(spec["readiness_gate"]["missing_gates"], list(REAL_MODE_REQUIRED_GATES))

        flags = spec["closed_runtime_flags"]
        for flag in (
            "document_ingestion",
            "file_crawling",
            "pdf_parsing",
            "network_calls",
            "body_export",
            "origin_identifier_export",
            "local_name_export",
            "path_export",
            "url_export",
            "provider_detail_export",
            "parser_execution",
            "runtime_execution",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(flags[flag])
        self._assert_no_private_values(spec)

    def test_rf_booth_spec_is_contract_only(self):
        spec = phase11_wifi_csi_rf_booth_contract_spec()
        result = validate_phase11_contract_spec(spec)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(spec["domain"], PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        self.assertEqual(spec["required_contracts"], list(PHASE11_RF_BOOTH_REQUIRED_CONTRACTS))
        self.assertEqual(spec["runtime_stage"], "not-implemented")
        self.assertFalse(spec["execution_permitted"])
        self.assertFalse(spec["real_mode_runtime_enabled"])
        topology = spec["booth_hardware_topology_metadata_contract"]
        self.assertEqual(topology["booth_size_class"], "small-controlled-booth")
        self.assertEqual(topology["subject_scope"], "single-intended-subject")
        self.assertEqual(topology["fixed_ap_role"], "role-metadata-only")
        self.assertEqual(topology["receiver_role_count_range"], "four-to-six")
        self.assertTrue(topology["empty_booth_baseline_concept"])
        self.assertTrue(topology["booth_role_metadata_only"])
        self.assertFalse(topology["topology_claim"])

        flags = spec["closed_runtime_flags"]
        for flag in (
            "hardware_access",
            "capture_execution",
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
            "rf_signal_export",
            "data_export",
            "runtime_execution",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(flags[flag])
        self._assert_no_private_values(spec)

    def test_review_complete_specs_still_do_not_enable_runtime(self):
        review_record = {
            "consent": True,
            "license_review": True,
            "privacy_review": True,
            "hardware_review": True,
            "model_artifact_review": True,
            "dependency_review": True,
            "network_policy_review": True,
        }

        for spec in (
            phase11_document_ingestion_contract_spec(review_record),
            phase11_wifi_csi_rf_booth_contract_spec(review_record),
        ):
            with self.subTest(domain=spec["domain"]):
                self.assertTrue(validate_phase11_contract_spec(spec).compatible)
                self.assertTrue(spec["readiness_gate"]["ready"])
                self.assertEqual(spec["readiness_gate"]["missing_gate_count"], 0)
                self.assertFalse(spec["readiness_gate"]["execution_permitted"])
                self.assertFalse(spec["readiness_gate"]["real_mode_runtime_enabled"])
                self.assertFalse(spec["execution_permitted"])
                self.assertFalse(spec["real_mode_runtime_enabled"])

    def test_unknown_and_private_spec_fields_fail_closed_without_echo(self):
        spec = copy.deepcopy(phase11_wifi_csi_rf_booth_contract_spec())
        spec["extra_metadata"] = "public-looking but outside contract"
        spec["source_id"] = "private-source"
        spec["device_id"] = "device-secret"
        spec["remote_url"] = "https://example.invalid/private"
        spec["model_body"] = {"raw_values": [1, 2, 3]}
        spec["closed_runtime_flags"]["packet_capture"] = True

        result = validate_phase11_contract_spec(spec)
        combined = json.dumps((result.to_dict(), result.sanitized_spec), sort_keys=True).lower()

        self.assertFalse(result.compatible)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("phase11_contract_unknown_field", result.errors)
        self.assertIn("phase11_contract_privacy_boundary", result.errors)
        self.assertIn("phase11_contract_closed_flag_not_preserved", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self.assertEqual(result.sanitized_spec["status"], "rejected-fail-closed")
        for forbidden in (
            "private-source",
            "device-secret",
            "https://example.invalid",
            "raw_values",
            "extra_metadata",
            "model_body",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)

    def test_compact_adapter_status_is_safe_for_public_surfaces(self):
        for status in (
            document_fixture_adapter_status(),
            wifi_csi_source_adapter_status(),
        ):
            with self.subTest(adapter=status["adapter_kind"]):
                phase11 = status["p11a_contract_status"]
                self.assertEqual(phase11["contract_spec_version"], 1)
                self.assertEqual(phase11["status"], PHASE11_REAL_MODE_CONTRACT_STATUS)
                self.assertTrue(phase11["planning_only"])
                self.assertTrue(phase11["metadata_only"])
                self.assertEqual(phase11["runtime_stage"], "not-implemented")
                self.assertEqual(phase11["readiness_gate_status"], "blocked-fixture-reference-only")
                self.assertEqual(phase11["readiness_gate_missing_count"], 7)
                self.assertFalse(phase11["execution_permitted"])
                self.assertFalse(phase11["real_mode_runtime_enabled"])
                self.assertIn("p11a-contract-spec-only", status["capability_labels"])
                self.assertIn("real-mode-planning-only", status["capability_labels"])
                self.assertIn("no-runtime-enable", status["capability_labels"])
                self._assert_no_private_values(phase11)

    def test_contract_bundle_is_planning_only(self):
        bundle = phase11_real_mode_contract_bundle()
        self.assertEqual(bundle["contract_spec_version"], 1)
        self.assertEqual(bundle["contract_spec_kind"], PHASE11_REAL_MODE_CONTRACT_SPEC_KIND)
        self.assertTrue(bundle["planning_only"])
        self.assertTrue(bundle["metadata_only"])
        self.assertFalse(bundle["execution_permitted"])
        self.assertFalse(bundle["real_mode_runtime_enabled"])
        self.assertTrue(validate_phase11_contract_spec(bundle["document_contract_spec"]).compatible)
        self.assertTrue(validate_phase11_contract_spec(bundle["rf_booth_contract_spec"]).compatible)

    def test_status_summary_never_converts_gate_review_to_runtime(self):
        document_spec = phase11_document_ingestion_contract_spec(
            {gate.replace("-", "_"): True for gate in REAL_MODE_REQUIRED_GATES}
        )
        summary = phase11_contract_status_summary(
            domain=PHASE11_DOCUMENT_DOMAIN,
            readiness_gate=document_spec["readiness_gate"],
        )

        self.assertEqual(summary["readiness_gate_missing_count"], 0)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self._assert_no_private_values(summary)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in FORBIDDEN_SPEC_TERMS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
