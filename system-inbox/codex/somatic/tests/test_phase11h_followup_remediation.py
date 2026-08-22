import copy
import json
import unittest
from pathlib import Path

from somatic.safety.phase11_contracts import (
    PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    _finalize_phase11h_record,
    phase11_acceptance_followup_fixture_bundle,
    phase11_acceptance_followup_record,
    phase11_acceptance_followup_status_summary,
    validate_phase11_acceptance_followup_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FOLLOWUP_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11h-followup-remediation-v1.json"
UNSAFE_PHASE11H_SENTINELS = (
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


class Phase11HFollowupRemediationTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(FOLLOWUP_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_acceptance_followup_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(fixture["fixture_kind"], "phase-11h-followup-remediation")
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self._assert_no_private_values(fixture)

    def test_followup_records_are_compact_sanitized_and_non_executable(self):
        records = phase11_acceptance_followup_fixture_bundle()["followup_records"]
        expected = {
            "document_blocker_disposition": (
                PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE,
                PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS,
            ),
            "document_reviewer_queue": (
                PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE,
                PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS,
            ),
            "document_needs_more_review": (
                PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
                PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS,
            ),
            "rf_booth_resolved_for_planning": (
                PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE,
                PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS,
            ),
            "rf_booth_stale_renewal": (
                PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE,
                PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS,
            ),
            "rf_booth_archived_no_action": (
                PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE,
                PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS,
            ),
            "rejected": (
                PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
                PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS,
            ),
        }

        self.assertEqual(set(records), set(expected))
        for name, record in records.items():
            with self.subTest(record=name):
                result = validate_phase11_acceptance_followup_record(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(record["followup_type"], expected[name][0])
                self.assertEqual(record["status"], expected[name][1])
                self.assertTrue(record["followup_id"].startswith("p11h-followup-"))
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self.assertNotIn("acceptance_records", record)
                self.assertNotIn("handoffs", record)
                self.assertNotIn("entries", record)
                self.assertNotIn("reviews", record)
                self.assertNotIn("rejection_reasons", record)
                self.assertNotIn("blocking_reasons", record)
                self._assert_no_private_values(record)

    def test_status_summary_is_compact_for_public_surfaces(self):
        document = phase11_acceptance_followup_status_summary(domain=PHASE11_DOCUMENT_DOMAIN)
        rf_booth = phase11_acceptance_followup_status_summary(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN
        )

        self.assertEqual(document["status"], PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS)
        self.assertEqual(
            document["followup_type"],
            PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
        )
        self.assertGreater(document["unresolved_review_count"], 0)
        self.assertEqual(rf_booth["status"], PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS)
        self.assertEqual(rf_booth["blocking_count"], 0)
        self.assertEqual(rf_booth["rejection_count"], 0)
        for payload in (document, rf_booth):
            with self.subTest(domain=payload["domain"]):
                self.assertTrue(payload["followup_id"].startswith("p11h-followup-"))
                self.assertEqual(len(payload["source_acceptance_hash"]), 64)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])
                self.assertNotIn("rejection_reasons", payload)
                self.assertNotIn("blocking_reasons", payload)
                self._assert_no_private_values(payload)

    def test_resolved_for_planning_still_does_not_enable_runtime(self):
        resolved = phase11_acceptance_followup_fixture_bundle()["followup_records"][
            "rf_booth_resolved_for_planning"
        ]
        result = validate_phase11_acceptance_followup_record(resolved)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(resolved["status"], PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS)
        self.assertEqual(resolved["unresolved_review_count"], 0)
        self.assertEqual(resolved["blocking_count"], 0)
        self.assertEqual(resolved["rejection_count"], 0)
        self.assertFalse(resolved["execution_permitted"])
        self.assertFalse(resolved["real_mode_runtime_enabled"])
        self.assertEqual(result.to_dict()["runtime_stage"], "not-implemented")
        self.assertFalse(result.to_dict()["execution_permitted"])

        runtime = copy.deepcopy(resolved)
        runtime["execution_permitted"] = True
        runtime = _finalize_phase11h_record(runtime)
        runtime_result = validate_phase11_acceptance_followup_record(runtime)

        self.assertFalse(runtime_result.compatible)
        self.assertFalse(runtime_result.to_dict()["execution_permitted"])
        self.assertFalse(runtime_result.to_dict()["real_mode_runtime_enabled"])
        self._assert_no_private_values(runtime_result.sanitized_record)

    def test_explicit_non_acceptance_input_fails_closed(self):
        invalid = phase11_acceptance_followup_record(
            {"schema_version": 1, "not": "a-phase-11g-acceptance"},
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )
        result = validate_phase11_acceptance_followup_record(invalid)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(invalid["status"], PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS)
        self.assertEqual(invalid["domain"], "unknown")
        self.assertFalse(invalid["execution_permitted"])
        self.assertFalse(invalid["real_mode_runtime_enabled"])
        self._assert_no_private_values(invalid)

    def test_validator_fails_closed_for_unsafe_or_contradictory_followups(self):
        followup = phase11_acceptance_followup_record(domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        cases = []

        missing = copy.deepcopy(followup)
        missing.pop("source_acceptance_label")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(followup)
        unsupported["acceptance_followup_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        runtime = copy.deepcopy(followup)
        runtime["execution_permitted"] = True
        cases.append(("runtime", runtime))

        contradiction = copy.deepcopy(followup)
        contradiction["blocking_count"] = 1
        cases.append(("contradiction", contradiction))

        unsafe = copy.deepcopy(followup)
        unsafe["followup_id"] = "p11h-source-id-c:/private"
        cases.append(("unsafe", unsafe))

        execution_wording = copy.deepcopy(followup)
        execution_wording["reviewer_queue_summary"] = "accepted-for-runtime"
        cases.append(("execution-wording", execution_wording))

        unknown = copy.deepcopy(followup)
        unknown["domain"] = "unknown"
        unknown = _finalize_phase11h_record(unknown)
        cases.append(("unknown-resolved", unknown))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_acceptance_followup_record(payload)
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
                for sentinel in UNSAFE_PHASE11H_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11H_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
