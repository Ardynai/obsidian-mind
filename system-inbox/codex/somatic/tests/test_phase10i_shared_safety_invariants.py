import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.mock_runtime import run_mock_workflow
from somatic.sensors.registry import sensor_evidence_provider_manifest
from tests.doctor_fixture import DOCTOR_RESULT

REPO_ROOT = Path(__file__).resolve().parents[1]
NOF1_WORKFLOW = REPO_ROOT / "fixtures" / "workflows" / "valid-n-of-1.yaml"
DOCUMENT_WORKFLOW = (
    REPO_ROOT / "examples" / "document-evidence-demo" / "document-fixture-workflow.yaml"
)
RELEASE_SUMMARY = REPO_ROOT / "fixtures" / "reports" / "sensor-evidence-subsystem-summary-v1.json"


PRIVATE_STRING_FRAGMENTS = (
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "invalid-utf8-csi",
    "environment-parsed.csv",
    "environment-mixed.csv",
    "toy-counter-parsed.csv",
    "toy-counter-mixed.csv",
    "document-fixture-pack.json",
    "fixture://",
    "fixtures/",
    "fixtures\\",
    "http://",
    "https://",
    "example.invalid",
    "source_id",
    "source_ids",
    "private_ref",
    "provider_payload",
    "provider_payload_body",
    "parser_report_body",
    "parser_summary_body",
    "provider_body",
    "parser_body",
    "model_body",
    "model weights",
    "device_id",
    "device_ids",
    "router_id",
    "router-secret",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "bearer private",
    "password",
    "raw_values",
    "raw_csi",
    "raw_rf",
    "raw_signal",
    "signal_values",
)

PRIVATE_KEY_NAMES = {
    "source_id",
    "source_ids",
    "provider_payload",
    "provider_payload_body",
    "parser_report_body",
    "parser_summary_body",
    "provider_body",
    "parser_body",
    "model_body",
    "model_weights",
    "device_id",
    "device_ids",
    "router_id",
    "router_ids",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "password",
}


class Phase10ISharedSafetyInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.output_root = Path(cls._tmp.name)
        cls.nof1_run = run_mock_workflow(
            NOF1_WORKFLOW,
            repo_root=REPO_ROOT,
            output_root=cls.output_root,
            run_id="run-phase10i-invariant-csi",
        )
        cls.document_run = run_mock_workflow(
            DOCUMENT_WORKFLOW,
            repo_root=REPO_ROOT,
            output_root=cls.output_root,
            run_id="run-phase10i-invariant-document",
        )

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_provider_manifest_and_listing_share_adapter_invariants(self):
        manifest = sensor_evidence_provider_manifest()
        json_exit, json_output = self._run_cli(["sensor-evidence", "providers", "--format", "json"])
        text_exit, text_output = self._run_cli(["sensor-evidence", "providers"])

        self.assertEqual(json_exit, 0)
        self.assertEqual(text_exit, 0)
        listing = json.loads(json_output)
        self.assertEqual(listing, manifest)
        self.assertEqual(
            listing["provider_order"],
            ["wifi-csi", "environment-fixture", "toy-counter-fixture", "document-fixture"],
        )
        self.assertTrue(listing["metadata_only"])
        self.assertTrue(listing["offline_fixture_only"])
        self.assertTrue(listing["sanitized"])

        providers = {provider["provider_id"]: provider for provider in listing["providers"]}
        self._assert_manifest_document_provider(providers["document-fixture"])
        self._assert_manifest_csi_provider(providers["wifi-csi"])
        self._assert_no_private_keys_or_string_values(listing, "provider manifest")
        self._assert_text_has_no_private_values(text_output, "provider listing")

    def test_doctor_reports_adapter_boundaries_without_private_values(self):
        exit_code, output = DOCTOR_RESULT

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "Sensor evidence provider registry: wifi-csi, environment-fixture, "
            "toy-counter-fixture, document-fixture",
            output,
        )
        self.assertIn("Sensor evidence registry validation: valid", output)
        self.assertIn("Sensor evidence registry output: sanitized metadata only", output)
        self.assertIn("Document fixture adapter: metadata-document-adapter", output)
        self.assertIn("Document real-mode readiness gate: blocked-fixture-reference-only", output)
        self.assertIn("Document real-mode execution permitted: false", output)
        self.assertIn("WiFi CSI source adapter: metadata-wifi-csi-source-adapter", output)
        self.assertIn("WiFi CSI real-mode readiness gate: blocked-fixture-reference-only", output)
        self.assertIn("WiFi CSI real-mode execution permitted: false", output)
        self.assertIn("WiFi CSI RuView posture: conditional-reference-only", output)
        self.assertIn("WiFi CSI booth-first profile: booth-first-single-subject-v1", output)
        self.assertIn("WiFi CSI RuView execution/import/vendor/model use: disabled", output)
        self.assertIn("Phase 11A real-mode contract specs: planning only, runtime disabled", output)
        self.assertIn("Phase 11A document contract runtime: not-implemented", output)
        self.assertIn("Phase 11A RF booth contract runtime: not-implemented", output)
        self.assertIn("Phase 11C preflight dossiers: planning packets only", output)
        self.assertIn("Phase 11C document preflight missing gates: 7", output)
        self.assertIn("Phase 11C RF booth preflight missing gates: 7", output)
        self.assertIn("Phase 11C preflight execution permitted: false", output)
        self.assertIn("Phase 11D dossier lifecycle audit: audit trail only", output)
        self.assertIn("Phase 11D document lifecycle stage: created", output)
        self.assertIn("Phase 11D RF booth lifecycle stage: created", output)
        self.assertIn("Phase 11D lifecycle audit execution permitted: false", output)
        self.assertIn("Phase 11E audit index/change control: local metadata only", output)
        self.assertIn(
            "Phase 11E document audit index status: audit-index-runtime-disabled",
            output,
        )
        self.assertIn("Phase 11E document audit index entries: 1", output)
        self.assertIn(
            "Phase 11E RF booth audit index status: audit-index-runtime-disabled",
            output,
        )
        self.assertIn("Phase 11E RF booth audit index entries: 1", output)
        self.assertIn("Phase 11E audit index execution permitted: false", output)
        self.assertIn(
            "Phase 11F audit handoffs: compact reporting only, runtime disabled",
            output,
        )
        self.assertIn(
            "Phase 11F document handoff status: audit-handoff-runtime-disabled",
            output,
        )
        self.assertIn(
            "Phase 11F RF booth handoff status: audit-handoff-runtime-disabled",
            output,
        )
        self.assertIn("Phase 11F audit handoff execution permitted: false", output)
        self.assertIn(
            "Phase 11G handoff acceptance checks: planning review only, runtime disabled",
            output,
        )
        self.assertIn(
            "Phase 11G document acceptance status: rejected-fail-closed",
            output,
        )
        self.assertIn("Phase 11G document accepted for planning: false", output)
        self.assertIn(
            "Phase 11G RF booth acceptance status: accepted-for-planning-runtime-disabled",
            output,
        )
        self.assertIn("Phase 11G RF booth accepted for planning: true", output)
        self.assertIn("Phase 11G handoff acceptance execution permitted: false", output)
        self.assertIn(
            "Phase 11H follow-up/remediation queues: planning only, runtime disabled",
            output,
        )
        self.assertIn("Phase 11H document follow-up status: rejected", output)
        self.assertIn("Phase 11H document follow-up type: needs-more-review", output)
        self.assertIn(
            "Phase 11H RF booth follow-up status: resolved-for-planning",
            output,
        )
        self.assertIn(
            "Phase 11H RF booth follow-up type: blocker-disposition",
            output,
        )
        self.assertIn(
            "Phase 11H follow-up/remediation execution permitted: false",
            output,
        )
        self.assertIn(
            "Phase 11I follow-up queue indexes: reviewer navigation only, runtime disabled",
            output,
        )
        self.assertIn("Phase 11I document queue status: needs-more-review", output)
        self.assertIn("Phase 11I RF booth queue status: stale-queue", output)
        self.assertIn("Phase 11I queue index execution permitted: false", output)
        self.assertIn("Phase 11K review trail export: reviewer navigation only", output)
        self.assertIn("Phase 11K readiness gap: real-mode-authorization-missing", output)
        self.assertIn("Phase 11K review trail export execution permitted: false", output)
        self.assertIn("Phase 11L runtime authorization gap ledger: metadata only", output)
        self.assertIn("Phase 11L authorization status: not-authorized", output)
        self.assertIn("Phase 11L missing future gates: 9", output)
        self.assertIn("Phase 11L runtime gap ledger execution permitted: false", output)
        self.assertIn("Phase 12A runtime authorization design charter: design only", output)
        self.assertIn("Phase 12A authorization status: not-authorized", output)
        self.assertIn("Phase 12A future required gates: 8", output)
        self.assertIn("Phase 12A execution permitted: false", output)
        self.assertIn(
            "Phase 12B runtime authorization record candidate: record candidate only",
            output,
        )
        self.assertIn("Phase 12B authorization status: not-authorized", output)
        self.assertIn("Phase 12B decision status: not-submitted", output)
        self.assertIn("Phase 12B grant status: no-grant", output)
        self.assertIn("Phase 12B future gates: 8", output)
        self.assertIn("Phase 12B execution permitted: false", output)
        self._assert_text_has_no_private_values(output, "doctor")

    def test_workflow_artifacts_and_reports_share_adapter_invariants(self):
        nof1_summary = self._read_json(self.nof1_run / "artifacts" / "n_of_1_summary.json")
        report_packet = self._read_json(self.nof1_run / "artifacts" / "n_of_1_report_packet.json")
        csi_pack = self._read_json(self.nof1_run / "artifacts" / "csi_evidence_pack.json")
        nof1_report = (self.nof1_run / "reports" / "report.md").read_text(encoding="utf-8")
        team_summary = self._read_json(
            self.document_run / "artifacts" / "team_orchestrator_summary.json"
        )
        document_pack = self._read_json(
            self.document_run / "artifacts" / "document_evidence_pack.json"
        )
        document_report = (self.document_run / "reports" / "report.md").read_text(encoding="utf-8")

        csi = nof1_summary["csi_metadata"]
        self.assertEqual(csi["reference_inventory_ref"], "csi-reference-inventory-v1")
        self.assertNotIn("fixtures/", csi["reference_inventory_ref"])
        self._assert_csi_source_adapter_status(csi["source_adapter_status"])
        self._assert_csi_pack(csi_pack)
        self._assert_nof1_report_packet(report_packet)
        self.assertIn("CSI reference inventory: `csi-reference-inventory-v1`", nof1_report)
        self.assertIn("CSI source adapter validation: `compatible`", nof1_report)
        self.assertIn(
            "CSI real-mode readiness gate: `blocked-fixture-reference-only`",
            nof1_report,
        )
        self.assertIn("CSI real-mode execution permitted: `False`", nof1_report)

        readiness = team_summary["document_readiness_metadata"]
        self.assertTrue(readiness["metadata_only"])
        self.assertTrue(readiness["fixture_only"])
        self.assertFalse(readiness["network_calls"])
        self.assertFalse(readiness["hardware_access"])
        self._assert_document_adapter_status(readiness["document_adapter_status"])
        self._assert_document_pack(document_pack)
        self.assertIn("Document Fixture Evidence", document_report)
        self.assertIn(
            "Document real-mode readiness gate: `blocked-fixture-reference-only`",
            document_report,
        )
        self.assertIn("Document real-mode execution permitted: `False`", document_report)

        for surface_name, payload in (
            ("n-of-1 summary", nof1_summary),
            ("n-of-1 report packet", report_packet),
            ("CSI evidence pack", csi_pack),
            ("document team summary", team_summary),
            ("document evidence pack", document_pack),
        ):
            self._assert_no_private_keys_or_string_values(payload, surface_name)
        self._assert_text_has_no_private_values(nof1_report, "n-of-1 report")
        self._assert_text_has_no_private_values(document_report, "document report")

    def test_artifact_inspect_outputs_cover_document_and_csi(self):
        csi_json_exit, csi_json = self._run_cli(
            [
                "sensor-evidence",
                "inspect",
                "--artifact",
                str(self.nof1_run / "artifacts" / "csi_evidence_pack.json"),
                "--format",
                "json",
            ]
        )
        csi_text_exit, csi_text = self._run_cli(
            [
                "sensor-evidence",
                "inspect",
                "--artifact",
                str(self.nof1_run / "artifacts" / "csi_evidence_pack.json"),
            ]
        )
        document_json_exit, document_json = self._run_cli(
            [
                "sensor-evidence",
                "inspect",
                "--artifact",
                str(self.document_run / "artifacts" / "document_evidence_pack.json"),
                "--format",
                "json",
            ]
        )
        document_text_exit, document_text = self._run_cli(
            [
                "sensor-evidence",
                "inspect",
                "--artifact",
                str(self.document_run / "artifacts" / "document_evidence_pack.json"),
            ]
        )

        self.assertEqual(csi_json_exit, 0)
        self.assertEqual(csi_text_exit, 0)
        self.assertEqual(document_json_exit, 0)
        self.assertEqual(document_text_exit, 0)
        csi_payload = json.loads(csi_json)
        document_payload = json.loads(document_json)
        self._assert_csi_inspect_payload(csi_payload)
        self._assert_document_inspect_payload(document_payload)

        for surface_name, payload in (
            ("CSI inspect JSON", csi_payload),
            ("document inspect JSON", document_payload),
        ):
            self._assert_no_private_keys_or_string_values(payload, surface_name)
        for surface_name, text in (
            ("CSI inspect text", csi_text),
            ("document inspect text", document_text),
        ):
            self._assert_text_has_no_private_values(text, surface_name)
            self.assertNotIn(
                str(self.output_root).replace("\\", "/").lower(), text.lower().replace("\\", "/")
            )

    def test_release_summary_machine_fixture_keeps_shared_invariants(self):
        summary = self._read_json(RELEASE_SUMMARY)

        self.assertEqual(summary["provider_count"], 4)
        providers = {provider["provider_id"]: provider for provider in summary["providers"]}
        self.assertEqual(
            [provider["provider_id"] for provider in summary["providers"]],
            ["wifi-csi", "environment-fixture", "toy-counter-fixture", "document-fixture"],
        )
        self.assertEqual(providers["wifi-csi"]["readiness_gate"], "real-mode-readiness-gate-v1")
        self.assertEqual(
            providers["document-fixture"]["readiness_gate"],
            "real-mode-readiness-gate-v1",
        )
        csi_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "csi-source-adapter-boundary"
        )
        document_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "document-adapter-boundary"
        )
        gate_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "real-mode-readiness-gate"
        )
        lifecycle_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11d-lifecycle-audit-records"
        )
        audit_index_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11e-audit-index-change-control"
        )
        audit_handoff_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11f-audit-handoff-reporting"
        )
        self.assertEqual(csi_surface["readiness_gate_status"], "blocked-fixture-reference-only")
        self.assertEqual(csi_surface["readiness_gate_missing_count"], 7)
        self.assertFalse(csi_surface["real_mode_execution_permitted"])
        self.assertEqual(
            document_surface["readiness_gate_status"], "blocked-fixture-reference-only"
        )
        self.assertEqual(document_surface["readiness_gate_missing_count"], 7)
        self.assertFalse(document_surface["real_mode_execution_permitted"])
        self.assertEqual(gate_surface["default_status"], "blocked-fixture-reference-only")
        self.assertFalse(gate_surface["real_mode_execution_permitted"])
        self.assertEqual(lifecycle_surface["default_stage"], "created")
        self.assertEqual(lifecycle_surface["default_decision"], "needs-more-review")
        self.assertEqual(lifecycle_surface["runtime_stage"], "not-implemented")
        self.assertFalse(lifecycle_surface["real_mode_execution_permitted"])
        self.assertEqual(
            audit_index_surface["default_status"],
            "audit-index-runtime-disabled",
        )
        self.assertEqual(audit_index_surface["runtime_stage"], "not-implemented")
        self.assertFalse(audit_index_surface["real_mode_execution_permitted"])
        self.assertEqual(
            audit_handoff_surface["default_status"],
            "audit-handoff-runtime-disabled",
        )
        self.assertEqual(audit_handoff_surface["runtime_stage"], "not-implemented")
        self.assertFalse(audit_handoff_surface["real_mode_execution_permitted"])
        self._assert_no_private_keys_or_string_values(summary, "release summary fixture")

    def _assert_manifest_document_provider(self, provider):
        self.assertEqual(provider["provider_kind"], "document-fixture")
        self.assertEqual(provider["evidence_kind"], "document-evidence-pack")
        self.assertEqual(provider["adapter_kind"], "metadata-document-adapter")
        self.assertTrue(provider["metadata_only"])
        self.assertTrue(provider["offline_fixture_only"])
        labels = set(provider["adapter_boundary_labels"])
        for label in (
            "metadata-only",
            "fixture-only",
            "offline",
            "no-network",
            "no-file-crawling",
            "no-pdf-parsing",
            "no-real-ingestion",
            "no-raw-body-export",
            "no-source-id-export",
            "no-absolute-path-export",
            "no-url-export",
            "p11a-contract-spec-only",
            "real-mode-planning-only",
            "no-runtime-enable",
            "p11b-review-record-fixture",
            "runtime-disabled-after-review",
            "p11c-preflight-dossier",
            "runtime-disabled-after-preflight",
            "p11d-lifecycle-audit-record",
            "runtime-disabled-after-audit",
            "p11e-audit-index",
            "change-control-only",
            "runtime-disabled-after-index",
            "p11f-audit-handoff",
            "reporting-only",
            "runtime-disabled-after-handoff",
            "p11g-handoff-acceptance",
            "accepted-for-planning-only",
            "runtime-disabled-after-acceptance",
            "p11h-followup-remediation",
            "planning-queue-only",
            "runtime-disabled-after-followup",
            "p11i-followup-queue-index",
            "reviewer-navigation-only",
            "runtime-disabled-after-queue-index",
            "p11j-decision-closeout",
            "planning-decision-metadata-only",
            "runtime-disabled-after-closeout",
            "p11k-review-trail-export",
            "review-trail-navigation-only",
            "runtime-disabled-after-review-trail-export",
            "p11l-runtime-gap-ledger",
            "runtime-disabled-after-gap-ledger",
            "p11m-governance-closeout",
            "runtime-disabled-after-governance-closeout",
        ):
            self.assertIn(label, labels)
        self._assert_manifest_gate(provider)
        self.assertEqual(provider["followup_queue_status"], "needs-more-review")
        self.assertEqual(provider["followup_queue_runtime_stage"], "not-implemented")
        self.assertFalse(provider["followup_queue_execution_permitted"])
        self.assertEqual(provider["decision_closeout_status"], "incomplete")
        self.assertEqual(
            provider["decision_closeout_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(provider["decision_closeout_execution_permitted"])
        self.assertEqual(provider["review_trail_phase_range"], "11A-11J")
        self.assertEqual(provider["review_trail_covered_phase_count"], 10)
        self.assertEqual(provider["review_trail_domain_label"], "document-ingestion")
        self.assertEqual(provider["review_trail_closeout_status"], "incomplete")
        self.assertEqual(provider["review_trail_runtime_stage"], "not-implemented")
        self.assertFalse(provider["review_trail_execution_permitted"])
        self.assertEqual(provider["runtime_gap_phase_range"], "11A-11K")
        self.assertEqual(provider["runtime_gap_covered_phase_count"], 11)
        self.assertEqual(provider["runtime_gap_domain_label"], "document-ingestion")
        self.assertEqual(provider["runtime_gap_authorization_status"], "not-authorized")
        self.assertEqual(provider["runtime_gap_runtime_stage"], "not-implemented")
        self.assertFalse(provider["runtime_gap_adapter_execution_granted"])
        self.assertFalse(provider["runtime_gap_provider_execution_granted"])
        self.assertFalse(provider["runtime_gap_model_execution_granted"])
        self.assertFalse(provider["runtime_gap_execution_permitted"])
        self.assertFalse(provider["runtime_gap_real_mode_runtime_enabled"])
        self._assert_manifest_governance_closeout(provider)

    def _assert_manifest_csi_provider(self, provider):
        self.assertEqual(provider["provider_kind"], "wifi-csi")
        self.assertEqual(provider["evidence_kind"], "csi-evidence-pack")
        self.assertEqual(provider["adapter_kind"], "metadata-wifi-csi-source-adapter")
        self.assertTrue(provider["metadata_only"])
        self.assertTrue(provider["offline_fixture_only"])
        labels = set(provider["adapter_boundary_labels"])
        for label in (
            "metadata-only",
            "reference-only",
            "offline",
            "fixture-backed",
            "no-hardware-access",
            "no-packet-capture",
            "no-monitor-mode",
            "no-esp32-flashing",
            "no-router-ap-control",
            "no-mqtt-udp-listener",
            "no-smart-home-bridge",
            "no-model-download",
            "no-model-execution",
            "no-vitals-inference",
            "no-care-claim",
            "rf-booth-review-only",
            "p11a-contract-spec-only",
            "real-mode-planning-only",
            "no-runtime-enable",
            "p11b-review-record-fixture",
            "runtime-disabled-after-review",
            "p11c-preflight-dossier",
            "runtime-disabled-after-preflight",
            "p11d-lifecycle-audit-record",
            "runtime-disabled-after-audit",
            "p11e-audit-index",
            "change-control-only",
            "runtime-disabled-after-index",
            "p11f-audit-handoff",
            "reporting-only",
            "runtime-disabled-after-handoff",
            "p11g-handoff-acceptance",
            "accepted-for-planning-only",
            "runtime-disabled-after-acceptance",
            "p11h-followup-remediation",
            "planning-queue-only",
            "runtime-disabled-after-followup",
            "p11i-followup-queue-index",
            "reviewer-navigation-only",
            "runtime-disabled-after-queue-index",
            "p11j-decision-closeout",
            "planning-decision-metadata-only",
            "runtime-disabled-after-closeout",
            "p11k-review-trail-export",
            "review-trail-navigation-only",
            "runtime-disabled-after-review-trail-export",
            "p11l-runtime-gap-ledger",
            "runtime-disabled-after-gap-ledger",
            "p11m-governance-closeout",
            "runtime-disabled-after-governance-closeout",
        ):
            self.assertIn(label, labels)
        self._assert_manifest_gate(provider)
        self.assertEqual(provider["followup_queue_status"], "stale-queue")
        self.assertEqual(provider["followup_queue_runtime_stage"], "not-implemented")
        self.assertFalse(provider["followup_queue_execution_permitted"])
        self.assertEqual(provider["decision_closeout_status"], "incomplete")
        self.assertEqual(
            provider["decision_closeout_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(provider["decision_closeout_execution_permitted"])
        self.assertEqual(provider["review_trail_phase_range"], "11A-11J")
        self.assertEqual(provider["review_trail_covered_phase_count"], 10)
        self.assertEqual(provider["review_trail_domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(provider["review_trail_closeout_status"], "incomplete")
        self.assertEqual(provider["review_trail_runtime_stage"], "not-implemented")
        self.assertFalse(provider["review_trail_execution_permitted"])
        self.assertEqual(provider["runtime_gap_phase_range"], "11A-11K")
        self.assertEqual(provider["runtime_gap_covered_phase_count"], 11)
        self.assertEqual(provider["runtime_gap_domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(provider["runtime_gap_authorization_status"], "not-authorized")
        self.assertEqual(provider["runtime_gap_runtime_stage"], "not-implemented")
        self.assertFalse(provider["runtime_gap_adapter_execution_granted"])
        self.assertFalse(provider["runtime_gap_provider_execution_granted"])
        self.assertFalse(provider["runtime_gap_model_execution_granted"])
        self.assertFalse(provider["runtime_gap_execution_permitted"])
        self.assertFalse(provider["runtime_gap_real_mode_runtime_enabled"])
        self._assert_manifest_governance_closeout(provider)

    def _assert_manifest_gate(self, provider):
        self.assertEqual(provider["readiness_gate_status"], "blocked-fixture-reference-only")
        self.assertEqual(len(provider["readiness_gate_required_gates"]), 7)
        self.assertEqual(
            provider["readiness_gate_missing_gates"],
            provider["readiness_gate_required_gates"],
        )
        self.assertFalse(provider["readiness_gate_ready"])
        self.assertFalse(provider["real_mode_execution_permitted"])
        self.assertEqual(provider["review_record_status"], "missing-required-reviews")
        self.assertEqual(provider["review_record_missing_gate_count"], 7)
        self.assertEqual(provider["review_record_reviewed_gate_count"], 0)
        self.assertEqual(provider["review_record_rejected_gate_count"], 0)
        self.assertEqual(provider["review_record_runtime_stage"], "not-implemented")
        self.assertFalse(provider["review_record_execution_permitted"])
        self.assertEqual(provider["preflight_packet_status"], "missing-required-records")
        self.assertEqual(provider["preflight_packet_missing_gate_count"], 7)
        self.assertEqual(provider["preflight_packet_reviewed_gate_count"], 0)
        self.assertEqual(provider["preflight_packet_rejected_gate_count"], 0)
        self.assertEqual(provider["preflight_packet_runtime_stage"], "not-implemented")
        self.assertFalse(provider["preflight_packet_execution_permitted"])
        self.assertTrue(provider["preflight_packet_id"].startswith("p11c-preflight-"))
        self.assertEqual(len(provider["preflight_packet_fingerprint"]), 64)
        self.assertEqual(provider["lifecycle_audit_stage"], "created")
        self.assertEqual(provider["lifecycle_audit_status"], "created-runtime-disabled")
        self.assertEqual(provider["lifecycle_audit_decision"], "needs-more-review")
        self.assertEqual(provider["lifecycle_audit_signoff_verdict"], "blockers")
        self.assertEqual(provider["lifecycle_audit_runtime_stage"], "not-implemented")
        self.assertFalse(provider["lifecycle_audit_execution_permitted"])
        self.assertTrue(provider["lifecycle_audit_record_id"].startswith("p11d-lifecycle-"))
        self.assertEqual(len(provider["lifecycle_audit_record_fingerprint"]), 64)
        self.assertEqual(provider["audit_index_status"], "audit-index-runtime-disabled")
        self.assertEqual(provider["audit_index_entry_count"], 1)
        self.assertEqual(provider["audit_index_blocking_count"], 8)
        self.assertEqual(provider["audit_index_rejection_count"], 0)
        self.assertEqual(provider["audit_index_runtime_stage"], "not-implemented")
        self.assertFalse(provider["audit_index_execution_permitted"])
        self.assertTrue(provider["audit_index_id"].startswith("p11e-index-"))
        self.assertEqual(len(provider["audit_index_fingerprint"]), 64)
        self.assertEqual(provider["handoff_status"], "audit-handoff-runtime-disabled")
        self.assertEqual(provider["handoff_runtime_stage"], "not-implemented")
        self.assertFalse(provider["handoff_execution_permitted"])
        self.assertTrue(provider["handoff_id"].startswith("p11f-handoff-"))
        self.assertEqual(len(provider["handoff_fingerprint"]), 64)

    def _assert_manifest_governance_closeout(self, provider):
        self.assertTrue(provider["governance_closeout_id"].startswith("p11m-closeout-"))
        self.assertEqual(provider["governance_closeout_phase_range"], "11A-11L")
        self.assertEqual(provider["governance_closeout_covered_phase_count"], 12)
        self.assertEqual(
            provider["governance_closeout_final_status"],
            "phase-11-planning-governance-complete",
        )
        self.assertEqual(
            provider["governance_closeout_runtime_authorization_status"],
            "not-authorized",
        )
        self.assertEqual(
            provider["governance_closeout_readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(provider["governance_closeout_runtime_stage"], "not-implemented")
        self.assertFalse(provider["governance_closeout_adapter_execution_granted"])
        self.assertFalse(provider["governance_closeout_provider_execution_granted"])
        self.assertFalse(provider["governance_closeout_model_execution_granted"])
        self.assertFalse(provider["governance_closeout_execution_permitted"])
        self.assertFalse(provider["governance_closeout_real_mode_runtime_enabled"])

    def _assert_document_adapter_status(self, status):
        self.assertEqual(status["adapter_kind"], "metadata-document-adapter")
        self.assertTrue(status["metadata_only"])
        self.assertTrue(status["fixture_only"])
        self.assertTrue(status["offline"])
        self.assertTrue(status["fail_closed_output_validation"])
        for flag in ("network_calls", "document_bodies_exported", "origin_ids_exported"):
            if flag in status:
                self.assertFalse(status[flag])
        labels = set(status["capability_labels"])
        for label in (
            "metadata-only",
            "fixture-only",
            "offline",
            "no-network",
            "no-file-crawling",
            "no-pdf-parsing",
            "no-real-ingestion",
            "no-raw-body-export",
            "no-source-id-export",
            "no-absolute-path-export",
            "no-url-export",
            "p11d-lifecycle-audit-record",
            "runtime-disabled-after-audit",
            "p11e-audit-index",
            "change-control-only",
            "runtime-disabled-after-index",
            "p11f-audit-handoff",
            "reporting-only",
            "runtime-disabled-after-handoff",
            "p11k-review-trail-export",
            "review-trail-navigation-only",
            "runtime-disabled-after-review-trail-export",
        ):
            self.assertIn(label, labels)
        self._assert_readiness_gate(status["real_mode_readiness_gate"])
        self.assertEqual(status["real_mode_readiness_status"], "blocked-fixture-reference-only")
        self.assertFalse(status["real_mode_execution_permitted"])
        p11a = status["p11a_contract_status"]
        self.assertEqual(p11a["status"], "planning-only-runtime-disabled")
        self.assertTrue(p11a["planning_only"])
        self.assertFalse(p11a["execution_permitted"])
        self.assertFalse(p11a["real_mode_runtime_enabled"])
        p11b = status["p11b_review_record_status"]
        self.assertEqual(p11b["review_record_status"], "missing-required-reviews")
        self.assertEqual(p11b["missing_gate_count"], 7)
        self.assertEqual(p11b["reviewed_gate_count"], 0)
        self.assertEqual(p11b["rejected_gate_count"], 0)
        self.assertFalse(p11b["execution_permitted"])
        self.assertFalse(p11b["real_mode_runtime_enabled"])
        p11c = status["p11c_preflight_status"]
        self.assertEqual(p11c["preflight_status"], "missing-required-records")
        self.assertEqual(p11c["missing_gate_count"], 7)
        self.assertEqual(p11c["reviewed_gate_count"], 0)
        self.assertEqual(p11c["rejected_gate_count"], 0)
        self.assertEqual(p11c["runtime_stage"], "not-implemented")
        self.assertFalse(p11c["execution_permitted"])
        self.assertFalse(p11c["real_mode_runtime_enabled"])
        p11d = status["p11d_lifecycle_audit_status"]
        self.assertEqual(p11d["lifecycle_stage"], "created")
        self.assertEqual(p11d["audit_decision"], "needs-more-review")
        self.assertEqual(p11d["signoff_verdict"], "blockers")
        self.assertEqual(p11d["runtime_stage"], "not-implemented")
        self.assertFalse(p11d["execution_permitted"])
        self.assertFalse(p11d["real_mode_runtime_enabled"])
        p11e = status["p11e_audit_index_status"]
        self.assertEqual(p11e["status"], "audit-index-runtime-disabled")
        self.assertEqual(p11e["entry_count"], 1)
        self.assertEqual(p11e["blocking_count"], 8)
        self.assertEqual(p11e["runtime_stage"], "not-implemented")
        self.assertFalse(p11e["execution_permitted"])
        self.assertFalse(p11e["real_mode_runtime_enabled"])
        p11f = status["p11f_audit_handoff_status"]
        self.assertEqual(p11f["status"], "audit-handoff-runtime-disabled")
        self.assertEqual(p11f["audit_index_entry_count"], 5)
        self.assertEqual(p11f["blocking_count"], 10)
        self.assertEqual(p11f["unresolved_review_count"], 8)
        self.assertEqual(p11f["runtime_stage"], "not-implemented")
        self.assertFalse(p11f["execution_permitted"])
        self.assertFalse(p11f["real_mode_runtime_enabled"])
        p11k = status["p11k_review_trail_export_status"]
        self.assertEqual(p11k["phase_range"], "11A-11J")
        self.assertEqual(p11k["covered_phase_count"], 10)
        self.assertEqual(p11k["domain_label"], "document-ingestion")
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
        self.assertEqual(p11m["runtime_stage"], "not-implemented")
        self.assertFalse(p11m["adapter_execution_granted"])
        self.assertFalse(p11m["provider_execution_granted"])
        self.assertFalse(p11m["model_execution_granted"])
        self.assertFalse(p11m["execution_permitted"])
        self.assertFalse(p11m["real_mode_runtime_enabled"])

    def _assert_csi_source_adapter_status(self, status):
        self.assertEqual(status["adapter_kind"], "metadata-wifi-csi-source-adapter")
        self.assertTrue(status["metadata_only"])
        self.assertTrue(status["reference_only"])
        self.assertTrue(status["fixture_backed"])
        self.assertTrue(status["offline"])
        self.assertTrue(status["fail_closed_output_validation"])
        for flag in (
            "hardware_access",
            "packet_capture",
            "monitor_mode",
            "wifi_network_probing",
            "network_calls",
            "esp32_flashing",
            "router_ap_control",
            "mqtt_udp_listener",
            "smart_home_bridge",
            "model_download",
            "model_execution",
            "vitals_inference",
            "medical_or_clinical_claim",
            "raw_signal_export",
        ):
            self.assertFalse(status[flag])
        self._assert_readiness_gate(status["real_mode_readiness_gate"])
        self.assertEqual(status["real_mode_readiness_status"], "blocked-fixture-reference-only")
        self.assertFalse(status["real_mode_execution_permitted"])
        p11a = status["p11a_contract_status"]
        self.assertEqual(p11a["status"], "planning-only-runtime-disabled")
        self.assertTrue(p11a["planning_only"])
        self.assertFalse(p11a["execution_permitted"])
        self.assertFalse(p11a["real_mode_runtime_enabled"])
        p11b = status["p11b_review_record_status"]
        self.assertEqual(p11b["review_record_status"], "missing-required-reviews")
        self.assertEqual(p11b["missing_gate_count"], 7)
        self.assertEqual(p11b["reviewed_gate_count"], 0)
        self.assertEqual(p11b["rejected_gate_count"], 0)
        self.assertFalse(p11b["execution_permitted"])
        self.assertFalse(p11b["real_mode_runtime_enabled"])
        p11c = status["p11c_preflight_status"]
        self.assertEqual(p11c["preflight_status"], "missing-required-records")
        self.assertEqual(p11c["missing_gate_count"], 7)
        self.assertEqual(p11c["reviewed_gate_count"], 0)
        self.assertEqual(p11c["rejected_gate_count"], 0)
        self.assertEqual(p11c["runtime_stage"], "not-implemented")
        self.assertFalse(p11c["execution_permitted"])
        self.assertFalse(p11c["real_mode_runtime_enabled"])
        p11d = status["p11d_lifecycle_audit_status"]
        self.assertEqual(p11d["lifecycle_stage"], "created")
        self.assertEqual(p11d["audit_decision"], "needs-more-review")
        self.assertEqual(p11d["signoff_verdict"], "blockers")
        self.assertEqual(p11d["runtime_stage"], "not-implemented")
        self.assertFalse(p11d["execution_permitted"])
        self.assertFalse(p11d["real_mode_runtime_enabled"])
        p11e = status["p11e_audit_index_status"]
        self.assertEqual(p11e["status"], "audit-index-runtime-disabled")
        self.assertEqual(p11e["entry_count"], 1)
        self.assertEqual(p11e["blocking_count"], 8)
        self.assertEqual(p11e["runtime_stage"], "not-implemented")
        self.assertFalse(p11e["execution_permitted"])
        self.assertFalse(p11e["real_mode_runtime_enabled"])
        p11f = status["p11f_audit_handoff_status"]
        self.assertEqual(p11f["status"], "audit-handoff-runtime-disabled")
        self.assertEqual(p11f["audit_index_entry_count"], 1)
        self.assertEqual(p11f["blocking_count"], 0)
        self.assertEqual(p11f["unresolved_review_count"], 0)
        self.assertEqual(p11f["runtime_stage"], "not-implemented")
        self.assertFalse(p11f["execution_permitted"])
        self.assertFalse(p11f["real_mode_runtime_enabled"])
        p11k = status["p11k_review_trail_export_status"]
        self.assertEqual(p11k["phase_range"], "11A-11J")
        self.assertEqual(p11k["covered_phase_count"], 10)
        self.assertEqual(p11k["domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(p11k["final_closeout_status"], "incomplete")
        self.assertEqual(p11k["readiness_gap_summary"], "real-mode-authorization-missing")
        self.assertEqual(p11k["runtime_stage"], "not-implemented")
        self.assertFalse(p11k["execution_permitted"])
        self.assertFalse(p11k["real_mode_runtime_enabled"])
        p11l = status["p11l_runtime_gap_ledger_status"]
        self.assertEqual(p11l["source_phase_range"], "11A-11K")
        self.assertEqual(p11l["covered_phase_count"], 11)
        self.assertEqual(p11l["domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(p11l["authorization_status"], "not-authorized")
        self.assertEqual(p11l["readiness_gap"], "real-mode-authorization-missing")
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
        self.assertEqual(p11m["runtime_stage"], "not-implemented")
        self.assertFalse(p11m["adapter_execution_granted"])
        self.assertFalse(p11m["provider_execution_granted"])
        self.assertFalse(p11m["model_execution_granted"])
        self.assertFalse(p11m["execution_permitted"])
        self.assertFalse(p11m["real_mode_runtime_enabled"])

    def _assert_readiness_gate(self, gate):
        self.assertEqual(gate["status"], "blocked-fixture-reference-only")
        self.assertFalse(gate["ready"])
        self.assertFalse(gate["execution_permitted"])
        self.assertFalse(gate["real_mode_runtime_enabled"])
        self.assertEqual(gate["missing_gate_count"], 7)
        self.assertEqual(len(gate["required_gates"]), 7)

    def _assert_csi_pack(self, pack):
        self.assertEqual(pack["id"], "csi-sanitized-evidence-pack")
        self.assertEqual(pack["status"], "parsed")
        self.assertTrue(pack["metadata_only"])
        self.assertTrue(pack["fixture_only"])
        self.assertTrue(pack["offline"])
        self.assertFalse(pack["hardware_access"])
        self.assertFalse(pack["network_calls"])
        self.assertFalse(pack["packet_capture"])
        self.assertFalse(pack["monitor_mode"])
        self.assertFalse(pack["raw_csi_data_collected"])
        self.assertFalse(pack["raw_csi_data_exported"])
        self.assertFalse(pack["raw_signal_values_exported"])
        self.assertFalse(pack["medical_or_clinical_claim"])
        self.assertFalse(pack["ranking_input"])
        self.assertFalse(pack["core_tournament_scores_modified"])
        self.assertFalse(pack["tournament_rankings_modified"])

    def _assert_document_pack(self, pack):
        self.assertEqual(pack["provider_kind"], "document-fixture")
        self.assertEqual(pack["evidence_kind"], "document-evidence-pack")
        self.assertTrue(pack["metadata_only"])
        self.assertTrue(pack["fixture_only"])
        self.assertTrue(pack["offline"])
        self.assertFalse(pack["hardware_access"])
        self.assertFalse(pack["network_calls"])
        self.assertFalse(pack["live_capture"])
        self._assert_document_adapter_status(pack["adapter_status"])

    def _assert_nof1_report_packet(self, packet):
        self.assertTrue(packet["offline"])
        self.assertTrue(packet["local_only"])
        self.assertFalse(packet["hardware_access"])
        self.assertFalse(packet["network_calls"])
        self.assertFalse(packet["medical_or_clinical_claim"])
        self.assertFalse(packet["real_monitoring"])
        self.assertEqual(
            packet["artifact_refs"]["csi_evidence_pack"]["relative_path"],
            "artifacts/csi_evidence_pack.json",
        )
        self._assert_run_relative_artifact_ref(
            packet["artifact_refs"]["csi_evidence_pack"]["relative_path"]
        )

    def _assert_csi_inspect_payload(self, payload):
        self.assertTrue(payload["compatible"])
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["provider_kind"], "wifi-csi")
        self.assertEqual(payload["evidence_kind"], "csi-evidence-pack")
        self.assertEqual(payload["artifact_name"], "csi_evidence_pack")
        self.assertEqual(payload["artifact_ref"], "artifacts/csi_evidence_pack.json")
        self.assertTrue(payload["metadata_only"])
        self.assertTrue(payload["fixture_only"])
        self.assertTrue(payload["offline_fixture_only"])
        self.assertFalse(payload["hardware_access"])
        self.assertFalse(payload["network_calls"])
        self.assertFalse(payload["packet_capture"])
        self.assertFalse(payload["monitor_mode"])
        self.assertFalse(payload["model_download"])
        self.assertFalse(payload["model_execution"])
        self.assertFalse(payload["runtime_execution"])
        self.assertFalse(payload["real_mode_execution_permitted"])
        self.assertFalse(payload["artifact_path_echoed"])
        self.assertFalse(payload["fixture_filenames_exported"])

    def _assert_document_inspect_payload(self, payload):
        self.assertTrue(payload["compatible"])
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["provider_kind"], "document-fixture")
        self.assertEqual(payload["evidence_kind"], "document-evidence-pack")
        self.assertEqual(payload["artifact_name"], "document_evidence_pack")
        self.assertEqual(payload["artifact_ref"], "artifacts/document_evidence_pack.json")
        self.assertTrue(payload["metadata_only"])
        self.assertTrue(payload["fixture_only"])
        self.assertTrue(payload["offline_fixture_only"])
        self.assertFalse(payload["hardware_access"])
        self.assertFalse(payload["network_calls"])
        self.assertFalse(payload["model_download"])
        self.assertFalse(payload["model_execution"])
        self.assertFalse(payload["runtime_execution"])
        self.assertFalse(payload["real_mode_execution_permitted"])
        self.assertFalse(payload["artifact_path_echoed"])
        self._assert_document_adapter_status(payload["document_adapter_status"])

    def _assert_run_relative_artifact_ref(self, ref):
        self.assertTrue(ref.startswith("artifacts/"))
        self.assertTrue(ref.endswith(".json"))
        self.assertNotIn("..", Path(ref).parts)
        self.assertIsNone(re.match(r"^[A-Za-z]:", ref))

    def _assert_no_private_keys_or_string_values(self, payload, surface_name):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(surface=surface_name, key=key):
                    self.assertNotIn(str(key).lower(), PRIVATE_KEY_NAMES)
                self._assert_no_private_keys_or_string_values(value, surface_name)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_private_keys_or_string_values(item, surface_name)
        elif isinstance(payload, str):
            self._assert_string_has_no_private_values(payload, surface_name)

    def _assert_text_has_no_private_values(self, text, surface_name):
        self._assert_string_has_no_private_values(text, surface_name)

    def _assert_string_has_no_private_values(self, text, surface_name):
        lowered = str(text).lower().replace("\\", "/")
        self.assertNotRegex(lowered, r"[a-z]:/")
        for forbidden in PRIVATE_STRING_FRAGMENTS:
            with self.subTest(surface=surface_name, forbidden=forbidden):
                self.assertNotIn(forbidden.lower().replace("\\", "/"), lowered)
        self.assertLessEqual(lowered.count("real-mode-authorization-missing"), 10)

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def _run_cli(args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(args)
        return exit_code, stdout.getvalue()


if __name__ == "__main__":
    unittest.main()
