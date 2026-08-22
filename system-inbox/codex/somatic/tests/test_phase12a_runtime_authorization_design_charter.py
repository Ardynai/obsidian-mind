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
    PHASE12A_AUTHORIZATION_PHASE,
    PHASE12A_AUTHORIZATION_STATUS,
    PHASE12A_FUTURE_REQUIRED_GATES,
    PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION,
    PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
    phase12a_runtime_authorization_design_charter,
    phase12a_runtime_authorization_design_charter_status_summary,
    validate_phase12a_runtime_authorization_design_charter,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CHARTER_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-12a-runtime-authorization-design-charter-v1.json"
)
UNSAFE_PHASE12A_SENTINELS = (
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
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase12ARuntimeAuthorizationDesignCharterTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(CHARTER_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12a_runtime_authorization_design_charter()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["runtime_authorization_design_charter_contract_version"],
            PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["charter_kind"],
            PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        )
        self.assertTrue(fixture["charter_id"].startswith("p12a-charter-"))
        self.assertEqual(fixture["source_phase_range"], "11L-11M")
        self.assertEqual(fixture["authorization_phase"], PHASE12A_AUTHORIZATION_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12A_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["phase12a_satisfies_future_gates"])
        self.assertFalse(fixture["adapter_execution_granted"])
        self.assertFalse(fixture["provider_execution_granted"])
        self.assertFalse(fixture["model_execution_granted"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            [gate["gate_id"] for gate in fixture["future_required_gates"]],
            list(PHASE12A_FUTURE_REQUIRED_GATES),
        )
        self.assertEqual(fixture["future_required_gate_count"], 8)
        self.assertEqual(fixture["satisfied_future_gate_count"], 0)
        self.assertEqual(fixture["passed_future_gate_count"], 0)
        self.assertTrue(fixture["jules_review_required_for_validator_or_authorization_semantics"])
        for gate in fixture["future_required_gates"]:
            with self.subTest(gate=gate["gate_id"]):
                self.assertEqual(gate["gate_status"], "future-required-not-satisfied")
                self.assertTrue(gate["required_before_runtime_authorization"])
                self.assertFalse(gate["satisfied_by_phase12a"])
                self.assertFalse(gate["passed"])
                self.assertTrue(gate["metadata_only"])
                self.assertFalse(gate["execution_permitted"])
                self.assertFalse(gate["real_mode_runtime_enabled"])
        result = validate_phase12a_runtime_authorization_design_charter(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12a_runtime_authorization_design_charter_status_summary()

        self.assertEqual(summary["source_phase_range"], "11L-11M")
        self.assertEqual(summary["authorization_phase"], "design-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["future_required_gate_count"], 8)
        self.assertEqual(summary["satisfied_future_gate_count"], 0)
        self.assertEqual(summary["passed_future_gate_count"], 0)
        self.assertTrue(summary["jules_review_required_for_validator_or_authorization_semantics"])
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["adapter_execution_granted"])
        self.assertFalse(summary["provider_execution_granted"])
        self.assertFalse(summary["model_execution_granted"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self._assert_no_private_values(summary)

    def test_status_words_never_enable_execution(self):
        charter = phase12a_runtime_authorization_design_charter()
        finalize = phase12_contracts_module._finalize_phase12a_runtime_authorization_design_charter
        for wording in (
            "authorized",
            "ready",
            "approved",
            "complete",
            "chartered",
            "designed",
            "gate-defined",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(charter)
                unsafe["authorization_status"] = wording
                unsafe["charter_status"] = wording
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12a_runtime_authorization_design_charter(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(result.sanitized_record["adapter_execution_granted"])
                self.assertFalse(result.sanitized_record["provider_execution_granted"])
                self.assertFalse(result.sanitized_record["model_execution_granted"])

    def test_future_gate_metadata_cannot_be_interpreted_as_passed(self):
        charter = phase12a_runtime_authorization_design_charter()
        unsafe = copy.deepcopy(charter)
        unsafe["future_required_gates"][0]["gate_status"] = "passed"
        unsafe["future_required_gates"][0]["satisfied_by_phase12a"] = True
        unsafe["future_required_gates"][0]["passed"] = True
        unsafe["future_required_gates"][0]["execution_permitted"] = True
        unsafe["satisfied_future_gate_count"] = 1
        unsafe["passed_future_gate_count"] = 1
        unsafe = phase12_contracts_module._finalize_phase12a_runtime_authorization_design_charter(
            unsafe
        )

        result = validate_phase12a_runtime_authorization_design_charter(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        self.assertEqual(result.sanitized_record["satisfied_future_gate_count"], 0)
        self.assertEqual(result.sanitized_record["passed_future_gate_count"], 0)
        for gate in result.sanitized_record["future_required_gates"]:
            with self.subTest(gate=gate["gate_id"]):
                self.assertFalse(gate["satisfied_by_phase12a"])
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["execution_permitted"])

    def test_validator_fails_closed_for_unsafe_or_contradictory_charters(self):
        charter = phase12a_runtime_authorization_design_charter()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(charter)
        missing.pop("future_required_gates")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(charter)
        unsupported["runtime_authorization_design_charter_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(charter)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        runtime = copy.deepcopy(charter)
        runtime["adapter_execution_granted"] = True
        runtime["provider_execution_granted"] = True
        runtime["model_execution_granted"] = True
        runtime["execution_permitted"] = True
        runtime["real_mode_runtime_enabled"] = True
        cases.append(("runtime-grant", runtime))

        authorization = copy.deepcopy(charter)
        authorization["authorization_status"] = "authorization-granted"
        cases.append(("authorization-wording", authorization))

        permission = copy.deepcopy(charter)
        permission["charter_scope"] = "runtime-permission-granted"
        cases.append(("permission-wording", permission))

        unsafe = copy.deepcopy(charter)
        unsafe["source_runtime_gap_ledger"]["readiness_gap"] = "https://example.invalid/api_key"
        cases.append(("unsafe", unsafe))

        boolean_count = copy.deepcopy(charter)
        boolean_count["future_required_gate_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(charter)
        string_count["source_governance_closeout"]["blocker_count"] = "10"
        cases.append(("string-count", string_count))

        source_id = copy.deepcopy(charter)
        source_id["source_governance_closeout"]["source_id"] = "private-source"
        cases.append(("source-id", source_id))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12a_runtime_authorization_design_charter(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE12A_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_phase11_sources_remain_not_authorized_and_non_executing(self):
        ledger = phase11_runtime_authorization_gap_ledger()
        closeout = phase11_planning_governance_closeout_index(ledger)
        ledger_result = validate_phase11_runtime_authorization_gap_ledger(ledger)
        closeout_result = validate_phase11_planning_governance_closeout_index(closeout)

        self.assertTrue(ledger_result.compatible, ledger_result.errors)
        self.assertTrue(closeout_result.compatible, closeout_result.errors)
        for payload in (ledger, closeout):
            with self.subTest(keys=tuple(sorted(payload))):
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["adapter_execution_granted"])
                self.assertFalse(payload["provider_execution_granted"])
                self.assertFalse(payload["model_execution_granted"])
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12a_module_does_not_add_runtime_execution_imports(self):
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
        for forbidden in UNSAFE_PHASE12A_SENTINELS:
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
