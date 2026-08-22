import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase11_contracts as phase11_contracts_module
from somatic.safety.phase11_contracts import (
    PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION,
    PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_review_trail_export_bundle,
    phase11_runtime_authorization_gap_ledger,
    phase11_runtime_authorization_gap_ledger_status_summary,
    validate_phase11_runtime_authorization_gap_ledger,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_GAP_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-11l-runtime-authorization-gap-ledger-v1.json"
)
UNSAFE_PHASE11L_SENTINELS = (
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


class Phase11LRuntimeGapLedgerTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(RUNTIME_GAP_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_runtime_authorization_gap_ledger()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["runtime_authorization_gap_ledger_contract_version"],
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION,
        )
        self.assertTrue(fixture["ledger_id"].startswith("p11l-ledger-"))
        self.assertEqual(
            fixture["source_phase_range"],
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE,
        )
        self.assertEqual(
            fixture["covered_phase_count"],
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT,
        )
        self.assertEqual(
            fixture["domain_labels"],
            [PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN],
        )
        self.assertEqual(
            fixture["authorization_status"],
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS,
        )
        self.assertEqual(fixture["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(
            fixture["missing_future_gates"],
            list(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
        )
        self.assertEqual(fixture["missing_future_gate_count"], 9)
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["adapter_execution_granted"])
        self.assertFalse(fixture["provider_execution_granted"])
        self.assertFalse(fixture["model_execution_granted"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            set(fixture),
            {
                "runtime_authorization_gap_ledger_contract_version",
                "ledger_id",
                "source_phase_range",
                "covered_phase_count",
                "domain_labels",
                "domain_gap_summaries",
                "authorization_status",
                "readiness_gap",
                "missing_future_gates",
                "missing_future_gate_count",
                "adapter_execution_granted",
                "provider_execution_granted",
                "model_execution_granted",
                "runtime_stage",
                "execution_permitted",
                "real_mode_runtime_enabled",
            },
        )
        for summary in fixture["domain_gap_summaries"]:
            self.assertEqual(
                set(summary),
                {
                    "domain_label",
                    "source_closeout_decision",
                    "source_closeout_status",
                    "unresolved_review_count",
                    "blocker_count",
                    "stale_count",
                    "missing_future_gate_count",
                },
            )
            self.assertIs(type(summary["unresolved_review_count"]), int)
            self.assertIs(type(summary["blocker_count"]), int)
            self.assertIs(type(summary["stale_count"]), int)
            self.assertIs(type(summary["missing_future_gate_count"]), int)
        result = validate_phase11_runtime_authorization_gap_ledger(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_for_public_surfaces(self):
        document = phase11_runtime_authorization_gap_ledger_status_summary(
            domain=PHASE11_DOCUMENT_DOMAIN,
        )
        rf_booth = phase11_runtime_authorization_gap_ledger_status_summary(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )

        self.assertEqual(document["ledger_id"], rf_booth["ledger_id"])
        self.assertEqual(document["source_phase_range"], "11A-11K")
        self.assertEqual(document["covered_phase_count"], 11)
        self.assertEqual(document["domain_label"], PHASE11_DOCUMENT_DOMAIN)
        self.assertEqual(rf_booth["domain_label"], PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        self.assertEqual(document["authorization_status"], "not-authorized")
        self.assertEqual(document["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(document["missing_future_gate_count"], 9)
        self.assertEqual(document["unresolved_review_count"], 21)
        self.assertEqual(document["blocker_count"], 9)
        self.assertEqual(rf_booth["unresolved_review_count"], 0)
        self.assertEqual(rf_booth["blocker_count"], 1)
        self.assertEqual(rf_booth["stale_count"], 1)
        for payload in (document, rf_booth):
            with self.subTest(domain=payload["domain_label"]):
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["adapter_execution_granted"])
                self.assertFalse(payload["provider_execution_granted"])
                self.assertFalse(payload["model_execution_granted"])
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])
                self._assert_no_private_values(payload)

    def test_ready_complete_closed_exported_or_ledgers_never_enable_runtime(self):
        export = copy.deepcopy(phase11_review_trail_export_bundle())
        for closeout in export["domain_closeouts"]:
            closeout["final_closeout_decision"] = PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION
            closeout["final_closeout_status"] = PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS
            closeout["unresolved_review_count"] = 0
            closeout["blocker_count"] = 0
            closeout["stale_count"] = 0
        export = phase11_contracts_module._finalize_phase11k_review_trail_export(export)
        ledger = phase11_runtime_authorization_gap_ledger(export)
        result = validate_phase11_runtime_authorization_gap_ledger(ledger)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.sanitized_record["authorization_status"], "not-authorized")
        self.assertFalse(result.sanitized_record["adapter_execution_granted"])
        self.assertFalse(result.sanitized_record["provider_execution_granted"])
        self.assertFalse(result.sanitized_record["model_execution_granted"])
        self.assertFalse(result.sanitized_record["execution_permitted"])
        self.assertFalse(result.sanitized_record["real_mode_runtime_enabled"])

        for wording in ("ready", "complete", "closed", "exported", "ledgered"):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(ledger)
                unsafe["authorization_status"] = wording
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = phase11_contracts_module._finalize_phase11l_runtime_gap_ledger(unsafe)
                unsafe_result = validate_phase11_runtime_authorization_gap_ledger(unsafe)

                self.assertFalse(unsafe_result.compatible)
                self.assertFalse(unsafe_result.to_dict()["execution_permitted"])
                self.assertFalse(unsafe_result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(unsafe_result.sanitized_record["adapter_execution_granted"])
                self.assertFalse(unsafe_result.sanitized_record["provider_execution_granted"])
                self.assertFalse(unsafe_result.sanitized_record["model_execution_granted"])

    def test_validator_fails_closed_for_unsafe_or_contradictory_ledgers(self):
        ledger = phase11_runtime_authorization_gap_ledger()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(ledger)
        missing.pop("domain_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(ledger)
        unsupported["runtime_authorization_gap_ledger_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(ledger)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        runtime = copy.deepcopy(ledger)
        runtime["adapter_execution_granted"] = True
        runtime["provider_execution_granted"] = True
        runtime["model_execution_granted"] = True
        cases.append(("runtime-grant", runtime))

        authorization = copy.deepcopy(ledger)
        authorization["authorization_status"] = "authorization-granted"
        cases.append(("authorization-wording", authorization))

        permission = copy.deepcopy(ledger)
        permission["missing_future_gates"] = ["runtime-permission-granted"]
        permission["missing_future_gate_count"] = 1
        cases.append(("permission-wording", permission))

        approved = copy.deepcopy(ledger)
        approved["authorization_status"] = "runtime-approved"
        cases.append(("approval-wording", approved))

        unsafe = copy.deepcopy(ledger)
        unsafe["readiness_gap"] = "https://example.invalid/api_key"
        cases.append(("unsafe", unsafe))

        boolean_count = copy.deepcopy(ledger)
        boolean_count["domain_gap_summaries"][0]["unresolved_review_count"] = True
        boolean_count = phase11_contracts_module._finalize_phase11l_runtime_gap_ledger(
            boolean_count
        )
        cases.append(("boolean-count", boolean_count))

        contradictory_status = copy.deepcopy(ledger)
        contradictory_status["domain_gap_summaries"][0]["source_closeout_decision"] = (
            PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION
        )
        contradictory_status = phase11_contracts_module._finalize_phase11l_runtime_gap_ledger(
            contradictory_status
        )
        cases.append(("contradictory-status", contradictory_status))

        wrong_order = copy.deepcopy(ledger)
        wrong_order["domain_gap_summaries"] = list(reversed(wrong_order["domain_gap_summaries"]))
        wrong_order = phase11_contracts_module._finalize_phase11l_runtime_gap_ledger(wrong_order)
        cases.append(("wrong-domain-order", wrong_order))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_runtime_authorization_gap_ledger(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE11L_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def _assert_no_private_values(self, payload):
        encoded = self._safe_encoded(payload)
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11L_SENTINELS:
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
            .replace("runtime_authorization_gap", "runtime_gap")
            .replace("authorization_status", "runtime_status")
        )


if __name__ == "__main__":
    unittest.main()
