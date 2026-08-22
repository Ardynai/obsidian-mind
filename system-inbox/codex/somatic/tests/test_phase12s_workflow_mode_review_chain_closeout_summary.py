import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12S_AUTHORIZATION_STATUS,
    PHASE12S_CLOSEOUT_STATUSES,
    PHASE12S_CLOSEOUT_SUMMARY_PHASE,
    PHASE12S_DEFAULT_CLOSEOUT_STATUS,
    PHASE12S_GRANT_STATUS,
    PHASE12S_SOURCE_PHASE_RANGE,
    PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT_VERSION,
    PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND,
    PHASE12S_WORKFLOW_MODES,
)

phase12s_summary = phase12_contracts_module.phase12s_workflow_mode_review_chain_closeout_summary
phase12s_status_summary = (
    phase12_contracts_module.phase12s_workflow_mode_review_chain_closeout_summary_status_summary
)
validate_phase12s_summary = (
    phase12_contracts_module.validate_phase12s_workflow_mode_review_chain_closeout_summary
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT_SUMMARY_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12s-workflow-mode-review-chain-closeout-summary-v1.json"
)


class Phase12SWorkflowModeReviewChainCloseoutSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_summary = phase12s_summary()
        cls.fixture = json.loads(CLOSEOUT_SUMMARY_FIXTURE.read_text(encoding="utf-8"))

    def _summary(self):
        return copy.deepcopy(self.generated_summary)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture

        self.assertEqual(fixture, self.generated_summary)
        self.assertEqual(
            fixture["workflow_mode_review_chain_closeout_summary_contract_version"],
            PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["closeout_summary_kind"],
            PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND,
        )
        self.assertTrue(
            fixture["closeout_summary_id"].startswith(
                "p12s-workflow-mode-review-chain-closeout-summary-"
            )
        )
        self.assertEqual(fixture["source_phase_range"], PHASE12S_SOURCE_PHASE_RANGE)
        self.assertEqual(fixture["closeout_summary_phase"], PHASE12S_CLOSEOUT_SUMMARY_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12S_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12S_GRANT_STATUS)
        self.assertEqual(fixture["closeout_status"], PHASE12S_DEFAULT_CLOSEOUT_STATUS)
        self.assertEqual(
            [item["source_phase_label"] for item in fixture["source_phase_references"]],
            ["12N", "12O", "12P", "12Q", "12R"],
        )
        self.assertEqual(
            [item["workflow_mode_label"] for item in fixture["workflow_mode_labels_covered"]],
            list(PHASE12S_WORKFLOW_MODES),
        )
        self.assertEqual(fixture["source_phase_reference_count"], 5)
        self.assertEqual(fixture["workflow_mode_label_count"], 3)
        self.assertEqual(fixture["future_gate_count"], 11)
        self.assertEqual(fixture["unsatisfied_gate_count"], 11)
        self.assertEqual(fixture["blocker_count"], 15)
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["workflow_mode_review_chain_closeout_summary_only"])
        self.assertTrue(fixture["standalone_first"])
        self.assertTrue(fixture["non_authorizing_proof"])
        self.assertTrue(fixture["not_authorized"])
        self.assertTrue(fixture["no_active_grant"])
        self.assertTrue(fixture["no_runtime_authorization"])
        self.assertTrue(fixture["no_execution_permission"])
        self.assertTrue(fixture["runtime_authorization_not_granted"])
        self.assertTrue(fixture["workflow_mode_activation_not_permitted"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12s_summary(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12s_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12S_SOURCE_PHASE_RANGE)
        self.assertEqual(summary["closeout_summary_phase"], PHASE12S_CLOSEOUT_SUMMARY_PHASE)
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["workflow_mode_review_chain_closeout_summary_only"])
        self.assertTrue(summary["runtime_authorization_not_granted"])
        self.assertTrue(summary["workflow_mode_activation_not_permitted"])
        self.assertFalse(summary["phase12s_authorizes_runtime"])
        self.assertFalse(summary["phase12s_creates_active_grant"])
        self.assertFalse(summary["phase12s_grants_execution_permission"])
        self.assertFalse(summary["phase12s_allows_workflow_activation"])
        self.assertFalse(summary["phase12s_allows_workflow_execution"])
        self.assertFalse(summary["phase12s_allows_model_routing"])
        self.assertFalse(summary["phase12s_allows_provider_execution"])
        self.assertFalse(summary["phase12s_allows_code_execution"])
        self.assertFalse(summary["phase12s_allows_shell_execution"])
        self.assertFalse(summary["phase12s_allows_process_execution"])
        self.assertFalse(summary["phase12s_allows_network_behavior"])
        self.assertFalse(summary["phase12s_allows_transport_implementation"])
        self.assertFalse(summary["phase12s_allows_fabric_implementation"])
        self.assertFalse(summary["phase12s_allows_p2p_implementation"])
        self.assertFalse(summary["phase12s_allows_private_health_data_processing"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self.assertFalse(summary["production_ready"])

    def test_sources_and_workflow_mode_coverage_are_non_executing(self):
        summary = self._summary()

        for reference in summary["source_phase_references"]:
            with self.subTest(reference=reference["source_phase_label"]):
                self.assertTrue(reference["metadata_only"])
                self.assertEqual(reference["runtime_stage"], "not-implemented")
                self.assertFalse(reference["execution_permitted"])
                self.assertFalse(reference["real_mode_runtime_enabled"])

        for mode in summary["workflow_mode_labels_covered"]:
            with self.subTest(mode=mode["workflow_mode_label"]):
                self.assertTrue(mode["metadata_only"])
                self.assertTrue(mode["covered_for_closeout_only"])
                self.assertTrue(mode["workflow_mode_activation_not_permitted"])
                self.assertFalse(mode["workflow_execution_permitted"])
                self.assertFalse(mode["workflow_mode_execution_permitted"])
                self.assertFalse(mode["model_routing_execution_permitted"])
                self.assertFalse(mode["provider_execution_granted"])
                self.assertFalse(mode["code_execution_permitted"])
                self.assertFalse(mode["shell_execution_permitted"])
                self.assertFalse(mode["process_execution_permitted"])
                self.assertFalse(mode["experiment_execution_permitted"])
                self.assertFalse(mode["clinical_decision_support_allowed"])
                self.assertFalse(mode["private_health_data_allowed"])
                self.assertFalse(mode["execution_permitted"])

    def test_allowed_closeout_statuses_remain_non_authorizing(self):
        for status in PHASE12S_CLOSEOUT_STATUSES:
            with self.subTest(status=status):
                payload = self._summary()
                payload["closeout_status"] = status
                payload = phase12_contracts_module._finalize_phase12s_closeout_summary(payload)

                result = validate_phase12s_summary(payload)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(result.sanitized_record["closeout_status"], status)
                self.assertFalse(result.sanitized_record["execution_permitted"])
                self.assertFalse(result.sanitized_record["runtime_authorization_granted"])
                self.assertFalse(result.sanitized_record["workflow_mode_activation_permitted"])

    def test_unsafe_fields_and_wording_fail_closed_with_sanitized_false_output(self):
        summary = self._summary()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(summary)
        missing.pop("source_phase_references")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(summary)
        unsupported["workflow_mode_review_chain_closeout_summary_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(summary)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(summary)
        nested_unknown["workflow_mode_labels_covered"][0]["runtime_approval"] = "approved"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "approval-for-runtime": ("closeout_status", "approved-for-runtime"),
            "activation": ("closeout_boundary_statement", "activation approved"),
            "enablement": ("closeout_boundary_statement", "mode enablement ready"),
            "grant": ("grant_status", "active-grant-created"),
            "runtime": ("closeout_boundary_statement", "runtime authorization granted"),
            "workflow-execution": ("closeout_boundary_statement", "workflow execution"),
            "model-routing": ("closeout_boundary_statement", "model routing"),
            "provider-execution": ("closeout_boundary_statement", "provider execution"),
            "code-execution": ("closeout_boundary_statement", "code execution"),
            "shell-execution": ("closeout_boundary_statement", "shell execution"),
            "process-execution": ("closeout_boundary_statement", "process execution"),
            "experiment-execution": ("closeout_boundary_statement", "experiment execution"),
            "network": ("closeout_boundary_statement", "network behavior"),
            "database": ("closeout_boundary_statement", "database writes"),
            "query-execution": ("closeout_boundary_statement", "query execution"),
            "cache-runtime": ("closeout_boundary_statement", "cache runtime"),
            "transport": ("closeout_boundary_statement", "transport implementation"),
            "fabric": ("closeout_boundary_statement", "fabric implementation"),
            "p2p": ("closeout_boundary_statement", "P2P implementation"),
            "clinical": ("medical_privacy_boundary_statement", "clinical use"),
            "private-health": (
                "medical_privacy_boundary_statement",
                "private health data processing",
            ),
            "diagnosis": ("medical_privacy_boundary_statement", "diagnosis"),
            "medical-advice": ("medical_privacy_boundary_statement", "medical advice"),
            "deployment-ready": ("closeout_boundary_statement", "deployment ready"),
            "production-ready": ("closeout_boundary_statement", "production ready"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(summary)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12s_summary(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12s_authorizes_runtime"])
                self.assertFalse(safe["phase12s_creates_active_grant"])
                self.assertFalse(safe["phase12s_grants_execution_permission"])
                self.assertFalse(safe["phase12s_allows_workflow_activation"])
                self.assertFalse(safe["phase12s_allows_workflow_execution"])
                self.assertFalse(safe["phase12s_allows_model_routing"])
                self.assertFalse(safe["phase12s_allows_provider_execution"])
                self.assertFalse(safe["phase12s_allows_code_execution"])
                self.assertFalse(safe["phase12s_allows_shell_execution"])
                self.assertFalse(safe["phase12s_allows_process_execution"])
                self.assertFalse(safe["phase12s_allows_network_behavior"])
                self.assertFalse(safe["phase12s_allows_transport_implementation"])
                self.assertFalse(safe["phase12s_allows_fabric_implementation"])
                self.assertFalse(safe["phase12s_allows_p2p_implementation"])
                self.assertFalse(safe["phase12s_allows_clinical_decision_support"])
                self.assertFalse(safe["phase12s_allows_private_health_data_processing"])
                self.assertFalse(safe["deployment_ready"])
                self.assertFalse(safe["production_ready"])
                self.assertFalse(safe["active_grant_present"])
                self.assertFalse(safe["runtime_authorization_granted"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_and_nested_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._summary()
                unsafe[field] = True

                result = validate_phase12s_summary(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

        for path in (
            ("workflow_mode_labels_covered", 0, "workflow_execution_permitted"),
            ("workflow_mode_labels_covered", 0, "model_routing_execution_permitted"),
            ("workflow_mode_labels_covered", 0, "provider_execution_granted"),
            ("workflow_mode_labels_covered", 0, "shell_execution_permitted"),
            ("workflow_mode_labels_covered", 0, "process_execution_permitted"),
            ("workflow_mode_labels_covered", 0, "private_health_data_allowed"),
            ("source_phase_references", 0, "execution_permitted"),
            ("source_phase_references", 4, "real_mode_runtime_enabled"),
        ):
            with self.subTest(path=path):
                unsafe = self._summary()
                unsafe[path[0]][path[1]][path[2]] = True

                result = validate_phase12s_summary(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record["execution_permitted"])

    def test_phase12s_module_does_not_add_runtime_imports_or_true_flags(self):
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
            '"workflow_execution_permitted": true',
            '"workflow_mode_execution_permitted": true',
            '"workflow_mode_activation_permitted": true',
            '"model_routing_execution_permitted": true',
            '"provider_execution_granted": true',
            '"code_execution_permitted": true',
            '"shell_execution_permitted": true',
            '"process_execution_permitted": true',
            '"experiment_execution_permitted": true',
            '"autonomous_experimentation_permitted": true',
            '"web_access_permitted": true',
            '"network_behavior_added": true',
            '"database_ingestion_added": true',
            '"database_write_permitted": true',
            '"query_execution_permitted": true',
            '"cache_event_bus_runtime_added": true',
            '"transport_implementation_added": true',
            '"fabric_implementation_added": true',
            '"p2p_implementation_added": true',
            '"clinical_decision_support_allowed": true',
            '"private_health_data_allowed": true',
            '"deployment_ready": true',
            '"production_ready": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    def _runtime_false_fields(self):
        return tuple(
            field
            for field, value in self.generated_summary.items()
            if (field.startswith("phase12s_") and value is False)
            or field
            in {
                "workflow_execution_permitted",
                "workflow_mode_execution_permitted",
                "workflow_mode_activation_permitted",
                "runtime_adapter_execution_granted",
                "model_routing_execution_permitted",
                "provider_execution_granted",
                "model_execution_granted",
                "model_loading_added",
                "training_permitted",
                "fine_tuning_permitted",
                "code_execution_permitted",
                "shell_execution_permitted",
                "process_execution_permitted",
                "experiment_execution_permitted",
                "autonomous_experimentation_permitted",
                "web_access_permitted",
                "network_behavior_added",
                "database_ingestion_added",
                "database_write_permitted",
                "query_execution_permitted",
                "cache_event_bus_runtime_added",
                "pubsub_runtime_added",
                "transport_implementation_added",
                "fabric_implementation_added",
                "p2p_implementation_added",
                "web_scraping_added",
                "network_call_execution_granted",
                "clinical_decision_support_allowed",
                "clinical_decision_support_added",
                "diagnosis_provided",
                "treatment_plan_provided",
                "medical_advice_provided",
                "dosing_added",
                "nutrition_prescription_added",
                "private_health_data_allowed",
                "private_health_data_processing_added",
                "device_access_granted",
                "sensor_access_granted",
                "raw_sensor_processing_added",
                "active_grant_present",
                "runtime_authorization_granted",
                "real_mode_authorization_added",
                "approval_for_runtime_present",
                "deployment_ready",
                "production_ready",
                "execution_permitted",
                "real_mode_runtime_enabled",
            }
        )


if __name__ == "__main__":
    unittest.main()
