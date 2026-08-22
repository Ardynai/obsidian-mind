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
    PHASE12M_AUTHORIZATION_STATUS,
    PHASE12M_CANDIDATE_LABELS,
    PHASE12M_GRANT_STATUS,
    PHASE12M_MODEL_OPTION_CATEGORIES,
    PHASE12M_MODEL_OPTION_PROFILE_PHASE,
    PHASE12M_REQUIRED_FUTURE_GATES,
    PHASE12M_SOURCE_PHASE_RANGE,
    PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_CONTRACT_VERSION,
    PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
)

phase12m_profile = (
    phase12_contracts_module.phase12m_specialized_model_option_registry_capability_profile
)
PHASE12M_STATUS_SUMMARY_ATTR = (
    "phase12m_specialized_model_option_registry_capability_profile_status_summary"
)
phase12m_status_summary = getattr(phase12_contracts_module, PHASE12M_STATUS_SUMMARY_ATTR)
validate_phase12m_profile = (
    phase12_contracts_module.validate_phase12m_specialized_model_option_registry_capability_profile
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12m-specialized-model-option-registry-capability-profile-v1.json"
)


class Phase12MSpecializedModelOptionRegistryCapabilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_profile = phase12m_profile()
        cls.fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))

    def _profile(self):
        return copy.deepcopy(self.generated_profile)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture
        generated = self.generated_profile

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["specialized_model_option_registry_profile_contract_version"],
            PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["profile_kind"],
            PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
        )
        self.assertTrue(fixture["profile_id"].startswith("p12m-model-option-registry-profile-"))
        self.assertEqual(fixture["source_phase_range"], PHASE12M_SOURCE_PHASE_RANGE)
        self.assertEqual(
            fixture["model_option_profile_phase"],
            PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        )
        self.assertEqual(fixture["authorization_status"], PHASE12M_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12M_GRANT_STATUS)
        self.assertEqual(
            [ref["phase_label"] for ref in fixture["source_phase_references"]],
            ["12A", "12B", "12C", "12D", "12E", "12F", "12G", "12H", "12I", "12K", "12L"],
        )
        self.assertEqual(
            [item["model_option_category_label"] for item in fixture["model_option_categories"]],
            list(PHASE12M_MODEL_OPTION_CATEGORIES),
        )
        self.assertEqual(
            [item["candidate_label"] for item in fixture["candidate_labels"]],
            list(PHASE12M_CANDIDATE_LABELS),
        )
        self.assertEqual(
            [item["future_gate_label"] for item in fixture["required_future_gates"]],
            list(PHASE12M_REQUIRED_FUTURE_GATES),
        )
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["non_authorizing_proof"])
        self.assertTrue(fixture["security_review_required"])
        self.assertTrue(fixture["medical_safety_review_required"])
        self.assertTrue(fixture["model_labels_selectable_metadata_only"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12m_profile(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12m_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12M_SOURCE_PHASE_RANGE)
        self.assertEqual(summary["model_option_profile_phase"], "metadata-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["model_option_category_count"], 18)
        self.assertEqual(summary["candidate_label_count"], 16)
        self.assertEqual(summary["required_future_gate_count"], 12)
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["non_authorizing_proof"])
        self.assertTrue(summary["model_labels_selectable_metadata_only"])
        self.assertFalse(summary["phase12m_authorizes_runtime"])
        self.assertFalse(summary["phase12m_allows_model_execution"])
        self.assertFalse(summary["phase12m_allows_provider_execution"])
        self.assertFalse(summary["phase12m_allows_clinical_decision_support"])
        self.assertFalse(summary["phase12m_allows_diagnosis_or_treatment"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_model_labels_are_selectable_metadata_only(self):
        profile = self._profile()

        for item in profile["model_option_categories"]:
            with self.subTest(category=item["model_option_category_label"]):
                self.assertTrue(item["selectable_metadata_only"])
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["future_option_only"])
                self.assertFalse(item["model_loading_added"])
                self.assertFalse(item["model_execution_permitted"])
                self.assertFalse(item["provider_execution_permitted"])
                self.assertFalse(item["training_permitted"])
                self.assertFalse(item["fine_tuning_permitted"])
                self.assertFalse(item["clinical_decision_support_allowed"])
                self.assertFalse(item["diagnosis_or_treatment_allowed"])
                self.assertFalse(item["execution_permitted"])
        for item in profile["candidate_labels"]:
            with self.subTest(candidate=item["candidate_label"]):
                self.assertTrue(item["selectable_metadata_only"])
                self.assertTrue(item["metadata_only"])
                self.assertFalse(item["model_loading_added"])
                self.assertFalse(item["model_execution_permitted"])
                self.assertFalse(item["provider_execution_permitted"])
                self.assertFalse(item["training_permitted"])
                self.assertFalse(item["fine_tuning_permitted"])
                self.assertFalse(item["clinical_decision_support_allowed"])
                self.assertFalse(item["diagnosis_or_treatment_allowed"])
                self.assertFalse(item["execution_permitted"])

    def test_status_words_never_create_execution(self):
        finalize = (
            phase12_contracts_module._finalize_phase12m_specialized_model_option_registry_profile
        )
        for wording in (
            "model",
            "specialist",
            "enabled",
            "configured",
            "available",
            "trained",
            "fine-tuned",
            "ready",
            "approved",
            "authorized",
            "provider",
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
                unsafe["phase12m_authorizes_runtime"] = True
                unsafe["phase12m_allows_model_execution"] = True
                unsafe["phase12m_allows_provider_execution"] = True
                unsafe["phase12m_allows_training"] = True
                unsafe["phase12m_allows_clinical_decision_support"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12m_profile(unsafe)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12m_authorizes_runtime"])
                self.assertFalse(safe["phase12m_allows_model_execution"])
                self.assertFalse(safe["phase12m_allows_provider_execution"])
                self.assertFalse(safe["phase12m_allows_training"])
                self.assertFalse(safe["phase12m_allows_clinical_decision_support"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_and_model_action_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._profile()
                unsafe[field] = True

                result = validate_phase12m_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_sensor_model_labels_do_not_imply_device_or_clinical_access(self):
        profile = self._profile()
        sensor_fragments = ("csi-rf", "bia", "acoustic", "ultrasound", "time-series")
        sensor_categories = [
            item
            for item in profile["model_option_categories"]
            if any(
                fragment in item["model_option_category_label"].lower()
                for fragment in sensor_fragments
            )
        ]
        sensor_candidates = [
            item
            for item in profile["candidate_labels"]
            if any(fragment in item["candidate_label"].lower() for fragment in sensor_fragments)
        ]

        self.assertGreaterEqual(len(sensor_categories), 4)
        self.assertGreaterEqual(len(sensor_candidates), 4)
        for item in [*sensor_categories, *sensor_candidates]:
            label = item.get("model_option_category_label") or item.get("candidate_label")
            with self.subTest(label=label):
                self.assertFalse(item["device_access_allowed"])
                self.assertFalse(item["raw_sensor_processing_allowed"])
                self.assertFalse(item["clinical_decision_support_allowed"])
                self.assertFalse(item["diagnosis_or_treatment_allowed"])
                self.assertFalse(item["execution_permitted"])

        unsafe = self._profile()
        unsafe["phase12m_allows_device_access"] = True
        unsafe["phase12m_allows_raw_sensor_processing"] = True
        unsafe["device_access_granted"] = True
        unsafe["raw_sensor_processing_added"] = True
        unsafe["monitoring_added"] = True

        result = validate_phase12m_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.to_dict()
        self.assertFalse(safe["phase12m_allows_device_access"])
        self.assertFalse(safe["phase12m_allows_raw_sensor_processing"])
        self.assertFalse(safe["device_access_granted"])
        self.assertFalse(safe["raw_sensor_processing_added"])
        self.assertFalse(safe["monitoring_added"])

    def test_medical_model_labels_do_not_imply_clinical_recommendations(self):
        profile = self._profile()
        medical_items = [
            item
            for item in [*profile["model_option_categories"], *profile["candidate_labels"]]
            if "medical"
            in (item.get("model_option_category_label") or item.get("candidate_label")).lower()
        ]

        self.assertGreaterEqual(len(medical_items), 6)
        for item in medical_items:
            label = item.get("model_option_category_label") or item.get("candidate_label")
            with self.subTest(label=label):
                self.assertFalse(item["clinical_decision_support_allowed"])
                self.assertFalse(item["diagnosis_or_treatment_allowed"])
                self.assertFalse(item["private_health_data_allowed"])
                self.assertFalse(item["execution_permitted"])

        unsafe = self._profile()
        unsafe["clinical_decision_support_allowed"] = True
        unsafe["diagnosis_or_treatment_allowed"] = True
        unsafe["private_health_data_allowed"] = True
        unsafe["phase12m_allows_clinical_decision_support"] = True
        unsafe["phase12m_allows_diagnosis_or_treatment"] = True
        unsafe["phase12m_provides_medical_advice"] = True
        unsafe["phase12m_provides_prescribing"] = True
        unsafe["medical_advice_provided"] = True
        unsafe["diagnosis_provided"] = True
        unsafe["treatment_plan_provided"] = True
        unsafe["prescribing_added"] = True

        result = validate_phase12m_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.to_dict()
        self.assertFalse(safe["clinical_decision_support_allowed"])
        self.assertFalse(safe["diagnosis_or_treatment_allowed"])
        self.assertFalse(safe["private_health_data_allowed"])
        self.assertFalse(safe["phase12m_provides_medical_advice"])
        self.assertFalse(safe["phase12m_provides_prescribing"])
        self.assertFalse(safe["medical_advice_provided"])
        self.assertFalse(safe["diagnosis_provided"])
        self.assertFalse(safe["treatment_plan_provided"])

    def test_hidden_model_runtime_semantics_fail_closed(self):
        profile = self._profile()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("model_option_categories")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["specialized_model_option_registry_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(profile)
        nested_unknown["candidate_labels"][0]["runner"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "model-loading": ("model_boundary_statement", "model loading"),
            "model-execution": ("model_boundary_statement", "model execution"),
            "provider-execution": ("model_boundary_statement", "provider execution"),
            "training": ("model_boundary_statement", "training execution"),
            "fine-tuning": ("model_boundary_statement", "fine-tuning execution"),
            "database-ingestion": ("model_boundary_statement", "database ingestion"),
            "web-scraping": ("model_boundary_statement", "web scraping"),
            "network-call": ("model_boundary_statement", "network call"),
            "runtime-adapter": ("model_boundary_statement", "runtime adapter"),
            "real-mode": ("model_boundary_statement", "real-mode authorization"),
            "clinical": ("medical_boundary_statement", "clinical recommendation"),
            "diagnosis": ("medical_boundary_statement", "diagnosis"),
            "treatment": ("medical_boundary_statement", "treatment planning"),
            "medical-advice": ("medical_boundary_statement", "medical advice"),
            "prescribing": ("medical_boundary_statement", "prescribing"),
            "private-health": ("medical_boundary_statement", "private health data processing"),
            "device-access": ("sensor_boundary_statement", "device access"),
            "raw-sensor": ("sensor_boundary_statement", "raw sensor processing"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(profile)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12m_profile(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12m_authorizes_runtime"])
                self.assertFalse(safe["model_execution_permitted"])
                self.assertFalse(safe["provider_execution_permitted"])
                self.assertFalse(safe["training_permitted"])
                self.assertFalse(safe["fine_tuning_permitted"])
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

    def test_phase12m_module_does_not_add_runtime_imports_or_true_flags(self):
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
            '"model_execution_permitted": true',
            '"provider_execution_permitted": true',
            '"training_permitted": true',
            '"fine_tuning_permitted": true',
            '"model_loading_added": true',
            '"model_execution_granted": true',
            '"provider_execution_granted": true',
            '"training_execution_granted": true',
            '"fine_tuning_execution_granted": true',
            '"network_call_execution_granted": true',
            '"clinical_decision_support_allowed": true',
            '"diagnosis_or_treatment_allowed": true',
            '"private_health_data_allowed": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
            "model_execution_permitted",
            "provider_execution_permitted",
            "training_permitted",
            "fine_tuning_permitted",
            "clinical_decision_support_allowed",
            "diagnosis_or_treatment_allowed",
            "private_health_data_allowed",
            "model_loading_added",
            "runtime_model_execution_granted",
            "provider_execution_granted",
            "model_execution_granted",
            "training_execution_granted",
            "fine_tuning_execution_granted",
            "runtime_adapter_execution_granted",
            "active_grant_present",
            "real_mode_authorization_added",
            "database_ingestion_added",
            "web_scraping_added",
            "network_call_execution_granted",
            "clinical_decision_support_added",
            "clinical_recommendation_added",
            "medical_advice_provided",
            "diagnosis_provided",
            "treatment_plan_provided",
            "prescribing_added",
            "herb_dosing_added",
            "supplement_dosing_added",
            "calorie_macro_prescription_added",
            "nutrition_prescription_added",
            "private_health_data_processing_added",
            "device_access_granted",
            "device_connection_execution_granted",
            "raw_sensor_processing_added",
            "sensor_processing_execution_granted",
            "monitoring_added",
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
