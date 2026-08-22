import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12Q_DEFAULT_DECISION_REASON_CODE,
    PHASE12Q_DEFAULT_DECISION_STATUS,
    PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
    PHASE12R_AUTHORIZATION_STATUS,
    PHASE12R_GRANT_STATUS,
    PHASE12R_REQUIRED_FUTURE_GATES,
    PHASE12R_REQUIRED_REVIEWER_CLASSES,
    PHASE12R_SOURCE_PHASE_RANGE,
    PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_CONTRACT_VERSION,
    PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
    PHASE12R_WORKFLOW_MODES,
)

phase12r_index = phase12_contracts_module.phase12r_workflow_mode_review_audit_trail_index
PHASE12R_STATUS_SUMMARY_ATTR = "phase12r_workflow_mode_review_audit_trail_index_status_summary"
phase12r_status_summary = getattr(phase12_contracts_module, PHASE12R_STATUS_SUMMARY_ATTR)
PHASE12R_VALIDATE_ATTR = "validate_phase12r_workflow_mode_review_audit_trail_index"
validate_phase12r_index = getattr(phase12_contracts_module, PHASE12R_VALIDATE_ATTR)

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_TRAIL_INDEX_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-12r-workflow-mode-review-audit-trail-index-v1.json"
)


class Phase12RWorkflowModeReviewAuditTrailIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_index = phase12r_index()
        cls.fixture = json.loads(AUDIT_TRAIL_INDEX_FIXTURE.read_text(encoding="utf-8"))

    def _index(self):
        return copy.deepcopy(self.generated_index)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture

        self.assertEqual(fixture, self.generated_index)
        self.assertEqual(
            fixture["workflow_mode_review_audit_trail_index_contract_version"],
            PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["audit_trail_index_kind"],
            PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
        )
        self.assertTrue(
            fixture["audit_trail_index_id"].startswith(
                "p12r-workflow-mode-review-audit-trail-index-"
            )
        )
        self.assertEqual(fixture["source_phase_range"], PHASE12R_SOURCE_PHASE_RANGE)
        self.assertEqual(fixture["audit_trail_index_phase"], PHASE12R_AUDIT_TRAIL_INDEX_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12R_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12R_GRANT_STATUS)
        self.assertEqual(fixture["decision_status"], PHASE12Q_DEFAULT_DECISION_STATUS)
        self.assertEqual(fixture["decision_reason_code"], PHASE12Q_DEFAULT_DECISION_REASON_CODE)
        self.assertEqual(
            [item["source_phase_label"] for item in fixture["source_phase_references"]],
            ["12N", "12O", "12P", "12Q"],
        )
        self.assertEqual(
            [item["workflow_mode_label"] for item in fixture["indexed_workflow_modes"]],
            list(PHASE12R_WORKFLOW_MODES),
        )
        self.assertTrue(
            fixture["activation_request_packet_reference_metadata"][
                "activation_request_packet_id"
            ].startswith("p12p-workflow-mode-review-packet-")
        )
        self.assertTrue(
            fixture["review_decision_record_reference_metadata"]["decision_record_id"].startswith(
                "p12q-workflow-mode-review-decision-"
            )
        )
        self.assertEqual(fixture["source_phase_reference_count"], 4)
        self.assertEqual(fixture["indexed_workflow_mode_count"], 3)
        self.assertEqual(fixture["required_future_gate_count"], 11)
        self.assertEqual(fixture["unsatisfied_gate_count"], 11)
        self.assertEqual(fixture["blocker_count"], 15)
        self.assertEqual(fixture["stale_count"], 0)
        self.assertEqual(fixture["review_needed_count"], 1)
        self.assertEqual(fixture["reviewer_class_required_count"], 4)
        self.assertEqual(fixture["reviewer_class_represented_count"], 0)
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["workflow_mode_review_audit_trail_index_only"])
        self.assertTrue(fixture["not_authorized"])
        self.assertTrue(fixture["no_active_grant"])
        self.assertTrue(fixture["no_runtime_authorization"])
        self.assertTrue(fixture["no_execution_permission"])
        self.assertTrue(fixture["runtime_authorization_not_granted"])
        self.assertTrue(fixture["workflow_mode_activation_not_permitted"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12r_index(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12r_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12R_SOURCE_PHASE_RANGE)
        self.assertEqual(
            summary["audit_trail_index_phase"],
            "workflow-mode-review-audit-trail-index-only",
        )
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["decision_status"], "review-not-submitted")
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["workflow_mode_review_audit_trail_index_only"])
        self.assertTrue(summary["runtime_authorization_not_granted"])
        self.assertTrue(summary["workflow_mode_activation_not_permitted"])
        self.assertFalse(summary["phase12r_authorizes_runtime"])
        self.assertFalse(summary["phase12r_creates_active_grant"])
        self.assertFalse(summary["phase12r_grants_execution_permission"])
        self.assertFalse(summary["phase12r_allows_workflow_activation"])
        self.assertFalse(summary["phase12r_allows_workflow_execution"])
        self.assertFalse(summary["phase12r_allows_model_routing"])
        self.assertFalse(summary["phase12r_allows_provider_execution"])
        self.assertFalse(summary["phase12r_allows_code_execution"])
        self.assertFalse(summary["phase12r_allows_shell_execution"])
        self.assertFalse(summary["phase12r_allows_process_execution"])
        self.assertFalse(summary["phase12r_allows_database_writes"])
        self.assertFalse(summary["phase12r_allows_query_execution"])
        self.assertFalse(summary["phase12r_allows_network_calls"])
        self.assertFalse(summary["phase12r_allows_private_health_data_processing"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self.assertFalse(summary["production_ready"])

    def test_audit_index_covers_sources_modes_reviewers_and_decision_status(self):
        index = self._index()

        self.assertEqual(
            [item["source_phase_label"] for item in index["source_phase_references"]],
            ["12N", "12O", "12P", "12Q"],
        )
        for reference in index["source_phase_references"]:
            with self.subTest(reference=reference["source_phase_label"]):
                self.assertTrue(reference["metadata_only"])
                self.assertEqual(reference["runtime_stage"], "not-implemented")
                self.assertFalse(reference["execution_permitted"])
                self.assertFalse(reference["real_mode_runtime_enabled"])

        for mode in index["indexed_workflow_modes"]:
            with self.subTest(mode=mode["workflow_mode_label"]):
                self.assertTrue(mode["metadata_only"])
                self.assertTrue(mode["indexed_for_audit_only"])
                self.assertTrue(mode["workflow_mode_activation_not_permitted"])
                self.assertEqual(
                    mode["required_future_gate_count"],
                    len(PHASE12R_REQUIRED_FUTURE_GATES),
                )
                self.assertEqual(
                    mode["unsatisfied_gate_count"],
                    len(PHASE12R_REQUIRED_FUTURE_GATES),
                )
                self.assertFalse(mode["workflow_execution_permitted"])
                self.assertFalse(mode["workflow_mode_execution_permitted"])
                self.assertFalse(mode["model_routing_execution_permitted"])
                self.assertFalse(mode["provider_execution_granted"])
                self.assertFalse(mode["code_execution_permitted"])
                self.assertFalse(mode["experiment_execution_permitted"])
                self.assertFalse(mode["execution_permitted"])

        packet_reference = index["activation_request_packet_reference_metadata"]
        self.assertEqual(packet_reference["source_phase_label"], "12P")
        self.assertTrue(packet_reference["metadata_only"])
        self.assertTrue(packet_reference["workflow_mode_activation_not_permitted"])
        self.assertFalse(packet_reference["execution_permitted"])

        decision_reference = index["review_decision_record_reference_metadata"]
        self.assertEqual(decision_reference["source_phase_label"], "12Q")
        self.assertTrue(decision_reference["runtime_authorization_not_granted"])
        self.assertTrue(decision_reference["workflow_mode_activation_not_permitted"])
        self.assertFalse(decision_reference["execution_permitted"])

        decision_summary = index["decision_status_summary"]
        self.assertEqual(decision_summary["decision_status"], "review-not-submitted")
        self.assertTrue(decision_summary["request_review_not_submitted"])
        self.assertFalse(decision_summary["request_review_blocked"])
        self.assertFalse(decision_summary["request_review_complete_no_runtime_authorization"])
        self.assertFalse(decision_summary["execution_permitted"])

        self.assertEqual(
            [item["reviewer_class_label"] for item in index["reviewer_classes_required"]],
            list(PHASE12R_REQUIRED_REVIEWER_CLASSES),
        )
        self.assertEqual(
            [item["reviewer_class_label"] for item in index["reviewer_classes_represented"]],
            list(PHASE12R_REQUIRED_REVIEWER_CLASSES),
        )
        for reviewer in index["reviewer_classes_required"]:
            with self.subTest(required=reviewer["reviewer_class_label"]):
                self.assertTrue(reviewer["required"])
                self.assertFalse(reviewer["execution_permitted"])
        for reviewer in index["reviewer_classes_represented"]:
            with self.subTest(represented=reviewer["reviewer_class_label"]):
                self.assertFalse(reviewer["represented"])
                self.assertFalse(reviewer["execution_permitted"])

    def test_unsafe_fields_and_wording_fail_closed_with_sanitized_false_output(self):
        index = self._index()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(index)
        missing.pop("source_phase_references")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(index)
        unsupported["workflow_mode_review_audit_trail_index_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(index)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(index)
        nested_unknown["indexed_workflow_modes"][0]["runtime_approval"] = "approved"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "approval-for-runtime": ("audit_trail_index_status", "approved-for-runtime"),
            "activation": ("audit_trail_boundary_statement", "activation approved"),
            "enablement": ("audit_trail_boundary_statement", "mode enablement ready"),
            "grant": ("grant_status", "active-grant-created"),
            "runtime": ("audit_trail_boundary_statement", "runtime authorization granted"),
            "workflow-execution": ("audit_trail_boundary_statement", "workflow execution"),
            "model-routing": ("audit_trail_boundary_statement", "model routing"),
            "provider-execution": ("audit_trail_boundary_statement", "provider execution"),
            "code-execution": ("audit_trail_boundary_statement", "code execution"),
            "experiment-execution": ("audit_trail_boundary_statement", "experiment execution"),
            "shell-execution": ("audit_trail_boundary_statement", "shell execution"),
            "process-execution": ("audit_trail_boundary_statement", "process execution"),
            "cache-runtime": ("audit_trail_boundary_statement", "cache runtime"),
            "database-write": ("audit_trail_boundary_statement", "database writes"),
            "query-execution": ("audit_trail_boundary_statement", "query execution"),
            "network-call": ("audit_trail_boundary_statement", "network call"),
            "clinical": ("medical_privacy_boundary_statement", "clinical use"),
            "private-health": (
                "medical_privacy_boundary_statement",
                "private health data processing",
            ),
            "diagnosis": ("medical_privacy_boundary_statement", "diagnosis"),
            "medical-advice": ("medical_privacy_boundary_statement", "medical advice"),
            "production-ready": ("audit_trail_boundary_statement", "production ready"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(index)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12r_index(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12r_authorizes_runtime"])
                self.assertFalse(safe["phase12r_creates_active_grant"])
                self.assertFalse(safe["phase12r_grants_execution_permission"])
                self.assertFalse(safe["phase12r_allows_workflow_activation"])
                self.assertFalse(safe["phase12r_allows_workflow_execution"])
                self.assertFalse(safe["phase12r_allows_model_routing"])
                self.assertFalse(safe["phase12r_allows_provider_execution"])
                self.assertFalse(safe["phase12r_allows_code_execution"])
                self.assertFalse(safe["phase12r_allows_shell_execution"])
                self.assertFalse(safe["phase12r_allows_process_execution"])
                self.assertFalse(safe["phase12r_allows_database_writes"])
                self.assertFalse(safe["phase12r_allows_query_execution"])
                self.assertFalse(safe["phase12r_allows_network_calls"])
                self.assertFalse(safe["phase12r_allows_clinical_decision_support"])
                self.assertFalse(safe["phase12r_allows_private_health_data_processing"])
                self.assertFalse(safe["active_grant_present"])
                self.assertFalse(safe["runtime_authorization_granted"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_review_and_nested_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._index()
                unsafe[field] = True

                result = validate_phase12r_index(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

        for path in (
            ("indexed_workflow_modes", 0, "workflow_execution_permitted"),
            ("indexed_workflow_modes", 0, "model_routing_execution_permitted"),
            ("indexed_workflow_modes", 0, "provider_execution_granted"),
            (
                "activation_request_packet_reference_metadata",
                "workflow_mode_activation_not_permitted",
                False,
            ),
            (
                "review_decision_record_reference_metadata",
                "runtime_authorization_not_granted",
                False,
            ),
            ("decision_status_summary", "request_review_not_submitted", False),
            ("reviewer_classes_represented", 0, "represented"),
        ):
            with self.subTest(path=path):
                unsafe = self._index()
                if len(path) == 4:
                    unsafe[path[0]][path[1]][path[2]] = True
                elif len(path) == 3 and isinstance(path[1], int):
                    unsafe[path[0]][path[1]][path[2]] = True
                else:
                    unsafe[path[0]][path[1]] = path[2]

                result = validate_phase12r_index(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record["execution_permitted"])

    def test_phase12r_module_does_not_add_runtime_imports_or_true_flags(self):
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
            '"model_execution_granted": true',
            '"code_execution_permitted": true',
            '"experiment_execution_permitted": true',
            '"autonomous_experimentation_permitted": true',
            '"shell_execution_permitted": true',
            '"process_execution_permitted": true',
            '"database_write_permitted": true',
            '"query_execution_permitted": true',
            '"cache_event_bus_runtime_added": true',
            '"pubsub_runtime_added": true',
            '"network_call_execution_granted": true',
            '"clinical_decision_support_allowed": true',
            '"private_health_data_allowed": true',
            '"active_grant_present": true',
            '"runtime_authorization_granted": true',
            '"approval_for_runtime_present": true',
            '"production_ready": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
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
            "experiment_execution_permitted",
            "autonomous_experimentation_permitted",
            "shell_execution_permitted",
            "process_execution_permitted",
            "web_access_permitted",
            "database_ingestion_added",
            "database_write_permitted",
            "query_execution_permitted",
            "cache_event_bus_runtime_added",
            "pubsub_runtime_added",
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
            "production_ready",
            "execution_permitted",
            "real_mode_runtime_enabled",
        )


if __name__ == "__main__":
    unittest.main()
