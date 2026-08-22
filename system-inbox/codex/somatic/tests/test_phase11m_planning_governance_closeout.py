import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase11_contracts as phase11_contracts_module
from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_planning_governance_closeout_index,
    phase11_planning_governance_closeout_status_summary,
    phase11_runtime_authorization_gap_ledger,
    validate_phase11_planning_governance_closeout_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_CLOSEOUT_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-11m-planning-governance-closeout-index-v1.json"
)
UNSAFE_PHASE11M_SENTINELS = (
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
    "model-execution-granted",
    "provider-execution-granted",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase11MPlanningGovernanceCloseoutTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(GOVERNANCE_CLOSEOUT_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_planning_governance_closeout_index()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["planning_governance_closeout_contract_version"],
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION,
        )
        self.assertTrue(fixture["closeout_index_id"].startswith("p11m-closeout-"))
        self.assertEqual(
            fixture["phase_range"],
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
        )
        self.assertEqual(
            fixture["covered_phase_count"],
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT,
        )
        self.assertEqual(
            fixture["domain_labels"],
            [PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN],
        )
        self.assertEqual(fixture["domain_count"], 2)
        self.assertEqual(
            fixture["final_status"],
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
        )
        self.assertEqual(fixture["runtime_authorization_status"], "not-authorized")
        self.assertEqual(fixture["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(
            fixture["next_phase_requirement"],
            "explicit-future-phase-required-before-runtime-work",
        )
        self.assertTrue(fixture["gap_ledger_id"].startswith("p11l-ledger-"))
        self.assertEqual(fixture["gap_ledger_phase_range"], "11A-11K")
        self.assertEqual(fixture["missing_future_gate_count"], 9)
        self.assertEqual(
            fixture["missing_future_gate_count"],
            len(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
        )
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["adapter_execution_granted"])
        self.assertFalse(fixture["provider_execution_granted"])
        self.assertFalse(fixture["model_execution_granted"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            set(fixture),
            {
                "planning_governance_closeout_contract_version",
                "closeout_index_id",
                "phase_range",
                "covered_phase_count",
                "final_status",
                "runtime_authorization_status",
                "readiness_gap",
                "next_phase_requirement",
                "gap_ledger_id",
                "gap_ledger_contract_version",
                "gap_ledger_phase_range",
                "domain_labels",
                "domain_count",
                "unresolved_review_count",
                "blocker_count",
                "stale_count",
                "missing_future_gate_count",
                "adapter_execution_granted",
                "provider_execution_granted",
                "model_execution_granted",
                "runtime_stage",
                "execution_permitted",
                "real_mode_runtime_enabled",
            },
        )
        for field in (
            "covered_phase_count",
            "domain_count",
            "unresolved_review_count",
            "blocker_count",
            "stale_count",
            "missing_future_gate_count",
        ):
            self.assertIs(type(fixture[field]), int)
        result = validate_phase11_planning_governance_closeout_index(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_for_public_surfaces(self):
        summary = phase11_planning_governance_closeout_status_summary()

        self.assertEqual(
            summary["planning_governance_closeout_contract_version"],
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION,
        )
        self.assertTrue(summary["closeout_index_id"].startswith("p11m-closeout-"))
        self.assertEqual(summary["phase_range"], "11A-11L")
        self.assertEqual(summary["covered_phase_count"], 12)
        self.assertEqual(summary["final_status"], "phase-11-planning-governance-complete")
        self.assertEqual(summary["runtime_authorization_status"], "not-authorized")
        self.assertEqual(summary["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(
            summary["next_phase_requirement"],
            "explicit-future-phase-required-before-runtime-work",
        )
        self.assertTrue(summary["gap_ledger_id"].startswith("p11l-ledger-"))
        self.assertEqual(summary["domain_count"], 2)
        self.assertEqual(summary["unresolved_review_count"], 21)
        self.assertEqual(summary["blocker_count"], 10)
        self.assertEqual(summary["stale_count"], 1)
        self.assertEqual(summary["missing_future_gate_count"], 9)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["adapter_execution_granted"])
        self.assertFalse(summary["provider_execution_granted"])
        self.assertFalse(summary["model_execution_granted"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self._assert_no_private_values(summary)

    def test_complete_closed_finalized_indexed_or_governance_complete_never_enable_runtime(self):
        closeout = phase11_planning_governance_closeout_index()
        result = validate_phase11_planning_governance_closeout_index(closeout)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(
            result.sanitized_record["final_status"], PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS
        )
        self.assertEqual(result.sanitized_record["runtime_authorization_status"], "not-authorized")
        self.assertFalse(result.sanitized_record["adapter_execution_granted"])
        self.assertFalse(result.sanitized_record["provider_execution_granted"])
        self.assertFalse(result.sanitized_record["model_execution_granted"])
        self.assertFalse(result.sanitized_record["execution_permitted"])
        self.assertFalse(result.sanitized_record["real_mode_runtime_enabled"])
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

        for wording in (
            "complete",
            "closed",
            "finalized",
            "indexed",
            "governance complete",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(closeout)
                unsafe["final_status"] = wording
                unsafe["runtime_authorization_status"] = "authorization-granted"
                unsafe["adapter_execution_granted"] = True
                unsafe["provider_execution_granted"] = True
                unsafe["model_execution_granted"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = phase11_contracts_module._finalize_phase11m_governance_closeout(unsafe)
                unsafe_result = validate_phase11_planning_governance_closeout_index(unsafe)

                self.assertFalse(unsafe_result.compatible)
                self.assertFalse(unsafe_result.to_dict()["execution_permitted"])
                self.assertFalse(unsafe_result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(unsafe_result.sanitized_record["adapter_execution_granted"])
                self.assertFalse(unsafe_result.sanitized_record["provider_execution_granted"])
                self.assertFalse(unsafe_result.sanitized_record["model_execution_granted"])

    def test_complete_gap_ledger_still_yields_not_authorized_closeout(self):
        ledger = copy.deepcopy(phase11_runtime_authorization_gap_ledger())
        ledger["domain_gap_summaries"][0]["unresolved_review_count"] = 0
        ledger["domain_gap_summaries"][0]["blocker_count"] = 0
        ledger["domain_gap_summaries"][0]["stale_count"] = 0
        ledger["domain_gap_summaries"][1]["unresolved_review_count"] = 0
        ledger["domain_gap_summaries"][1]["blocker_count"] = 0
        ledger["domain_gap_summaries"][1]["stale_count"] = 0
        ledger = phase11_contracts_module._finalize_phase11l_runtime_gap_ledger(ledger)
        closeout = phase11_planning_governance_closeout_index(ledger)
        result = validate_phase11_planning_governance_closeout_index(closeout)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.sanitized_record["runtime_authorization_status"], "not-authorized")
        self.assertEqual(
            result.sanitized_record["readiness_gap"], "real-mode-authorization-missing"
        )
        self.assertFalse(result.sanitized_record["adapter_execution_granted"])
        self.assertFalse(result.sanitized_record["provider_execution_granted"])
        self.assertFalse(result.sanitized_record["model_execution_granted"])
        self.assertFalse(result.sanitized_record["execution_permitted"])
        self.assertFalse(result.sanitized_record["real_mode_runtime_enabled"])

    def test_validator_fails_closed_for_unsafe_or_contradictory_closeouts(self):
        closeout = phase11_planning_governance_closeout_index()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(closeout)
        missing.pop("domain_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(closeout)
        unsupported["planning_governance_closeout_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(closeout)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        runtime = copy.deepcopy(closeout)
        runtime["adapter_execution_granted"] = True
        runtime["provider_execution_granted"] = True
        runtime["model_execution_granted"] = True
        runtime["execution_permitted"] = True
        runtime["real_mode_runtime_enabled"] = True
        cases.append(("runtime-grant", runtime))

        authorization = copy.deepcopy(closeout)
        authorization["runtime_authorization_status"] = "authorization-granted"
        cases.append(("authorization-wording", authorization))

        permission = copy.deepcopy(closeout)
        permission["next_phase_requirement"] = "runtime-permission-granted"
        cases.append(("permission-wording", permission))

        unsafe = copy.deepcopy(closeout)
        unsafe["readiness_gap"] = "https://example.invalid/api_key"
        cases.append(("unsafe", unsafe))

        boolean_count = copy.deepcopy(closeout)
        boolean_count["unresolved_review_count"] = True
        boolean_count = phase11_contracts_module._finalize_phase11m_governance_closeout(
            boolean_count
        )
        cases.append(("boolean-count", boolean_count))

        wrong_domains = copy.deepcopy(closeout)
        wrong_domains["domain_labels"] = list(reversed(wrong_domains["domain_labels"]))
        wrong_domains = phase11_contracts_module._finalize_phase11m_governance_closeout(
            wrong_domains
        )
        cases.append(("wrong-domain-order", wrong_domains))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_planning_governance_closeout_index(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE11M_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def _assert_no_private_values(self, payload):
        encoded = self._safe_encoded(payload)
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11M_SENTINELS:
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
            .replace("runtime_authorization_status", "runtime_status")
            .replace("authorization_status", "runtime_status")
            .replace("runtime_authorization_gap", "runtime_gap")
            .replace("explicit-future-phase-required-before-runtime-work", "future-phase-required")
        )


if __name__ == "__main__":
    unittest.main()
