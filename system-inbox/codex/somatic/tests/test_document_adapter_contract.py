import json
import unittest
from pathlib import Path
from unittest.mock import patch

from somatic.evidence.document_adapter import (
    DOCUMENT_ADAPTER_CAPABILITY_LABELS,
    DOCUMENT_ADAPTER_CONTRACT_VERSION,
    DOCUMENT_ADAPTER_KIND,
    document_fixture_adapter_status,
    validate_document_adapter_output,
)
from somatic.evidence.document_evidence_pack import (
    build_document_evidence_pack,
    validate_document_evidence_pack_v1,
)
from somatic.evidence.document_fixture import (
    DocumentFixtureEvidenceProvider,
    evaluate_document_fixture_refs,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_ADAPTER_WORDS = (
    "document-parsed.json",
    "document-mixed.json",
    "fixture://",
    "fixtures/",
    "source_id",
    "source_ids",
    "provider_payload",
    "provider_payload_body",
    "parser_report_body",
    "parser_summary_body",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "bearer",
    "credential",
    "example.invalid",
)


class DocumentAdapterContractTests(unittest.TestCase):
    def test_fixture_adapter_status_is_metadata_only(self):
        status = document_fixture_adapter_status()

        self.assertEqual(status["adapter_contract_version"], DOCUMENT_ADAPTER_CONTRACT_VERSION)
        self.assertEqual(status["adapter_kind"], DOCUMENT_ADAPTER_KIND)
        self.assertEqual(status["capability_labels"], list(DOCUMENT_ADAPTER_CAPABILITY_LABELS))
        self.assertTrue(status["metadata_only"])
        self.assertTrue(status["fixture_only"])
        self.assertTrue(status["offline"])
        self.assertTrue(status["fail_closed_output_validation"])
        self.assertFalse(status["network_calls"])
        self.assertFalse(status["file_crawling"])
        self.assertFalse(status["pdf_parsing"])
        self.assertFalse(status["real_ingestion"])
        self.assertFalse(status["document_bodies_exported"])
        self.assertFalse(status["origin_ids_exported"])
        self.assertFalse(status["absolute_paths_exported"])
        self.assertFalse(status["urls_exported"])
        self.assertFalse(status["provider_bodies_exported"])
        self.assertFalse(status["parser_bodies_exported"])
        phase11 = status["p11a_contract_status"]
        self.assertEqual(phase11["domain"], "document-ingestion")
        self.assertEqual(phase11["status"], "planning-only-runtime-disabled")
        self.assertTrue(phase11["planning_only"])
        self.assertTrue(phase11["metadata_only"])
        self.assertEqual(phase11["runtime_stage"], "not-implemented")
        self.assertEqual(phase11["readiness_gate_missing_count"], 7)
        self.assertFalse(phase11["execution_permitted"])
        self.assertFalse(phase11["real_mode_runtime_enabled"])
        self.assertIn("p11a-contract-spec-only", status["capability_labels"])
        self.assertIn("real-mode-planning-only", status["capability_labels"])
        self.assertIn("no-runtime-enable", status["capability_labels"])
        self.assertIn("p11f-audit-handoff", status["capability_labels"])
        self.assertIn("p11g-handoff-acceptance", status["capability_labels"])
        self.assertIn("p11h-followup-remediation", status["capability_labels"])
        self.assertIn("p11i-followup-queue-index", status["capability_labels"])
        self.assertIn("p11j-decision-closeout", status["capability_labels"])
        self.assertIn("p11k-review-trail-export", status["capability_labels"])
        self.assertIn("p11l-runtime-gap-ledger", status["capability_labels"])
        self.assertIn("p11m-governance-closeout", status["capability_labels"])
        p11f = status["p11f_audit_handoff_status"]
        self.assertEqual(p11f["status"], "audit-handoff-runtime-disabled")
        self.assertEqual(p11f["runtime_stage"], "not-implemented")
        self.assertFalse(p11f["execution_permitted"])
        self.assertFalse(p11f["real_mode_runtime_enabled"])
        p11g = status["p11g_handoff_acceptance_status"]
        self.assertEqual(p11g["status"], "rejected-fail-closed")
        self.assertFalse(p11g["accepted_for_planning"])
        self.assertTrue(p11g["blocked"])
        self.assertEqual(p11g["runtime_stage"], "not-implemented")
        self.assertFalse(p11g["execution_permitted"])
        self.assertFalse(p11g["real_mode_runtime_enabled"])
        p11h = status["p11h_acceptance_followup_status"]
        self.assertEqual(p11h["status"], "rejected")
        self.assertEqual(p11h["followup_type"], "needs-more-review")
        self.assertEqual(p11h["runtime_stage"], "not-implemented")
        self.assertFalse(p11h["execution_permitted"])
        self.assertFalse(p11h["real_mode_runtime_enabled"])
        p11i = status["p11i_followup_queue_index_status"]
        self.assertEqual(p11i["status"], "needs-more-review")
        self.assertEqual(p11i["acceptance_status"], "needs-more-review")
        self.assertEqual(p11i["runtime_stage"], "not-implemented")
        self.assertFalse(p11i["execution_permitted"])
        self.assertFalse(p11i["real_mode_runtime_enabled"])
        p11j = status["p11j_decision_closeout_status"]
        self.assertEqual(p11j["closeout_decision"], "needs-new-review")
        self.assertEqual(p11j["closeout_status"], "incomplete")
        self.assertEqual(p11j["runtime_stage"], "not-implemented")
        self.assertFalse(p11j["execution_permitted"])
        self.assertFalse(p11j["real_mode_runtime_enabled"])
        p11k = status["p11k_review_trail_export_status"]
        self.assertEqual(p11k["phase_range"], "11A-11J")
        self.assertEqual(p11k["covered_phase_count"], 10)
        self.assertEqual(p11k["domain_label"], "document-ingestion")
        self.assertEqual(p11k["final_closeout_decision"], "needs-new-review")
        self.assertEqual(p11k["final_closeout_status"], "incomplete")
        self.assertEqual(p11k["readiness_gap_summary"], "real-mode-authorization-missing")
        self.assertEqual(p11k["runtime_stage"], "not-implemented")
        self.assertFalse(p11k["execution_permitted"])
        self.assertFalse(p11k["real_mode_runtime_enabled"])
        p11l = status["p11l_runtime_gap_ledger_status"]
        self.assertEqual(p11l["source_phase_range"], "11A-11K")
        self.assertEqual(p11l["covered_phase_count"], 11)
        self.assertEqual(p11l["domain_label"], "document-ingestion")
        self.assertEqual(p11l["authorization_status"], "not-authorized")
        self.assertEqual(p11l["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(p11l["missing_future_gate_count"], 9)
        self.assertEqual(p11l["runtime_stage"], "not-implemented")
        self.assertFalse(p11l["adapter_execution_granted"])
        self.assertFalse(p11l["provider_execution_granted"])
        self.assertFalse(p11l["model_execution_granted"])
        self.assertFalse(p11l["execution_permitted"])
        self.assertFalse(p11l["real_mode_runtime_enabled"])
        p11m = status["p11m_planning_governance_closeout_status"]
        self.assertEqual(p11m["phase_range"], "11A-11L")
        self.assertEqual(p11m["covered_phase_count"], 12)
        self.assertEqual(p11m["final_status"], "phase-11-planning-governance-complete")
        self.assertEqual(p11m["runtime_authorization_status"], "not-authorized")
        self.assertEqual(p11m["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(p11m["missing_future_gate_count"], 9)
        self.assertEqual(p11m["runtime_stage"], "not-implemented")
        self.assertFalse(p11m["adapter_execution_granted"])
        self.assertFalse(p11m["provider_execution_granted"])
        self.assertFalse(p11m["model_execution_granted"])
        self.assertFalse(p11m["execution_permitted"])
        self.assertFalse(p11m["real_mode_runtime_enabled"])
        self.assertEqual(
            status["real_mode_readiness_gate"]["status"],
            "blocked-fixture-reference-only",
        )
        self.assertEqual(status["real_mode_readiness_gate"]["missing_gate_count"], 7)
        self.assertFalse(status["real_mode_execution_permitted"])
        self._assert_no_adapter_leak(status)

    def test_fixture_evaluation_validates_before_pack_build(self):
        evaluation = evaluate_document_fixture_refs(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        result = validate_document_adapter_output(evaluation)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.classification, "compatible")
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.sanitized_output["status"], "parsed")
        self.assertEqual(result.sanitized_output["document_count"], 3)
        self.assertEqual(result.sanitized_output["status_counts"]["parsed"], 3)
        self._assert_no_adapter_leak(result.to_dict())
        self._assert_no_adapter_leak(result.sanitized_output)

    def test_unsafe_adapter_output_is_rejected_before_pack_build(self):
        unsafe = self._valid_adapter_output()
        unsafe.update(
            {
                "raw_document_text": "private body should not cross boundary",
                "source_id": "private-source",
                "absolute_path": "C:/Users/Josh/private/document.pdf",
                "url": "https://example.invalid/private",
                "provider_payload_body": {"body": "sk-private-value"},
            }
        )

        result = validate_document_adapter_output(unsafe)
        self.assertFalse(result.valid)
        self.assertEqual(result.classification, "incompatible")
        self.assertGreater(result.privacy_violation_count, 0)
        self.assertEqual(result.sanitized_output["status"], "rejected")
        self.assertEqual(result.sanitized_output["document_count"], 0)
        self.assertEqual(
            result.sanitized_output["parse_error_categories"],
            {"adapter-output-privacy-boundary": 1},
        )

        pack = build_document_evidence_pack(fixture_evaluation=unsafe)
        self.assertEqual(pack["status"], "rejected")
        self.assertEqual(pack["readiness_status"], "rejected-fail-closed")
        self.assertEqual(pack["counts"]["document_count"], 0)
        self.assertEqual(pack["adapter_output_validation"]["classification"], "incompatible")
        self.assertGreater(
            pack["adapter_output_validation"]["privacy_violation_count"],
            0,
        )
        pack_result = validate_document_evidence_pack_v1(pack)
        self.assertTrue(pack_result.compatible, pack_result.errors)
        self._assert_no_adapter_leak(result.to_dict())
        self._assert_no_adapter_leak(result.sanitized_output)
        self._assert_no_adapter_leak(pack)

    def test_provider_preserves_first_adapter_validation_result(self):
        unsafe = self._valid_adapter_output()
        unsafe.update(
            {
                "raw_document_text": "private body should not cross boundary",
                "source_id": "private-source",
                "url": "https://example.invalid/private",
            }
        )

        with patch(
            "somatic.evidence.document_fixture.evaluate_document_fixture_refs",
            return_value=unsafe,
        ):
            pack = DocumentFixtureEvidenceProvider().evidence_pack(
                ("document-parsed.json",),
                repo_root=REPO_ROOT,
            )

        self.assertEqual(pack["status"], "rejected")
        self.assertEqual(
            pack["adapter_output_validation"]["classification"],
            "incompatible",
        )
        self.assertGreater(
            pack["adapter_output_validation"]["privacy_violation_count"],
            0,
        )
        self.assertEqual(pack["counts"]["document_count"], 0)
        self.assertTrue(validate_document_evidence_pack_v1(pack).compatible)
        self._assert_no_adapter_leak(pack)

    def test_malformed_adapter_output_fails_closed_without_echo(self):
        for output in (
            ["not", "metadata"],
            {"status": "parsed", "document_count": 1},
        ):
            with self.subTest(output_type=type(output).__name__):
                result = validate_document_adapter_output(output)

                self.assertFalse(result.valid)
                self.assertEqual(result.sanitized_output["status"], "rejected")
                self.assertEqual(result.sanitized_output["document_count"], 0)
                self.assertEqual(result.sanitized_output["evidence_quality"], 0)
                self._assert_no_adapter_leak(result.to_dict())
                self._assert_no_adapter_leak(result.sanitized_output)

    def test_unknown_safe_adapter_fields_still_fail_closed(self):
        output = self._valid_adapter_output()
        output["extra_metadata"] = "public-looking but outside contract"

        result = validate_document_adapter_output(output)

        self.assertFalse(result.valid)
        self.assertIn("adapter_output_unknown_field", result.errors)
        self.assertEqual(result.sanitized_output["status"], "rejected")
        self._assert_no_adapter_leak(result.to_dict())
        self._assert_no_adapter_leak(result.sanitized_output)

    def _valid_adapter_output(self):
        return {
            "status": "parsed",
            "fixture_count": 1,
            "document_count": 1,
            "total_word_count": 10,
            "total_line_count": 2,
            "total_char_count": 50,
            "format_count": 1,
            "status_counts": {"parsed": 1, "partial": 0, "rejected": 0},
            "parse_error_categories": {},
            "error_count": 0,
            "warning_count": 0,
            "evidence_quality": 100,
            "replay_integrity": 100,
        }

    def _assert_no_adapter_leak(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower()
        self.assertNotRegex(encoded.replace("\\", "/"), r"[a-z]:/")
        self.assertNotIn("://", encoded)
        for forbidden in FORBIDDEN_ADAPTER_WORDS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)
        self.assertLessEqual(
            encoded.count("real-mode-authorization-missing"),
            3,
        )


if __name__ == "__main__":
    unittest.main()
