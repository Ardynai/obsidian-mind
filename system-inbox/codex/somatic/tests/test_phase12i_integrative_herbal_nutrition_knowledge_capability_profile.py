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
    PHASE12I_AUTHORIZATION_STATUS,
    PHASE12I_CAPABILITY_PHASE,
    PHASE12I_GRANT_STATUS,
    PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_CONTRACT_VERSION,
    PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
    PHASE12I_REQUIRED_FUTURE_GATES,
    PHASE12I_SOURCE_CLASS_LABELS,
    PHASE12I_SOURCE_PHASE_RANGE,
    PHASE12I_SPECIALIST_PROFILE_LABELS,
    PHASE12I_USER_PREFERENCE_MODES,
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
_p12c = phase12_contracts_module
phase12i_status_summary = (
    _p12c.phase12i_integrative_herbal_nutrition_knowledge_capability_profile_status_summary
)
validate_phase12i_profile = (
    _p12c.validate_phase12i_integrative_herbal_nutrition_knowledge_capability_profile
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12i-integrative-herbal-nutrition-knowledge-capability-profile-v1.json"
)


class Phase12IIntegrativeHerbalNutritionKnowledgeCapabilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_profile = phase12i_profile()
        cls.fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))

    def _profile(self):
        return copy.deepcopy(self.generated_profile)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture
        generated = self.generated_profile

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["integrative_herbal_nutrition_profile_contract_version"],
            PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["profile_kind"],
            PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
        )
        self.assertTrue(fixture["profile_id"].startswith("p12i-integrative-profile-"))
        self.assertEqual(fixture["source_phase_range"], PHASE12I_SOURCE_PHASE_RANGE)
        self.assertEqual(fixture["capability_phase"], PHASE12I_CAPABILITY_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12I_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12I_GRANT_STATUS)
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
            ],
        )
        self.assertEqual(
            [item["preference_mode_label"] for item in fixture["user_preference_modes"]],
            list(PHASE12I_USER_PREFERENCE_MODES),
        )
        self.assertEqual(
            [item["specialist_profile_label"] for item in fixture["specialist_profile_labels"]],
            list(PHASE12I_SPECIALIST_PROFILE_LABELS),
        )
        self.assertEqual(
            [item["source_class_label"] for item in fixture["source_class_labels"]],
            list(PHASE12I_SOURCE_CLASS_LABELS),
        )
        self.assertEqual(
            [item["future_gate_label"] for item in fixture["required_future_gates"]],
            list(PHASE12I_REQUIRED_FUTURE_GATES),
        )
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["non_authorizing_proof"])
        self.assertTrue(fixture["medical_safety_review_required"])
        self.assertFalse(fixture["phase12i_provides_medical_advice"])
        self.assertFalse(fixture["phase12i_authorizes_runtime"])
        self.assertFalse(fixture["phase12i_suppresses_safety_warnings"])
        self.assertTrue(fixture["emergency_escalation_preserved"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12i_profile(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12i_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12I_SOURCE_PHASE_RANGE)
        self.assertEqual(summary["capability_phase"], "knowledge-profile-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["user_preference_mode_count"], 15)
        self.assertEqual(summary["specialist_profile_label_count"], 9)
        self.assertEqual(summary["source_class_label_count"], 19)
        self.assertEqual(summary["required_future_gate_count"], 13)
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["non_authorizing_proof"])
        self.assertTrue(summary["medical_safety_review_required"])
        self.assertFalse(summary["phase12i_provides_medical_advice"])
        self.assertFalse(summary["phase12i_authorizes_runtime"])
        self.assertFalse(summary["phase12i_suppresses_safety_warnings"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_capability_labels_are_metadata_only(self):
        profile = self._profile()

        for item in profile["user_preference_modes"]:
            with self.subTest(preference=item["preference_mode_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["safety_warnings_preserved"])
                self.assertTrue(item["emergency_escalation_preserved"])
                self.assertTrue(item["preference_cannot_suppress_warnings"])
                self.assertFalse(item["medical_advice_provided"])
                self.assertFalse(item["execution_permitted"])
        for item in profile["specialist_profile_labels"]:
            with self.subTest(specialist=item["specialist_profile_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["review_profile_only"])
                self.assertFalse(item["provider_execution_granted"])
                self.assertFalse(item["model_execution_granted"])
                self.assertFalse(item["clinical_recommendation_added"])
        for item in profile["source_class_labels"]:
            with self.subTest(source_class=item["source_class_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["provenance_review_required"])
                self.assertFalse(item["ingestion_permitted"])
                self.assertFalse(item["web_scraping_permitted"])
                self.assertFalse(item["database_ingestion_permitted"])
                self.assertFalse(item["network_call_execution_granted"])

    def test_user_preferences_cannot_suppress_warnings(self):
        unsafe = self._profile()
        unsafe["phase12i_suppresses_safety_warnings"] = True
        unsafe["emergency_escalation_preserved"] = False
        unsafe["contraindication_warnings_preserved"] = False
        unsafe["medication_interaction_warnings_preserved"] = False
        unsafe["pregnancy_liver_kidney_cardiac_risk_warnings_preserved"] = False
        unsafe["eating_disorder_risk_warnings_preserved"] = False
        unsafe["toxicity_warnings_preserved"] = False
        unsafe["contamination_adulteration_warnings_preserved"] = False
        unsafe["user_preference_modes"][0]["safety_warnings_preserved"] = False
        unsafe["user_preference_modes"][0]["emergency_escalation_preserved"] = False
        unsafe["user_preference_modes"][0]["preference_cannot_suppress_warnings"] = False

        result = validate_phase12i_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.sanitized_record
        self.assertFalse(safe["phase12i_suppresses_safety_warnings"])
        self.assertTrue(safe["emergency_escalation_preserved"])
        self.assertTrue(safe["contraindication_warnings_preserved"])
        self.assertTrue(safe["medication_interaction_warnings_preserved"])
        self.assertTrue(safe["pregnancy_liver_kidney_cardiac_risk_warnings_preserved"])
        self.assertTrue(safe["eating_disorder_risk_warnings_preserved"])
        self.assertTrue(safe["toxicity_warnings_preserved"])
        self.assertTrue(safe["contamination_adulteration_warnings_preserved"])

    def test_metadata_words_never_enable_execution(self):
        finalize = phase12_contracts_module._finalize_phase12i_knowledge_capability_profile
        for wording in (
            "natural",
            "traditional",
            "herbal",
            "nutrition",
            "diet",
            "food-as-medicine",
            "approved",
            "authorized",
            "ready",
            "enabled",
            "configured",
            "specialist",
        ):
            with self.subTest(wording=wording):
                unsafe = self._profile()
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["profile_status"] = wording
                unsafe["phase12i_authorizes_runtime"] = True
                unsafe["medical_advice_provided"] = True
                unsafe["provider_execution_granted"] = True
                unsafe["model_execution_granted"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12i_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["phase12i_authorizes_runtime"])
                self.assertFalse(result.to_dict()["medical_advice_provided"])
                self.assertFalse(result.to_dict()["provider_execution_granted"])
                self.assertFalse(result.to_dict()["model_execution_granted"])
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_runtime_and_medical_action_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._profile()
                unsafe[field] = True

                result = validate_phase12i_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_hidden_medical_ingestion_and_runtime_semantics_fail_closed(self):
        profile = self._profile()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("user_preference_modes")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["integrative_herbal_nutrition_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(profile)
        nested_unknown["source_class_labels"][0]["runner"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "medical-action": ("medical_boundary_statement", "clinical recommendation"),
            "diagnosis": ("medical_boundary_statement", "diagnosis"),
            "treatment-plan": ("medical_boundary_statement", "treatment plan"),
            "herb-dosing": ("medical_boundary_statement", "herb dosing"),
            "supplement-dosing": ("medical_boundary_statement", "supplement dosing"),
            "calorie-prescription": ("medical_boundary_statement", "calorie prescription"),
            "unsafe-fasting": ("medical_boundary_statement", "unsafe fasting"),
            "western-invalid": (
                "western_medicine_boundary_statement",
                "western medicine is invalid",
            ),
            "natural-safe": ("natural_remedy_boundary_statement", "natural remedies are safe"),
            "food-cure": ("food_cure_boundary_statement", "food cures disease"),
            "suppress-emergency": (
                "safety_warning_preservation_statement",
                "suppress emergency escalation",
            ),
            "database-ingestion": ("medical_boundary_statement", "database ingestion"),
            "web-scraping": ("medical_boundary_statement", "web scraping"),
            "network-call": ("medical_boundary_statement", "network call"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(profile)
            payload[field] = value
            cases.append((name, payload))

        source_id = copy.deepcopy(profile)
        source_id["source_phase_references"][0]["source_id"] = "source_id"
        cases.append(("source-id", source_id))

        raw_payload = copy.deepcopy(profile)
        raw_payload["source_class_labels"][0]["source_class_label"] = "raw_csi"
        cases.append(("raw-sensor", raw_payload))

        url_payload = copy.deepcopy(profile)
        url_payload["source_class_labels"][0]["source_class_label"] = "https://example.invalid"
        cases.append(("url", url_payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12i_profile(payload)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["phase12i_provides_medical_advice"])
                self.assertFalse(result.to_dict()["phase12i_authorizes_runtime"])
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
        )
        for payload, validator in phase12_sources:
            with self.subTest(kind=payload.get("profile_kind") or payload.get("matrix_kind")):
                result = validator(payload)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12i_module_does_not_add_runtime_imports_or_true_flags(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "import fastapi",
            "from fastapi",
            "import django",
            "from django",
            "import flask",
            "from flask",
            "import sqlalchemy",
            "from sqlalchemy",
            "import requests",
            "from requests",
            "urllib.",
            "socket.",
            "subprocess.",
            "bs4",
            "beautifulsoup",
            "selenium",
            "playwright",
            "scrapy",
            '"execution_permitted": true',
            '"real_mode_runtime_enabled": true',
            '"provider_execution_granted": true',
            '"model_execution_granted": true',
            '"database_ingestion_added": true',
            '"web_scraping_added": true',
            '"secure_drop_send_permitted": true',
            '"secure_drop_receive_permitted": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
            "medical_advice_provided",
            "clinical_decision_support_added",
            "clinical_recommendation_added",
            "diagnosis_provided",
            "treatment_plan_provided",
            "prescribing_added",
            "supplement_recommendation_added",
            "herb_dosing_added",
            "supplement_dosing_added",
            "calorie_macro_prescription_added",
            "weight_loss_target_prescription_added",
            "unsafe_fasting_weight_loss_advice_added",
            "nutrition_prescription_added",
            "database_ingestion_added",
            "web_scraping_added",
            "network_call_execution_granted",
            "runtime_model_execution_granted",
            "provider_execution_granted",
            "model_execution_granted",
            "active_grant_present",
            "runtime_adapter_execution_granted",
            "real_mode_authorization_added",
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
