import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12Q_AUTHORIZATION_STATUS,
    PHASE12Q_DECISION_RECORD_PHASE,
    PHASE12Q_DECISION_STATUSES,
    PHASE12Q_DEFAULT_DECISION_REASON_CODE,
    PHASE12Q_DEFAULT_DECISION_STATUS,
    PHASE12Q_GRANT_STATUS,
    PHASE12Q_REQUIRED_FUTURE_GATES,
    PHASE12Q_REQUIRED_REVIEWER_CLASSES,
    PHASE12Q_SOURCE_PHASE_RANGE,
    PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_CONTRACT_VERSION,
    PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
    PHASE12Q_WORKFLOW_MODES,
)

phase12q_record = (
    phase12_contracts_module.phase12q_non_authorizing_workflow_mode_review_decision_record
)
PHASE12Q_STATUS_SUMMARY_ATTR = (
    "phase12q_non_authorizing_workflow_mode_review_decision_record_status_summary"
)
phase12q_status_summary = getattr(phase12_contracts_module, PHASE12Q_STATUS_SUMMARY_ATTR)
PHASE12Q_VALIDATE_ATTR = "validate_phase12q_non_authorizing_workflow_mode_review_decision_record"
validate_phase12q_record = getattr(phase12_contracts_module, PHASE12Q_VALIDATE_ATTR)

REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_RECORD_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12q-non-authorizing-workflow-mode-review-decision-record-v1.json"
)


class Phase12QWorkflowModeReviewDecisionRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_record = phase12q_record()
        cls.fixture = json.loads(DECISION_RECORD_FIXTURE.read_text(encoding="utf-8"))

    def _record(self):
        return copy.deepcopy(self.generated_record)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture

        self.assertEqual(fixture, self.generated_record)
        self.assertEqual(
            fixture["workflow_mode_review_decision_record_contract_version"],
            PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["decision_record_kind"],
            PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        )
        self.assertTrue(
            fixture["decision_record_id"].startswith("p12q-workflow-mode-review-decision-")
        )
        self.assertEqual(fixture["source_phase_range"], PHASE12Q_SOURCE_PHASE_RANGE)
        self.assertEqual(fixture["decision_record_phase"], PHASE12Q_DECISION_RECORD_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12Q_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12Q_GRANT_STATUS)
        self.assertEqual(fixture["decision_status"], PHASE12Q_DEFAULT_DECISION_STATUS)
        self.assertEqual(fixture["decision_reason_code"], PHASE12Q_DEFAULT_DECISION_REASON_CODE)
        self.assertEqual(fixture["requested_workflow_mode_label"], PHASE12Q_WORKFLOW_MODES[0])
        self.assertEqual(
            [item["source_phase_label"] for item in fixture["source_phase_references"]],
            ["12N", "12O", "12P"],
        )
        self.assertTrue(
            fixture["source_activation_request_packet_id"].startswith(
                "p12p-workflow-mode-review-packet-"
            )
        )
        self.assertEqual(fixture["required_future_gate_count"], 11)
        self.assertEqual(fixture["unsatisfied_gate_count"], 11)
        self.assertEqual(fixture["blocker_count"], 15)
        self.assertEqual(fixture["reviewer_class_required_count"], 4)
        self.assertEqual(fixture["reviewer_class_represented_count"], 0)
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["review_decision_record_only"])
        self.assertTrue(fixture["not_authorized"])
        self.assertTrue(fixture["no_active_grant"])
        self.assertTrue(fixture["no_runtime_authorization"])
        self.assertTrue(fixture["no_execution_permission"])
        self.assertTrue(fixture["runtime_authorization_not_granted"])
        self.assertTrue(fixture["workflow_mode_activation_not_permitted"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12q_record(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12q_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12Q_SOURCE_PHASE_RANGE)
        self.assertEqual(summary["decision_record_phase"], "review-decision-record-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["decision_status"], "review-not-submitted")
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["review_decision_record_only"])
        self.assertTrue(summary["runtime_authorization_not_granted"])
        self.assertTrue(summary["workflow_mode_activation_not_permitted"])
        self.assertFalse(summary["phase12q_authorizes_runtime"])
        self.assertFalse(summary["phase12q_creates_active_grant"])
        self.assertFalse(summary["phase12q_grants_execution_permission"])
        self.assertFalse(summary["phase12q_allows_workflow_activation"])
        self.assertFalse(summary["phase12q_allows_workflow_execution"])
        self.assertFalse(summary["phase12q_allows_workflow_mode_execution"])
        self.assertFalse(summary["phase12q_allows_model_routing"])
        self.assertFalse(summary["phase12q_allows_provider_execution"])
        self.assertFalse(summary["phase12q_allows_code_execution"])
        self.assertFalse(summary["phase12q_allows_experiment_execution"])
        self.assertFalse(summary["phase12q_allows_private_health_data_processing"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self.assertFalse(summary["production_ready"])

    def test_future_gates_and_reviewers_remain_unsatisfied(self):
        record = self._record()

        self.assertEqual(
            [item["future_gate_label"] for item in record["required_future_gates_snapshot"]],
            list(PHASE12Q_REQUIRED_FUTURE_GATES),
        )
        for gate in record["required_future_gates_snapshot"]:
            with self.subTest(gate=gate["future_gate_label"]):
                self.assertTrue(gate["metadata_only"])
                self.assertTrue(gate["blocks_runtime_authorization"])
                self.assertFalse(gate["satisfied"])
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["review_completed"])
                self.assertFalse(gate["execution_permitted"])

        self.assertEqual(
            [item["reviewer_class_label"] for item in record["reviewer_classes_required"]],
            list(PHASE12Q_REQUIRED_REVIEWER_CLASSES),
        )
        self.assertEqual(
            [item["reviewer_class_label"] for item in record["reviewer_classes_represented"]],
            list(PHASE12Q_REQUIRED_REVIEWER_CLASSES),
        )
        for reviewer in record["reviewer_classes_required"]:
            with self.subTest(required=reviewer["reviewer_class_label"]):
                self.assertTrue(reviewer["required"])
                self.assertFalse(reviewer["execution_permitted"])
        for reviewer in record["reviewer_classes_represented"]:
            with self.subTest(represented=reviewer["reviewer_class_label"]):
                self.assertFalse(reviewer["represented"])
                self.assertFalse(reviewer["execution_permitted"])

    def test_allowed_decision_statuses_are_non_authorizing(self):
        finalize = phase12_contracts_module._finalize_phase12q_decision_record
        status_reason_codes = phase12_contracts_module.PHASE12Q_DECISION_STATUS_REASON_CODES
        status_dispositions = phase12_contracts_module.PHASE12Q_DECISION_STATUS_DISPOSITIONS

        for status in PHASE12Q_DECISION_STATUSES:
            with self.subTest(status=status):
                record = self._record()
                record["decision_status"] = status
                record["decision_reason_code"] = status_reason_codes[status]
                record["request_disposition_status"] = status_dispositions[status]
                finalized = finalize(record)
                result = validate_phase12q_record(finalized)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(finalized["decision_status"], status)
                self.assertFalse(finalized["phase12q_authorizes_runtime"])
                self.assertFalse(finalized["phase12q_grants_execution_permission"])
                self.assertFalse(finalized["workflow_mode_activation_permitted"])
                self.assertFalse(finalized["execution_permitted"])
                self.assertFalse(finalized["real_mode_runtime_enabled"])

    def test_unsafe_fields_and_wording_fail_closed_with_sanitized_false_output(self):
        record = self._record()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(record)
        missing.pop("required_future_gates_snapshot")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(record)
        unsupported["workflow_mode_review_decision_record_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(record)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(record)
        nested_unknown["reviewer_classes_represented"][0]["runtime_approval"] = "approved"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "approval-for-runtime": ("decision_status", "approved-for-runtime"),
            "activation": ("decision_summary", "activation approved"),
            "enablement": ("decision_boundary_statement", "mode enablement ready"),
            "grant": ("decision_reason_code", "active-grant-created"),
            "runtime": ("decision_summary", "runtime authorization granted"),
            "workflow-execution": ("decision_boundary_statement", "workflow execution"),
            "model-routing": ("decision_boundary_statement", "model routing"),
            "provider-execution": ("decision_boundary_statement", "provider execution"),
            "code-execution": ("decision_boundary_statement", "code execution"),
            "experiment-execution": ("decision_boundary_statement", "experiment execution"),
            "network-call": ("decision_boundary_statement", "network call"),
            "clinical": ("medical_privacy_boundary_statement", "clinical use"),
            "private-health": (
                "medical_privacy_boundary_statement",
                "private health data processing",
            ),
            "diagnosis": ("medical_privacy_boundary_statement", "diagnosis"),
            "medical-advice": ("medical_privacy_boundary_statement", "medical advice"),
            "production-ready": ("decision_boundary_statement", "production ready"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(record)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12q_record(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12q_authorizes_runtime"])
                self.assertFalse(safe["phase12q_creates_active_grant"])
                self.assertFalse(safe["phase12q_grants_execution_permission"])
                self.assertFalse(safe["phase12q_allows_workflow_activation"])
                self.assertFalse(safe["phase12q_allows_workflow_execution"])
                self.assertFalse(safe["phase12q_allows_workflow_mode_execution"])
                self.assertFalse(safe["phase12q_allows_model_routing"])
                self.assertFalse(safe["phase12q_allows_provider_execution"])
                self.assertFalse(safe["phase12q_allows_code_execution"])
                self.assertFalse(safe["phase12q_allows_experiment_execution"])
                self.assertFalse(safe["phase12q_allows_clinical_decision_support"])
                self.assertFalse(safe["phase12q_allows_private_health_data_processing"])
                self.assertFalse(safe["active_grant_present"])
                self.assertFalse(safe["runtime_authorization_granted"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_review_and_decision_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._record()
                unsafe[field] = True

                result = validate_phase12q_record(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

        for path in (
            ("required_future_gates_snapshot", 0, "satisfied"),
            ("required_future_gates_snapshot", 0, "passed"),
            ("required_future_gates_snapshot", 0, "review_completed"),
            ("required_future_gates_snapshot", 0, "blocks_runtime_authorization", False),
            ("reviewer_classes_represented", 0, "represented"),
        ):
            with self.subTest(path=path):
                unsafe = self._record()
                if len(path) == 4:
                    unsafe[path[0]][path[1]][path[2]] = path[3]
                else:
                    unsafe[path[0]][path[1]][path[2]] = True

                result = validate_phase12q_record(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record["execution_permitted"])

        unsafe_status = self._record()
        unsafe_status["request_denied_no_runtime_authorization"] = True
        result = validate_phase12q_record(unsafe_status)
        self.assertFalse(result.compatible)
        self.assertFalse(result.sanitized_record["request_denied_no_runtime_authorization"])

    def test_source_references_remain_non_executing(self):
        record = self._record()

        self.assertEqual(
            [item["source_phase_label"] for item in record["source_phase_references"]],
            ["12N", "12O", "12P"],
        )
        for reference in record["source_phase_references"]:
            with self.subTest(reference=reference["source_phase_label"]):
                self.assertTrue(reference["metadata_only"])
                self.assertEqual(reference["runtime_stage"], "not-implemented")
                self.assertFalse(reference["execution_permitted"])
                self.assertFalse(reference["real_mode_runtime_enabled"])

    def test_phase12q_module_does_not_add_runtime_imports_or_true_flags(self):
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
            "web_access_permitted",
            "database_ingestion_added",
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
