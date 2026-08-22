import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12O_AUTHORIZATION_STATUS,
    PHASE12O_GRANT_STATUS,
    PHASE12O_MATRIX_PHASE,
    PHASE12O_REQUIRED_FUTURE_GATES,
    PHASE12O_SOURCE_PHASE,
    PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_CONTRACT_VERSION,
    PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
    PHASE12O_WORKFLOW_MODES,
)

phase12o_matrix = (
    phase12_contracts_module.phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix
)
PHASE12O_STATUS_SUMMARY_ATTR = (
    "phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix_status_summary"
)
phase12o_status_summary = getattr(phase12_contracts_module, PHASE12O_STATUS_SUMMARY_ATTR)
PHASE12O_VALIDATE_ATTR = "validate_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix"
validate_phase12o_matrix = getattr(phase12_contracts_module, PHASE12O_VALIDATE_ATTR)

REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12o-workflow-mode-safety-gate-runtime-prerequisite-matrix-v1.json"
)


class Phase12OWorkflowModeSafetyGateRuntimePrerequisiteMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_matrix = phase12o_matrix()
        cls.fixture = json.loads(MATRIX_FIXTURE.read_text(encoding="utf-8"))

    def _matrix(self):
        return copy.deepcopy(self.generated_matrix)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture

        self.assertEqual(fixture, self.generated_matrix)
        self.assertEqual(
            fixture["workflow_mode_safety_gate_matrix_contract_version"],
            PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["matrix_kind"],
            PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        )
        self.assertTrue(fixture["matrix_id"].startswith("p12o-workflow-safety-gate-matrix-"))
        self.assertEqual(fixture["source_phase"], PHASE12O_SOURCE_PHASE)
        self.assertEqual(fixture["matrix_phase"], PHASE12O_MATRIX_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12O_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12O_GRANT_STATUS)
        self.assertEqual(
            [item["workflow_mode_label"] for item in fixture["workflow_mode_prerequisite_matrix"]],
            list(PHASE12O_WORKFLOW_MODES),
        )
        self.assertEqual(
            [item["future_gate_label"] for item in fixture["required_future_gates"]],
            list(PHASE12O_REQUIRED_FUTURE_GATES),
        )
        self.assertEqual(fixture["workflow_mode_prerequisite_count"], 3)
        self.assertEqual(fixture["required_future_gate_count"], 11)
        self.assertEqual(fixture["mode_gate_requirement_count"], 33)
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["non_authorizing_proof"])
        self.assertTrue(fixture["standalone_first"])
        self.assertTrue(fixture["workflow_mode_safety_gates_metadata_only"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12o_matrix(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12o_status_summary()

        self.assertEqual(summary["source_phase"], PHASE12O_SOURCE_PHASE)
        self.assertEqual(summary["matrix_phase"], PHASE12O_MATRIX_PHASE)
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["workflow_mode_prerequisite_count"], 3)
        self.assertEqual(summary["required_future_gate_count"], 11)
        self.assertEqual(summary["mode_gate_requirement_count"], 33)
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["standalone_first"])
        self.assertTrue(summary["workflow_mode_safety_gates_metadata_only"])
        self.assertFalse(summary["phase12o_authorizes_runtime"])
        self.assertFalse(summary["phase12o_satisfies_runtime_prerequisites"])
        self.assertFalse(summary["phase12o_allows_workflow_execution"])
        self.assertFalse(summary["phase12o_allows_workflow_mode_execution"])
        self.assertFalse(summary["phase12o_allows_runtime_adapter"])
        self.assertFalse(summary["phase12o_allows_model_routing"])
        self.assertFalse(summary["phase12o_allows_clinical_decision_support"])
        self.assertFalse(summary["phase12o_allows_private_health_data_processing"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_matrix_covers_all_modes_and_gates_as_unsatisfied_prerequisites(self):
        matrix = self._matrix()
        mode_gate_pairs = [
            (item["workflow_mode_label"], item["future_gate_label"])
            for item in matrix["mode_gate_requirements"]
        ]
        expected_pairs = [
            (mode, gate)
            for mode in PHASE12O_WORKFLOW_MODES
            for gate in PHASE12O_REQUIRED_FUTURE_GATES
        ]
        self.assertEqual(mode_gate_pairs, expected_pairs)

        for entry in matrix["workflow_mode_prerequisite_matrix"]:
            with self.subTest(mode=entry["workflow_mode_label"]):
                self.assertTrue(entry["metadata_only"])
                self.assertTrue(entry["standalone_first"])
                self.assertTrue(entry["runtime_prerequisite_only"])
                self.assertEqual(
                    entry["required_future_gate_labels"],
                    list(PHASE12O_REQUIRED_FUTURE_GATES),
                )
                self.assertFalse(entry["all_prerequisites_satisfied"])
                self.assertTrue(entry["runtime_blocked"])
                self.assertTrue(entry["review_required"])
                self.assertFalse(entry["workflow_execution_permitted"])
                self.assertFalse(entry["workflow_mode_execution_permitted"])
                self.assertFalse(entry["model_routing_execution_permitted"])
                self.assertFalse(entry["code_execution_permitted"])
                self.assertFalse(entry["experiment_execution_permitted"])
                self.assertFalse(entry["clinical_decision_support_allowed"])
                self.assertFalse(entry["private_health_data_allowed"])
                self.assertFalse(entry["execution_permitted"])

        for gate in matrix["required_future_gates"]:
            with self.subTest(gate=gate["future_gate_label"]):
                self.assertTrue(gate["metadata_only"])
                self.assertFalse(gate["satisfied"])
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["runtime_prerequisite_satisfied"])
                self.assertFalse(gate["execution_permitted"])

        for row in matrix["mode_gate_requirements"]:
            with self.subTest(mode=row["workflow_mode_label"], gate=row["future_gate_label"]):
                self.assertTrue(row["metadata_only"])
                self.assertFalse(row["satisfied"])
                self.assertFalse(row["passed"])
                self.assertFalse(row["runtime_prerequisite_satisfied"])
                self.assertFalse(row["execution_permitted"])

    def test_status_words_never_satisfy_runtime_prerequisites_or_create_grants(self):
        finalize = phase12_contracts_module._finalize_phase12o_workflow_mode_safety_gate_matrix
        for wording in (
            "normal",
            "fusion",
            "scientist",
            "gate",
            "review",
            "satisfied",
            "passed",
            "enabled",
            "configured",
            "available",
            "ready",
            "approved",
            "authorized",
            "deployed",
            "production",
            "runtime",
        ):
            with self.subTest(wording=wording):
                unsafe = self._matrix()
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["matrix_status"] = wording
                unsafe["phase12o_authorizes_runtime"] = True
                unsafe["phase12o_satisfies_runtime_prerequisites"] = True
                unsafe["phase12o_allows_workflow_execution"] = True
                unsafe["phase12o_active_grant_present"] = True
                unsafe["runtime_prerequisite_satisfied"] = True
                unsafe["active_grant_present"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12o_matrix(unsafe)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12o_authorizes_runtime"])
                self.assertFalse(safe["phase12o_satisfies_runtime_prerequisites"])
                self.assertFalse(safe["phase12o_allows_workflow_execution"])
                self.assertFalse(safe["phase12o_active_grant_present"])
                self.assertFalse(safe["runtime_prerequisite_satisfied"])
                self.assertFalse(safe["active_grant_present"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_and_prerequisite_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._matrix()
                unsafe[field] = True

                result = validate_phase12o_matrix(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_hidden_runtime_and_medical_semantics_fail_closed(self):
        matrix = self._matrix()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(matrix)
        missing.pop("mode_gate_requirements")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(matrix)
        unsupported["workflow_mode_safety_gate_matrix_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(matrix)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(matrix)
        nested_unknown["mode_gate_requirements"][0]["runner"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "workflow-execution": ("matrix_boundary_statement", "workflow execution"),
            "runtime-adapter": ("matrix_boundary_statement", "runtime adapter"),
            "model-routing": ("matrix_boundary_statement", "model routing"),
            "provider-execution": ("matrix_boundary_statement", "provider execution"),
            "model-execution": ("matrix_boundary_statement", "model execution"),
            "code-execution": ("matrix_boundary_statement", "code execution"),
            "experiment-execution": ("matrix_boundary_statement", "experiment execution"),
            "web-behavior": ("matrix_boundary_statement", "web behavior"),
            "database-behavior": ("matrix_boundary_statement", "database behavior"),
            "network-call": ("matrix_boundary_statement", "network call"),
            "clinical": ("medical_privacy_boundary_statement", "clinical recommendation"),
            "private-health": (
                "medical_privacy_boundary_statement",
                "private health data processing",
            ),
            "diagnosis": ("medical_privacy_boundary_statement", "diagnosis"),
            "treatment": ("medical_privacy_boundary_statement", "treatment planning"),
            "medical-advice": ("medical_privacy_boundary_statement", "medical advice"),
            "device-access": ("medical_privacy_boundary_statement", "device access"),
            "raw-sensor": ("medical_privacy_boundary_statement", "raw sensor processing"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(matrix)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12o_matrix(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12o_authorizes_runtime"])
                self.assertFalse(safe["workflow_execution_permitted"])
                self.assertFalse(safe["workflow_mode_execution_permitted"])
                self.assertFalse(safe["runtime_prerequisite_satisfied"])
                self.assertFalse(safe["model_routing_execution_permitted"])
                self.assertFalse(safe["code_execution_permitted"])
                self.assertFalse(safe["experiment_execution_permitted"])
                self.assertFalse(safe["clinical_decision_support_allowed"])
                self.assertFalse(safe["private_health_data_allowed"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_source_phase12n_reference_remains_non_executing(self):
        matrix = self._matrix()
        source = matrix["source_phase12n_profile"]

        self.assertEqual(source["source_phase_label"], "12N")
        self.assertTrue(source["metadata_only"])
        self.assertEqual(source["runtime_stage"], "not-implemented")
        self.assertFalse(source["execution_permitted"])
        self.assertFalse(source["real_mode_runtime_enabled"])

    def test_phase12o_module_does_not_add_runtime_imports_or_true_flags(self):
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
            '"runtime_prerequisite_satisfied": true',
            '"all_prerequisites_satisfied": true',
            '"model_routing_execution_permitted": true',
            '"code_execution_permitted": true',
            '"experiment_execution_permitted": true',
            '"runtime_adapter_execution_granted": true',
            '"network_call_execution_granted": true',
            '"clinical_decision_support_allowed": true',
            '"private_health_data_allowed": true',
            '"active_grant_present": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
            "workflow_execution_permitted",
            "workflow_mode_execution_permitted",
            "runtime_prerequisite_satisfied",
            "all_prerequisites_satisfied",
            "runtime_adapter_execution_granted",
            "model_routing_execution_permitted",
            "provider_execution_granted",
            "model_execution_granted",
            "code_execution_permitted",
            "experiment_execution_permitted",
            "autonomous_experimentation_permitted",
            "web_access_permitted",
            "database_ingestion_added",
            "web_scraping_added",
            "network_call_execution_granted",
            "clinical_decision_support_allowed",
            "clinical_decision_support_added",
            "private_health_data_allowed",
            "private_health_data_processing_added",
            "active_grant_present",
            "real_mode_authorization_added",
            "diagnosis_provided",
            "treatment_plan_provided",
            "medical_advice_provided",
            "dosing_added",
            "nutrition_prescription_added",
            "device_access_granted",
            "raw_sensor_processing_added",
            "production_ready",
            "execution_permitted",
            "real_mode_runtime_enabled",
        )


if __name__ == "__main__":
    unittest.main()
