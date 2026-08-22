import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12E_AUTHORIZATION_STATUS,
    PHASE12E_GRANT_STATUS,
    PHASE12E_NON_DIAGNOSTIC_BOUNDARIES,
    PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION,
    PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
    PHASE12E_PROFILE_STATUS,
    PHASE12E_REQUIRED_FUTURE_GATES,
    PHASE12E_SENSOR_CAPABILITY_LABELS,
    PHASE12E_SENSOR_PHASE,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12d_visual_desktop_consent_gate_requirements,
    phase12e_physiological_sensor_capability_profile,
    phase12e_physiological_sensor_capability_profile_status_summary,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12d_visual_desktop_consent_gate_requirements,
    validate_phase12e_physiological_sensor_capability_profile,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-12e-physiological-sensor-capability-profile-v1.json"
)
UNSAFE_PHASE12E_SENTINELS = (
    "raw_bia",
    "raw-bia",
    "raw_impedance",
    "raw-impedance",
    "raw_impedance_trace",
    "raw-impedance-trace",
    "raw_ultrasound",
    "raw-ultrasound",
    "raw_acoustic",
    "raw-acoustic",
    "bia_reading",
    "bia-reading",
    "impedance_trace",
    "impedance-trace",
    "ultrasound_payload",
    "ultrasound-payload",
    "acoustic_payload",
    "acoustic-payload",
    "serial_number",
    "serial-number",
    "bluetooth_mac",
    "bluetooth-mac",
    "mac_address",
    "mac-address",
    "fixture://",
    "fixtures/",
    "https://",
    "http://",
    "example.invalid",
    "c:/",
    "source_id",
    "source-id",
    "device_id",
    "device-id",
    "router_id",
    "api_key",
    "access_token",
    "secret_value",
    "password",
    "raw_document_text",
    "raw_csi",
    "raw_rf",
    "raw_screenshot",
    "raw_ocr",
    "model_body",
    "parser_body",
    "provider_body",
    "accepted-for-runtime",
    "execution-permitted",
    "runtime-enabled",
    "permission-granted",
    "authorization-granted",
    "approval-granted",
    "sensor-enabled",
    "measurement-enabled",
    "diagnosis-confirmed",
    "clinical-recommendation-issued",
    "disease-detection-enabled",
    "mri-replacement-claim",
    "ct-replacement-claim",
    "scanner-equivalence-claim",
)


class Phase12EPhysiologicalSensorCapabilityProfileTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12e_physiological_sensor_capability_profile()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["physiological_sensor_profile_contract_version"],
            PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(fixture["profile_kind"], PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND)
        self.assertTrue(
            fixture["physiological_sensor_profile_id"].startswith("p12e-sensor-profile-")
        )
        self.assertEqual(fixture["source_phase_range"], "12A-12B,12D,sensor-evidence")
        self.assertEqual(fixture["sensor_phase"], PHASE12E_SENSOR_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12E_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12E_GRANT_STATUS)
        self.assertEqual(fixture["profile_status"], PHASE12E_PROFILE_STATUS)
        self.assertFalse(fixture["phase12e_profiles_are_approvals_grants_or_permissions"])
        self.assertFalse(fixture["phase12e_satisfies_sensor_gates"])
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            [
                capability["sensor_capability_label"]
                for capability in fixture["sensor_capability_labels"]
            ],
            list(PHASE12E_SENSOR_CAPABILITY_LABELS),
        )
        self.assertEqual(
            [boundary["boundary_id"] for boundary in fixture["non_diagnostic_boundaries"]],
            list(PHASE12E_NON_DIAGNOSTIC_BOUNDARIES),
        )
        self.assertEqual(
            [gate["gate_id"] for gate in fixture["required_future_gates"]],
            list(PHASE12E_REQUIRED_FUTURE_GATES),
        )
        self.assertEqual(fixture["sensor_capability_label_count"], 9)
        self.assertEqual(fixture["non_diagnostic_boundary_count"], 6)
        self.assertEqual(fixture["required_future_gate_count"], 10)
        self.assertEqual(fixture["satisfied_sensor_gate_count"], 0)
        self.assertEqual(fixture["passed_sensor_gate_count"], 0)
        self.assertTrue(fixture["jules_review_required_for_validator_or_authorization_semantics"])
        for capability in fixture["sensor_capability_labels"]:
            with self.subTest(capability=capability["sensor_capability_label"]):
                self.assertEqual(
                    capability["capability_status"],
                    "metadata-only-no-sensor-enabled",
                )
                self.assertTrue(capability["metadata_only"])
                self.assertFalse(capability["sensor_enabled_by_phase12e"])
                self.assertFalse(capability["measurement_permitted"])
                self.assertFalse(capability["execution_permitted"])
                self.assertFalse(capability["real_mode_runtime_enabled"])
        for boundary in fixture["non_diagnostic_boundaries"]:
            with self.subTest(boundary=boundary["boundary_id"]):
                self.assertEqual(
                    boundary["boundary_status"],
                    "non-diagnostic-wellness-trend-metadata-only",
                )
                self.assertTrue(boundary["metadata_only"])
                self.assertFalse(boundary["satisfied_by_phase12e"])
                self.assertFalse(boundary["diagnosis_permitted"])
                self.assertFalse(boundary["clinical_recommendation_permitted"])
                self.assertFalse(boundary["execution_permitted"])
                self.assertFalse(boundary["real_mode_runtime_enabled"])
        for gate in fixture["required_future_gates"]:
            with self.subTest(gate=gate["gate_id"]):
                self.assertEqual(
                    gate["gate_status"],
                    "future-physiological-sensor-gate-required-not-satisfied",
                )
                self.assertTrue(gate["required_before_physiological_sensor_runtime"])
                self.assertTrue(gate["metadata_only"])
                self.assertFalse(gate["satisfied_by_phase12e"])
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["execution_permitted"])
                self.assertFalse(gate["real_mode_runtime_enabled"])
        source_boundaries = fixture["source_sensor_evidence_boundaries"]
        self.assertEqual(source_boundaries["source_phase_range"], "7A-11M")
        self.assertEqual(source_boundaries["boundary_label_count"], 4)
        self.assertFalse(source_boundaries["execution_permitted"])
        result = validate_phase12e_physiological_sensor_capability_profile(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12e_physiological_sensor_capability_profile_status_summary()

        self.assertEqual(summary["source_phase_range"], "12A-12B,12D,sensor-evidence")
        self.assertEqual(summary["sensor_phase"], "capability-profile-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["sensor_capability_label_count"], 9)
        self.assertEqual(summary["non_diagnostic_boundary_count"], 6)
        self.assertEqual(summary["required_future_gate_count"], 10)
        self.assertEqual(summary["satisfied_sensor_gate_count"], 0)
        self.assertEqual(summary["passed_sensor_gate_count"], 0)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self._assert_no_private_values(summary)

    def test_status_words_never_enable_execution(self):
        profile = phase12e_physiological_sensor_capability_profile()
        finalize = (
            phase12_contracts_module._finalize_phase12e_physiological_sensor_capability_profile
        )
        for wording in (
            "connected",
            "measured",
            "scanned",
            "authorized",
            "approved",
            "granted",
            "ready",
            "enabled",
            "configured",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(profile)
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["profile_status"] = wording
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12e_physiological_sensor_capability_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(result.sanitized_record["bia_measurement_execution_granted"])
                self.assertFalse(result.sanitized_record["device_connection_execution_granted"])

    def test_sensor_labels_and_future_gates_are_metadata_only(self):
        profile = phase12e_physiological_sensor_capability_profile()
        finalize = (
            phase12_contracts_module._finalize_phase12e_physiological_sensor_capability_profile
        )
        unsafe = copy.deepcopy(profile)
        unsafe["phase12e_satisfies_sensor_gates"] = True
        unsafe["satisfied_sensor_gate_count"] = 1
        unsafe["passed_sensor_gate_count"] = 1
        unsafe["sensor_capability_labels"][0]["sensor_enabled_by_phase12e"] = True
        unsafe["sensor_capability_labels"][0]["measurement_permitted"] = True
        unsafe["non_diagnostic_boundaries"][0]["satisfied_by_phase12e"] = True
        unsafe["non_diagnostic_boundaries"][1]["diagnosis_permitted"] = True
        unsafe["required_future_gates"][0]["satisfied_by_phase12e"] = True
        unsafe["required_future_gates"][0]["passed"] = True
        unsafe = finalize(unsafe)

        result = validate_phase12e_physiological_sensor_capability_profile(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        safe = result.sanitized_record
        self.assertFalse(safe["phase12e_satisfies_sensor_gates"])
        self.assertEqual(safe["satisfied_sensor_gate_count"], 0)
        self.assertEqual(safe["passed_sensor_gate_count"], 0)
        for capability in safe["sensor_capability_labels"]:
            self.assertFalse(capability["sensor_enabled_by_phase12e"])
            self.assertFalse(capability["measurement_permitted"])
        for boundary in safe["non_diagnostic_boundaries"]:
            self.assertFalse(boundary["satisfied_by_phase12e"])
            self.assertFalse(boundary["diagnosis_permitted"])
        for gate in safe["required_future_gates"]:
            self.assertFalse(gate["satisfied_by_phase12e"])
            self.assertFalse(gate["passed"])

    def test_no_active_authorization_grant_or_sensor_runtime_can_validate(self):
        profile = phase12e_physiological_sensor_capability_profile()
        unsafe = copy.deepcopy(profile)
        unsafe["authorization_status"] = "authorized"
        unsafe["grant_status"] = "granted"
        unsafe["phase12e_profiles_are_approvals_grants_or_permissions"] = True
        for field in self._runtime_flag_fields():
            unsafe[field] = True
        unsafe["execution_permitted"] = True
        unsafe["real_mode_runtime_enabled"] = True
        unsafe["active_grant"] = {
            "status": "permission-granted",
            "runtime_stage": "ready",
        }

        result = validate_phase12e_physiological_sensor_capability_profile(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        self.assertEqual(result.sanitized_record["grant_status"], "no-grant")
        self.assertFalse(
            result.sanitized_record["phase12e_profiles_are_approvals_grants_or_permissions"]
        )
        self.assertNotIn("active_grant", result.sanitized_record)

    def test_validator_fails_closed_for_unsafe_or_contradictory_records(self):
        profile = phase12e_physiological_sensor_capability_profile()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("sensor_capability_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["physiological_sensor_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        authorization = copy.deepcopy(profile)
        authorization["authorization_status"] = "authorization-granted"
        cases.append(("authorization-wording", authorization))

        permission = copy.deepcopy(profile)
        permission["profile_status"] = "runtime-permission-granted"
        cases.append(("permission-wording", permission))

        unsafe_url = copy.deepcopy(profile)
        unsafe_url["source_sensor_evidence_boundaries"]["boundary_status"] = (
            "https://example.invalid/api_key"
        )
        cases.append(("unsafe-url", unsafe_url))

        boolean_count = copy.deepcopy(profile)
        boolean_count["sensor_capability_label_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(profile)
        string_count["required_future_gate_count"] = "10"
        cases.append(("string-count", string_count))

        device_id = copy.deepcopy(profile)
        device_id["source_sensor_evidence_boundaries"]["device_id"] = "private-device"
        cases.append(("device-id", device_id))

        serial = copy.deepcopy(profile)
        serial["source_sensor_evidence_boundaries"]["serial_number"] = "private-serial"
        cases.append(("serial-number", serial))

        bluetooth_mac = copy.deepcopy(profile)
        bluetooth_mac["source_sensor_evidence_boundaries"]["bluetooth_mac"] = "00:11:22:33:44:55"
        cases.append(("bluetooth-mac", bluetooth_mac))

        raw_bia = copy.deepcopy(profile)
        raw_bia["sensor_capability_labels"][0]["sensor_capability_label"] = "raw_bia"
        cases.append(("raw-bia", raw_bia))

        raw_impedance = copy.deepcopy(profile)
        raw_impedance["required_future_gates"][0]["gate_status"] = "raw_impedance_trace"
        cases.append(("raw-impedance", raw_impedance))

        ultrasound_payload = copy.deepcopy(profile)
        ultrasound_payload["source_sensor_evidence_boundaries"]["ultrasound_payload"] = "frame"
        cases.append(("ultrasound-payload", ultrasound_payload))

        acoustic_payload = copy.deepcopy(profile)
        acoustic_payload["source_sensor_evidence_boundaries"]["acoustic_payload"] = "wave"
        cases.append(("acoustic-payload", acoustic_payload))

        clinical_claim = copy.deepcopy(profile)
        clinical_claim["non_diagnostic_boundaries"][0]["boundary_status"] = (
            "clinical-recommendation-issued"
        )
        cases.append(("clinical-claim", clinical_claim))

        replacement_claim = copy.deepcopy(profile)
        replacement_claim["non_diagnostic_boundaries"][0]["boundary_status"] = (
            "mri-replacement-claim"
        )
        cases.append(("replacement-claim", replacement_claim))

        raw_visual = copy.deepcopy(profile)
        raw_visual["source_consent_gate_profile"]["raw_screenshot"] = "pixels"
        cases.append(("raw-visual", raw_visual))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12e_physiological_sensor_capability_profile(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE12E_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_phase11_and_phase12_sources_remain_non_executing(self):
        charter = phase12a_runtime_authorization_design_charter()
        record = phase12b_runtime_authorization_record_candidate()
        consent_profile = phase12d_visual_desktop_consent_gate_requirements()

        charter_result = validate_phase12a_runtime_authorization_design_charter(charter)
        record_result = validate_phase12b_runtime_authorization_record_candidate(record)
        consent_result = validate_phase12d_visual_desktop_consent_gate_requirements(consent_profile)

        self.assertTrue(charter_result.compatible, charter_result.errors)
        self.assertTrue(record_result.compatible, record_result.errors)
        self.assertTrue(consent_result.compatible, consent_result.errors)
        for payload in (charter, record, consent_profile):
            self.assertEqual(payload["runtime_stage"], "not-implemented")
            self.assertFalse(payload["execution_permitted"])
            self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12e_module_does_not_add_runtime_execution_imports(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8")
        lowered = module_text.lower()

        for forbidden in (
            "import bleak",
            "from bleak",
            "import serial",
            "from serial",
            "import bluetooth",
            "from bluetooth",
            "import usb",
            "from usb",
            "pydicom",
            "sounddevice",
            "pyaudio",
            "requests",
            "urllib",
            "socket",
            "subprocess",
            "open(",
            '"execution_permitted": true',
            '"real_mode_runtime_enabled": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)

    def _assert_no_private_values(self, payload):
        encoded = self._safe_encoded(payload)
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE12E_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    @staticmethod
    def _runtime_flag_fields():
        return (
            "bia_measurement_execution_granted",
            "device_connection_execution_granted",
            "bluetooth_execution_granted",
            "usb_execution_granted",
            "cloud_sync_execution_granted",
            "acoustic_processing_execution_granted",
            "ultrasound_processing_execution_granted",
            "medical_inference_execution_granted",
            "clinical_recommendation_execution_granted",
            "network_call_execution_granted",
            "runtime_adapter_execution_granted",
            "adapter_execution_granted",
            "provider_execution_granted",
            "model_execution_granted",
        )

    @staticmethod
    def _safe_encoded(payload):
        return (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace("\\", "/")
            .replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace("runtime_authorization", "runtime_status")
            .replace("physiological_sensor", "phys_sensor")
            .replace("sensor_capability", "sensor_cap")
            .replace("metadata-only-no-sensor-enabled", "metadata-only-no-sensor-en")
            .replace("sensor_enabled", "sensor_en")
            .replace("measurement_permitted", "measurement_perm")
            .replace("bia_measurement", "bia_meta")
            .replace("hand-to-foot-bia-scale", "hand-to-foot-b-scale")
            .replace("hand-to-feet-segmental-bia-scale", "hand-to-feet-seg-b-scale")
            .replace("multi-frequency-bia", "multi-frequency-b")
            .replace("raw_bia", "raw_b")
            .replace("raw-bia", "raw-b")
            .replace("no-diagnosis", "no-dx")
            .replace("diagnosis_permitted", "dx_perm")
            .replace("no-clinical-recommendation", "no-clinical-rec")
            .replace("clinical_recommendation_permitted", "clinical_rec_perm")
            .replace("clinical_recommendation_execution", "clinical_rec_exec")
            .replace("clinical-boundary-disclaimer", "clinical-boundary-note")
            .replace("no-medical-scanner-equivalence-claim", "no-med-scan-eq-claim")
            .replace("medical_inference_execution", "med_inf_exec")
            .replace("no-mri-ct-ultrasound-replacement-claim", "no-mri-ct-us-repl-claim")
            .replace("future-ultrasound-body-map", "future-us-body-map")
            .replace("ultrasound_processing", "us_processing")
            .replace("raw_ultrasound", "raw_us")
            .replace("raw-ultrasound", "raw-us")
            .replace("ultrasound_payload", "us_payload")
            .replace("ultrasound-payload", "us-payload")
            .replace("future-acoustic-body-map", "future-ac-body-map")
            .replace("acoustic_processing", "ac_processing")
            .replace("raw_acoustic", "raw_ac")
            .replace("raw-acoustic", "raw-ac")
            .replace("acoustic_payload", "ac_payload")
            .replace("acoustic-payload", "ac-payload")
            .replace("raw_impedance", "raw_imp")
            .replace("raw-impedance", "raw-imp")
            .replace("raw_impedance_trace", "raw_imp_trace")
            .replace("raw-impedance-trace", "raw-imp-trace")
            .replace("impedance_trace", "imp_trace")
            .replace("impedance-trace", "imp-trace")
            .replace("serial_number", "serial_num")
            .replace("serial-number", "serial-num")
            .replace("bluetooth_mac", "bt_mac")
            .replace("bluetooth-mac", "bt-mac")
            .replace("mac_address", "mac_addr")
            .replace("mac-address", "mac-addr")
            .replace("raw_screenshot", "raw_scr")
            .replace("raw_ocr", "raw_o")
        )


if __name__ == "__main__":
    unittest.main()
