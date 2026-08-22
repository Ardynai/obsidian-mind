import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.mock_runtime import run_mock_workflow
from somatic.sensors.registry import (
    SENSOR_EVIDENCE_PROVIDER_MANIFEST_CONTRACT_VERSION,
    classify_sensor_evidence_provider_manifest_compatibility,
    sensor_evidence_provider_manifest,
    validate_sensor_evidence_provider_manifest,
)
from tests.doctor_fixture import DOCTOR_RESULT

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MANIFEST = (
    REPO_ROOT / "fixtures" / "providers" / "sensor-evidence-provider-manifest-v1.json"
)
TOURNAMENT_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-hypothesis-tournament.yaml"


class SensorEvidenceProviderManifestTests(unittest.TestCase):
    def test_manifest_matches_checked_in_snapshot_and_validates(self):
        manifest = sensor_evidence_provider_manifest()
        expected = json.loads(EXPECTED_MANIFEST.read_text(encoding="utf-8"))
        result = validate_sensor_evidence_provider_manifest(manifest)

        self.assertEqual(manifest, expected)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.classification, "compatible")
        self.assertEqual(result.manifest_contract_version, 1)
        self.assertEqual(result.provider_count, 4)
        self.assertEqual(
            manifest["provider_order"],
            ["wifi-csi", "environment-fixture", "toy-counter-fixture", "document-fixture"],
        )
        self.assertEqual(
            [provider["provider_id"] for provider in manifest["providers"]],
            manifest["provider_order"],
        )
        csi_provider = manifest["providers"][0]
        self.assertEqual(csi_provider["provider_id"], "wifi-csi")
        self.assertEqual(
            csi_provider["adapter_kind"],
            "metadata-wifi-csi-source-adapter",
        )
        self.assertEqual(csi_provider["adapter_contract_version"], 1)
        self.assertIn(
            "reference-only",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-model-execution",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-esp32-flashing",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-router-ap-control",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-mqtt-udp-listener",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-smart-home-bridge",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-vitals-inference",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-care-claim",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "rf-booth-review-only",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11a-contract-spec-only",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "real-mode-planning-only",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-runtime-enable",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11b-review-record-fixture",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-review",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11c-preflight-dossier",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-preflight",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11d-lifecycle-audit-record",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-audit",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11e-audit-index",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-index",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11f-audit-handoff",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-handoff",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11g-handoff-acceptance",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-acceptance",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11h-followup-remediation",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-followup",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11i-followup-queue-index",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-queue-index",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn("p11j-decision-closeout", csi_provider["adapter_boundary_labels"])
        self.assertIn(
            "planning-decision-metadata-only",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-closeout",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn("p11k-review-trail-export", csi_provider["adapter_boundary_labels"])
        self.assertIn(
            "review-trail-navigation-only",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-review-trail-export",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn("p11l-runtime-gap-ledger", csi_provider["adapter_boundary_labels"])
        self.assertIn(
            "runtime-disabled-after-gap-ledger",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertIn("p11m-governance-closeout", csi_provider["adapter_boundary_labels"])
        self.assertIn(
            "runtime-disabled-after-governance-closeout",
            csi_provider["adapter_boundary_labels"],
        )
        self.assertEqual(
            csi_provider["readiness_gate_kind"],
            "real-mode-readiness-gate",
        )
        self.assertEqual(
            csi_provider["readiness_gate_status"],
            "blocked-fixture-reference-only",
        )
        self.assertEqual(len(csi_provider["readiness_gate_required_gates"]), 7)
        self.assertEqual(
            csi_provider["readiness_gate_missing_gates"],
            csi_provider["readiness_gate_required_gates"],
        )
        self.assertFalse(csi_provider["readiness_gate_ready"])
        self.assertFalse(csi_provider["real_mode_execution_permitted"])
        self.assertEqual(csi_provider["review_record_contract_version"], 1)
        self.assertEqual(
            csi_provider["review_record_status"],
            "missing-required-reviews",
        )
        self.assertEqual(csi_provider["review_record_reviewed_gate_count"], 0)
        self.assertEqual(csi_provider["review_record_missing_gate_count"], 7)
        self.assertEqual(csi_provider["review_record_rejected_gate_count"], 0)
        self.assertEqual(csi_provider["review_record_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["review_record_execution_permitted"])
        self.assertEqual(csi_provider["preflight_packet_contract_version"], 1)
        self.assertTrue(csi_provider["preflight_packet_id"].startswith("p11c-preflight-"))
        self.assertEqual(len(csi_provider["preflight_packet_fingerprint"]), 64)
        self.assertEqual(
            csi_provider["preflight_packet_status"],
            "missing-required-records",
        )
        self.assertEqual(csi_provider["preflight_packet_reviewed_gate_count"], 0)
        self.assertEqual(csi_provider["preflight_packet_missing_gate_count"], 7)
        self.assertEqual(csi_provider["preflight_packet_rejected_gate_count"], 0)
        self.assertEqual(csi_provider["preflight_packet_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["preflight_packet_execution_permitted"])
        self.assertEqual(csi_provider["lifecycle_audit_contract_version"], 1)
        self.assertTrue(csi_provider["lifecycle_audit_record_id"].startswith("p11d-lifecycle-"))
        self.assertEqual(len(csi_provider["lifecycle_audit_record_fingerprint"]), 64)
        self.assertEqual(csi_provider["lifecycle_audit_stage"], "created")
        self.assertEqual(
            csi_provider["lifecycle_audit_status"],
            "created-runtime-disabled",
        )
        self.assertEqual(
            csi_provider["lifecycle_audit_decision"],
            "needs-more-review",
        )
        self.assertEqual(csi_provider["lifecycle_audit_signoff_verdict"], "blockers")
        self.assertEqual(csi_provider["lifecycle_audit_signoff_count"], 1)
        self.assertEqual(csi_provider["lifecycle_audit_decision_count"], 1)
        self.assertEqual(csi_provider["lifecycle_audit_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["lifecycle_audit_execution_permitted"])
        self.assertEqual(csi_provider["audit_index_contract_version"], 1)
        self.assertTrue(csi_provider["audit_index_id"].startswith("p11e-index-"))
        self.assertEqual(len(csi_provider["audit_index_fingerprint"]), 64)
        self.assertEqual(csi_provider["audit_index_status"], "audit-index-runtime-disabled")
        self.assertEqual(csi_provider["audit_index_entry_count"], 1)
        self.assertEqual(csi_provider["audit_index_blocking_count"], 8)
        self.assertEqual(csi_provider["audit_index_rejection_count"], 0)
        self.assertEqual(csi_provider["audit_index_supersession_chain_count"], 1)
        self.assertEqual(csi_provider["audit_index_change_control_record_count"], 0)
        self.assertEqual(csi_provider["audit_index_export_retention_policy_count"], 1)
        self.assertEqual(csi_provider["audit_index_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["audit_index_execution_permitted"])
        self.assertEqual(csi_provider["handoff_contract_version"], 1)
        self.assertTrue(csi_provider["handoff_id"].startswith("p11f-handoff-"))
        self.assertEqual(len(csi_provider["handoff_fingerprint"]), 64)
        self.assertEqual(csi_provider["handoff_status"], "audit-handoff-runtime-disabled")
        self.assertEqual(csi_provider["handoff_entry_count"], 1)
        self.assertEqual(csi_provider["handoff_blocking_count"], 0)
        self.assertEqual(csi_provider["handoff_rejection_count"], 0)
        self.assertEqual(csi_provider["handoff_unresolved_review_count"], 0)
        self.assertEqual(csi_provider["handoff_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["handoff_execution_permitted"])
        self.assertEqual(csi_provider["handoff_acceptance_contract_version"], 1)
        self.assertTrue(csi_provider["handoff_acceptance_id"].startswith("p11g-acceptance-"))
        self.assertEqual(len(csi_provider["handoff_acceptance_fingerprint"]), 64)
        self.assertEqual(
            csi_provider["handoff_acceptance_status"],
            "accepted-for-planning-runtime-disabled",
        )
        self.assertEqual(
            csi_provider["handoff_acceptance_handoff_label"],
            csi_provider["handoff_id"],
        )
        self.assertEqual(
            csi_provider["handoff_acceptance_handoff_hash"],
            csi_provider["handoff_fingerprint"],
        )
        self.assertTrue(csi_provider["handoff_accepted_for_planning"])
        self.assertFalse(csi_provider["handoff_acceptance_blocked"])
        self.assertFalse(csi_provider["handoff_acceptance_stale"])
        self.assertEqual(csi_provider["handoff_acceptance_missing_review_count"], 0)
        self.assertEqual(
            csi_provider["handoff_acceptance_unresolved_review_count"],
            0,
        )
        self.assertEqual(csi_provider["handoff_acceptance_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["handoff_acceptance_execution_permitted"])
        self.assertEqual(csi_provider["acceptance_followup_contract_version"], 1)
        self.assertTrue(csi_provider["acceptance_followup_id"].startswith("p11h-followup-"))
        self.assertEqual(csi_provider["acceptance_followup_type"], "blocker-disposition")
        self.assertEqual(
            csi_provider["acceptance_followup_status"],
            "resolved-for-planning",
        )
        self.assertEqual(
            csi_provider["acceptance_followup_acceptance_label"],
            csi_provider["handoff_acceptance_id"],
        )
        self.assertEqual(
            csi_provider["acceptance_followup_acceptance_hash"],
            csi_provider["handoff_acceptance_fingerprint"],
        )
        self.assertEqual(
            csi_provider["acceptance_followup_blocker_summary"],
            "blockers-dispositioned",
        )
        self.assertEqual(csi_provider["acceptance_followup_reviewer_summary"], "reviews-clear")
        self.assertEqual(csi_provider["acceptance_followup_stale_summary"], "source-current")
        self.assertEqual(csi_provider["acceptance_followup_unresolved_review_count"], 0)
        self.assertEqual(csi_provider["acceptance_followup_blocking_count"], 0)
        self.assertEqual(csi_provider["acceptance_followup_rejection_count"], 0)
        self.assertEqual(csi_provider["acceptance_followup_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["acceptance_followup_execution_permitted"])
        self.assertEqual(csi_provider["followup_queue_index_contract_version"], 1)
        self.assertTrue(csi_provider["followup_queue_id"].startswith("p11i-queue-"))
        self.assertEqual(len(csi_provider["followup_queue_fingerprint"]), 64)
        self.assertEqual(csi_provider["followup_queue_status"], "stale-queue")
        self.assertEqual(csi_provider["followup_queue_acceptance_status"], "stale-queue")
        self.assertTrue(csi_provider["followup_queue_acceptance_id"].startswith("p11i-check-"))
        self.assertEqual(len(csi_provider["followup_queue_acceptance_fingerprint"]), 64)
        self.assertEqual(csi_provider["followup_queue_entry_count"], 3)
        self.assertEqual(csi_provider["followup_queue_open_count"], 1)
        self.assertEqual(csi_provider["followup_queue_blocked_count"], 0)
        self.assertEqual(csi_provider["followup_queue_stale_count"], 1)
        self.assertEqual(csi_provider["followup_queue_unresolved_review_count"], 0)
        self.assertEqual(csi_provider["followup_queue_blocking_count"], 1)
        self.assertEqual(csi_provider["followup_queue_archived_count"], 1)
        self.assertEqual(csi_provider["followup_queue_rejected_count"], 0)
        self.assertEqual(csi_provider["followup_queue_resolved_for_planning_count"], 1)
        self.assertEqual(csi_provider["followup_queue_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["followup_queue_execution_permitted"])
        self.assertEqual(csi_provider["decision_closeout_contract_version"], 1)
        self.assertTrue(csi_provider["decision_closeout_id"].startswith("p11j-closeout-"))
        self.assertTrue(csi_provider["decision_closeout_queue_label"].startswith("p11i-queue-"))
        self.assertEqual(len(csi_provider["decision_closeout_queue_hash"]), 64)
        self.assertEqual(csi_provider["decision_closeout_decision"], "deferred")
        self.assertEqual(csi_provider["decision_closeout_status"], "incomplete")
        self.assertEqual(
            csi_provider["decision_closeout_reviewer_disposition_summary"],
            "stale-items-deferred",
        )
        self.assertEqual(csi_provider["decision_closeout_unresolved_review_count"], 0)
        self.assertEqual(csi_provider["decision_closeout_blocker_count"], 1)
        self.assertEqual(csi_provider["decision_closeout_stale_count"], 1)
        self.assertEqual(csi_provider["decision_closeout_archived_count"], 1)
        self.assertEqual(csi_provider["decision_closeout_rejected_count"], 0)
        self.assertEqual(csi_provider["decision_closeout_deferred_count"], 1)
        self.assertEqual(
            csi_provider["decision_closeout_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(csi_provider["decision_closeout_execution_permitted"])
        self.assertEqual(csi_provider["review_trail_export_contract_version"], 1)
        self.assertTrue(csi_provider["review_trail_export_id"].startswith("p11k-export-"))
        self.assertEqual(csi_provider["review_trail_phase_range"], "11A-11J")
        self.assertEqual(csi_provider["review_trail_covered_phase_count"], 10)
        self.assertEqual(csi_provider["review_trail_domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(csi_provider["review_trail_closeout_decision"], "deferred")
        self.assertEqual(csi_provider["review_trail_closeout_status"], "incomplete")
        self.assertEqual(csi_provider["review_trail_unresolved_review_count"], 0)
        self.assertEqual(csi_provider["review_trail_blocker_count"], 1)
        self.assertEqual(csi_provider["review_trail_stale_count"], 1)
        self.assertEqual(
            csi_provider["review_trail_readiness_gap_summary"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(csi_provider["review_trail_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["review_trail_execution_permitted"])
        self.assertEqual(csi_provider["runtime_gap_ledger_contract_version"], 1)
        self.assertTrue(csi_provider["runtime_gap_ledger_id"].startswith("p11l-ledger-"))
        self.assertEqual(csi_provider["runtime_gap_phase_range"], "11A-11K")
        self.assertEqual(csi_provider["runtime_gap_covered_phase_count"], 11)
        self.assertEqual(csi_provider["runtime_gap_domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(csi_provider["runtime_gap_authorization_status"], "not-authorized")
        self.assertEqual(
            csi_provider["runtime_gap_readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(csi_provider["runtime_gap_missing_future_gate_count"], 9)
        self.assertEqual(csi_provider["runtime_gap_unresolved_review_count"], 0)
        self.assertEqual(csi_provider["runtime_gap_blocker_count"], 1)
        self.assertEqual(csi_provider["runtime_gap_stale_count"], 1)
        self.assertEqual(csi_provider["runtime_gap_runtime_stage"], "not-implemented")
        self.assertFalse(csi_provider["runtime_gap_adapter_execution_granted"])
        self.assertFalse(csi_provider["runtime_gap_provider_execution_granted"])
        self.assertFalse(csi_provider["runtime_gap_model_execution_granted"])
        self.assertFalse(csi_provider["runtime_gap_execution_permitted"])
        self.assertFalse(csi_provider["runtime_gap_real_mode_runtime_enabled"])
        self.assertEqual(csi_provider["governance_closeout_contract_version"], 1)
        self.assertTrue(csi_provider["governance_closeout_id"].startswith("p11m-closeout-"))
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
        self.assertEqual(
            csi_provider["governance_closeout_next_phase_requirement"],
            "explicit-future-phase-required-before-runtime-work",
        )
        self.assertTrue(
            csi_provider["governance_closeout_gap_ledger_id"].startswith("p11l-ledger-")
        )
        self.assertEqual(csi_provider["governance_closeout_domain_count"], 2)
        self.assertEqual(
            csi_provider["governance_closeout_unresolved_review_count"],
            21,
        )
        self.assertEqual(csi_provider["governance_closeout_blocker_count"], 10)
        self.assertEqual(csi_provider["governance_closeout_stale_count"], 1)
        self.assertEqual(
            csi_provider["governance_closeout_missing_future_gate_count"],
            9,
        )
        self.assertEqual(
            csi_provider["governance_closeout_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(csi_provider["governance_closeout_adapter_execution_granted"])
        self.assertFalse(csi_provider["governance_closeout_provider_execution_granted"])
        self.assertFalse(csi_provider["governance_closeout_model_execution_granted"])
        self.assertFalse(csi_provider["governance_closeout_execution_permitted"])
        self.assertFalse(csi_provider["governance_closeout_real_mode_runtime_enabled"])
        document_provider = manifest["providers"][-1]
        self.assertEqual(document_provider["provider_id"], "document-fixture")
        self.assertEqual(document_provider["provider_kind"], "document-fixture")
        self.assertEqual(document_provider["evidence_kind"], "document-evidence-pack")
        self.assertEqual(document_provider["artifact_name"], "document_evidence_pack")
        self.assertIn(
            "status-readiness-fingerprint",
            document_provider["public_artifact_boundary"],
        )
        self.assertEqual(
            document_provider["adapter_kind"],
            "metadata-document-adapter",
        )
        self.assertEqual(document_provider["adapter_contract_version"], 1)
        self.assertIn(
            "no-network",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-source-id-export",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11a-contract-spec-only",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "real-mode-planning-only",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "no-runtime-enable",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11b-review-record-fixture",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-review",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11c-preflight-dossier",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-preflight",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11d-lifecycle-audit-record",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-audit",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11e-audit-index",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-index",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11f-audit-handoff",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-handoff",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11g-handoff-acceptance",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-acceptance",
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
            "runtime-disabled-after-closeout",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11k-review-trail-export",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "review-trail-navigation-only",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-review-trail-export",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-followup",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "p11m-governance-closeout",
            document_provider["adapter_boundary_labels"],
        )
        self.assertIn(
            "runtime-disabled-after-governance-closeout",
            document_provider["adapter_boundary_labels"],
        )
        self.assertEqual(
            document_provider["readiness_gate_kind"],
            "real-mode-readiness-gate",
        )
        self.assertEqual(
            document_provider["readiness_gate_status"],
            "blocked-fixture-reference-only",
        )
        self.assertEqual(len(document_provider["readiness_gate_required_gates"]), 7)
        self.assertEqual(
            document_provider["readiness_gate_missing_gates"],
            document_provider["readiness_gate_required_gates"],
        )
        self.assertFalse(document_provider["readiness_gate_ready"])
        self.assertFalse(document_provider["real_mode_execution_permitted"])
        self.assertEqual(document_provider["review_record_contract_version"], 1)
        self.assertEqual(
            document_provider["review_record_status"],
            "missing-required-reviews",
        )
        self.assertEqual(document_provider["review_record_reviewed_gate_count"], 0)
        self.assertEqual(document_provider["review_record_missing_gate_count"], 7)
        self.assertEqual(document_provider["review_record_rejected_gate_count"], 0)
        self.assertEqual(
            document_provider["review_record_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["review_record_execution_permitted"])
        self.assertEqual(document_provider["preflight_packet_contract_version"], 1)
        self.assertTrue(document_provider["preflight_packet_id"].startswith("p11c-preflight-"))
        self.assertEqual(len(document_provider["preflight_packet_fingerprint"]), 64)
        self.assertEqual(
            document_provider["preflight_packet_status"],
            "missing-required-records",
        )
        self.assertEqual(document_provider["preflight_packet_reviewed_gate_count"], 0)
        self.assertEqual(document_provider["preflight_packet_missing_gate_count"], 7)
        self.assertEqual(document_provider["preflight_packet_rejected_gate_count"], 0)
        self.assertEqual(
            document_provider["preflight_packet_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["preflight_packet_execution_permitted"])
        self.assertEqual(document_provider["lifecycle_audit_contract_version"], 1)
        self.assertTrue(
            document_provider["lifecycle_audit_record_id"].startswith("p11d-lifecycle-")
        )
        self.assertEqual(
            len(document_provider["lifecycle_audit_record_fingerprint"]),
            64,
        )
        self.assertEqual(document_provider["lifecycle_audit_stage"], "created")
        self.assertEqual(
            document_provider["lifecycle_audit_status"],
            "created-runtime-disabled",
        )
        self.assertEqual(
            document_provider["lifecycle_audit_decision"],
            "needs-more-review",
        )
        self.assertEqual(
            document_provider["lifecycle_audit_signoff_verdict"],
            "blockers",
        )
        self.assertEqual(document_provider["lifecycle_audit_signoff_count"], 1)
        self.assertEqual(document_provider["lifecycle_audit_decision_count"], 1)
        self.assertEqual(
            document_provider["lifecycle_audit_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["lifecycle_audit_execution_permitted"])
        self.assertEqual(document_provider["audit_index_contract_version"], 1)
        self.assertTrue(document_provider["audit_index_id"].startswith("p11e-index-"))
        self.assertEqual(len(document_provider["audit_index_fingerprint"]), 64)
        self.assertEqual(
            document_provider["audit_index_status"],
            "audit-index-runtime-disabled",
        )
        self.assertEqual(document_provider["audit_index_entry_count"], 1)
        self.assertEqual(document_provider["audit_index_blocking_count"], 8)
        self.assertEqual(document_provider["audit_index_rejection_count"], 0)
        self.assertEqual(document_provider["audit_index_supersession_chain_count"], 1)
        self.assertEqual(document_provider["audit_index_change_control_record_count"], 0)
        self.assertEqual(document_provider["audit_index_export_retention_policy_count"], 1)
        self.assertEqual(
            document_provider["audit_index_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["audit_index_execution_permitted"])
        self.assertEqual(document_provider["handoff_contract_version"], 1)
        self.assertTrue(document_provider["handoff_id"].startswith("p11f-handoff-"))
        self.assertEqual(len(document_provider["handoff_fingerprint"]), 64)
        self.assertEqual(
            document_provider["handoff_status"],
            "audit-handoff-runtime-disabled",
        )
        self.assertEqual(document_provider["handoff_entry_count"], 5)
        self.assertEqual(document_provider["handoff_blocking_count"], 10)
        self.assertEqual(document_provider["handoff_rejection_count"], 1)
        self.assertEqual(document_provider["handoff_unresolved_review_count"], 8)
        self.assertEqual(document_provider["handoff_runtime_stage"], "not-implemented")
        self.assertFalse(document_provider["handoff_execution_permitted"])
        self.assertEqual(document_provider["handoff_acceptance_contract_version"], 1)
        self.assertTrue(document_provider["handoff_acceptance_id"].startswith("p11g-acceptance-"))
        self.assertEqual(
            len(document_provider["handoff_acceptance_fingerprint"]),
            64,
        )
        self.assertEqual(
            document_provider["handoff_acceptance_status"],
            "rejected-fail-closed",
        )
        self.assertEqual(
            document_provider["handoff_acceptance_handoff_label"],
            document_provider["handoff_id"],
        )
        self.assertEqual(
            document_provider["handoff_acceptance_handoff_hash"],
            document_provider["handoff_fingerprint"],
        )
        self.assertFalse(document_provider["handoff_accepted_for_planning"])
        self.assertTrue(document_provider["handoff_acceptance_blocked"])
        self.assertFalse(document_provider["handoff_acceptance_stale"])
        self.assertEqual(
            document_provider["handoff_acceptance_missing_review_count"],
            0,
        )
        self.assertEqual(
            document_provider["handoff_acceptance_unresolved_review_count"],
            8,
        )
        self.assertEqual(
            document_provider["handoff_acceptance_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["handoff_acceptance_execution_permitted"])
        self.assertEqual(document_provider["acceptance_followup_contract_version"], 1)
        self.assertTrue(document_provider["acceptance_followup_id"].startswith("p11h-followup-"))
        self.assertEqual(document_provider["acceptance_followup_type"], "needs-more-review")
        self.assertEqual(document_provider["acceptance_followup_status"], "rejected")
        self.assertEqual(
            document_provider["acceptance_followup_acceptance_label"],
            document_provider["handoff_acceptance_id"],
        )
        self.assertEqual(
            document_provider["acceptance_followup_acceptance_hash"],
            document_provider["handoff_acceptance_fingerprint"],
        )
        self.assertEqual(
            document_provider["acceptance_followup_blocker_summary"],
            "source-rejected",
        )
        self.assertEqual(
            document_provider["acceptance_followup_reviewer_summary"],
            "needs-more-review",
        )
        self.assertEqual(
            document_provider["acceptance_followup_stale_summary"],
            "source-current",
        )
        self.assertGreater(
            document_provider["acceptance_followup_unresolved_review_count"],
            0,
        )
        self.assertGreater(document_provider["acceptance_followup_blocking_count"], 0)
        self.assertEqual(document_provider["acceptance_followup_rejection_count"], 1)
        self.assertEqual(
            document_provider["acceptance_followup_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["acceptance_followup_execution_permitted"])
        self.assertEqual(document_provider["followup_queue_index_contract_version"], 1)
        self.assertTrue(document_provider["followup_queue_id"].startswith("p11i-queue-"))
        self.assertEqual(len(document_provider["followup_queue_fingerprint"]), 64)
        self.assertEqual(document_provider["followup_queue_status"], "needs-more-review")
        self.assertEqual(
            document_provider["followup_queue_acceptance_status"],
            "needs-more-review",
        )
        self.assertTrue(document_provider["followup_queue_acceptance_id"].startswith("p11i-check-"))
        self.assertEqual(
            len(document_provider["followup_queue_acceptance_fingerprint"]),
            64,
        )
        self.assertEqual(document_provider["followup_queue_entry_count"], 3)
        self.assertEqual(document_provider["followup_queue_open_count"], 1)
        self.assertEqual(document_provider["followup_queue_blocked_count"], 2)
        self.assertEqual(document_provider["followup_queue_stale_count"], 0)
        self.assertEqual(
            document_provider["followup_queue_unresolved_review_count"],
            21,
        )
        self.assertEqual(document_provider["followup_queue_blocking_count"], 9)
        self.assertEqual(document_provider["followup_queue_archived_count"], 0)
        self.assertEqual(document_provider["followup_queue_rejected_count"], 0)
        self.assertEqual(
            document_provider["followup_queue_resolved_for_planning_count"],
            0,
        )
        self.assertEqual(
            document_provider["followup_queue_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["followup_queue_execution_permitted"])
        self.assertEqual(document_provider["decision_closeout_contract_version"], 1)
        self.assertTrue(document_provider["decision_closeout_id"].startswith("p11j-closeout-"))
        self.assertTrue(
            document_provider["decision_closeout_queue_label"].startswith("p11i-queue-")
        )
        self.assertEqual(len(document_provider["decision_closeout_queue_hash"]), 64)
        self.assertEqual(
            document_provider["decision_closeout_decision"],
            "needs-new-review",
        )
        self.assertEqual(document_provider["decision_closeout_status"], "incomplete")
        self.assertEqual(
            document_provider["decision_closeout_reviewer_disposition_summary"],
            "reviewer-queue-open",
        )
        self.assertEqual(
            document_provider["decision_closeout_unresolved_review_count"],
            21,
        )
        self.assertEqual(document_provider["decision_closeout_blocker_count"], 9)
        self.assertEqual(document_provider["decision_closeout_stale_count"], 0)
        self.assertEqual(document_provider["decision_closeout_archived_count"], 0)
        self.assertEqual(document_provider["decision_closeout_rejected_count"], 0)
        self.assertEqual(document_provider["decision_closeout_deferred_count"], 0)
        self.assertEqual(
            document_provider["decision_closeout_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["decision_closeout_execution_permitted"])
        self.assertEqual(document_provider["review_trail_export_contract_version"], 1)
        self.assertTrue(document_provider["review_trail_export_id"].startswith("p11k-export-"))
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
        self.assertEqual(document_provider["review_trail_stale_count"], 0)
        self.assertEqual(
            document_provider["review_trail_readiness_gap_summary"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(
            document_provider["review_trail_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["review_trail_execution_permitted"])
        self.assertEqual(document_provider["runtime_gap_ledger_contract_version"], 1)
        self.assertTrue(document_provider["runtime_gap_ledger_id"].startswith("p11l-ledger-"))
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
        self.assertEqual(document_provider["runtime_gap_unresolved_review_count"], 21)
        self.assertEqual(document_provider["runtime_gap_blocker_count"], 9)
        self.assertEqual(document_provider["runtime_gap_stale_count"], 0)
        self.assertEqual(
            document_provider["runtime_gap_runtime_stage"],
            "not-implemented",
        )
        self.assertFalse(document_provider["runtime_gap_adapter_execution_granted"])
        self.assertFalse(document_provider["runtime_gap_provider_execution_granted"])
        self.assertFalse(document_provider["runtime_gap_model_execution_granted"])
        self.assertFalse(document_provider["runtime_gap_execution_permitted"])
        self.assertFalse(document_provider["runtime_gap_real_mode_runtime_enabled"])
        self.assertEqual(document_provider["governance_closeout_contract_version"], 1)
        self.assertTrue(document_provider["governance_closeout_id"].startswith("p11m-closeout-"))
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
            document_provider["governance_closeout_next_phase_requirement"],
            "explicit-future-phase-required-before-runtime-work",
        )
        self.assertTrue(
            document_provider["governance_closeout_gap_ledger_id"].startswith("p11l-ledger-")
        )
        self.assertEqual(document_provider["governance_closeout_domain_count"], 2)
        self.assertEqual(
            document_provider["governance_closeout_unresolved_review_count"],
            21,
        )
        self.assertEqual(document_provider["governance_closeout_blocker_count"], 10)
        self.assertEqual(document_provider["governance_closeout_stale_count"], 1)
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

    def test_manifest_generation_is_deterministic(self):
        first = sensor_evidence_provider_manifest()
        second = sensor_evidence_provider_manifest()

        self.assertEqual(first, second)
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )

    def test_cli_provider_json_is_the_manifest_contract(self):
        first_stdout = io.StringIO()
        second_stdout = io.StringIO()

        with contextlib.redirect_stdout(first_stdout):
            first_exit = main(["sensor-evidence", "providers", "--format", "json"])
        with contextlib.redirect_stdout(second_stdout):
            second_exit = main(["sensor-evidence", "providers", "--format", "json"])

        first_payload = json.loads(first_stdout.getvalue())
        second_payload = json.loads(second_stdout.getvalue())
        self.assertEqual(first_exit, 0)
        self.assertEqual(second_exit, 0)
        self.assertEqual(first_payload, sensor_evidence_provider_manifest())
        self.assertEqual(first_payload, second_payload)
        self._assert_manifest_sanitized(first_payload)

    def test_cli_provider_text_renders_manifest_order(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(["sensor-evidence", "providers"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        positions = [
            output.index("- wifi-csi:"),
            output.index("- environment-fixture:"),
            output.index("- toy-counter-fixture:"),
            output.index("- document-fixture:"),
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("adapter_boundary=metadata-only,reference-only,offline", output)
        self.assertIn("adapter_boundary=metadata-only,fixture-only,offline", output)
        self._assert_manifest_sanitized(output)

    def test_doctor_summarizes_registry_without_dumping_manifest(self):
        exit_code, output = DOCTOR_RESULT
        output = output.lower()
        self.assertEqual(exit_code, 0)
        self.assertIn("sensor evidence provider count: 4", output)
        self.assertIn("sensor evidence registry validation: valid", output)
        for internal in (
            "manifest_contract_version",
            "provider_order",
            "public_artifact_boundary",
            "artifact_ref",
            "private_artifact_boundary",
            "max_fixture_refs",
        ):
            with self.subTest(internal=internal):
                self.assertNotIn(internal, output)
        self.assertNotIn("sample-esp32-csi", output)
        self.assertNotIn("environment-parsed.csv", output)
        self.assertNotIn("toy-counter-parsed.csv", output)
        self.assertNotIn("fixture://", output)

    def test_manifest_compatibility_rejects_malformed_unsupported_and_incompatible(self):
        self.assertEqual(
            classify_sensor_evidence_provider_manifest_compatibility(
                "not-a-manifest"
            ).classification,
            "malformed",
        )

        unsupported = sensor_evidence_provider_manifest()
        unsupported["manifest_contract_version"] = (
            SENSOR_EVIDENCE_PROVIDER_MANIFEST_CONTRACT_VERSION + 1
        )
        self.assertEqual(
            validate_sensor_evidence_provider_manifest(unsupported).classification,
            "unsupported_version",
        )

        missing = sensor_evidence_provider_manifest()
        missing.pop("provider_count")
        missing_result = validate_sensor_evidence_provider_manifest(missing)
        self.assertEqual(missing_result.classification, "incompatible")
        self.assertIn(
            "manifest:sensor_provider_manifest_required_field_missing",
            missing_result.errors,
        )

        reordered = sensor_evidence_provider_manifest()
        reordered["providers"] = list(reversed(reordered["providers"]))
        reordered_result = validate_sensor_evidence_provider_manifest(reordered)
        self.assertEqual(reordered_result.classification, "incompatible")
        self.assertIn(
            "manifest.providers:sensor_provider_manifest_order_invalid",
            reordered_result.errors,
        )

    def test_manifest_accepts_safe_additive_metadata(self):
        manifest = sensor_evidence_provider_manifest()
        manifest["public_note"] = "stable-public-registry-snapshot"
        manifest["providers"][0]["public_note"] = "stable-provider-label"

        result = validate_sensor_evidence_provider_manifest(manifest)

        self.assertTrue(result.compatible, result.errors)

    def test_manifest_rejects_real_mode_readiness_gate_drift(self):
        for field, value in (
            ("readiness_gate_status", "ready"),
            ("readiness_gate_missing_gates", []),
            ("readiness_gate_ready", True),
            ("real_mode_execution_permitted", True),
        ):
            with self.subTest(field=field):
                manifest = sensor_evidence_provider_manifest()
                manifest["providers"][0][field] = value

                result = validate_sensor_evidence_provider_manifest(manifest)

                self.assertEqual(result.classification, "incompatible")
                self.assertIn(
                    f"manifest.providers:sensor_provider_manifest_provider_{field}_invalid",
                    result.errors,
                )

        missing = sensor_evidence_provider_manifest()
        missing["providers"][0].pop("real_mode_execution_permitted")

        missing_result = validate_sensor_evidence_provider_manifest(missing)

        self.assertEqual(missing_result.classification, "incompatible")
        self.assertIn(
            "manifest.providers:sensor_provider_manifest_provider_real_mode_execution_permitted_missing",
            missing_result.errors,
        )

    def test_manifest_rejects_private_or_internal_metadata_without_echoing_values(self):
        manifest = sensor_evidence_provider_manifest()
        manifest["providers"][0]["artifact_ref"] = "artifacts/csi_evidence_pack.json"
        manifest["providers"][0]["provider_payload_body"] = "private payload body"
        manifest["public_note"] = "C:/Users/Josh/private.csv"

        result = validate_sensor_evidence_provider_manifest(manifest)
        encoded = json.dumps(result.to_dict(), sort_keys=True).lower()

        self.assertEqual(result.classification, "incompatible")
        self.assertIn("sensor_provider_manifest_private_field_present", encoded)
        self.assertIn("sensor_provider_manifest_private_scalar_present", encoded)
        for forbidden in (
            "artifacts/csi_evidence_pack.json",
            "provider_payload_body",
            "private payload body",
            "c:/users/josh",
            "private.csv",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def test_manifest_generation_does_not_change_tournament_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            before = run_mock_workflow(
                TOURNAMENT_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=output_root,
                run_id="run-before-manifest",
            )
            sensor_evidence_provider_manifest()
            after = run_mock_workflow(
                TOURNAMENT_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=output_root,
                run_id="run-after-manifest",
            )

            for relative in (
                "artifacts/ranked_hypotheses.json",
                "artifacts/elo_ratings.json",
                "artifacts/tournament_bracket.json",
            ):
                with self.subTest(relative=relative):
                    left = json.loads((before / relative).read_text(encoding="utf-8"))
                    right = json.loads((after / relative).read_text(encoding="utf-8"))
                    self.assertEqual(left, right)

    def test_manifest_required_field_set_is_stable(self):
        manifest = sensor_evidence_provider_manifest()
        self.assertEqual(
            set(manifest),
            {
                "schema_version",
                "manifest_contract_version",
                "manifest_kind",
                "provider_count",
                "provider_order",
                "providers",
                "sanitized",
                "metadata_only",
                "offline_fixture_only",
                "public_boundary_label",
            },
        )
        self.assertEqual(
            set(manifest["providers"][0]),
            {
                "provider_id",
                "provider_kind",
                "evidence_kind",
                "contract_version",
                "contract_identity",
                "artifact_name",
                "fixture_mode_labels",
                "supported_fixture_formats",
                "offline_fixture_only",
                "metadata_only",
                "sanitized",
                "public_artifact_boundary",
                "adapter_contract_version",
                "adapter_kind",
                "adapter_boundary_labels",
                "readiness_gate_contract_version",
                "readiness_gate_kind",
                "readiness_gate_status",
                "readiness_gate_required_gates",
                "readiness_gate_missing_gates",
                "readiness_gate_ready",
                "real_mode_execution_permitted",
                "review_record_contract_version",
                "review_record_status",
                "review_record_reviewed_gate_count",
                "review_record_missing_gate_count",
                "review_record_rejected_gate_count",
                "review_record_runtime_stage",
                "review_record_execution_permitted",
                "preflight_packet_contract_version",
                "preflight_packet_id",
                "preflight_packet_fingerprint",
                "preflight_packet_status",
                "preflight_packet_reviewed_gate_count",
                "preflight_packet_missing_gate_count",
                "preflight_packet_rejected_gate_count",
                "preflight_packet_runtime_stage",
                "preflight_packet_execution_permitted",
                "lifecycle_audit_contract_version",
                "lifecycle_audit_record_id",
                "lifecycle_audit_record_fingerprint",
                "lifecycle_audit_stage",
                "lifecycle_audit_status",
                "lifecycle_audit_decision",
                "lifecycle_audit_signoff_verdict",
                "lifecycle_audit_signoff_count",
                "lifecycle_audit_decision_count",
                "lifecycle_audit_runtime_stage",
                "lifecycle_audit_execution_permitted",
                "audit_index_contract_version",
                "audit_index_id",
                "audit_index_fingerprint",
                "audit_index_status",
                "audit_index_entry_count",
                "audit_index_blocking_count",
                "audit_index_rejection_count",
                "audit_index_supersession_chain_count",
                "audit_index_change_control_record_count",
                "audit_index_export_retention_policy_count",
                "audit_index_runtime_stage",
                "audit_index_execution_permitted",
                "handoff_contract_version",
                "handoff_id",
                "handoff_fingerprint",
                "handoff_status",
                "handoff_entry_count",
                "handoff_blocking_count",
                "handoff_rejection_count",
                "handoff_unresolved_review_count",
                "handoff_runtime_stage",
                "handoff_execution_permitted",
                "handoff_acceptance_contract_version",
                "handoff_acceptance_id",
                "handoff_acceptance_fingerprint",
                "handoff_acceptance_status",
                "handoff_acceptance_handoff_label",
                "handoff_acceptance_handoff_hash",
                "handoff_acceptance_handoff_fingerprint",
                "handoff_accepted_for_planning",
                "handoff_acceptance_blocked",
                "handoff_acceptance_stale",
                "handoff_acceptance_missing_review_count",
                "handoff_acceptance_unresolved_review_count",
                "handoff_acceptance_rejection_reason_count",
                "handoff_acceptance_blocking_reason_count",
                "handoff_acceptance_runtime_stage",
                "handoff_acceptance_execution_permitted",
                "acceptance_followup_contract_version",
                "acceptance_followup_id",
                "acceptance_followup_type",
                "acceptance_followup_status",
                "acceptance_followup_acceptance_label",
                "acceptance_followup_acceptance_hash",
                "acceptance_followup_blocker_summary",
                "acceptance_followup_reviewer_summary",
                "acceptance_followup_stale_summary",
                "acceptance_followup_unresolved_review_count",
                "acceptance_followup_blocking_count",
                "acceptance_followup_rejection_count",
                "acceptance_followup_runtime_stage",
                "acceptance_followup_execution_permitted",
                "followup_queue_index_contract_version",
                "followup_queue_id",
                "followup_queue_fingerprint",
                "followup_queue_status",
                "followup_queue_acceptance_status",
                "followup_queue_acceptance_id",
                "followup_queue_acceptance_fingerprint",
                "followup_queue_entry_count",
                "followup_queue_open_count",
                "followup_queue_blocked_count",
                "followup_queue_stale_count",
                "followup_queue_unresolved_review_count",
                "followup_queue_blocking_count",
                "followup_queue_archived_count",
                "followup_queue_rejected_count",
                "followup_queue_resolved_for_planning_count",
                "followup_queue_runtime_stage",
                "followup_queue_execution_permitted",
                "decision_closeout_contract_version",
                "decision_closeout_id",
                "decision_closeout_queue_label",
                "decision_closeout_queue_hash",
                "decision_closeout_decision",
                "decision_closeout_status",
                "decision_closeout_reviewer_disposition_summary",
                "decision_closeout_unresolved_review_count",
                "decision_closeout_blocker_count",
                "decision_closeout_stale_count",
                "decision_closeout_archived_count",
                "decision_closeout_rejected_count",
                "decision_closeout_deferred_count",
                "decision_closeout_runtime_stage",
                "decision_closeout_execution_permitted",
                "review_trail_export_contract_version",
                "review_trail_export_id",
                "review_trail_phase_range",
                "review_trail_covered_phase_count",
                "review_trail_domain_label",
                "review_trail_closeout_decision",
                "review_trail_closeout_status",
                "review_trail_unresolved_review_count",
                "review_trail_blocker_count",
                "review_trail_stale_count",
                "review_trail_readiness_gap_summary",
                "review_trail_runtime_stage",
                "review_trail_execution_permitted",
                "runtime_gap_ledger_contract_version",
                "runtime_gap_ledger_id",
                "runtime_gap_phase_range",
                "runtime_gap_covered_phase_count",
                "runtime_gap_domain_label",
                "runtime_gap_authorization_status",
                "runtime_gap_readiness_gap",
                "runtime_gap_missing_future_gate_count",
                "runtime_gap_unresolved_review_count",
                "runtime_gap_blocker_count",
                "runtime_gap_stale_count",
                "runtime_gap_adapter_execution_granted",
                "runtime_gap_provider_execution_granted",
                "runtime_gap_model_execution_granted",
                "runtime_gap_runtime_stage",
                "runtime_gap_execution_permitted",
                "runtime_gap_real_mode_runtime_enabled",
                "governance_closeout_contract_version",
                "governance_closeout_id",
                "governance_closeout_phase_range",
                "governance_closeout_covered_phase_count",
                "governance_closeout_final_status",
                "governance_closeout_runtime_authorization_status",
                "governance_closeout_readiness_gap",
                "governance_closeout_next_phase_requirement",
                "governance_closeout_gap_ledger_id",
                "governance_closeout_domain_count",
                "governance_closeout_unresolved_review_count",
                "governance_closeout_blocker_count",
                "governance_closeout_stale_count",
                "governance_closeout_missing_future_gate_count",
                "governance_closeout_adapter_execution_granted",
                "governance_closeout_provider_execution_granted",
                "governance_closeout_model_execution_granted",
                "governance_closeout_runtime_stage",
                "governance_closeout_execution_permitted",
                "governance_closeout_real_mode_runtime_enabled",
            },
        )
        self.assertEqual(
            set(manifest["providers"][-1]) - set(manifest["providers"][0]),
            set(),
        )

    def _assert_manifest_sanitized(self, payload):
        encoded = (
            json.dumps(payload, sort_keys=True).lower()
            if not isinstance(payload, str)
            else payload.lower()
        )
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
            "unsafe_ref",
            "provider_payload",
            "provider_payload_body",
            "parser_report_body",
            "parser_summary_body",
            "api_key",
            "access_token",
            "secret_value",
            "raw_values",
            "raw_signal",
            "signal_values",
            "amplitude",
            "rssi",
            "clinical",
            "diagnosis",
            "treatment",
            "medical",
            "health",
        ):
            with self.subTest(manifest_forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)
        self.assertLessEqual(encoded.count("real-mode-authorization-missing"), 6)


if __name__ == "__main__":
    unittest.main()
