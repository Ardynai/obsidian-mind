import copy
import json
import unittest
from pathlib import Path

from somatic.safety.phase11_contracts import (
    PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    _finalize_phase11g_record,
    phase11_handoff_acceptance_fixture_bundle,
    phase11_handoff_acceptance_record,
    phase11_handoff_acceptance_status_summary,
    validate_phase11_handoff_acceptance_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11g-handoff-acceptance-v1.json"
UNSAFE_PHASE11G_SENTINELS = (
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


class Phase11GHandoffAcceptanceTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(ACCEPTANCE_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_handoff_acceptance_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(fixture["fixture_kind"], "phase-11g-handoff-acceptance")
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self._assert_no_private_values(fixture)

    def test_acceptance_records_are_compact_sanitized_and_non_executable(self):
        bundle = phase11_handoff_acceptance_fixture_bundle()
        records = bundle["acceptance_records"]

        expected_statuses = {
            "document_blocked": PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS,
            "rf_booth_accepted": PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS,
            "rf_booth_stale": PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS,
            "rejected": PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS,
        }
        for name, record in records.items():
            with self.subTest(record=name):
                result = validate_phase11_handoff_acceptance_record(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(record["status"], expected_statuses[name])
                self.assertTrue(record["acceptance_id"].startswith("p11g-acceptance-"))
                self.assertEqual(len(record["acceptance_fingerprint"]), 64)
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self.assertNotIn("handoff", record.get("acceptance_records", {}))
                self.assertNotIn("entries", record)
                self.assertNotIn("audit_index", record)
                self.assertNotIn("reviews", record)
                self.assertNotIn("records", record)
                self._assert_no_private_values(record)

    def test_status_summary_is_compact_for_public_surfaces(self):
        status = phase11_handoff_acceptance_status_summary(domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)

        self.assertEqual(status["status"], PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS)
        self.assertTrue(status["acceptance_id"].startswith("p11g-acceptance-"))
        self.assertEqual(len(status["acceptance_fingerprint"]), 64)
        self.assertTrue(status["accepted_for_planning"])
        self.assertFalse(status["blocked"])
        self.assertFalse(status["stale"])
        self.assertEqual(status["runtime_stage"], "not-implemented")
        self.assertFalse(status["execution_permitted"])
        self.assertFalse(status["real_mode_runtime_enabled"])
        self.assertNotIn("rejection_reasons", status)
        self.assertNotIn("blocking_reasons", status)
        self._assert_no_private_values(status)

    def test_accepted_for_planning_still_does_not_enable_runtime(self):
        accepted = phase11_handoff_acceptance_fixture_bundle()["acceptance_records"][
            "rf_booth_accepted"
        ]
        result = validate_phase11_handoff_acceptance_record(accepted)

        self.assertTrue(result.compatible, result.errors)
        self.assertTrue(accepted["accepted_for_planning"])
        self.assertFalse(accepted["blocked"])
        self.assertFalse(accepted["stale"])
        self.assertEqual(accepted["missing_review_count"], 0)
        self.assertEqual(accepted["unresolved_review_count"], 0)
        self.assertFalse(accepted["execution_permitted"])
        self.assertFalse(accepted["real_mode_runtime_enabled"])
        self.assertEqual(result.to_dict()["runtime_stage"], "not-implemented")
        self.assertFalse(result.to_dict()["execution_permitted"])
        self._assert_no_private_values(accepted)

    def test_explicit_non_handoff_input_fails_closed(self):
        invalid = phase11_handoff_acceptance_record(
            {"schema_version": 1, "not": "a-phase-11f-handoff"},
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )
        result = validate_phase11_handoff_acceptance_record(invalid)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(invalid["status"], PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS)
        self.assertFalse(invalid["accepted_for_planning"])
        self.assertTrue(invalid["blocked"])
        self.assertFalse(invalid["execution_permitted"])
        self.assertFalse(invalid["real_mode_runtime_enabled"])
        self._assert_no_private_values(invalid)

    def test_validator_fails_closed_for_unsafe_or_contradictory_acceptance(self):
        accepted = phase11_handoff_acceptance_record(domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        cases = []

        missing = copy.deepcopy(accepted)
        missing.pop("source_handoff_label")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(accepted)
        unsupported["handoff_acceptance_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        runtime = copy.deepcopy(accepted)
        runtime["execution_permitted"] = True
        cases.append(("runtime", runtime))

        contradiction = copy.deepcopy(accepted)
        contradiction["blocked"] = True
        cases.append(("contradiction", contradiction))

        stale_mismatch = copy.deepcopy(accepted)
        stale_mismatch["source_handoff_hash"] = "0" * 64
        cases.append(("stale-mismatch", stale_mismatch))

        unsafe = copy.deepcopy(accepted)
        unsafe["acceptance_id"] = "p11g-source-id-c:/private"
        cases.append(("unsafe", unsafe))

        unknown = phase11_handoff_acceptance_record(domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        unknown["domain"] = "unknown"
        unknown["acceptance_fingerprint"] = None
        unknown["acceptance_id"] = None
        # Recompute the fingerprint to prove the validator rejects the domain
        # contradiction itself, not merely a stale fingerprint.
        unknown = _finalize_phase11g_record(unknown)
        cases.append(("unknown-accepted", unknown))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase11_handoff_acceptance_record(payload)
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
                for sentinel in UNSAFE_PHASE11G_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE11G_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
