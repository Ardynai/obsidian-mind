import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase11_contracts import (
    phase11_planning_governance_closeout_status_summary,
    phase11_runtime_authorization_gap_ledger_status_summary,
)
from somatic.safety.phase12_contracts import (
    PHASE12K_AUTHORIZATION_STATUS,
    PHASE12K_BACKEND_OPTION_LABELS,
    PHASE12K_CAPABILITY_PHASE,
    PHASE12K_CREDENTIAL_POLICY,
    PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_CONTRACT_VERSION,
    PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
    PHASE12K_GRANT_STATUS,
    PHASE12K_REQUIRED_FUTURE_GATES,
    PHASE12K_SOURCE_PHASE_RANGE,
    PHASE12K_WORKLOAD_CLASSES,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12c_visual_supervision_capability_profile,
    phase12d_visual_desktop_consent_gate_requirements,
    phase12e_physiological_sensor_capability_profile,
    phase12f_secure_drop_consumer_boundary,
    phase12g_production_readiness_coverage_matrix,
    phase12h_somatic_standalone_production_readiness_ownership_map,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12c_visual_supervision_capability_profile,
    validate_phase12d_visual_desktop_consent_gate_requirements,
    validate_phase12e_physiological_sensor_capability_profile,
    validate_phase12f_secure_drop_consumer_boundary,
    validate_phase12g_production_readiness_coverage_matrix,
    validate_phase12h_somatic_standalone_production_readiness_ownership_map,
)

phase12i_profile = (
    phase12_contracts_module.phase12i_integrative_herbal_nutrition_knowledge_capability_profile
)
PHASE12I_VALIDATOR_ATTR = (
    "validate_phase12i_integrative_herbal_nutrition_knowledge_capability_profile"
)
validate_phase12i_profile = getattr(
    phase12_contracts_module,
    PHASE12I_VALIDATOR_ATTR,
)
phase12k_profile = (
    phase12_contracts_module.phase12k_external_compute_quantum_backend_capability_profile
)
PHASE12K_STATUS_SUMMARY_ATTR = (
    "phase12k_external_compute_quantum_backend_capability_profile_status_summary"
)
phase12k_status_summary = getattr(
    phase12_contracts_module,
    PHASE12K_STATUS_SUMMARY_ATTR,
)
validate_phase12k_profile = (
    phase12_contracts_module.validate_phase12k_external_compute_quantum_backend_capability_profile
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12k-external-compute-quantum-backend-capability-profile-v1.json"
)


class Phase12KExternalComputeQuantumBackendCapabilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_profile = phase12k_profile()
        cls.fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))

    def _profile(self):
        return copy.deepcopy(self.generated_profile)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture
        generated = self.generated_profile

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["external_compute_quantum_profile_contract_version"],
            PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["profile_kind"],
            PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
        )
        self.assertTrue(fixture["profile_id"].startswith("p12k-compute-quantum-profile-"))
        self.assertEqual(fixture["source_phase_range"], PHASE12K_SOURCE_PHASE_RANGE)
        self.assertEqual(fixture["capability_phase"], PHASE12K_CAPABILITY_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12K_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12K_GRANT_STATUS)
        self.assertEqual(fixture["credential_policy"], PHASE12K_CREDENTIAL_POLICY)
        self.assertEqual(
            [ref["phase_label"] for ref in fixture["source_phase_references"]],
            [
                "12A",
                "12B",
                "12C",
                "12D",
                "12E",
                "12F",
                "12G",
                "12H",
                "12I",
            ],
        )
        self.assertEqual(
            [item["backend_option_label"] for item in fixture["backend_options"]],
            list(PHASE12K_BACKEND_OPTION_LABELS),
        )
        self.assertEqual(
            [item["workload_class_label"] for item in fixture["workload_classes"]],
            list(PHASE12K_WORKLOAD_CLASSES),
        )
        self.assertEqual(
            [item["future_gate_label"] for item in fixture["required_future_gates"]],
            list(PHASE12K_REQUIRED_FUTURE_GATES),
        )
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["non_authorizing_proof"])
        self.assertTrue(fixture["security_review_required"])
        self.assertTrue(fixture["medical_safety_review_required"])
        self.assertTrue(fixture["human_approval_required"])
        self.assertTrue(fixture["cost_guard_required"])
        self.assertFalse(fixture["private_health_data_allowed"])
        self.assertFalse(fixture["clinical_decision_support_allowed"])
        self.assertFalse(fixture["diagnosis_or_treatment_allowed"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12k_profile(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12k_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12K_SOURCE_PHASE_RANGE)
        self.assertEqual(summary["capability_phase"], "external-compute-quantum-profile-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["credential_policy"], "external-secret-only")
        self.assertEqual(summary["backend_option_count"], 5)
        self.assertEqual(summary["workload_class_count"], 10)
        self.assertEqual(summary["required_future_gate_count"], 11)
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["non_authorizing_proof"])
        self.assertTrue(summary["human_approval_required"])
        self.assertTrue(summary["cost_guard_required"])
        self.assertFalse(summary["private_health_data_allowed"])
        self.assertFalse(summary["clinical_decision_support_allowed"])
        self.assertFalse(summary["diagnosis_or_treatment_allowed"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_backend_and_workload_labels_are_metadata_only(self):
        profile = self._profile()

        for item in profile["backend_options"]:
            with self.subTest(backend=item["backend_option_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertEqual(item["credential_policy"], "external-secret-only")
                self.assertTrue(item["human_approval_required"])
                self.assertTrue(item["cost_guard_required"])
                self.assertFalse(item["private_health_data_allowed"])
                self.assertFalse(item["api_call_execution_granted"])
                self.assertFalse(item["sdk_execution_granted"])
                self.assertFalse(item["simulator_execution_granted"])
                self.assertFalse(item["provider_execution_granted"])
                self.assertFalse(item["network_call_execution_granted"])
                self.assertFalse(item["spending_permitted"])
                self.assertFalse(item["execution_permitted"])
        for item in profile["workload_classes"]:
            with self.subTest(workload=item["workload_class_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertFalse(item["private_health_data_allowed"])
                self.assertFalse(item["clinical_decision_support_allowed"])
                self.assertFalse(item["diagnosis_or_treatment_allowed"])
                self.assertFalse(item["medical_advice_provided"])
                self.assertFalse(item["execution_permitted"])

    def test_status_words_never_create_grants(self):
        finalize = phase12_contracts_module._finalize_phase12k_external_compute_quantum_profile
        for wording in (
            "configured",
            "available",
            "keyed",
            "enabled",
            "approved",
            "authorized",
            "trained",
            "ready",
            "production",
        ):
            with self.subTest(wording=wording):
                unsafe = self._profile()
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["profile_status"] = wording
                unsafe["phase12k_authorizes_runtime"] = True
                unsafe["api_call_execution_granted"] = True
                unsafe["sdk_execution_granted"] = True
                unsafe["simulator_execution_granted"] = True
                unsafe["network_call_execution_granted"] = True
                unsafe["spending_permitted"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12k_profile(unsafe)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12k_authorizes_runtime"])
                self.assertFalse(safe["api_call_execution_granted"])
                self.assertFalse(safe["sdk_execution_granted"])
                self.assertFalse(safe["simulator_execution_granted"])
                self.assertFalse(safe["network_call_execution_granted"])
                self.assertFalse(safe["spending_permitted"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_and_backend_action_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._profile()
                unsafe[field] = True

                result = validate_phase12k_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_quantum_workloads_cannot_produce_medical_outputs(self):
        unsafe = self._profile()
        unsafe["private_health_data_allowed"] = True
        unsafe["clinical_decision_support_allowed"] = True
        unsafe["diagnosis_or_treatment_allowed"] = True
        unsafe["phase12k_allows_private_health_data_processing"] = True
        unsafe["phase12k_provides_medical_advice"] = True
        unsafe["phase12k_allows_diagnosis_or_treatment"] = True
        unsafe["workload_classes"][0]["private_health_data_allowed"] = True
        unsafe["workload_classes"][0]["clinical_decision_support_allowed"] = True
        unsafe["workload_classes"][0]["diagnosis_or_treatment_allowed"] = True
        unsafe["workload_classes"][0]["medical_advice_provided"] = True

        result = validate_phase12k_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.sanitized_record
        self.assertFalse(safe["private_health_data_allowed"])
        self.assertFalse(safe["clinical_decision_support_allowed"])
        self.assertFalse(safe["diagnosis_or_treatment_allowed"])
        self.assertFalse(safe["phase12k_allows_private_health_data_processing"])
        self.assertFalse(safe["phase12k_provides_medical_advice"])
        self.assertFalse(safe["phase12k_allows_diagnosis_or_treatment"])

    def test_hidden_backend_runtime_and_private_semantics_fail_closed(self):
        profile = self._profile()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("backend_options")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["external_compute_quantum_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(profile)
        nested_unknown["backend_options"][0]["runner"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "api-key": ("compute_boundary_statement", "api_key"),
            "env-var": ("compute_boundary_statement", "env var token"),
            "vault-ref": ("compute_boundary_statement", "vault reference"),
            "tokenized-url": ("compute_boundary_statement", "remote_url token marker"),
            "provider-call": ("compute_boundary_statement", "provider call executed"),
            "network-call": ("compute_boundary_statement", "network call"),
            "spending": ("compute_boundary_statement", "spending permitted"),
            "sdk-execution": ("compute_boundary_statement", "sdk execution"),
            "simulator-execution": ("compute_boundary_statement", "simulator execution"),
            "runtime-adapter": ("compute_boundary_statement", "runtime adapter"),
            "real-mode": ("compute_boundary_statement", "real-mode authorization"),
            "diagnosis": ("medical_boundary_statement", "diagnosis"),
            "treatment": ("medical_boundary_statement", "treatment planning"),
            "clinical-recommendation": ("medical_boundary_statement", "clinical recommendation"),
            "medical-advice": ("medical_boundary_statement", "medical advice"),
            "private-health-data": ("medical_boundary_statement", "private health data processing"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(profile)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12k_profile(payload)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["phase12k_authorizes_runtime"])
                self.assertFalse(result.to_dict()["api_call_execution_granted"])
                self.assertFalse(result.to_dict()["sdk_execution_granted"])
                self.assertFalse(result.to_dict()["simulator_execution_granted"])
                self.assertFalse(result.to_dict()["spending_permitted"])
                self.assertFalse(result.to_dict()["medical_advice_provided"])
                self.assertFalse(result.to_dict()["diagnosis_provided"])
                self.assertFalse(result.to_dict()["treatment_plan_provided"])
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_phase11_and_phase12_sources_remain_non_executing(self):
        phase11_summaries = (
            phase11_runtime_authorization_gap_ledger_status_summary(),
            phase11_planning_governance_closeout_status_summary(),
        )
        for summary in phase11_summaries:
            phase_label = summary.get("source_phase_range") or summary.get("phase_range")
            with self.subTest(phase11=phase_label):
                self.assertEqual(summary["runtime_stage"], "not-implemented")
                self.assertFalse(summary["execution_permitted"])
                self.assertFalse(summary["real_mode_runtime_enabled"])

        phase12_sources = (
            (
                phase12a_runtime_authorization_design_charter(),
                validate_phase12a_runtime_authorization_design_charter,
            ),
            (
                phase12b_runtime_authorization_record_candidate(),
                validate_phase12b_runtime_authorization_record_candidate,
            ),
            (
                phase12c_visual_supervision_capability_profile(),
                validate_phase12c_visual_supervision_capability_profile,
            ),
            (
                phase12d_visual_desktop_consent_gate_requirements(),
                validate_phase12d_visual_desktop_consent_gate_requirements,
            ),
            (
                phase12e_physiological_sensor_capability_profile(),
                validate_phase12e_physiological_sensor_capability_profile,
            ),
            (
                phase12f_secure_drop_consumer_boundary(),
                validate_phase12f_secure_drop_consumer_boundary,
            ),
            (
                phase12g_production_readiness_coverage_matrix(),
                validate_phase12g_production_readiness_coverage_matrix,
            ),
            (
                phase12h_somatic_standalone_production_readiness_ownership_map(),
                validate_phase12h_somatic_standalone_production_readiness_ownership_map,
            ),
            (
                phase12i_profile(),
                validate_phase12i_profile,
            ),
        )
        for payload, validator in phase12_sources:
            with self.subTest(kind=payload.get("profile_kind") or payload.get("matrix_kind")):
                result = validator(payload)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12k_module_does_not_add_runtime_imports_or_true_flags(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "import qiskit",
            "from qiskit",
            "qiskit_ibm_runtime",
            "import boto3",
            "from boto3",
            "azure.quantum",
            "dwave.cloud",
            "import dimod",
            "from dimod",
            "import requests",
            "from requests",
            "urllib.",
            "socket.",
            "subprocess.",
            '"execution_permitted": true',
            '"real_mode_runtime_enabled": true',
            '"api_call_execution_granted": true',
            '"sdk_execution_granted": true',
            '"simulator_execution_granted": true',
            '"spending_permitted": true',
            '"provider_execution_granted": true',
            '"network_call_execution_granted": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
            "api_call_execution_granted",
            "sdk_execution_granted",
            "simulator_execution_granted",
            "provider_call_execution_granted",
            "network_call_execution_granted",
            "spending_permitted",
            "credential_loading_added",
            "runtime_model_execution_granted",
            "provider_execution_granted",
            "model_execution_granted",
            "training_execution_granted",
            "fine_tuning_execution_granted",
            "runtime_adapter_execution_granted",
            "active_grant_present",
            "real_mode_authorization_added",
            "external_compute_execution_granted",
            "quantum_backend_execution_granted",
            "clinical_decision_support_added",
            "clinical_recommendation_added",
            "medical_advice_provided",
            "diagnosis_provided",
            "treatment_plan_provided",
            "private_health_data_processing_added",
            "database_ingestion_added",
            "web_scraping_added",
            "command_execution_granted",
            "connector_grant_present",
            "fabric_transfer_execution_granted",
            "ws_stream_execution_granted",
            "http_execution_granted",
            "mcp_tool_exposure_added",
            "task_execution_granted",
            "secure_drop_send_permitted",
            "secure_drop_receive_permitted",
            "service_discovery_runtime_added",
            "schedule_enforcement_added",
            "filesystem_access_granted",
            "process_control_granted",
            "db_storage_write_added",
            "secrets_access_granted",
            "production_ready",
            "execution_permitted",
            "real_mode_runtime_enabled",
        )


if __name__ == "__main__":
    unittest.main()
