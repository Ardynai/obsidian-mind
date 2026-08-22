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
    PHASE12N_AUTHORIZATION_STATUS,
    PHASE12N_FUSION_CONCEPT_LABELS,
    PHASE12N_GRANT_STATUS,
    PHASE12N_REQUIRED_FUTURE_GATES,
    PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS,
    PHASE12N_SOURCE_PHASE_RANGE,
    PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
    PHASE12N_WORKFLOW_MODES,
    PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_CONTRACT_VERSION,
    PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
)

phase12n_profile = (
    phase12_contracts_module.phase12n_workflow_orchestration_mode_registry_capability_profile
)
PHASE12N_STATUS_SUMMARY_ATTR = (
    "phase12n_workflow_orchestration_mode_registry_capability_profile_status_summary"
)
phase12n_status_summary = getattr(phase12_contracts_module, PHASE12N_STATUS_SUMMARY_ATTR)
PHASE12N_VALIDATE_ATTR = "validate_phase12n_workflow_orchestration_mode_registry_capability_profile"
validate_phase12n_profile = getattr(phase12_contracts_module, PHASE12N_VALIDATE_ATTR)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12n-workflow-orchestration-mode-registry-capability-profile-v1.json"
)


class Phase12NWorkflowOrchestrationModeRegistryCapabilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_profile = phase12n_profile()
        cls.fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))

    def _profile(self):
        return copy.deepcopy(self.generated_profile)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture
        generated = self.generated_profile

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["workflow_orchestration_mode_registry_profile_contract_version"],
            PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["profile_kind"],
            PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        )
        self.assertTrue(fixture["profile_id"].startswith("p12n-workflow-mode-registry-profile-"))
        self.assertEqual(fixture["source_phase_range"], PHASE12N_SOURCE_PHASE_RANGE)
        self.assertEqual(
            fixture["workflow_mode_profile_phase"],
            PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
        )
        self.assertEqual(fixture["authorization_status"], PHASE12N_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12N_GRANT_STATUS)
        self.assertEqual(
            [ref["phase_label"] for ref in fixture["source_phase_references"]],
            ["12A", "12B", "12C", "12D", "12E", "12F", "12G", "12H", "12I", "12K", "12L", "12M"],
        )
        self.assertEqual(
            [item["workflow_mode_label"] for item in fixture["workflow_modes"]],
            [label for label, _ in PHASE12N_WORKFLOW_MODES],
        )
        self.assertEqual(
            [item["fusion_concept_label"] for item in fixture["fusion_concepts"]],
            list(PHASE12N_FUSION_CONCEPT_LABELS),
        )
        self.assertEqual(
            [
                item["scientist_evolution_concept_label"]
                for item in fixture["scientist_evolution_concepts"]
            ],
            list(PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS),
        )
        self.assertEqual(
            [item["future_gate_label"] for item in fixture["required_future_gates"]],
            list(PHASE12N_REQUIRED_FUTURE_GATES),
        )
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["non_authorizing_proof"])
        self.assertTrue(fixture["security_review_required"])
        self.assertTrue(fixture["medical_safety_review_required"])
        self.assertTrue(fixture["workflow_modes_metadata_only"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12n_profile(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12n_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12N_SOURCE_PHASE_RANGE)
        self.assertEqual(summary["workflow_mode_profile_phase"], "metadata-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["workflow_mode_count"], 3)
        self.assertEqual(summary["fusion_concept_count"], 9)
        self.assertEqual(summary["scientist_evolution_concept_count"], 11)
        self.assertEqual(summary["required_future_gate_count"], 11)
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["non_authorizing_proof"])
        self.assertTrue(summary["workflow_modes_metadata_only"])
        self.assertFalse(summary["phase12n_authorizes_runtime"])
        self.assertFalse(summary["phase12n_allows_workflow_mode_execution"])
        self.assertFalse(summary["phase12n_allows_runtime_orchestration"])
        self.assertFalse(summary["phase12n_allows_model_routing"])
        self.assertFalse(summary["phase12n_allows_clinical_decision_support"])
        self.assertFalse(summary["phase12n_allows_diagnosis_or_treatment"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_workflow_modes_are_metadata_only(self):
        profile = self._profile()

        for item in profile["workflow_modes"]:
            with self.subTest(mode=item["workflow_mode_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["future_mode_only"])
                self.assertFalse(item["workflow_mode_execution_permitted"])
                self.assertFalse(item["runtime_orchestration_added"])
                self.assertFalse(item["model_routing_execution_permitted"])
                self.assertFalse(item["autonomous_experimentation_permitted"])
                self.assertFalse(item["code_execution_permitted"])
                self.assertFalse(item["clinical_decision_support_allowed"])
                self.assertFalse(item["diagnosis_or_treatment_allowed"])
                self.assertFalse(item["private_health_data_allowed"])
                self.assertFalse(item["execution_permitted"])

    def test_status_words_never_create_runtime_permission_or_active_grant(self):
        finalize = (
            phase12_contracts_module._finalize_phase12n_workflow_orchestration_mode_registry_profile
        )
        for wording in (
            "normal",
            "fusion",
            "fugu",
            "trinity",
            "conductor",
            "scientist",
            "evolution",
            "tree-search",
            "experiment",
            "autonomous",
            "enabled",
            "configured",
            "available",
            "ready",
            "approved",
            "authorized",
            "runtime",
            "clinical",
            "diagnosis",
            "treatment",
        ):
            with self.subTest(wording=wording):
                unsafe = self._profile()
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["profile_status"] = wording
                unsafe["phase12n_authorizes_runtime"] = True
                unsafe["phase12n_allows_workflow_mode_execution"] = True
                unsafe["phase12n_allows_model_routing"] = True
                unsafe["active_grant_present"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12n_profile(unsafe)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12n_authorizes_runtime"])
                self.assertFalse(safe["phase12n_allows_workflow_mode_execution"])
                self.assertFalse(safe["phase12n_allows_model_routing"])
                self.assertFalse(safe["active_grant_present"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_and_workflow_action_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._profile()
                unsafe[field] = True

                result = validate_phase12n_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_optional_fusion_mode_does_not_execute_routing_or_provider_calls(self):
        profile = self._profile()
        fusion_mode = [
            item
            for item in profile["workflow_modes"]
            if item["workflow_mode_label"] == "fusion-mode"
        ]
        self.assertEqual(len(fusion_mode), 1)
        self.assertFalse(fusion_mode[0]["model_routing_execution_permitted"])
        self.assertFalse(fusion_mode[0]["runtime_orchestration_added"])

        for item in profile["fusion_concepts"]:
            with self.subTest(concept=item["fusion_concept_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["future_concept_only"])
                self.assertFalse(item["model_routing_execution_permitted"])
                self.assertFalse(item["provider_call_execution_granted"])
                self.assertFalse(item["model_loading_added"])
                self.assertFalse(item["learned_coordination_execution_granted"])
                self.assertFalse(item["agent_routing_execution_granted"])
                self.assertFalse(item["network_call_execution_granted"])
                self.assertFalse(item["runtime_orchestration_added"])
                self.assertFalse(item["execution_permitted"])

        unsafe = self._profile()
        unsafe["phase12n_allows_model_routing"] = True
        unsafe["model_routing_execution_permitted"] = True
        unsafe["provider_call_execution_granted"] = True
        unsafe["model_loading_added"] = True
        unsafe["learned_coordination_execution_granted"] = True
        unsafe["agent_routing_execution_granted"] = True
        unsafe["network_call_execution_granted"] = True
        unsafe["runtime_orchestration_added"] = True

        result = validate_phase12n_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.to_dict()
        self.assertFalse(safe["phase12n_allows_model_routing"])
        self.assertFalse(safe["model_routing_execution_permitted"])
        self.assertFalse(safe["provider_call_execution_granted"])
        self.assertFalse(safe["runtime_orchestration_added"])

    def test_scientist_evolution_mode_does_not_execute_research_actions(self):
        profile = self._profile()
        scientist_mode = [
            item
            for item in profile["workflow_modes"]
            if item["workflow_mode_label"] == "scientist-evolution-mode"
        ]
        self.assertEqual(len(scientist_mode), 1)
        self.assertFalse(scientist_mode[0]["code_execution_permitted"])
        self.assertFalse(scientist_mode[0]["autonomous_experimentation_permitted"])

        for item in profile["scientist_evolution_concepts"]:
            with self.subTest(concept=item["scientist_evolution_concept_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["future_concept_only"])
                self.assertFalse(item["code_execution_permitted"])
                self.assertFalse(item["experiment_execution_permitted"])
                self.assertFalse(item["web_access_permitted"])
                self.assertFalse(item["literature_search_execution_permitted"])
                self.assertFalse(item["database_ingestion_added"])
                self.assertFalse(item["manuscript_generation_added"])
                self.assertFalse(item["autonomous_publication_allowed"])
                self.assertFalse(item["model_training_execution_granted"])
                self.assertFalse(item["model_fine_tuning_execution_granted"])
                self.assertFalse(item["autonomous_research_action_permitted"])
                self.assertFalse(item["execution_permitted"])

        unsafe = self._profile()
        unsafe["phase12n_allows_code_execution"] = True
        unsafe["phase12n_allows_experiment_execution"] = True
        unsafe["phase12n_allows_autonomous_experimentation"] = True
        unsafe["phase12n_allows_web_access"] = True
        unsafe["code_execution_permitted"] = True
        unsafe["experiment_execution_permitted"] = True
        unsafe["web_access_permitted"] = True
        unsafe["literature_search_execution_permitted"] = True
        unsafe["database_ingestion_added"] = True
        unsafe["manuscript_generation_added"] = True
        unsafe["autonomous_publication_allowed"] = True
        unsafe["model_training_execution_granted"] = True
        unsafe["model_fine_tuning_execution_granted"] = True
        unsafe["autonomous_research_action_permitted"] = True

        result = validate_phase12n_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.to_dict()
        self.assertFalse(safe["phase12n_allows_code_execution"])
        self.assertFalse(safe["phase12n_allows_experiment_execution"])
        self.assertFalse(safe["phase12n_allows_autonomous_experimentation"])
        self.assertFalse(safe["code_execution_permitted"])
        self.assertFalse(safe["autonomous_research_action_permitted"])

    def test_medical_sensor_and_private_health_boundaries_remain_blocked(self):
        unsafe = self._profile()
        unsafe["phase12n_allows_clinical_decision_support"] = True
        unsafe["phase12n_allows_diagnosis_or_treatment"] = True
        unsafe["phase12n_allows_private_health_data_processing"] = True
        unsafe["phase12n_allows_device_or_sensor_access"] = True
        unsafe["phase12n_provides_medical_advice"] = True
        unsafe["clinical_decision_support_allowed"] = True
        unsafe["diagnosis_or_treatment_allowed"] = True
        unsafe["private_health_data_allowed"] = True
        unsafe["medical_advice_provided"] = True
        unsafe["diagnosis_provided"] = True
        unsafe["treatment_plan_provided"] = True
        unsafe["dosing_added"] = True
        unsafe["nutrition_prescription_added"] = True
        unsafe["device_access_granted"] = True
        unsafe["sensor_access_granted"] = True
        unsafe["raw_sensor_processing_added"] = True
        unsafe["private_health_data_processing_added"] = True

        result = validate_phase12n_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.to_dict()
        self.assertFalse(safe["phase12n_allows_clinical_decision_support"])
        self.assertFalse(safe["phase12n_allows_diagnosis_or_treatment"])
        self.assertFalse(safe["phase12n_allows_private_health_data_processing"])
        self.assertFalse(safe["phase12n_allows_device_or_sensor_access"])
        self.assertFalse(safe["phase12n_provides_medical_advice"])
        self.assertFalse(safe["clinical_decision_support_allowed"])
        self.assertFalse(safe["diagnosis_or_treatment_allowed"])
        self.assertFalse(safe["private_health_data_allowed"])
        self.assertFalse(safe["medical_advice_provided"])
        self.assertFalse(safe["device_access_granted"])
        self.assertFalse(safe["raw_sensor_processing_added"])

    def test_hidden_workflow_runtime_semantics_fail_closed(self):
        profile = self._profile()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("workflow_modes")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["workflow_orchestration_mode_registry_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(profile)
        nested_unknown["fusion_concepts"][0]["runner"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "runtime-orchestration": ("workflow_boundary_statement", "runtime orchestration"),
            "model-routing": ("fusion_boundary_statement", "model routing"),
            "provider-call": ("fusion_boundary_statement", "provider call"),
            "model-loading": ("fusion_boundary_statement", "model loading"),
            "agent-routing": ("fusion_boundary_statement", "agent routing"),
            "code-execution": ("scientist_boundary_statement", "code execution"),
            "experiment-execution": ("scientist_boundary_statement", "experiment execution"),
            "web-access": ("scientist_boundary_statement", "web access"),
            "literature-search": ("scientist_boundary_statement", "literature search"),
            "database-ingestion": ("scientist_boundary_statement", "database ingestion"),
            "manuscript-generation": ("scientist_boundary_statement", "manuscript generation"),
            "autonomous-publication": ("scientist_boundary_statement", "autonomous publication"),
            "clinical": ("medical_sensor_boundary_statement", "clinical recommendation"),
            "diagnosis": ("medical_sensor_boundary_statement", "diagnosis"),
            "treatment": ("medical_sensor_boundary_statement", "treatment planning"),
            "medical-advice": ("medical_sensor_boundary_statement", "medical advice"),
            "dosing": ("medical_sensor_boundary_statement", "dosing"),
            "private-health": (
                "medical_sensor_boundary_statement",
                "private health data processing",
            ),
            "device-access": ("medical_sensor_boundary_statement", "device access"),
            "raw-sensor": ("medical_sensor_boundary_statement", "raw sensor processing"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(profile)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12n_profile(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12n_authorizes_runtime"])
                self.assertFalse(safe["workflow_mode_execution_permitted"])
                self.assertFalse(safe["model_routing_execution_permitted"])
                self.assertFalse(safe["code_execution_permitted"])
                self.assertFalse(safe["experiment_execution_permitted"])
                self.assertFalse(safe["clinical_decision_support_allowed"])
                self.assertFalse(safe["diagnosis_or_treatment_allowed"])
                self.assertFalse(safe["private_health_data_allowed"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_source_references_and_phase11_summaries_remain_non_executing(self):
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

        profile = self._profile()
        for reference in profile["source_phase_references"]:
            with self.subTest(phase=reference["phase_label"]):
                self.assertTrue(reference["metadata_only"])
                self.assertEqual(reference["runtime_stage"], "not-implemented")
                self.assertFalse(reference["execution_permitted"])
                self.assertFalse(reference["real_mode_runtime_enabled"])

    def test_phase12n_module_does_not_add_runtime_imports_or_true_flags(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "import transformers",
            "from transformers",
            "import torch",
            "from torch",
            "import tensorflow",
            "from tensorflow",
            "huggingface_hub",
            "openai.",
            "google.generativeai",
            "import requests",
            "from requests",
            "urllib.",
            "socket.",
            "subprocess.",
            '"execution_permitted": true',
            '"real_mode_runtime_enabled": true',
            '"workflow_mode_execution_permitted": true',
            '"model_routing_execution_permitted": true',
            '"code_execution_permitted": true',
            '"experiment_execution_permitted": true',
            '"autonomous_experimentation_permitted": true',
            '"provider_call_execution_granted": true',
            '"model_loading_added": true',
            '"network_call_execution_granted": true',
            '"clinical_decision_support_allowed": true',
            '"diagnosis_or_treatment_allowed": true',
            '"private_health_data_allowed": true',
            '"device_access_granted": true',
            '"raw_sensor_processing_added": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
            "workflow_mode_execution_permitted",
            "autonomous_experimentation_permitted",
            "code_execution_permitted",
            "model_routing_execution_permitted",
            "clinical_decision_support_allowed",
            "diagnosis_or_treatment_allowed",
            "private_health_data_allowed",
            "runtime_orchestration_added",
            "fusion_coordination_execution_granted",
            "learned_coordination_execution_granted",
            "agent_routing_execution_granted",
            "provider_call_execution_granted",
            "provider_execution_granted",
            "model_loading_added",
            "runtime_model_execution_granted",
            "model_execution_granted",
            "training_permitted",
            "fine_tuning_permitted",
            "training_execution_granted",
            "fine_tuning_execution_granted",
            "model_training_execution_granted",
            "model_fine_tuning_execution_granted",
            "experiment_execution_permitted",
            "experiment_execution_granted",
            "web_access_permitted",
            "literature_search_execution_permitted",
            "database_ingestion_added",
            "web_scraping_added",
            "network_call_execution_granted",
            "runtime_adapter_execution_granted",
            "active_grant_present",
            "real_mode_authorization_added",
            "clinical_decision_support_added",
            "clinical_recommendation_added",
            "medical_advice_provided",
            "diagnosis_provided",
            "treatment_plan_provided",
            "dosing_added",
            "nutrition_prescription_added",
            "device_access_granted",
            "device_connection_execution_granted",
            "sensor_access_granted",
            "raw_sensor_processing_added",
            "sensor_processing_execution_granted",
            "private_health_data_processing_added",
            "manuscript_generation_added",
            "autonomous_publication_allowed",
            "autonomous_research_action_permitted",
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
