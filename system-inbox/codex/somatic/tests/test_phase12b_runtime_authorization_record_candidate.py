import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase11_contracts import (
    phase11_planning_governance_closeout_index,
    phase11_runtime_authorization_gap_ledger,
    validate_phase11_planning_governance_closeout_index,
    validate_phase11_runtime_authorization_gap_ledger,
)
from somatic.safety.phase12_contracts import (
    PHASE12B_AUTHORIZATION_PHASE,
    PHASE12B_AUTHORIZATION_STATUS,
    PHASE12B_DECISION_STATUS_REVIEW_REQUIRED,
    PHASE12B_GRANT_STATUS,
    PHASE12B_RECORD_CANDIDATE_STATUS,
    PHASE12B_REQUESTED_DOMAINS,
    PHASE12B_REQUIRED_FUTURE_GATES,
    PHASE12B_REQUIRED_REVIEWER_ROLES,
    PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION,
    PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12b_runtime_authorization_record_candidate_status_summary,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-12b-runtime-authorization-record-candidate-v1.json"
)
UNSAFE_PHASE12B_SENTINELS = (
    "document-parsed.json",
    "sample-esp32-csi",
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
    "model_body",
    "parser_body",
    "provider_body",
    "accepted-for-runtime",
    "execution-permitted",
    "runtime-enabled",
    "permission-granted",
    "authorization-granted",
    "approval-granted",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase12BRuntimeAuthorizationRecordCandidateTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(RECORD_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12b_runtime_authorization_record_candidate()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["runtime_authorization_record_candidate_contract_version"],
            PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION,
        )
        self.assertEqual(fixture["record_kind"], PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND)
        self.assertTrue(fixture["record_id"].startswith("p12b-record-"))
        self.assertEqual(fixture["source_phase"], "12A")
        self.assertEqual(fixture["authorization_phase"], PHASE12B_AUTHORIZATION_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12B_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["decision_status"], "not-submitted")
        self.assertEqual(fixture["grant_status"], PHASE12B_GRANT_STATUS)
        self.assertEqual(
            fixture["record_candidate_status"],
            PHASE12B_RECORD_CANDIDATE_STATUS,
        )
        self.assertFalse(fixture["phase12b_records_are_approvals_grants_or_permissions"])
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["adapter_execution_granted"])
        self.assertFalse(fixture["provider_execution_granted"])
        self.assertFalse(fixture["model_execution_granted"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            [domain["domain_label"] for domain in fixture["requested_domains"]],
            list(PHASE12B_REQUESTED_DOMAINS),
        )
        self.assertEqual(fixture["requested_domain_count"], 2)
        self.assertEqual(
            [role["reviewer_role"] for role in fixture["required_future_reviewer_roles"]],
            list(PHASE12B_REQUIRED_REVIEWER_ROLES),
        )
        self.assertEqual(fixture["required_future_reviewer_role_count"], 6)
        self.assertEqual(
            [(gate["gate_id"], gate["reviewer_role"]) for gate in fixture["required_future_gates"]],
            list(PHASE12B_REQUIRED_FUTURE_GATES),
        )
        self.assertEqual(fixture["required_future_gate_count"], 8)
        self.assertEqual(fixture["submitted_future_gate_count"], 0)
        self.assertEqual(fixture["satisfied_future_gate_count"], 0)
        self.assertEqual(fixture["passed_future_gate_count"], 0)
        self.assertTrue(fixture["jules_review_required_for_validator_or_authorization_semantics"])
        for domain in fixture["requested_domains"]:
            with self.subTest(domain=domain["domain_label"]):
                self.assertEqual(domain["request_status"], "record-candidate-only")
                self.assertTrue(domain["metadata_only"])
                self.assertFalse(domain["execution_permitted"])
                self.assertFalse(domain["real_mode_runtime_enabled"])
        for role in fixture["required_future_reviewer_roles"]:
            with self.subTest(role=role["reviewer_role"]):
                self.assertEqual(role["review_status"], "future-review-required")
                self.assertTrue(role["metadata_only"])
                self.assertFalse(role["satisfied_by_phase12b"])
                self.assertFalse(role["passed"])
                self.assertFalse(role["execution_permitted"])
                self.assertFalse(role["real_mode_runtime_enabled"])
        for gate in fixture["required_future_gates"]:
            with self.subTest(gate=gate["gate_id"]):
                self.assertEqual(gate["gate_status"], "future-review-required-not-passed")
                self.assertTrue(gate["required_before_runtime_authorization"])
                self.assertFalse(gate["submitted_by_phase12b"])
                self.assertFalse(gate["satisfied_by_phase12b"])
                self.assertFalse(gate["passed"])
                self.assertTrue(gate["metadata_only"])
                self.assertFalse(gate["execution_permitted"])
                self.assertFalse(gate["real_mode_runtime_enabled"])
        result = validate_phase12b_runtime_authorization_record_candidate(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12b_runtime_authorization_record_candidate_status_summary()

        self.assertEqual(summary["source_phase"], "12A")
        self.assertEqual(summary["authorization_phase"], "record-candidate-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["decision_status"], "not-submitted")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["requested_domain_count"], 2)
        self.assertEqual(summary["required_future_reviewer_role_count"], 6)
        self.assertEqual(summary["required_future_gate_count"], 8)
        self.assertEqual(summary["submitted_future_gate_count"], 0)
        self.assertEqual(summary["satisfied_future_gate_count"], 0)
        self.assertEqual(summary["passed_future_gate_count"], 0)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["adapter_execution_granted"])
        self.assertFalse(summary["provider_execution_granted"])
        self.assertFalse(summary["model_execution_granted"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self._assert_no_private_values(summary)

    def test_review_required_decision_status_still_does_not_authorize_runtime(self):
        record = phase12b_runtime_authorization_record_candidate(
            decision_status=PHASE12B_DECISION_STATUS_REVIEW_REQUIRED,
        )
        result = validate_phase12b_runtime_authorization_record_candidate(record)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(record["decision_status"], "review-required")
        self.assertEqual(record["authorization_status"], "not-authorized")
        self.assertEqual(record["grant_status"], "no-grant")
        self.assertFalse(record["adapter_execution_granted"])
        self.assertFalse(record["provider_execution_granted"])
        self.assertFalse(record["model_execution_granted"])
        self.assertFalse(record["execution_permitted"])
        self.assertFalse(record["real_mode_runtime_enabled"])

    def test_status_words_never_enable_execution(self):
        record = phase12b_runtime_authorization_record_candidate()
        finalize = (
            phase12_contracts_module._finalize_phase12b_runtime_authorization_record_candidate
        )
        for wording in (
            "approved",
            "authorized",
            "granted",
            "ready",
            "complete",
            "candidate",
            "submitted",
            "review-required",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(record)
                unsafe["authorization_status"] = wording
                unsafe["decision_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["record_candidate_status"] = wording
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12b_runtime_authorization_record_candidate(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(result.sanitized_record["adapter_execution_granted"])
                self.assertFalse(result.sanitized_record["provider_execution_granted"])
                self.assertFalse(result.sanitized_record["model_execution_granted"])

    def test_future_reviewer_and_gate_metadata_cannot_be_interpreted_as_passed(self):
        record = phase12b_runtime_authorization_record_candidate()
        unsafe = copy.deepcopy(record)
        unsafe["required_future_reviewer_roles"][0]["review_status"] = "approved"
        unsafe["required_future_reviewer_roles"][0]["satisfied_by_phase12b"] = True
        unsafe["required_future_reviewer_roles"][0]["passed"] = True
        unsafe["required_future_reviewer_roles"][0]["execution_permitted"] = True
        unsafe["required_future_gates"][0]["gate_status"] = "passed"
        unsafe["required_future_gates"][0]["submitted_by_phase12b"] = True
        unsafe["required_future_gates"][0]["satisfied_by_phase12b"] = True
        unsafe["required_future_gates"][0]["passed"] = True
        unsafe["required_future_gates"][0]["execution_permitted"] = True
        unsafe["submitted_future_gate_count"] = 1
        unsafe["satisfied_future_gate_count"] = 1
        unsafe["passed_future_gate_count"] = 1
        unsafe = phase12_contracts_module._finalize_phase12b_runtime_authorization_record_candidate(
            unsafe
        )

        result = validate_phase12b_runtime_authorization_record_candidate(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        self.assertEqual(result.sanitized_record["submitted_future_gate_count"], 0)
        self.assertEqual(result.sanitized_record["satisfied_future_gate_count"], 0)
        self.assertEqual(result.sanitized_record["passed_future_gate_count"], 0)
        for role in result.sanitized_record["required_future_reviewer_roles"]:
            with self.subTest(role=role["reviewer_role"]):
                self.assertFalse(role["satisfied_by_phase12b"])
                self.assertFalse(role["passed"])
                self.assertFalse(role["execution_permitted"])
        for gate in result.sanitized_record["required_future_gates"]:
            with self.subTest(gate=gate["gate_id"]):
                self.assertFalse(gate["submitted_by_phase12b"])
                self.assertFalse(gate["satisfied_by_phase12b"])
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["execution_permitted"])

    def test_no_active_authorization_grant_can_validate(self):
        record = phase12b_runtime_authorization_record_candidate()
        unsafe = copy.deepcopy(record)
        unsafe["grant_status"] = "granted"
        unsafe["authorization_status"] = "authorized"
        unsafe["decision_status"] = "approved"
        unsafe["phase12b_records_are_approvals_grants_or_permissions"] = True
        unsafe["adapter_execution_granted"] = True
        unsafe["provider_execution_granted"] = True
        unsafe["model_execution_granted"] = True
        unsafe["execution_permitted"] = True
        unsafe["real_mode_runtime_enabled"] = True
        unsafe["authorization_grant"] = {
            "status": "permission-granted",
            "runtime_stage": "ready",
        }

        result = validate_phase12b_runtime_authorization_record_candidate(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        self.assertEqual(result.sanitized_record["grant_status"], "no-grant")
        self.assertFalse(
            result.sanitized_record["phase12b_records_are_approvals_grants_or_permissions"]
        )
        self.assertNotIn("authorization_grant", result.sanitized_record)

    def test_validator_fails_closed_for_unsafe_or_contradictory_records(self):
        record = phase12b_runtime_authorization_record_candidate()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(record)
        missing.pop("required_future_gates")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(record)
        unsupported["runtime_authorization_record_candidate_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(record)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        authorization = copy.deepcopy(record)
        authorization["authorization_status"] = "authorization-granted"
        cases.append(("authorization-wording", authorization))

        permission = copy.deepcopy(record)
        permission["record_candidate_status"] = "runtime-permission-granted"
        cases.append(("permission-wording", permission))

        unsafe = copy.deepcopy(record)
        unsafe["source_design_charter"]["charter_status"] = "https://example.invalid/api_key"
        cases.append(("unsafe", unsafe))

        boolean_count = copy.deepcopy(record)
        boolean_count["required_future_gate_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(record)
        string_count["requested_domain_count"] = "2"
        cases.append(("string-count", string_count))

        source_id = copy.deepcopy(record)
        source_id["source_design_charter"]["source_id"] = "private-source"
        cases.append(("source-id", source_id))

        raw_marker = copy.deepcopy(record)
        raw_marker["requested_domains"][0]["domain_label"] = "raw_csi"
        cases.append(("raw-marker", raw_marker))

        model_body = copy.deepcopy(record)
        model_body["required_future_gates"][0]["gate_status"] = "model_body"
        cases.append(("model-body", model_body))

        clinical = copy.deepcopy(record)
        clinical["required_future_reviewer_roles"][0]["review_status"] = "clinical"
        cases.append(("clinical", clinical))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12b_runtime_authorization_record_candidate(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE12B_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_phase11_and_phase12a_sources_remain_non_executing(self):
        ledger = phase11_runtime_authorization_gap_ledger()
        closeout = phase11_planning_governance_closeout_index(ledger)
        charter = phase12a_runtime_authorization_design_charter()
        ledger_result = validate_phase11_runtime_authorization_gap_ledger(ledger)
        closeout_result = validate_phase11_planning_governance_closeout_index(closeout)
        charter_result = validate_phase12a_runtime_authorization_design_charter(charter)

        self.assertTrue(ledger_result.compatible, ledger_result.errors)
        self.assertTrue(closeout_result.compatible, closeout_result.errors)
        self.assertTrue(charter_result.compatible, charter_result.errors)
        for payload in (ledger, closeout, charter):
            with self.subTest(keys=tuple(sorted(payload))):
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["adapter_execution_granted"])
                self.assertFalse(payload["provider_execution_granted"])
                self.assertFalse(payload["model_execution_granted"])
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12b_module_does_not_add_runtime_execution_imports(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "requests",
            "urllib",
            "socket",
            "subprocess",
            "import serial",
            "from serial",
            "mqtt",
            "udp",
            "tcpdump",
            "tshark",
            "aircrack",
            "open(",
            'network_calls": true',
            'execution_permitted": true',
            'real_mode_runtime_enabled": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    def _assert_no_private_values(self, payload):
        encoded = self._safe_encoded(payload)
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE12B_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    @staticmethod
    def _safe_encoded(payload):
        return (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace("\\", "/")
            .replace("real-mode-authorization-missing", "real-mode-gap-missing")
            .replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace("runtime_authorization", "runtime_status")
            .replace("explicit-human-authorization-record", "explicit-human-review-record")
            .replace(
                "jules-human-review-for-validator-authorization-semantics",
                "jules-human-review-for-validator-semantics",
            )
        )


if __name__ == "__main__":
    unittest.main()
