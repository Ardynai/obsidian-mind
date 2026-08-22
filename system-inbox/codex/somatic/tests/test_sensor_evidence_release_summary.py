import json
import re
import unittest
from pathlib import Path

from somatic.sensors.registry import (
    SENSOR_EVIDENCE_PROVIDER_MANIFEST_COMPATIBILITY_CLASSIFICATIONS,
    sensor_evidence_provider_manifest,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_DOC = REPO_ROOT / "docs" / "phase-9h-release-summary.md"
CHECKPOINT_DOC = REPO_ROOT / "docs" / "phase-10-checkpoint.md"
PHASE11_DOC = REPO_ROOT / "docs" / "phase-11a-real-mode-contract-specs.md"
PHASE11B_DOC = REPO_ROOT / "docs" / "phase-11b-review-record-fixtures.md"
PHASE11C_DOC = REPO_ROOT / "docs" / "phase-11c-preflight-dossiers.md"
PHASE11D_DOC = REPO_ROOT / "docs" / "phase-11d-dossier-lifecycle.md"
PHASE11E_DOC = REPO_ROOT / "docs" / "phase-11e-audit-index-change-control.md"
PHASE11F_DOC = REPO_ROOT / "docs" / "phase-11f-audit-handoff-reporting.md"
PHASE11G_DOC = REPO_ROOT / "docs" / "phase-11g-handoff-acceptance.md"
PHASE11H_DOC = REPO_ROOT / "docs" / "phase-11h-followup-remediation.md"
PHASE11I_DOC = REPO_ROOT / "docs" / "phase-11i-followup-queue-index.md"
PHASE11J_DOC = REPO_ROOT / "docs" / "phase-11j-decision-closeout.md"
PHASE11K_DOC = REPO_ROOT / "docs" / "phase-11k-review-trail-export.md"
PHASE11L_DOC = REPO_ROOT / "docs" / "phase-11l-runtime-authorization-gap-ledger.md"
PHASE11M_DOC = REPO_ROOT / "docs" / "phase-11m-planning-governance-closeout.md"
SUMMARY_JSON = REPO_ROOT / "fixtures" / "reports" / "sensor-evidence-subsystem-summary-v1.json"
CLI_DOC = REPO_ROOT / "docs" / "cli.md"
CLI_TESTS = REPO_ROOT / "tests" / "test_cli_commands.py"


class SensorEvidenceReleaseSummaryTests(unittest.TestCase):
    def test_release_summary_artifacts_exist(self):
        self.assertTrue(SUMMARY_DOC.exists())
        self.assertTrue(CHECKPOINT_DOC.exists())
        self.assertTrue(PHASE11_DOC.exists())
        self.assertTrue(PHASE11B_DOC.exists())
        self.assertTrue(PHASE11C_DOC.exists())
        self.assertTrue(PHASE11D_DOC.exists())
        self.assertTrue(PHASE11E_DOC.exists())
        self.assertTrue(PHASE11F_DOC.exists())
        self.assertTrue(PHASE11G_DOC.exists())
        self.assertTrue(PHASE11H_DOC.exists())
        self.assertTrue(PHASE11I_DOC.exists())
        self.assertTrue(PHASE11J_DOC.exists())
        self.assertTrue(PHASE11K_DOC.exists())
        self.assertTrue(PHASE11L_DOC.exists())
        self.assertTrue(PHASE11M_DOC.exists())
        self.assertTrue(SUMMARY_JSON.exists())

    def test_machine_summary_aligns_with_provider_manifest(self):
        summary = self._read_summary()
        manifest = sensor_evidence_provider_manifest()

        self.assertEqual(summary["schema_version"], 1)
        self.assertEqual(
            summary["summary_id"],
            "sensor-evidence-subsystem-phase-8c-through-11m",
        )
        self.assertEqual(summary["phase_range"], "8C-11M")
        self.assertEqual(
            summary["provider_manifest_contract_version"],
            manifest["manifest_contract_version"],
        )
        self.assertEqual(summary["provider_count"], manifest["provider_count"])
        self.assertEqual(
            [provider["provider_id"] for provider in summary["providers"]],
            manifest["provider_order"],
        )
        self.assertEqual(
            summary["compatibility_classifications"],
            list(SENSOR_EVIDENCE_PROVIDER_MANIFEST_COMPATIBILITY_CLASSIFICATIONS),
        )

        manifest_by_id = {provider["provider_id"]: provider for provider in manifest["providers"]}
        for provider in summary["providers"]:
            manifest_provider = manifest_by_id[provider["provider_id"]]
            self.assertEqual(
                provider["evidence_kind"],
                manifest_provider["evidence_kind"],
            )
            self.assertEqual(
                provider["artifact_name"],
                manifest_provider["artifact_name"],
            )
            if provider["provider_id"] in {"wifi-csi", "document-fixture"}:
                self.assertEqual(
                    provider["preflight_packet_contract_version"],
                    manifest_provider["preflight_packet_contract_version"],
                )
                self.assertEqual(
                    provider["preflight_packet_status"],
                    manifest_provider["preflight_packet_status"],
                )
                self.assertEqual(
                    provider["preflight_packet_missing_gate_count"],
                    manifest_provider["preflight_packet_missing_gate_count"],
                )
                self.assertEqual(
                    provider["preflight_packet_runtime_stage"],
                    manifest_provider["preflight_packet_runtime_stage"],
                )
                self.assertFalse(provider["preflight_packet_execution_permitted"])
                self.assertEqual(
                    provider["lifecycle_audit_contract_version"],
                    manifest_provider["lifecycle_audit_contract_version"],
                )
                self.assertEqual(
                    provider["lifecycle_audit_stage"],
                    manifest_provider["lifecycle_audit_stage"],
                )
                self.assertEqual(
                    provider["lifecycle_audit_decision"],
                    manifest_provider["lifecycle_audit_decision"],
                )
                self.assertEqual(
                    provider["lifecycle_audit_runtime_stage"],
                    manifest_provider["lifecycle_audit_runtime_stage"],
                )
                self.assertFalse(provider["lifecycle_audit_execution_permitted"])
                self.assertEqual(
                    provider["audit_index_contract_version"],
                    manifest_provider["audit_index_contract_version"],
                )
                self.assertEqual(
                    provider["audit_index_status"],
                    manifest_provider["audit_index_status"],
                )
                self.assertEqual(
                    provider["audit_index_entry_count"],
                    manifest_provider["audit_index_entry_count"],
                )
                self.assertEqual(
                    provider["audit_index_runtime_stage"],
                    manifest_provider["audit_index_runtime_stage"],
                )
                self.assertFalse(provider["audit_index_execution_permitted"])
                self.assertEqual(
                    provider["handoff_status"],
                    manifest_provider["handoff_status"],
                )
                self.assertEqual(
                    provider["handoff_entry_count"],
                    manifest_provider["handoff_entry_count"],
                )
                self.assertEqual(
                    provider["handoff_runtime_stage"],
                    manifest_provider["handoff_runtime_stage"],
                )
                self.assertFalse(provider["handoff_execution_permitted"])
                self.assertEqual(
                    provider["handoff_acceptance_contract_version"],
                    manifest_provider["handoff_acceptance_contract_version"],
                )
                self.assertEqual(
                    provider["handoff_acceptance_status"],
                    manifest_provider["handoff_acceptance_status"],
                )
                self.assertEqual(
                    provider["handoff_accepted_for_planning"],
                    manifest_provider["handoff_accepted_for_planning"],
                )
                self.assertEqual(
                    provider["handoff_acceptance_blocked"],
                    manifest_provider["handoff_acceptance_blocked"],
                )
                self.assertEqual(
                    provider["handoff_acceptance_stale"],
                    manifest_provider["handoff_acceptance_stale"],
                )
                self.assertEqual(
                    provider["handoff_acceptance_missing_review_count"],
                    manifest_provider["handoff_acceptance_missing_review_count"],
                )
                self.assertEqual(
                    provider["handoff_acceptance_unresolved_review_count"],
                    manifest_provider["handoff_acceptance_unresolved_review_count"],
                )
                self.assertEqual(
                    provider["handoff_acceptance_runtime_stage"],
                    manifest_provider["handoff_acceptance_runtime_stage"],
                )
                self.assertFalse(provider["handoff_acceptance_execution_permitted"])
                self.assertEqual(
                    provider["acceptance_followup_contract_version"],
                    manifest_provider["acceptance_followup_contract_version"],
                )
                self.assertEqual(
                    provider["acceptance_followup_type"],
                    manifest_provider["acceptance_followup_type"],
                )
                self.assertEqual(
                    provider["acceptance_followup_status"],
                    manifest_provider["acceptance_followup_status"],
                )
                self.assertEqual(
                    provider["acceptance_followup_acceptance_label"],
                    manifest_provider["acceptance_followup_acceptance_label"],
                )
                self.assertEqual(
                    provider["acceptance_followup_acceptance_hash"],
                    manifest_provider["acceptance_followup_acceptance_hash"],
                )
                self.assertEqual(
                    provider["acceptance_followup_stale_summary"],
                    manifest_provider["acceptance_followup_stale_summary"],
                )
                self.assertEqual(
                    provider["acceptance_followup_blocker_summary"],
                    manifest_provider["acceptance_followup_blocker_summary"],
                )
                self.assertEqual(
                    provider["acceptance_followup_reviewer_summary"],
                    manifest_provider["acceptance_followup_reviewer_summary"],
                )
                self.assertEqual(
                    provider["acceptance_followup_blocking_count"],
                    manifest_provider["acceptance_followup_blocking_count"],
                )
                self.assertEqual(
                    provider["acceptance_followup_unresolved_review_count"],
                    manifest_provider["acceptance_followup_unresolved_review_count"],
                )
                self.assertEqual(
                    provider["acceptance_followup_rejection_count"],
                    manifest_provider["acceptance_followup_rejection_count"],
                )
                self.assertEqual(
                    provider["acceptance_followup_runtime_stage"],
                    manifest_provider["acceptance_followup_runtime_stage"],
                )
                self.assertFalse(provider["acceptance_followup_execution_permitted"])
                self.assertEqual(
                    provider["followup_queue_index_contract_version"],
                    manifest_provider["followup_queue_index_contract_version"],
                )
                self.assertEqual(
                    provider["followup_queue_status"],
                    manifest_provider["followup_queue_status"],
                )
                self.assertEqual(
                    provider["followup_queue_acceptance_status"],
                    manifest_provider["followup_queue_acceptance_status"],
                )
                self.assertEqual(
                    provider["followup_queue_entry_count"],
                    manifest_provider["followup_queue_entry_count"],
                )
                self.assertEqual(
                    provider["followup_queue_open_count"],
                    manifest_provider["followup_queue_open_count"],
                )
                self.assertEqual(
                    provider["followup_queue_blocked_count"],
                    manifest_provider["followup_queue_blocked_count"],
                )
                self.assertEqual(
                    provider["followup_queue_stale_count"],
                    manifest_provider["followup_queue_stale_count"],
                )
                self.assertEqual(
                    provider["followup_queue_unresolved_review_count"],
                    manifest_provider["followup_queue_unresolved_review_count"],
                )
                self.assertEqual(
                    provider["followup_queue_blocking_count"],
                    manifest_provider["followup_queue_blocking_count"],
                )
                self.assertEqual(
                    provider["followup_queue_archived_count"],
                    manifest_provider["followup_queue_archived_count"],
                )
                self.assertEqual(
                    provider["followup_queue_rejected_count"],
                    manifest_provider["followup_queue_rejected_count"],
                )
                self.assertEqual(
                    provider["followup_queue_resolved_for_planning_count"],
                    manifest_provider["followup_queue_resolved_for_planning_count"],
                )
                self.assertEqual(
                    provider["followup_queue_runtime_stage"],
                    manifest_provider["followup_queue_runtime_stage"],
                )
                self.assertFalse(provider["followup_queue_execution_permitted"])
                self.assertEqual(
                    provider["decision_closeout_contract_version"],
                    manifest_provider["decision_closeout_contract_version"],
                )
                self.assertEqual(
                    provider["decision_closeout_decision"],
                    manifest_provider["decision_closeout_decision"],
                )
                self.assertEqual(
                    provider["decision_closeout_status"],
                    manifest_provider["decision_closeout_status"],
                )
                self.assertEqual(
                    provider["decision_closeout_queue_label"],
                    manifest_provider["decision_closeout_queue_label"],
                )
                self.assertEqual(
                    provider["decision_closeout_queue_hash"],
                    manifest_provider["decision_closeout_queue_hash"],
                )
                self.assertEqual(
                    provider["decision_closeout_unresolved_review_count"],
                    manifest_provider["decision_closeout_unresolved_review_count"],
                )
                self.assertEqual(
                    provider["decision_closeout_blocker_count"],
                    manifest_provider["decision_closeout_blocker_count"],
                )
                self.assertEqual(
                    provider["decision_closeout_stale_count"],
                    manifest_provider["decision_closeout_stale_count"],
                )
                self.assertEqual(
                    provider["decision_closeout_runtime_stage"],
                    manifest_provider["decision_closeout_runtime_stage"],
                )
                self.assertFalse(provider["decision_closeout_execution_permitted"])
                self.assertEqual(
                    provider["review_trail_export_contract_version"],
                    manifest_provider["review_trail_export_contract_version"],
                )
                self.assertEqual(
                    provider["review_trail_export_id"],
                    manifest_provider["review_trail_export_id"],
                )
                self.assertEqual(
                    provider["review_trail_phase_range"],
                    manifest_provider["review_trail_phase_range"],
                )
                self.assertEqual(
                    provider["review_trail_covered_phase_count"],
                    manifest_provider["review_trail_covered_phase_count"],
                )
                self.assertEqual(
                    provider["review_trail_domain_label"],
                    manifest_provider["review_trail_domain_label"],
                )
                self.assertEqual(
                    provider["review_trail_closeout_decision"],
                    manifest_provider["review_trail_closeout_decision"],
                )
                self.assertEqual(
                    provider["review_trail_closeout_status"],
                    manifest_provider["review_trail_closeout_status"],
                )
                self.assertEqual(
                    provider["review_trail_unresolved_review_count"],
                    manifest_provider["review_trail_unresolved_review_count"],
                )
                self.assertEqual(
                    provider["review_trail_blocker_count"],
                    manifest_provider["review_trail_blocker_count"],
                )
                self.assertEqual(
                    provider["review_trail_stale_count"],
                    manifest_provider["review_trail_stale_count"],
                )
                self.assertEqual(
                    provider["review_trail_readiness_gap_summary"],
                    manifest_provider["review_trail_readiness_gap_summary"],
                )
                self.assertEqual(
                    provider["review_trail_runtime_stage"],
                    manifest_provider["review_trail_runtime_stage"],
                )
                self.assertFalse(provider["review_trail_execution_permitted"])
                self.assertEqual(
                    provider["runtime_gap_ledger_contract_version"],
                    manifest_provider["runtime_gap_ledger_contract_version"],
                )
                self.assertEqual(
                    provider["runtime_gap_ledger_id"],
                    manifest_provider["runtime_gap_ledger_id"],
                )
                self.assertEqual(
                    provider["runtime_gap_phase_range"],
                    manifest_provider["runtime_gap_phase_range"],
                )
                self.assertEqual(
                    provider["runtime_gap_covered_phase_count"],
                    manifest_provider["runtime_gap_covered_phase_count"],
                )
                self.assertEqual(
                    provider["runtime_gap_domain_label"],
                    manifest_provider["runtime_gap_domain_label"],
                )
                self.assertEqual(
                    provider["runtime_gap_authorization_status"],
                    manifest_provider["runtime_gap_authorization_status"],
                )
                self.assertEqual(
                    provider["runtime_gap_readiness_gap"],
                    manifest_provider["runtime_gap_readiness_gap"],
                )
                self.assertEqual(
                    provider["runtime_gap_missing_future_gate_count"],
                    manifest_provider["runtime_gap_missing_future_gate_count"],
                )
                self.assertEqual(
                    provider["runtime_gap_unresolved_review_count"],
                    manifest_provider["runtime_gap_unresolved_review_count"],
                )
                self.assertEqual(
                    provider["runtime_gap_blocker_count"],
                    manifest_provider["runtime_gap_blocker_count"],
                )
                self.assertEqual(
                    provider["runtime_gap_stale_count"],
                    manifest_provider["runtime_gap_stale_count"],
                )
                self.assertEqual(
                    provider["runtime_gap_runtime_stage"],
                    manifest_provider["runtime_gap_runtime_stage"],
                )
                self.assertFalse(provider["runtime_gap_adapter_execution_granted"])
                self.assertFalse(provider["runtime_gap_provider_execution_granted"])
                self.assertFalse(provider["runtime_gap_model_execution_granted"])
                self.assertFalse(provider["runtime_gap_execution_permitted"])
                self.assertFalse(provider["runtime_gap_real_mode_runtime_enabled"])
                self.assertEqual(
                    provider["governance_closeout_contract_version"],
                    manifest_provider["governance_closeout_contract_version"],
                )
                self.assertEqual(
                    provider["governance_closeout_id"],
                    manifest_provider["governance_closeout_id"],
                )
                self.assertEqual(
                    provider["governance_closeout_phase_range"],
                    manifest_provider["governance_closeout_phase_range"],
                )
                self.assertEqual(
                    provider["governance_closeout_covered_phase_count"],
                    manifest_provider["governance_closeout_covered_phase_count"],
                )
                self.assertEqual(
                    provider["governance_closeout_final_status"],
                    manifest_provider["governance_closeout_final_status"],
                )
                self.assertEqual(
                    provider["governance_closeout_runtime_authorization_status"],
                    manifest_provider["governance_closeout_runtime_authorization_status"],
                )
                self.assertEqual(
                    provider["governance_closeout_readiness_gap"],
                    manifest_provider["governance_closeout_readiness_gap"],
                )
                self.assertEqual(
                    provider["governance_closeout_next_phase_requirement"],
                    manifest_provider["governance_closeout_next_phase_requirement"],
                )
                self.assertEqual(
                    provider["governance_closeout_gap_ledger_id"],
                    manifest_provider["governance_closeout_gap_ledger_id"],
                )
                self.assertEqual(
                    provider["governance_closeout_domain_count"],
                    manifest_provider["governance_closeout_domain_count"],
                )
                self.assertEqual(
                    provider["governance_closeout_unresolved_review_count"],
                    manifest_provider["governance_closeout_unresolved_review_count"],
                )
                self.assertEqual(
                    provider["governance_closeout_blocker_count"],
                    manifest_provider["governance_closeout_blocker_count"],
                )
                self.assertEqual(
                    provider["governance_closeout_stale_count"],
                    manifest_provider["governance_closeout_stale_count"],
                )
                self.assertEqual(
                    provider["governance_closeout_missing_future_gate_count"],
                    manifest_provider["governance_closeout_missing_future_gate_count"],
                )
                self.assertEqual(
                    provider["governance_closeout_runtime_stage"],
                    manifest_provider["governance_closeout_runtime_stage"],
                )
                self.assertFalse(provider["governance_closeout_adapter_execution_granted"])
                self.assertFalse(provider["governance_closeout_provider_execution_granted"])
                self.assertFalse(provider["governance_closeout_model_execution_granted"])
                self.assertFalse(provider["governance_closeout_execution_permitted"])
                self.assertFalse(provider["governance_closeout_real_mode_runtime_enabled"])

    def test_human_summary_references_current_contracts_and_providers(self):
        text = SUMMARY_DOC.read_text(encoding="utf-8")
        summary = self._read_summary()

        self.assertIn("Phase 8C through Phase 11M", text)
        self.assertIn("manifest contract version is 1", text)
        self.assertIn("provider count is 4", text)
        self.assertIn("fixtures/providers/sensor-evidence-provider-manifest-v1.json", text)
        self.assertIn("docs/sensor-evidence-extension-template.md", text)
        self.assertIn("docs/phase-10-checkpoint.md", text)
        self.assertIn("Phase 10D operationalizes `document-fixture`", text)
        self.assertIn("Phase 10E introduces `somatic.evidence.framework`", text)
        self.assertIn("Phase 10F adds `somatic.evidence.document_adapter`", text)
        self.assertIn("Phase 10G adds `somatic.sensors.csi_adapter`", text)
        self.assertIn("Phase 10H adds `somatic.safety.adapter_readiness`", text)
        self.assertIn("Phase 10I adds shared invariant coverage", text)
        self.assertIn("Phase 10J adds `docs/phase-10-checkpoint.md`", text)
        self.assertIn("Phase 11A adds `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11a-real-mode-contract-specs.md", text)
        self.assertIn("Phase 11B extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11b-review-record-fixtures.md", text)
        self.assertIn("Phase 11C extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11c-preflight-dossiers.md", text)
        self.assertIn("Phase 11D extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11d-dossier-lifecycle.md", text)
        self.assertIn("Phase 11E extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11e-audit-index-change-control.md", text)
        self.assertIn("Phase 11F extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11f-audit-handoff-reporting.md", text)
        self.assertIn("Phase 11G extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11g-handoff-acceptance.md", text)
        self.assertIn("Phase 11H extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11h-followup-remediation.md", text)
        self.assertIn("Phase 11I extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11i-followup-queue-index.md", text)
        self.assertIn("Phase 11J extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11j-decision-closeout.md", text)
        self.assertIn("Phase 11K extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11k-review-trail-export.md", text)
        self.assertIn("Phase 11L extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11l-runtime-authorization-gap-ledger.md", text)
        self.assertIn("Phase 11M extends `somatic.safety.phase11_contracts`", text)
        self.assertIn("docs/phase-11m-planning-governance-closeout.md", text)
        for provider in summary["providers"]:
            with self.subTest(provider=provider["provider_id"]):
                self.assertIn(provider["provider_id"], text)
                self.assertIn(provider["artifact_name"], text)
                self.assertIn(provider["run_relative_artifact"], text)
        document_provider = next(
            provider
            for provider in summary["providers"]
            if provider["provider_id"] == "document-fixture"
        )
        self.assertEqual(document_provider["evidence_kind"], "document-evidence-pack")
        self.assertEqual(document_provider["artifact_name"], "document_evidence_pack")
        self.assertEqual(
            document_provider["run_relative_artifact"],
            "artifacts/document_evidence_pack.json",
        )
        document_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["provider_id"] == "document-fixture"
        )
        self.assertEqual(document_surface["surface"], "artifact-inspection-cli")
        self.assertEqual(document_surface["evidence_kind"], "document-evidence-pack")
        self.assertEqual(document_surface["artifact_name"], "document_evidence_pack")
        self.assertTrue(document_surface["reports_compatibility"])
        self.assertTrue(document_surface["reports_readiness"])
        self.assertTrue(document_surface["reports_counts"])
        framework_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "cross-domain-evidence-framework"
        )
        self.assertEqual(framework_surface["module"], "somatic.evidence.framework")
        self.assertIn("wifi-csi", framework_surface["domains"])
        self.assertIn("document-fixture", framework_surface["domains"])
        self.assertTrue(framework_surface["shares_compatibility_validation"])
        self.assertTrue(framework_surface["domain_contracts_preserved"])
        csi_adapter_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "csi-source-adapter-boundary"
        )
        self.assertEqual(csi_adapter_surface["provider_id"], "wifi-csi")
        self.assertEqual(csi_adapter_surface["module"], "somatic.sensors.csi_adapter")
        self.assertEqual(
            csi_adapter_surface["adapter_kind"],
            "metadata-wifi-csi-source-adapter",
        )
        self.assertEqual(csi_adapter_surface["adapter_contract_version"], 1)
        self.assertEqual(
            csi_adapter_surface["ruview_reference_status"],
            "conditional-reference-only",
        )
        self.assertEqual(
            csi_adapter_surface["booth_profile"],
            "booth-first-single-subject-v1",
        )
        self.assertIn("reference-only", csi_adapter_surface["capability_labels"])
        self.assertIn("no-router-ap-control", csi_adapter_surface["capability_labels"])
        self.assertIn("no-mqtt-udp-listener", csi_adapter_surface["capability_labels"])
        self.assertIn("no-model-execution", csi_adapter_surface["capability_labels"])
        self.assertEqual(
            csi_adapter_surface["readiness_gate_status"],
            "blocked-fixture-reference-only",
        )
        self.assertEqual(csi_adapter_surface["readiness_gate_missing_count"], 7)
        self.assertFalse(csi_adapter_surface["real_mode_execution_permitted"])
        self.assertTrue(csi_adapter_surface["validates_before_planning_metadata"])
        self.assertTrue(csi_adapter_surface["rejects_unsafe_outputs"])
        adapter_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "document-adapter-boundary"
        )
        self.assertEqual(adapter_surface["module"], "somatic.evidence.document_adapter")
        self.assertEqual(adapter_surface["adapter_kind"], "metadata-document-adapter")
        self.assertEqual(adapter_surface["adapter_contract_version"], 1)
        self.assertIn("no-network", adapter_surface["capability_labels"])
        self.assertIn("no-source-id-export", adapter_surface["capability_labels"])
        self.assertEqual(
            adapter_surface["readiness_gate_status"],
            "blocked-fixture-reference-only",
        )
        self.assertEqual(adapter_surface["readiness_gate_missing_count"], 7)
        self.assertFalse(adapter_surface["real_mode_execution_permitted"])
        self.assertTrue(adapter_surface["validates_before_pack"])
        self.assertTrue(adapter_surface["rejects_unsafe_outputs"])
        real_mode_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "real-mode-readiness-gate"
        )
        self.assertEqual(real_mode_surface["module"], "somatic.safety.adapter_readiness")
        self.assertEqual(real_mode_surface["gate_contract_version"], 1)
        self.assertEqual(real_mode_surface["default_status"], "blocked-fixture-reference-only")
        self.assertEqual(len(real_mode_surface["required_gates"]), 7)
        self.assertIn("wifi-csi", real_mode_surface["applied_providers"])
        self.assertIn("document-fixture", real_mode_surface["applied_providers"])
        self.assertFalse(real_mode_surface["real_mode_execution_permitted"])
        invariant_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "shared-safety-invariant-audit"
        )
        self.assertEqual(
            invariant_surface["module"],
            "tests.test_phase10i_shared_safety_invariants",
        )
        self.assertIn("wifi-csi", invariant_surface["domains"])
        self.assertIn("document-fixture", invariant_surface["domains"])
        self.assertTrue(invariant_surface["checks_provider_manifest"])
        self.assertTrue(invariant_surface["checks_doctor"])
        self.assertTrue(invariant_surface["checks_workflow_reports"])
        self.assertTrue(invariant_surface["checks_artifact_inspect"])
        self.assertTrue(invariant_surface["checks_release_summary_fixture"])
        self.assertFalse(invariant_surface["runtime_behavior_changed"])
        checkpoint_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "phase-10-checkpoint"
        )
        self.assertEqual(checkpoint_surface["document"], "docs/phase-10-checkpoint.md")
        self.assertEqual(checkpoint_surface["phase_range"], "10A-10J")
        self.assertTrue(checkpoint_surface["summarizes_current_state_matrix"])
        self.assertTrue(checkpoint_surface["documents_intentional_blocks"])
        self.assertTrue(checkpoint_surface["documents_next_safe_lanes"])
        self.assertFalse(checkpoint_surface["runtime_behavior_changed"])
        phase11_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11a-real-mode-contract-specs"
        )
        self.assertEqual(phase11_surface["module"], "somatic.safety.phase11_contracts")
        self.assertIn("document-ingestion", phase11_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11_surface["domains"])
        self.assertIn("metadata-only-staging", phase11_surface["document_contracts"])
        self.assertIn("license-source-review", phase11_surface["document_contracts"])
        self.assertIn("booth-topology-metadata", phase11_surface["rf_booth_contracts"])
        self.assertIn("network-policy", phase11_surface["rf_booth_contracts"])
        self.assertEqual(phase11_surface["default_status"], "planning-only-runtime-disabled")
        self.assertEqual(phase11_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11_surface["planning_only"])
        self.assertFalse(phase11_surface["runtime_behavior_changed"])
        phase11b_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11b-review-record-fixtures"
        )
        self.assertEqual(phase11b_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11b_surface["document"],
            "docs/phase-11b-review-record-fixtures.md",
        )
        self.assertEqual(
            phase11b_surface["fixture_label"],
            "p11b-review-record-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11b_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11b_surface["domains"])
        self.assertEqual(phase11b_surface["review_record_contract_version"], 1)
        self.assertEqual(phase11b_surface["default_status"], "missing-required-reviews")
        self.assertEqual(phase11b_surface["complete_status"], "reviewed-runtime-disabled")
        self.assertEqual(phase11b_surface["rejected_status"], "rejected-fail-closed")
        self.assertEqual(phase11b_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11b_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11b_surface["planning_only"])
        self.assertFalse(phase11b_surface["runtime_behavior_changed"])
        phase11c_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11c-preflight-dossiers"
        )
        self.assertEqual(phase11c_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11c_surface["document"],
            "docs/phase-11c-preflight-dossiers.md",
        )
        self.assertEqual(
            phase11c_surface["fixture_label"],
            "p11c-preflight-dossier-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11c_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11c_surface["domains"])
        self.assertEqual(phase11c_surface["preflight_packet_contract_version"], 1)
        self.assertEqual(phase11c_surface["default_status"], "missing-required-records")
        self.assertEqual(phase11c_surface["complete_status"], "reviewed-runtime-disabled")
        self.assertEqual(phase11c_surface["rejected_status"], "rejected-fail-closed")
        self.assertEqual(
            phase11c_surface["fingerprint_scope"],
            "included-sanitized-records",
        )
        self.assertEqual(phase11c_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11c_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11c_surface["planning_only"])
        self.assertFalse(phase11c_surface["runtime_behavior_changed"])
        phase11d_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11d-lifecycle-audit-records"
        )
        self.assertEqual(phase11d_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11d_surface["document"],
            "docs/phase-11d-dossier-lifecycle.md",
        )
        self.assertEqual(
            phase11d_surface["fixture_label"],
            "p11d-lifecycle-audit-record-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11d_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11d_surface["domains"])
        self.assertEqual(phase11d_surface["lifecycle_audit_contract_version"], 1)
        self.assertEqual(phase11d_surface["default_stage"], "created")
        self.assertEqual(phase11d_surface["default_decision"], "needs-more-review")
        self.assertEqual(phase11d_surface["reviewed_stage"], "reviewed")
        self.assertEqual(
            phase11d_surface["all_gates_reviewed_decision"],
            "all-gates-reviewed-runtime-disabled",
        )
        self.assertEqual(phase11d_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11d_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11d_surface["planning_only"])
        self.assertFalse(phase11d_surface["runtime_behavior_changed"])
        phase11e_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11e-audit-index-change-control"
        )
        self.assertEqual(phase11e_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11e_surface["document"],
            "docs/phase-11e-audit-index-change-control.md",
        )
        self.assertEqual(
            phase11e_surface["fixture_label"],
            "p11e-audit-index-change-control-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11e_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11e_surface["domains"])
        self.assertEqual(phase11e_surface["audit_index_contract_version"], 1)
        self.assertEqual(
            phase11e_surface["default_status"],
            "audit-index-runtime-disabled",
        )
        self.assertEqual(
            phase11e_surface["deterministic_ordering"],
            "sanitized-label-hash-v1",
        )
        self.assertEqual(phase11e_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11e_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11e_surface["planning_only"])
        self.assertFalse(phase11e_surface["runtime_behavior_changed"])
        phase11f_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11f-audit-handoff-reporting"
        )
        self.assertEqual(phase11f_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11f_surface["document"],
            "docs/phase-11f-audit-handoff-reporting.md",
        )
        self.assertEqual(
            phase11f_surface["fixture_label"],
            "p11f-audit-handoff-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11f_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11f_surface["domains"])
        self.assertEqual(phase11f_surface["audit_handoff_contract_version"], 1)
        self.assertEqual(
            phase11f_surface["default_status"],
            "audit-handoff-runtime-disabled",
        )
        self.assertEqual(phase11f_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11f_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11f_surface["planning_only"])
        self.assertFalse(phase11f_surface["runtime_behavior_changed"])
        phase11g_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11g-handoff-acceptance"
        )
        self.assertEqual(phase11g_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11g_surface["document"],
            "docs/phase-11g-handoff-acceptance.md",
        )
        self.assertEqual(
            phase11g_surface["fixture_label"],
            "p11g-handoff-acceptance-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11g_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11g_surface["domains"])
        self.assertEqual(phase11g_surface["handoff_acceptance_contract_version"], 1)
        self.assertEqual(
            phase11g_surface["default_status"],
            "rejected-fail-closed",
        )
        self.assertEqual(
            phase11g_surface["accepted_status"],
            "accepted-for-planning-runtime-disabled",
        )
        self.assertEqual(
            phase11g_surface["blocked_status"],
            "blocked-runtime-disabled",
        )
        self.assertEqual(phase11g_surface["stale_status"], "stale-runtime-disabled")
        self.assertEqual(
            phase11g_surface["rejected_status"],
            "rejected-fail-closed",
        )
        self.assertEqual(
            phase11g_surface["included_handoff"],
            "label-and-fingerprint-only",
        )
        self.assertEqual(phase11g_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11g_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11g_surface["planning_only"])
        self.assertFalse(phase11g_surface["runtime_behavior_changed"])
        phase11h_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11h-followup-remediation"
        )
        self.assertEqual(phase11h_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11h_surface["document"],
            "docs/phase-11h-followup-remediation.md",
        )
        self.assertEqual(
            phase11h_surface["fixture_label"],
            "p11h-followup-remediation-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11h_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11h_surface["domains"])
        self.assertEqual(phase11h_surface["acceptance_followup_contract_version"], 1)
        self.assertEqual(
            phase11h_surface["followup_statuses"],
            [
                "open",
                "blocked",
                "resolved-for-planning",
                "rejected",
                "archived",
            ],
        )
        self.assertEqual(
            phase11h_surface["followup_types"],
            [
                "stale-renewal",
                "blocker-disposition",
                "reviewer-queue",
                "needs-more-review",
                "archived-no-action",
            ],
        )
        self.assertEqual(
            phase11h_surface["included_acceptance"],
            "label-and-hash-only",
        )
        self.assertEqual(
            phase11h_surface["stale_renewal_summary"],
            "summary-label-only",
        )
        self.assertEqual(
            phase11h_surface["blocker_disposition_summary"],
            "summary-label-only",
        )
        self.assertEqual(
            phase11h_surface["reviewer_queue_summary"],
            "summary-label-only",
        )
        self.assertEqual(phase11h_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11h_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11h_surface["planning_only"])
        self.assertFalse(phase11h_surface["runtime_behavior_changed"])
        phase11i_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11i-followup-queue-index"
        )
        self.assertEqual(phase11i_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11i_surface["document"],
            "docs/phase-11i-followup-queue-index.md",
        )
        self.assertEqual(
            phase11i_surface["fixture_label"],
            "p11i-followup-queue-index-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11i_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11i_surface["domains"])
        self.assertEqual(phase11i_surface["queue_index_contract_version"], 1)
        self.assertEqual(
            phase11i_surface["queue_index_kind"],
            "phase-11i-followup-queue-index",
        )
        self.assertEqual(
            phase11i_surface["queue_acceptance_kind"],
            "phase-11i-queue-acceptance-check",
        )
        self.assertEqual(
            phase11i_surface["queue_acceptance_statuses"],
            [
                "accepted-for-planning-queue",
                "blocked-queue",
                "stale-queue",
                "rejected-queue",
                "archived-no-action",
                "needs-more-review",
            ],
        )
        self.assertEqual(
            phase11i_surface["included_followups"],
            "label-and-hash-only",
        )
        self.assertEqual(
            phase11i_surface["queue_status_counts"],
            "summary-counts-only",
        )
        self.assertEqual(
            phase11i_surface["blocker_disposition_counts"],
            "summary-counts-only",
        )
        self.assertEqual(
            phase11i_surface["reviewer_queue_counts"],
            "summary-counts-only",
        )
        self.assertEqual(
            phase11i_surface["stale_renewal_counts"],
            "summary-counts-only",
        )
        self.assertEqual(phase11i_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11i_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11i_surface["planning_only"])
        self.assertFalse(phase11i_surface["runtime_behavior_changed"])
        phase11j_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11j-decision-closeout"
        )
        self.assertEqual(phase11j_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11j_surface["document"],
            "docs/phase-11j-decision-closeout.md",
        )
        self.assertEqual(
            phase11j_surface["fixture_label"],
            "p11j-decision-closeout-bundle-v1",
        )
        self.assertIn("document-ingestion", phase11j_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11j_surface["domains"])
        self.assertEqual(phase11j_surface["closeout_contract_version"], 1)
        self.assertEqual(
            phase11j_surface["closeout_decisions"],
            [
                "closed-for-planning",
                "deferred",
                "rejected",
                "archived",
                "needs-new-review",
                "blocked",
            ],
        )
        self.assertEqual(
            phase11j_surface["closeout_statuses"],
            ["complete", "incomplete", "blocked", "rejected", "archived"],
        )
        self.assertEqual(phase11j_surface["included_queue"], "label-and-hash-only")
        self.assertEqual(
            phase11j_surface["reviewer_disposition_summary"],
            "summary-label-only",
        )
        self.assertEqual(phase11j_surface["closeout_counts"], "summary-counts-only")
        self.assertEqual(phase11j_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11j_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11j_surface["planning_only"])
        self.assertFalse(phase11j_surface["runtime_behavior_changed"])
        phase11k_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11k-review-trail-export"
        )
        self.assertEqual(phase11k_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11k_surface["document"],
            "docs/phase-11k-review-trail-export.md",
        )
        self.assertEqual(
            phase11k_surface["fixture_label"],
            "p11k-review-trail-export-v1",
        )
        self.assertEqual(phase11k_surface["phase_range"], "11A-11J")
        self.assertEqual(phase11k_surface["covered_phase_count"], 10)
        self.assertIn("document-ingestion", phase11k_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11k_surface["domains"])
        self.assertEqual(phase11k_surface["review_trail_export_contract_version"], 1)
        self.assertEqual(
            phase11k_surface["readiness_gap_summary"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(phase11k_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11k_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11k_surface["planning_only"])
        self.assertFalse(phase11k_surface["runtime_behavior_changed"])
        phase11l_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11l-runtime-gap-ledger"
        )
        self.assertEqual(phase11l_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11l_surface["document"],
            "docs/phase-11l-runtime-authorization-gap-ledger.md",
        )
        self.assertEqual(
            phase11l_surface["fixture_label"],
            "p11l-runtime-authorization-gap-ledger-v1",
        )
        self.assertEqual(phase11l_surface["phase_range"], "11A-11K")
        self.assertEqual(phase11l_surface["covered_phase_count"], 11)
        self.assertIn("document-ingestion", phase11l_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11l_surface["domains"])
        self.assertEqual(
            phase11l_surface["runtime_authorization_gap_ledger_contract_version"],
            1,
        )
        self.assertEqual(phase11l_surface["authorization_status"], "not-authorized")
        self.assertEqual(
            phase11l_surface["readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(phase11l_surface["missing_future_gate_count"], 9)
        self.assertFalse(phase11l_surface["execution_grants"])
        self.assertEqual(phase11l_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11l_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11l_surface["planning_only"])
        self.assertFalse(phase11l_surface["runtime_behavior_changed"])
        phase11m_surface = next(
            surface
            for surface in summary["operational_surfaces"]
            if surface["surface"] == "p11m-planning-governance-closeout"
        )
        self.assertEqual(phase11m_surface["module"], "somatic.safety.phase11_contracts")
        self.assertEqual(
            phase11m_surface["document"],
            "docs/phase-11m-planning-governance-closeout.md",
        )
        self.assertEqual(
            phase11m_surface["fixture_label"],
            "p11m-planning-governance-closeout-index-v1",
        )
        self.assertEqual(phase11m_surface["phase_range"], "11A-11L")
        self.assertEqual(phase11m_surface["covered_phase_count"], 12)
        self.assertIn("document-ingestion", phase11m_surface["domains"])
        self.assertIn("wifi-csi-rf-booth", phase11m_surface["domains"])
        self.assertEqual(
            phase11m_surface["planning_governance_closeout_contract_version"],
            1,
        )
        self.assertEqual(
            phase11m_surface["final_status"],
            "phase-11-planning-governance-complete",
        )
        self.assertEqual(
            phase11m_surface["runtime_authorization_status"],
            "not-authorized",
        )
        self.assertEqual(
            phase11m_surface["readiness_gap"],
            "real-mode-authorization-missing",
        )
        self.assertEqual(
            phase11m_surface["next_phase_requirement"],
            "explicit-future-phase-required-before-runtime-work",
        )
        self.assertFalse(phase11m_surface["execution_grants"])
        self.assertEqual(phase11m_surface["runtime_stage"], "not-implemented")
        self.assertFalse(phase11m_surface["real_mode_execution_permitted"])
        self.assertTrue(phase11m_surface["planning_only"])
        self.assertFalse(phase11m_surface["runtime_behavior_changed"])

    def test_phase_10_checkpoint_documents_current_baseline(self):
        text = CHECKPOINT_DOC.read_text(encoding="utf-8")

        for phase in (
            "10A",
            "10B",
            "10C",
            "10D",
            "10E",
            "10F",
            "10G",
            "10H",
            "10I",
            "10J",
        ):
            with self.subTest(phase=phase):
                self.assertIn(f"| {phase} |", text)
        for domain in (
            "Generic sensor evidence",
            "WiFi CSI evidence",
            "Document evidence",
            "Document adapter",
            "WiFi CSI source adapter",
            "Real-mode readiness gate",
        ):
            with self.subTest(domain=domain):
                self.assertIn(domain, text)
        for implemented in (
            "Metadata-only evidence packs",
            "Sanitized artifacts",
            "Provider registry",
            "CLI inspect",
            "CLI doctor",
            "adapter readiness status",
        ):
            with self.subTest(implemented=implemented):
                self.assertIn(implemented, text)
        for blocked in (
            "Real document ingestion",
            "file crawling",
            "PDF parsing",
            "RuView execution",
            "model download",
            "model execution",
            "WiFi CSI hardware access",
            "ESP32 flashing",
            "packet capture",
            "monitor mode",
            "MQTT/UDP",
            "router/AP control",
            "smart-home bridges",
            "Medical inference",
        ):
            with self.subTest(blocked=blocked):
                self.assertIn(blocked, text)
        for gate in (
            "consent",
            "license review",
            "privacy review",
            "hardware review",
            "model artifact review",
            "dependency review",
            "network policy review",
        ):
            with self.subTest(gate=gate):
                self.assertIn(gate, text)
        self.assertIn("Phase 11A should stay contract-spec-only", text)
        self.assertIn("future RF booth hardware specs", text)
        self._assert_checkpoint_doc_is_sanitized(text)

    def test_documented_public_commands_are_covered_by_docs_and_tests(self):
        summary = self._read_summary()
        summary_text = SUMMARY_DOC.read_text(encoding="utf-8")
        cli_doc_text = CLI_DOC.read_text(encoding="utf-8")
        cli_test_text = CLI_TESTS.read_text(encoding="utf-8")

        for command in summary["public_commands"]:
            with self.subTest(command=command):
                self.assertIn(command, summary_text)

        for token in ("csi-parse", "sensor-evidence", "providers", "validate", "inspect"):
            with self.subTest(token=token):
                self.assertIn(token, cli_doc_text)
                self.assertIn(token, cli_test_text)

    def test_release_summary_privacy_boundary_is_sanitized(self):
        combined = "\n".join(
            (
                SUMMARY_DOC.read_text(encoding="utf-8"),
                json.dumps(self._read_summary(), sort_keys=True),
            )
        ).lower()

        for forbidden in (
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "sample-csi-jsonl",
            "mixed-valid-invalid-csi",
            "unsupported-csi",
            "environment-parsed.csv",
            "environment-mixed.csv",
            "toy-counter-parsed.csv",
            "toy-counter-mixed.csv",
            "fixture://",
            "source_id",
            "source_ids",
            "provider_payload",
            "provider_payload_body",
            "parser_report_body",
            "parser_summary_body",
            "api_key",
            "access_token",
            "secret_value",
            "raw_values",
            "raw_csi",
            "raw_rf",
            "raw_signal",
            "signal_values",
            "amplitude",
            "rssi",
            "diagnosis",
            "treatment",
            "medical",
            "health",
            "heart-rate",
            "respiration",
            "fall detection",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)
        self.assertGreaterEqual(
            combined.count("real-mode-authorization-missing"),
            1,
        )
        self.assertLessEqual(combined.count("real-mode-authorization-missing"), 12)
        self.assertNotRegex(combined.replace("\\", "/"), r"[a-z]:/")

    def test_run_relative_artifact_paths_are_artifact_only(self):
        summary = self._read_summary()
        for provider in summary["providers"]:
            artifact = provider["run_relative_artifact"]
            with self.subTest(artifact=artifact):
                self.assertTrue(artifact.startswith("artifacts/"))
                self.assertTrue(artifact.endswith(".json"))
                self.assertIsNone(re.match(r"^[A-Za-z]:", artifact))
                self.assertNotIn("..", Path(artifact).parts)

    @staticmethod
    def _read_summary():
        return json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    def _assert_checkpoint_doc_is_sanitized(self, text):
        lowered = text.lower().replace("\\", "/")
        self.assertNotIn("://", lowered)
        self.assertNotRegex(lowered, r"[a-z]:/")
        for forbidden in (
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "sample-csi-jsonl",
            "mixed-valid-invalid-csi",
            "unsupported-csi",
            "document-fixture-pack.json",
            "environment-parsed.csv",
            "toy-counter-parsed.csv",
            "fixture://",
            "source_id",
            "source_ids",
            "provider_payload",
            "parser_report_body",
            "parser_summary_body",
            "api_key",
            "access_token",
            "secret_value",
            "authorization",
            "raw_values",
            "raw_csi",
            "raw_rf",
            "raw_signal",
            "signal_values",
        ):
            with self.subTest(checkpoint_forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
