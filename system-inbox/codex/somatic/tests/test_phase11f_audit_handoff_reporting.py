import copy
import json
import unittest
from pathlib import Path

from somatic.safety.phase11_contracts import (
    PHASE11_AUDIT_HANDOFF_STATUS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
    PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
    PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
    PHASE11_LIFECYCLE_STAGE_REVIEWED,
    PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_audit_handoff_fixture_bundle,
    phase11_audit_handoff_record,
    phase11_audit_handoff_status_summary,
    phase11_audit_index,
    phase11_document_ingestion_preflight_dossier,
    phase11_document_ingestion_review_record,
    phase11_dossier_decision_record,
    phase11_dossier_lifecycle_record,
    phase11_reviewer_signoff_metadata,
    phase11_wifi_csi_rf_booth_preflight_dossier,
    phase11_wifi_csi_rf_booth_review_record,
    validate_phase11_audit_handoff_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_HANDOFF_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11f-audit-handoff-v1.json"
UNSAFE_PHASE11F_SENTINELS = (
    "document-parsed.json",
    "document-mixed.json",
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
    "authorization",
    "password",
    "raw_document_text",
    "raw_csi",
    "raw_rf",
    "raw_values",
    "model_body",
    "parser_body",
    "provider_body",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase11FAuditHandoffReportingTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(AUDIT_HANDOFF_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_audit_handoff_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(
            fixture["fixture_kind"],
            "phase-11f-audit-handoff-reporting",
        )
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self._assert_no_private_values(fixture)

    def test_handoffs_are_compact_sanitized_and_non_executable(self):
        first = phase11_audit_handoff_fixture_bundle()
        second = phase11_audit_handoff_fixture_bundle()

        self.assertEqual(first, second)
        for handoff in first["handoffs"]:
            with self.subTest(domain=handoff["domain"]):
                result = validate_phase11_audit_handoff_record(handoff)
                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(handoff["status"], PHASE11_AUDIT_HANDOFF_STATUS)
                self.assertTrue(handoff["handoff_id"].startswith("p11f-handoff-"))
                self.assertEqual(len(handoff["handoff_fingerprint"]), 64)
                self.assertEqual(handoff["runtime_stage"], "not-implemented")
                self.assertFalse(handoff["execution_permitted"])
                self.assertFalse(handoff["real_mode_runtime_enabled"])
                self.assertNotIn("entries", handoff)
                self.assertNotIn("change_control_records", handoff)
                self.assertNotIn("reviewer_scope_coverage", handoff)
                self.assertNotIn("export_retention_policies", handoff)
                self.assertNotIn("dossiers", handoff)
                self.assertNotIn("records", handoff)
                self._assert_no_private_values(handoff)

    def test_status_summary_is_compact_for_public_surfaces(self):
        for domain in (PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN):
            with self.subTest(domain=domain):
                status = phase11_audit_handoff_status_summary(domain=domain)

                self.assertEqual(status["status"], PHASE11_AUDIT_HANDOFF_STATUS)
                self.assertEqual(status["runtime_stage"], "not-implemented")
                self.assertFalse(status["execution_permitted"])
                self.assertFalse(status["real_mode_runtime_enabled"])
                self.assertTrue(status["handoff_id"].startswith("p11f-handoff-"))
                self.assertEqual(len(status["handoff_fingerprint"]), 64)
                self.assertNotIn("contract_versions", status)
                self.assertNotIn("lifecycle_status_counts", status)
                self.assertNotIn("retention_export_policy_summary", status)
                self._assert_no_private_values(status)

    def test_completed_reviews_still_do_not_enable_runtime(self):
        reviewed_document = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        reviewed_rf = phase11_wifi_csi_rf_booth_preflight_dossier(
            phase11_wifi_csi_rf_booth_review_record()
        )
        index = phase11_audit_index(
            (
                phase11_dossier_lifecycle_record(
                    reviewed_document,
                    lifecycle_stage=PHASE11_LIFECYCLE_STAGE_REVIEWED,
                    signoff=phase11_reviewer_signoff_metadata(
                        verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
                    ),
                    decision_record=phase11_dossier_decision_record(
                        reviewed_document,
                        decision=PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
                    ),
                ),
                phase11_dossier_lifecycle_record(
                    reviewed_rf,
                    lifecycle_stage=PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
                    signoff=phase11_reviewer_signoff_metadata(
                        verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
                    ),
                    decision_record=phase11_dossier_decision_record(
                        reviewed_rf,
                        decision=(PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED),
                    ),
                ),
            )
        )

        for domain in (PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN):
            with self.subTest(domain=domain):
                handoff = phase11_audit_handoff_record(index, domain=domain)
                result = validate_phase11_audit_handoff_record(handoff)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(handoff["blocking_count"], 0)
                self.assertEqual(handoff["rejection_count"], 0)
                self.assertEqual(handoff["unresolved_review_count"], 0)
                self.assertTrue(handoff["reviewer_scope_coverage_summary"]["coverage_complete"])
                self.assertFalse(handoff["execution_permitted"])
                self.assertFalse(handoff["real_mode_runtime_enabled"])
                self._assert_no_private_values(handoff)

    def test_validator_fails_closed_for_unsafe_or_contradictory_handoffs(self):
        handoff = phase11_audit_handoff_record(domain=PHASE11_DOCUMENT_DOMAIN)
        cases = []

        missing = copy.deepcopy(handoff)
        missing.pop("audit_index_label")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(handoff)
        unsupported["audit_handoff_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        runtime = copy.deepcopy(handoff)
        runtime["execution_permitted"] = True
        cases.append(("runtime", runtime))

        wrong_count = copy.deepcopy(handoff)
        wrong_count["rejection_count"] = wrong_count["audit_index_entry_count"] + 1
        cases.append(("wrong-count", wrong_count))

        unsafe = copy.deepcopy(handoff)
        unsafe["handoff_id"] = "p11f-source-id-c:/private"
        cases.append(("unsafe", unsafe))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_audit_handoff_record(payload)
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
                for sentinel in UNSAFE_PHASE11F_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11F_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
