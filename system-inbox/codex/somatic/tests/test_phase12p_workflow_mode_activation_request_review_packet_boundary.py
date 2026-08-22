import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12P_AUTHORIZATION_STATUS,
    PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS,
    PHASE12P_GRANT_STATUS,
    PHASE12P_PACKET_PHASE,
    PHASE12P_REQUIRED_FUTURE_GATES,
    PHASE12P_REQUIRED_REVIEWER_CLASSES,
    PHASE12P_RISK_SUMMARY_PLACEHOLDERS,
    PHASE12P_SOURCE_PHASE_RANGE,
    PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_CONTRACT_VERSION,
    PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
    PHASE12P_WORKFLOW_MODES,
)

phase12p_packet = (
    phase12_contracts_module.phase12p_workflow_mode_activation_request_review_packet_boundary
)
PHASE12P_STATUS_SUMMARY_ATTR = (
    "phase12p_workflow_mode_activation_request_review_packet_boundary_status_summary"
)
phase12p_status_summary = getattr(phase12_contracts_module, PHASE12P_STATUS_SUMMARY_ATTR)
PHASE12P_VALIDATE_ATTR = "validate_phase12p_workflow_mode_activation_request_review_packet_boundary"
validate_phase12p_packet = getattr(phase12_contracts_module, PHASE12P_VALIDATE_ATTR)

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12p-workflow-mode-activation-request-review-packet-boundary-v1.json"
)


class Phase12PWorkflowModeActivationRequestReviewPacketBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_packet = phase12p_packet()
        cls.fixture = json.loads(PACKET_FIXTURE.read_text(encoding="utf-8"))

    def _packet(self):
        return copy.deepcopy(self.generated_packet)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture

        self.assertEqual(fixture, self.generated_packet)
        self.assertEqual(
            fixture["workflow_mode_activation_request_review_packet_contract_version"],
            PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["packet_kind"],
            PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        )
        self.assertTrue(
            fixture["activation_request_packet_id"].startswith("p12p-workflow-mode-review-packet-")
        )
        self.assertEqual(fixture["source_phase_range"], PHASE12P_SOURCE_PHASE_RANGE)
        self.assertEqual(fixture["packet_phase"], PHASE12P_PACKET_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12P_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12P_GRANT_STATUS)
        self.assertEqual(
            [
                item["requested_workflow_mode_label"]
                for item in fixture["workflow_mode_review_packets"]
            ],
            list(PHASE12P_WORKFLOW_MODES),
        )
        self.assertEqual(
            [item["future_gate_label"] for item in fixture["required_future_gates"]],
            list(PHASE12P_REQUIRED_FUTURE_GATES),
        )
        self.assertEqual(
            [item["reviewer_class_label"] for item in fixture["required_reviewer_classes"]],
            list(PHASE12P_REQUIRED_REVIEWER_CLASSES),
        )
        self.assertEqual(fixture["workflow_mode_review_packet_count"], 3)
        self.assertEqual(fixture["required_future_gate_count"], 11)
        self.assertEqual(fixture["required_reviewer_class_count"], 4)
        self.assertEqual(fixture["risk_summary_placeholder_count"], 6)
        self.assertEqual(fixture["evidence_inventory_placeholder_count"], 4)
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["review_packet_boundary_only"])
        self.assertTrue(fixture["not_authorized"])
        self.assertTrue(fixture["no_active_grant"])
        self.assertTrue(fixture["no_runtime_authorization"])
        self.assertTrue(fixture["no_execution_permission"])
        self.assertTrue(fixture["workflow_mode_activation_not_permitted"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12p_packet(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12p_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12P_SOURCE_PHASE_RANGE)
        self.assertEqual(summary["packet_phase"], "review-packet-boundary-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertEqual(summary["workflow_mode_review_packet_count"], 3)
        self.assertEqual(summary["required_future_gate_count"], 11)
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["review_packet_boundary_only"])
        self.assertTrue(summary["all_future_gates_unsatisfied"])
        self.assertTrue(summary["workflow_mode_activation_not_permitted"])
        self.assertFalse(summary["phase12p_authorizes_runtime"])
        self.assertFalse(summary["phase12p_creates_active_grant"])
        self.assertFalse(summary["phase12p_grants_execution_permission"])
        self.assertFalse(summary["phase12p_allows_workflow_execution"])
        self.assertFalse(summary["phase12p_allows_workflow_mode_execution"])
        self.assertFalse(summary["phase12p_allows_model_routing"])
        self.assertFalse(summary["phase12p_allows_provider_execution"])
        self.assertFalse(summary["phase12p_allows_code_execution"])
        self.assertFalse(summary["phase12p_allows_experiment_execution"])
        self.assertFalse(summary["phase12p_allows_private_health_data_processing"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self.assertFalse(summary["production_ready"])

    def test_packet_covers_all_modes_and_unsatisfied_future_gates(self):
        packet = self._packet()

        for entry in packet["workflow_mode_review_packets"]:
            with self.subTest(mode=entry["requested_workflow_mode_label"]):
                self.assertTrue(entry["metadata_only"])
                self.assertTrue(entry["review_packet_boundary_only"])
                self.assertTrue(entry["standalone_first"])
                self.assertTrue(entry["not_authorized"])
                self.assertTrue(entry["no_active_grant"])
                self.assertTrue(entry["no_runtime_authorization"])
                self.assertTrue(entry["no_execution_permission"])
                self.assertTrue(entry["workflow_mode_activation_not_permitted"])
                self.assertEqual(
                    entry["required_future_gate_labels"],
                    list(PHASE12P_REQUIRED_FUTURE_GATES),
                )
                self.assertFalse(entry["workflow_execution_permitted"])
                self.assertFalse(entry["workflow_mode_execution_permitted"])
                self.assertFalse(entry["model_routing_execution_permitted"])
                self.assertFalse(entry["provider_execution_granted"])
                self.assertFalse(entry["code_execution_permitted"])
                self.assertFalse(entry["experiment_execution_permitted"])
                self.assertFalse(entry["clinical_decision_support_allowed"])
                self.assertFalse(entry["private_health_data_allowed"])
                self.assertFalse(entry["execution_permitted"])

        for gate in packet["required_future_gates"]:
            with self.subTest(gate=gate["future_gate_label"]):
                self.assertTrue(gate["metadata_only"])
                self.assertFalse(gate["satisfied"])
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["review_completed"])
                self.assertFalse(gate["execution_permitted"])

    def test_reviewers_risk_and_evidence_remain_unmet_placeholders(self):
        packet = self._packet()

        self.assertEqual(
            [
                item["risk_summary_placeholder_label"]
                for item in packet["risk_summary_placeholders"]
            ],
            list(PHASE12P_RISK_SUMMARY_PLACEHOLDERS),
        )
        self.assertEqual(
            [
                item["evidence_inventory_placeholder_label"]
                for item in packet["evidence_inventory_placeholders"]
            ],
            list(PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS),
        )
        for reviewer in packet["required_reviewer_classes"]:
            with self.subTest(reviewer=reviewer["reviewer_class_label"]):
                self.assertTrue(reviewer["required"])
                self.assertFalse(reviewer["completed"])
                self.assertFalse(reviewer["approved"])
                self.assertFalse(reviewer["execution_permitted"])
        for placeholder in [
            *packet["risk_summary_placeholders"],
            *packet["evidence_inventory_placeholders"],
        ]:
            with self.subTest(placeholder=placeholder):
                self.assertTrue(placeholder["required"])
                self.assertFalse(placeholder["filled"])
                self.assertFalse(placeholder["execution_permitted"])

    def test_unsafe_fields_and_wording_fail_closed_with_sanitized_false_output(self):
        packet = self._packet()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(packet)
        missing.pop("workflow_mode_review_packets")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(packet)
        unsupported["workflow_mode_activation_request_review_packet_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(packet)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(packet)
        nested_unknown["workflow_mode_review_packets"][0]["runner"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "activation": ("packet_status", "activation approved"),
            "enablement": ("packet_boundary_statement", "mode enablement ready"),
            "grant": ("grant_status", "active grant"),
            "runtime": ("packet_boundary_statement", "runtime authorization granted"),
            "workflow-execution": ("packet_boundary_statement", "workflow execution"),
            "model-routing": ("packet_boundary_statement", "model routing"),
            "provider-execution": ("packet_boundary_statement", "provider execution"),
            "code-execution": ("packet_boundary_statement", "code execution"),
            "experiment-execution": ("packet_boundary_statement", "experiment execution"),
            "network-call": ("packet_boundary_statement", "network call"),
            "clinical": ("medical_privacy_boundary_statement", "clinical use"),
            "private-health": (
                "medical_privacy_boundary_statement",
                "private health data processing",
            ),
            "diagnosis": ("medical_privacy_boundary_statement", "diagnosis"),
            "medical-advice": ("medical_privacy_boundary_statement", "medical advice"),
            "production-ready": ("packet_boundary_statement", "production ready"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(packet)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12p_packet(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12p_authorizes_runtime"])
                self.assertFalse(safe["phase12p_creates_active_grant"])
                self.assertFalse(safe["phase12p_grants_execution_permission"])
                self.assertFalse(safe["phase12p_allows_workflow_execution"])
                self.assertFalse(safe["phase12p_allows_workflow_mode_execution"])
                self.assertFalse(safe["phase12p_allows_model_routing"])
                self.assertFalse(safe["phase12p_allows_provider_execution"])
                self.assertFalse(safe["phase12p_allows_code_execution"])
                self.assertFalse(safe["phase12p_allows_experiment_execution"])
                self.assertFalse(safe["phase12p_allows_clinical_decision_support"])
                self.assertFalse(safe["phase12p_allows_private_health_data_processing"])
                self.assertFalse(safe["active_grant_present"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_and_review_satisfaction_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._packet()
                unsafe[field] = True

                result = validate_phase12p_packet(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

        for path in (
            ("required_future_gates", 0, "satisfied"),
            ("required_future_gates", 0, "passed"),
            ("required_future_gates", 0, "review_completed"),
            ("required_reviewer_classes", 0, "completed"),
            ("required_reviewer_classes", 0, "approved"),
            ("risk_summary_placeholders", 0, "filled"),
            ("evidence_inventory_placeholders", 0, "filled"),
        ):
            with self.subTest(path=path):
                unsafe = self._packet()
                unsafe[path[0]][path[1]][path[2]] = True

                result = validate_phase12p_packet(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record["execution_permitted"])

    def test_source_references_remain_non_executing(self):
        packet = self._packet()

        self.assertEqual(
            [item["source_phase_label"] for item in packet["source_phase_references"]],
            ["12N", "12O"],
        )
        for reference in [
            *packet["source_phase_references"],
            packet["prerequisite_matrix_reference"],
        ]:
            with self.subTest(reference=reference["source_phase_label"]):
                self.assertTrue(reference["metadata_only"])
                self.assertEqual(reference["runtime_stage"], "not-implemented")
                self.assertFalse(reference["execution_permitted"])
                self.assertFalse(reference["real_mode_runtime_enabled"])
        self.assertFalse(packet["prerequisite_matrix_reference"]["runtime_prerequisites_satisfied"])

    def test_phase12p_module_does_not_add_runtime_imports_or_true_flags(self):
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
            '"production_ready": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
            "workflow_execution_permitted",
            "workflow_mode_execution_permitted",
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
            "production_ready",
            "execution_permitted",
            "real_mode_runtime_enabled",
        )


if __name__ == "__main__":
    unittest.main()
