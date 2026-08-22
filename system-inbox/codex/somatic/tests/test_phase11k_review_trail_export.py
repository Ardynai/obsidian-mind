import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase11_contracts as phase11_contracts_module
from somatic.safety.phase11_contracts import (
    PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION,
    PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS,
    PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
    PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION,
    PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT,
    PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE,
    PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_review_trail_export_bundle,
    phase11_review_trail_export_status_summary,
    validate_phase11_review_trail_export_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_TRAIL_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11k-review-trail-export-v1.json"
UNSAFE_PHASE11K_SENTINELS = (
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
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase11KReviewTrailExportTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(REVIEW_TRAIL_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_review_trail_export_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["review_trail_export_contract_version"],
            PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION,
        )
        self.assertTrue(fixture["export_id"].startswith("p11k-export-"))
        self.assertEqual(fixture["phase_range"], PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE)
        self.assertEqual(fixture["covered_phase_count"], PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT)
        self.assertEqual(
            fixture["domain_labels"],
            [PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN],
        )
        self.assertEqual(
            fixture["readiness_gap_summary"],
            PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        )
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            set(fixture),
            {
                "review_trail_export_contract_version",
                "export_id",
                "phase_range",
                "covered_phase_count",
                "domain_labels",
                "domain_closeouts",
                "readiness_gap_summary",
                "runtime_stage",
                "execution_permitted",
                "real_mode_runtime_enabled",
            },
        )
        for closeout in fixture["domain_closeouts"]:
            self.assertEqual(
                set(closeout),
                {
                    "domain_label",
                    "final_closeout_decision",
                    "final_closeout_status",
                    "unresolved_review_count",
                    "blocker_count",
                    "stale_count",
                },
            )
            self.assertIs(type(closeout["unresolved_review_count"]), int)
            self.assertIs(type(closeout["blocker_count"]), int)
            self.assertIs(type(closeout["stale_count"]), int)
        self.assertTrue(validate_phase11_review_trail_export_bundle(fixture).compatible)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_for_public_surfaces(self):
        document = phase11_review_trail_export_status_summary(
            domain=PHASE11_DOCUMENT_DOMAIN,
        )
        rf_booth = phase11_review_trail_export_status_summary(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )

        self.assertEqual(document["export_id"], rf_booth["export_id"])
        self.assertEqual(document["phase_range"], PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE)
        self.assertEqual(document["covered_phase_count"], PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT)
        self.assertEqual(document["domain_label"], PHASE11_DOCUMENT_DOMAIN)
        self.assertEqual(rf_booth["domain_label"], PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        self.assertEqual(document["final_closeout_decision"], "needs-new-review")
        self.assertEqual(document["final_closeout_status"], "incomplete")
        self.assertEqual(document["unresolved_review_count"], 21)
        self.assertEqual(document["blocker_count"], 9)
        self.assertEqual(rf_booth["final_closeout_decision"], "deferred")
        self.assertEqual(rf_booth["final_closeout_status"], "incomplete")
        self.assertEqual(rf_booth["stale_count"], 1)
        for payload in (document, rf_booth):
            with self.subTest(domain=payload["domain_label"]):
                self.assertEqual(
                    payload["readiness_gap_summary"],
                    PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
                )
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])
                self._assert_no_private_values(payload)

    def test_unknown_domain_status_summary_fails_closed(self):
        summary = phase11_review_trail_export_status_summary(
            domain="unknown-domain",
        )

        self.assertEqual(
            summary["final_closeout_decision"],
            PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
        )
        self.assertEqual(
            summary["final_closeout_status"],
            PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
        )
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self._assert_no_private_values(summary)

    def test_complete_exported_closed_trail_never_enables_runtime(self):
        export = copy.deepcopy(phase11_review_trail_export_bundle())
        for closeout in export["domain_closeouts"]:
            closeout["final_closeout_decision"] = PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION
            closeout["final_closeout_status"] = PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS
            closeout["unresolved_review_count"] = 0
            closeout["blocker_count"] = 0
            closeout["stale_count"] = 0
        export = phase11_contracts_module._finalize_phase11k_review_trail_export(export)

        result = validate_phase11_review_trail_export_bundle(export)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.sanitized_record["phase_range"], "11A-11J")
        self.assertEqual(result.sanitized_record["covered_phase_count"], 10)
        self.assertFalse(result.sanitized_record["execution_permitted"])
        self.assertFalse(result.sanitized_record["real_mode_runtime_enabled"])
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_validator_fails_closed_for_unsafe_or_contradictory_exports(self):
        export = phase11_review_trail_export_bundle()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(export)
        missing.pop("domain_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(export)
        unsupported["review_trail_export_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(export)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        runtime = copy.deepcopy(export)
        runtime["execution_permitted"] = True
        runtime["real_mode_runtime_enabled"] = True
        cases.append(("runtime", runtime))

        unsafe = copy.deepcopy(export)
        unsafe["readiness_gap_summary"] = "https://example.invalid/api_key"
        cases.append(("unsafe", unsafe))

        boolean_count = copy.deepcopy(export)
        boolean_count["domain_closeouts"][0]["unresolved_review_count"] = True
        boolean_count = phase11_contracts_module._finalize_phase11k_review_trail_export(
            boolean_count
        )
        cases.append(("boolean-count", boolean_count))

        contradictory_status = copy.deepcopy(export)
        contradictory_status["domain_closeouts"][0]["final_closeout_decision"] = (
            PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION
        )
        contradictory_status = phase11_contracts_module._finalize_phase11k_review_trail_export(
            contradictory_status
        )
        cases.append(("contradictory-status", contradictory_status))

        unknown_domain = copy.deepcopy(export)
        unknown_domain["domain_closeouts"][0]["domain_label"] = "unknown-domain"
        unknown_domain = phase11_contracts_module._finalize_phase11k_review_trail_export(
            unknown_domain
        )
        cases.append(("unknown-domain-closeout", unknown_domain))

        wrong_order = copy.deepcopy(export)
        wrong_order["domain_closeouts"] = list(reversed(wrong_order["domain_closeouts"]))
        wrong_order = phase11_contracts_module._finalize_phase11k_review_trail_export(wrong_order)
        cases.append(("wrong-domain-order", wrong_order))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_review_trail_export_bundle(payload)
                encoded = (
                    json.dumps(
                        (result.to_dict(), result.sanitized_record),
                        sort_keys=True,
                    )
                    .lower()
                    .replace("\\", "/")
                )

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE11K_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11K_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
