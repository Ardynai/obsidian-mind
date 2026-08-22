import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.cli.main import (
    _phase11_audit_handoff_status_cli_summary,
    _phase11_audit_index_status_cli_summary,
    _phase11_lifecycle_status_cli_summary,
    _phase11_preflight_status_cli_summary,
)
from somatic.mock_runtime import run_mock_workflow
from somatic.sensors.registry import sensor_evidence_provider_manifest
from tests.doctor_fixture import DOCTOR_RESULT

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_EXAMPLE = (
    REPO_ROOT / "examples" / "document-evidence-demo" / "document-fixture-workflow.yaml"
)
FORBIDDEN_CSI_REPORT_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
}
FORBIDDEN_CSI_REPORT_WORDS = (
    "raw_values",
    "samples",
    "imag",
    "amplitude",
    "rssi",
    "source_id",
    "source_ids",
)


class CliCommandTests(unittest.TestCase):
    def test_doctor_reports_offline_foundation(self):
        exit_code, output = DOCTOR_RESULT
        self.assertEqual(exit_code, 0)
        self.assertIn("Somatic doctor", output)
        self.assertIn("offline", output)
        self.assertIn("no provider secrets", output.lower())
        self.assertIn("PaperQA2 provider: scaffolded", output)
        self.assertIn("PaperQA2 optional dependency:", output)
        self.assertIn("scientific-agent-skills provider: scaffolded", output)
        self.assertIn("scientific-agent-skills execution: disabled", output)
        self.assertIn("AutoScientists provider: reference-only", output)
        self.assertIn("AutoScientists execution: disabled", output)
        self.assertIn("FutureHouse Robin provider: reference-only", output)
        self.assertIn("FutureHouse Robin/Aviary/LDP execution: disabled", output)
        self.assertIn("Boltz-2 biomodel provider: scaffolded", output)
        self.assertIn("Boltz-2 staged source:", output)
        self.assertIn("Boltz-2 optional dependency:", output)
        self.assertIn("Boltz-2 model downloads: disabled", output)
        self.assertIn("Boltz-2 MSA server: disabled", output)
        self.assertIn("Boltz-2 runtime execution: disabled", output)
        self.assertIn(
            (
                "Sensor evidence provider registry: wifi-csi, "
                "environment-fixture, toy-counter-fixture, document-fixture"
            ),
            output,
        )
        self.assertIn("Sensor evidence provider count: 4", output)
        self.assertIn("Sensor evidence registry validation: valid", output)
        self.assertIn("Sensor evidence registry output: sanitized metadata only", output)
        self.assertIn("Document fixture adapter: metadata-document-adapter", output)
        self.assertIn("Document fixture adapter boundary:", output)
        self.assertIn(
            "Document real-mode readiness gate: blocked-fixture-reference-only",
            output,
        )
        self.assertIn("Document real-mode missing gates: 7", output)
        self.assertIn("Document real-mode execution permitted: false", output)
        self.assertIn("no-raw-body-export", output)
        self.assertIn("no-source-id-export", output)
        self.assertIn("WiFi CSI source adapter: metadata-wifi-csi-source-adapter", output)
        self.assertIn("WiFi CSI source adapter boundary:", output)
        self.assertIn(
            "WiFi CSI real-mode readiness gate: blocked-fixture-reference-only",
            output,
        )
        self.assertIn("WiFi CSI real-mode missing gates: 7", output)
        self.assertIn("WiFi CSI real-mode execution permitted: false", output)
        self.assertIn("WiFi CSI RuView posture: conditional-reference-only", output)
        self.assertIn("WiFi CSI booth-first profile: booth-first-single-subject-v1", output)
        self.assertIn("WiFi CSI RuView execution/import/vendor/model use: disabled", output)
        self.assertIn("Phase 11A real-mode contract specs: planning only, runtime disabled", output)
        self.assertIn("Phase 11A document contracts: metadata-only-staging", output)
        self.assertIn("Phase 11A document contract runtime: not-implemented", output)
        self.assertIn("Phase 11A RF booth contracts: booth-topology-metadata", output)
        self.assertIn("Phase 11A RF booth contract runtime: not-implemented", output)
        self.assertIn("Phase 11B review-record fixtures: planning evidence only", output)
        self.assertIn(
            "Phase 11B document review status: missing-required-reviews",
            output,
        )
        self.assertIn("Phase 11B document review missing gates: 7", output)
        self.assertIn(
            "Phase 11B RF booth review status: missing-required-reviews",
            output,
        )
        self.assertIn("Phase 11B RF booth review missing gates: 7", output)
        self.assertIn("Phase 11B review-record execution permitted: false", output)
        self.assertIn("Phase 11C preflight dossiers: planning packets only", output)
        self.assertIn(
            "Phase 11C document preflight status: missing-required-records",
            output,
        )
        self.assertIn("Phase 11C document preflight missing gates: 7", output)
        self.assertIn(
            "Phase 11C RF booth preflight status: missing-required-records",
            output,
        )
        self.assertIn("Phase 11C RF booth preflight missing gates: 7", output)
        self.assertIn("Phase 11C preflight execution permitted: false", output)
        self.assertIn("Phase 11D dossier lifecycle audit: audit trail only", output)
        self.assertIn("Phase 11D document lifecycle stage: created", output)
        self.assertIn("Phase 11D document audit decision: needs-more-review", output)
        self.assertIn("Phase 11D RF booth lifecycle stage: created", output)
        self.assertIn("Phase 11D RF booth audit decision: needs-more-review", output)
        self.assertIn("Phase 11D lifecycle audit execution permitted: false", output)
        self.assertIn("Phase 11E audit index/change control: local metadata only", output)
        self.assertIn("Phase 11E document audit index status: audit-index-runtime-disabled", output)
        self.assertIn("Phase 11E document audit index entries: 1", output)
        self.assertIn("Phase 11E RF booth audit index status: audit-index-runtime-disabled", output)
        self.assertIn("Phase 11E RF booth audit index entries: 1", output)
        self.assertIn("Phase 11E audit index execution permitted: false", output)
        self.assertIn("Phase 11F audit handoffs: compact reporting only", output)
        self.assertIn("Phase 11F document handoff status: audit-handoff-runtime-disabled", output)
        self.assertIn("Phase 11F RF booth handoff status: audit-handoff-runtime-disabled", output)
        self.assertIn("Phase 11F audit handoff execution permitted: false", output)
        self.assertIn("Phase 11G handoff acceptance checks: planning review only", output)
        self.assertIn("Phase 11G document acceptance status: rejected-fail-closed", output)
        self.assertIn("Phase 11G document accepted for planning: false", output)
        self.assertIn(
            "Phase 11G RF booth acceptance status: accepted-for-planning-runtime-disabled",
            output,
        )
        self.assertIn("Phase 11G RF booth accepted for planning: true", output)
        self.assertIn("Phase 11G handoff acceptance execution permitted: false", output)
        self.assertIn("Phase 11H follow-up/remediation queues: planning only", output)
        self.assertIn("Phase 11H document follow-up status: rejected", output)
        self.assertIn("Phase 11H document follow-up type: needs-more-review", output)
        self.assertIn("Phase 11H RF booth follow-up status: resolved-for-planning", output)
        self.assertIn("Phase 11H RF booth follow-up type: blocker-disposition", output)
        self.assertIn("Phase 11H follow-up/remediation execution permitted: false", output)
        self.assertIn("Phase 11I follow-up queue indexes: reviewer navigation only", output)
        self.assertIn("Phase 11I document queue status: needs-more-review", output)
        self.assertIn("Phase 11I document queue unresolved reviews: 21", output)
        self.assertIn("Phase 11I RF booth queue status: stale-queue", output)
        self.assertIn("Phase 11I RF booth queue stale count: 1", output)
        self.assertIn("Phase 11I queue index execution permitted: false", output)
        self.assertIn("Phase 11J reviewer decision closeouts: planning metadata only", output)
        self.assertIn("Phase 11J document closeout decision: needs-new-review", output)
        self.assertIn("Phase 11J document closeout status: incomplete", output)
        self.assertIn("Phase 11J RF booth closeout decision: deferred", output)
        self.assertIn("Phase 11J RF booth closeout status: incomplete", output)
        self.assertIn("Phase 11J decision closeout execution permitted: false", output)
        self.assertIn("Phase 11K review trail export: reviewer navigation only", output)
        self.assertIn("Phase 11K review trail phase range: 11A-11J", output)
        self.assertIn("Phase 11K document final closeout: needs-new-review/incomplete", output)
        self.assertIn("Phase 11K RF booth final closeout: deferred/incomplete", output)
        self.assertIn("Phase 11K readiness gap: real-mode-authorization-missing", output)
        self.assertIn("Phase 11K review trail export execution permitted: false", output)
        self.assertIn("Phase 11L runtime authorization gap ledger: metadata only", output)
        self.assertIn("Phase 11L ledger phase range: 11A-11K", output)
        self.assertIn("Phase 11L authorization status: not-authorized", output)
        self.assertIn("Phase 11L missing future gates: 9", output)
        self.assertIn("Phase 11L runtime gap ledger execution permitted: false", output)
        self.assertIn("Phase 11M planning/governance closeout: complete", output)
        self.assertIn("Phase 11M phase range: 11A-11L", output)
        self.assertIn(
            "Phase 11M final status: phase-11-planning-governance-complete",
            output,
        )
        self.assertIn("Phase 11M runtime authorization status: not-authorized", output)
        self.assertIn(
            "Phase 11M next phase requirement: explicit-future-phase-required-before-runtime-work",
            output,
        )
        self.assertIn("Phase 11M governance closeout execution permitted: false", output)
        self.assertIn("Phase 12A runtime authorization design charter: design only", output)
        self.assertIn("Phase 12A source phase range: 11L-11M", output)
        self.assertIn("Phase 12A authorization status: not-authorized", output)
        self.assertIn("Phase 12A future required gates: 8", output)
        self.assertIn("Phase 12A satisfied future gates: 0", output)
        self.assertIn("Phase 12A execution permitted: false", output)
        self.assertIn(
            "Phase 12B runtime authorization record candidate: record candidate only",
            output,
        )
        self.assertIn("Phase 12B source phase: 12A", output)
        self.assertIn("Phase 12B authorization status: not-authorized", output)
        self.assertIn("Phase 12B decision status: not-submitted", output)
        self.assertIn("Phase 12B grant status: no-grant", output)
        self.assertIn("Phase 12B requested domains: 2", output)
        self.assertIn("Phase 12B future reviewer roles: 6", output)
        self.assertIn("Phase 12B future gates: 8", output)
        self.assertIn("Phase 12B satisfied future gates: 0", output)
        self.assertIn("Phase 12B execution permitted: false", output)
        self.assertIn(
            "Phase 12C visual supervision capability profile: capability profile only",
            output,
        )
        self.assertIn("Phase 12C source phase: 12B", output)
        self.assertIn("Phase 12C supervision phase: capability-profile-only", output)
        self.assertIn("Phase 12C authorization status: not-authorized", output)
        self.assertIn("Phase 12C grant status: no-grant", output)
        self.assertIn("Phase 12C capability labels: 7", output)
        self.assertIn("Phase 12C execution permitted: false", output)
        self.assertIn(
            "Phase 12D visual/desktop consent gate requirements: consent gate requirements only",
            output,
        )
        self.assertIn("Phase 12D source phase range: 12A-12C", output)
        self.assertIn("Phase 12D consent phase: gate-requirements-only", output)
        self.assertIn("Phase 12D authorization status: not-authorized", output)
        self.assertIn("Phase 12D grant status: no-grant", output)
        self.assertIn("Phase 12D capability categories: 12", output)
        self.assertIn("Phase 12D future consent gates: 9", output)
        self.assertIn("Phase 12D satisfied consent gates: 0", output)
        self.assertIn("Phase 12D execution permitted: false", output)
        self.assertIn(
            "Phase 12E physiological sensor capability profile: capability profile only",
            output,
        )
        self.assertIn("Phase 12E source phase range: 12A-12B,12D,sensor-evidence", output)
        self.assertIn("Phase 12E sensor phase: capability-profile-only", output)
        self.assertIn("Phase 12E authorization status: not-authorized", output)
        self.assertIn("Phase 12E grant status: no-grant", output)
        self.assertIn("Phase 12E sensor capability labels: 9", output)
        self.assertIn("Phase 12E non-diagnostic boundaries: 6", output)
        self.assertIn("Phase 12E future sensor gates: 10", output)
        self.assertIn("Phase 12E satisfied sensor gates: 0", output)
        self.assertIn("Phase 12E execution permitted: false", output)
        self.assertIn(
            "Phase 12F Secure Drop consumer boundary: boundary profile only",
            output,
        )
        self.assertIn(
            "Phase 12F source phase range: 12A-12E,content-fabric-secure-drop",
            output,
        )
        self.assertIn("Phase 12F consumer phase: boundary-profile-only", output)
        self.assertIn("Phase 12F canonical owner: content-fabric", output)
        self.assertIn("Phase 12F authorization status: not-authorized", output)
        self.assertIn("Phase 12F grant status: no-grant", output)
        self.assertIn("Phase 12F allowed artifact labels: 6", output)
        self.assertIn("Phase 12F prohibited autonomous sources: 11", output)
        self.assertIn("Phase 12F Secure Drop send permitted: false", output)
        self.assertIn("Phase 12F Secure Drop receive permitted: false", output)
        self.assertIn("Phase 12F execution permitted: false", output)
        self.assertIn(
            "Phase 12G production-readiness coverage matrix: coverage matrix only",
            output,
        )
        self.assertIn("Phase 12G source phase range: 11A-11M,12A-12F", output)
        self.assertIn("Phase 12G readiness phase: coverage-matrix-only", output)
        self.assertIn("Phase 12G authorization status: not-authorized", output)
        self.assertIn("Phase 12G grant status: no-grant", output)
        self.assertIn("Phase 12G production-readiness areas: 19", output)
        self.assertIn("Phase 12G Somatic direct areas: 4", output)
        self.assertIn("Phase 12G Somatic boundary-only areas: 7", output)
        self.assertIn("Phase 12G external-owner areas: 8", output)
        self.assertIn("Phase 12G makes Somatic production-ready: false", output)
        self.assertIn("Phase 12G authorizes runtime: false", output)
        self.assertIn("Phase 12G execution permitted: false", output)
        for forbidden in (
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "environment-parsed.csv",
            "toy-counter-parsed.csv",
            "fixture://",
            "fixtures/sensors",
            "c:\\",
            "source_id",
            "provider_payload_body",
            "api_key",
            "access_token",
            "raw_bia",
            "raw_impedance",
            "raw_ultrasound",
            "raw_acoustic",
            "bluetooth_mac",
            "serial_number",
        ):
            with self.subTest(doctor_forbidden=forbidden):
                self.assertNotIn(forbidden, output.lower())
        self.assertIn("WiFi CSI evidence scoring: Phase 8E sanitized metadata only", output)
        self.assertIn(
            "WiFi CSI batch replay evaluation: Phase 8F tournament readiness metadata only", output
        )

    def test_doctor_reports_spine_status(self):
        exit_code, output = DOCTOR_RESULT
        self.assertEqual(exit_code, 0)
        self.assertIn("Spine consent scopes (default OFF):", output)
        self.assertIn("data-ingestion: default OFF", output)
        self.assertIn("ai-advisory: default OFF", output)
        self.assertIn("Spine persisted grants:", output)
        self.assertIn("Spine adapter config:", output)
        self.assertIn("Spine emergency-screen self-test: triggered", output)

    def test_sensor_evidence_provider_listing_is_deterministic_and_sanitized(self):
        text_stdout = io.StringIO()
        json_stdout = io.StringIO()
        second_json_stdout = io.StringIO()

        with contextlib.redirect_stdout(text_stdout):
            text_exit = main(["sensor-evidence", "providers"])
        with contextlib.redirect_stdout(json_stdout):
            json_exit = main(["sensor-evidence", "providers", "--format", "json"])
        with contextlib.redirect_stdout(second_json_stdout):
            second_json_exit = main(["sensor-evidence", "providers", "--format", "json"])

        self.assertEqual(text_exit, 0)
        self.assertEqual(json_exit, 0)
        self.assertEqual(second_json_exit, 0)
        text_output = text_stdout.getvalue()
        payload = json.loads(json_stdout.getvalue())
        second_payload = json.loads(second_json_stdout.getvalue())
        self.assertEqual(payload, sensor_evidence_provider_manifest())
        self.assertEqual(payload, second_payload)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["manifest_contract_version"], 1)
        self.assertTrue(payload["sanitized"])
        self.assertTrue(payload["metadata_only"])
        self.assertEqual(payload["provider_count"], 4)
        self.assertEqual(
            [provider["provider_id"] for provider in payload["providers"]],
            ["wifi-csi", "environment-fixture", "toy-counter-fixture", "document-fixture"],
        )
        self.assertIn("wifi-csi: evidence_kind=csi-evidence-pack", text_output)
        self.assertIn("environment-fixture", text_output)
        self.assertIn("toy-counter-fixture", text_output)
        csi_provider = payload["providers"][0]
        self.assertEqual(csi_provider["provider_id"], "wifi-csi")
        self.assertEqual(csi_provider["adapter_kind"], "metadata-wifi-csi-source-adapter")
        self.assertIn("reference-only", csi_provider["adapter_boundary_labels"])
        self.assertIn("no-model-download", csi_provider["adapter_boundary_labels"])
        self.assertIn("rf-booth-review-only", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11a-contract-spec-only", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11b-review-record-fixture", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11d-lifecycle-audit-record", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11e-audit-index", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11f-audit-handoff", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11g-handoff-acceptance", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11h-followup-remediation", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11i-followup-queue-index", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11j-decision-closeout", csi_provider["adapter_boundary_labels"])
        self.assertIn("p11m-governance-closeout", csi_provider["adapter_boundary_labels"])
        self.assertEqual(csi_provider["review_record_status"], "missing-required-reviews")
        self.assertEqual(csi_provider["review_record_missing_gate_count"], 7)
        self.assertFalse(csi_provider["review_record_execution_permitted"])
        self.assertEqual(csi_provider["preflight_packet_status"], "missing-required-records")
        self.assertEqual(csi_provider["preflight_packet_missing_gate_count"], 7)
        self.assertFalse(csi_provider["preflight_packet_execution_permitted"])
        self.assertEqual(csi_provider["lifecycle_audit_stage"], "created")
        self.assertEqual(csi_provider["lifecycle_audit_decision"], "needs-more-review")
        self.assertFalse(csi_provider["lifecycle_audit_execution_permitted"])
        self.assertEqual(csi_provider["audit_index_status"], "audit-index-runtime-disabled")
        self.assertEqual(csi_provider["audit_index_entry_count"], 1)
        self.assertEqual(csi_provider["audit_index_blocking_count"], 8)
        self.assertFalse(csi_provider["audit_index_execution_permitted"])
        self.assertEqual(csi_provider["handoff_status"], "audit-handoff-runtime-disabled")
        self.assertEqual(csi_provider["handoff_entry_count"], 1)
        self.assertEqual(csi_provider["handoff_blocking_count"], 0)
        self.assertEqual(csi_provider["handoff_unresolved_review_count"], 0)
        self.assertFalse(csi_provider["handoff_execution_permitted"])
        self.assertEqual(
            csi_provider["handoff_acceptance_status"],
            "accepted-for-planning-runtime-disabled",
        )
        self.assertTrue(csi_provider["handoff_accepted_for_planning"])
        self.assertFalse(csi_provider["handoff_acceptance_execution_permitted"])
        self.assertEqual(csi_provider["acceptance_followup_status"], "resolved-for-planning")
        self.assertEqual(csi_provider["acceptance_followup_type"], "blocker-disposition")
        self.assertFalse(csi_provider["acceptance_followup_execution_permitted"])
        self.assertEqual(csi_provider["followup_queue_status"], "stale-queue")
        self.assertEqual(csi_provider["followup_queue_acceptance_status"], "stale-queue")
        self.assertEqual(csi_provider["followup_queue_stale_count"], 1)
        self.assertFalse(csi_provider["followup_queue_execution_permitted"])
        self.assertEqual(csi_provider["decision_closeout_decision"], "deferred")
        self.assertEqual(csi_provider["decision_closeout_status"], "incomplete")
        self.assertEqual(csi_provider["decision_closeout_stale_count"], 1)
        self.assertEqual(csi_provider["decision_closeout_deferred_count"], 1)
        self.assertEqual(csi_provider["decision_closeout_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["decision_closeout_execution_permitted"])
        self.assertIn("p11k-review-trail-export", csi_provider["adapter_boundary_labels"])
        self.assertEqual(csi_provider["review_trail_phase_range"], "11A-11J")
        self.assertEqual(csi_provider["review_trail_covered_phase_count"], 10)
        self.assertEqual(csi_provider["review_trail_domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(csi_provider["review_trail_closeout_decision"], "deferred")
        self.assertEqual(csi_provider["review_trail_closeout_status"], "incomplete")
        self.assertEqual(csi_provider["review_trail_stale_count"], 1)
        self.assertEqual(
            csi_provider["review_trail_readiness_gap_summary"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(csi_provider["review_trail_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["review_trail_execution_permitted"])
        self.assertEqual(csi_provider["runtime_gap_phase_range"], "11A-11K")
        self.assertEqual(csi_provider["runtime_gap_covered_phase_count"], 11)
        self.assertEqual(csi_provider["runtime_gap_domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(csi_provider["runtime_gap_authorization_status"], "not-authorized")
        self.assertEqual(
            csi_provider["runtime_gap_readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(csi_provider["runtime_gap_missing_future_gate_count"], 9)
        self.assertEqual(csi_provider["runtime_gap_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["runtime_gap_adapter_execution_granted"])
        self.assertFalse(csi_provider["runtime_gap_provider_execution_granted"])
        self.assertFalse(csi_provider["runtime_gap_model_execution_granted"])
        self.assertFalse(csi_provider["runtime_gap_execution_permitted"])
        self.assertFalse(csi_provider["runtime_gap_real_mode_runtime_enabled"])
        self.assertEqual(csi_provider["governance_closeout_phase_range"], "11A-11L")
        self.assertEqual(csi_provider["governance_closeout_covered_phase_count"], 12)
        self.assertEqual(
            csi_provider["governance_closeout_final_status"],
            "phase-11-planning-governance-complete",
        )
        self.assertEqual(
            csi_provider["governance_closeout_runtime_authorization_status"],
            "not-authorized",
        )
        self.assertEqual(
            csi_provider["governance_closeout_readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(csi_provider["governance_closeout_missing_future_gate_count"], 9)
        self.assertEqual(csi_provider["governance_closeout_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["governance_closeout_adapter_execution_granted"])
        self.assertFalse(csi_provider["governance_closeout_provider_execution_granted"])
        self.assertFalse(csi_provider["governance_closeout_model_execution_granted"])
        self.assertFalse(csi_provider["governance_closeout_execution_permitted"])
        self.assertFalse(csi_provider["governance_closeout_real_mode_runtime_enabled"])
        self.assertEqual(
            csi_provider["readiness_gate_status"],
            "blocked-fixture-reference-only",
        )
        self.assertFalse(csi_provider["real_mode_execution_permitted"])
        document_provider = payload["providers"][-1]
        self.assertEqual(document_provider["provider_id"], "document-fixture")
        self.assertEqual(document_provider["adapter_kind"], "metadata-document-adapter")
        self.assertIn("no-network", document_provider["adapter_boundary_labels"])
        self.assertIn("no-raw-body-export", document_provider["adapter_boundary_labels"])
        self.assertIn("p11a-contract-spec-only", document_provider["adapter_boundary_labels"])
        self.assertIn(
            "p11b-review-record-fixture",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11d-lifecycle-audit-record",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11e-audit-index",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11f-audit-handoff",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11g-handoff-acceptance",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11h-followup-remediation",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11i-followup-queue-index",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11j-decision-closeout",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11k-review-trail-export",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11m-governance-closeout",
            document_provider["adapter_boundary_labels"],
        )
        self.assertEqual(
            document_provider["review_record_status"],
            "missing-required-reviews",
        )
        self.assertEqual(document_provider["review_record_missing_gate_count"], 7)
        self.assertFalse(document_provider["review_record_execution_permitted"])
        self.assertEqual(
            document_provider["preflight_packet_status"],
            "missing-required-records",
        )
        self.assertEqual(document_provider["preflight_packet_missing_gate_count"], 7)
        self.assertFalse(document_provider["preflight_packet_execution_permitted"])
        self.assertEqual(document_provider["lifecycle_audit_stage"], "created")
        self.assertEqual(
            document_provider["lifecycle_audit_decision"],
            "needs-more-review",
        )
        self.assertFalse(document_provider["lifecycle_audit_execution_permitted"])
        self.assertEqual(
            document_provider["audit_index_status"],
            "audit-index-runtime-disabled",
        )
        self.assertEqual(document_provider["audit_index_entry_count"], 1)
        self.assertEqual(document_provider["audit_index_blocking_count"], 8)
        self.assertFalse(document_provider["audit_index_execution_permitted"])
        self.assertEqual(
            document_provider["handoff_status"],
            "audit-handoff-runtime-disabled",
        )
        self.assertEqual(document_provider["handoff_entry_count"], 5)
        self.assertEqual(document_provider["handoff_blocking_count"], 10)
        self.assertEqual(document_provider["handoff_unresolved_review_count"], 8)
        self.assertFalse(document_provider["handoff_execution_permitted"])
        self.assertEqual(
            document_provider["handoff_acceptance_status"],
            "rejected-fail-closed",
        )
        self.assertFalse(document_provider["handoff_accepted_for_planning"])
        self.assertFalse(document_provider["handoff_acceptance_execution_permitted"])
        self.assertEqual(document_provider["acceptance_followup_status"], "rejected")
        self.assertEqual(document_provider["acceptance_followup_type"], "needs-more-review")
        self.assertFalse(document_provider["acceptance_followup_execution_permitted"])
        self.assertEqual(document_provider["followup_queue_status"], "needs-more-review")
        self.assertEqual(
            document_provider["followup_queue_acceptance_status"],
            "needs-more-review",
        )
        self.assertEqual(document_provider["followup_queue_unresolved_review_count"], 21)
        self.assertFalse(document_provider["followup_queue_execution_permitted"])
        self.assertEqual(
            document_provider["decision_closeout_decision"],
            "needs-new-review",
        )
        self.assertEqual(document_provider["decision_closeout_status"], "incomplete")
        self.assertEqual(
            document_provider["decision_closeout_unresolved_review_count"],
            21,
        )
        self.assertEqual(document_provider["decision_closeout_blocker_count"], 9)
        self.assertEqual(
            document_provider["decision_closeout_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["decision_closeout_execution_permitted"])
        self.assertEqual(document_provider["review_trail_phase_range"], "11A-11J")
        self.assertEqual(document_provider["review_trail_covered_phase_count"], 10)
        self.assertEqual(
            document_provider["review_trail_domain_label"],
            "document-ingestion",
        )
        self.assertEqual(
            document_provider["review_trail_closeout_decision"],
            "needs-new-review",
        )
        self.assertEqual(document_provider["review_trail_closeout_status"], "incomplete")
        self.assertEqual(
            document_provider["review_trail_unresolved_review_count"],
            21,
        )
        self.assertEqual(document_provider["review_trail_blocker_count"], 9)
        self.assertEqual(
            document_provider["review_trail_readiness_gap_summary"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(
            document_provider["review_trail_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["review_trail_execution_permitted"])
        self.assertEqual(document_provider["runtime_gap_phase_range"], "11A-11K")
        self.assertEqual(document_provider["runtime_gap_covered_phase_count"], 11)
        self.assertEqual(
            document_provider["runtime_gap_domain_label"],
            "document-ingestion",
        )
        self.assertEqual(
            document_provider["runtime_gap_authorization_status"],
            "not-authorized",
        )
        self.assertEqual(
            document_provider["runtime_gap_readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(document_provider["runtime_gap_missing_future_gate_count"], 9)
        self.assertEqual(document_provider["runtime_gap_runtime_stage"], "not-implemented")
        self.assertFalse(document_provider["runtime_gap_adapter_execution_granted"])
        self.assertFalse(document_provider["runtime_gap_provider_execution_granted"])
        self.assertFalse(document_provider["runtime_gap_model_execution_granted"])
        self.assertFalse(document_provider["runtime_gap_execution_permitted"])
        self.assertFalse(document_provider["runtime_gap_real_mode_runtime_enabled"])
        self.assertEqual(
            document_provider["governance_closeout_phase_range"],
            "11A-11L",
        )
        self.assertEqual(
            document_provider["governance_closeout_covered_phase_count"],
            12,
        )
        self.assertEqual(
            document_provider["governance_closeout_final_status"],
            "phase-11-planning-governance-complete",
        )
        self.assertEqual(
            document_provider["governance_closeout_runtime_authorization_status"],
            "not-authorized",
        )
        self.assertEqual(
            document_provider["governance_closeout_readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(
            document_provider["governance_closeout_missing_future_gate_count"],
            9,
        )
        self.assertEqual(
            document_provider["governance_closeout_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["governance_closeout_adapter_execution_granted"])
        self.assertFalse(document_provider["governance_closeout_provider_execution_granted"])
        self.assertFalse(document_provider["governance_closeout_model_execution_granted"])
        self.assertFalse(document_provider["governance_closeout_execution_permitted"])
        self.assertFalse(document_provider["governance_closeout_real_mode_runtime_enabled"])
        self.assertEqual(
            document_provider["readiness_gate_status"],
            "blocked-fixture-reference-only",
        )
        self.assertFalse(document_provider["real_mode_execution_permitted"])
        self.assertIn("adapter_boundary=", text_output)
        self.assertIn("readiness_gate=blocked-fixture-reference-only", text_output)
        encoded = (text_output + json.dumps(payload, sort_keys=True)).lower()
        self._assert_sensor_cli_sanitized(encoded)

    def test_sensor_evidence_validate_public_example(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "sensor-evidence",
                    "validate",
                    "--workflow",
                    "examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml",
                    "--format",
                    "json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["error_count"], 0)
        self.assertEqual(payload["error_categories"], [])
        self.assertEqual(payload["provider_count"], 1)
        self.assertEqual(payload["input_count"], 1)
        self._assert_sensor_cli_sanitized(json.dumps(payload, sort_keys=True).lower())

    def test_sensor_evidence_validate_and_inspect_document_pack(self):
        validate_stdout = io.StringIO()

        with contextlib.redirect_stdout(validate_stdout):
            validate_exit = main(
                [
                    "sensor-evidence",
                    "validate",
                    "--workflow",
                    str(DOCUMENT_EXAMPLE),
                    "--format",
                    "json",
                ]
            )

        self.assertEqual(validate_exit, 0)
        validation = json.loads(validate_stdout.getvalue())
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["provider_count"], 1)
        self.assertEqual(validation["input_count"], 1)
        self.assertTrue(validation["metadata_only"])
        self.assertTrue(validation["offline_fixture_only"])
        self.assertTrue(validation["sanitized"])

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                DOCUMENT_EXAMPLE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-document-inspect-cli-test",
            )
            artifact = run_dir / "artifacts" / "document_evidence_pack.json"
            json_stdout = io.StringIO()
            text_stdout = io.StringIO()

            with contextlib.redirect_stdout(json_stdout):
                json_exit = main(
                    [
                        "sensor-evidence",
                        "inspect",
                        "--artifact",
                        str(artifact),
                        "--format",
                        "json",
                    ]
                )
            with contextlib.redirect_stdout(text_stdout):
                text_exit = main(
                    [
                        "sensor-evidence",
                        "inspect",
                        "--artifact",
                        str(artifact),
                    ]
                )

            self.assertNotIn(
                str(run_dir).replace("\\", "/").lower(),
                (json_stdout.getvalue() + text_stdout.getvalue()).replace("\\", "/").lower(),
            )

        self.assertEqual(json_exit, 0)
        self.assertEqual(text_exit, 0)
        payload = json.loads(json_stdout.getvalue())
        self.assertTrue(payload["compatible"])
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["classification"], "compatible")
        self.assertEqual(payload["provider_kind"], "document-fixture")
        self.assertEqual(payload["evidence_kind"], "document-evidence-pack")
        self.assertEqual(payload["artifact_name"], "document_evidence_pack")
        self.assertEqual(payload["artifact_ref"], "artifacts/document_evidence_pack.json")
        self.assertEqual(payload["status"], "parsed")
        self.assertEqual(payload["readiness_status"], "ready-with-sanitized-metadata")
        self.assertEqual(payload["counts"]["document_count"], 3)
        self.assertEqual(payload["counts"]["parsed_document_count"], 3)
        self.assertEqual(payload["counts"]["fixture_count"], 1)
        self.assertEqual(
            payload["document_adapter_status"]["adapter_kind"],
            "metadata-document-adapter",
        )
        self.assertIn(
            "no-file-crawling",
            payload["document_adapter_status"]["capability_labels"],
        )
        self.assertEqual(
            payload["adapter_output_validation"]["classification"],
            "compatible",
        )
        self.assertEqual(
            payload["document_adapter_status"]["real_mode_readiness_gate"]["status"],
            "blocked-fixture-reference-only",
        )
        phase11 = payload["document_adapter_status"]["p11a_contract_status"]
        self.assertEqual(phase11["domain"], "document-ingestion")
        self.assertEqual(phase11["status"], "planning-only-runtime-disabled")
        self.assertTrue(phase11["planning_only"])
        self.assertFalse(phase11["execution_permitted"])
        self.assertFalse(phase11["real_mode_runtime_enabled"])
        p11c = payload["document_adapter_status"]["p11c_preflight_status"]
        self.assertEqual(p11c["domain"], "document-ingestion")
        self.assertEqual(p11c["preflight_status"], "missing-required-records")
        self.assertEqual(p11c["missing_gate_count"], 7)
        self.assertEqual(p11c["runtime_stage"], "not-implemented")
        self.assertFalse(p11c["execution_permitted"])
        self.assertFalse(p11c["real_mode_runtime_enabled"])
        p11d = payload["document_adapter_status"]["p11d_lifecycle_audit_status"]
        self.assertEqual(p11d["domain"], "document-ingestion")
        self.assertEqual(p11d["lifecycle_stage"], "created")
        self.assertEqual(p11d["audit_decision"], "needs-more-review")
        self.assertEqual(p11d["runtime_stage"], "not-implemented")
        self.assertFalse(p11d["execution_permitted"])
        self.assertFalse(p11d["real_mode_runtime_enabled"])
        p11e = payload["document_adapter_status"]["p11e_audit_index_status"]
        self.assertEqual(p11e["status"], "audit-index-runtime-disabled")
        self.assertEqual(p11e["entry_count"], 1)
        self.assertEqual(p11e["blocking_count"], 8)
        self.assertEqual(p11e["runtime_stage"], "not-implemented")
        self.assertFalse(p11e["execution_permitted"])
        self.assertFalse(p11e["real_mode_runtime_enabled"])
        p11f = payload["document_adapter_status"]["p11f_audit_handoff_status"]
        self.assertEqual(p11f["status"], "audit-handoff-runtime-disabled")
        self.assertEqual(p11f["audit_index_entry_count"], 5)
        self.assertEqual(p11f["blocking_count"], 10)
        self.assertEqual(p11f["unresolved_review_count"], 8)
        self.assertEqual(p11f["runtime_stage"], "not-implemented")
        self.assertFalse(p11f["execution_permitted"])
        self.assertFalse(p11f["real_mode_runtime_enabled"])
        self.assertEqual(
            payload["document_adapter_status"]["real_mode_readiness_gate"]["missing_gate_count"],
            7,
        )
        self.assertFalse(payload["document_adapter_status"]["real_mode_execution_permitted"])
        self.assertIn("document_adapter_status", text_stdout.getvalue())
        self.assertIn("document_adapter_boundary", text_stdout.getvalue())
        self.assertEqual(payload["error_count"], 0)
        self.assertTrue(payload["metadata_only"])
        self.assertTrue(payload["offline_fixture_only"])
        self.assertTrue(payload["sanitized"])
        self.assertFalse(payload["artifact_path_echoed"])
        self.assertIn("document-fixture", text_stdout.getvalue())
        self.assertIn("document_count=3", text_stdout.getvalue())

        encoded = (
            json.dumps(validation, sort_keys=True)
            + json.dumps(payload, sort_keys=True)
            + text_stdout.getvalue()
        ).lower()
        self._assert_sensor_cli_sanitized(encoded)

    def test_sensor_evidence_inspect_fails_closed_with_sanitized_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            malformed = tmp_path / "private-document-artifact.json"
            malformed.write_text(
                "{ private: https://example.invalid source_id api_key }",
                encoding="utf-8",
            )
            unsupported = tmp_path / "unsupported-document-artifact.json"
            unsupported.write_text(
                json.dumps(
                    {
                        "provider_kind": "https://example.invalid/private-provider",
                        "evidence_kind": "source_id-private-kind",
                        "provider_payload_body": "sk-private-value",
                    }
                ),
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                malformed_exit = main(
                    [
                        "sensor-evidence",
                        "inspect",
                        "--artifact",
                        str(malformed),
                        "--format",
                        "json",
                    ]
                )
            malformed_payload = json.loads(stdout.getvalue())

            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                unsupported_exit = main(
                    [
                        "sensor-evidence",
                        "inspect",
                        "--artifact",
                        str(unsupported),
                        "--format",
                        "json",
                    ]
                )
            unsupported_payload = json.loads(stdout.getvalue())

            run_dir = run_mock_workflow(
                DOCUMENT_EXAMPLE,
                repo_root=REPO_ROOT,
                output_root=tmp_path,
                run_id="run-document-inspect-fail-closed-test",
            )
            pack_path = run_dir / "artifacts" / "document_evidence_pack.json"
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
            pack["counts"]["document_count"] = 999
            mismatched = tmp_path / "fingerprint-mismatch.json"
            mismatched.write_text(json.dumps(pack), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                mismatch_exit = main(
                    [
                        "sensor-evidence",
                        "inspect",
                        "--artifact",
                        str(mismatched),
                        "--format",
                        "json",
                    ]
                )
            mismatch_payload = json.loads(stdout.getvalue())

            combined_output = json.dumps(
                (malformed_payload, unsupported_payload, mismatch_payload),
                sort_keys=True,
            ).lower()
            self.assertNotIn(str(tmp_path).replace("\\", "/").lower(), combined_output)

        self.assertEqual(malformed_exit, 1)
        self.assertEqual(malformed_payload["classification"], "malformed")
        self.assertEqual(malformed_payload["provider_kind"], "unknown")
        self.assertEqual(malformed_payload["evidence_kind"], "unknown")
        self.assertEqual(malformed_payload["readiness_status"], "rejected-fail-closed")
        self.assertFalse(malformed_payload["compatible"])
        self.assertFalse(malformed_payload["artifact_path_echoed"])

        self.assertEqual(unsupported_exit, 1)
        self.assertEqual(unsupported_payload["classification"], "unsupported_version")
        self.assertEqual(unsupported_payload["provider_kind"], "unknown")
        self.assertEqual(unsupported_payload["evidence_kind"], "unknown")
        self.assertEqual(unsupported_payload["readiness_status"], "rejected-fail-closed")
        self.assertFalse(unsupported_payload["compatible"])

        self.assertEqual(mismatch_exit, 1)
        self.assertEqual(mismatch_payload["classification"], "incompatible")
        self.assertEqual(mismatch_payload["provider_kind"], "document-fixture")
        self.assertEqual(mismatch_payload["evidence_kind"], "document-evidence-pack")
        self.assertEqual(mismatch_payload["readiness_status"], "rejected-fail-closed")
        self.assertFalse(mismatch_payload["compatible"])
        self.assertIn("invalid_fingerprint_or_pack_id", mismatch_payload["errors"])

        self._assert_sensor_cli_sanitized(combined_output)

    def test_phase11c_cli_preflight_summary_strips_private_identifier_labels(self):
        summary = _phase11_preflight_status_cli_summary(
            {
                "preflight_packet_contract_version": 1,
                "domain": "document-ingestion",
                "preflight_packet_label": "p11c-source-id-c:/private-device-id",
                "preflight_packet_id": "p11c-source-id-c:/private-device-id",
                "preflight_packet_fingerprint": "0" * 64,
                "preflight_status": "missing-required-records",
                "reviewed_gate_count": 0,
                "missing_gate_count": 7,
                "rejected_gate_count": 0,
                "blocking_reason_count": 7,
                "planning_only": True,
                "metadata_only": True,
                "runtime_stage": "not-implemented",
                "execution_permitted": True,
                "real_mode_runtime_enabled": True,
            }
        )

        self.assertEqual(summary["preflight_packet_label"], "")
        self.assertEqual(summary["preflight_packet_id"], "")
        self.assertEqual(summary["preflight_packet_fingerprint"], "0" * 64)
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])

    def test_phase11d_cli_lifecycle_summary_strips_private_identifier_labels(self):
        summary = _phase11_lifecycle_status_cli_summary(
            {
                "lifecycle_contract_version": 1,
                "domain": "document-ingestion",
                "lifecycle_record_id": "p11d-source-id-c:/private-device-id",
                "lifecycle_record_fingerprint": "0" * 64,
                "lifecycle_stage": "created",
                "lifecycle_status": "created-runtime-disabled",
                "audit_decision": "needs-more-review",
                "signoff_verdict": "blockers",
                "signoff_count": 1,
                "decision_count": 1,
                "comparison_changed_field_count": 0,
                "blocking_reason_count": 7,
                "planning_only": True,
                "metadata_only": True,
                "runtime_stage": "not-implemented",
                "execution_permitted": True,
                "real_mode_runtime_enabled": True,
            }
        )

        self.assertEqual(summary["lifecycle_record_id"], "")
        self.assertEqual(summary["lifecycle_record_fingerprint"], "0" * 64)
        self.assertEqual(summary["lifecycle_stage"], "created")
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])

    def test_phase11e_cli_audit_index_summary_strips_private_identifier_labels(self):
        for index_id in (
            "p11e-source-id-c:/private-device-id",
            "p11e-private-audit",
            "p11e-secret-token",
            "p11e-parser-body",
            "p11e-provider-body",
            "p11e-model-body",
            "p11e-raw-csi",
        ):
            with self.subTest(index_id=index_id):
                summary = _phase11_audit_index_status_cli_summary(
                    {
                        "audit_index_contract_version": 1,
                        "domain_scope": "multi-domain",
                        "index_id": index_id,
                        "index_fingerprint": "0" * 64,
                        "status": "audit-index-runtime-disabled",
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
                        "runtime_stage": "not-implemented",
                        "execution_permitted": True,
                        "real_mode_runtime_enabled": True,
                    }
                )

                self.assertEqual(summary["index_id"], "")
                self.assertEqual(summary["index_fingerprint"], "0" * 64)
                self.assertEqual(summary["status"], "audit-index-runtime-disabled")
                self.assertFalse(summary["execution_permitted"])
                self.assertFalse(summary["real_mode_runtime_enabled"])

    def test_phase11f_cli_handoff_summary_strips_private_identifier_labels(self):
        for handoff_id in (
            "p11f-source-id-c:/private-device-id",
            "p11f-private-handoff",
            "p11f-secret-token",
            "p11f-parser-body",
            "p11f-provider-body",
            "p11f-model-body",
            "p11f-raw-csi",
        ):
            with self.subTest(handoff_id=handoff_id):
                summary = _phase11_audit_handoff_status_cli_summary(
                    {
                        "audit_handoff_contract_version": 1,
                        "domain": "document-ingestion",
                        "handoff_id": handoff_id,
                        "handoff_fingerprint": "0" * 64,
                        "status": "audit-handoff-runtime-disabled",
                        "audit_index_label": "p11e-index-0000000000000000",
                        "audit_index_fingerprint": "1" * 64,
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
                        "runtime_stage": "not-implemented",
                        "execution_permitted": True,
                        "real_mode_runtime_enabled": True,
                    }
                )

                self.assertEqual(summary["handoff_id"], "")
                self.assertEqual(summary["handoff_fingerprint"], "0" * 64)
                self.assertEqual(summary["status"], "audit-handoff-runtime-disabled")
                self.assertFalse(summary["execution_permitted"])
                self.assertFalse(summary["real_mode_runtime_enabled"])

    def test_sensor_evidence_validate_rejects_unsafe_config_with_categories(self):
        workflow_text = (
            REPO_ROOT / "examples" / "sensor-evidence-demo" / "toy-counter-fixture-workflow.yaml"
        ).read_text(encoding="utf-8")
        workflow_text = workflow_text.replace(
            "    provider_id: toy-counter-fixture",
            "\n".join(
                (
                    "    provider_id: toy-counter-fixture",
                    "    fixture_mode: private-live-mode-value",
                    "    api_key: sk-private-value",
                    "    device_id: private-device",
                )
            ),
            1,
        ).replace(
            "    refs:\n      - toy-counter-parsed.csv",
            "\n".join(
                (
                    "    refs:",
                    "      - C:/Users/Josh/private.csv",
                    "      - https://example.invalid/private.csv",
                    "      - ../private.csv",
                    "      - toy-counter-parsed.json",
                )
            ),
            1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / "unsafe-sensor-evidence.yaml"
            workflow.write_text(workflow_text, encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "sensor-evidence",
                        "validate",
                        "--workflow",
                        str(workflow),
                        "--format",
                        "json",
                    ]
                )

        self.assertEqual(exit_code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["valid"])
        encoded = json.dumps(payload, sort_keys=True).lower()
        for category in (
            "credential_like_field",
            "excessive_count",
            "live_device_network_field",
            "unsafe_ref",
            "unsupported_fixture_format",
            "unsupported_fixture_mode",
        ):
            with self.subTest(validation_category=category):
                self.assertIn(category, payload["error_categories"])
        for code in (
            "sensor_credential_field_present",
            "sensor_live_device_or_network_field_present",
            "sensor_fixture_ref_count_exceeded",
            "sensor_fixture_ref_parent_traversal_rejected",
            "sensor_fixture_ref_unsupported_format",
            "sensor_fixture_mode_unsupported",
        ):
            with self.subTest(validation_code=code):
                self.assertIn(code, encoded)
        self._assert_sensor_cli_sanitized(encoded)
        for forbidden in (
            "private-live-mode-value",
            "sk-private-value",
            "private-device",
            "example.invalid",
            "private.csv",
            str(REPO_ROOT).replace("\\", "/").lower(),
        ):
            with self.subTest(validation_forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def test_launch_accepts_local_config_without_running_advanced_lanes(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "launch.yaml"
            config.write_text(
                "schema_version: 1\n"
                "mode: local-mock\n"
                "workflow: fixtures/workflows/valid-literature-only.yaml\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(["launch", "--config", str(config)])

        self.assertEqual(exit_code, 0)
        self.assertIn("Launch plan loaded", stdout.getvalue())
        self.assertIn("advanced lanes disabled", stdout.getvalue())

    def test_replay_reads_existing_run_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            run_dir = runs_dir / "run-replay-test"
            run_dir.mkdir(parents=True)
            (run_dir / "manifest.json").write_text(
                json.dumps({"run_id": "run-replay-test", "mock": True}),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(["replay", "run-replay-test", "--runs-dir", str(runs_dir)])

        self.assertEqual(exit_code, 0)
        self.assertIn("run-replay-test", stdout.getvalue())
        self.assertIn("mock", stdout.getvalue())

    def test_csi_parse_prints_sanitized_offline_report_json(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "csi-parse",
                    "sample-esp32-csi.csv",
                    "--repo-root",
                    str(REPO_ROOT),
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["report"]["status"], "parsed")
        self.assertEqual(payload["summary"]["frame_count"], 2)
        self.assertEqual(payload["summary"]["sample_count"], 8)
        self.assertEqual(payload["report"]["csi_evidence_scoring"]["status"], "parsed")
        self.assertEqual(payload["report"]["csi_evidence_scoring"]["score"], 100)
        self.assertEqual(
            payload["summary"]["csi_evidence_scoring"],
            payload["report"]["csi_evidence_scoring"],
        )
        self.assertTrue(payload["summary"]["fixture_only"])
        self.assertFalse(payload["summary"]["network_calls"])
        self.assertFalse(payload["summary"]["hardware_access"])
        self._assert_no_forbidden_csi_keys(payload)
        self._assert_no_forbidden_csi_words(payload)
        self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), stdout.getvalue().replace("\\", "/"))

    def test_csi_parse_all_local_fixtures_emit_sanitized_metadata(self):
        fixture_dir = REPO_ROOT / "fixtures" / "sensors" / "csi"

        for fixture_path in sorted(path for path in fixture_dir.iterdir() if path.is_file()):
            with self.subTest(fixture=fixture_path.name):
                stdout = io.StringIO()

                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "csi-parse",
                            fixture_path.name,
                            "--repo-root",
                            str(REPO_ROOT),
                        ]
                    )

                payload = json.loads(stdout.getvalue())
                expected_exit = 0 if payload["report"]["status"] in {"parsed", "partial"} else 1
                self.assertEqual(exit_code, expected_exit)
                self._assert_no_forbidden_csi_keys(payload)
                self._assert_no_forbidden_csi_words(payload)
                self.assertNotIn(
                    str(REPO_ROOT).replace("\\", "/"),
                    stdout.getvalue().replace("\\", "/"),
                )

    def test_csi_parse_rejected_unsafe_refs_are_sanitized(self):
        refs = (
            str(REPO_ROOT / "fixtures" / "sensors" / "csi" / "sample-esp32-csi.csv"),
            "https://example.invalid/csi-fixture.csv",
        )

        for ref in refs:
            with self.subTest(ref=ref):
                stdout = io.StringIO()

                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["csi-parse", ref, "--repo-root", str(REPO_ROOT)])

                payload = json.loads(stdout.getvalue())
                self.assertEqual(exit_code, 1)
                self.assertEqual(payload["report"]["status"], "rejected")
                self.assertEqual(payload["report"]["csi_evidence_scoring"]["status"], "rejected")
                self.assertEqual(payload["report"]["csi_evidence_scoring"]["score"], 0)
                self.assertEqual(payload["report"]["fixture_refs"], ["csi-fixture-001.csv"])
                self.assertEqual(
                    payload["report"]["parse_errors"][0]["code"],
                    "unsafe_fixture_ref",
                )
                self.assertEqual(
                    payload["report"]["fixtures"][0]["path"],
                    "<unsafe-csi-fixture-ref>",
                )
                self._assert_no_forbidden_csi_keys(payload)
                self._assert_no_forbidden_csi_words(payload)
                self.assertNotIn(
                    str(REPO_ROOT).replace("\\", "/"),
                    stdout.getvalue().replace("\\", "/"),
                )
                self.assertNotIn("example.invalid", stdout.getvalue())

    def _assert_no_forbidden_csi_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(csi_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_CSI_REPORT_KEYS)
                self._assert_no_forbidden_csi_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_keys(item)

    def _assert_no_forbidden_csi_words(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_csi_words(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_words(item)
        elif isinstance(payload, str):
            lowered = payload.lower()
            for word in FORBIDDEN_CSI_REPORT_WORDS:
                with self.subTest(csi_word=word):
                    self.assertNotIn(word, lowered)

    def _assert_sensor_cli_sanitized(self, encoded):
        for forbidden in (
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "sample-csi-jsonl",
            "environment-parsed.csv",
            "environment-mixed.csv",
            "toy-counter-parsed.csv",
            "toy-counter-mixed.csv",
            "fixture://",
            "fixtures/",
            "fixtures\\",
            "c:/",
            "c:\\",
            "source_id",
            "source_ids",
            "private_ref",
            "provider_payload_body",
            "parser_report_body",
            "parser_summary_body",
            "api_key",
            "access_token",
            "secret_value",
            "raw_values",
            "amplitude",
            "rssi",
            "diagnosis",
            "treatment",
            "medical",
            "health",
        ):
            with self.subTest(sensor_cli_forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)
        self.assertLessEqual(
            encoded.count("real-mode-authorization-missing"),
            6,
        )


if __name__ == "__main__":
    unittest.main()
