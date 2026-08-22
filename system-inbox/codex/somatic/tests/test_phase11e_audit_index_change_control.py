import copy
import json
import unittest
from pathlib import Path

from somatic.safety.phase11_contracts import (
    PHASE11_AUDIT_INDEX_STATUS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
    PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
    PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
    PHASE11_LIFECYCLE_STAGE_REVIEWED,
    PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_audit_index,
    phase11_audit_index_fixture_bundle,
    phase11_audit_index_status_summary,
    phase11_document_ingestion_preflight_dossier,
    phase11_document_ingestion_review_record,
    phase11_dossier_decision_record,
    phase11_dossier_lifecycle_record,
    phase11_export_retention_policy,
    phase11_reviewer_signoff_metadata,
    phase11_wifi_csi_rf_booth_preflight_dossier,
    phase11_wifi_csi_rf_booth_review_record,
    validate_phase11_audit_index,
    validate_phase11_change_control_record,
    validate_phase11_export_retention_policy,
    validate_phase11_reviewer_scope_coverage,
    validate_phase11_supersession_chain,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_INDEX_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11e-audit-index-v1.json"
UNSAFE_PHASE11E_SENTINELS = (
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


class Phase11EAuditIndexChangeControlTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(AUDIT_INDEX_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_audit_index_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(
            fixture["fixture_kind"],
            "phase-11e-audit-index-change-control",
        )
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self._assert_no_private_values(fixture)

    def test_audit_index_is_deterministic_sanitized_and_non_executable(self):
        first = phase11_audit_index()
        second = phase11_audit_index()
        result = validate_phase11_audit_index(first)

        self.assertEqual(first, second)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(first["status"], PHASE11_AUDIT_INDEX_STATUS)
        self.assertEqual(first["runtime_stage"], "not-implemented")
        self.assertFalse(first["execution_permitted"])
        self.assertFalse(first["real_mode_runtime_enabled"])
        self.assertEqual(first["deterministic_ordering"], "sanitized-label-hash-v1")
        self.assertEqual(
            first["entries"],
            sorted(
                first["entries"],
                key=lambda entry: (
                    entry["entry_label"],
                    entry["lifecycle_record_fingerprint"],
                ),
            ),
        )
        self.assertNotIn("reviews", first)
        self.assertNotIn("gates", first)
        self._assert_no_private_values(first)

    def test_subrecords_validate_without_runtime_permission(self):
        fixture = phase11_audit_index_fixture_bundle()
        audit_index = fixture["audit_index"]

        for record in audit_index["change_control_records"]:
            with self.subTest(record=record["change_control_id"]):
                result = validate_phase11_change_control_record(record)
                self.assertTrue(result.compatible, result.errors)
                self.assertFalse(record["execution_permitted"])
                self._assert_no_private_values(record)

        for chain in audit_index["supersession_chains"]:
            with self.subTest(chain=chain["chain_id"]):
                result = validate_phase11_supersession_chain(chain)
                self.assertTrue(result.compatible, result.errors)
                self.assertFalse(chain["cross_domain_allowed"])
                self.assertFalse(chain["execution_permitted"])
                self._assert_no_private_values(chain)

        for coverage in audit_index["reviewer_scope_coverage"]:
            with self.subTest(coverage=coverage["coverage_id"]):
                result = validate_phase11_reviewer_scope_coverage(coverage)
                self.assertTrue(result.compatible, result.errors)
                self.assertFalse(coverage["execution_permitted"])
                self.assertNotIn("reviewer_label", coverage)
                self._assert_no_private_values(coverage)

        for policy in audit_index["export_retention_policies"]:
            with self.subTest(policy=policy["policy_id"]):
                result = validate_phase11_export_retention_policy(policy)
                self.assertTrue(result.compatible, result.errors)
                self.assertTrue(policy["local_only"])
                self.assertTrue(policy["payload_export_prohibited"])
                self.assertTrue(policy["external_upload_prohibited"])
                self.assertFalse(policy["execution_permitted"])
                self._assert_no_private_values(policy)

    def test_all_reviewed_records_still_do_not_enable_runtime(self):
        reviewed_document = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        reviewed_rf = phase11_wifi_csi_rf_booth_preflight_dossier(
            phase11_wifi_csi_rf_booth_review_record()
        )
        lifecycle_records = (
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
        index = phase11_audit_index(lifecycle_records)
        result = validate_phase11_audit_index(index)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(index["blocking_count"], 0)
        self.assertEqual(index["rejection_count"], 0)
        self.assertFalse(index["execution_permitted"])
        self.assertFalse(index["real_mode_runtime_enabled"])
        for coverage in index["reviewer_scope_coverage"]:
            self.assertTrue(coverage["coverage_complete"])
            self.assertFalse(coverage["execution_permitted"])
        self._assert_no_private_values(index)

    def test_validators_fail_closed_for_unsafe_or_contradictory_records(self):
        index = phase11_audit_index()
        cases = []

        unsupported = copy.deepcopy(index)
        unsupported["audit_index_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        runtime = copy.deepcopy(index)
        runtime["execution_permitted"] = True
        cases.append(("runtime", runtime))

        unsorted = copy.deepcopy(index)
        unsorted["entries"] = list(reversed(unsorted["entries"]))
        cases.append(("unsorted", unsorted))

        wrong_count = copy.deepcopy(index)
        wrong_count["blocking_count"] += 1
        cases.append(("wrong-count", wrong_count))

        unsafe = copy.deepcopy(index)
        unsafe["source_id"] = "source-id-c:/private"
        cases.append(("unsafe", unsafe))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_audit_index(payload)
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
                for sentinel in UNSAFE_PHASE11E_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_supersession_chain_rejects_cycles_and_cross_domain_drift(self):
        fixture = phase11_audit_index_fixture_bundle()["audit_index"]
        chain = copy.deepcopy(fixture["supersession_chains"][0])
        cycle = copy.deepcopy(chain)
        cycle["links"][1]["record_label"] = cycle["links"][0]["record_label"]
        cycle["links"][1]["record_fingerprint"] = cycle["links"][0]["record_fingerprint"]
        cross_domain = copy.deepcopy(chain)
        cross_domain["cross_domain_allowed"] = True
        missing_future = copy.deepcopy(chain)
        missing_future["links"][0]["future_record_label"] = ""

        for payload in (cycle, cross_domain, missing_future):
            result = validate_phase11_supersession_chain(payload)
            self.assertFalse(result.compatible)
            self.assertFalse(result.to_dict()["execution_permitted"])
            self._assert_no_private_values(result.sanitized_record)

    def test_change_control_and_policy_reject_runtime_or_private_values(self):
        fixture = phase11_audit_index_fixture_bundle()["audit_index"]
        change = copy.deepcopy(fixture["change_control_records"][0])
        change["current_lifecycle_record_label"] = "p11d-source-id-c:/private"
        change["execution_permitted"] = True
        policy = phase11_export_retention_policy(domain=PHASE11_DOCUMENT_DOMAIN)
        policy["export_class"] = "external-upload"

        for payload, validator in (
            (change, validate_phase11_change_control_record),
            (policy, validate_phase11_export_retention_policy),
        ):
            result = validator(payload)
            self.assertFalse(result.compatible)
            self.assertFalse(result.to_dict()["execution_permitted"])
            self._assert_no_private_values(result.sanitized_record)

    def test_status_summary_is_compact_and_runtime_disabled(self):
        for domain in (PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN):
            with self.subTest(domain=domain):
                status = phase11_audit_index_status_summary(domain=domain)

                self.assertEqual(status["status"], PHASE11_AUDIT_INDEX_STATUS)
                self.assertEqual(status["entry_count"], 1)
                self.assertEqual(status["runtime_stage"], "not-implemented")
                self.assertFalse(status["execution_permitted"])
                self.assertFalse(status["real_mode_runtime_enabled"])
                self.assertNotIn("entries", status)
                self.assertNotIn("change_control_records", status)
                self._assert_no_private_values(status)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11E_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
