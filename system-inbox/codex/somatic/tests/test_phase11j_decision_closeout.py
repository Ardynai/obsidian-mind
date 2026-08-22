import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase11_contracts as phase11_contracts_module
from somatic.safety.phase11_contracts import (
    PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION,
    PHASE11_DECISION_CLOSEOUT_ARCHIVED_STATUS,
    PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION,
    PHASE11_DECISION_CLOSEOUT_BLOCKED_STATUS,
    PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION,
    PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS,
    PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION,
    PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS,
    PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION,
    PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
    PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_acceptance_followup_fixture_bundle,
    phase11_decision_closeout_fixture_bundle,
    phase11_decision_closeout_record,
    phase11_decision_closeout_status_summary,
    phase11_followup_queue_acceptance_check,
    phase11_followup_queue_index_fixture_bundle,
    phase11_followup_queue_index_record,
    validate_phase11_decision_closeout_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11j-decision-closeout-v1.json"
UNSAFE_PHASE11J_SENTINELS = (
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


class Phase11JDecisionCloseoutTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(CLOSEOUT_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_decision_closeout_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(fixture["fixture_kind"], "phase-11j-decision-closeout")
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self._assert_no_private_values(fixture)

    def test_closeouts_are_built_from_phase11i_queue_metadata_only(self):
        records = phase11_decision_closeout_fixture_bundle()["decision_closeout_records"]
        document = records["document_ingestion_closeout"]
        rf_booth = records["rf_booth_closeout"]

        self.assertEqual(document["domain"], PHASE11_DOCUMENT_DOMAIN)
        self.assertEqual(
            document["closeout_decision"],
            PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION,
        )
        self.assertEqual(document["closeout_status"], PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS)
        self.assertEqual(document["unresolved_review_count"], 21)
        self.assertEqual(document["blocker_count"], 9)

        self.assertEqual(rf_booth["domain"], PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        self.assertEqual(
            rf_booth["closeout_decision"],
            PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION,
        )
        self.assertEqual(rf_booth["closeout_status"], PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS)
        self.assertEqual(rf_booth["stale_count"], 1)
        self.assertEqual(rf_booth["deferred_count"], 1)

        for name, record in records.items():
            with self.subTest(record=name):
                result = validate_phase11_decision_closeout_record(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertTrue(record["closeout_id"].startswith("p11j-closeout-"))
                self.assertTrue(record["source_queue_label"].startswith("p11i-queue-"))
                self.assertEqual(len(record["source_queue_hash"]), 64)
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self.assertNotIn("queue_status_counts", record)
                self.assertNotIn("included_followup_labels", record)
                self.assertNotIn("followup_records", record)
                self.assertNotIn("queue_acceptance_checks", record)
                self._assert_no_private_values(record)

    def test_decision_closeouts_cover_phase11i_queue_statuses(self):
        followups = phase11_acceptance_followup_fixture_bundle()["followup_records"]
        cases = {
            "closed": (
                PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
                (followups["rf_booth_resolved_for_planning"],),
                PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION,
                PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS,
            ),
            "blocked": (
                PHASE11_DOCUMENT_DOMAIN,
                (followups["document_blocker_disposition"],),
                PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION,
                PHASE11_DECISION_CLOSEOUT_BLOCKED_STATUS,
            ),
            "deferred": (
                PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
                (followups["rf_booth_stale_renewal"],),
                PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION,
                PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS,
            ),
            "rejected": (
                "unknown",
                (followups["rejected"],),
                PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
                PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
            ),
            "archived": (
                PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
                (followups["rf_booth_archived_no_action"],),
                PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION,
                PHASE11_DECISION_CLOSEOUT_ARCHIVED_STATUS,
            ),
            "needs-review": (
                PHASE11_DOCUMENT_DOMAIN,
                (followups["document_needs_more_review"],),
                PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION,
                PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS,
            ),
        }

        for name, (domain, source_followups, decision, status) in cases.items():
            with self.subTest(case=name):
                queue = phase11_followup_queue_index_record(
                    source_followups,
                    domain=domain,
                )
                acceptance = phase11_followup_queue_acceptance_check(queue)
                closeout = phase11_decision_closeout_record(queue, acceptance)
                result = validate_phase11_decision_closeout_record(closeout)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(closeout["closeout_decision"], decision)
                self.assertEqual(closeout["closeout_status"], status)
                self.assertFalse(closeout["execution_permitted"])
                self.assertFalse(closeout["real_mode_runtime_enabled"])

    def test_closed_for_planning_still_cannot_enable_runtime(self):
        followups = phase11_acceptance_followup_fixture_bundle()["followup_records"]
        queue = phase11_followup_queue_index_record(
            (followups["rf_booth_resolved_for_planning"],),
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )
        closeout = phase11_decision_closeout_record(queue)
        result = validate_phase11_decision_closeout_record(closeout)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(
            closeout["closeout_decision"],
            PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION,
        )
        self.assertEqual(closeout["closeout_status"], PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS)
        self.assertFalse(closeout["execution_permitted"])
        self.assertFalse(closeout["real_mode_runtime_enabled"])

        runtime = copy.deepcopy(closeout)
        runtime["execution_permitted"] = True
        runtime_result = validate_phase11_decision_closeout_record(runtime)

        self.assertFalse(runtime_result.compatible)
        self.assertFalse(runtime_result.to_dict()["execution_permitted"])
        self.assertFalse(runtime_result.to_dict()["real_mode_runtime_enabled"])
        self._assert_no_private_values(runtime_result.sanitized_record)

    def test_builder_fails_closed_for_mismatched_phase11i_source_pair(self):
        phase11i = phase11_followup_queue_index_fixture_bundle()
        document_queue = phase11i["queue_index_records"]["document_ingestion_queue"]
        rf_queue = phase11i["queue_index_records"]["rf_booth_queue"]
        rf_acceptance = phase11_followup_queue_acceptance_check(rf_queue)

        closeout = phase11_decision_closeout_record(document_queue, rf_acceptance)
        result = validate_phase11_decision_closeout_record(closeout)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(closeout["domain"], "unknown")
        self.assertEqual(
            closeout["closeout_decision"],
            PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
        )
        self.assertEqual(closeout["closeout_status"], PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS)
        self.assertFalse(closeout["execution_permitted"])
        self.assertFalse(closeout["real_mode_runtime_enabled"])
        self._assert_no_private_values(closeout)

    def test_status_summary_is_compact_for_public_surfaces(self):
        document = phase11_decision_closeout_status_summary(domain=PHASE11_DOCUMENT_DOMAIN)
        rf_booth = phase11_decision_closeout_status_summary(domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)

        self.assertEqual(
            document["closeout_decision"],
            PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION,
        )
        self.assertEqual(rf_booth["closeout_decision"], PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION)
        for payload in (document, rf_booth):
            with self.subTest(domain=payload["domain"]):
                self.assertTrue(payload["closeout_id"].startswith("p11j-closeout-"))
                self.assertTrue(payload["source_queue_label"].startswith("p11i-queue-"))
                self.assertEqual(len(payload["source_queue_hash"]), 64)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])
                self.assertNotIn("queue_status_counts", payload)
                self.assertNotIn("included_followup_labels", payload)
                self._assert_no_private_values(payload)

    def test_validator_fails_closed_for_unsafe_or_contradictory_closeouts(self):
        closeout = phase11_decision_closeout_fixture_bundle()["decision_closeout_records"][
            "rf_booth_closeout"
        ]
        cases = []

        missing = copy.deepcopy(closeout)
        missing.pop("source_queue_label")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(closeout)
        unsupported["closeout_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        runtime = copy.deepcopy(closeout)
        runtime["real_mode_runtime_enabled"] = True
        cases.append(("runtime", runtime))

        contradictory_status = copy.deepcopy(closeout)
        contradictory_status["closeout_status"] = PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS
        cases.append(("contradictory-status", contradictory_status))

        contradictory_count = copy.deepcopy(closeout)
        contradictory_count["deferred_count"] = 0
        cases.append(("contradictory-count", contradictory_count))

        boolean_count = copy.deepcopy(closeout)
        boolean_count["stale_count"] = True
        boolean_count["deferred_count"] = True
        boolean_count = phase11_contracts_module._finalize_phase11j_closeout(boolean_count)
        cases.append(("boolean-count", boolean_count))

        unsafe = copy.deepcopy(closeout)
        unsafe["reviewer_disposition_summary"] = "https://example.invalid/source_id"
        cases.append(("unsafe", unsafe))

        execution_wording = copy.deepcopy(closeout)
        execution_wording["closeout_decision"] = "accepted-for-runtime"
        cases.append(("execution-wording", execution_wording))

        unknown = copy.deepcopy(closeout)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_decision_closeout_record(payload)
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
                for sentinel in UNSAFE_PHASE11J_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11J_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
