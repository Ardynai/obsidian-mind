"""Phase 10A document-fixture evidence-pack tests.

Tests prove:
- deterministic evidence artifact and fingerprint
- artifact refs are run-relative path + SHA-256
- malformed/unsafe configs fail closed with sanitized errors
- no raw document body, private refs, absolute paths, URLs, credentials,
  source IDs, provider bodies, parser bodies, CSI/signal terms, or
  health/medical claims leak into artifacts
"""

import json
import tempfile
import unittest
from pathlib import Path

from somatic.evidence.document_evidence_pack import (
    DOCUMENT_EVIDENCE_KIND,
    DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF,
    DOCUMENT_EVIDENCE_PACK_CONTRACT,
    DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
    DOCUMENT_EVIDENCE_PROVIDER_KIND,
    classify_document_evidence_pack_compatibility,
    compute_document_evidence_pack_fingerprint,
    document_evidence_pack_artifact_metadata,
    validate_document_evidence_pack_v1,
)
from somatic.evidence.document_fixture import (
    DocumentFixtureEvidenceProvider,
    evaluate_document_fixture_refs,
)
from somatic.mock_runtime import run_mock_workflow
from somatic.sensors.evidence import (
    SENSOR_EVIDENCE_FORBIDDEN_KEYS,
    SENSOR_EVIDENCE_SCHEMA_VERSION,
    compute_sensor_evidence_fingerprint,
    sensor_evidence_payload_sha256,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

DOCUMENT_EXAMPLE = (
    REPO_ROOT / "examples" / "document-evidence-demo" / "document-fixture-workflow.yaml"
)

FORBIDDEN_DOC_WORDS = (
    "document-parsed.json",
    "document-mixed.json",
    "fixture://",
    "fixtures/",
    "raw_values",
    "samples",
    "payload",
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
    "authorization",
    "bearer",
    "credential",
)
FORBIDDEN_DOC_KEYS = frozenset(SENSOR_EVIDENCE_FORBIDDEN_KEYS)


class DocumentEvidencePackTests(unittest.TestCase):
    """Phase 10A document-fixture evidence-pack contract tests."""

    @staticmethod
    def _mask_phase11l_safe_terms(text):
        return (
            text.replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
            .replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace(
                "runtime_authorization_gap_ledger_contract_version",
                "runtime_gap_ledger_contract_version",
            )
        )

    def _read_json(self, path):
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    def _refresh(self, pack):
        pack["pack_id"] = None
        pack["pack_fingerprint"] = None
        fingerprint = sensor_evidence_payload_sha256(pack)
        pack["pack_fingerprint"] = fingerprint
        pack["pack_id"] = f"document-evidence-pack-{fingerprint[:16]}"
        return pack

    def _assert_doc_pack_sanitized(self, pack):
        self._assert_no_forbidden_doc_keys(pack)
        encoded = self._mask_phase11l_safe_terms(json.dumps(pack, sort_keys=True).lower())
        for forbidden in FORBIDDEN_DOC_WORDS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)
        self._assert_no_absolute_paths(pack)

    def _assert_no_forbidden_doc_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_DOC_KEYS)
                self._assert_no_forbidden_doc_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_doc_keys(item)

    def _assert_no_absolute_paths(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_absolute_paths(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_absolute_paths(item)
        elif isinstance(payload, str):
            normalized = payload.replace("\\", "/")
            self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), normalized)
            self.assertNotRegex(normalized, r"^[A-Za-z]:/")

    # -- deterministic artifact and fingerprint --

    def test_document_evidence_pack_is_deterministic_and_compatible(self):
        provider = DocumentFixtureEvidenceProvider()
        pack_a = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        pack_b = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(pack_a, pack_b)
        self.assertEqual(
            json.dumps(pack_a, sort_keys=True),
            json.dumps(pack_b, sort_keys=True),
        )
        self.assertEqual(pack_a["pack_fingerprint"], pack_b["pack_fingerprint"])
        self.assertEqual(pack_a["pack_id"], pack_b["pack_id"])
        self.assertTrue(pack_a["pack_id"].startswith("document-evidence-pack-"))

        result = validate_document_evidence_pack_v1(pack_a)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(result.classification, "compatible")
        self.assertTrue(result.fingerprint_verified)

        self.assertEqual(pack_a["schema_version"], SENSOR_EVIDENCE_SCHEMA_VERSION)
        self.assertEqual(pack_a["contract_version"], DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION)
        self.assertEqual(
            pack_a["evidence_contract_version"], DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION
        )
        self.assertEqual(pack_a["provider_kind"], DOCUMENT_EVIDENCE_PROVIDER_KIND)
        self.assertEqual(pack_a["evidence_kind"], DOCUMENT_EVIDENCE_KIND)
        self.assertEqual(pack_a["evidence_domain"], "document")
        self.assertEqual(pack_a["status"], "parsed")
        self.assertTrue(pack_a["metadata_only"])
        self.assertTrue(pack_a["fixture_only"])
        self.assertTrue(pack_a["deterministic"])
        self.assertTrue(pack_a["bounded"])
        self.assertTrue(pack_a["offline"])
        self.assertTrue(pack_a["local_only"])
        self.assertTrue(pack_a["non_diagnostic"])
        self.assertTrue(pack_a["fabric_pack_reference_safe"])
        self.assertFalse(pack_a["ranking_input"])
        self.assertFalse(pack_a["core_tournament_scores_modified"])
        self.assertFalse(pack_a["tournament_rankings_modified"])
        self.assertFalse(pack_a["hardware_access"])
        self.assertFalse(pack_a["network_calls"])
        self.assertFalse(pack_a["live_capture"])
        self.assertEqual(
            pack_a["adapter_status"]["adapter_kind"],
            "metadata-document-adapter",
        )
        self.assertEqual(
            pack_a["adapter_status"]["adapter_contract_version"],
            1,
        )
        self.assertIn(
            "no-raw-body-export",
            pack_a["adapter_status"]["capability_labels"],
        )
        self.assertIn(
            "no-source-id-export",
            pack_a["adapter_status"]["capability_labels"],
        )
        self.assertTrue(pack_a["adapter_status"]["fail_closed_output_validation"])
        self.assertFalse(pack_a["adapter_status"]["network_calls"])
        self.assertFalse(pack_a["adapter_status"]["document_bodies_exported"])
        self.assertFalse(pack_a["adapter_status"]["origin_ids_exported"])
        self.assertFalse(pack_a["adapter_status"]["absolute_paths_exported"])
        self.assertFalse(pack_a["adapter_status"]["urls_exported"])
        self.assertEqual(
            pack_a["adapter_status"]["real_mode_readiness_gate"]["status"],
            "blocked-fixture-reference-only",
        )
        self.assertEqual(
            pack_a["adapter_status"]["real_mode_readiness_gate"]["missing_gate_count"],
            7,
        )
        self.assertFalse(pack_a["adapter_status"]["real_mode_execution_permitted"])
        self.assertEqual(
            pack_a["adapter_output_validation"]["classification"],
            "compatible",
        )
        self.assertEqual(
            pack_a["adapter_output_validation"]["privacy_violation_count"],
            0,
        )

        self.assertEqual(pack_a["counts"]["document_count"], 3)
        self.assertEqual(pack_a["counts"]["parsed_document_count"], 3)
        self.assertEqual(pack_a["counts"]["fixture_count"], 1)
        self.assertGreater(pack_a["counts"]["total_word_count"], 0)
        self.assertGreater(pack_a["counts"]["total_line_count"], 0)
        self.assertGreater(pack_a["counts"]["total_char_count"], 0)

        self.assertEqual(pack_a["scores"]["evidence_quality"], 100)
        self.assertEqual(pack_a["scores"]["score"], 100)

        recomputed = compute_document_evidence_pack_fingerprint(pack_a)
        self.assertEqual(recomputed, pack_a["pack_fingerprint"])
        self.assertEqual(
            compute_sensor_evidence_fingerprint(pack_a),
            pack_a["pack_fingerprint"],
        )

        self._assert_doc_pack_sanitized(pack_a)

    def test_document_evidence_pack_partial_status_without_ranking(self):
        provider = DocumentFixtureEvidenceProvider()
        pack = provider.evidence_pack(
            ("document-mixed.json",),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(pack["status"], "partial")
        self.assertFalse(pack["ranking_input"])
        self.assertFalse(pack["core_tournament_scores_modified"])
        self.assertFalse(pack["tournament_rankings_modified"])
        self.assertEqual(pack["counts"]["parsed_document_count"], 1)
        self.assertEqual(pack["counts"]["partial_document_count"], 1)
        self.assertEqual(pack["counts"]["rejected_document_count"], 1)
        self.assertLess(pack["scores"]["evidence_quality"], 100)

        result = validate_document_evidence_pack_v1(pack)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(result.classification, "compatible")
        self._assert_doc_pack_sanitized(pack)

    def test_document_evidence_pack_fails_closed_on_missing_unsafe_refs(self):
        provider = DocumentFixtureEvidenceProvider()

        for bad_ref in (
            "../private.json",
            "/etc/passwd",
            "http://evil.com/doc.json",
            "no-such-file.json",
        ):
            with self.subTest(bad_ref=bad_ref):
                pack = provider.evidence_pack(
                    (bad_ref,),
                    repo_root=REPO_ROOT,
                )
                self.assertEqual(pack["status"], "rejected")
                self.assertEqual(pack["readiness_status"], "rejected-fail-closed")
                self.assertEqual(pack["scores"]["evidence_quality"], 0)
                result = validate_document_evidence_pack_v1(pack)
        self.assertEqual(result.classification, "compatible")
        self._assert_doc_pack_sanitized(pack)

    def test_document_artifact_metadata_sanitizes_phase11b_review_status(self):
        provider = DocumentFixtureEvidenceProvider()
        pack = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        pack["adapter_status"] = dict(pack["adapter_status"])
        pack["adapter_status"]["p11b_review_record_status"] = {
            "schema_version": 1,
            "review_record_contract_version": 1,
            "domain": "C:/private/source_id",
            "review_record_status": "https://example.invalid",
            "reviewed_gate_count": 7,
            "missing_gate_count": 0,
            "rejected_gate_count": 0,
            "planning_only": True,
            "metadata_only": True,
            "sanitized": True,
            "runtime_stage": "C:/private/source_id",
            "execution_permitted": True,
            "real_mode_runtime_enabled": True,
        }

        metadata = document_evidence_pack_artifact_metadata(pack)
        review_status = metadata["adapter_status"]["p11b_review_record_status"]
        encoded = (
            json.dumps(metadata, sort_keys=True)
            .lower()
            .replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
        )

        self.assertEqual(review_status["domain"], "unknown")
        self.assertEqual(review_status["review_record_status"], "rejected-fail-closed")
        self.assertEqual(review_status["runtime_stage"], "not-implemented")
        self.assertFalse(review_status["execution_permitted"])
        self.assertFalse(review_status["real_mode_runtime_enabled"])
        self.assertNotIn("c:/private", encoded)
        self.assertNotIn("source_id", encoded)
        self.assertNotIn("https://example.invalid", encoded)

    def test_document_artifact_metadata_sanitizes_phase11c_preflight_status(self):
        provider = DocumentFixtureEvidenceProvider()
        pack = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        pack["adapter_status"] = dict(pack["adapter_status"])
        pack["adapter_status"]["p11c_preflight_status"] = {
            "schema_version": 1,
            "preflight_packet_contract_version": 1,
            "domain": "C:/private/source_id",
            "preflight_packet_label": "C:/private/source_id",
            "preflight_packet_id": "C:/private/source_id",
            "preflight_packet_fingerprint": "not-a-hash",
            "preflight_status": "https://example.invalid",
            "reviewed_gate_count": 7,
            "missing_gate_count": 0,
            "rejected_gate_count": 0,
            "blocking_reason_count": 0,
            "planning_only": True,
            "metadata_only": True,
            "sanitized": True,
            "runtime_stage": "C:/private/source_id",
            "execution_permitted": True,
            "real_mode_runtime_enabled": True,
        }

        metadata = document_evidence_pack_artifact_metadata(pack)
        preflight = metadata["adapter_status"]["p11c_preflight_status"]
        encoded = json.dumps(metadata, sort_keys=True).lower()

        self.assertEqual(preflight["domain"], "unknown")
        self.assertEqual(preflight["preflight_packet_label"], "")
        self.assertEqual(preflight["preflight_packet_id"], "")
        self.assertEqual(preflight["preflight_packet_fingerprint"], "")
        self.assertEqual(preflight["preflight_status"], "rejected-fail-closed")
        self.assertEqual(preflight["runtime_stage"], "not-implemented")
        self.assertFalse(preflight["execution_permitted"])
        self.assertFalse(preflight["real_mode_runtime_enabled"])
        self.assertNotIn("c:/private", encoded)
        self.assertNotIn("source_id", encoded)
        self.assertNotIn("https://example.invalid", encoded)

    def test_document_artifact_metadata_sanitizes_phase11d_lifecycle_status(self):
        provider = DocumentFixtureEvidenceProvider()
        pack = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        pack["adapter_status"] = dict(pack["adapter_status"])
        pack["adapter_status"]["p11d_lifecycle_audit_status"] = {
            "schema_version": 1,
            "lifecycle_contract_version": 1,
            "domain": "C:/private/source_id",
            "lifecycle_record_id": "p11d-source-id-c:/private-device-id",
            "lifecycle_record_fingerprint": "not-a-hash",
            "lifecycle_stage": "https://example.invalid",
            "lifecycle_status": "https://example.invalid",
            "audit_decision": "https://example.invalid",
            "signoff_verdict": "https://example.invalid",
            "signoff_count": 1,
            "decision_count": 1,
            "comparison_changed_field_count": 0,
            "blocking_reason_count": 7,
            "planning_only": True,
            "metadata_only": True,
            "sanitized": True,
            "runtime_stage": "C:/private/source_id",
            "execution_permitted": True,
            "real_mode_runtime_enabled": True,
        }

        metadata = document_evidence_pack_artifact_metadata(pack)
        lifecycle = metadata["adapter_status"]["p11d_lifecycle_audit_status"]
        encoded = json.dumps(metadata, sort_keys=True).lower()

        self.assertEqual(lifecycle["domain"], "unknown")
        self.assertEqual(lifecycle["lifecycle_record_id"], "")
        self.assertEqual(lifecycle["lifecycle_record_fingerprint"], "")
        self.assertEqual(lifecycle["lifecycle_stage"], "rejected")
        self.assertEqual(lifecycle["lifecycle_status"], "rejected-runtime-disabled")
        self.assertEqual(lifecycle["audit_decision"], "needs-more-review")
        self.assertEqual(lifecycle["signoff_verdict"], "blockers")
        self.assertEqual(lifecycle["runtime_stage"], "not-implemented")
        self.assertFalse(lifecycle["execution_permitted"])
        self.assertFalse(lifecycle["real_mode_runtime_enabled"])
        self.assertNotIn("c:/private", encoded)
        self.assertNotIn("source_id", encoded)
        self.assertNotIn("https://example.invalid", encoded)

    def test_document_artifact_metadata_sanitizes_phase11e_audit_index_status(self):
        provider = DocumentFixtureEvidenceProvider()
        pack = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        pack["adapter_status"] = dict(pack["adapter_status"])
        pack["adapter_status"]["p11e_audit_index_status"] = {
            "schema_version": 1,
            "audit_index_contract_version": 1,
            "domain_scope": "multi-domain",
            "index_id": "p11e-source-id-c:/private-device-id",
            "index_fingerprint": "not-a-hash",
            "status": "https://example.invalid",
            "entry_count": 1,
            "created_count": 1,
            "reviewed_count": 0,
            "superseded_count": 0,
            "rejected_count": 0,
            "archived_count": 0,
            "decision_recorded_count": 0,
            "blocking_count": 7,
            "rejection_count": 0,
            "coverage_summary_count": 1,
            "supersession_chain_count": 1,
            "change_control_record_count": 0,
            "export_retention_policy_count": 1,
            "planning_only": True,
            "metadata_only": True,
            "sanitized": True,
            "runtime_stage": "C:/private/source_id",
            "execution_permitted": True,
            "real_mode_runtime_enabled": True,
        }

        metadata = document_evidence_pack_artifact_metadata(pack)
        audit_index = metadata["adapter_status"]["p11e_audit_index_status"]
        encoded = json.dumps(metadata, sort_keys=True).lower()

        self.assertEqual(audit_index["index_id"], "")
        self.assertEqual(audit_index["index_fingerprint"], "")
        self.assertEqual(audit_index["status"], "rejected-fail-closed")
        self.assertEqual(audit_index["runtime_stage"], "not-implemented")
        self.assertFalse(audit_index["execution_permitted"])
        self.assertFalse(audit_index["real_mode_runtime_enabled"])
        self.assertNotIn("c:/private", encoded)
        self.assertNotIn("source_id", encoded)
        self.assertNotIn("https://example.invalid", encoded)

    def test_document_artifact_metadata_sanitizes_phase11f_audit_handoff_status(self):
        provider = DocumentFixtureEvidenceProvider()
        pack = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        pack["adapter_status"] = dict(pack["adapter_status"])
        pack["adapter_status"]["p11f_audit_handoff_status"] = {
            "schema_version": 1,
            "audit_handoff_contract_version": 1,
            "domain": "document-ingestion",
            "handoff_id": "p11f-source-id-c:/private-device-id",
            "handoff_fingerprint": "not-a-hash",
            "status": "https://example.invalid",
            "audit_index_label": "p11e-source-id-c:/private-device-id",
            "audit_index_fingerprint": "not-a-hash",
            "audit_index_entry_count": 1,
            "created_count": 1,
            "reviewed_count": 0,
            "superseded_count": 0,
            "rejected_count": 0,
            "archived_count": 0,
            "decision_recorded_count": 0,
            "coverage_required_gate_count": 7,
            "coverage_covered_gate_count": 0,
            "coverage_missing_gate_count": 7,
            "blocking_count": 7,
            "rejection_count": 0,
            "unresolved_review_count": 7,
            "planning_only": True,
            "metadata_only": True,
            "sanitized": True,
            "runtime_stage": "C:/private/source_id",
            "execution_permitted": True,
            "real_mode_runtime_enabled": True,
        }

        metadata = document_evidence_pack_artifact_metadata(pack)
        handoff = metadata["adapter_status"]["p11f_audit_handoff_status"]
        encoded = json.dumps(metadata, sort_keys=True).lower()

        self.assertEqual(handoff["handoff_id"], "")
        self.assertEqual(handoff["handoff_fingerprint"], "")
        self.assertEqual(handoff["audit_index_label"], "")
        self.assertEqual(handoff["status"], "rejected-fail-closed")
        self.assertEqual(handoff["runtime_stage"], "not-implemented")
        self.assertFalse(handoff["execution_permitted"])
        self.assertFalse(handoff["real_mode_runtime_enabled"])
        self.assertNotIn("c:/private", encoded)
        self.assertNotIn("source_id", encoded)
        self.assertNotIn("https://example.invalid", encoded)

    # -- artifact refs are run-relative path + SHA-256 --

    def test_document_evidence_artifact_metadata_uses_run_relative_refs(self):
        provider = DocumentFixtureEvidenceProvider()
        pack = provider.evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )
        sha = "a" * 64
        metadata = document_evidence_pack_artifact_metadata(
            pack,
            artifact_sha256=sha,
        )

        self.assertEqual(
            metadata["artifact_ref"],
            DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF,
        )
        self.assertEqual(metadata["artifact_sha256"], sha)
        self.assertEqual(metadata["pack_fingerprint"], pack["pack_fingerprint"])
        self.assertEqual(metadata["provider_kind"], DOCUMENT_EVIDENCE_PROVIDER_KIND)
        self.assertEqual(metadata["evidence_kind"], DOCUMENT_EVIDENCE_KIND)
        self.assertTrue(metadata["metadata_only"])
        self.assertTrue(metadata["fixture_only"])
        self.assertTrue(metadata["summary_output_only"])
        self.assertEqual(
            metadata["adapter_status"]["adapter_kind"],
            "metadata-document-adapter",
        )
        self.assertIn(
            "no-absolute-path-export",
            metadata["adapter_status"]["capability_labels"],
        )
        self.assertEqual(
            metadata["adapter_output_validation"]["classification"],
            "compatible",
        )
        self.assertEqual(
            metadata["evidence_contract_version"],
            DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        )

        encoded = self._mask_phase11l_safe_terms(json.dumps(metadata, sort_keys=True).lower())
        for forbidden in FORBIDDEN_DOC_WORDS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    # -- contract classification --

    def test_document_contract_rejects_malformed_unsupported_and_private(self):
        good = DocumentFixtureEvidenceProvider().evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )

        non_object = classify_document_evidence_pack_compatibility(["not-a-pack"])
        self.assertEqual(non_object.classification, "malformed")
        self.assertEqual(non_object.readiness_status, "rejected-fail-closed")

        unsupported = dict(good)
        unsupported["contract_version"] = 2
        unsupported["evidence_contract_version"] = 2
        self._refresh(unsupported)
        self.assertEqual(
            validate_document_evidence_pack_v1(unsupported).classification,
            "unsupported_version",
        )

        stale = dict(good)
        stale["counts"] = dict(stale["counts"], document_count=999)
        result = validate_document_evidence_pack_v1(stale)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_fingerprint_or_pack_id", result.errors)

        missing_adapter = dict(good)
        missing_adapter.pop("adapter_status")
        missing_adapter.pop("adapter_output_validation")
        self._refresh(missing_adapter)
        result = validate_document_evidence_pack_v1(missing_adapter)
        self.assertEqual(result.classification, "malformed")
        self.assertIn("missing_required_fields", result.errors)

        private = dict(good)
        private["provider_payload_body"] = {"values": [1, 2, 3]}
        self._refresh(private)
        result = validate_document_evidence_pack_v1(private)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("privacy_boundary_violation", result.errors)

    # -- evaluation does not echo refs --

    def test_document_evaluation_does_not_echo_refs(self):
        evaluation = evaluate_document_fixture_refs(
            ("document-parsed.json", "../private.json"),
            repo_root=REPO_ROOT,
        )

        encoded = json.dumps(evaluation, sort_keys=True).lower()
        self.assertEqual(evaluation["status"], "partial")
        self.assertIn("unsafe-ref", evaluation["parse_error_categories"])
        self.assertNotIn("document-parsed.json", encoded)
        self.assertNotIn("../private.json", encoded)

    # -- no leakage into pack artifacts --

    def test_document_evidence_pack_forbids_all_privacy_violations(self):
        provider = DocumentFixtureEvidenceProvider()
        for refs in (
            ("document-parsed.json",),
            ("document-mixed.json",),
            ("document-parsed.json", "document-mixed.json"),
        ):
            with self.subTest(refs=refs):
                pack = provider.evidence_pack(refs, repo_root=REPO_ROOT)
                self._assert_doc_pack_sanitized(pack)

    # -- provider status boundary --

    def test_document_provider_status_metadata_boundary(self):
        provider = DocumentFixtureEvidenceProvider()
        status = provider.status()

        self.assertTrue(status["metadata_only"])
        self.assertTrue(status["fixture_only"])
        self.assertTrue(status["offline"])
        self.assertTrue(status["mock"])
        self.assertEqual(status["adapter_kind"], "metadata-document-adapter")
        self.assertEqual(status["adapter_contract_version"], 1)
        self.assertIn("no-network", status["adapter_boundary_labels"])
        self.assertIn("no-raw-body-export", status["adapter_boundary_labels"])
        self.assertIn("no-source-id-export", status["adapter_boundary_labels"])
        self.assertTrue(status["fail_closed_output_validation"])
        self.assertTrue(status["adapter_status"]["metadata_only"])
        self.assertFalse(status["hardware_access"])
        self.assertFalse(status["network_calls"])
        self.assertFalse(status["live_capture"])

    # -- contract identity --

    def test_document_evidence_contract_identity(self):
        contract = DOCUMENT_EVIDENCE_PACK_CONTRACT
        self.assertEqual(contract.identity.provider_kind, DOCUMENT_EVIDENCE_PROVIDER_KIND)
        self.assertEqual(contract.identity.evidence_kind, DOCUMENT_EVIDENCE_KIND)
        self.assertEqual(
            contract.identity.contract_version, DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION
        )
        self.assertEqual(
            contract.pack_id_prefix,
            "document-evidence-pack-",
        )

    # -- example workflow run writes refs without ranking changes --

    def test_document_example_run_writes_generic_refs_without_ranking_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                DOCUMENT_EXAMPLE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-document-fixture-test",
            )

            manifest = self._read_json(run_dir / "manifest.json")
            team_summary = self._read_json(run_dir / "artifacts" / "team_orchestrator_summary.json")
            doc_pack = self._read_json(run_dir / "artifacts" / "document_evidence_pack.json")
            ranked = self._read_json(run_dir / "artifacts" / "ranked_hypotheses.json")
            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")

        self.assertEqual(doc_pack["status"], "parsed")
        self.assertFalse(doc_pack["ranking_input"])
        self.assertFalse(doc_pack["core_tournament_scores_modified"])
        self.assertFalse(doc_pack["tournament_rankings_modified"])
        self.assertIn("document_evidence_pack", manifest["artifacts"])
        self.assertEqual(
            manifest["artifacts"]["document_evidence_pack"],
            "artifacts/document_evidence_pack.json",
        )
        manifest_ref = manifest["sensor_evidence_artifact_refs"]["document_evidence_pack"]
        summary_ref = team_summary["sensor_evidence_artifact_refs"]["document_evidence_pack"]
        for ref in (manifest_ref, summary_ref):
            self.assertEqual(ref["classification"], "compatible")
            self.assertEqual(
                ref["artifact_ref"],
                "artifacts/document_evidence_pack.json",
            )
            self.assertEqual(ref["sha256"], manifest["hashes"]["document_evidence_pack"])
            self.assertEqual(ref["pack_fingerprint"], doc_pack["pack_fingerprint"])
        self.assertEqual(
            team_summary["document_evidence_pack"]["pack_fingerprint"],
            doc_pack["pack_fingerprint"],
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["fixture_count"],
            1,
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["document_count"],
            3,
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["parsed_document_count"],
            3,
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["partial_document_count"],
            0,
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["rejected_document_count"],
            0,
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["readiness_status"],
            "ready-with-sanitized-metadata",
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["status_counts"]["parsed"],
            3,
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["document_adapter_status"]["adapter_kind"],
            "metadata-document-adapter",
        )
        self.assertIn(
            "no-url-export",
            team_summary["document_readiness_metadata"]["document_adapter_status"][
                "capability_labels"
            ],
        )
        self.assertEqual(
            team_summary["document_readiness_metadata"]["document_adapter_output_validation"][
                "classification"
            ],
            "compatible",
        )
        self.assertIn("Document Fixture Evidence", report)
        self.assertIn("Document count: 3", report)
        self.assertIn("Document adapter status: `metadata-only-ready`", report)
        self.assertIn("Document adapter validation: `compatible`", report)
        self.assertIn(
            "Document real-mode readiness gate: `blocked-fixture-reference-only`",
            report,
        )
        self.assertIn("Document real-mode missing gates: 7", report)
        self.assertIn(
            "Document generic evidence ref: `artifacts/document_evidence_pack.json`",
            report,
        )
        self.assertEqual(
            [item["rank"] for item in ranked],
            list(range(1, len(ranked) + 1)),
        )
        self.assertEqual(
            [item["final_score"] for item in ranked],
            sorted([item["final_score"] for item in ranked], reverse=True),
        )

        doc_encoded = self._mask_phase11l_safe_terms(json.dumps(doc_pack, sort_keys=True).lower())
        manifest_encoded = self._mask_phase11l_safe_terms(
            json.dumps(manifest, sort_keys=True).lower()
        )
        summary_encoded = self._mask_phase11l_safe_terms(
            json.dumps(team_summary, sort_keys=True).lower()
        )
        report_encoded = self._mask_phase11l_safe_terms(report.lower())
        for forbidden in FORBIDDEN_DOC_WORDS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, doc_encoded)
                self.assertNotIn(forbidden, manifest_encoded)
                self.assertNotIn(forbidden, summary_encoded)
                self.assertNotIn(forbidden, report_encoded)
        self.assertNotIn("document-parsed.json", summary_encoded)
        self.assertNotIn("document-parsed.json", report_encoded)


if __name__ == "__main__":
    unittest.main()
