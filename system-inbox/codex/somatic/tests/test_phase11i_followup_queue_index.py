import copy
import json
import unittest
from pathlib import Path

from somatic.safety.phase11_contracts import (
    PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_BLOCKED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS,
    PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_STALE_STATUS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    _finalize_phase11i_acceptance_check,
    _finalize_phase11i_queue_index,
    _phase11h_record_hash,
    phase11_acceptance_followup_fixture_bundle,
    phase11_followup_queue_index_fixture_bundle,
    phase11_followup_queue_index_record,
    phase11_followup_queue_index_status_summary,
    validate_phase11_followup_queue_acceptance_check,
    validate_phase11_followup_queue_index_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11i-followup-queue-index-v1.json"
UNSAFE_PHASE11I_SENTINELS = (
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
    "accepted-for-runtime",
    "execution-permitted",
    "runtime-enabled",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase11IFollowupQueueIndexTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(QUEUE_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_followup_queue_index_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(fixture["fixture_kind"], "phase-11i-followup-queue-index")
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self._assert_no_private_values(fixture)

    def test_queue_indexes_are_compact_sanitized_and_non_executable(self):
        records = phase11_followup_queue_index_fixture_bundle()["queue_index_records"]
        followups = phase11_acceptance_followup_fixture_bundle()["followup_records"]
        expected_followup_hashes = {
            record["followup_id"]: _phase11h_record_hash(record) for record in followups.values()
        }

        document = records["document_ingestion_queue"]
        rf_booth = records["rf_booth_queue"]

        self.assertEqual(document["domain"], PHASE11_DOCUMENT_DOMAIN)
        self.assertEqual(document["status"], PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS)
        self.assertEqual(document["entry_count"], 3)
        self.assertEqual(
            document["queue_status_counts"][PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS], 1
        )
        self.assertEqual(
            document["queue_status_counts"][PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS], 2
        )
        self.assertEqual(document["unresolved_review_count"], 21)
        self.assertEqual(document["blocking_count"], 9)

        self.assertEqual(rf_booth["domain"], PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        self.assertEqual(rf_booth["status"], PHASE11_FOLLOWUP_QUEUE_STALE_STATUS)
        self.assertEqual(rf_booth["entry_count"], 3)
        self.assertEqual(
            rf_booth["queue_status_counts"][PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS], 1
        )
        self.assertEqual(
            rf_booth["queue_status_counts"][PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS], 1
        )
        self.assertEqual(rf_booth["stale_count"], 1)
        self.assertEqual(rf_booth["resolved_for_planning_count"], 1)

        for name, record in records.items():
            with self.subTest(record=name):
                result = validate_phase11_followup_queue_index_record(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertTrue(record["queue_id"].startswith("p11i-queue-"))
                self.assertEqual(len(record["queue_fingerprint"]), 64)
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self.assertNotIn("followup_records", record)
                self.assertNotIn("acceptance_records", record)
                self.assertNotIn("entries", record)
                self.assertNotIn("reviews", record)
                self.assertEqual(
                    record["included_followup_hashes"],
                    [
                        expected_followup_hashes[label]
                        for label in record["included_followup_labels"]
                    ],
                )
                self._assert_no_private_values(record)

    def test_queue_acceptance_checks_cover_allowed_statuses(self):
        checks = phase11_followup_queue_index_fixture_bundle()["queue_acceptance_checks"]
        expected = {
            "accepted_for_planning_queue": PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS,
            "blocked_queue": PHASE11_FOLLOWUP_QUEUE_BLOCKED_STATUS,
            "stale_queue": PHASE11_FOLLOWUP_QUEUE_STALE_STATUS,
            "rejected_queue": PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS,
            "archived_no_action": PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS,
            "needs_more_review": PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS,
        }

        self.assertEqual(set(checks), set(expected))
        for name, record in checks.items():
            with self.subTest(record=name):
                result = validate_phase11_followup_queue_acceptance_check(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(record["status"], expected[name])
                self.assertTrue(record["acceptance_id"].startswith("p11i-check-"))
                self.assertTrue(record["queue_label"].startswith("p11i-queue-"))
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self._assert_no_private_values(record)

    def test_status_summary_is_compact_for_public_surfaces(self):
        document = phase11_followup_queue_index_status_summary(domain=PHASE11_DOCUMENT_DOMAIN)
        rf_booth = phase11_followup_queue_index_status_summary(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN
        )

        self.assertEqual(document["status"], PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS)
        self.assertEqual(document["acceptance_status"], document["status"])
        self.assertEqual(rf_booth["status"], PHASE11_FOLLOWUP_QUEUE_STALE_STATUS)
        self.assertEqual(rf_booth["acceptance_status"], rf_booth["status"])
        for payload in (document, rf_booth):
            with self.subTest(domain=payload["domain"]):
                self.assertTrue(payload["queue_id"].startswith("p11i-queue-"))
                self.assertTrue(payload["acceptance_id"].startswith("p11i-check-"))
                self.assertEqual(len(payload["queue_fingerprint"]), 64)
                self.assertEqual(len(payload["acceptance_fingerprint"]), 64)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])
                self.assertNotIn("followup_records", payload)
                self.assertNotIn("acceptance_records", payload)
                self._assert_no_private_values(payload)

    def test_accepted_for_planning_queue_still_does_not_enable_runtime(self):
        followups = phase11_acceptance_followup_fixture_bundle()["followup_records"]
        resolved_queue = phase11_followup_queue_index_record(
            (followups["rf_booth_resolved_for_planning"],),
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )
        result = validate_phase11_followup_queue_index_record(resolved_queue)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(resolved_queue["status"], PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS)
        self.assertEqual(resolved_queue["resolved_for_planning_count"], 1)
        self.assertEqual(resolved_queue["unresolved_review_count"], 0)
        self.assertEqual(resolved_queue["blocking_count"], 0)
        self.assertFalse(resolved_queue["execution_permitted"])
        self.assertFalse(resolved_queue["real_mode_runtime_enabled"])

        runtime = copy.deepcopy(resolved_queue)
        runtime["execution_permitted"] = True
        runtime_result = validate_phase11_followup_queue_index_record(runtime)

        self.assertFalse(runtime_result.compatible)
        self.assertFalse(runtime_result.to_dict()["execution_permitted"])
        self.assertFalse(runtime_result.to_dict()["real_mode_runtime_enabled"])
        self._assert_no_private_values(runtime_result.sanitized_record)

    def test_validator_fails_closed_for_unsafe_or_contradictory_queue_indexes(self):
        queue = phase11_followup_queue_index_fixture_bundle()["queue_index_records"][
            "rf_booth_queue"
        ]
        cases = []

        missing = copy.deepcopy(queue)
        missing.pop("included_followup_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(queue)
        unsupported["queue_index_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        runtime = copy.deepcopy(queue)
        runtime["execution_permitted"] = True
        cases.append(("runtime", runtime))

        contradictory_count = copy.deepcopy(queue)
        contradictory_count["resolved_for_planning_count"] = 99
        cases.append(("contradictory-count", contradictory_count))

        contradictory_status = copy.deepcopy(queue)
        contradictory_status["status"] = PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS
        cases.append(("contradictory-status", contradictory_status))

        unsafe = copy.deepcopy(queue)
        unsafe["queue_id"] = "p11i-queue-source-id-c:/private"
        cases.append(("unsafe", unsafe))

        execution_wording = copy.deepcopy(queue)
        execution_wording["status"] = "accepted-for-runtime"
        cases.append(("execution-wording", execution_wording))

        unknown = copy.deepcopy(queue)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_followup_queue_index_record(payload)
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
                for sentinel in UNSAFE_PHASE11I_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_queue_index_enforces_declared_deterministic_ordering(self):
        queue = copy.deepcopy(
            phase11_followup_queue_index_fixture_bundle()["queue_index_records"]["rf_booth_queue"]
        )
        queue["included_followup_labels"] = list(reversed(queue["included_followup_labels"]))
        queue["included_followup_hashes"] = list(reversed(queue["included_followup_hashes"]))
        queue = _finalize_phase11i_queue_index(queue)

        result = validate_phase11_followup_queue_index_record(queue)

        self.assertFalse(result.compatible)
        self.assertIn("phase11i_queue_ordering_contradiction", result.errors)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_queue_builder_fails_closed_when_any_source_followup_is_invalid(self):
        followups = copy.deepcopy(phase11_acceptance_followup_fixture_bundle()["followup_records"])
        followups["document_reviewer_queue"]["execution_permitted"] = True

        queue = phase11_followup_queue_index_record(
            followups,
            domain=PHASE11_DOCUMENT_DOMAIN,
        )
        result = validate_phase11_followup_queue_index_record(queue)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(queue["domain"], "unknown")
        self.assertEqual(queue["status"], PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS)
        self.assertEqual(queue["included_followup_labels"], ["p11h-redacted-record"])
        self.assertFalse(queue["execution_permitted"])
        self.assertFalse(queue["real_mode_runtime_enabled"])
        self._assert_no_private_values(queue)

    def test_acceptance_validator_fails_closed_for_contradictory_status(self):
        check = phase11_followup_queue_index_fixture_bundle()["queue_acceptance_checks"][
            "accepted_for_planning_queue"
        ]
        contradictory = copy.deepcopy(check)
        contradictory["blocking_count"] = 1

        result = validate_phase11_followup_queue_acceptance_check(contradictory)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        self._assert_no_private_values(result.sanitized_record)

    def test_acceptance_validator_binds_queue_label_to_domain_and_fingerprint(self):
        fixture = phase11_followup_queue_index_fixture_bundle()
        document_queue = fixture["queue_index_records"]["document_ingestion_queue"]
        check = copy.deepcopy(fixture["queue_acceptance_checks"]["stale_queue"])
        check["queue_label"] = document_queue["queue_id"]
        check["queue_fingerprint"] = document_queue["queue_fingerprint"]
        check = _finalize_phase11i_acceptance_check(check)

        result = validate_phase11_followup_queue_acceptance_check(check)

        self.assertFalse(result.compatible)
        self.assertIn(
            "phase11i_queue_acceptance_queue_ref_contradiction",
            result.errors,
        )
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11I_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
