"""Phase 11A real-mode contract/spec planning surfaces.

These helpers describe the contracts a future real adapter must satisfy before
runtime work can be considered. They do not enable ingestion, capture, model
execution, networking, or any live adapter behavior.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256

from somatic.safety._builder_cache import install_builder_cache
from somatic.safety.adapter_readiness import (
    REAL_MODE_GATE_BLOCKED_STATUS,
    REAL_MODE_PHASE_RUNTIME,
    REAL_MODE_REQUIRED_GATES,
    evaluate_real_mode_readiness,
    real_mode_readiness_gate_summary,
)

PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION = 1
PHASE11_REAL_MODE_CONTRACT_SPEC_KIND = "phase-11-real-mode-contract-spec"
PHASE11_REAL_MODE_CONTRACT_PHASE = "11A"
PHASE11_REAL_MODE_CONTRACT_STATUS = "planning-only-runtime-disabled"
PHASE11_DOCUMENT_DOMAIN = "document-ingestion"
PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN = "wifi-csi-rf-booth"
PHASE11_REVIEW_RECORD_CONTRACT_VERSION = 1
PHASE11_REVIEW_RECORD_KIND = "phase-11-real-mode-review-record"
PHASE11_REVIEW_RECORD_FIXTURE_KIND = "phase-11b-review-record-fixtures"
PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE = "missing-required-reviews"
PHASE11_REVIEW_RECORD_STATUS_REVIEWED = "reviewed-runtime-disabled"
PHASE11_REVIEW_RECORD_STATUS_REJECTED = "rejected-fail-closed"
PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION = 1
PHASE11_PREFLIGHT_DOSSIER_KIND = "phase-11c-real-mode-preflight-dossier"
PHASE11_PREFLIGHT_DOSSIER_FIXTURE_KIND = "phase-11c-preflight-dossiers"
PHASE11_PREFLIGHT_STATUS_MISSING = "missing-required-records"
PHASE11_PREFLIGHT_STATUS_REVIEWED = "reviewed-runtime-disabled"
PHASE11_PREFLIGHT_STATUS_REJECTED = "rejected-fail-closed"
PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION = 1
PHASE11_DOSSIER_LIFECYCLE_KIND = "phase-11d-dossier-lifecycle-audit-record"
PHASE11_DOSSIER_LIFECYCLE_FIXTURE_KIND = "phase-11d-dossier-lifecycle-records"
PHASE11_REVIEWER_SIGNOFF_KIND = "phase-11d-reviewer-signoff-metadata"
PHASE11_DOSSIER_DECISION_KIND = "phase-11d-dossier-decision-record"
PHASE11_DOSSIER_COMPARISON_KIND = "phase-11d-dossier-comparison"
PHASE11_AUDIT_INDEX_CONTRACT_VERSION = 1
PHASE11_AUDIT_INDEX_KIND = "phase-11e-dossier-audit-index"
PHASE11_AUDIT_INDEX_FIXTURE_KIND = "phase-11e-audit-index-change-control"
PHASE11_CHANGE_CONTROL_KIND = "phase-11e-change-control-record"
PHASE11_SUPERSESSION_CHAIN_KIND = "phase-11e-supersession-chain"
PHASE11_REVIEWER_SCOPE_COVERAGE_KIND = "phase-11e-reviewer-scope-coverage"
PHASE11_EXPORT_RETENTION_POLICY_KIND = "phase-11e-export-retention-policy"
PHASE11_AUDIT_INDEX_STATUS = "audit-index-runtime-disabled"
PHASE11_AUDIT_INDEX_REJECTED_STATUS = "rejected-fail-closed"
PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION = 1
PHASE11_AUDIT_HANDOFF_KIND = "phase-11f-compact-audit-handoff"
PHASE11_AUDIT_HANDOFF_FIXTURE_KIND = "phase-11f-audit-handoff-reporting"
PHASE11_AUDIT_HANDOFF_STATUS = "audit-handoff-runtime-disabled"
PHASE11_AUDIT_HANDOFF_REJECTED_STATUS = "rejected-fail-closed"
PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION = 1
PHASE11_HANDOFF_ACCEPTANCE_KIND = "phase-11g-handoff-acceptance-check"
PHASE11_HANDOFF_ACCEPTANCE_FIXTURE_KIND = "phase-11g-handoff-acceptance"
PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS = "accepted-for-planning-runtime-disabled"
PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS = "blocked-runtime-disabled"
PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS = "stale-runtime-disabled"
PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS = "rejected-fail-closed"
PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION = 1
PHASE11_ACCEPTANCE_FOLLOWUP_KIND = "phase-11h-acceptance-followup-remediation"
PHASE11_ACCEPTANCE_FOLLOWUP_FIXTURE_KIND = "phase-11h-followup-remediation"
PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS = "open"
PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS = "blocked"
PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS = "resolved-for-planning"
PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS = "rejected"
PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS = "archived"
PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE = "stale-renewal"
PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE = "blocker-disposition"
PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE = "reviewer-queue"
PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE = "needs-more-review"
PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE = "archived-no-action"
PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION = 1
PHASE11_FOLLOWUP_QUEUE_INDEX_KIND = "phase-11i-followup-queue-index"
PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_KIND = "phase-11i-queue-acceptance-check"
PHASE11_FOLLOWUP_QUEUE_FIXTURE_KIND = "phase-11i-followup-queue-index"
PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS = "accepted-for-planning-queue"
PHASE11_FOLLOWUP_QUEUE_BLOCKED_STATUS = "blocked-queue"
PHASE11_FOLLOWUP_QUEUE_STALE_STATUS = "stale-queue"
PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS = "rejected-queue"
PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS = "archived-no-action"
PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS = "needs-more-review"
PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION = 1
PHASE11_DECISION_CLOSEOUT_FIXTURE_KIND = "phase-11j-decision-closeout"
PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION = "closed-for-planning"
PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION = "deferred"
PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION = "rejected"
PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION = "archived"
PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION = "needs-new-review"
PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION = "blocked"
PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS = "complete"
PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS = "incomplete"
PHASE11_DECISION_CLOSEOUT_BLOCKED_STATUS = "blocked"
PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS = "rejected"
PHASE11_DECISION_CLOSEOUT_ARCHIVED_STATUS = "archived"
PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION = 1
PHASE11_REVIEW_TRAIL_EXPORT_FIXTURE_KIND = "phase-11k-review-trail-export"
PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE = "11A-11J"
PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT = 10
PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP = "real-mode-authorization-missing"
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION = 1
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_FIXTURE_KIND = "phase-11l-runtime-authorization-gap-ledger"
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE = "11A-11K"
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT = 11
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS = "not-authorized"
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES = (
    "explicit-runtime-decision-record",
    "consent-review",
    "privacy-review",
    "license-source-review",
    "hardware-review",
    "model-artifact-review",
    "dependency-review",
    "network-policy-review",
    "operator-safety-review",
)
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION = 1
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_FIXTURE_KIND = "phase-11m-planning-governance-closeout-index"
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE = "11A-11L"
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT = 12
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS = "phase-11-planning-governance-complete"
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_NEXT_PHASE_REQUIREMENT = (
    "explicit-future-phase-required-before-runtime-work"
)
PHASE11_CHANGE_CONTROL_REASON = "planning-change-control"
PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY = "local-metadata-only"
PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY = "audit-metadata-only"
PHASE11_LIFECYCLE_STAGE_CREATED = "created"
PHASE11_LIFECYCLE_STAGE_REVIEWED = "reviewed"
PHASE11_LIFECYCLE_STAGE_SUPERSEDED = "superseded"
PHASE11_LIFECYCLE_STAGE_REJECTED = "rejected"
PHASE11_LIFECYCLE_STAGE_ARCHIVED = "archived"
PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED = "decision-recorded"
PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS = "no-blockers"
PHASE11_SIGNOFF_VERDICT_BLOCKERS = "blockers"
PHASE11_SIGNOFF_VERDICT_REJECTED = "rejected"
PHASE11_SIGNOFF_VERDICT_SUPERSEDED = "superseded"
PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING = "safe-for-planning"
PHASE11_LIFECYCLE_DECISION_BLOCKED = "blocked"
PHASE11_LIFECYCLE_DECISION_REJECTED = "rejected"
PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW = "needs-more-review"
PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED = (
    "all-gates-reviewed-runtime-disabled"
)
PHASE11_DOCUMENT_REQUIRED_CONTRACTS = (
    "metadata-only-staging",
    "parser-boundary",
    "artifact-privacy",
    "license-source-review",
)
PHASE11_RF_BOOTH_REQUIRED_CONTRACTS = (
    "booth-topology-metadata",
    "consent-privacy",
    "hardware-review",
    "model-artifact-review",
    "network-policy",
)
PHASE11_CONTRACT_STATUS_LABELS = (
    "p11a-contract-spec-only",
    "real-mode-planning-only",
    "no-runtime-enable",
)
PHASE11_REVIEW_RECORD_STATUS_LABELS = (
    "p11b-review-record-fixture",
    "review-evidence-only",
    "runtime-disabled-after-review",
)
PHASE11_PREFLIGHT_STATUS_LABELS = (
    "p11c-preflight-dossier",
    "preflight-evidence-only",
    "runtime-disabled-after-preflight",
)
PHASE11_LIFECYCLE_STATUS_LABELS = (
    "p11d-lifecycle-audit-record",
    "audit-evidence-only",
    "runtime-disabled-after-audit",
)
PHASE11_AUDIT_INDEX_STATUS_LABELS = (
    "p11e-audit-index",
    "change-control-only",
    "runtime-disabled-after-index",
)
PHASE11_AUDIT_HANDOFF_STATUS_LABELS = (
    "p11f-audit-handoff",
    "reporting-only",
    "runtime-disabled-after-handoff",
)
PHASE11_HANDOFF_ACCEPTANCE_STATUS_LABELS = (
    "p11g-handoff-acceptance",
    "accepted-for-planning-only",
    "runtime-disabled-after-acceptance",
)
PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_LABELS = (
    "p11h-followup-remediation",
    "planning-queue-only",
    "runtime-disabled-after-followup",
)
PHASE11_FOLLOWUP_QUEUE_STATUS_LABELS = (
    "p11i-followup-queue-index",
    "reviewer-navigation-only",
    "runtime-disabled-after-queue-index",
)
PHASE11_DECISION_CLOSEOUT_STATUS_LABELS = (
    "p11j-decision-closeout",
    "planning-decision-metadata-only",
    "runtime-disabled-after-closeout",
)
PHASE11_REVIEW_TRAIL_EXPORT_STATUS_LABELS = (
    "p11k-review-trail-export",
    "review-trail-navigation-only",
    "runtime-disabled-after-review-trail-export",
)
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS_LABELS = (
    "p11l-runtime-gap-ledger",
    "reviewer-navigation-only",
    "runtime-disabled-after-gap-ledger",
)
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS_LABELS = (
    "p11m-governance-closeout",
    "runtime-disabled-after-governance-closeout",
)
PHASE11_REVIEW_RECORD_SPECS = (
    (
        "consent",
        "consent",
        "consent-review",
        "consent-boundary-metadata",
    ),
    (
        "license_review",
        "license-review",
        "license-source-review",
        "license-source-boundary-metadata",
    ),
    (
        "privacy_review",
        "privacy-review",
        "privacy-review",
        "privacy-boundary-metadata",
    ),
    (
        "hardware_review",
        "hardware-review",
        "hardware-review",
        "hardware-boundary-metadata",
    ),
    (
        "model_artifact_review",
        "model-artifact-review",
        "model-artifact-review",
        "model-artifact-boundary-metadata",
    ),
    (
        "dependency_review",
        "dependency-review",
        "dependency-review",
        "dependency-boundary-metadata",
    ),
    (
        "network_policy_review",
        "network-policy-review",
        "network-policy-review",
        "network-policy-boundary-metadata",
    ),
)
PHASE11_REVIEW_RECORD_FIELDS_BY_GATE = {
    gate: field for field, gate, _review_type, _scope in PHASE11_REVIEW_RECORD_SPECS
}
PHASE11_REVIEW_RECORD_GATES_BY_FIELD = {
    field: gate for field, gate, _review_type, _scope in PHASE11_REVIEW_RECORD_SPECS
}
PHASE11_REVIEW_RECORD_STATUS_VALUES = (
    PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
    PHASE11_REVIEW_RECORD_STATUS_REVIEWED,
    PHASE11_REVIEW_RECORD_STATUS_REJECTED,
)
PHASE11_REVIEW_ENTRY_STATUS_VALUES = ("not-reviewed", "reviewed", "rejected")
PHASE11_REVIEW_RECORD_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "review_record_contract_version",
        "review_record_kind",
        "domain",
        "record_status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "required_gates",
        "reviewed_gates",
        "missing_gates",
        "rejected_gates",
        "reviewed_gate_count",
        "missing_gate_count",
        "rejected_gate_count",
        "reviews",
    }
)
PHASE11_REVIEW_RECORD_ALLOWED_FIELDS = PHASE11_REVIEW_RECORD_REQUIRED_FIELDS
PHASE11_REVIEW_ENTRY_REQUIRED_FIELDS = frozenset(
    {
        "gate_id",
        "review_type",
        "status",
        "required",
        "safe_to_proceed",
        "runtime_permission",
        "metadata_only",
        "sanitized",
        "review_scope",
    }
)
PHASE11_REVIEW_ENTRY_ALLOWED_FIELDS = PHASE11_REVIEW_ENTRY_REQUIRED_FIELDS
PHASE11_REVIEW_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "records",
    }
)
PHASE11_PREFLIGHT_DOSSIER_STATUS_VALUES = (
    PHASE11_PREFLIGHT_STATUS_MISSING,
    PHASE11_PREFLIGHT_STATUS_REVIEWED,
    PHASE11_PREFLIGHT_STATUS_REJECTED,
)
PHASE11_PREFLIGHT_DOSSIER_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "preflight_dossier_contract_version",
        "preflight_dossier_kind",
        "packet_id",
        "packet_fingerprint",
        "domain",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "contract_spec_version",
        "review_record_contract_version",
        "contract_spec_label",
        "review_record_label",
        "included_record_fingerprints",
        "required_gates",
        "gates",
        "reviewed_gate_count",
        "missing_gate_count",
        "rejected_gate_count",
        "blocking_reasons",
    }
)
PHASE11_PREFLIGHT_DOSSIER_ALLOWED_FIELDS = PHASE11_PREFLIGHT_DOSSIER_REQUIRED_FIELDS
PHASE11_PREFLIGHT_GATE_REQUIRED_FIELDS = frozenset(
    {
        "gate_id",
        "contract_required",
        "review_status",
        "preflight_status",
        "blocking_reason",
        "execution_permitted",
    }
)
PHASE11_PREFLIGHT_GATE_ALLOWED_FIELDS = PHASE11_PREFLIGHT_GATE_REQUIRED_FIELDS
PHASE11_PREFLIGHT_FINGERPRINT_REQUIRED_FIELDS = frozenset(
    {
        "contract_spec_sha256",
        "review_record_sha256",
    }
)
PHASE11_LIFECYCLE_STAGE_VALUES = (
    PHASE11_LIFECYCLE_STAGE_CREATED,
    PHASE11_LIFECYCLE_STAGE_REVIEWED,
    PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
    PHASE11_LIFECYCLE_STAGE_REJECTED,
    PHASE11_LIFECYCLE_STAGE_ARCHIVED,
    PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
)
PHASE11_SIGNOFF_VERDICT_VALUES = (
    PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
    PHASE11_SIGNOFF_VERDICT_BLOCKERS,
    PHASE11_SIGNOFF_VERDICT_REJECTED,
    PHASE11_SIGNOFF_VERDICT_SUPERSEDED,
)
PHASE11_LIFECYCLE_DECISION_VALUES = (
    PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
    PHASE11_LIFECYCLE_DECISION_BLOCKED,
    PHASE11_LIFECYCLE_DECISION_REJECTED,
    PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
    PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
)
PHASE11_SIGNOFF_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "signoff_contract_version",
        "signoff_kind",
        "signoff_id",
        "signoff_fingerprint",
        "reviewer_label",
        "review_timestamp",
        "review_scope",
        "verdict",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_SIGNOFF_ALLOWED_FIELDS = PHASE11_SIGNOFF_REQUIRED_FIELDS
PHASE11_DECISION_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "decision_contract_version",
        "decision_kind",
        "decision_id",
        "decision_fingerprint",
        "domain",
        "dossier_packet_id",
        "dossier_packet_fingerprint",
        "decision",
        "decision_reason",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_DECISION_ALLOWED_FIELDS = PHASE11_DECISION_REQUIRED_FIELDS
PHASE11_COMPARISON_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "comparison_contract_version",
        "comparison_kind",
        "domain",
        "left_packet_id",
        "right_packet_id",
        "left_packet_fingerprint",
        "right_packet_fingerprint",
        "left_status",
        "right_status",
        "left_blocking_reason_count",
        "right_blocking_reason_count",
        "equal",
        "changed_fields",
        "changed_field_count",
        "gate_status_delta_count",
        "record_hash_delta_count",
        "rejection_reason_delta_count",
        "right_rejection_reasons",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_COMPARISON_ALLOWED_FIELDS = PHASE11_COMPARISON_REQUIRED_FIELDS
PHASE11_LIFECYCLE_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "lifecycle_contract_version",
        "lifecycle_record_kind",
        "lifecycle_record_id",
        "lifecycle_record_fingerprint",
        "domain",
        "lifecycle_stage",
        "lifecycle_status",
        "dossier_packet_id",
        "dossier_packet_fingerprint",
        "preflight_status",
        "preflight_reviewed_gate_count",
        "preflight_missing_gate_count",
        "preflight_rejected_gate_count",
        "blocking_reason_count",
        "comparison",
        "reviewer_signoff",
        "audit_decision",
        "signoff_count",
        "decision_count",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_LIFECYCLE_ALLOWED_FIELDS = PHASE11_LIFECYCLE_REQUIRED_FIELDS
PHASE11_PREFLIGHT_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "dossiers",
    }
)
PHASE11_LIFECYCLE_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "records",
        "comparisons",
    }
)
PHASE11_AUDIT_INDEX_ENTRY_REQUIRED_FIELDS = frozenset(
    {
        "entry_label",
        "domain",
        "dossier_packet_label",
        "dossier_packet_fingerprint",
        "lifecycle_record_label",
        "lifecycle_record_fingerprint",
        "decision_record_label",
        "decision_record_fingerprint",
        "lifecycle_stage",
        "audit_decision",
        "reviewer_scope_label",
        "preflight_status",
        "reviewed_gate_count",
        "missing_gate_count",
        "rejected_gate_count",
        "blocking_reason_count",
        "retention_label",
        "export_class",
        "execution_permitted",
    }
)
PHASE11_AUDIT_INDEX_ENTRY_ALLOWED_FIELDS = PHASE11_AUDIT_INDEX_ENTRY_REQUIRED_FIELDS
PHASE11_CHANGE_CONTROL_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "change_control_contract_version",
        "change_control_kind",
        "change_control_id",
        "change_control_fingerprint",
        "domain",
        "prior_lifecycle_record_label",
        "prior_lifecycle_record_fingerprint",
        "current_lifecycle_record_label",
        "current_lifecycle_record_fingerprint",
        "change_timestamp",
        "change_reason",
        "reviewer_scope_label",
        "decision",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_CHANGE_CONTROL_ALLOWED_FIELDS = PHASE11_CHANGE_CONTROL_REQUIRED_FIELDS
PHASE11_SUPERSESSION_LINK_REQUIRED_FIELDS = frozenset(
    {
        "position",
        "record_label",
        "record_fingerprint",
        "prior_record_label",
        "prior_record_fingerprint",
        "future_record_label",
        "future_record_fingerprint",
        "lifecycle_stage",
        "decision",
        "has_prior",
        "has_future",
    }
)
PHASE11_SUPERSESSION_LINK_ALLOWED_FIELDS = PHASE11_SUPERSESSION_LINK_REQUIRED_FIELDS
PHASE11_SUPERSESSION_CHAIN_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "supersession_contract_version",
        "supersession_chain_kind",
        "chain_id",
        "chain_fingerprint",
        "domain",
        "chain_status",
        "cross_domain_allowed",
        "record_count",
        "links",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_SUPERSESSION_CHAIN_ALLOWED_FIELDS = PHASE11_SUPERSESSION_CHAIN_REQUIRED_FIELDS
PHASE11_REVIEWER_SCOPE_COVERAGE_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "coverage_contract_version",
        "coverage_kind",
        "coverage_id",
        "coverage_fingerprint",
        "domain",
        "reviewer_scope_label",
        "required_gates",
        "covered_gates",
        "missing_gates",
        "gate_scope_labels",
        "coverage_complete",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_REVIEWER_SCOPE_COVERAGE_ALLOWED_FIELDS = PHASE11_REVIEWER_SCOPE_COVERAGE_REQUIRED_FIELDS
PHASE11_EXPORT_RETENTION_POLICY_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "export_retention_contract_version",
        "export_retention_kind",
        "policy_id",
        "policy_fingerprint",
        "domain",
        "retention_label",
        "export_class",
        "local_only",
        "metadata_export_allowed",
        "deterministic_fixture_export_allowed",
        "payload_export_prohibited",
        "document_text_export_prohibited",
        "signal_export_prohibited",
        "origin_identifier_export_prohibited",
        "hardware_identifier_export_prohibited",
        "auth_material_export_prohibited",
        "path_export_prohibited",
        "url_export_prohibited",
        "model_artifact_payload_export_prohibited",
        "adapter_component_payload_export_prohibited",
        "external_upload_prohibited",
        "network_export_prohibited",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_EXPORT_RETENTION_POLICY_ALLOWED_FIELDS = PHASE11_EXPORT_RETENTION_POLICY_REQUIRED_FIELDS
PHASE11_AUDIT_INDEX_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "audit_index_contract_version",
        "audit_index_kind",
        "index_id",
        "index_fingerprint",
        "domain_scope",
        "status",
        "included_dossier_packet_labels",
        "included_lifecycle_record_labels",
        "included_decision_record_labels",
        "included_record_fingerprints",
        "lifecycle_stage_counts",
        "decision_counts",
        "reviewer_scope_coverage",
        "supersession_chains",
        "change_control_records",
        "export_retention_policies",
        "entries",
        "entry_count",
        "created_count",
        "reviewed_count",
        "superseded_count",
        "rejected_count",
        "archived_count",
        "decision_recorded_count",
        "blocking_count",
        "rejection_count",
        "deterministic_ordering",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_AUDIT_INDEX_ALLOWED_FIELDS = PHASE11_AUDIT_INDEX_REQUIRED_FIELDS
PHASE11_AUDIT_INDEX_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "audit_index",
        "change_control_records",
        "supersession_chains",
        "reviewer_scope_coverage",
        "export_retention_policies",
    }
)
PHASE11_AUDIT_HANDOFF_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "audit_handoff_contract_version",
        "audit_handoff_kind",
        "handoff_id",
        "handoff_fingerprint",
        "domain",
        "status",
        "contract_versions",
        "audit_index_label",
        "audit_index_fingerprint",
        "audit_index_status",
        "audit_index_entry_count",
        "lifecycle_status_counts",
        "reviewer_scope_coverage_summary",
        "retention_export_policy_summary",
        "blocking_count",
        "rejection_count",
        "unresolved_review_count",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_AUDIT_HANDOFF_ALLOWED_FIELDS = PHASE11_AUDIT_HANDOFF_REQUIRED_FIELDS
PHASE11_AUDIT_HANDOFF_COVERAGE_SUMMARY_REQUIRED_FIELDS = frozenset(
    {
        "reviewer_scope_label",
        "required_gate_count",
        "covered_gate_count",
        "missing_gate_count",
        "coverage_complete",
    }
)
PHASE11_AUDIT_HANDOFF_RETENTION_SUMMARY_REQUIRED_FIELDS = frozenset(
    {
        "retention_label",
        "export_class",
        "metadata_export_allowed",
        "deterministic_fixture_export_allowed",
        "external_upload_prohibited",
        "network_export_prohibited",
    }
)
PHASE11_AUDIT_HANDOFF_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "handoffs",
    }
)
PHASE11_HANDOFF_ACCEPTANCE_STATUS_VALUES = (
    PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS,
)
PHASE11_HANDOFF_ACCEPTANCE_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "handoff_acceptance_contract_version",
        "handoff_acceptance_kind",
        "acceptance_id",
        "acceptance_fingerprint",
        "domain",
        "status",
        "contract_versions",
        "source_handoff_label",
        "source_handoff_hash",
        "handoff_fingerprint",
        "handoff_status",
        "accepted_for_planning",
        "blocked",
        "stale",
        "missing_review_count",
        "unresolved_review_count",
        "rejection_reasons",
        "blocking_reasons",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_HANDOFF_ACCEPTANCE_ALLOWED_FIELDS = PHASE11_HANDOFF_ACCEPTANCE_REQUIRED_FIELDS
PHASE11_HANDOFF_ACCEPTANCE_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "acceptance_records",
    }
)
PHASE11_ACCEPTANCE_FOLLOWUP_TYPE_VALUES = (
    PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
    PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE,
)
PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_VALUES = (
    PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS,
    PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS,
)
PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_SUMMARIES = (
    "no-blockers",
    "blockers-open",
    "blockers-dispositioned",
    "source-rejected",
)
PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_SUMMARIES = (
    "reviews-clear",
    "reviewer-queue-open",
    "needs-more-review",
    "reviewer-queue-blocked",
)
PHASE11_ACCEPTANCE_FOLLOWUP_STALE_SUMMARIES = (
    "source-current",
    "source-stale-renewal-open",
    "source-stale-renewal-blocked",
)
PHASE11_ACCEPTANCE_FOLLOWUP_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "acceptance_followup_contract_version",
        "followup_kind",
        "followup_id",
        "domain",
        "followup_type",
        "status",
        "contract_versions",
        "source_acceptance_label",
        "source_acceptance_hash",
        "blocker_disposition_summary",
        "reviewer_queue_summary",
        "stale_renewal_summary",
        "unresolved_review_count",
        "blocking_count",
        "rejection_count",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_ACCEPTANCE_FOLLOWUP_ALLOWED_FIELDS = PHASE11_ACCEPTANCE_FOLLOWUP_REQUIRED_FIELDS
PHASE11_ACCEPTANCE_FOLLOWUP_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "followup_records",
    }
)
PHASE11_FOLLOWUP_QUEUE_STATUS_VALUES = (
    PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_BLOCKED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_STALE_STATUS,
    PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS,
    PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS,
)
PHASE11_FOLLOWUP_QUEUE_INDEX_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "queue_index_contract_version",
        "queue_index_kind",
        "queue_id",
        "queue_fingerprint",
        "domain",
        "status",
        "contract_versions",
        "included_followup_labels",
        "included_followup_hashes",
        "queue_status_counts",
        "blocker_disposition_counts",
        "reviewer_queue_counts",
        "stale_renewal_counts",
        "entry_count",
        "open_count",
        "blocked_count",
        "stale_count",
        "unresolved_review_count",
        "blocking_count",
        "blocker_disposition_count",
        "reviewer_queue_count",
        "stale_renewal_count",
        "needs_more_review_count",
        "archived_count",
        "rejected_count",
        "resolved_for_planning_count",
        "deterministic_ordering",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_FOLLOWUP_QUEUE_INDEX_ALLOWED_FIELDS = PHASE11_FOLLOWUP_QUEUE_INDEX_REQUIRED_FIELDS
PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "queue_index_contract_version",
        "queue_acceptance_kind",
        "acceptance_id",
        "acceptance_fingerprint",
        "queue_label",
        "queue_fingerprint",
        "domain",
        "status",
        "contract_versions",
        "queue_status_counts",
        "entry_count",
        "unresolved_review_count",
        "blocking_count",
        "stale_count",
        "archived_count",
        "rejected_count",
        "resolved_for_planning_count",
        "reviewer_queue_count",
        "blocker_disposition_count",
        "needs_more_review_count",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_ALLOWED_FIELDS = PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_REQUIRED_FIELDS
PHASE11_FOLLOWUP_QUEUE_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "queue_index_records",
        "queue_acceptance_checks",
    }
)
PHASE11_DECISION_CLOSEOUT_DECISION_VALUES = (
    PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION,
    PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION,
    PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
    PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION,
    PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION,
    PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION,
)
PHASE11_DECISION_CLOSEOUT_STATUS_VALUES = (
    PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS,
    PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS,
    PHASE11_DECISION_CLOSEOUT_BLOCKED_STATUS,
    PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
    PHASE11_DECISION_CLOSEOUT_ARCHIVED_STATUS,
)
PHASE11_DECISION_CLOSEOUT_DISPOSITION_SUMMARIES = (
    "all-queue-items-resolved-for-planning",
    "stale-items-deferred",
    "queue-rejected",
    "queue-archived",
    "reviewer-queue-open",
    "blockers-remain",
)
PHASE11_DECISION_CLOSEOUT_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "closeout_contract_version",
        "closeout_id",
        "contract_versions",
        "domain",
        "source_queue_label",
        "source_queue_hash",
        "closeout_decision",
        "closeout_status",
        "reviewer_disposition_summary",
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
        "archived_count",
        "rejected_count",
        "deferred_count",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_DECISION_CLOSEOUT_ALLOWED_FIELDS = PHASE11_DECISION_CLOSEOUT_REQUIRED_FIELDS
PHASE11_DECISION_CLOSEOUT_FIXTURE_BUNDLE_ALLOWED_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_contract_version",
        "fixture_kind",
        "status",
        "planning_only",
        "metadata_only",
        "sanitized",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
        "decision_closeout_records",
    }
)
PHASE11_REVIEW_TRAIL_EXPORT_DOMAIN_REQUIRED_FIELDS = frozenset(
    {
        "domain_label",
        "final_closeout_decision",
        "final_closeout_status",
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
    }
)
PHASE11_REVIEW_TRAIL_EXPORT_DOMAIN_ALLOWED_FIELDS = (
    PHASE11_REVIEW_TRAIL_EXPORT_DOMAIN_REQUIRED_FIELDS
)
PHASE11_REVIEW_TRAIL_EXPORT_REQUIRED_FIELDS = frozenset(
    {
        "review_trail_export_contract_version",
        "export_id",
        "phase_range",
        "covered_phase_count",
        "domain_labels",
        "domain_closeouts",
        "readiness_gap_summary",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_REVIEW_TRAIL_EXPORT_ALLOWED_FIELDS = PHASE11_REVIEW_TRAIL_EXPORT_REQUIRED_FIELDS
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_DOMAIN_REQUIRED_FIELDS = frozenset(
    {
        "domain_label",
        "source_closeout_decision",
        "source_closeout_status",
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
        "missing_future_gate_count",
    }
)
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_DOMAIN_ALLOWED_FIELDS = (
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_DOMAIN_REQUIRED_FIELDS
)
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_REQUIRED_FIELDS = frozenset(
    {
        "runtime_authorization_gap_ledger_contract_version",
        "ledger_id",
        "source_phase_range",
        "covered_phase_count",
        "domain_labels",
        "domain_gap_summaries",
        "authorization_status",
        "readiness_gap",
        "missing_future_gates",
        "missing_future_gate_count",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_ALLOWED_FIELDS = (
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_REQUIRED_FIELDS
)
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_REQUIRED_FIELDS = frozenset(
    {
        "planning_governance_closeout_contract_version",
        "closeout_index_id",
        "phase_range",
        "covered_phase_count",
        "final_status",
        "runtime_authorization_status",
        "readiness_gap",
        "next_phase_requirement",
        "gap_ledger_id",
        "gap_ledger_contract_version",
        "gap_ledger_phase_range",
        "domain_labels",
        "domain_count",
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
        "missing_future_gate_count",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_ALLOWED_FIELDS = (
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_REQUIRED_FIELDS
)

PHASE11_ALLOWED_KEYS = frozenset(
    {
        "adapter_kind",
        "adapter_execution_granted",
        "artifact_privacy_contract",
        "accepted_for_planning",
        "acceptance_followup_acceptance_hash",
        "acceptance_followup_acceptance_label",
        "acceptance_followup_blocker_summary",
        "acceptance_followup_blocking_count",
        "acceptance_followup_contract_version",
        "acceptance_followup_execution_permitted",
        "acceptance_followup_id",
        "acceptance_followup_rejection_count",
        "acceptance_followup_reviewer_summary",
        "acceptance_followup_runtime_stage",
        "acceptance_followup_stale_summary",
        "acceptance_followup_status",
        "acceptance_followup_type",
        "acceptance_followup_unresolved_review_count",
        "acceptance_id",
        "acceptance_fingerprint",
        "archived_count",
        "blocker_disposition_summary",
        "blocker_disposition_count",
        "blocker_disposition_counts",
        "body_export",
        "blocked",
        "blocked_count",
        "blocking_count",
        "blocking_reasons",
        "booth_hardware_topology_metadata_contract",
        "booth_role_metadata_only",
        "booth_size_class",
        "capture_execution",
        "closed_runtime_flags",
        "closeout_index_id",
        "consent_privacy_contract",
        "contract_spec_kind",
        "contract_spec_version",
        "contract_status",
        "counts_status_only",
        "current_mode",
        "data_export",
        "dependency_execution",
        "document_contract_spec",
        "document_ingestion",
        "domain",
        "domain_count",
        "domain_gap_summaries",
        "deterministic_ordering",
        "empty_booth_baseline_concept",
        "esp32_flashing",
        "execution_permitted",
        "file_crawling",
        "fixed_ap_role",
        "final_status",
        "followup_id",
        "followup_kind",
        "followup_type",
        "gate_contract_version",
        "gate_kind",
        "gap_ledger_contract_version",
        "gap_ledger_id",
        "gap_ledger_phase_range",
        "hardware_access",
        "hardware_review_contract",
        "handoff_acceptance_contract_version",
        "handoff_acceptance_kind",
        "handoff_fingerprint",
        "handoff_status",
        "included_followup_hashes",
        "included_followup_labels",
        "local_name_export",
        "license_source_review_contract",
        "metadata_only",
        "metadata_staging_contract",
        "missing_future_gate_count",
        "missing_future_gates",
        "missing_gate_count",
        "missing_gates",
        "missing_review_count",
        "model_artifact_review_contract",
        "model_download",
        "model_execution_granted",
        "model_execution",
        "monitor_mode",
        "mqtt_udp_listener",
        "network_calls",
        "network_policy_contract",
        "next_phase_requirement",
        "needs_more_review_count",
        "origin_identifier_export",
        "open_count",
        "packet_capture",
        "parser_boundary_contract",
        "parser_execution",
        "path_export",
        "pdf_parsing",
        "phase",
        "phase_range",
        "planning_governance_closeout_contract_version",
        "planning_only",
        "provider_detail_export",
        "provider_execution_granted",
        "queue_acceptance_kind",
        "queue_acceptance_checks",
        "queue_fingerprint",
        "queue_id",
        "queue_index_contract_version",
        "queue_index_kind",
        "queue_index_records",
        "queue_label",
        "queue_status_counts",
        "readiness_gate",
        "readiness_gate_missing_count",
        "readiness_gate_status",
        "readiness_gap",
        "ready",
        "real_mode_runtime_enabled",
        "receiver_role_count_range",
        "rejection_count",
        "rejection_reasons",
        "required_contracts",
        "required_gate_count",
        "required_gates",
        "review_required",
        "p11b_review_record_status",
        "review_record_contract_version",
        "review_record_kind",
        "review_record_status",
        "reviewed_gate_count",
        "rejected_count",
        "rejected_gate_count",
        "rejected_gates",
        "resolved_for_planning_count",
        "rf_signal_export",
        "rf_booth_contract_spec",
        "router_ap_control",
        "runtime_execution",
        "runtime_stage",
        "sanitized",
        "schema_version",
        "smart_home_bridge",
        "source_handoff_hash",
        "source_handoff_label",
        "source_acceptance_hash",
        "source_acceptance_label",
        "space_scope",
        "stale",
        "stale_count",
        "stale_renewal_count",
        "stale_renewal_counts",
        "stale_renewal_summary",
        "status",
        "subject_scope",
        "topology_claim",
        "url_export",
        "unresolved_review_count",
        "reviewer_queue_summary",
        "reviewer_queue_count",
        "reviewer_queue_counts",
        "wifi_network_probing",
        "authorization_status",
        "covered_phase_count",
        "ledger_id",
        "runtime_authorization_gap_ledger_contract_version",
        "runtime_authorization_status",
        "source_closeout_decision",
        "source_closeout_status",
        "source_phase_range",
    }
)
PHASE11_FORBIDDEN_KEYS = frozenset(
    {
        "absolute_path",
        "absolute_paths",
        "access_token",
        "api_key",
        "authorization",
        "bssid",
        "credential",
        "credentials",
        "device_id",
        "device_ids",
        "endpoint",
        "file",
        "files",
        "fixture_ref",
        "fixture_refs",
        "host",
        "hostname",
        "ip_address",
        "mac",
        "model_body",
        "model_weights",
        "parser_body",
        "parser_payload",
        "password",
        "path",
        "paths",
        "provider_body",
        "provider_payload",
        "raw_csi",
        "raw_document_text",
        "raw_rf",
        "raw_signal",
        "raw_text",
        "raw_values",
        "refresh_token",
        "remote_url",
        "router_id",
        "secret",
        "secret_value",
        "source_id",
        "source_ids",
        "ssid",
        "token",
        "url",
        "urls",
    }
)
PHASE11_FORBIDDEN_KEY_FRAGMENTS = (
    "access_token",
    "api_key",
    "authorization",
    "credential",
    "fixture_ref",
    "model_body",
    "model_weight",
    "parser_body",
    "parser_payload",
    "provider_body",
    "provider_payload",
    "raw_",
    "refresh_token",
    "remote_url",
    "secret",
    "device_id",
    "router_id",
    "source_id",
)
PHASE11_FORBIDDEN_VALUE_FRAGMENTS = (
    "://",
    "c:/",
    "c:\\",
    "/home/",
    "\\home\\",
    "document-parsed.json",
    "document-mixed.json",
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "fixture://",
    "fixtures/",
    "raw document text",
    "raw_document_text",
    "raw_csi",
    "raw_rf",
    "raw signal",
    "raw_values",
    "source_id",
    "source_ids",
    "device_id",
    "device_ids",
    "router_id",
    "router_ids",
    "parser_body",
    "parser_payload",
    "model body",
    "model weights",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "bearer",
    "credential",
    "password",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
    "accepted-for-runtime",
    "accepted for runtime",
    "execution-permitted",
    "execution permitted",
    "runtime-enabled",
    "runtime enabled",
    "enable-runtime",
    "enable runtime",
    "run-adapter",
    "run adapter",
    "example.invalid",
)
PHASE11_REQUIRED_FALSE_FLAGS = (
    "document_ingestion",
    "file_crawling",
    "pdf_parsing",
    "network_calls",
    "body_export",
    "origin_identifier_export",
    "local_name_export",
    "path_export",
    "url_export",
    "provider_detail_export",
    "parser_execution",
    "runtime_execution",
    "hardware_access",
    "capture_execution",
    "packet_capture",
    "monitor_mode",
    "wifi_network_probing",
    "esp32_flashing",
    "router_ap_control",
    "mqtt_udp_listener",
    "smart_home_bridge",
    "model_download",
    "model_execution",
    "rf_signal_export",
    "data_export",
    "dependency_execution",
)


@dataclass(frozen=True)
class Phase11ContractSpecValidationResult:
    """Sanitized validation result for Phase 11A contract/spec payloads."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_spec: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
        }


@dataclass(frozen=True)
class Phase11ReviewRecordValidationResult:
    """Sanitized validation result for Phase 11B review records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    reviewed_gate_count: int = 0
    missing_gate_count: int = len(REAL_MODE_REQUIRED_GATES)
    rejected_gate_count: int = 0
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def record_status(self) -> str:
        return str(
            self.sanitized_record.get("record_status") or PHASE11_REVIEW_RECORD_STATUS_REJECTED
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "record_status": self.record_status,
            "reviewed_gate_count": self.reviewed_gate_count,
            "missing_gate_count": self.missing_gate_count,
            "rejected_gate_count": self.rejected_gate_count,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11PreflightDossierValidationResult:
    """Sanitized validation result for Phase 11C preflight dossiers."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_dossier: dict[str, object]
    reviewed_gate_count: int = 0
    missing_gate_count: int = len(REAL_MODE_REQUIRED_GATES)
    rejected_gate_count: int = 0
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_dossier.get("status") or PHASE11_PREFLIGHT_STATUS_REJECTED)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "reviewed_gate_count": self.reviewed_gate_count,
            "missing_gate_count": self.missing_gate_count,
            "rejected_gate_count": self.rejected_gate_count,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11LifecycleAuditValidationResult:
    """Sanitized validation result for Phase 11D lifecycle/audit records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("lifecycle_stage")
            or self.sanitized_record.get("decision")
            or self.sanitized_record.get("verdict")
            or PHASE11_LIFECYCLE_STAGE_REJECTED
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11AuditIndexValidationResult:
    """Sanitized validation result for Phase 11E audit-index records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("status")
            or self.sanitized_record.get("chain_status")
            or self.sanitized_record.get("export_class")
            or PHASE11_AUDIT_INDEX_REJECTED_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11AuditHandoffValidationResult:
    """Sanitized validation result for Phase 11F audit handoff records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_record.get("status") or PHASE11_AUDIT_HANDOFF_REJECTED_STATUS)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11HandoffAcceptanceValidationResult:
    """Sanitized validation result for Phase 11G handoff acceptance records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("status") or PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11AcceptanceFollowupValidationResult:
    """Sanitized validation result for Phase 11H follow-up records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("status") or PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11FollowupQueueValidationResult:
    """Sanitized validation result for Phase 11I queue index records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_record.get("status") or PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11FollowupQueueAcceptanceValidationResult:
    """Sanitized validation result for Phase 11I queue acceptance checks."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_record.get("status") or PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11DecisionCloseoutValidationResult:
    """Sanitized validation result for Phase 11J decision-closeout records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("closeout_status")
            or PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11ReviewTrailExportValidationResult:
    """Sanitized validation result for Phase 11K review trail exports."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_record.get("readiness_gap_summary") or "")

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11RuntimeAuthorizationGapLedgerValidationResult:
    """Sanitized validation result for Phase 11L runtime gap ledgers."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status")
            or PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase11PlanningGovernanceCloseoutValidationResult:
    """Sanitized validation result for Phase 11M governance closeout indexes."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    planning_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("final_status") or PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "runtime_authorization_status": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS),
            "sanitized": self.sanitized,
            "planning_only": self.planning_only,
            "metadata_only": self.metadata_only,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


def phase11_review_record_schema() -> dict[str, object]:
    """Return the Phase 11B review-record schema shape as metadata."""

    return {
        "schema_version": 1,
        "review_record_contract_version": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "review_record_kind": PHASE11_REVIEW_RECORD_KIND,
        "required_fields": sorted(PHASE11_REVIEW_RECORD_REQUIRED_FIELDS),
        "review_entry_required_fields": sorted(PHASE11_REVIEW_ENTRY_REQUIRED_FIELDS),
        "review_types": [
            {
                "field": field,
                "gate_id": gate,
                "review_type": review_type,
                "review_scope": scope,
            }
            for field, gate, review_type, scope in PHASE11_REVIEW_RECORD_SPECS
        ],
        "record_statuses": list(PHASE11_REVIEW_RECORD_STATUS_VALUES),
        "entry_statuses": list(PHASE11_REVIEW_ENTRY_STATUS_VALUES),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_review_record(
    *,
    domain: str,
    reviewed_gates: tuple[str, ...] | list[str] | None = None,
    rejected_gates: tuple[str, ...] | list[str] | None = None,
    record_status: str | None = None,
) -> dict[str, object]:
    """Build a deterministic Phase 11B review record without runtime authority."""

    reviewed = _ordered_gate_subset(reviewed_gates)
    rejected = _ordered_gate_subset(rejected_gates)
    rejected_set = set(rejected)
    reviewed = tuple(gate for gate in reviewed if gate not in rejected_set)
    reviewed_set = set(reviewed)
    missing = tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate not in reviewed_set)
    inferred_status = _review_record_status(reviewed, missing, rejected)
    status = _safe_review_record_status(record_status, inferred_status)
    return {
        "schema_version": 1,
        "review_record_contract_version": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "review_record_kind": PHASE11_REVIEW_RECORD_KIND,
        "domain": _safe_domain(domain),
        "record_status": status,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "required_gates": list(REAL_MODE_REQUIRED_GATES),
        "reviewed_gates": list(reviewed),
        "missing_gates": list(missing),
        "rejected_gates": list(rejected),
        "reviewed_gate_count": len(reviewed),
        "missing_gate_count": len(missing),
        "rejected_gate_count": len(rejected),
        "reviews": {
            field: _phase11_review_entry(
                gate_id=gate,
                review_type=review_type,
                review_scope=scope,
                status=(
                    "rejected"
                    if gate in rejected_set
                    else "reviewed"
                    if gate in reviewed_set
                    else "not-reviewed"
                ),
            )
            for field, gate, review_type, scope in PHASE11_REVIEW_RECORD_SPECS
        },
    }


def phase11_document_ingestion_review_record(
    *,
    complete: bool = True,
) -> dict[str, object]:
    """Return a deterministic document-ingestion review record fixture."""

    reviewed = REAL_MODE_REQUIRED_GATES if complete else REAL_MODE_REQUIRED_GATES[:4]
    return phase11_review_record(
        domain=PHASE11_DOCUMENT_DOMAIN,
        reviewed_gates=reviewed,
    )


def phase11_wifi_csi_rf_booth_review_record(
    *,
    complete: bool = True,
) -> dict[str, object]:
    """Return a deterministic WiFi CSI/RF booth review record fixture."""

    reviewed = REAL_MODE_REQUIRED_GATES if complete else REAL_MODE_REQUIRED_GATES[:3]
    return phase11_review_record(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        reviewed_gates=reviewed,
    )


def phase11_rejected_review_record(
    *,
    domain: str,
    rejected_gate: str = "privacy-review",
) -> dict[str, object]:
    """Return a deterministic rejected fail-closed review record fixture."""

    return phase11_review_record(
        domain=domain,
        reviewed_gates=REAL_MODE_REQUIRED_GATES,
        rejected_gates=(rejected_gate,),
    )


def phase11_review_record_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11B review-record fixture examples."""

    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "fixture_kind": PHASE11_REVIEW_RECORD_FIXTURE_KIND,
        "status": "review-record-fixtures-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "records": {
            "document_ingestion_reviewed": phase11_document_ingestion_review_record(),
            "wifi_csi_rf_booth_reviewed": phase11_wifi_csi_rf_booth_review_record(),
            "incomplete_review_record": phase11_document_ingestion_review_record(complete=False),
            "rejected_review_record": phase11_rejected_review_record(
                domain=PHASE11_DOCUMENT_DOMAIN,
                rejected_gate="license-review",
            ),
            "all_gates_reviewed_runtime_disabled": phase11_review_record(
                domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
                reviewed_gates=REAL_MODE_REQUIRED_GATES,
            ),
        },
    }


def phase11_document_ingestion_preflight_dossier(
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build a deterministic document-ingestion preflight dossier."""

    return phase11_preflight_dossier(
        domain=PHASE11_DOCUMENT_DOMAIN,
        contract_spec=phase11_document_ingestion_contract_spec(review_record),
        review_record=review_record,
    )


def phase11_wifi_csi_rf_booth_preflight_dossier(
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build a deterministic RF booth/WiFi CSI preflight dossier."""

    return phase11_preflight_dossier(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        contract_spec=phase11_wifi_csi_rf_booth_contract_spec(review_record),
        review_record=review_record,
    )


def phase11_preflight_dossier(
    *,
    domain: str,
    contract_spec: Mapping[str, object] | None = None,
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Assemble Phase 11A/11B planning evidence into a non-executable packet."""

    safe_domain = _safe_domain(domain)
    spec = (
        contract_spec
        if isinstance(contract_spec, Mapping)
        else _default_contract_spec_for_domain(safe_domain, review_record)
    )
    spec_result = validate_phase11_contract_spec(spec)
    review_result = (
        validate_phase11_review_record(review_record, expected_domain=safe_domain)
        if _looks_like_phase11_review_record(review_record)
        else _missing_phase11_review_record_result(
            domain=safe_domain,
        )
    )
    gates = _phase11_preflight_gate_statuses(
        review_result,
        spec_result=spec_result,
    )
    reviewed_count = sum(1 for gate in gates if gate["preflight_status"] == "reviewed")
    missing_count = sum(1 for gate in gates if gate["preflight_status"] == "missing")
    rejected_count = sum(1 for gate in gates if gate["preflight_status"] == "rejected")
    blocking_reasons = _phase11_preflight_blocking_reasons(
        spec_result=spec_result,
        review_result=review_result,
        gates=gates,
    )
    status = _phase11_preflight_status(
        missing_count=missing_count,
        rejected_count=rejected_count,
        blocking_reasons=blocking_reasons,
    )
    payload = {
        "schema_version": 1,
        "preflight_dossier_contract_version": (PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION),
        "preflight_dossier_kind": PHASE11_PREFLIGHT_DOSSIER_KIND,
        "packet_id": None,
        "packet_fingerprint": None,
        "domain": safe_domain,
        "status": status,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "contract_spec_version": PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
        "review_record_contract_version": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "contract_spec_label": f"{safe_domain}-p11a-contract-v1",
        "review_record_label": _phase11_review_record_label(
            review_record,
            domain=safe_domain,
        ),
        "included_record_fingerprints": {
            "contract_spec_sha256": _phase11_payload_sha256(spec_result.sanitized_spec),
            "review_record_sha256": _phase11_payload_sha256(review_result.sanitized_record),
        },
        "required_gates": list(REAL_MODE_REQUIRED_GATES),
        "gates": gates,
        "reviewed_gate_count": reviewed_count,
        "missing_gate_count": missing_count,
        "rejected_gate_count": rejected_count,
        "blocking_reasons": blocking_reasons,
    }
    return _finalize_phase11_preflight_dossier(payload)


def phase11_preflight_dossier_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11C preflight dossier fixture examples."""

    records = phase11_review_record_fixture_bundle()["records"]
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION,
        "fixture_kind": PHASE11_PREFLIGHT_DOSSIER_FIXTURE_KIND,
        "status": "preflight-dossiers-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "dossiers": {
            "document_ingestion_reviewed": (
                phase11_document_ingestion_preflight_dossier(
                    records["document_ingestion_reviewed"],
                )
            ),
            "wifi_csi_rf_booth_reviewed": (
                phase11_wifi_csi_rf_booth_preflight_dossier(
                    records["wifi_csi_rf_booth_reviewed"],
                )
            ),
            "incomplete_review_record": (
                phase11_document_ingestion_preflight_dossier(
                    records["incomplete_review_record"],
                )
            ),
            "rejected_review_record": (
                phase11_document_ingestion_preflight_dossier(
                    records["rejected_review_record"],
                )
            ),
            "missing_review_record": phase11_document_ingestion_preflight_dossier(),
        },
    }


def phase11_preflight_status_summary(
    dossier: Mapping[str, object] | None = None,
    *,
    domain: str,
) -> dict[str, object]:
    """Return compact preflight status safe for public surfaces."""

    built = (
        dossier
        if _looks_like_phase11_preflight_dossier(dossier)
        else _default_preflight_dossier_for_domain(_safe_domain(domain))
    )
    result = validate_phase11_preflight_dossier(
        built,
        expected_domain=_safe_domain(domain),
    )
    safe = result.sanitized_dossier
    return {
        "schema_version": 1,
        "preflight_packet_contract_version": (PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION),
        "domain": _safe_domain(domain),
        "preflight_packet_label": f"p11c-{_safe_domain(domain)}-preflight",
        "preflight_packet_id": _safe_preflight_packet_id(safe.get("packet_id")),
        "preflight_packet_fingerprint": _safe_sha256(safe.get("packet_fingerprint")),
        "preflight_status": _safe_preflight_status(safe.get("status")),
        "reviewed_gate_count": result.reviewed_gate_count,
        "missing_gate_count": result.missing_gate_count,
        "rejected_gate_count": result.rejected_gate_count,
        "blocking_reason_count": len(safe.get("blocking_reasons") or ()),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_reviewer_signoff_metadata(
    *,
    reviewer_label: str = "p11d-planning-reviewer",
    review_timestamp: str = "2026-06-09T00:00:00Z",
    review_scope: str = "planning-audit",
    verdict: str = PHASE11_SIGNOFF_VERDICT_BLOCKERS,
) -> dict[str, object]:
    """Return sanitized reviewer signoff metadata without identity secrets."""

    payload = {
        "schema_version": 1,
        "signoff_contract_version": PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
        "signoff_kind": PHASE11_REVIEWER_SIGNOFF_KIND,
        "signoff_id": None,
        "signoff_fingerprint": None,
        "reviewer_label": _safe_phase11d_label(reviewer_label),
        "review_timestamp": _safe_phase11d_timestamp(review_timestamp),
        "review_scope": _safe_category(review_scope),
        "verdict": _safe_signoff_verdict(verdict),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11d_record(payload, "signoff")


def phase11_dossier_decision_record(
    dossier: Mapping[str, object] | None = None,
    *,
    decision: str = PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
    decision_reason: str = "planning-review-required",
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Return an explicit non-runtime decision record for a preflight dossier."""

    built = (
        dossier
        if _looks_like_phase11_preflight_dossier(dossier)
        else _default_preflight_dossier_for_domain(_safe_domain(domain))
    )
    safe = validate_phase11_preflight_dossier(built).sanitized_dossier
    safe_decision = _safe_lifecycle_decision(decision)
    payload = {
        "schema_version": 1,
        "decision_contract_version": PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
        "decision_kind": PHASE11_DOSSIER_DECISION_KIND,
        "decision_id": None,
        "decision_fingerprint": None,
        "domain": _safe_domain(safe.get("domain")),
        "dossier_packet_id": _safe_preflight_packet_id(safe.get("packet_id")),
        "dossier_packet_fingerprint": _safe_sha256(safe.get("packet_fingerprint")),
        "decision": safe_decision,
        "decision_reason": _safe_category(decision_reason),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11d_record(payload, "decision")


def phase11_compare_preflight_dossiers(
    left: Mapping[str, object] | None,
    right: Mapping[str, object] | None,
) -> dict[str, object]:
    """Compare two dossiers through sanitized metadata only."""

    left_ref = _phase11_preflight_comparison_ref(left)
    right_ref = _phase11_preflight_comparison_ref(right)
    changed: list[str] = []
    if left_ref["packet_id"] != right_ref["packet_id"]:
        changed.append("packet-id")
    if left_ref["contract_versions"] != right_ref["contract_versions"]:
        changed.append("contract-versions")
    if left_ref["status"] != right_ref["status"]:
        changed.append("status")
    if left_ref["gate_statuses"] != right_ref["gate_statuses"]:
        changed.append("gate-statuses")
    if left_ref["record_hashes"] != right_ref["record_hashes"]:
        changed.append("record-fingerprints")
    if left_ref["blocking_reason_count"] != right_ref["blocking_reason_count"]:
        changed.append("blocking-count")
    if left_ref["rejection_reasons"] != right_ref["rejection_reasons"]:
        changed.append("rejection-reasons")
    gate_delta = sum(
        1
        for gate in REAL_MODE_REQUIRED_GATES
        if left_ref["gate_statuses"].get(gate) != right_ref["gate_statuses"].get(gate)
    )
    record_delta = sum(
        1
        for field in PHASE11_PREFLIGHT_FINGERPRINT_REQUIRED_FIELDS
        if left_ref["record_hashes"].get(field) != right_ref["record_hashes"].get(field)
    )
    rejection_delta = abs(len(left_ref["rejection_reasons"]) - len(right_ref["rejection_reasons"]))
    return {
        "schema_version": 1,
        "comparison_contract_version": PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
        "comparison_kind": PHASE11_DOSSIER_COMPARISON_KIND,
        "domain": _safe_domain(right_ref["domain"] or left_ref["domain"]),
        "left_packet_id": left_ref["packet_id"],
        "right_packet_id": right_ref["packet_id"],
        "left_packet_fingerprint": left_ref["packet_fingerprint"],
        "right_packet_fingerprint": right_ref["packet_fingerprint"],
        "left_status": left_ref["status"],
        "right_status": right_ref["status"],
        "left_blocking_reason_count": left_ref["blocking_reason_count"],
        "right_blocking_reason_count": right_ref["blocking_reason_count"],
        "equal": not changed,
        "changed_fields": sorted(changed),
        "changed_field_count": len(changed),
        "gate_status_delta_count": gate_delta,
        "record_hash_delta_count": record_delta,
        "rejection_reason_delta_count": rejection_delta,
        "right_rejection_reasons": list(right_ref["rejection_reasons"]),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_dossier_lifecycle_record(
    dossier: Mapping[str, object] | None = None,
    *,
    lifecycle_stage: str = PHASE11_LIFECYCLE_STAGE_CREATED,
    signoff: Mapping[str, object] | None = None,
    decision_record: Mapping[str, object] | None = None,
    previous_dossier: Mapping[str, object] | None = None,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Build a sanitized Phase 11D lifecycle/audit record."""

    built = (
        dossier
        if _looks_like_phase11_preflight_dossier(dossier)
        else _default_preflight_dossier_for_domain(_safe_domain(domain))
    )
    result = validate_phase11_preflight_dossier(built)
    safe = result.sanitized_dossier
    stage = _safe_lifecycle_stage(lifecycle_stage)
    safe_signoff = (
        signoff
        if isinstance(signoff, Mapping)
        else phase11_reviewer_signoff_metadata(verdict=_default_phase11d_verdict_for_stage(stage))
    )
    safe_decision = (
        decision_record
        if isinstance(decision_record, Mapping)
        else phase11_dossier_decision_record(
            safe,
            decision=_default_phase11d_decision_for_stage(stage, safe),
        )
    )
    comparison = phase11_compare_preflight_dossiers(previous_dossier, safe)
    payload = {
        "schema_version": 1,
        "lifecycle_contract_version": PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
        "lifecycle_record_kind": PHASE11_DOSSIER_LIFECYCLE_KIND,
        "lifecycle_record_id": None,
        "lifecycle_record_fingerprint": None,
        "domain": _safe_domain(safe.get("domain")),
        "lifecycle_stage": stage,
        "lifecycle_status": f"{stage}-runtime-disabled",
        "dossier_packet_id": _safe_preflight_packet_id(safe.get("packet_id")),
        "dossier_packet_fingerprint": _safe_sha256(safe.get("packet_fingerprint")),
        "preflight_status": _safe_preflight_status(safe.get("status")),
        "preflight_reviewed_gate_count": result.reviewed_gate_count,
        "preflight_missing_gate_count": result.missing_gate_count,
        "preflight_rejected_gate_count": result.rejected_gate_count,
        "blocking_reason_count": len(safe.get("blocking_reasons") or ()),
        "comparison": comparison,
        "reviewer_signoff": dict(safe_signoff),
        "audit_decision": dict(safe_decision),
        "signoff_count": 1,
        "decision_count": 1,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11d_record(payload, "lifecycle")


def phase11_dossier_lifecycle_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11D lifecycle/audit fixture examples."""

    missing = phase11_document_ingestion_preflight_dossier()
    missing_rf = phase11_wifi_csi_rf_booth_preflight_dossier()
    reviewed_doc = phase11_document_ingestion_preflight_dossier(
        phase11_document_ingestion_review_record()
    )
    reviewed_rf = phase11_wifi_csi_rf_booth_preflight_dossier(
        phase11_wifi_csi_rf_booth_review_record()
    )
    rejected = phase11_document_ingestion_preflight_dossier(
        phase11_rejected_review_record(
            domain=PHASE11_DOCUMENT_DOMAIN,
            rejected_gate="license-review",
        )
    )
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
        "fixture_kind": PHASE11_DOSSIER_LIFECYCLE_FIXTURE_KIND,
        "status": "lifecycle-audit-records-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "records": {
            "created": phase11_dossier_lifecycle_record(
                missing,
                lifecycle_stage=PHASE11_LIFECYCLE_STAGE_CREATED,
                signoff=phase11_reviewer_signoff_metadata(verdict=PHASE11_SIGNOFF_VERDICT_BLOCKERS),
                decision_record=phase11_dossier_decision_record(
                    missing,
                    decision=PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
                ),
            ),
            "reviewed": phase11_dossier_lifecycle_record(
                reviewed_doc,
                lifecycle_stage=PHASE11_LIFECYCLE_STAGE_REVIEWED,
                signoff=phase11_reviewer_signoff_metadata(
                    verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS
                ),
                decision_record=phase11_dossier_decision_record(
                    reviewed_doc,
                    decision=PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
                ),
            ),
            "superseded": phase11_dossier_lifecycle_record(
                reviewed_doc,
                lifecycle_stage=PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
                previous_dossier=missing,
                signoff=phase11_reviewer_signoff_metadata(
                    verdict=PHASE11_SIGNOFF_VERDICT_SUPERSEDED
                ),
                decision_record=phase11_dossier_decision_record(
                    reviewed_doc,
                    decision=PHASE11_LIFECYCLE_DECISION_BLOCKED,
                ),
            ),
            "rejected": phase11_dossier_lifecycle_record(
                rejected,
                lifecycle_stage=PHASE11_LIFECYCLE_STAGE_REJECTED,
                previous_dossier=missing,
                signoff=phase11_reviewer_signoff_metadata(verdict=PHASE11_SIGNOFF_VERDICT_REJECTED),
                decision_record=phase11_dossier_decision_record(
                    rejected,
                    decision=PHASE11_LIFECYCLE_DECISION_REJECTED,
                ),
            ),
            "archived": phase11_dossier_lifecycle_record(
                reviewed_doc,
                lifecycle_stage=PHASE11_LIFECYCLE_STAGE_ARCHIVED,
                previous_dossier=missing,
                signoff=phase11_reviewer_signoff_metadata(
                    verdict=PHASE11_SIGNOFF_VERDICT_SUPERSEDED
                ),
                decision_record=phase11_dossier_decision_record(
                    reviewed_doc,
                    decision=PHASE11_LIFECYCLE_DECISION_BLOCKED,
                ),
            ),
            "decision_recorded": phase11_dossier_lifecycle_record(
                reviewed_rf,
                lifecycle_stage=PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
                previous_dossier=missing_rf,
                signoff=phase11_reviewer_signoff_metadata(
                    verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS
                ),
                decision_record=phase11_dossier_decision_record(
                    reviewed_rf,
                    decision=(PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED),
                ),
            ),
        },
        "comparisons": {
            "missing_to_reviewed_document": phase11_compare_preflight_dossiers(
                missing,
                reviewed_doc,
            ),
            "missing_to_reviewed_rf_booth": phase11_compare_preflight_dossiers(
                missing_rf,
                reviewed_rf,
            ),
        },
    }


def phase11_dossier_lifecycle_status_summary(
    record: Mapping[str, object] | None = None,
    *,
    domain: str,
) -> dict[str, object]:
    """Return compact lifecycle/audit status safe for public surfaces."""

    built = (
        record
        if _looks_like_phase11_lifecycle_record(record)
        else phase11_dossier_lifecycle_record(
            _default_preflight_dossier_for_domain(_safe_domain(domain)),
            lifecycle_stage=PHASE11_LIFECYCLE_STAGE_CREATED,
            signoff=phase11_reviewer_signoff_metadata(verdict=PHASE11_SIGNOFF_VERDICT_BLOCKERS),
            decision_record=phase11_dossier_decision_record(
                _default_preflight_dossier_for_domain(_safe_domain(domain)),
                decision=PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
            ),
        )
    )
    result = validate_phase11_dossier_lifecycle_record(
        built,
        expected_domain=_safe_domain(domain),
    )
    safe = result.sanitized_record
    decision = safe.get("audit_decision") if isinstance(safe.get("audit_decision"), Mapping) else {}
    signoff = (
        safe.get("reviewer_signoff") if isinstance(safe.get("reviewer_signoff"), Mapping) else {}
    )
    comparison = safe.get("comparison") if isinstance(safe.get("comparison"), Mapping) else {}
    return {
        "schema_version": 1,
        "lifecycle_contract_version": PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
        "domain": _safe_domain(domain),
        "lifecycle_record_id": _safe_phase11d_record_id(safe.get("lifecycle_record_id")),
        "lifecycle_record_fingerprint": _safe_sha256(safe.get("lifecycle_record_fingerprint")),
        "lifecycle_stage": _safe_lifecycle_stage(safe.get("lifecycle_stage")),
        "lifecycle_status": _safe_phase11d_lifecycle_status(safe.get("lifecycle_status")),
        "audit_decision": _safe_lifecycle_decision(decision.get("decision")),
        "signoff_verdict": _safe_signoff_verdict(signoff.get("verdict")),
        "signoff_count": _safe_int(safe.get("signoff_count")),
        "decision_count": _safe_int(safe.get("decision_count")),
        "comparison_changed_field_count": _safe_int(comparison.get("changed_field_count")),
        "blocking_reason_count": _safe_int(safe.get("blocking_reason_count")),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_export_retention_policy(
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
    retention_label: str = PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY,
    export_class: str = PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY,
) -> dict[str, object]:
    """Return a local-only metadata export/retention policy record."""

    payload = {
        "schema_version": 1,
        "export_retention_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "export_retention_kind": PHASE11_EXPORT_RETENTION_POLICY_KIND,
        "policy_id": None,
        "policy_fingerprint": None,
        "domain": _safe_domain(domain),
        "retention_label": _safe_category(retention_label),
        "export_class": _safe_category(export_class),
        "local_only": True,
        "metadata_export_allowed": True,
        "deterministic_fixture_export_allowed": True,
        "payload_export_prohibited": True,
        "document_text_export_prohibited": True,
        "signal_export_prohibited": True,
        "origin_identifier_export_prohibited": True,
        "hardware_identifier_export_prohibited": True,
        "auth_material_export_prohibited": True,
        "path_export_prohibited": True,
        "url_export_prohibited": True,
        "model_artifact_payload_export_prohibited": True,
        "adapter_component_payload_export_prohibited": True,
        "external_upload_prohibited": True,
        "network_export_prohibited": True,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "policy")


def phase11_reviewer_scope_coverage_summary(
    lifecycle_record: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
    reviewer_scope_label: str = "planning-audit",
) -> dict[str, object]:
    """Return compact per-gate reviewer-scope coverage without identities."""

    record = (
        lifecycle_record
        if _looks_like_phase11_lifecycle_record(lifecycle_record)
        else phase11_dossier_lifecycle_record(
            _default_preflight_dossier_for_domain(_safe_domain(domain))
        )
    )
    result = validate_phase11_dossier_lifecycle_record(
        record,
        expected_domain=_safe_domain(domain),
    )
    safe = result.sanitized_record
    covered = (
        REAL_MODE_REQUIRED_GATES
        if result.compatible
        and _safe_int(safe.get("preflight_reviewed_gate_count")) == len(REAL_MODE_REQUIRED_GATES)
        and safe.get("preflight_status") == PHASE11_PREFLIGHT_STATUS_REVIEWED
        else ()
    )
    missing = tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate not in covered)
    scope_label = _safe_category(reviewer_scope_label) or "planning-audit"
    payload = {
        "schema_version": 1,
        "coverage_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "coverage_kind": PHASE11_REVIEWER_SCOPE_COVERAGE_KIND,
        "coverage_id": None,
        "coverage_fingerprint": None,
        "domain": _safe_domain(domain),
        "reviewer_scope_label": scope_label,
        "required_gates": list(REAL_MODE_REQUIRED_GATES),
        "covered_gates": list(covered),
        "missing_gates": list(missing),
        "gate_scope_labels": {
            gate: (scope_label if gate in covered else "planning-review-missing")
            for gate in REAL_MODE_REQUIRED_GATES
        },
        "coverage_complete": not missing,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "coverage")


def phase11_change_control_record(
    prior_record: Mapping[str, object] | None,
    current_record: Mapping[str, object] | None,
    *,
    change_reason: str = PHASE11_CHANGE_CONTROL_REASON,
    reviewer_scope_label: str = "planning-audit",
) -> dict[str, object]:
    """Return a deterministic change-control link between lifecycle records."""

    prior = _phase11_lifecycle_ref(prior_record)
    current = _phase11_lifecycle_ref(current_record)
    payload = {
        "schema_version": 1,
        "change_control_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "change_control_kind": PHASE11_CHANGE_CONTROL_KIND,
        "change_control_id": None,
        "change_control_fingerprint": None,
        "domain": current["domain"],
        "prior_lifecycle_record_label": prior["record_label"],
        "prior_lifecycle_record_fingerprint": prior["record_fingerprint"],
        "current_lifecycle_record_label": current["record_label"],
        "current_lifecycle_record_fingerprint": current["record_fingerprint"],
        "change_timestamp": "2026-06-09T00:00:00Z",
        "change_reason": _safe_category(change_reason),
        "reviewer_scope_label": _safe_category(reviewer_scope_label),
        "decision": current["decision"],
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "change")


def phase11_supersession_chain(
    lifecycle_records: tuple[Mapping[str, object], ...] | list[Mapping[str, object]],
    *,
    domain: str,
    cross_domain_allowed: bool = False,
) -> dict[str, object]:
    """Return a deterministic sanitized supersession chain."""

    refs = [
        ref
        for ref in (_phase11_lifecycle_ref(record) for record in lifecycle_records)
        if ref["domain"] == _safe_domain(domain) or cross_domain_allowed
    ]
    refs = sorted(
        refs,
        key=lambda ref: (
            _phase11_lifecycle_stage_order(ref["lifecycle_stage"]),
            ref["record_label"],
            ref["record_fingerprint"],
        ),
    )
    links: list[dict[str, object]] = []
    for index, ref in enumerate(refs):
        prior = refs[index - 1] if index else None
        future = refs[index + 1] if index + 1 < len(refs) else None
        links.append(
            {
                "position": index,
                "record_label": ref["record_label"],
                "record_fingerprint": ref["record_fingerprint"],
                "prior_record_label": prior["record_label"] if prior else "",
                "prior_record_fingerprint": (prior["record_fingerprint"] if prior else ""),
                "future_record_label": future["record_label"] if future else "",
                "future_record_fingerprint": (future["record_fingerprint"] if future else ""),
                "lifecycle_stage": ref["lifecycle_stage"],
                "decision": ref["decision"],
                "has_prior": prior is not None,
                "has_future": future is not None,
            }
        )
    payload = {
        "schema_version": 1,
        "supersession_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "supersession_chain_kind": PHASE11_SUPERSESSION_CHAIN_KIND,
        "chain_id": None,
        "chain_fingerprint": None,
        "domain": _safe_domain(domain),
        "chain_status": "single-record" if len(links) <= 1 else "linked-runtime-disabled",
        "cross_domain_allowed": bool(cross_domain_allowed),
        "record_count": len(links),
        "links": links,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "chain")


def phase11_audit_index(
    lifecycle_records: tuple[Mapping[str, object], ...] | list[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Build a deterministic Phase 11E audit-index/change-control record."""

    records = (
        tuple(lifecycle_records)
        if lifecycle_records is not None
        else (tuple(phase11_dossier_lifecycle_fixture_bundle()["records"].values()))
    )
    refs = [_phase11_lifecycle_ref(record) for record in records]
    entries = sorted(
        (_phase11_audit_index_entry(ref) for ref in refs),
        key=lambda entry: (
            str(entry["entry_label"]),
            str(entry["lifecycle_record_fingerprint"]),
        ),
    )
    document_records = tuple(
        record
        for record in records
        if _phase11_lifecycle_ref(record)["domain"] == PHASE11_DOCUMENT_DOMAIN
    )
    rf_records = tuple(
        record
        for record in records
        if _phase11_lifecycle_ref(record)["domain"] == PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN
    )
    domains_present = tuple(
        domain
        for domain in (PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN)
        if any(ref["domain"] == domain for ref in refs)
    )
    records_by_domain = {
        PHASE11_DOCUMENT_DOMAIN: document_records,
        PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN: rf_records,
    }
    coverage_records = []
    for domain in domains_present:
        preferred_stage = (
            PHASE11_LIFECYCLE_STAGE_REVIEWED
            if domain == PHASE11_DOCUMENT_DOMAIN
            else PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED
        )
        coverage_records.append(
            phase11_reviewer_scope_coverage_summary(
                _phase11_first_lifecycle_record(
                    records_by_domain[domain],
                    stage=preferred_stage,
                ),
                domain=domain,
            )
        )
    change_records = _phase11_default_change_control_records(document_records)
    chains = [
        phase11_supersession_chain(
            records_by_domain[domain],
            domain=domain,
        )
        for domain in domains_present
    ]
    policies = [phase11_export_retention_policy(domain=domain) for domain in domains_present]
    stage_counts = {
        stage: sum(1 for ref in refs if ref["lifecycle_stage"] == stage)
        for stage in PHASE11_LIFECYCLE_STAGE_VALUES
    }
    decision_counts = {
        decision: sum(1 for ref in refs if ref["decision"] == decision)
        for decision in PHASE11_LIFECYCLE_DECISION_VALUES
    }
    payload = {
        "schema_version": 1,
        "audit_index_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "audit_index_kind": PHASE11_AUDIT_INDEX_KIND,
        "index_id": None,
        "index_fingerprint": None,
        "domain_scope": "multi-domain",
        "status": PHASE11_AUDIT_INDEX_STATUS,
        "included_dossier_packet_labels": sorted(
            {str(entry["dossier_packet_label"]) for entry in entries}
        ),
        "included_lifecycle_record_labels": sorted(
            {str(entry["lifecycle_record_label"]) for entry in entries}
        ),
        "included_decision_record_labels": sorted(
            {str(entry["decision_record_label"]) for entry in entries}
        ),
        "included_record_fingerprints": sorted(
            {
                str(entry[field])
                for entry in entries
                for field in (
                    "dossier_packet_fingerprint",
                    "lifecycle_record_fingerprint",
                    "decision_record_fingerprint",
                )
            }
        ),
        "lifecycle_stage_counts": stage_counts,
        "decision_counts": decision_counts,
        "reviewer_scope_coverage": coverage_records,
        "supersession_chains": chains,
        "change_control_records": change_records,
        "export_retention_policies": policies,
        "entries": entries,
        "entry_count": len(entries),
        "created_count": stage_counts[PHASE11_LIFECYCLE_STAGE_CREATED],
        "reviewed_count": stage_counts[PHASE11_LIFECYCLE_STAGE_REVIEWED],
        "superseded_count": stage_counts[PHASE11_LIFECYCLE_STAGE_SUPERSEDED],
        "rejected_count": stage_counts[PHASE11_LIFECYCLE_STAGE_REJECTED],
        "archived_count": stage_counts[PHASE11_LIFECYCLE_STAGE_ARCHIVED],
        "decision_recorded_count": (stage_counts[PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED]),
        "blocking_count": sum(_safe_int(entry["blocking_reason_count"]) for entry in entries),
        "rejection_count": sum(
            1
            for entry in entries
            if entry["lifecycle_stage"] == PHASE11_LIFECYCLE_STAGE_REJECTED
            or entry["audit_decision"] == PHASE11_LIFECYCLE_DECISION_REJECTED
            or _safe_int(entry["rejected_gate_count"]) > 0
        ),
        "deterministic_ordering": "sanitized-label-hash-v1",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "index")


def phase11_audit_index_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11E audit-index/change-control fixtures."""

    index = phase11_audit_index()
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "fixture_kind": PHASE11_AUDIT_INDEX_FIXTURE_KIND,
        "status": "audit-index-change-control-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "audit_index": index,
        "change_control_records": index["change_control_records"],
        "supersession_chains": index["supersession_chains"],
        "reviewer_scope_coverage": index["reviewer_scope_coverage"],
        "export_retention_policies": index["export_retention_policies"],
    }


def phase11_audit_index_status_summary(
    index: Mapping[str, object] | None = None,
    *,
    domain: str | None = None,
) -> dict[str, object]:
    """Return compact Phase 11E status safe for public surfaces."""

    built = (
        index
        if _looks_like_phase11_audit_index(index)
        else phase11_audit_index(
            (
                phase11_dossier_lifecycle_record(
                    _default_preflight_dossier_for_domain(_safe_domain(domain)),
                ),
            )
            if domain
            else None
        )
    )
    result = validate_phase11_audit_index(built)
    safe = result.sanitized_record
    coverage = safe.get("reviewer_scope_coverage")
    chains = safe.get("supersession_chains")
    changes = safe.get("change_control_records")
    policies = safe.get("export_retention_policies")
    return {
        "schema_version": 1,
        "audit_index_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "domain_scope": _safe_category(safe.get("domain_scope")),
        "index_id": _safe_phase11e_record_id(safe.get("index_id")),
        "index_fingerprint": _safe_sha256(safe.get("index_fingerprint")),
        "status": _safe_audit_index_status(safe.get("status")),
        "entry_count": _safe_int(safe.get("entry_count")),
        "created_count": _safe_int(safe.get("created_count")),
        "reviewed_count": _safe_int(safe.get("reviewed_count")),
        "superseded_count": _safe_int(safe.get("superseded_count")),
        "rejected_count": _safe_int(safe.get("rejected_count")),
        "archived_count": _safe_int(safe.get("archived_count")),
        "decision_recorded_count": _safe_int(safe.get("decision_recorded_count")),
        "blocking_count": _safe_int(safe.get("blocking_count")),
        "rejection_count": _safe_int(safe.get("rejection_count")),
        "coverage_summary_count": len(coverage) if isinstance(coverage, list) else 0,
        "supersession_chain_count": len(chains) if isinstance(chains, list) else 0,
        "change_control_record_count": len(changes) if isinstance(changes, list) else 0,
        "export_retention_policy_count": len(policies) if isinstance(policies, list) else 0,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_audit_handoff_record(
    audit_index: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Build a compact Phase 11F handoff from sanitized Phase 11E metadata."""

    domain_label = _safe_domain(domain)
    if domain_label not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        return rejected_phase11_audit_handoff_record()
    built = audit_index if _looks_like_phase11_audit_index(audit_index) else phase11_audit_index()
    index_result = validate_phase11_audit_index(built)
    safe_index = index_result.sanitized_record
    entries = _phase11f_domain_entries(safe_index, domain_label)
    coverage = _phase11f_coverage_summary(safe_index, domain_label, entries)
    retention = _phase11f_retention_summary(safe_index, domain_label)
    lifecycle_counts = _phase11f_lifecycle_status_counts(entries)
    status = (
        PHASE11_AUDIT_HANDOFF_STATUS
        if index_result.compatible and entries
        else PHASE11_AUDIT_HANDOFF_REJECTED_STATUS
    )
    payload = {
        "schema_version": 1,
        "audit_handoff_contract_version": PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION,
        "audit_handoff_kind": PHASE11_AUDIT_HANDOFF_KIND,
        "handoff_id": None,
        "handoff_fingerprint": None,
        "domain": domain_label,
        "status": status,
        "contract_versions": _phase11f_contract_versions(),
        "audit_index_label": _safe_phase11e_record_id(safe_index.get("index_id")),
        "audit_index_fingerprint": _safe_sha256(safe_index.get("index_fingerprint")),
        "audit_index_status": _safe_audit_index_status(safe_index.get("status")),
        "audit_index_entry_count": len(entries),
        "lifecycle_status_counts": lifecycle_counts,
        "reviewer_scope_coverage_summary": coverage,
        "retention_export_policy_summary": retention,
        "blocking_count": sum(_safe_int(entry.get("blocking_reason_count")) for entry in entries),
        "rejection_count": sum(
            1
            for entry in entries
            if entry.get("lifecycle_stage") == PHASE11_LIFECYCLE_STAGE_REJECTED
            or entry.get("audit_decision") == PHASE11_LIFECYCLE_DECISION_REJECTED
            or _safe_int(entry.get("rejected_gate_count")) > 0
        ),
        "unresolved_review_count": sum(
            _safe_int(entry.get("missing_gate_count")) + _safe_int(entry.get("rejected_gate_count"))
            for entry in entries
        ),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11f_record(payload)


def phase11_audit_handoff_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11F compact audit handoff fixtures."""

    index = phase11_audit_index()
    handoffs = [
        phase11_audit_handoff_record(index, domain=PHASE11_DOCUMENT_DOMAIN),
        phase11_audit_handoff_record(index, domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN),
    ]
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION,
        "fixture_kind": PHASE11_AUDIT_HANDOFF_FIXTURE_KIND,
        "status": "audit-handoff-reporting-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "handoffs": handoffs,
    }


def phase11_audit_handoff_status_summary(
    audit_index: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Return compact Phase 11F handoff status safe for public surfaces."""

    handoff = phase11_audit_handoff_record(audit_index, domain=domain)
    result = validate_phase11_audit_handoff_record(handoff)
    safe = result.sanitized_record
    return {
        "schema_version": 1,
        "audit_handoff_contract_version": PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION,
        "domain": _safe_domain(safe.get("domain")),
        "handoff_id": _safe_phase11f_record_id(safe.get("handoff_id")),
        "handoff_fingerprint": _safe_sha256(safe.get("handoff_fingerprint")),
        "status": _safe_audit_handoff_status(safe.get("status")),
        "audit_index_label": _safe_phase11e_record_id(safe.get("audit_index_label")),
        "audit_index_fingerprint": _safe_sha256(safe.get("audit_index_fingerprint")),
        "audit_index_entry_count": _safe_int(safe.get("audit_index_entry_count")),
        "created_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("lifecycle_status_counts"),
                PHASE11_LIFECYCLE_STAGE_CREATED,
            )
        ),
        "reviewed_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("lifecycle_status_counts"),
                PHASE11_LIFECYCLE_STAGE_REVIEWED,
            )
        ),
        "superseded_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("lifecycle_status_counts"),
                PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
            )
        ),
        "rejected_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("lifecycle_status_counts"),
                PHASE11_LIFECYCLE_STAGE_REJECTED,
            )
        ),
        "archived_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("lifecycle_status_counts"),
                PHASE11_LIFECYCLE_STAGE_ARCHIVED,
            )
        ),
        "decision_recorded_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("lifecycle_status_counts"),
                PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
            )
        ),
        "coverage_required_gate_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("reviewer_scope_coverage_summary"),
                "required_gate_count",
            )
        ),
        "coverage_covered_gate_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("reviewer_scope_coverage_summary"),
                "covered_gate_count",
            )
        ),
        "coverage_missing_gate_count": _safe_int(
            _phase11f_count_from_mapping(
                safe.get("reviewer_scope_coverage_summary"),
                "missing_gate_count",
            )
        ),
        "blocking_count": _safe_int(safe.get("blocking_count")),
        "rejection_count": _safe_int(safe.get("rejection_count")),
        "unresolved_review_count": _safe_int(safe.get("unresolved_review_count")),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_handoff_acceptance_record(
    handoff: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
    source_handoff_hash: str | None = None,
) -> dict[str, object]:
    """Build a Phase 11G acceptance check from a sanitized Phase 11F handoff."""

    domain_label = _safe_domain(domain)
    if domain_label not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        return rejected_phase11_handoff_acceptance_record()
    if handoff is None:
        built = phase11_audit_handoff_record(domain=domain_label)
    elif _looks_like_phase11_audit_handoff(handoff):
        built = handoff
    else:
        return rejected_phase11_handoff_acceptance_record()
    handoff_result = validate_phase11_audit_handoff_record(built)
    safe_handoff = handoff_result.sanitized_record
    actual_handoff_hash = _safe_sha256(safe_handoff.get("handoff_fingerprint"))
    expected_handoff_hash = (
        _safe_sha256(source_handoff_hash) or "0" * 64
        if source_handoff_hash is not None
        else actual_handoff_hash
    )
    missing_review_count = _safe_int(
        _phase11f_count_from_mapping(
            safe_handoff.get("reviewer_scope_coverage_summary"),
            "missing_gate_count",
        )
    )
    unresolved_review_count = _safe_int(safe_handoff.get("unresolved_review_count"))
    rejection_count = _safe_int(safe_handoff.get("rejection_count"))
    blocking_count = _safe_int(safe_handoff.get("blocking_count"))
    stale = expected_handoff_hash != actual_handoff_hash
    rejection_reasons: list[str] = []
    blocking_reasons: list[str] = []
    if not handoff_result.compatible:
        rejection_reasons.append("source-handoff-validation-failed")
    if safe_handoff.get("status") == PHASE11_AUDIT_HANDOFF_REJECTED_STATUS:
        rejection_reasons.append("source-handoff-rejected")
    if rejection_count:
        rejection_reasons.append("source-handoff-rejection-count")
    if stale:
        blocking_reasons.append("source-handoff-hash-mismatch")
    if blocking_count:
        blocking_reasons.append("source-handoff-blockers")
    if missing_review_count:
        blocking_reasons.append("missing-review-coverage")
    if unresolved_review_count:
        blocking_reasons.append("unresolved-review-count")
    blocked = bool(blocking_reasons or rejection_reasons)
    accepted = (
        not blocked
        and not stale
        and handoff_result.compatible
        and safe_handoff.get("status") == PHASE11_AUDIT_HANDOFF_STATUS
    )
    if stale:
        status = PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS
    elif rejection_reasons:
        status = PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS
    elif blocked:
        status = PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS
    else:
        status = PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS
    payload = {
        "schema_version": 1,
        "handoff_acceptance_contract_version": (PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION),
        "handoff_acceptance_kind": PHASE11_HANDOFF_ACCEPTANCE_KIND,
        "acceptance_id": None,
        "acceptance_fingerprint": None,
        "domain": _safe_domain(safe_handoff.get("domain")) or domain_label,
        "status": status,
        "contract_versions": _phase11g_contract_versions(),
        "source_handoff_label": _safe_phase11f_record_id(safe_handoff.get("handoff_id")),
        "source_handoff_hash": expected_handoff_hash,
        "handoff_fingerprint": actual_handoff_hash,
        "handoff_status": _safe_audit_handoff_status(safe_handoff.get("status")),
        "accepted_for_planning": accepted,
        "blocked": blocked,
        "stale": stale,
        "missing_review_count": missing_review_count,
        "unresolved_review_count": unresolved_review_count,
        "rejection_reasons": sorted(set(rejection_reasons)),
        "blocking_reasons": sorted(set(blocking_reasons)),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11g_record(payload)


def phase11_handoff_acceptance_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11G handoff acceptance fixtures."""

    handoffs = phase11_audit_handoff_fixture_bundle()["handoffs"]
    blocked_document_lifecycle = phase11_dossier_lifecycle_record(
        phase11_document_ingestion_preflight_dossier(),
        lifecycle_stage=PHASE11_LIFECYCLE_STAGE_CREATED,
    )
    blocked_document_handoff = phase11_audit_handoff_record(
        phase11_audit_index((blocked_document_lifecycle,)),
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    rf_handoff = next(
        handoff for handoff in handoffs if handoff.get("domain") == PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN
    )
    acceptance_records = {
        "document_blocked": phase11_handoff_acceptance_record(
            blocked_document_handoff,
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        "rf_booth_accepted": phase11_handoff_acceptance_record(
            rf_handoff,
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        "rf_booth_stale": phase11_handoff_acceptance_record(
            rf_handoff,
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            source_handoff_hash="0" * 64,
        ),
        "rejected": phase11_handoff_acceptance_record(
            rejected_phase11_audit_handoff_record(),
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
    }
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION,
        "fixture_kind": PHASE11_HANDOFF_ACCEPTANCE_FIXTURE_KIND,
        "status": "handoff-acceptance-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "acceptance_records": acceptance_records,
    }


def phase11_handoff_acceptance_status_summary(
    handoff: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Return compact Phase 11G acceptance status safe for public surfaces."""

    acceptance = phase11_handoff_acceptance_record(handoff, domain=domain)
    result = validate_phase11_handoff_acceptance_record(acceptance)
    safe = result.sanitized_record
    return {
        "schema_version": 1,
        "handoff_acceptance_contract_version": (PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION),
        "domain": _safe_domain(safe.get("domain")),
        "acceptance_id": _safe_phase11g_record_id(safe.get("acceptance_id")),
        "acceptance_fingerprint": _safe_sha256(safe.get("acceptance_fingerprint")),
        "status": _safe_handoff_acceptance_status(safe.get("status")),
        "source_handoff_label": _safe_phase11f_record_id(safe.get("source_handoff_label")),
        "source_handoff_hash": _safe_sha256(safe.get("source_handoff_hash")),
        "handoff_fingerprint": _safe_sha256(safe.get("handoff_fingerprint")),
        "accepted_for_planning": bool(safe.get("accepted_for_planning")),
        "blocked": bool(safe.get("blocked")),
        "stale": bool(safe.get("stale")),
        "missing_review_count": _safe_int(safe.get("missing_review_count")),
        "unresolved_review_count": _safe_int(safe.get("unresolved_review_count")),
        "rejection_reason_count": len(safe.get("rejection_reasons") or ()),
        "blocking_reason_count": len(safe.get("blocking_reasons") or ()),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_acceptance_followup_record(
    acceptance: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
    followup_type: str | None = None,
) -> dict[str, object]:
    """Build a Phase 11H planning follow-up from sanitized Phase 11G metadata."""

    domain_label = _safe_domain(domain)
    if domain_label not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        return rejected_phase11_acceptance_followup_record()
    if acceptance is None:
        acceptance = _phase11h_default_acceptance_record(domain_label)
    if not _looks_like_phase11_handoff_acceptance(acceptance):
        return rejected_phase11_acceptance_followup_record()

    acceptance_result = validate_phase11_handoff_acceptance_record(acceptance)
    safe_acceptance = acceptance_result.sanitized_record
    accepted = bool(safe_acceptance.get("accepted_for_planning"))
    stale = bool(safe_acceptance.get("stale"))
    unresolved_count = _safe_int(safe_acceptance.get("unresolved_review_count"))
    blocking_count = len(safe_acceptance.get("blocking_reasons") or ())
    rejection_count = len(safe_acceptance.get("rejection_reasons") or ())
    source_rejected = (
        not acceptance_result.compatible
        or safe_acceptance.get("status") == PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS
    )
    if source_rejected and rejection_count == 0:
        rejection_count = 1
    normalized_type = _safe_acceptance_followup_type(followup_type)
    if normalized_type is None:
        normalized_type = _phase11h_default_followup_type(
            accepted=accepted,
            stale=stale,
            unresolved_count=unresolved_count,
            blocking_count=blocking_count,
            rejection_count=rejection_count,
        )
    status = _phase11h_followup_status(
        normalized_type,
        accepted=accepted,
        stale=stale,
        unresolved_count=unresolved_count,
        blocking_count=blocking_count,
        rejection_count=rejection_count,
        source_rejected=source_rejected,
    )
    payload = {
        "schema_version": 1,
        "acceptance_followup_contract_version": (PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION),
        "followup_kind": PHASE11_ACCEPTANCE_FOLLOWUP_KIND,
        "followup_id": None,
        "domain": _safe_domain(safe_acceptance.get("domain")) or domain_label,
        "followup_type": normalized_type,
        "status": status,
        "contract_versions": _phase11h_contract_versions(),
        "source_acceptance_label": _safe_phase11g_record_id(safe_acceptance.get("acceptance_id")),
        "source_acceptance_hash": _safe_sha256(safe_acceptance.get("acceptance_fingerprint"))
        or "0" * 64,
        "blocker_disposition_summary": _phase11h_blocker_summary(
            blocking_count=blocking_count,
            rejection_count=rejection_count,
            status=status,
        ),
        "reviewer_queue_summary": _phase11h_reviewer_summary(
            unresolved_count=unresolved_count,
            blocking_count=blocking_count,
            rejection_count=rejection_count,
            status=status,
        ),
        "stale_renewal_summary": _phase11h_stale_summary(
            stale=stale,
            blocking_count=blocking_count,
            status=status,
        ),
        "unresolved_review_count": unresolved_count,
        "blocking_count": blocking_count,
        "rejection_count": rejection_count,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11h_record(payload)


def phase11_acceptance_followup_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11H follow-up/remediation fixtures."""

    acceptances = phase11_handoff_acceptance_fixture_bundle()["acceptance_records"]
    document_blocked = acceptances["document_blocked"]
    rf_accepted = acceptances["rf_booth_accepted"]
    rf_stale = acceptances["rf_booth_stale"]
    rejected = acceptances["rejected"]
    followup_records = {
        "document_blocker_disposition": phase11_acceptance_followup_record(
            document_blocked,
            domain=PHASE11_DOCUMENT_DOMAIN,
            followup_type=PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE,
        ),
        "document_reviewer_queue": phase11_acceptance_followup_record(
            document_blocked,
            domain=PHASE11_DOCUMENT_DOMAIN,
            followup_type=PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE,
        ),
        "document_needs_more_review": phase11_acceptance_followup_record(
            document_blocked,
            domain=PHASE11_DOCUMENT_DOMAIN,
            followup_type=PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
        ),
        "rf_booth_resolved_for_planning": phase11_acceptance_followup_record(
            rf_accepted,
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            followup_type=PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE,
        ),
        "rf_booth_stale_renewal": phase11_acceptance_followup_record(
            rf_stale,
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            followup_type=PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE,
        ),
        "rf_booth_archived_no_action": phase11_acceptance_followup_record(
            rf_accepted,
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            followup_type=PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE,
        ),
        "rejected": phase11_acceptance_followup_record(
            rejected,
            domain=PHASE11_DOCUMENT_DOMAIN,
            followup_type=PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
        ),
    }
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION,
        "fixture_kind": PHASE11_ACCEPTANCE_FOLLOWUP_FIXTURE_KIND,
        "status": "followup-remediation-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "followup_records": followup_records,
    }


def phase11_acceptance_followup_status_summary(
    acceptance: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
    followup_type: str | None = None,
) -> dict[str, object]:
    """Return compact Phase 11H follow-up status safe for public surfaces."""

    followup = phase11_acceptance_followup_record(
        acceptance,
        domain=domain,
        followup_type=followup_type,
    )
    result = validate_phase11_acceptance_followup_record(followup)
    safe = result.sanitized_record
    return {
        "schema_version": 1,
        "acceptance_followup_contract_version": (PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION),
        "domain": _safe_domain(safe.get("domain")),
        "followup_id": _safe_phase11h_record_id(safe.get("followup_id")),
        "followup_type": _safe_acceptance_followup_type(safe.get("followup_type"))
        or PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
        "status": _safe_acceptance_followup_status(safe.get("status")),
        "contract_versions": _phase11h_contract_versions(),
        "source_acceptance_label": _safe_phase11g_record_id(safe.get("source_acceptance_label")),
        "source_acceptance_hash": _safe_sha256(safe.get("source_acceptance_hash")),
        "blocker_disposition_summary": _safe_acceptance_followup_blocker_summary(
            safe.get("blocker_disposition_summary")
        ),
        "reviewer_queue_summary": _safe_acceptance_followup_reviewer_summary(
            safe.get("reviewer_queue_summary")
        ),
        "stale_renewal_summary": _safe_acceptance_followup_stale_summary(
            safe.get("stale_renewal_summary")
        ),
        "unresolved_review_count": _safe_int(safe.get("unresolved_review_count")),
        "blocking_count": _safe_int(safe.get("blocking_count")),
        "rejection_count": _safe_int(safe.get("rejection_count")),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_followup_queue_index_record(
    followups: Mapping[str, object] | tuple[object, ...] | list[object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Build a Phase 11I reviewer queue index from sanitized Phase 11H records."""

    domain_label = _safe_domain(domain)
    if domain_label not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
        return rejected_phase11_followup_queue_index()
    safe_followups = _phase11i_sanitized_followups(followups, domain=domain_label)
    if not safe_followups:
        return rejected_phase11_followup_queue_index()
    return _phase11i_queue_index_from_followups(safe_followups, domain=domain_label)


def phase11_followup_queue_acceptance_check(
    queue_index: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return a compact Phase 11I queue acceptance check without runtime authority."""

    if queue_index is None:
        queue_index = phase11_followup_queue_index_record(domain=PHASE11_DOCUMENT_DOMAIN)
    queue_result = validate_phase11_followup_queue_index_record(queue_index)
    queue = queue_result.sanitized_record
    payload = {
        "schema_version": 1,
        "queue_index_contract_version": (PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION),
        "queue_acceptance_kind": PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_KIND,
        "acceptance_id": None,
        "acceptance_fingerprint": None,
        "queue_label": _safe_phase11i_queue_id(queue.get("queue_id")),
        "queue_fingerprint": _safe_sha256(queue.get("queue_fingerprint")),
        "domain": _safe_domain(queue.get("domain")),
        "status": _safe_followup_queue_status(queue.get("status")),
        "contract_versions": _phase11i_contract_versions(),
        "queue_status_counts": _phase11i_status_counts(queue.get("queue_status_counts")),
        "entry_count": _safe_int(queue.get("entry_count")),
        "unresolved_review_count": _safe_int(queue.get("unresolved_review_count")),
        "blocking_count": _safe_int(queue.get("blocking_count")),
        "stale_count": _safe_int(queue.get("stale_count")),
        "archived_count": _safe_int(queue.get("archived_count")),
        "rejected_count": _safe_int(queue.get("rejected_count")),
        "resolved_for_planning_count": _safe_int(queue.get("resolved_for_planning_count")),
        "reviewer_queue_count": _safe_int(queue.get("reviewer_queue_count")),
        "blocker_disposition_count": _safe_int(queue.get("blocker_disposition_count")),
        "needs_more_review_count": _safe_int(queue.get("needs_more_review_count")),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11i_acceptance_check(payload)


def phase11_followup_queue_index_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11I queue index and acceptance fixtures."""

    followups = phase11_acceptance_followup_fixture_bundle()["followup_records"]
    queue_index_records = {
        "document_ingestion_queue": phase11_followup_queue_index_record(
            followups,
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        "rf_booth_queue": phase11_followup_queue_index_record(
            followups,
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
    }
    queue_acceptance_checks = {
        "accepted_for_planning_queue": phase11_followup_queue_acceptance_check(
            phase11_followup_queue_index_record(
                (followups["rf_booth_resolved_for_planning"],),
                domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            )
        ),
        "blocked_queue": phase11_followup_queue_acceptance_check(
            phase11_followup_queue_index_record(
                (followups["document_blocker_disposition"],),
                domain=PHASE11_DOCUMENT_DOMAIN,
            )
        ),
        "stale_queue": phase11_followup_queue_acceptance_check(
            phase11_followup_queue_index_record(
                (followups["rf_booth_stale_renewal"],),
                domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            )
        ),
        "rejected_queue": phase11_followup_queue_acceptance_check(
            phase11_followup_queue_index_record(
                (followups["rejected"],),
                domain="unknown",
            )
        ),
        "archived_no_action": phase11_followup_queue_acceptance_check(
            phase11_followup_queue_index_record(
                (followups["rf_booth_archived_no_action"],),
                domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            )
        ),
        "needs_more_review": phase11_followup_queue_acceptance_check(
            phase11_followup_queue_index_record(
                (followups["document_needs_more_review"],),
                domain=PHASE11_DOCUMENT_DOMAIN,
            )
        ),
    }
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION,
        "fixture_kind": PHASE11_FOLLOWUP_QUEUE_FIXTURE_KIND,
        "status": "followup-queue-index-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "queue_index_records": queue_index_records,
        "queue_acceptance_checks": queue_acceptance_checks,
    }


def phase11_followup_queue_index_status_summary(
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Return compact Phase 11I queue/index status safe for public surfaces."""

    queue = phase11_followup_queue_index_record(domain=domain)
    result = validate_phase11_followup_queue_index_record(queue)
    safe = result.sanitized_record
    acceptance = phase11_followup_queue_acceptance_check(safe)
    acceptance_result = validate_phase11_followup_queue_acceptance_check(acceptance)
    safe_acceptance = acceptance_result.sanitized_record
    return {
        "schema_version": 1,
        "queue_index_contract_version": PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION,
        "domain": _safe_domain(safe.get("domain")),
        "queue_id": _safe_phase11i_queue_id(safe.get("queue_id")),
        "queue_fingerprint": _safe_sha256(safe.get("queue_fingerprint")),
        "status": _safe_followup_queue_status(safe.get("status")),
        "acceptance_status": _safe_followup_queue_status(safe_acceptance.get("status")),
        "acceptance_id": _safe_phase11i_acceptance_id(safe_acceptance.get("acceptance_id")),
        "acceptance_fingerprint": _safe_sha256(safe_acceptance.get("acceptance_fingerprint")),
        "contract_versions": _phase11i_contract_versions(),
        "included_followup_labels": [
            _safe_phase11h_record_id(label) for label in safe.get("included_followup_labels", [])
        ],
        "included_followup_hashes": [
            _safe_sha256(item) for item in safe.get("included_followup_hashes", [])
        ],
        "queue_status_counts": _phase11i_status_counts(safe.get("queue_status_counts")),
        "blocker_disposition_counts": _phase11i_summary_counts(
            safe.get("blocker_disposition_counts"),
            PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_SUMMARIES,
        ),
        "reviewer_queue_counts": _phase11i_summary_counts(
            safe.get("reviewer_queue_counts"),
            PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_SUMMARIES,
        ),
        "stale_renewal_counts": _phase11i_summary_counts(
            safe.get("stale_renewal_counts"),
            PHASE11_ACCEPTANCE_FOLLOWUP_STALE_SUMMARIES,
        ),
        "entry_count": _safe_int(safe.get("entry_count")),
        "open_count": _safe_int(safe.get("open_count")),
        "blocked_count": _safe_int(safe.get("blocked_count")),
        "stale_count": _safe_int(safe.get("stale_count")),
        "unresolved_review_count": _safe_int(safe.get("unresolved_review_count")),
        "blocking_count": _safe_int(safe.get("blocking_count")),
        "blocker_disposition_count": _safe_int(safe.get("blocker_disposition_count")),
        "reviewer_queue_count": _safe_int(safe.get("reviewer_queue_count")),
        "stale_renewal_count": _safe_int(safe.get("stale_renewal_count")),
        "needs_more_review_count": _safe_int(safe.get("needs_more_review_count")),
        "archived_count": _safe_int(safe.get("archived_count")),
        "rejected_count": _safe_int(safe.get("rejected_count")),
        "resolved_for_planning_count": _safe_int(safe.get("resolved_for_planning_count")),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_decision_closeout_record(
    queue_index: Mapping[str, object] | None = None,
    queue_acceptance: Mapping[str, object] | None = None,
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Build a Phase 11J closeout record from sanitized Phase 11I records only."""

    if queue_index is None:
        queue_index = phase11_followup_queue_index_record(domain=domain)
    queue_result = validate_phase11_followup_queue_index_record(queue_index)
    if not queue_result.compatible:
        return rejected_phase11_decision_closeout_record()
    queue = queue_result.sanitized_record

    if queue_acceptance is None:
        queue_acceptance = phase11_followup_queue_acceptance_check(queue)
    acceptance_result = validate_phase11_followup_queue_acceptance_check(queue_acceptance)
    if not acceptance_result.compatible:
        return rejected_phase11_decision_closeout_record()
    acceptance = acceptance_result.sanitized_record

    if not _phase11j_queue_acceptance_matches_index(queue, acceptance):
        return rejected_phase11_decision_closeout_record()

    decision = _phase11j_decision_from_source_queue(acceptance)
    payload = {
        "schema_version": 1,
        "closeout_contract_version": PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION,
        "closeout_id": None,
        "contract_versions": _phase11j_contract_versions(),
        "domain": _safe_domain(queue.get("domain")),
        "source_queue_label": _safe_phase11i_queue_id(acceptance.get("queue_label")),
        "source_queue_hash": _safe_sha256(acceptance.get("queue_fingerprint")),
        "closeout_decision": decision,
        "closeout_status": _phase11j_status_from_decision(decision),
        "reviewer_disposition_summary": (_phase11j_reviewer_disposition_summary(decision)),
        "unresolved_review_count": _safe_int(acceptance.get("unresolved_review_count")),
        "blocker_count": _safe_int(acceptance.get("blocking_count")),
        "stale_count": _safe_int(acceptance.get("stale_count")),
        "archived_count": _safe_int(acceptance.get("archived_count")),
        "rejected_count": _safe_int(acceptance.get("rejected_count")),
        "deferred_count": _safe_int(acceptance.get("stale_count")),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11j_closeout(payload)


def phase11_decision_closeout_fixture_bundle() -> dict[str, object]:
    """Return deterministic Phase 11J decision-closeout fixtures."""

    phase11i = phase11_followup_queue_index_fixture_bundle()
    queues = phase11i["queue_index_records"]
    closeout_records = {
        "document_ingestion_closeout": phase11_decision_closeout_record(
            queues["document_ingestion_queue"],
        ),
        "rf_booth_closeout": phase11_decision_closeout_record(
            queues["rf_booth_queue"],
        ),
    }
    return {
        "schema_version": 1,
        "fixture_contract_version": PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION,
        "fixture_kind": PHASE11_DECISION_CLOSEOUT_FIXTURE_KIND,
        "status": "decision-closeout-runtime-disabled",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "decision_closeout_records": closeout_records,
    }


def phase11_decision_closeout_status_summary(
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Return compact Phase 11J closeout status safe for public surfaces."""

    closeout = phase11_decision_closeout_record(domain=domain)
    result = validate_phase11_decision_closeout_record(closeout)
    safe = result.sanitized_record
    return {
        "schema_version": 1,
        "closeout_contract_version": PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION,
        "domain": _safe_domain(safe.get("domain")),
        "closeout_id": _safe_phase11j_closeout_id(safe.get("closeout_id")),
        "contract_versions": _phase11j_contract_versions(),
        "source_queue_label": _safe_phase11i_queue_id(safe.get("source_queue_label")),
        "source_queue_hash": _safe_sha256(safe.get("source_queue_hash")),
        "closeout_decision": _safe_phase11j_decision(safe.get("closeout_decision")),
        "closeout_status": _safe_phase11j_status(safe.get("closeout_status")),
        "reviewer_disposition_summary": _safe_phase11j_reviewer_summary(
            safe.get("reviewer_disposition_summary")
        ),
        "unresolved_review_count": _safe_int(safe.get("unresolved_review_count")),
        "blocker_count": _safe_int(safe.get("blocker_count")),
        "stale_count": _safe_int(safe.get("stale_count")),
        "archived_count": _safe_int(safe.get("archived_count")),
        "rejected_count": _safe_int(safe.get("rejected_count")),
        "deferred_count": _safe_int(safe.get("deferred_count")),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_review_trail_export_bundle(
    closeout_summaries: tuple[Mapping[str, object], ...] | None = None,
) -> dict[str, object]:
    """Return a deterministic Phase 11K review-trail export over 11A-11J."""

    summaries = closeout_summaries or (
        phase11_decision_closeout_status_summary(domain=PHASE11_DOCUMENT_DOMAIN),
        phase11_decision_closeout_status_summary(domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN),
    )
    domain_closeouts = [_phase11k_domain_closeout_summary(summary) for summary in summaries]
    domain_labels = [_safe_domain(item.get("domain_label")) for item in domain_closeouts]
    payload = {
        "review_trail_export_contract_version": (PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION),
        "export_id": None,
        "phase_range": PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE,
        "covered_phase_count": PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT,
        "domain_labels": domain_labels,
        "domain_closeouts": domain_closeouts,
        "readiness_gap_summary": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    export = _finalize_phase11k_review_trail_export(payload)
    result = validate_phase11_review_trail_export_bundle(export)
    return export if result.compatible else rejected_phase11_review_trail_export_bundle()


def phase11_review_trail_export_status_summary(
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Return compact Phase 11K export status safe for public surfaces."""

    export = phase11_review_trail_export_bundle()
    result = validate_phase11_review_trail_export_bundle(export)
    safe = result.sanitized_record
    safe_domain = _safe_domain(domain)
    domain_closeout = _phase11k_domain_closeout_for(
        safe.get("domain_closeouts"),
        safe_domain,
    )
    return {
        "review_trail_export_contract_version": (PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION),
        "export_id": _safe_phase11k_export_id(safe.get("export_id")),
        "phase_range": PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE,
        "covered_phase_count": PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT,
        "domain_label": _safe_domain(domain_closeout.get("domain_label")),
        "final_closeout_decision": _safe_phase11j_decision(
            domain_closeout.get("final_closeout_decision")
        ),
        "final_closeout_status": _safe_phase11j_status(
            domain_closeout.get("final_closeout_status")
        ),
        "unresolved_review_count": _safe_int(domain_closeout.get("unresolved_review_count")),
        "blocker_count": _safe_int(domain_closeout.get("blocker_count")),
        "stale_count": _safe_int(domain_closeout.get("stale_count")),
        "readiness_gap_summary": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_runtime_authorization_gap_ledger(
    review_trail_export: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return a Phase 11L planning-only runtime authorization gap ledger."""

    export = review_trail_export or phase11_review_trail_export_bundle()
    export_result = validate_phase11_review_trail_export_bundle(export)
    safe_export = (
        export_result.sanitized_record
        if export_result.compatible
        else rejected_phase11_review_trail_export_bundle()
    )
    domain_summaries = [
        _phase11l_domain_gap_summary(summary) for summary in safe_export.get("domain_closeouts", [])
    ]
    payload = {
        "runtime_authorization_gap_ledger_contract_version": (
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION
        ),
        "ledger_id": None,
        "source_phase_range": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE),
        "covered_phase_count": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT),
        "domain_labels": _phase11k_domain_labels(),
        "domain_gap_summaries": domain_summaries,
        "authorization_status": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS),
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "missing_future_gates": list(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
        "missing_future_gate_count": len(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    ledger = _finalize_phase11l_runtime_gap_ledger(payload)
    result = validate_phase11_runtime_authorization_gap_ledger(ledger)
    return ledger if result.compatible else rejected_phase11_runtime_authorization_gap_ledger()


def phase11_runtime_authorization_gap_ledger_status_summary(
    *,
    domain: str = PHASE11_DOCUMENT_DOMAIN,
) -> dict[str, object]:
    """Return compact Phase 11L ledger status safe for public surfaces."""

    ledger = phase11_runtime_authorization_gap_ledger()
    result = validate_phase11_runtime_authorization_gap_ledger(ledger)
    safe = result.sanitized_record
    domain_summary = _phase11l_domain_gap_for(
        safe.get("domain_gap_summaries"),
        _safe_domain(domain),
    )
    return {
        "runtime_authorization_gap_ledger_contract_version": (
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION
        ),
        "ledger_id": _safe_phase11l_ledger_id(safe.get("ledger_id")),
        "source_phase_range": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE),
        "covered_phase_count": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT),
        "domain_label": _safe_domain(domain_summary.get("domain_label")),
        "authorization_status": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS),
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "missing_future_gate_count": _safe_int(safe.get("missing_future_gate_count")),
        "unresolved_review_count": _safe_int(domain_summary.get("unresolved_review_count")),
        "blocker_count": _safe_int(domain_summary.get("blocker_count")),
        "stale_count": _safe_int(domain_summary.get("stale_count")),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_planning_governance_closeout_index(
    runtime_gap_ledger: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return a Phase 11M planning/governance closeout index."""

    ledger = runtime_gap_ledger or phase11_runtime_authorization_gap_ledger()
    ledger_result = validate_phase11_runtime_authorization_gap_ledger(ledger)
    safe_ledger = (
        ledger_result.sanitized_record
        if ledger_result.compatible
        else rejected_phase11_runtime_authorization_gap_ledger()
    )
    domain_summaries = safe_ledger.get("domain_gap_summaries")
    payload = {
        "planning_governance_closeout_contract_version": (
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION
        ),
        "closeout_index_id": None,
        "phase_range": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
        "covered_phase_count": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT,
        "final_status": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
        "runtime_authorization_status": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS),
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "next_phase_requirement": (PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_NEXT_PHASE_REQUIREMENT),
        "gap_ledger_id": _safe_phase11l_ledger_id(safe_ledger.get("ledger_id")),
        "gap_ledger_contract_version": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION),
        "gap_ledger_phase_range": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE),
        "domain_labels": _phase11k_domain_labels(),
        "domain_count": len(_phase11k_domain_labels()),
        "unresolved_review_count": _phase11m_count_total(
            domain_summaries,
            "unresolved_review_count",
        ),
        "blocker_count": _phase11m_count_total(domain_summaries, "blocker_count"),
        "stale_count": _phase11m_count_total(domain_summaries, "stale_count"),
        "missing_future_gate_count": _safe_int(safe_ledger.get("missing_future_gate_count")),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    closeout = _finalize_phase11m_governance_closeout(payload)
    result = validate_phase11_planning_governance_closeout_index(closeout)
    return closeout if result.compatible else rejected_phase11_planning_governance_closeout_index()


def phase11_planning_governance_closeout_status_summary() -> dict[str, object]:
    """Return compact Phase 11M closeout status safe for public surfaces."""

    closeout = phase11_planning_governance_closeout_index()
    result = validate_phase11_planning_governance_closeout_index(closeout)
    safe = result.sanitized_record
    return {
        "planning_governance_closeout_contract_version": (
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION
        ),
        "closeout_index_id": _safe_phase11m_closeout_id(safe.get("closeout_index_id")),
        "phase_range": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
        "covered_phase_count": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT,
        "final_status": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
        "runtime_authorization_status": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS),
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "next_phase_requirement": (PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_NEXT_PHASE_REQUIREMENT),
        "gap_ledger_id": _safe_phase11l_ledger_id(safe.get("gap_ledger_id")),
        "domain_count": _safe_int(safe.get("domain_count")),
        "unresolved_review_count": _safe_int(safe.get("unresolved_review_count")),
        "blocker_count": _safe_int(safe.get("blocker_count")),
        "stale_count": _safe_int(safe.get("stale_count")),
        "missing_future_gate_count": _safe_int(safe.get("missing_future_gate_count")),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase11_reviewer_signoff_metadata(
    signoff: object,
) -> Phase11LifecycleAuditValidationResult:
    """Validate Phase 11D reviewer signoff metadata and fail closed."""

    if not isinstance(signoff, Mapping):
        return _invalid_phase11d_result(
            ("phase11d_signoff_not_object",),
            "malformed",
            rejected_phase11_reviewer_signoff_metadata(),
        )
    privacy_violations = _privacy_violation_count(signoff)
    errors: list[str] = []
    if PHASE11_SIGNOFF_REQUIRED_FIELDS - set(signoff):
        errors.append("phase11d_signoff_required_field_missing")
    if set(str(key) for key in signoff) - PHASE11_SIGNOFF_ALLOWED_FIELDS:
        errors.append("phase11d_signoff_unknown_field")
    if signoff.get("schema_version") != 1:
        errors.append("phase11d_signoff_schema_version_invalid")
    version = signoff.get("signoff_contract_version")
    if version != PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION:
        classification = "unsupported_version" if isinstance(version, int) else "malformed"
        return _invalid_phase11d_result(
            ("phase11d_signoff_contract_version_unsupported",),
            classification,
            rejected_phase11_reviewer_signoff_metadata(),
            privacy_violation_count=privacy_violations,
        )
    if signoff.get("signoff_kind") != PHASE11_REVIEWER_SIGNOFF_KIND:
        errors.append("phase11d_signoff_kind_invalid")
    if _safe_phase11d_label(signoff.get("reviewer_label")) != signoff.get("reviewer_label"):
        errors.append("phase11d_signoff_reviewer_label_invalid")
    if not _looks_phase11d_timestamp(signoff.get("review_timestamp")):
        errors.append("phase11d_signoff_timestamp_invalid")
    if _safe_signoff_verdict(signoff.get("verdict")) != signoff.get("verdict"):
        errors.append("phase11d_signoff_verdict_invalid")
    if privacy_violations:
        errors.append("phase11d_signoff_privacy_boundary")
    _phase11_required_runtime_disabled_errors(signoff, errors, "phase11d_signoff")
    expected = _phase11d_record_fingerprint(signoff, "signoff")
    if not _looks_sha256(expected):
        errors.append("phase11d_signoff_payload_not_json")
    else:
        if signoff.get("signoff_fingerprint") != expected:
            errors.append("phase11d_signoff_fingerprint_invalid")
        expected_id = f"p11d-signoff-{expected[:16]}"
        if signoff.get("signoff_id") != expected_id:
            errors.append("phase11d_signoff_id_invalid")
    if errors:
        return _invalid_phase11d_result(
            tuple(sorted(set(errors))),
            "incompatible",
            rejected_phase11_reviewer_signoff_metadata(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11LifecycleAuditValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(signoff),
    )


def validate_phase11_dossier_decision_record(
    decision_record: object,
    *,
    expected_domain: str | None = None,
) -> Phase11LifecycleAuditValidationResult:
    """Validate a Phase 11D non-runtime dossier decision record."""

    if not isinstance(decision_record, Mapping):
        return _invalid_phase11d_result(
            ("phase11d_decision_not_object",),
            "malformed",
            rejected_phase11_dossier_decision_record(),
        )
    privacy_violations = _privacy_violation_count(decision_record)
    errors: list[str] = []
    if PHASE11_DECISION_REQUIRED_FIELDS - set(decision_record):
        errors.append("phase11d_decision_required_field_missing")
    if set(str(key) for key in decision_record) - PHASE11_DECISION_ALLOWED_FIELDS:
        errors.append("phase11d_decision_unknown_field")
    if decision_record.get("schema_version") != 1:
        errors.append("phase11d_decision_schema_version_invalid")
    version = decision_record.get("decision_contract_version")
    if version != PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION:
        classification = "unsupported_version" if isinstance(version, int) else "malformed"
        return _invalid_phase11d_result(
            ("phase11d_decision_contract_version_unsupported",),
            classification,
            rejected_phase11_dossier_decision_record(),
            privacy_violation_count=privacy_violations,
        )
    if decision_record.get("decision_kind") != PHASE11_DOSSIER_DECISION_KIND:
        errors.append("phase11d_decision_kind_invalid")
    domain = _safe_domain(decision_record.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11d_decision_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11d_decision_domain_mismatch")
    if _safe_preflight_packet_id(decision_record.get("dossier_packet_id")) != decision_record.get(
        "dossier_packet_id"
    ):
        errors.append("phase11d_decision_packet_id_invalid")
    if not _looks_sha256(decision_record.get("dossier_packet_fingerprint")):
        errors.append("phase11d_decision_packet_fingerprint_invalid")
    if _safe_lifecycle_decision(decision_record.get("decision")) != decision_record.get("decision"):
        errors.append("phase11d_decision_value_invalid")
    if _safe_category(decision_record.get("decision_reason")) != decision_record.get(
        "decision_reason"
    ):
        errors.append("phase11d_decision_reason_invalid")
    if privacy_violations:
        errors.append("phase11d_decision_privacy_boundary")
    _phase11_required_runtime_disabled_errors(decision_record, errors, "phase11d_decision")
    expected = _phase11d_record_fingerprint(decision_record, "decision")
    if not _looks_sha256(expected):
        errors.append("phase11d_decision_payload_not_json")
    else:
        if decision_record.get("decision_fingerprint") != expected:
            errors.append("phase11d_decision_fingerprint_invalid")
        expected_id = f"p11d-decision-{expected[:16]}"
        if decision_record.get("decision_id") != expected_id:
            errors.append("phase11d_decision_id_invalid")
    if errors:
        return _invalid_phase11d_result(
            tuple(sorted(set(errors))),
            "incompatible",
            rejected_phase11_dossier_decision_record(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11LifecycleAuditValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(decision_record),
    )


def validate_phase11_dossier_lifecycle_record(
    record: object,
    *,
    expected_domain: str | None = None,
) -> Phase11LifecycleAuditValidationResult:
    """Validate a Phase 11D lifecycle/audit record and fail closed."""

    if not isinstance(record, Mapping):
        return _invalid_phase11d_result(
            ("phase11d_lifecycle_not_object",),
            "malformed",
            rejected_phase11_dossier_lifecycle_record(),
        )
    privacy_violations = _privacy_violation_count(record)
    errors: list[str] = []
    if PHASE11_LIFECYCLE_REQUIRED_FIELDS - set(record):
        errors.append("phase11d_lifecycle_required_field_missing")
    if set(str(key) for key in record) - PHASE11_LIFECYCLE_ALLOWED_FIELDS:
        errors.append("phase11d_lifecycle_unknown_field")
    if record.get("schema_version") != 1:
        errors.append("phase11d_lifecycle_schema_version_invalid")
    version = record.get("lifecycle_contract_version")
    if version != PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION:
        classification = "unsupported_version" if isinstance(version, int) else "malformed"
        return _invalid_phase11d_result(
            ("phase11d_lifecycle_contract_version_unsupported",),
            classification,
            rejected_phase11_dossier_lifecycle_record(),
            privacy_violation_count=privacy_violations,
        )
    if record.get("lifecycle_record_kind") != PHASE11_DOSSIER_LIFECYCLE_KIND:
        errors.append("phase11d_lifecycle_kind_invalid")
    domain = _safe_domain(record.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11d_lifecycle_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11d_lifecycle_domain_mismatch")
    stage = _safe_lifecycle_stage(record.get("lifecycle_stage"))
    if stage != record.get("lifecycle_stage"):
        errors.append("phase11d_lifecycle_stage_invalid")
    if record.get("lifecycle_status") != f"{stage}-runtime-disabled":
        errors.append("phase11d_lifecycle_status_contradiction")
    if _safe_preflight_packet_id(record.get("dossier_packet_id")) != record.get(
        "dossier_packet_id"
    ):
        errors.append("phase11d_lifecycle_packet_id_invalid")
    if not _looks_sha256(record.get("dossier_packet_fingerprint")):
        errors.append("phase11d_lifecycle_packet_fingerprint_invalid")
    preflight_status = _safe_preflight_status(record.get("preflight_status"))
    if preflight_status != record.get("preflight_status"):
        errors.append("phase11d_lifecycle_preflight_status_invalid")
    if _safe_int(record.get("preflight_reviewed_gate_count")) + _safe_int(
        record.get("preflight_missing_gate_count")
    ) + _safe_int(record.get("preflight_rejected_gate_count")) != len(REAL_MODE_REQUIRED_GATES):
        errors.append("phase11d_lifecycle_gate_count_contradiction")
    signoff_result = validate_phase11_reviewer_signoff_metadata(record.get("reviewer_signoff"))
    decision_result = validate_phase11_dossier_decision_record(
        record.get("audit_decision"),
        expected_domain=domain,
    )
    if not signoff_result.compatible:
        errors.append("phase11d_lifecycle_signoff_invalid")
    if not decision_result.compatible:
        errors.append("phase11d_lifecycle_decision_invalid")
    comparison_errors = _phase11d_comparison_errors(
        record.get("comparison"),
        expected_domain=domain,
    )
    errors.extend(comparison_errors)
    if record.get("signoff_count") != 1 or record.get("decision_count") != 1:
        errors.append("phase11d_lifecycle_audit_count_contradiction")
    if privacy_violations:
        errors.append("phase11d_lifecycle_privacy_boundary")
    _phase11_required_runtime_disabled_errors(record, errors, "phase11d_lifecycle")
    if isinstance(record.get("audit_decision"), Mapping) and isinstance(
        record.get("reviewer_signoff"), Mapping
    ):
        decision = record["audit_decision"].get("decision")
        verdict = record["reviewer_signoff"].get("verdict")
        errors.extend(
            _phase11d_lifecycle_contradictions(
                stage=stage,
                decision=str(decision or ""),
                verdict=str(verdict or ""),
                preflight_status=preflight_status,
                reviewed_count=_safe_int(record.get("preflight_reviewed_gate_count")),
            )
        )
    expected = _phase11d_record_fingerprint(record, "lifecycle")
    if not _looks_sha256(expected):
        errors.append("phase11d_lifecycle_payload_not_json")
    else:
        if record.get("lifecycle_record_fingerprint") != expected:
            errors.append("phase11d_lifecycle_fingerprint_invalid")
        expected_id = f"p11d-lifecycle-{expected[:16]}"
        if record.get("lifecycle_record_id") != expected_id:
            errors.append("phase11d_lifecycle_id_invalid")
    if errors:
        return _invalid_phase11d_result(
            tuple(sorted(set(errors))),
            "incompatible",
            rejected_phase11_dossier_lifecycle_record(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11LifecycleAuditValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(record),
    )


def validate_phase11_export_retention_policy(
    policy: object,
    *,
    expected_domain: str | None = None,
) -> Phase11AuditIndexValidationResult:
    """Validate a Phase 11E local-only metadata export/retention policy."""

    if not isinstance(policy, Mapping):
        return _invalid_phase11e_result(
            ("phase11e_export_policy_not_object",),
            "malformed",
            rejected_phase11_export_retention_policy(),
        )
    privacy_violations = _privacy_violation_count(policy)
    errors: list[str] = []
    if PHASE11_EXPORT_RETENTION_POLICY_REQUIRED_FIELDS - set(policy):
        errors.append("phase11e_export_policy_required_field_missing")
    if set(str(key) for key in policy) - PHASE11_EXPORT_RETENTION_POLICY_ALLOWED_FIELDS:
        errors.append("phase11e_export_policy_unknown_field")
    if policy.get("schema_version") != 1:
        errors.append("phase11e_export_policy_schema_version_invalid")
    if policy.get("export_retention_contract_version") != PHASE11_AUDIT_INDEX_CONTRACT_VERSION:
        errors.append("phase11e_export_policy_contract_version_unsupported")
    if policy.get("export_retention_kind") != PHASE11_EXPORT_RETENTION_POLICY_KIND:
        errors.append("phase11e_export_policy_kind_invalid")
    domain = _safe_domain(policy.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11e_export_policy_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11e_export_policy_domain_mismatch")
    if policy.get("retention_label") != PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY:
        errors.append("phase11e_export_policy_retention_invalid")
    if policy.get("export_class") != PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY:
        errors.append("phase11e_export_policy_export_class_invalid")
    for field in (
        "local_only",
        "metadata_export_allowed",
        "deterministic_fixture_export_allowed",
        "payload_export_prohibited",
        "document_text_export_prohibited",
        "signal_export_prohibited",
        "origin_identifier_export_prohibited",
        "hardware_identifier_export_prohibited",
        "auth_material_export_prohibited",
        "path_export_prohibited",
        "url_export_prohibited",
        "model_artifact_payload_export_prohibited",
        "adapter_component_payload_export_prohibited",
        "external_upload_prohibited",
        "network_export_prohibited",
    ):
        if policy.get(field) is not True:
            errors.append("phase11e_export_policy_required_flag_missing")
            break
    _phase11_required_runtime_disabled_errors(policy, errors, "phase11e_export_policy")
    if privacy_violations:
        errors.append("phase11e_export_policy_privacy_boundary")
    expected = _phase11e_record_fingerprint(policy, "policy")
    if not _looks_sha256(expected):
        errors.append("phase11e_export_policy_payload_not_json")
    else:
        if policy.get("policy_fingerprint") != expected:
            errors.append("phase11e_export_policy_fingerprint_invalid")
        if policy.get("policy_id") != f"p11e-policy-{expected[:16]}":
            errors.append("phase11e_export_policy_id_invalid")
    if errors:
        return _invalid_phase11e_result(
            tuple(sorted(set(errors))),
            "incompatible",
            rejected_phase11_export_retention_policy(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11AuditIndexValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(policy),
    )


def validate_phase11_reviewer_scope_coverage(
    coverage: object,
    *,
    expected_domain: str | None = None,
) -> Phase11AuditIndexValidationResult:
    """Validate Phase 11E reviewer-scope coverage metadata."""

    if not isinstance(coverage, Mapping):
        return _invalid_phase11e_result(
            ("phase11e_coverage_not_object",),
            "malformed",
            rejected_phase11_reviewer_scope_coverage_summary(),
        )
    privacy_violations = _privacy_violation_count(coverage)
    errors: list[str] = []
    if PHASE11_REVIEWER_SCOPE_COVERAGE_REQUIRED_FIELDS - set(coverage):
        errors.append("phase11e_coverage_required_field_missing")
    if set(str(key) for key in coverage) - PHASE11_REVIEWER_SCOPE_COVERAGE_ALLOWED_FIELDS:
        errors.append("phase11e_coverage_unknown_field")
    if coverage.get("schema_version") != 1:
        errors.append("phase11e_coverage_schema_version_invalid")
    if coverage.get("coverage_contract_version") != PHASE11_AUDIT_INDEX_CONTRACT_VERSION:
        errors.append("phase11e_coverage_contract_version_unsupported")
    if coverage.get("coverage_kind") != PHASE11_REVIEWER_SCOPE_COVERAGE_KIND:
        errors.append("phase11e_coverage_kind_invalid")
    domain = _safe_domain(coverage.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11e_coverage_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11e_coverage_domain_mismatch")
    if _safe_category(coverage.get("reviewer_scope_label")) != coverage.get("reviewer_scope_label"):
        errors.append("phase11e_coverage_scope_invalid")
    required = tuple(coverage.get("required_gates") or ())
    covered = tuple(coverage.get("covered_gates") or ())
    missing = tuple(coverage.get("missing_gates") or ())
    if required != REAL_MODE_REQUIRED_GATES:
        errors.append("phase11e_coverage_required_gates_invalid")
    if tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate in covered) != covered:
        errors.append("phase11e_coverage_covered_gates_invalid")
    if tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate in missing) != missing:
        errors.append("phase11e_coverage_missing_gates_invalid")
    if set(covered) & set(missing):
        errors.append("phase11e_coverage_gate_overlap")
    if set(covered) | set(missing) != set(REAL_MODE_REQUIRED_GATES):
        errors.append("phase11e_coverage_gate_count_contradiction")
    if bool(coverage.get("coverage_complete")) != (len(missing) == 0):
        errors.append("phase11e_coverage_status_contradiction")
    labels = coverage.get("gate_scope_labels")
    if not isinstance(labels, Mapping):
        errors.append("phase11e_coverage_scope_labels_missing")
    else:
        if set(str(key) for key in labels) != set(REAL_MODE_REQUIRED_GATES):
            errors.append("phase11e_coverage_scope_labels_invalid")
        for value in labels.values():
            if _safe_category(value) != value:
                errors.append("phase11e_coverage_scope_label_invalid")
                break
    _phase11_required_runtime_disabled_errors(coverage, errors, "phase11e_coverage")
    if privacy_violations:
        errors.append("phase11e_coverage_privacy_boundary")
    expected = _phase11e_record_fingerprint(coverage, "coverage")
    if not _looks_sha256(expected):
        errors.append("phase11e_coverage_payload_not_json")
    else:
        if coverage.get("coverage_fingerprint") != expected:
            errors.append("phase11e_coverage_fingerprint_invalid")
        if coverage.get("coverage_id") != f"p11e-coverage-{expected[:16]}":
            errors.append("phase11e_coverage_id_invalid")
    if errors:
        return _invalid_phase11e_result(
            tuple(sorted(set(errors))),
            "incompatible",
            rejected_phase11_reviewer_scope_coverage_summary(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11AuditIndexValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(coverage),
    )


def validate_phase11_change_control_record(
    record: object,
    *,
    expected_domain: str | None = None,
) -> Phase11AuditIndexValidationResult:
    """Validate a Phase 11E change-control record."""

    if not isinstance(record, Mapping):
        return _invalid_phase11e_result(
            ("phase11e_change_control_not_object",),
            "malformed",
            rejected_phase11_change_control_record(),
        )
    privacy_violations = _privacy_violation_count(record)
    errors: list[str] = []
    if PHASE11_CHANGE_CONTROL_REQUIRED_FIELDS - set(record):
        errors.append("phase11e_change_control_required_field_missing")
    if set(str(key) for key in record) - PHASE11_CHANGE_CONTROL_ALLOWED_FIELDS:
        errors.append("phase11e_change_control_unknown_field")
    if record.get("schema_version") != 1:
        errors.append("phase11e_change_control_schema_version_invalid")
    if record.get("change_control_contract_version") != PHASE11_AUDIT_INDEX_CONTRACT_VERSION:
        errors.append("phase11e_change_control_contract_version_unsupported")
    if record.get("change_control_kind") != PHASE11_CHANGE_CONTROL_KIND:
        errors.append("phase11e_change_control_kind_invalid")
    domain = _safe_domain(record.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11e_change_control_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11e_change_control_domain_mismatch")
    for field in ("prior_lifecycle_record_label", "current_lifecycle_record_label"):
        if _safe_phase11e_link_label(record.get(field)) != record.get(field):
            errors.append("phase11e_change_control_record_label_invalid")
            break
    for field in (
        "prior_lifecycle_record_fingerprint",
        "current_lifecycle_record_fingerprint",
    ):
        if not _looks_sha256(record.get(field)):
            errors.append("phase11e_change_control_record_fingerprint_invalid")
            break
    if record.get("prior_lifecycle_record_label") == record.get("current_lifecycle_record_label"):
        errors.append("phase11e_change_control_self_link")
    if not _looks_phase11d_timestamp(record.get("change_timestamp")):
        errors.append("phase11e_change_control_timestamp_invalid")
    if record.get("change_reason") != PHASE11_CHANGE_CONTROL_REASON:
        errors.append("phase11e_change_control_reason_invalid")
    if _safe_category(record.get("reviewer_scope_label")) != record.get("reviewer_scope_label"):
        errors.append("phase11e_change_control_scope_invalid")
    if _safe_lifecycle_decision(record.get("decision")) != record.get("decision"):
        errors.append("phase11e_change_control_decision_invalid")
    _phase11_required_runtime_disabled_errors(record, errors, "phase11e_change_control")
    if privacy_violations:
        errors.append("phase11e_change_control_privacy_boundary")
    expected = _phase11e_record_fingerprint(record, "change")
    if not _looks_sha256(expected):
        errors.append("phase11e_change_control_payload_not_json")
    else:
        if record.get("change_control_fingerprint") != expected:
            errors.append("phase11e_change_control_fingerprint_invalid")
        if record.get("change_control_id") != f"p11e-change-{expected[:16]}":
            errors.append("phase11e_change_control_id_invalid")
    if errors:
        return _invalid_phase11e_result(
            tuple(sorted(set(errors))),
            "incompatible",
            rejected_phase11_change_control_record(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11AuditIndexValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(record),
    )


def validate_phase11_supersession_chain(
    chain: object,
    *,
    expected_domain: str | None = None,
) -> Phase11AuditIndexValidationResult:
    """Validate a Phase 11E sanitized supersession chain."""

    if not isinstance(chain, Mapping):
        return _invalid_phase11e_result(
            ("phase11e_supersession_chain_not_object",),
            "malformed",
            rejected_phase11_supersession_chain(),
        )
    privacy_violations = _privacy_violation_count(chain)
    errors: list[str] = []
    if PHASE11_SUPERSESSION_CHAIN_REQUIRED_FIELDS - set(chain):
        errors.append("phase11e_supersession_chain_required_field_missing")
    if set(str(key) for key in chain) - PHASE11_SUPERSESSION_CHAIN_ALLOWED_FIELDS:
        errors.append("phase11e_supersession_chain_unknown_field")
    if chain.get("schema_version") != 1:
        errors.append("phase11e_supersession_chain_schema_version_invalid")
    if chain.get("supersession_contract_version") != PHASE11_AUDIT_INDEX_CONTRACT_VERSION:
        errors.append("phase11e_supersession_chain_contract_version_unsupported")
    if chain.get("supersession_chain_kind") != PHASE11_SUPERSESSION_CHAIN_KIND:
        errors.append("phase11e_supersession_chain_kind_invalid")
    domain = _safe_domain(chain.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11e_supersession_chain_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11e_supersession_chain_domain_mismatch")
    if chain.get("cross_domain_allowed") is not False:
        errors.append("phase11e_supersession_chain_cross_domain_drift")
    links = chain.get("links")
    if not isinstance(links, list):
        errors.append("phase11e_supersession_chain_links_missing")
        links = []
    if chain.get("record_count") != len(links):
        errors.append("phase11e_supersession_chain_count_contradiction")
    labels: list[str] = []
    fingerprints: list[str] = []
    for index, link in enumerate(links):
        if not isinstance(link, Mapping):
            errors.append("phase11e_supersession_chain_link_malformed")
            continue
        if PHASE11_SUPERSESSION_LINK_REQUIRED_FIELDS - set(link):
            errors.append("phase11e_supersession_chain_link_field_missing")
        if set(str(key) for key in link) - PHASE11_SUPERSESSION_LINK_ALLOWED_FIELDS:
            errors.append("phase11e_supersession_chain_link_unknown_field")
        if link.get("position") != index:
            errors.append("phase11e_supersession_chain_link_order_invalid")
        if _safe_phase11e_link_label(link.get("record_label")) != link.get("record_label"):
            errors.append("phase11e_supersession_chain_label_invalid")
        if not _looks_sha256(link.get("record_fingerprint")):
            errors.append("phase11e_supersession_chain_fingerprint_invalid")
        label = str(link.get("record_label") or "")
        fingerprint = str(link.get("record_fingerprint") or "")
        labels.append(label)
        fingerprints.append(fingerprint)
        has_prior = link.get("has_prior") is True
        has_future = link.get("has_future") is True
        if has_prior:
            if not link.get("prior_record_label") or not _looks_sha256(
                link.get("prior_record_fingerprint")
            ):
                errors.append("phase11e_supersession_chain_prior_missing")
            elif index == 0:
                errors.append("phase11e_supersession_chain_prior_order_invalid")
            elif link.get("prior_record_label") != links[index - 1].get("record_label"):
                errors.append("phase11e_supersession_chain_prior_link_broken")
        elif link.get("prior_record_label") or link.get("prior_record_fingerprint"):
            errors.append("phase11e_supersession_chain_prior_contradiction")
        if has_future:
            if not link.get("future_record_label") or not _looks_sha256(
                link.get("future_record_fingerprint")
            ):
                errors.append("phase11e_supersession_chain_future_missing")
            elif index + 1 >= len(links):
                errors.append("phase11e_supersession_chain_future_order_invalid")
            elif link.get("future_record_label") != links[index + 1].get("record_label"):
                errors.append("phase11e_supersession_chain_future_link_broken")
        elif link.get("future_record_label") or link.get("future_record_fingerprint"):
            errors.append("phase11e_supersession_chain_future_contradiction")
        if _safe_lifecycle_stage(link.get("lifecycle_stage")) != link.get("lifecycle_stage"):
            errors.append("phase11e_supersession_chain_stage_invalid")
        if _safe_lifecycle_decision(link.get("decision")) != link.get("decision"):
            errors.append("phase11e_supersession_chain_decision_invalid")
    if len(labels) != len(set(labels)) or len(fingerprints) != len(set(fingerprints)):
        errors.append("phase11e_supersession_chain_cycle_or_duplicate")
    expected_status = "single-record" if len(links) <= 1 else "linked-runtime-disabled"
    if chain.get("chain_status") != expected_status:
        errors.append("phase11e_supersession_chain_status_contradiction")
    _phase11_required_runtime_disabled_errors(chain, errors, "phase11e_supersession_chain")
    if privacy_violations:
        errors.append("phase11e_supersession_chain_privacy_boundary")
    expected = _phase11e_record_fingerprint(chain, "chain")
    if not _looks_sha256(expected):
        errors.append("phase11e_supersession_chain_payload_not_json")
    else:
        if chain.get("chain_fingerprint") != expected:
            errors.append("phase11e_supersession_chain_fingerprint_invalid")
        if chain.get("chain_id") != f"p11e-chain-{expected[:16]}":
            errors.append("phase11e_supersession_chain_id_invalid")
    if errors:
        return _invalid_phase11e_result(
            tuple(sorted(set(errors))),
            "incompatible",
            rejected_phase11_supersession_chain(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11AuditIndexValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(chain),
    )


def validate_phase11_audit_index(
    audit_index: object,
) -> Phase11AuditIndexValidationResult:
    """Validate a Phase 11E audit-index/change-control record."""

    if not isinstance(audit_index, Mapping):
        return _invalid_phase11e_result(
            ("phase11e_audit_index_not_object",),
            "malformed",
            rejected_phase11_audit_index(),
        )
    privacy_violations = _privacy_violation_count(audit_index)
    errors: list[str] = []
    if PHASE11_AUDIT_INDEX_REQUIRED_FIELDS - set(audit_index):
        errors.append("phase11e_audit_index_required_field_missing")
    if set(str(key) for key in audit_index) - PHASE11_AUDIT_INDEX_ALLOWED_FIELDS:
        errors.append("phase11e_audit_index_unknown_field")
    if audit_index.get("schema_version") != 1:
        errors.append("phase11e_audit_index_schema_version_invalid")
    if audit_index.get("audit_index_contract_version") != PHASE11_AUDIT_INDEX_CONTRACT_VERSION:
        errors.append("phase11e_audit_index_contract_version_unsupported")
    if audit_index.get("audit_index_kind") != PHASE11_AUDIT_INDEX_KIND:
        errors.append("phase11e_audit_index_kind_invalid")
    if _safe_audit_index_status(audit_index.get("status")) != audit_index.get("status"):
        errors.append("phase11e_audit_index_status_invalid")
    if audit_index.get("domain_scope") != "multi-domain":
        errors.append("phase11e_audit_index_domain_scope_invalid")
    entries = audit_index.get("entries")
    if not isinstance(entries, list):
        errors.append("phase11e_audit_index_entries_missing")
        entries = []
    entry_errors, stage_counts, decision_counts, blocking_count, rejection_count = (
        _phase11e_audit_index_entry_errors(entries)
    )
    errors.extend(entry_errors)
    if audit_index.get("entry_count") != len(entries):
        errors.append("phase11e_audit_index_entry_count_contradiction")
    if audit_index.get("created_count") != stage_counts[PHASE11_LIFECYCLE_STAGE_CREATED]:
        errors.append("phase11e_audit_index_created_count_contradiction")
    if audit_index.get("reviewed_count") != stage_counts[PHASE11_LIFECYCLE_STAGE_REVIEWED]:
        errors.append("phase11e_audit_index_reviewed_count_contradiction")
    if audit_index.get("superseded_count") != stage_counts[PHASE11_LIFECYCLE_STAGE_SUPERSEDED]:
        errors.append("phase11e_audit_index_superseded_count_contradiction")
    if audit_index.get("rejected_count") != stage_counts[PHASE11_LIFECYCLE_STAGE_REJECTED]:
        errors.append("phase11e_audit_index_rejected_count_contradiction")
    if audit_index.get("archived_count") != stage_counts[PHASE11_LIFECYCLE_STAGE_ARCHIVED]:
        errors.append("phase11e_audit_index_archived_count_contradiction")
    if (
        audit_index.get("decision_recorded_count")
        != stage_counts[PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED]
    ):
        errors.append("phase11e_audit_index_decision_recorded_count_contradiction")
    if audit_index.get("blocking_count") != blocking_count:
        errors.append("phase11e_audit_index_blocking_count_contradiction")
    if audit_index.get("rejection_count") != rejection_count:
        errors.append("phase11e_audit_index_rejection_count_contradiction")
    if audit_index.get("deterministic_ordering") != "sanitized-label-hash-v1":
        errors.append("phase11e_audit_index_ordering_invalid")
    if audit_index.get("lifecycle_stage_counts") != stage_counts:
        errors.append("phase11e_audit_index_stage_counts_contradiction")
    if audit_index.get("decision_counts") != decision_counts:
        errors.append("phase11e_audit_index_decision_counts_contradiction")
    errors.extend(_phase11e_included_label_errors(audit_index, entries))
    for coverage in audit_index.get("reviewer_scope_coverage", ()):
        if not validate_phase11_reviewer_scope_coverage(coverage).compatible:
            errors.append("phase11e_audit_index_coverage_invalid")
            break
    for chain in audit_index.get("supersession_chains", ()):
        if not validate_phase11_supersession_chain(chain).compatible:
            errors.append("phase11e_audit_index_supersession_chain_invalid")
            break
    for change in audit_index.get("change_control_records", ()):
        if not validate_phase11_change_control_record(change).compatible:
            errors.append("phase11e_audit_index_change_control_invalid")
            break
    for policy in audit_index.get("export_retention_policies", ()):
        if not validate_phase11_export_retention_policy(policy).compatible:
            errors.append("phase11e_audit_index_export_policy_invalid")
            break
    _phase11_required_runtime_disabled_errors(audit_index, errors, "phase11e_audit_index")
    if privacy_violations:
        errors.append("phase11e_audit_index_privacy_boundary")
    expected = _phase11e_record_fingerprint(audit_index, "index")
    if not _looks_sha256(expected):
        errors.append("phase11e_audit_index_payload_not_json")
    else:
        if audit_index.get("index_fingerprint") != expected:
            errors.append("phase11e_audit_index_fingerprint_invalid")
        if audit_index.get("index_id") != f"p11e-index-{expected[:16]}":
            errors.append("phase11e_audit_index_id_invalid")
    if errors:
        return _invalid_phase11e_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11e_audit_index_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_audit_index(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11AuditIndexValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(audit_index),
    )


def validate_phase11_audit_handoff_record(
    handoff: object,
) -> Phase11AuditHandoffValidationResult:
    """Validate a Phase 11F compact audit handoff and fail closed."""

    if not isinstance(handoff, Mapping):
        return _invalid_phase11f_result(
            ("phase11f_audit_handoff_not_object",),
            "malformed",
            rejected_phase11_audit_handoff_record(),
        )
    privacy_violations = _privacy_violation_count(handoff)
    errors: list[str] = []
    if PHASE11_AUDIT_HANDOFF_REQUIRED_FIELDS - set(handoff):
        errors.append("phase11f_audit_handoff_required_field_missing")
    if set(str(key) for key in handoff) - PHASE11_AUDIT_HANDOFF_ALLOWED_FIELDS:
        errors.append("phase11f_audit_handoff_unknown_field")
    if handoff.get("schema_version") != 1:
        errors.append("phase11f_audit_handoff_schema_version_invalid")
    if handoff.get("audit_handoff_contract_version") != PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION:
        errors.append("phase11f_audit_handoff_contract_version_unsupported")
    if handoff.get("audit_handoff_kind") != PHASE11_AUDIT_HANDOFF_KIND:
        errors.append("phase11f_audit_handoff_kind_invalid")
    if _safe_audit_handoff_status(handoff.get("status")) != handoff.get("status"):
        errors.append("phase11f_audit_handoff_status_invalid")
    domain = _safe_domain(handoff.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
        errors.append("phase11f_audit_handoff_domain_invalid")
    if handoff.get("contract_versions") != _phase11f_contract_versions():
        errors.append("phase11f_audit_handoff_contract_versions_invalid")
    if _safe_phase11e_record_id(handoff.get("audit_index_label")) != handoff.get(
        "audit_index_label"
    ):
        errors.append("phase11f_audit_handoff_index_label_invalid")
    if not _looks_sha256(handoff.get("audit_index_fingerprint")):
        errors.append("phase11f_audit_handoff_index_fingerprint_invalid")
    if _safe_audit_index_status(handoff.get("audit_index_status")) != handoff.get(
        "audit_index_status"
    ):
        errors.append("phase11f_audit_handoff_index_status_invalid")
    entry_count = _safe_int(handoff.get("audit_index_entry_count"))
    lifecycle_counts = handoff.get("lifecycle_status_counts")
    coverage_summary = handoff.get("reviewer_scope_coverage_summary")
    retention_summary = handoff.get("retention_export_policy_summary")
    if not _phase11f_lifecycle_counts_valid(lifecycle_counts, entry_count):
        errors.append("phase11f_audit_handoff_lifecycle_counts_invalid")
    if not _phase11f_coverage_summary_valid(coverage_summary):
        errors.append("phase11f_audit_handoff_coverage_summary_invalid")
    if not _phase11f_retention_summary_valid(retention_summary):
        errors.append("phase11f_audit_handoff_retention_summary_invalid")
    for field in (
        "audit_index_entry_count",
        "blocking_count",
        "rejection_count",
        "unresolved_review_count",
    ):
        if _safe_int(handoff.get(field)) != handoff.get(field):
            errors.append("phase11f_audit_handoff_count_invalid")
            break
    if _safe_int(handoff.get("rejection_count")) > entry_count:
        errors.append("phase11f_audit_handoff_rejection_count_contradiction")
    if handoff.get("status") == PHASE11_AUDIT_HANDOFF_STATUS and entry_count <= 0:
        errors.append("phase11f_audit_handoff_status_contradiction")
    _phase11_required_runtime_disabled_errors(handoff, errors, "phase11f_audit_handoff")
    if privacy_violations:
        errors.append("phase11f_audit_handoff_privacy_boundary")
    expected = _phase11f_record_fingerprint(handoff)
    if not _looks_sha256(expected):
        errors.append("phase11f_audit_handoff_payload_not_json")
    else:
        if handoff.get("handoff_fingerprint") != expected:
            errors.append("phase11f_audit_handoff_fingerprint_invalid")
        if handoff.get("handoff_id") != f"p11f-handoff-{expected[:16]}":
            errors.append("phase11f_audit_handoff_id_invalid")
    if errors:
        return _invalid_phase11f_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11f_audit_handoff_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_audit_handoff_record(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11AuditHandoffValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(handoff),
    )


def validate_phase11_handoff_acceptance_record(
    acceptance: object,
) -> Phase11HandoffAcceptanceValidationResult:
    """Validate a Phase 11G handoff acceptance record and fail closed."""

    if not isinstance(acceptance, Mapping):
        return _invalid_phase11g_result(
            ("phase11g_handoff_acceptance_not_object",),
            "malformed",
            rejected_phase11_handoff_acceptance_record(),
        )
    privacy_violations = _privacy_violation_count(acceptance)
    errors: list[str] = []
    if PHASE11_HANDOFF_ACCEPTANCE_REQUIRED_FIELDS - set(acceptance):
        errors.append("phase11g_handoff_acceptance_required_field_missing")
    if set(str(key) for key in acceptance) - PHASE11_HANDOFF_ACCEPTANCE_ALLOWED_FIELDS:
        errors.append("phase11g_handoff_acceptance_unknown_field")
    if acceptance.get("schema_version") != 1:
        errors.append("phase11g_handoff_acceptance_schema_version_invalid")
    if (
        acceptance.get("handoff_acceptance_contract_version")
        != PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION
    ):
        errors.append("phase11g_handoff_acceptance_contract_version_unsupported")
    if acceptance.get("handoff_acceptance_kind") != PHASE11_HANDOFF_ACCEPTANCE_KIND:
        errors.append("phase11g_handoff_acceptance_kind_invalid")
    if _safe_handoff_acceptance_status(acceptance.get("status")) != acceptance.get("status"):
        errors.append("phase11g_handoff_acceptance_status_invalid")
    domain = _safe_domain(acceptance.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
        errors.append("phase11g_handoff_acceptance_domain_invalid")
    if acceptance.get("contract_versions") != _phase11g_contract_versions():
        errors.append("phase11g_handoff_acceptance_contract_versions_invalid")
    if _safe_phase11g_record_id(acceptance.get("acceptance_id")) != acceptance.get("acceptance_id"):
        errors.append("phase11g_handoff_acceptance_id_invalid")
    if not _looks_sha256(acceptance.get("acceptance_fingerprint")):
        errors.append("phase11g_handoff_acceptance_fingerprint_missing")
    if _safe_phase11f_record_id(acceptance.get("source_handoff_label")) != acceptance.get(
        "source_handoff_label"
    ):
        errors.append("phase11g_handoff_acceptance_handoff_label_invalid")
    if not _looks_sha256(acceptance.get("source_handoff_hash")):
        errors.append("phase11g_handoff_acceptance_source_hash_invalid")
    if not _looks_sha256(acceptance.get("handoff_fingerprint")):
        errors.append("phase11g_handoff_acceptance_handoff_hash_invalid")
    if _safe_audit_handoff_status(acceptance.get("handoff_status")) != acceptance.get(
        "handoff_status"
    ):
        errors.append("phase11g_handoff_acceptance_handoff_status_invalid")
    accepted = acceptance.get("accepted_for_planning")
    blocked = acceptance.get("blocked")
    stale = acceptance.get("stale")
    if (
        not isinstance(accepted, bool)
        or not isinstance(blocked, bool)
        or not isinstance(stale, bool)
    ):
        errors.append("phase11g_handoff_acceptance_boolean_invalid")
        accepted = False
        blocked = True
        stale = False
    for field in ("missing_review_count", "unresolved_review_count"):
        if _safe_int(acceptance.get(field)) != acceptance.get(field):
            errors.append("phase11g_handoff_acceptance_count_invalid")
            break
    rejection_reasons = acceptance.get("rejection_reasons")
    blocking_reasons = acceptance.get("blocking_reasons")
    if not _phase11g_reason_list_valid(rejection_reasons):
        errors.append("phase11g_handoff_acceptance_rejection_reasons_invalid")
        rejection_reasons = []
    if not _phase11g_reason_list_valid(blocking_reasons):
        errors.append("phase11g_handoff_acceptance_blocking_reasons_invalid")
        blocking_reasons = []
    source_hash = str(acceptance.get("source_handoff_hash") or "")
    handoff_hash = str(acceptance.get("handoff_fingerprint") or "")
    hash_mismatch = source_hash != handoff_hash
    if hash_mismatch and stale is not True:
        errors.append("phase11g_handoff_acceptance_stale_hash_mismatch")
    if stale is True and not hash_mismatch:
        errors.append("phase11g_handoff_acceptance_stale_contradiction")
    status = acceptance.get("status")
    if accepted is True and (blocked is True or stale is True):
        errors.append("phase11g_handoff_acceptance_status_contradiction")
    if domain == "unknown" and (
        accepted is True
        or blocked is not True
        or status != PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS
    ):
        errors.append("phase11g_handoff_acceptance_unknown_domain_not_rejected")
    if accepted is True and (
        acceptance.get("missing_review_count") != 0
        or acceptance.get("unresolved_review_count") != 0
        or rejection_reasons
        or blocking_reasons
        or acceptance.get("handoff_status") != PHASE11_AUDIT_HANDOFF_STATUS
        or status != PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS
    ):
        errors.append("phase11g_handoff_acceptance_acceptance_contradiction")
    if status == PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS and accepted is not True:
        errors.append("phase11g_handoff_acceptance_acceptance_contradiction")
    if status == PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS and (
        accepted is True or blocked is not True or stale is True or not blocking_reasons
    ):
        errors.append("phase11g_handoff_acceptance_blocked_contradiction")
    if status == PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS and (
        accepted is True
        or blocked is not True
        or stale is not True
        or "source-handoff-hash-mismatch" not in blocking_reasons
    ):
        errors.append("phase11g_handoff_acceptance_stale_contradiction")
    if status == PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS and (
        accepted is True or blocked is not True or not rejection_reasons
    ):
        errors.append("phase11g_handoff_acceptance_rejected_contradiction")
    _phase11_required_runtime_disabled_errors(
        acceptance,
        errors,
        "phase11g_handoff_acceptance",
    )
    if privacy_violations:
        errors.append("phase11g_handoff_acceptance_privacy_boundary")
    expected = _phase11g_record_fingerprint(acceptance)
    if not _looks_sha256(expected):
        errors.append("phase11g_handoff_acceptance_payload_not_json")
    else:
        if acceptance.get("acceptance_fingerprint") != expected:
            errors.append("phase11g_handoff_acceptance_fingerprint_invalid")
        if acceptance.get("acceptance_id") != f"p11g-acceptance-{expected[:16]}":
            errors.append("phase11g_handoff_acceptance_id_invalid")
    if errors:
        return _invalid_phase11g_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11g_handoff_acceptance_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_handoff_acceptance_record(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11HandoffAcceptanceValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(acceptance),
    )


def validate_phase11_acceptance_followup_record(
    followup: object,
) -> Phase11AcceptanceFollowupValidationResult:
    """Validate a Phase 11H follow-up/remediation record and fail closed."""

    if not isinstance(followup, Mapping):
        return _invalid_phase11h_result(
            ("phase11h_acceptance_followup_not_object",),
            "malformed",
            rejected_phase11_acceptance_followup_record(),
        )
    privacy_violations = _privacy_violation_count(followup)
    execution_wording = _execution_implying_wording_count(followup)
    errors: list[str] = []
    if PHASE11_ACCEPTANCE_FOLLOWUP_REQUIRED_FIELDS - set(followup):
        errors.append("phase11h_acceptance_followup_required_field_missing")
    if set(str(key) for key in followup) - PHASE11_ACCEPTANCE_FOLLOWUP_ALLOWED_FIELDS:
        errors.append("phase11h_acceptance_followup_unknown_field")
    if followup.get("schema_version") != 1:
        errors.append("phase11h_acceptance_followup_schema_version_invalid")
    if (
        followup.get("acceptance_followup_contract_version")
        != PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION
    ):
        errors.append("phase11h_acceptance_followup_contract_version_unsupported")
    if followup.get("followup_kind") != PHASE11_ACCEPTANCE_FOLLOWUP_KIND:
        errors.append("phase11h_acceptance_followup_kind_invalid")
    if _safe_phase11h_record_id(followup.get("followup_id")) != followup.get("followup_id"):
        errors.append("phase11h_acceptance_followup_id_invalid")
    domain = _safe_domain(followup.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
        errors.append("phase11h_acceptance_followup_domain_invalid")
    followup_type = _safe_acceptance_followup_type(followup.get("followup_type"))
    if followup_type != followup.get("followup_type"):
        errors.append("phase11h_acceptance_followup_type_invalid")
        followup_type = None
    status = _safe_acceptance_followup_status(followup.get("status"))
    if status != followup.get("status"):
        errors.append("phase11h_acceptance_followup_status_invalid")
    if followup.get("contract_versions") != _phase11h_contract_versions():
        errors.append("phase11h_acceptance_followup_contract_versions_invalid")
    if _safe_phase11g_record_id(followup.get("source_acceptance_label")) != followup.get(
        "source_acceptance_label"
    ):
        errors.append("phase11h_acceptance_followup_source_label_invalid")
    if not _looks_sha256(followup.get("source_acceptance_hash")):
        errors.append("phase11h_acceptance_followup_source_hash_invalid")
    if _safe_acceptance_followup_blocker_summary(
        followup.get("blocker_disposition_summary")
    ) != followup.get("blocker_disposition_summary"):
        errors.append("phase11h_acceptance_followup_blocker_summary_invalid")
    if _safe_acceptance_followup_reviewer_summary(
        followup.get("reviewer_queue_summary")
    ) != followup.get("reviewer_queue_summary"):
        errors.append("phase11h_acceptance_followup_reviewer_summary_invalid")
    if _safe_acceptance_followup_stale_summary(
        followup.get("stale_renewal_summary")
    ) != followup.get("stale_renewal_summary"):
        errors.append("phase11h_acceptance_followup_stale_summary_invalid")
    for field in ("unresolved_review_count", "blocking_count", "rejection_count"):
        if _safe_int(followup.get(field)) != followup.get(field):
            errors.append("phase11h_acceptance_followup_count_invalid")
            break
    unresolved_count = _safe_int(followup.get("unresolved_review_count"))
    blocking_count = _safe_int(followup.get("blocking_count"))
    rejection_count = _safe_int(followup.get("rejection_count"))
    blocker_summary = followup.get("blocker_disposition_summary")
    reviewer_summary = followup.get("reviewer_queue_summary")
    stale_summary = followup.get("stale_renewal_summary")
    if domain == "unknown" and status != PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS:
        errors.append("phase11h_acceptance_followup_unknown_domain_not_rejected")
    if status == PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS and (
        unresolved_count != 0
        or blocking_count != 0
        or rejection_count != 0
        or blocker_summary != "blockers-dispositioned"
        or reviewer_summary != "reviews-clear"
        or stale_summary != "source-current"
    ):
        errors.append("phase11h_acceptance_followup_resolved_contradiction")
    if status == PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS and (
        followup_type != PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE
        or unresolved_count != 0
        or blocking_count != 0
        or rejection_count != 0
        or stale_summary != "source-current"
    ):
        errors.append("phase11h_acceptance_followup_archived_contradiction")
    if status == PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS and (
        blocking_count == 0 and rejection_count == 0 and unresolved_count == 0
    ):
        errors.append("phase11h_acceptance_followup_blocked_contradiction")
    if status == PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS and (
        followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE or rejection_count != 0
    ):
        errors.append("phase11h_acceptance_followup_open_contradiction")
    if status == PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS and rejection_count == 0:
        errors.append("phase11h_acceptance_followup_rejected_contradiction")
    if followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE and (
        stale_summary == "source-current"
        or status
        not in {
            PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS,
            PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS,
        }
    ):
        errors.append("phase11h_acceptance_followup_stale_type_contradiction")
    if followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE and (
        unresolved_count == 0 or status != PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS
    ):
        errors.append("phase11h_acceptance_followup_reviewer_type_contradiction")
    if followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE and (
        status
        not in {
            PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS,
            PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS,
            PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS,
        }
        or (
            status != PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS
            and unresolved_count == 0
            and blocking_count == 0
        )
    ):
        errors.append("phase11h_acceptance_followup_review_type_contradiction")
    _phase11_required_runtime_disabled_errors(
        followup,
        errors,
        "phase11h_acceptance_followup",
    )
    if privacy_violations:
        errors.append("phase11h_acceptance_followup_privacy_boundary")
    if execution_wording:
        errors.append("phase11h_acceptance_followup_execution_wording")
    expected_id = _phase11h_record_id(followup)
    if not expected_id:
        errors.append("phase11h_acceptance_followup_payload_not_json")
    elif followup.get("followup_id") != expected_id:
        errors.append("phase11h_acceptance_followup_id_invalid")
    if errors:
        return _invalid_phase11h_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11h_acceptance_followup_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_acceptance_followup_record(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11AcceptanceFollowupValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(followup),
    )


def validate_phase11_followup_queue_index_record(
    queue_index: object,
) -> Phase11FollowupQueueValidationResult:
    """Validate a Phase 11I queue index record and fail closed."""

    if not isinstance(queue_index, Mapping):
        return _invalid_phase11i_queue_result(
            ("phase11i_queue_index_not_object",),
            "malformed",
            rejected_phase11_followup_queue_index(),
        )
    privacy_violations = _privacy_violation_count(queue_index)
    execution_wording = _execution_implying_wording_count(queue_index)
    errors: list[str] = []
    if PHASE11_FOLLOWUP_QUEUE_INDEX_REQUIRED_FIELDS - set(queue_index):
        errors.append("phase11i_queue_index_required_field_missing")
    if set(str(key) for key in queue_index) - PHASE11_FOLLOWUP_QUEUE_INDEX_ALLOWED_FIELDS:
        errors.append("phase11i_queue_index_unknown_field")
    if queue_index.get("schema_version") != 1:
        errors.append("phase11i_queue_index_schema_version_invalid")
    if (
        queue_index.get("queue_index_contract_version")
        != PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION
    ):
        errors.append("phase11i_queue_index_contract_version_unsupported")
    if queue_index.get("queue_index_kind") != PHASE11_FOLLOWUP_QUEUE_INDEX_KIND:
        errors.append("phase11i_queue_index_kind_invalid")
    if _safe_phase11i_queue_id(queue_index.get("queue_id")) != queue_index.get("queue_id"):
        errors.append("phase11i_queue_index_id_invalid")
    if not _looks_sha256(queue_index.get("queue_fingerprint")):
        errors.append("phase11i_queue_index_fingerprint_invalid")
    domain = _safe_domain(queue_index.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
        errors.append("phase11i_queue_index_domain_invalid")
    status = _safe_followup_queue_status(queue_index.get("status"))
    if status != queue_index.get("status"):
        errors.append("phase11i_queue_index_status_invalid")
    if queue_index.get("contract_versions") != _phase11i_contract_versions():
        errors.append("phase11i_queue_index_contract_versions_invalid")

    labels = queue_index.get("included_followup_labels")
    hashes = queue_index.get("included_followup_hashes")
    if not isinstance(labels, list) or not isinstance(hashes, list) or len(labels) != len(hashes):
        errors.append("phase11i_queue_index_included_followups_invalid")
        labels = []
        hashes = []
    for label in labels:
        if _safe_phase11h_record_id(label) != label:
            errors.append("phase11i_queue_index_followup_label_invalid")
            break
    for item in hashes:
        if not _looks_sha256(item):
            errors.append("phase11i_queue_index_followup_hash_invalid")
            break
    entry_count = _safe_int(queue_index.get("entry_count"))
    if entry_count != len(labels):
        errors.append("phase11i_queue_index_entry_count_contradiction")

    status_errors = _phase11i_queue_count_errors(queue_index)
    errors.extend(status_errors)
    errors.extend(_phase11i_ordering_errors(queue_index))
    expected_status = _phase11i_queue_status_from_counts(queue_index)
    if status != expected_status:
        errors.append("phase11i_queue_index_status_contradiction")
    _phase11_required_runtime_disabled_errors(
        queue_index,
        errors,
        "phase11i_queue_index",
    )
    if privacy_violations:
        errors.append("phase11i_queue_index_privacy_boundary")
    if execution_wording:
        errors.append("phase11i_queue_index_execution_wording")
    expected_fingerprint = _phase11i_queue_index_fingerprint(queue_index)
    if not _looks_sha256(expected_fingerprint):
        errors.append("phase11i_queue_index_payload_not_json")
    else:
        if queue_index.get("queue_fingerprint") != expected_fingerprint:
            errors.append("phase11i_queue_index_fingerprint_invalid")
        expected_id = f"p11i-queue-{domain}-{expected_fingerprint[:16]}"
        if queue_index.get("queue_id") != expected_id:
            errors.append("phase11i_queue_index_id_invalid")
    if errors:
        return _invalid_phase11i_queue_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11i_queue_index_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_followup_queue_index(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11FollowupQueueValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(queue_index),
    )


def validate_phase11_followup_queue_acceptance_check(
    acceptance: object,
) -> Phase11FollowupQueueAcceptanceValidationResult:
    """Validate a Phase 11I queue acceptance/check record and fail closed."""

    if not isinstance(acceptance, Mapping):
        return _invalid_phase11i_acceptance_result(
            ("phase11i_queue_acceptance_not_object",),
            "malformed",
            rejected_phase11_followup_queue_acceptance_check(),
        )
    privacy_violations = _privacy_violation_count(acceptance)
    execution_wording = _execution_implying_wording_count(acceptance)
    errors: list[str] = []
    if PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_REQUIRED_FIELDS - set(acceptance):
        errors.append("phase11i_queue_acceptance_required_field_missing")
    if set(str(key) for key in acceptance) - PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_ALLOWED_FIELDS:
        errors.append("phase11i_queue_acceptance_unknown_field")
    if acceptance.get("schema_version") != 1:
        errors.append("phase11i_queue_acceptance_schema_version_invalid")
    if (
        acceptance.get("queue_index_contract_version")
        != PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION
    ):
        errors.append("phase11i_queue_acceptance_contract_version_unsupported")
    if acceptance.get("queue_acceptance_kind") != PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_KIND:
        errors.append("phase11i_queue_acceptance_kind_invalid")
    if _safe_phase11i_acceptance_id(acceptance.get("acceptance_id")) != acceptance.get(
        "acceptance_id"
    ):
        errors.append("phase11i_queue_acceptance_id_invalid")
    if not _looks_sha256(acceptance.get("acceptance_fingerprint")):
        errors.append("phase11i_queue_acceptance_fingerprint_invalid")
    if _safe_phase11i_queue_id(acceptance.get("queue_label")) != acceptance.get("queue_label"):
        errors.append("phase11i_queue_acceptance_queue_label_invalid")
    if not _looks_sha256(acceptance.get("queue_fingerprint")):
        errors.append("phase11i_queue_acceptance_queue_fingerprint_invalid")
    domain = _safe_domain(acceptance.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
        errors.append("phase11i_queue_acceptance_domain_invalid")
    status = _safe_followup_queue_status(acceptance.get("status"))
    if status != acceptance.get("status"):
        errors.append("phase11i_queue_acceptance_status_invalid")
    if acceptance.get("contract_versions") != _phase11i_contract_versions():
        errors.append("phase11i_queue_acceptance_contract_versions_invalid")
    if not _phase11i_queue_label_matches_fingerprint(
        label=acceptance.get("queue_label"),
        domain=acceptance.get("domain"),
        fingerprint=acceptance.get("queue_fingerprint"),
    ):
        errors.append("phase11i_queue_acceptance_queue_ref_contradiction")
    errors.extend(_phase11i_queue_count_errors(acceptance, include_summary_counts=False))
    expected_status = _phase11i_queue_status_from_counts(acceptance)
    if status != expected_status:
        errors.append("phase11i_queue_acceptance_status_contradiction")
    _phase11_required_runtime_disabled_errors(
        acceptance,
        errors,
        "phase11i_queue_acceptance",
    )
    if privacy_violations:
        errors.append("phase11i_queue_acceptance_privacy_boundary")
    if execution_wording:
        errors.append("phase11i_queue_acceptance_execution_wording")
    expected_fingerprint = _phase11i_acceptance_fingerprint(acceptance)
    if not _looks_sha256(expected_fingerprint):
        errors.append("phase11i_queue_acceptance_payload_not_json")
    else:
        if acceptance.get("acceptance_fingerprint") != expected_fingerprint:
            errors.append("phase11i_queue_acceptance_fingerprint_invalid")
        expected_id = f"p11i-check-{expected_fingerprint[:16]}"
        if acceptance.get("acceptance_id") != expected_id:
            errors.append("phase11i_queue_acceptance_id_invalid")
    if errors:
        return _invalid_phase11i_acceptance_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11i_queue_acceptance_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_followup_queue_acceptance_check(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11FollowupQueueAcceptanceValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(acceptance),
    )


def validate_phase11_decision_closeout_record(
    closeout: object,
) -> Phase11DecisionCloseoutValidationResult:
    """Validate a Phase 11J decision-closeout record and fail closed."""

    if not isinstance(closeout, Mapping):
        return _invalid_phase11j_closeout_result(
            ("phase11j_closeout_not_object",),
            "malformed",
            rejected_phase11_decision_closeout_record(),
        )
    privacy_violations = _privacy_violation_count(closeout)
    execution_wording = _execution_implying_wording_count(closeout)
    errors: list[str] = []
    if PHASE11_DECISION_CLOSEOUT_REQUIRED_FIELDS - set(closeout):
        errors.append("phase11j_closeout_required_field_missing")
    if set(str(key) for key in closeout) - PHASE11_DECISION_CLOSEOUT_ALLOWED_FIELDS:
        errors.append("phase11j_closeout_unknown_field")
    if closeout.get("schema_version") != 1:
        errors.append("phase11j_closeout_schema_version_invalid")
    if closeout.get("closeout_contract_version") != PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION:
        errors.append("phase11j_closeout_contract_version_unsupported")
    if closeout.get("contract_versions") != _phase11j_contract_versions():
        errors.append("phase11j_closeout_contract_versions_invalid")
    if _safe_phase11j_closeout_id(closeout.get("closeout_id")) != closeout.get("closeout_id"):
        errors.append("phase11j_closeout_id_invalid")
    domain = _safe_domain(closeout.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
        errors.append("phase11j_closeout_domain_invalid")
    if _safe_phase11i_queue_id(closeout.get("source_queue_label")) != closeout.get(
        "source_queue_label"
    ):
        errors.append("phase11j_closeout_source_queue_label_invalid")
    if not _looks_sha256(closeout.get("source_queue_hash")):
        errors.append("phase11j_closeout_source_queue_hash_invalid")
    if not _phase11i_queue_label_matches_fingerprint(
        label=closeout.get("source_queue_label"),
        domain=domain,
        fingerprint=closeout.get("source_queue_hash"),
    ):
        errors.append("phase11j_closeout_source_queue_ref_contradiction")
    decision = _safe_phase11j_decision(closeout.get("closeout_decision"))
    if decision != closeout.get("closeout_decision"):
        errors.append("phase11j_closeout_decision_invalid")
    status = _safe_phase11j_status(closeout.get("closeout_status"))
    if status != closeout.get("closeout_status"):
        errors.append("phase11j_closeout_status_invalid")
    if _safe_phase11j_reviewer_summary(
        closeout.get("reviewer_disposition_summary")
    ) != closeout.get("reviewer_disposition_summary"):
        errors.append("phase11j_closeout_reviewer_summary_invalid")
    errors.extend(_phase11j_count_errors(closeout))
    if _phase11j_status_from_decision(decision) != status:
        errors.append("phase11j_closeout_status_contradiction")
    errors.extend(_phase11j_decision_count_contradictions(closeout))
    _phase11_required_runtime_disabled_errors(
        closeout,
        errors,
        "phase11j_closeout",
    )
    if privacy_violations:
        errors.append("phase11j_closeout_privacy_boundary")
    if execution_wording:
        errors.append("phase11j_closeout_execution_wording")
    expected_id = _phase11j_closeout_id(closeout)
    if not expected_id:
        errors.append("phase11j_closeout_payload_not_json")
    elif closeout.get("closeout_id") != expected_id:
        errors.append("phase11j_closeout_id_invalid")
    if errors:
        return _invalid_phase11j_closeout_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11j_closeout_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_decision_closeout_record(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11DecisionCloseoutValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(closeout),
    )


def validate_phase11_review_trail_export_bundle(
    export: object,
) -> Phase11ReviewTrailExportValidationResult:
    """Validate a Phase 11K review-trail export and fail closed."""

    if not isinstance(export, Mapping):
        return _invalid_phase11k_export_result(
            ("phase11k_review_trail_export_not_object",),
            "malformed",
            rejected_phase11_review_trail_export_bundle(),
        )
    privacy_violations = _phase11k_privacy_violation_count(export)
    execution_wording = _execution_implying_wording_count(export)
    errors: list[str] = []
    if PHASE11_REVIEW_TRAIL_EXPORT_REQUIRED_FIELDS - set(export):
        errors.append("phase11k_review_trail_export_required_field_missing")
    if set(str(key) for key in export) - PHASE11_REVIEW_TRAIL_EXPORT_ALLOWED_FIELDS:
        errors.append("phase11k_review_trail_export_unknown_field")
    if (
        export.get("review_trail_export_contract_version")
        != PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION
    ):
        errors.append("phase11k_review_trail_export_contract_version_unsupported")
    if _safe_phase11k_export_id(export.get("export_id")) != export.get("export_id"):
        errors.append("phase11k_review_trail_export_id_invalid")
    if export.get("phase_range") != PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE:
        errors.append("phase11k_review_trail_export_phase_range_invalid")
    if export.get("covered_phase_count") != PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT:
        errors.append("phase11k_review_trail_export_phase_count_invalid")
    if export.get("readiness_gap_summary") != PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP:
        errors.append("phase11k_review_trail_export_readiness_gap_invalid")
    domain_labels = export.get("domain_labels")
    if not isinstance(domain_labels, list):
        errors.append("phase11k_review_trail_export_domain_labels_invalid")
        domain_labels = []
    else:
        safe_labels = [_safe_domain(item) for item in domain_labels]
        if safe_labels != domain_labels or safe_labels != _phase11k_domain_labels():
            errors.append("phase11k_review_trail_export_domain_labels_invalid")
    domain_closeouts = export.get("domain_closeouts")
    if not isinstance(domain_closeouts, list):
        errors.append("phase11k_review_trail_export_domain_closeouts_invalid")
        domain_closeouts = []
    else:
        errors.extend(_phase11k_domain_closeout_errors(domain_closeouts))
    if export.get("execution_permitted") is not False:
        errors.append("phase11k_review_trail_export_runtime_implied")
    if export.get("real_mode_runtime_enabled") is not False:
        errors.append("phase11k_review_trail_export_runtime_implied")
    if export.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase11k_review_trail_export_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase11k_review_trail_export_privacy_boundary")
    if execution_wording:
        errors.append("phase11k_review_trail_export_execution_wording")
    expected_id = _phase11k_export_id(export)
    if not expected_id:
        errors.append("phase11k_review_trail_export_payload_not_json")
    elif export.get("export_id") != expected_id:
        errors.append("phase11k_review_trail_export_id_invalid")
    if errors:
        return _invalid_phase11k_export_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11k_review_trail_export_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_review_trail_export_bundle(),
            privacy_violation_count=privacy_violations,
        )
    return Phase11ReviewTrailExportValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(export),
    )


def validate_phase11_runtime_authorization_gap_ledger(
    ledger: object,
) -> Phase11RuntimeAuthorizationGapLedgerValidationResult:
    """Validate a Phase 11L runtime authorization gap ledger and fail closed."""

    if not isinstance(ledger, Mapping):
        return _invalid_phase11l_runtime_gap_result(
            ("phase11l_runtime_gap_ledger_not_object",),
            "malformed",
            rejected_phase11_runtime_authorization_gap_ledger(),
        )
    privacy_violations = _phase11l_privacy_violation_count(ledger)
    execution_wording = _execution_implying_wording_count(ledger)
    authorization_wording = _phase11l_authorization_wording_count(ledger)
    errors: list[str] = []
    if PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_REQUIRED_FIELDS - set(ledger):
        errors.append("phase11l_runtime_gap_ledger_required_field_missing")
    if set(str(key) for key in ledger) - PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_ALLOWED_FIELDS:
        errors.append("phase11l_runtime_gap_ledger_unknown_field")
    if (
        ledger.get("runtime_authorization_gap_ledger_contract_version")
        != PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION
    ):
        errors.append("phase11l_runtime_gap_ledger_contract_version_unsupported")
    if _safe_phase11l_ledger_id(ledger.get("ledger_id")) != ledger.get("ledger_id"):
        errors.append("phase11l_runtime_gap_ledger_id_invalid")
    if ledger.get("source_phase_range") != PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE:
        errors.append("phase11l_runtime_gap_ledger_phase_range_invalid")
    if ledger.get("covered_phase_count") != PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT:
        errors.append("phase11l_runtime_gap_ledger_phase_count_invalid")
    domain_labels = ledger.get("domain_labels")
    if not isinstance(domain_labels, list):
        errors.append("phase11l_runtime_gap_ledger_domain_labels_invalid")
    else:
        safe_labels = [_safe_domain(item) for item in domain_labels]
        if safe_labels != domain_labels or safe_labels != _phase11k_domain_labels():
            errors.append("phase11l_runtime_gap_ledger_domain_labels_invalid")
    domain_summaries = ledger.get("domain_gap_summaries")
    if not isinstance(domain_summaries, list):
        errors.append("phase11l_runtime_gap_ledger_domain_summaries_invalid")
    else:
        errors.extend(_phase11l_domain_gap_errors(domain_summaries))
    if ledger.get("authorization_status") != PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS:
        errors.append("phase11l_runtime_gap_ledger_authorization_status_invalid")
    if ledger.get("readiness_gap") != PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP:
        errors.append("phase11l_runtime_gap_ledger_readiness_gap_invalid")
    missing_gates = ledger.get("missing_future_gates")
    if not isinstance(missing_gates, list):
        errors.append("phase11l_runtime_gap_ledger_missing_gates_invalid")
    elif missing_gates != list(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES):
        errors.append("phase11l_runtime_gap_ledger_missing_gates_invalid")
    if ledger.get("missing_future_gate_count") != len(
        PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES
    ):
        errors.append("phase11l_runtime_gap_ledger_missing_gate_count_invalid")
    for field in (
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if ledger.get(field) is not False:
            errors.append("phase11l_runtime_gap_ledger_runtime_implied")
            break
    if ledger.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase11l_runtime_gap_ledger_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase11l_runtime_gap_ledger_privacy_boundary")
    if execution_wording:
        errors.append("phase11l_runtime_gap_ledger_execution_wording")
    if authorization_wording:
        errors.append("phase11l_runtime_gap_ledger_authorization_wording")
    expected_id = _phase11l_ledger_id(ledger)
    if not expected_id:
        errors.append("phase11l_runtime_gap_ledger_payload_not_json")
    elif ledger.get("ledger_id") != expected_id:
        errors.append("phase11l_runtime_gap_ledger_id_invalid")
    if errors:
        return _invalid_phase11l_runtime_gap_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11l_runtime_gap_ledger_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_runtime_authorization_gap_ledger(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase11RuntimeAuthorizationGapLedgerValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(ledger),
    )


def validate_phase11_planning_governance_closeout_index(
    closeout: object,
) -> Phase11PlanningGovernanceCloseoutValidationResult:
    """Validate a Phase 11M governance closeout index and fail closed."""

    if not isinstance(closeout, Mapping):
        return _invalid_phase11m_governance_result(
            ("phase11m_governance_closeout_not_object",),
            "malformed",
            rejected_phase11_planning_governance_closeout_index(),
        )
    privacy_violations = _phase11m_privacy_violation_count(closeout)
    execution_wording = _execution_implying_wording_count(closeout)
    authorization_wording = _phase11m_authorization_wording_count(closeout)
    errors: list[str] = []
    if PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_REQUIRED_FIELDS - set(closeout):
        errors.append("phase11m_governance_closeout_required_field_missing")
    if set(str(key) for key in closeout) - PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_ALLOWED_FIELDS:
        errors.append("phase11m_governance_closeout_unknown_field")
    if (
        closeout.get("planning_governance_closeout_contract_version")
        != PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION
    ):
        errors.append("phase11m_governance_closeout_version_unsupported")
    if _safe_phase11m_closeout_id(closeout.get("closeout_index_id")) != closeout.get(
        "closeout_index_id"
    ):
        errors.append("phase11m_governance_closeout_id_invalid")
    if closeout.get("phase_range") != PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE:
        errors.append("phase11m_governance_closeout_phase_range_invalid")
    if closeout.get("covered_phase_count") != PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT:
        errors.append("phase11m_governance_closeout_phase_count_invalid")
    if closeout.get("final_status") != PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS:
        errors.append("phase11m_governance_closeout_final_status_invalid")
    if (
        closeout.get("runtime_authorization_status")
        != PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS
    ):
        errors.append("phase11m_governance_closeout_runtime_status_invalid")
    if closeout.get("readiness_gap") != PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP:
        errors.append("phase11m_governance_closeout_readiness_gap_invalid")
    if (
        closeout.get("next_phase_requirement")
        != PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_NEXT_PHASE_REQUIREMENT
    ):
        errors.append("phase11m_governance_closeout_next_phase_invalid")
    if _safe_phase11l_ledger_id(closeout.get("gap_ledger_id")) != closeout.get("gap_ledger_id"):
        errors.append("phase11m_governance_closeout_gap_ledger_id_invalid")
    if (
        closeout.get("gap_ledger_contract_version")
        != PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION
    ):
        errors.append("phase11m_governance_closeout_gap_ledger_version_invalid")
    if (
        closeout.get("gap_ledger_phase_range")
        != PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE
    ):
        errors.append("phase11m_governance_closeout_gap_ledger_phase_invalid")
    domain_labels = closeout.get("domain_labels")
    if not isinstance(domain_labels, list):
        errors.append("phase11m_governance_closeout_domains_invalid")
    else:
        safe_labels = [_safe_domain(item) for item in domain_labels]
        if safe_labels != domain_labels or safe_labels != _phase11k_domain_labels():
            errors.append("phase11m_governance_closeout_domains_invalid")
    if closeout.get("domain_count") != len(_phase11k_domain_labels()):
        errors.append("phase11m_governance_closeout_domain_count_invalid")
    for field in (
        "covered_phase_count",
        "domain_count",
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
        "missing_future_gate_count",
    ):
        if not _is_phase11j_count(closeout.get(field)):
            errors.append("phase11m_governance_closeout_count_invalid")
            break
    if closeout.get("missing_future_gate_count") != len(
        PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES
    ):
        errors.append("phase11m_governance_closeout_missing_gate_count_invalid")
    for field in (
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if closeout.get(field) is not False:
            errors.append("phase11m_governance_closeout_runtime_implied")
            break
    if closeout.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase11m_governance_closeout_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase11m_governance_closeout_privacy_boundary")
    if execution_wording:
        errors.append("phase11m_governance_closeout_execution_wording")
    if authorization_wording:
        errors.append("phase11m_governance_closeout_authorization_wording")
    expected_id = _phase11m_closeout_id(closeout)
    if not expected_id:
        errors.append("phase11m_governance_closeout_payload_not_json")
    elif closeout.get("closeout_index_id") != expected_id:
        errors.append("phase11m_governance_closeout_id_invalid")
    if errors:
        return _invalid_phase11m_governance_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase11m_governance_closeout_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase11_planning_governance_closeout_index(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase11PlanningGovernanceCloseoutValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(closeout),
    )


def validate_phase11_review_record(
    record: object,
    *,
    expected_domain: str | None = None,
) -> Phase11ReviewRecordValidationResult:
    """Validate a Phase 11B review record and fail closed on unsafe content."""

    if not isinstance(record, Mapping):
        return _invalid_review_record_result(
            ("phase11_review_record_not_object",),
            "malformed",
        )

    privacy_violations = _privacy_violation_count(record)
    errors: list[str] = []
    missing_fields = PHASE11_REVIEW_RECORD_REQUIRED_FIELDS - set(record)
    if missing_fields:
        errors.append("phase11_review_record_required_field_missing")
    unknown_fields = set(str(key) for key in record) - PHASE11_REVIEW_RECORD_ALLOWED_FIELDS
    if unknown_fields:
        errors.append("phase11_review_record_unknown_field")
    if record.get("schema_version") != 1:
        errors.append("phase11_review_record_schema_version_invalid")
    version = record.get("review_record_contract_version")
    if version != PHASE11_REVIEW_RECORD_CONTRACT_VERSION:
        classification = "unsupported_version" if isinstance(version, int) else "malformed"
        return _invalid_review_record_result(
            ("phase11_review_record_contract_version_unsupported",),
            classification,
            privacy_violation_count=privacy_violations,
        )
    if record.get("review_record_kind") != PHASE11_REVIEW_RECORD_KIND:
        errors.append("phase11_review_record_kind_invalid")
    domain = _safe_domain(record.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11_review_record_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11_review_record_domain_mismatch")
    for field in ("planning_only", "metadata_only", "sanitized"):
        if record.get(field) is not True:
            errors.append("phase11_review_record_required_true_flag_missing")
            break
    for field in ("execution_permitted", "real_mode_runtime_enabled"):
        if record.get(field) is not False:
            errors.append("phase11_review_record_runtime_implied")
            break
    if record.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase11_review_record_runtime_stage_invalid")
    if tuple(record.get("required_gates") or ()) != REAL_MODE_REQUIRED_GATES:
        errors.append("phase11_review_record_required_gates_invalid")
    if privacy_violations:
        errors.append("phase11_review_record_privacy_boundary")

    review_errors, reviewed, missing, rejected = _review_record_body_errors(record)
    errors.extend(review_errors)

    expected_status = _review_record_status(reviewed, missing, rejected)
    if record.get("record_status") != expected_status:
        errors.append("phase11_review_record_status_contradiction")
    if list(reviewed) != list(record.get("reviewed_gates") or ()):
        errors.append("phase11_review_record_gate_summary_contradiction")
    if list(missing) != list(record.get("missing_gates") or ()):
        errors.append("phase11_review_record_gate_summary_contradiction")
    if list(rejected) != list(record.get("rejected_gates") or ()):
        errors.append("phase11_review_record_gate_summary_contradiction")
    if record.get("reviewed_gate_count") != len(reviewed):
        errors.append("phase11_review_record_gate_count_contradiction")
    if record.get("missing_gate_count") != len(missing):
        errors.append("phase11_review_record_gate_count_contradiction")
    if record.get("rejected_gate_count") != len(rejected):
        errors.append("phase11_review_record_gate_count_contradiction")

    if errors:
        return _invalid_review_record_result(
            tuple(sorted(set(errors))),
            "incompatible",
            privacy_violation_count=privacy_violations,
        )
    if rejected:
        return Phase11ReviewRecordValidationResult(
            classification="rejected",
            valid=False,
            errors=("phase11_review_record_rejected",),
            privacy_violation_count=0,
            sanitized_record=dict(record),
            reviewed_gate_count=len(reviewed),
            missing_gate_count=len(missing),
            rejected_gate_count=len(rejected),
        )
    if missing:
        return Phase11ReviewRecordValidationResult(
            classification="incomplete",
            valid=False,
            errors=("phase11_review_record_required_review_missing",),
            privacy_violation_count=0,
            sanitized_record=dict(record),
            reviewed_gate_count=len(reviewed),
            missing_gate_count=len(missing),
            rejected_gate_count=0,
        )
    return Phase11ReviewRecordValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_record=dict(record),
        reviewed_gate_count=len(reviewed),
        missing_gate_count=0,
        rejected_gate_count=0,
    )


def validate_phase11_preflight_dossier(
    dossier: object,
    *,
    expected_domain: str | None = None,
) -> Phase11PreflightDossierValidationResult:
    """Validate a Phase 11C preflight dossier and fail closed."""

    if not isinstance(dossier, Mapping):
        return _invalid_preflight_dossier_result(
            ("phase11_preflight_dossier_not_object",),
            "malformed",
        )

    privacy_violations = _privacy_violation_count(dossier)
    errors: list[str] = []
    missing_fields = PHASE11_PREFLIGHT_DOSSIER_REQUIRED_FIELDS - set(dossier)
    if missing_fields:
        errors.append("phase11_preflight_required_field_missing")
    unknown_fields = set(str(key) for key in dossier) - (PHASE11_PREFLIGHT_DOSSIER_ALLOWED_FIELDS)
    if unknown_fields:
        errors.append("phase11_preflight_unknown_field")
    if dossier.get("schema_version") != 1:
        errors.append("phase11_preflight_schema_version_invalid")
    version = dossier.get("preflight_dossier_contract_version")
    if version != PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION:
        classification = "unsupported_version" if isinstance(version, int) else "malformed"
        return _invalid_preflight_dossier_result(
            ("phase11_preflight_contract_version_unsupported",),
            classification,
            privacy_violation_count=privacy_violations,
        )
    if dossier.get("preflight_dossier_kind") != PHASE11_PREFLIGHT_DOSSIER_KIND:
        errors.append("phase11_preflight_kind_invalid")
    domain = _safe_domain(dossier.get("domain"))
    if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        errors.append("phase11_preflight_domain_invalid")
    if expected_domain is not None and domain != _safe_domain(expected_domain):
        errors.append("phase11_preflight_domain_mismatch")
    for field in ("planning_only", "metadata_only", "sanitized"):
        if dossier.get(field) is not True:
            errors.append("phase11_preflight_required_true_flag_missing")
            break
    for field in ("execution_permitted", "real_mode_runtime_enabled"):
        if dossier.get(field) is not False:
            errors.append("phase11_preflight_runtime_implied")
            break
    if dossier.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase11_preflight_runtime_stage_invalid")
    if dossier.get("contract_spec_version") != PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION:
        errors.append("phase11_preflight_contract_spec_version_invalid")
    if dossier.get("review_record_contract_version") != PHASE11_REVIEW_RECORD_CONTRACT_VERSION:
        errors.append("phase11_preflight_review_record_version_invalid")
    required_gates = dossier.get("required_gates")
    if not isinstance(required_gates, list) or tuple(required_gates) != REAL_MODE_REQUIRED_GATES:
        errors.append("phase11_preflight_required_gates_invalid")
    if privacy_violations:
        errors.append("phase11_preflight_privacy_boundary")

    fingerprint_errors = _phase11_preflight_fingerprint_errors(dossier)
    errors.extend(fingerprint_errors)
    gate_errors, reviewed, missing, rejected = _phase11_preflight_gate_errors(dossier)
    errors.extend(gate_errors)

    blocking_reasons = dossier.get("blocking_reasons")
    if not isinstance(blocking_reasons, list) or not all(
        isinstance(reason, str) for reason in blocking_reasons
    ):
        errors.append("phase11_preflight_blocking_reasons_invalid")
        safe_blocking_reasons: tuple[str, ...] = ()
    else:
        safe_blocking_reasons = tuple(blocking_reasons)

    expected_status = _phase11_preflight_status(
        missing_count=len(missing),
        rejected_count=len(rejected),
        blocking_reasons=safe_blocking_reasons,
    )
    if dossier.get("status") != expected_status:
        errors.append("phase11_preflight_status_contradiction")
    if dossier.get("reviewed_gate_count") != len(reviewed):
        errors.append("phase11_preflight_gate_count_contradiction")
    if dossier.get("missing_gate_count") != len(missing):
        errors.append("phase11_preflight_gate_count_contradiction")
    if dossier.get("rejected_gate_count") != len(rejected):
        errors.append("phase11_preflight_gate_count_contradiction")
    if errors:
        return _invalid_preflight_dossier_result(
            tuple(sorted(set(errors))),
            "incompatible",
            privacy_violation_count=privacy_violations,
        )

    classification = (
        "compatible"
        if not missing and not rejected and not dossier.get("blocking_reasons")
        else "incomplete"
        if missing and not rejected
        else "rejected"
    )
    return Phase11PreflightDossierValidationResult(
        classification=classification,
        valid=classification == "compatible",
        errors=()
        if classification == "compatible"
        else (
            ("phase11_preflight_required_record_missing",)
            if classification == "incomplete"
            else ("phase11_preflight_rejected",)
        ),
        privacy_violation_count=0,
        sanitized_dossier=dict(dossier),
        reviewed_gate_count=len(reviewed),
        missing_gate_count=len(missing),
        rejected_gate_count=len(rejected),
    )


def phase11_review_record_status_summary(
    review_record: Mapping[str, object] | None = None,
    *,
    domain: str,
) -> dict[str, object]:
    """Return compact review-record status safe for public surfaces."""

    if _looks_like_phase11_review_record(review_record):
        result = validate_phase11_review_record(
            review_record,
            expected_domain=domain,
        )
        record_status = result.record_status
        reviewed_count = result.reviewed_gate_count
        missing_count = result.missing_gate_count
        rejected_count = result.rejected_gate_count
    else:
        missing_count = len(REAL_MODE_REQUIRED_GATES)
        reviewed_count = 0
        rejected_count = 0
        record_status = PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE

    return {
        "schema_version": 1,
        "review_record_contract_version": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "domain": _safe_domain(domain),
        "review_record_status": record_status,
        "reviewed_gate_count": reviewed_count,
        "missing_gate_count": missing_count,
        "rejected_gate_count": rejected_count,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def phase11_review_record_gate_acknowledgements(
    review_record: Mapping[str, object] | None,
    *,
    domain: str,
) -> dict[str, bool]:
    """Convert a safe Phase 11B review record into readiness-gate booleans."""

    if not _looks_like_phase11_review_record(review_record):
        return dict(review_record or {})
    result = validate_phase11_review_record(review_record, expected_domain=domain)
    if result.classification not in {"compatible", "incomplete"}:
        return {}
    reviews = result.sanitized_record.get("reviews")
    if not isinstance(reviews, Mapping):
        return {}
    return {
        field: (
            isinstance(reviews.get(field), Mapping) and reviews[field].get("status") == "reviewed"
        )
        for field, _gate, _review_type, _scope in PHASE11_REVIEW_RECORD_SPECS
    }


def phase11_document_ingestion_contract_spec(
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the future document-ingestion contract/spec as metadata only."""

    review_gate_record = phase11_review_record_gate_acknowledgements(
        review_record,
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    gate = evaluate_real_mode_readiness(
        provider_kind="document-fixture",
        adapter_kind="metadata-document-adapter",
        current_mode="fixture-only",
        review_record=review_gate_record,
    ).to_dict()
    return {
        **_common_spec_fields(PHASE11_DOCUMENT_DOMAIN, "fixture-only", gate),
        "p11b_review_record_status": phase11_review_record_status_summary(
            review_record,
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        "required_contracts": list(PHASE11_DOCUMENT_REQUIRED_CONTRACTS),
        "closed_runtime_flags": {
            "document_ingestion": False,
            "file_crawling": False,
            "pdf_parsing": False,
            "network_calls": False,
            "body_export": False,
            "origin_identifier_export": False,
            "local_name_export": False,
            "path_export": False,
            "url_export": False,
            "provider_detail_export": False,
            "parser_execution": False,
            "runtime_execution": False,
        },
        "metadata_staging_contract": {
            "contract_status": "required-before-real-mode",
            "counts_status_only": True,
            "metadata_only": True,
            "body_export": False,
            "origin_identifier_export": False,
            "local_name_export": False,
            "path_export": False,
            "url_export": False,
        },
        "parser_boundary_contract": {
            "contract_status": "required-before-real-mode",
            "parser_execution": False,
            "pdf_parsing": False,
            "file_crawling": False,
            "provider_detail_export": False,
            "metadata_only": True,
        },
        "artifact_privacy_contract": {
            "contract_status": "required-before-real-mode",
            "metadata_only": True,
            "body_export": False,
            "origin_identifier_export": False,
            "local_name_export": False,
            "path_export": False,
            "url_export": False,
        },
        "license_source_review_contract": {
            "contract_status": "required-before-real-mode",
            "review_required": True,
            "runtime_execution": False,
            "dependency_execution": False,
        },
    }


def phase11_wifi_csi_rf_booth_contract_spec(
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the future RF booth/WiFi CSI contract/spec as metadata only."""

    review_gate_record = phase11_review_record_gate_acknowledgements(
        review_record,
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    gate = evaluate_real_mode_readiness(
        provider_kind="wifi-csi",
        adapter_kind="metadata-wifi-csi-source-adapter",
        current_mode="reference-only",
        review_record=review_gate_record,
    ).to_dict()
    return {
        **_common_spec_fields(PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "reference-only", gate),
        "p11b_review_record_status": phase11_review_record_status_summary(
            review_record,
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        "required_contracts": list(PHASE11_RF_BOOTH_REQUIRED_CONTRACTS),
        "closed_runtime_flags": {
            "hardware_access": False,
            "capture_execution": False,
            "packet_capture": False,
            "monitor_mode": False,
            "wifi_network_probing": False,
            "network_calls": False,
            "esp32_flashing": False,
            "router_ap_control": False,
            "mqtt_udp_listener": False,
            "smart_home_bridge": False,
            "model_download": False,
            "model_execution": False,
            "rf_signal_export": False,
            "data_export": False,
            "runtime_execution": False,
        },
        "booth_hardware_topology_metadata_contract": {
            "contract_status": "required-before-real-mode",
            "booth_size_class": "small-controlled-booth",
            "subject_scope": "single-intended-subject",
            "fixed_ap_role": "role-metadata-only",
            "receiver_role_count_range": "four-to-six",
            "empty_booth_baseline_concept": True,
            "booth_role_metadata_only": True,
            "topology_claim": False,
            "hardware_access": False,
        },
        "consent_privacy_contract": {
            "contract_status": "required-before-real-mode",
            "review_required": True,
            "rf_signal_export": False,
            "data_export": False,
            "capture_execution": False,
        },
        "hardware_review_contract": {
            "contract_status": "required-before-real-mode",
            "review_required": True,
            "hardware_access": False,
            "esp32_flashing": False,
            "packet_capture": False,
            "monitor_mode": False,
        },
        "model_artifact_review_contract": {
            "contract_status": "required-before-real-mode",
            "review_required": True,
            "model_download": False,
            "model_execution": False,
        },
        "network_policy_contract": {
            "contract_status": "required-before-real-mode",
            "review_required": True,
            "network_calls": False,
            "router_ap_control": False,
            "mqtt_udp_listener": False,
            "smart_home_bridge": False,
        },
    }


def phase11_real_mode_contract_bundle() -> dict[str, object]:
    """Return both Phase 11A specs without enabling runtime behavior."""

    document = phase11_document_ingestion_contract_spec()
    rf_booth = phase11_wifi_csi_rf_booth_contract_spec()
    return {
        "schema_version": 1,
        "contract_spec_version": PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
        "contract_spec_kind": PHASE11_REAL_MODE_CONTRACT_SPEC_KIND,
        "phase": PHASE11_REAL_MODE_CONTRACT_PHASE,
        "status": PHASE11_REAL_MODE_CONTRACT_STATUS,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "required_contracts": [
            PHASE11_DOCUMENT_DOMAIN,
            PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ],
        "document_contract_spec": document,
        "rf_booth_contract_spec": rf_booth,
    }


def phase11_contract_status_summary(
    *,
    domain: str,
    readiness_gate: Mapping[str, object] | None,
) -> dict[str, object]:
    """Return compact public status safe for provider and adapter summaries."""

    gate = real_mode_readiness_gate_summary(readiness_gate)
    return {
        "schema_version": 1,
        "contract_spec_version": PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
        "domain": _safe_domain(domain),
        "status": PHASE11_REAL_MODE_CONTRACT_STATUS,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": gate.get("runtime_stage") or REAL_MODE_PHASE_RUNTIME,
        "readiness_gate_status": gate.get("status") or REAL_MODE_GATE_BLOCKED_STATUS,
        "readiness_gate_missing_count": _safe_int(gate.get("missing_gate_count")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase11_contract_spec(
    spec: object,
) -> Phase11ContractSpecValidationResult:
    """Validate a Phase 11A contract/spec payload without echoing unsafe values."""

    if not isinstance(spec, Mapping):
        return _invalid_result(("phase11_contract_spec_not_object",), "malformed")

    errors: list[str] = []
    if spec.get("schema_version") != 1:
        errors.append("phase11_contract_schema_version_invalid")
    if spec.get("contract_spec_version") != PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION:
        errors.append("phase11_contract_spec_version_invalid")
    if spec.get("contract_spec_kind") != PHASE11_REAL_MODE_CONTRACT_SPEC_KIND:
        errors.append("phase11_contract_spec_kind_invalid")
    if spec.get("phase") != PHASE11_REAL_MODE_CONTRACT_PHASE:
        errors.append("phase11_contract_phase_invalid")
    if spec.get("status") != PHASE11_REAL_MODE_CONTRACT_STATUS:
        errors.append("phase11_contract_status_invalid")
    for field in ("planning_only", "metadata_only", "sanitized"):
        if spec.get(field) is not True:
            errors.append("phase11_contract_required_true_flag_missing")
            break
    for field in ("execution_permitted", "real_mode_runtime_enabled"):
        if spec.get(field) is not False:
            errors.append("phase11_contract_closed_flag_not_preserved")
            break
    if spec.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase11_contract_runtime_stage_invalid")

    domain = spec.get("domain")
    if domain == PHASE11_DOCUMENT_DOMAIN:
        if tuple(spec.get("required_contracts") or ()) != PHASE11_DOCUMENT_REQUIRED_CONTRACTS:
            errors.append("phase11_contract_required_contracts_invalid")
    elif domain == PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN:
        if tuple(spec.get("required_contracts") or ()) != PHASE11_RF_BOOTH_REQUIRED_CONTRACTS:
            errors.append("phase11_contract_required_contracts_invalid")
    else:
        errors.append("phase11_contract_domain_invalid")

    gate = real_mode_readiness_gate_summary(spec.get("readiness_gate"))
    if not gate:
        errors.append("phase11_contract_readiness_gate_missing")
    else:
        if gate["execution_permitted"] is not False:
            errors.append("phase11_contract_gate_execution_enabled")
        if gate["real_mode_runtime_enabled"] is not False:
            errors.append("phase11_contract_gate_runtime_enabled")

    review_status = spec.get("p11b_review_record_status")
    if isinstance(review_status, Mapping):
        if review_status.get("execution_permitted") is not False:
            errors.append("phase11_contract_review_status_runtime_enabled")
        if review_status.get("real_mode_runtime_enabled") is not False:
            errors.append("phase11_contract_review_status_runtime_enabled")
        if review_status.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
            errors.append("phase11_contract_review_status_runtime_enabled")

    errors.extend(_unknown_field_errors(spec))
    privacy_violations = _privacy_violation_count(spec)
    if privacy_violations:
        errors.append("phase11_contract_privacy_boundary")

    closed_flags = spec.get("closed_runtime_flags")
    if not isinstance(closed_flags, Mapping):
        errors.append("phase11_contract_closed_flags_missing")
    else:
        for field, value in closed_flags.items():
            if field in PHASE11_REQUIRED_FALSE_FLAGS and value is not False:
                errors.append("phase11_contract_closed_flag_not_preserved")
                break

    if errors:
        return _invalid_result(
            tuple(sorted(set(errors))),
            "incompatible",
            privacy_violation_count=privacy_violations,
        )

    return Phase11ContractSpecValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_spec=dict(spec),
    )


def rejected_phase11_contract_spec(
    domain: str = "unknown",
    category: str = "phase11-contract-spec-rejected",
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "contract_spec_version": PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
        "contract_spec_kind": PHASE11_REAL_MODE_CONTRACT_SPEC_KIND,
        "phase": PHASE11_REAL_MODE_CONTRACT_PHASE,
        "domain": _safe_domain(domain),
        "status": "rejected-fail-closed",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "readiness_gate": real_mode_readiness_gate_summary(
            evaluate_real_mode_readiness(
                provider_kind="unknown-provider",
                adapter_kind="unknown-adapter",
                current_mode="fixture-or-reference-only",
            ).to_dict()
        ),
        "required_contracts": [],
        "closed_runtime_flags": {
            "runtime_execution": False,
            "network_calls": False,
            "hardware_access": False,
            "model_execution": False,
            "data_export": False,
        },
        "contract_status": _safe_category(category),
    }


def rejected_phase11_review_record(
    domain: str = "unknown",
) -> dict[str, object]:
    """Return a sanitized rejected review record without echoing input."""

    return phase11_review_record(
        domain=_safe_domain(domain),
        reviewed_gates=(),
        rejected_gates=("privacy-review",),
    )


def _common_spec_fields(
    domain: str,
    current_mode: str,
    readiness_gate: Mapping[str, object],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "contract_spec_version": PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
        "contract_spec_kind": PHASE11_REAL_MODE_CONTRACT_SPEC_KIND,
        "phase": PHASE11_REAL_MODE_CONTRACT_PHASE,
        "domain": domain,
        "status": PHASE11_REAL_MODE_CONTRACT_STATUS,
        "current_mode": current_mode,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "readiness_gate": real_mode_readiness_gate_summary(readiness_gate),
    }


def _invalid_result(
    errors: tuple[str, ...],
    classification: str,
    *,
    privacy_violation_count: int = 0,
) -> Phase11ContractSpecValidationResult:
    return Phase11ContractSpecValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_spec=rejected_phase11_contract_spec(
            category=(
                "phase11-contract-privacy-boundary"
                if privacy_violation_count
                else "phase11-contract-invalid"
            )
        ),
    )


def _invalid_review_record_result(
    errors: tuple[str, ...],
    classification: str,
    *,
    privacy_violation_count: int = 0,
) -> Phase11ReviewRecordValidationResult:
    return Phase11ReviewRecordValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=rejected_phase11_review_record(),
        reviewed_gate_count=0,
        missing_gate_count=len(REAL_MODE_REQUIRED_GATES),
        rejected_gate_count=1,
    )


def _missing_phase11_review_record_result(
    *,
    domain: str,
) -> Phase11ReviewRecordValidationResult:
    return Phase11ReviewRecordValidationResult(
        classification="incomplete",
        valid=False,
        errors=("phase11_preflight_review_record_missing",),
        privacy_violation_count=0,
        sanitized_record=phase11_review_record(
            domain=_safe_domain(domain),
            reviewed_gates=(),
        ),
        reviewed_gate_count=0,
        missing_gate_count=len(REAL_MODE_REQUIRED_GATES),
        rejected_gate_count=0,
    )


def _invalid_preflight_dossier_result(
    errors: tuple[str, ...],
    classification: str,
    *,
    privacy_violation_count: int = 0,
) -> Phase11PreflightDossierValidationResult:
    return Phase11PreflightDossierValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_dossier=rejected_phase11_preflight_dossier(),
        reviewed_gate_count=0,
        missing_gate_count=len(REAL_MODE_REQUIRED_GATES),
        rejected_gate_count=0,
    )


def rejected_phase11_preflight_dossier(
    domain: str = "unknown",
) -> dict[str, object]:
    """Return sanitized rejected preflight metadata without echoing input."""

    payload = {
        "schema_version": 1,
        "preflight_dossier_contract_version": (PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION),
        "preflight_dossier_kind": PHASE11_PREFLIGHT_DOSSIER_KIND,
        "packet_id": None,
        "packet_fingerprint": None,
        "domain": _safe_domain(domain),
        "status": PHASE11_PREFLIGHT_STATUS_REJECTED,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
        "contract_spec_version": PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
        "review_record_contract_version": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "contract_spec_label": "rejected-p11a-contract-v1",
        "review_record_label": "rejected-p11b-review-record-v1",
        "included_record_fingerprints": {
            "contract_spec_sha256": _phase11_payload_sha256({}),
            "review_record_sha256": _phase11_payload_sha256({}),
        },
        "required_gates": list(REAL_MODE_REQUIRED_GATES),
        "gates": [
            {
                "gate_id": gate,
                "contract_required": True,
                "review_status": "missing",
                "preflight_status": "missing",
                "blocking_reason": "preflight-invalid",
                "execution_permitted": False,
            }
            for gate in REAL_MODE_REQUIRED_GATES
        ],
        "reviewed_gate_count": 0,
        "missing_gate_count": len(REAL_MODE_REQUIRED_GATES),
        "rejected_gate_count": 0,
        "blocking_reasons": ["preflight-invalid"],
    }
    return _finalize_phase11_preflight_dossier(payload)


def rejected_phase11_reviewer_signoff_metadata() -> dict[str, object]:
    """Return sanitized rejected signoff metadata without echoing input."""

    return phase11_reviewer_signoff_metadata(
        reviewer_label="p11d-rejected-reviewer",
        verdict=PHASE11_SIGNOFF_VERDICT_REJECTED,
        review_scope="rejected-audit",
    )


def rejected_phase11_dossier_decision_record() -> dict[str, object]:
    """Return sanitized rejected decision metadata without echoing input."""

    return phase11_dossier_decision_record(
        rejected_phase11_preflight_dossier(),
        decision=PHASE11_LIFECYCLE_DECISION_REJECTED,
        decision_reason="audit-invalid",
    )


def rejected_phase11_dossier_lifecycle_record() -> dict[str, object]:
    """Return sanitized rejected lifecycle metadata without echoing input."""

    return phase11_dossier_lifecycle_record(
        rejected_phase11_preflight_dossier(),
        lifecycle_stage=PHASE11_LIFECYCLE_STAGE_REJECTED,
        signoff=rejected_phase11_reviewer_signoff_metadata(),
        decision_record=rejected_phase11_dossier_decision_record(),
    )


def rejected_phase11_export_retention_policy() -> dict[str, object]:
    """Return sanitized rejected Phase 11E export policy metadata."""

    return phase11_export_retention_policy(domain="unknown")


def rejected_phase11_reviewer_scope_coverage_summary() -> dict[str, object]:
    """Return sanitized rejected Phase 11E coverage metadata."""

    payload = {
        "schema_version": 1,
        "coverage_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "coverage_kind": PHASE11_REVIEWER_SCOPE_COVERAGE_KIND,
        "coverage_id": None,
        "coverage_fingerprint": None,
        "domain": "unknown",
        "reviewer_scope_label": "planning-review-missing",
        "required_gates": list(REAL_MODE_REQUIRED_GATES),
        "covered_gates": [],
        "missing_gates": list(REAL_MODE_REQUIRED_GATES),
        "gate_scope_labels": {gate: "planning-review-missing" for gate in REAL_MODE_REQUIRED_GATES},
        "coverage_complete": False,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "coverage")


def rejected_phase11_change_control_record() -> dict[str, object]:
    """Return sanitized rejected Phase 11E change-control metadata."""

    current = _phase11_lifecycle_ref(rejected_phase11_dossier_lifecycle_record())
    payload = {
        "schema_version": 1,
        "change_control_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "change_control_kind": PHASE11_CHANGE_CONTROL_KIND,
        "change_control_id": None,
        "change_control_fingerprint": None,
        "domain": current["domain"],
        "prior_lifecycle_record_label": "p11d-redacted-record",
        "prior_lifecycle_record_fingerprint": _phase11_payload_sha256({}),
        "current_lifecycle_record_label": current["record_label"],
        "current_lifecycle_record_fingerprint": current["record_fingerprint"],
        "change_timestamp": "2026-06-09T00:00:00Z",
        "change_reason": PHASE11_CHANGE_CONTROL_REASON,
        "reviewer_scope_label": "planning-audit",
        "decision": PHASE11_LIFECYCLE_DECISION_REJECTED,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "change")


def rejected_phase11_supersession_chain() -> dict[str, object]:
    """Return sanitized rejected Phase 11E supersession metadata."""

    return phase11_supersession_chain(
        (rejected_phase11_dossier_lifecycle_record(),),
        domain="unknown",
    )


def rejected_phase11_audit_index() -> dict[str, object]:
    """Return sanitized rejected Phase 11E audit-index metadata."""

    entry = _phase11_audit_index_entry(
        _phase11_lifecycle_ref(rejected_phase11_dossier_lifecycle_record())
    )
    stage_counts = {stage: 0 for stage in PHASE11_LIFECYCLE_STAGE_VALUES}
    stage_counts[PHASE11_LIFECYCLE_STAGE_REJECTED] = 1
    decision_counts = {decision: 0 for decision in PHASE11_LIFECYCLE_DECISION_VALUES}
    decision_counts[PHASE11_LIFECYCLE_DECISION_REJECTED] = 1
    payload = {
        "schema_version": 1,
        "audit_index_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "audit_index_kind": PHASE11_AUDIT_INDEX_KIND,
        "index_id": None,
        "index_fingerprint": None,
        "domain_scope": "multi-domain",
        "status": PHASE11_AUDIT_INDEX_REJECTED_STATUS,
        "included_dossier_packet_labels": [entry["dossier_packet_label"]],
        "included_lifecycle_record_labels": [entry["lifecycle_record_label"]],
        "included_decision_record_labels": [entry["decision_record_label"]],
        "included_record_fingerprints": [
            entry["dossier_packet_fingerprint"],
            entry["lifecycle_record_fingerprint"],
            entry["decision_record_fingerprint"],
        ],
        "lifecycle_stage_counts": stage_counts,
        "decision_counts": decision_counts,
        "reviewer_scope_coverage": [rejected_phase11_reviewer_scope_coverage_summary()],
        "supersession_chains": [rejected_phase11_supersession_chain()],
        "change_control_records": [rejected_phase11_change_control_record()],
        "export_retention_policies": [rejected_phase11_export_retention_policy()],
        "entries": [entry],
        "entry_count": 1,
        "created_count": 0,
        "reviewed_count": 0,
        "superseded_count": 0,
        "rejected_count": 1,
        "archived_count": 0,
        "decision_recorded_count": 0,
        "blocking_count": _safe_int(entry["blocking_reason_count"]),
        "rejection_count": 1,
        "deterministic_ordering": "sanitized-label-hash-v1",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11e_record(payload, "index")


def rejected_phase11_audit_handoff_record() -> dict[str, object]:
    """Return sanitized rejected Phase 11F handoff metadata."""

    index = rejected_phase11_audit_index()
    entries = _phase11f_domain_entries(index, "unknown")
    payload = {
        "schema_version": 1,
        "audit_handoff_contract_version": PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION,
        "audit_handoff_kind": PHASE11_AUDIT_HANDOFF_KIND,
        "handoff_id": None,
        "handoff_fingerprint": None,
        "domain": "unknown",
        "status": PHASE11_AUDIT_HANDOFF_REJECTED_STATUS,
        "contract_versions": _phase11f_contract_versions(),
        "audit_index_label": _safe_phase11e_record_id(index.get("index_id")),
        "audit_index_fingerprint": _safe_sha256(index.get("index_fingerprint")),
        "audit_index_status": _safe_audit_index_status(index.get("status")),
        "audit_index_entry_count": len(entries),
        "lifecycle_status_counts": _phase11f_lifecycle_status_counts(entries),
        "reviewer_scope_coverage_summary": _phase11f_coverage_summary(
            index,
            "unknown",
            entries,
        ),
        "retention_export_policy_summary": _phase11f_retention_summary(
            index,
            "unknown",
        ),
        "blocking_count": sum(_safe_int(entry.get("blocking_reason_count")) for entry in entries),
        "rejection_count": 1,
        "unresolved_review_count": len(REAL_MODE_REQUIRED_GATES),
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11f_record(payload)


def rejected_phase11_handoff_acceptance_record() -> dict[str, object]:
    """Return sanitized rejected Phase 11G acceptance metadata."""

    handoff = rejected_phase11_audit_handoff_record()
    handoff_hash = _safe_sha256(handoff.get("handoff_fingerprint"))
    payload = {
        "schema_version": 1,
        "handoff_acceptance_contract_version": (PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION),
        "handoff_acceptance_kind": PHASE11_HANDOFF_ACCEPTANCE_KIND,
        "acceptance_id": None,
        "acceptance_fingerprint": None,
        "domain": "unknown",
        "status": PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS,
        "contract_versions": _phase11g_contract_versions(),
        "source_handoff_label": _safe_phase11f_record_id(handoff.get("handoff_id")),
        "source_handoff_hash": handoff_hash,
        "handoff_fingerprint": handoff_hash,
        "handoff_status": PHASE11_AUDIT_HANDOFF_REJECTED_STATUS,
        "accepted_for_planning": False,
        "blocked": True,
        "stale": False,
        "missing_review_count": len(REAL_MODE_REQUIRED_GATES),
        "unresolved_review_count": len(REAL_MODE_REQUIRED_GATES),
        "rejection_reasons": ["source-handoff-rejected"],
        "blocking_reasons": ["source-handoff-rejected"],
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11g_record(payload)


def rejected_phase11_acceptance_followup_record() -> dict[str, object]:
    """Return sanitized rejected Phase 11H follow-up metadata."""

    payload = {
        "schema_version": 1,
        "acceptance_followup_contract_version": (PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION),
        "followup_kind": PHASE11_ACCEPTANCE_FOLLOWUP_KIND,
        "followup_id": None,
        "domain": "unknown",
        "followup_type": PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE,
        "status": PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS,
        "contract_versions": _phase11h_contract_versions(),
        "source_acceptance_label": "p11g-redacted-record",
        "source_acceptance_hash": "0" * 64,
        "blocker_disposition_summary": "source-rejected",
        "reviewer_queue_summary": "needs-more-review",
        "stale_renewal_summary": "source-current",
        "unresolved_review_count": 0,
        "blocking_count": 0,
        "rejection_count": 1,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11h_record(payload)


def rejected_phase11_followup_queue_index() -> dict[str, object]:
    """Return sanitized rejected Phase 11I queue index metadata."""

    status_counts = _phase11i_zero_status_counts()
    status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS] = 1
    blocker_counts = {summary: 0 for summary in PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_SUMMARIES}
    blocker_counts["source-rejected"] = 1
    reviewer_counts = {summary: 0 for summary in PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_SUMMARIES}
    reviewer_counts["needs-more-review"] = 1
    stale_counts = {summary: 0 for summary in PHASE11_ACCEPTANCE_FOLLOWUP_STALE_SUMMARIES}
    stale_counts["source-current"] = 1
    payload = {
        "schema_version": 1,
        "queue_index_contract_version": PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION,
        "queue_index_kind": PHASE11_FOLLOWUP_QUEUE_INDEX_KIND,
        "queue_id": None,
        "queue_fingerprint": None,
        "domain": "unknown",
        "status": PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS,
        "contract_versions": _phase11i_contract_versions(),
        "included_followup_labels": ["p11h-redacted-record"],
        "included_followup_hashes": ["0" * 64],
        "queue_status_counts": status_counts,
        "blocker_disposition_counts": blocker_counts,
        "reviewer_queue_counts": reviewer_counts,
        "stale_renewal_counts": stale_counts,
        "entry_count": 1,
        "open_count": 0,
        "blocked_count": 0,
        "stale_count": 0,
        "unresolved_review_count": 0,
        "blocking_count": 0,
        "blocker_disposition_count": 0,
        "reviewer_queue_count": 0,
        "stale_renewal_count": 0,
        "needs_more_review_count": 1,
        "archived_count": 0,
        "rejected_count": 1,
        "resolved_for_planning_count": 0,
        "deterministic_ordering": "sanitized-followup-label-hash-v1",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11i_queue_index(payload)


def rejected_phase11_followup_queue_acceptance_check() -> dict[str, object]:
    """Return sanitized rejected Phase 11I queue acceptance metadata."""

    queue = rejected_phase11_followup_queue_index()
    payload = {
        "schema_version": 1,
        "queue_index_contract_version": PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION,
        "queue_acceptance_kind": PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_KIND,
        "acceptance_id": None,
        "acceptance_fingerprint": None,
        "queue_label": queue["queue_id"],
        "queue_fingerprint": queue["queue_fingerprint"],
        "domain": "unknown",
        "status": PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS,
        "contract_versions": _phase11i_contract_versions(),
        "queue_status_counts": queue["queue_status_counts"],
        "entry_count": 1,
        "unresolved_review_count": 0,
        "blocking_count": 0,
        "stale_count": 0,
        "archived_count": 0,
        "rejected_count": 1,
        "resolved_for_planning_count": 0,
        "reviewer_queue_count": 0,
        "blocker_disposition_count": 0,
        "needs_more_review_count": 1,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11i_acceptance_check(payload)


def rejected_phase11_decision_closeout_record() -> dict[str, object]:
    """Return sanitized rejected Phase 11J decision-closeout metadata."""

    queue = rejected_phase11_followup_queue_index()
    payload = {
        "schema_version": 1,
        "closeout_contract_version": PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION,
        "closeout_id": None,
        "contract_versions": _phase11j_contract_versions(),
        "domain": "unknown",
        "source_queue_label": queue["queue_id"],
        "source_queue_hash": queue["queue_fingerprint"],
        "closeout_decision": PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
        "closeout_status": PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
        "reviewer_disposition_summary": "queue-rejected",
        "unresolved_review_count": 0,
        "blocker_count": 0,
        "stale_count": 0,
        "archived_count": 0,
        "rejected_count": 1,
        "deferred_count": 0,
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11j_closeout(payload)


def rejected_phase11_review_trail_export_bundle() -> dict[str, object]:
    """Return sanitized rejected Phase 11K review-trail export metadata."""

    domain_closeouts = [
        {
            "domain_label": PHASE11_DOCUMENT_DOMAIN,
            "final_closeout_decision": PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
            "final_closeout_status": PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
            "unresolved_review_count": 0,
            "blocker_count": 0,
            "stale_count": 0,
        },
        {
            "domain_label": PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            "final_closeout_decision": PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
            "final_closeout_status": PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
            "unresolved_review_count": 0,
            "blocker_count": 0,
            "stale_count": 0,
        },
    ]
    payload = {
        "review_trail_export_contract_version": (PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION),
        "export_id": None,
        "phase_range": PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE,
        "covered_phase_count": PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT,
        "domain_labels": _phase11k_domain_labels(),
        "domain_closeouts": domain_closeouts,
        "readiness_gap_summary": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11k_review_trail_export(payload)


def rejected_phase11_runtime_authorization_gap_ledger() -> dict[str, object]:
    """Return sanitized rejected Phase 11L runtime gap ledger metadata."""

    domain_summaries = [
        {
            "domain_label": PHASE11_DOCUMENT_DOMAIN,
            "source_closeout_decision": PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
            "source_closeout_status": PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
            "unresolved_review_count": 0,
            "blocker_count": 0,
            "stale_count": 0,
            "missing_future_gate_count": len(
                PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES
            ),
        },
        {
            "domain_label": PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            "source_closeout_decision": PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION,
            "source_closeout_status": PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS,
            "unresolved_review_count": 0,
            "blocker_count": 0,
            "stale_count": 0,
            "missing_future_gate_count": len(
                PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES
            ),
        },
    ]
    payload = {
        "runtime_authorization_gap_ledger_contract_version": (
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION
        ),
        "ledger_id": None,
        "source_phase_range": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE),
        "covered_phase_count": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT),
        "domain_labels": _phase11k_domain_labels(),
        "domain_gap_summaries": domain_summaries,
        "authorization_status": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS),
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "missing_future_gates": list(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
        "missing_future_gate_count": len(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11l_runtime_gap_ledger(payload)


def rejected_phase11_planning_governance_closeout_index() -> dict[str, object]:
    """Return sanitized rejected Phase 11M governance closeout metadata."""

    payload = {
        "planning_governance_closeout_contract_version": (
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION
        ),
        "closeout_index_id": None,
        "phase_range": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
        "covered_phase_count": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT,
        "final_status": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
        "runtime_authorization_status": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS),
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "next_phase_requirement": (PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_NEXT_PHASE_REQUIREMENT),
        "gap_ledger_id": _safe_phase11l_ledger_id(
            rejected_phase11_runtime_authorization_gap_ledger().get("ledger_id")
        ),
        "gap_ledger_contract_version": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION),
        "gap_ledger_phase_range": (PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE),
        "domain_labels": _phase11k_domain_labels(),
        "domain_count": len(_phase11k_domain_labels()),
        "unresolved_review_count": 0,
        "blocker_count": 0,
        "stale_count": 0,
        "missing_future_gate_count": len(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase11m_governance_closeout(payload)


def _invalid_phase11d_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11LifecycleAuditValidationResult:
    return Phase11LifecycleAuditValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11e_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11AuditIndexValidationResult:
    return Phase11AuditIndexValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11f_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11AuditHandoffValidationResult:
    return Phase11AuditHandoffValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11g_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11HandoffAcceptanceValidationResult:
    return Phase11HandoffAcceptanceValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11h_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11AcceptanceFollowupValidationResult:
    return Phase11AcceptanceFollowupValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11i_queue_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11FollowupQueueValidationResult:
    return Phase11FollowupQueueValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11i_acceptance_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11FollowupQueueAcceptanceValidationResult:
    return Phase11FollowupQueueAcceptanceValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11j_closeout_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11DecisionCloseoutValidationResult:
    return Phase11DecisionCloseoutValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11k_export_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
) -> Phase11ReviewTrailExportValidationResult:
    return Phase11ReviewTrailExportValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11l_runtime_gap_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase11RuntimeAuthorizationGapLedgerValidationResult:
    return Phase11RuntimeAuthorizationGapLedgerValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase11m_governance_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase11PlanningGovernanceCloseoutValidationResult:
    return Phase11PlanningGovernanceCloseoutValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _phase11_review_entry(
    *,
    gate_id: str,
    review_type: str,
    review_scope: str,
    status: str,
) -> dict[str, object]:
    return {
        "gate_id": gate_id,
        "review_type": review_type,
        "status": status,
        "required": True,
        "safe_to_proceed": status == "reviewed",
        "runtime_permission": False,
        "metadata_only": True,
        "sanitized": True,
        "review_scope": review_scope,
    }


def _review_record_body_errors(
    record: Mapping[str, object],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    reviews = record.get("reviews")
    if not isinstance(reviews, Mapping):
        return (
            ("phase11_review_record_reviews_missing",),
            (),
            REAL_MODE_REQUIRED_GATES,
            (),
        )

    errors: list[str] = []
    reviewed: list[str] = []
    rejected: list[str] = []
    expected_fields = {field for field, _gate, _review_type, _scope in PHASE11_REVIEW_RECORD_SPECS}
    if set(str(key) for key in reviews) != expected_fields:
        errors.append("phase11_review_record_review_set_invalid")

    for field, gate, review_type, scope in PHASE11_REVIEW_RECORD_SPECS:
        entry = reviews.get(field)
        if not isinstance(entry, Mapping):
            errors.append("phase11_review_record_review_entry_missing")
            continue
        missing = PHASE11_REVIEW_ENTRY_REQUIRED_FIELDS - set(entry)
        if missing:
            errors.append("phase11_review_record_review_entry_field_missing")
        unknown = set(str(key) for key in entry) - PHASE11_REVIEW_ENTRY_ALLOWED_FIELDS
        if unknown:
            errors.append("phase11_review_record_review_entry_unknown_field")
        if entry.get("gate_id") != gate:
            errors.append("phase11_review_record_review_gate_invalid")
        if entry.get("review_type") != review_type:
            errors.append("phase11_review_record_review_type_invalid")
        if entry.get("review_scope") != scope:
            errors.append("phase11_review_record_review_scope_invalid")
        for required_true in ("required", "metadata_only", "sanitized"):
            if entry.get(required_true) is not True:
                errors.append("phase11_review_record_review_required_true_missing")
                break
        if entry.get("runtime_permission") is not False:
            errors.append("phase11_review_record_runtime_implied")
        status = entry.get("status")
        if status not in PHASE11_REVIEW_ENTRY_STATUS_VALUES:
            errors.append("phase11_review_record_review_status_invalid")
            continue
        safe = entry.get("safe_to_proceed")
        if status == "reviewed":
            if safe is not True:
                errors.append("phase11_review_record_status_contradiction")
            reviewed.append(gate)
        else:
            if safe is True:
                errors.append("phase11_review_record_status_contradiction")
            if status == "rejected":
                rejected.append(gate)

    reviewed_tuple = tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate in reviewed)
    rejected_tuple = tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate in rejected)
    missing_tuple = tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate not in reviewed_tuple)
    return (tuple(errors), reviewed_tuple, missing_tuple, rejected_tuple)


def _default_contract_spec_for_domain(
    domain: str,
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    if domain == PHASE11_DOCUMENT_DOMAIN:
        return phase11_document_ingestion_contract_spec(review_record)
    if domain == PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN:
        return phase11_wifi_csi_rf_booth_contract_spec(review_record)
    return rejected_phase11_contract_spec(domain=domain)


def _default_preflight_dossier_for_domain(domain: str) -> dict[str, object]:
    if domain == PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN:
        return phase11_wifi_csi_rf_booth_preflight_dossier()
    return phase11_document_ingestion_preflight_dossier()


def _phase11_review_record_label(
    review_record: Mapping[str, object] | None,
    *,
    domain: str,
) -> str:
    if _looks_like_phase11_review_record(review_record):
        return f"{domain}-p11b-review-record-v1"
    return f"{domain}-p11b-review-record-missing"


def _phase11_preflight_gate_statuses(
    review_result: Phase11ReviewRecordValidationResult,
    *,
    spec_result: Phase11ContractSpecValidationResult,
) -> list[dict[str, object]]:
    reviewed, missing, rejected = _phase11_review_result_gate_sets(review_result)
    spec_invalid = not spec_result.compatible
    gates: list[dict[str, object]] = []
    for gate in REAL_MODE_REQUIRED_GATES:
        if spec_invalid:
            review_status = "missing"
            preflight_status = "rejected"
            blocking_reason = "contract-spec-invalid"
        elif gate in rejected:
            review_status = "rejected"
            preflight_status = "rejected"
            blocking_reason = f"rejected:{gate}"
        elif gate in reviewed:
            review_status = "reviewed"
            preflight_status = "reviewed"
            blocking_reason = ""
        else:
            review_status = "missing"
            preflight_status = "missing"
            blocking_reason = f"missing:{gate}"
        gates.append(
            {
                "gate_id": gate,
                "contract_required": True,
                "review_status": review_status,
                "preflight_status": preflight_status,
                "blocking_reason": blocking_reason,
                "execution_permitted": False,
            }
        )
    return gates


def _phase11_review_result_gate_sets(
    result: Phase11ReviewRecordValidationResult,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    if result.classification not in {"compatible", "incomplete", "rejected"}:
        return ((), REAL_MODE_REQUIRED_GATES, ())
    record = result.sanitized_record
    reviewed = _ordered_gate_subset(record.get("reviewed_gates"))  # type: ignore[arg-type]
    rejected = _ordered_gate_subset(record.get("rejected_gates"))  # type: ignore[arg-type]
    missing = tuple(
        gate for gate in REAL_MODE_REQUIRED_GATES if gate not in reviewed and gate not in rejected
    )
    return reviewed, missing, rejected


def _phase11_preflight_blocking_reasons(
    *,
    spec_result: Phase11ContractSpecValidationResult,
    review_result: Phase11ReviewRecordValidationResult,
    gates: list[dict[str, object]],
) -> list[str]:
    reasons: list[str] = []
    if not spec_result.compatible:
        reasons.append("contract-spec-invalid")
    if review_result.classification in {"malformed", "incompatible", "unsupported_version"}:
        reasons.append("review-record-invalid")
    elif review_result.classification == "incomplete":
        reasons.append("review-record-incomplete")
    elif review_result.classification == "rejected":
        reasons.append("review-record-rejected")
    for gate in gates:
        reason = gate.get("blocking_reason")
        if isinstance(reason, str) and reason:
            reasons.append(reason)
    return list(dict.fromkeys(reasons))


def _phase11_preflight_status(
    *,
    missing_count: int,
    rejected_count: int,
    blocking_reasons: tuple[str, ...] | list[str],
) -> str:
    if rejected_count:
        return PHASE11_PREFLIGHT_STATUS_REJECTED
    if missing_count:
        return PHASE11_PREFLIGHT_STATUS_MISSING
    if blocking_reasons:
        return PHASE11_PREFLIGHT_STATUS_REJECTED
    return PHASE11_PREFLIGHT_STATUS_REVIEWED


def _phase11_preflight_gate_errors(
    dossier: Mapping[str, object],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    gates = dossier.get("gates")
    if not isinstance(gates, list):
        return (
            ("phase11_preflight_gates_missing",),
            (),
            REAL_MODE_REQUIRED_GATES,
            (),
        )
    errors: list[str] = []
    reviewed: list[str] = []
    missing: list[str] = []
    rejected: list[str] = []
    if len(gates) != len(REAL_MODE_REQUIRED_GATES):
        errors.append("phase11_preflight_gate_set_invalid")
    for index, expected_gate in enumerate(REAL_MODE_REQUIRED_GATES):
        entry = gates[index] if index < len(gates) else None
        if not isinstance(entry, Mapping):
            errors.append("phase11_preflight_gate_entry_missing")
            continue
        if PHASE11_PREFLIGHT_GATE_REQUIRED_FIELDS - set(entry):
            errors.append("phase11_preflight_gate_field_missing")
        if set(str(key) for key in entry) - PHASE11_PREFLIGHT_GATE_ALLOWED_FIELDS:
            errors.append("phase11_preflight_gate_unknown_field")
        if entry.get("gate_id") != expected_gate:
            errors.append("phase11_preflight_gate_id_invalid")
        if entry.get("contract_required") is not True:
            errors.append("phase11_preflight_gate_contract_required_invalid")
        if entry.get("execution_permitted") is not False:
            errors.append("phase11_preflight_runtime_implied")
        review_status = entry.get("review_status")
        preflight_status = entry.get("preflight_status")
        if review_status not in {"reviewed", "missing", "rejected"}:
            errors.append("phase11_preflight_gate_review_status_invalid")
        if preflight_status not in {"reviewed", "missing", "rejected"}:
            errors.append("phase11_preflight_gate_status_invalid")
            continue
        if preflight_status == "reviewed":
            if review_status != "reviewed" or entry.get("blocking_reason"):
                errors.append("phase11_preflight_gate_status_contradiction")
            reviewed.append(expected_gate)
        elif preflight_status == "missing":
            if review_status == "rejected":
                errors.append("phase11_preflight_gate_status_contradiction")
            missing.append(expected_gate)
        else:
            if not entry.get("blocking_reason"):
                errors.append("phase11_preflight_gate_status_contradiction")
            rejected.append(expected_gate)
    return (
        tuple(errors),
        tuple(reviewed),
        tuple(missing),
        tuple(rejected),
    )


def _phase11_preflight_fingerprint_errors(
    dossier: Mapping[str, object],
) -> tuple[str, ...]:
    errors: list[str] = []
    fingerprints = dossier.get("included_record_fingerprints")
    if not isinstance(fingerprints, Mapping):
        errors.append("phase11_preflight_fingerprints_missing")
    else:
        if PHASE11_PREFLIGHT_FINGERPRINT_REQUIRED_FIELDS - set(fingerprints):
            errors.append("phase11_preflight_fingerprint_field_missing")
        if set(str(key) for key in fingerprints) - PHASE11_PREFLIGHT_FINGERPRINT_REQUIRED_FIELDS:
            errors.append("phase11_preflight_fingerprint_unknown_field")
        for field in PHASE11_PREFLIGHT_FINGERPRINT_REQUIRED_FIELDS:
            if not _looks_sha256(fingerprints.get(field)):
                errors.append("phase11_preflight_fingerprint_invalid")
                break
    expected = _phase11_preflight_packet_fingerprint(dossier)
    if not _looks_sha256(expected):
        errors.append("phase11_preflight_payload_not_json")
        return tuple(errors)
    if dossier.get("packet_fingerprint") != expected:
        errors.append("phase11_preflight_packet_fingerprint_invalid")
    expected_id = f"p11c-preflight-{_safe_domain(dossier.get('domain'))}-{expected[:16]}"
    if dossier.get("packet_id") != expected_id:
        errors.append("phase11_preflight_packet_id_invalid")
    return tuple(errors)


def _finalize_phase11_preflight_dossier(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["packet_id"] = None
    payload["packet_fingerprint"] = None
    fingerprint = _phase11_preflight_packet_fingerprint(payload)
    payload["packet_fingerprint"] = fingerprint
    payload["packet_id"] = (
        f"p11c-preflight-{_safe_domain(payload.get('domain'))}-{fingerprint[:16]}"
    )
    return payload


def _phase11_preflight_packet_fingerprint(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["packet_id"] = None
    payload["packet_fingerprint"] = None
    return _phase11_payload_sha256(payload)


def _phase11_payload_sha256(value: object) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return ""
    return sha256(encoded).hexdigest()


def _looks_sha256(value: object) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text)


def _safe_sha256(value: object) -> str:
    text = str(value or "")
    return text if _looks_sha256(text) else ""


def _safe_preflight_packet_id(value: object) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    return "-".join(part for part in safe.split("-") if part)


def _safe_preflight_status(value: object) -> str:
    text = _safe_domain(value)
    if text in PHASE11_PREFLIGHT_DOSSIER_STATUS_VALUES:
        return text
    return PHASE11_PREFLIGHT_STATUS_REJECTED


def _looks_like_phase11_preflight_dossier(value: object) -> bool:
    return (
        isinstance(value, Mapping)
        and value.get("preflight_dossier_kind") == PHASE11_PREFLIGHT_DOSSIER_KIND
    )


def _finalize_phase11d_record(
    payload: dict[str, object],
    record_type: str,
) -> dict[str, object]:
    if record_type == "signoff":
        id_field = "signoff_id"
        fingerprint_field = "signoff_fingerprint"
        prefix = "p11d-signoff"
    elif record_type == "decision":
        id_field = "decision_id"
        fingerprint_field = "decision_fingerprint"
        prefix = "p11d-decision"
    else:
        id_field = "lifecycle_record_id"
        fingerprint_field = "lifecycle_record_fingerprint"
        prefix = "p11d-lifecycle"

    payload[id_field] = None
    payload[fingerprint_field] = None
    fingerprint = _phase11d_record_fingerprint(payload, record_type)
    payload[fingerprint_field] = fingerprint
    payload[id_field] = f"{prefix}-{fingerprint[:16]}"
    return payload


def _phase11d_record_fingerprint(
    value: Mapping[str, object],
    record_type: str,
) -> str:
    payload = dict(value)
    if record_type == "signoff":
        payload["signoff_id"] = None
        payload["signoff_fingerprint"] = None
    elif record_type == "decision":
        payload["decision_id"] = None
        payload["decision_fingerprint"] = None
    else:
        payload["lifecycle_record_id"] = None
        payload["lifecycle_record_fingerprint"] = None
    return _phase11_payload_sha256(payload)


def _finalize_phase11e_record(
    payload: dict[str, object],
    record_type: str,
) -> dict[str, object]:
    fields = {
        "index": ("index_id", "index_fingerprint", "p11e-index"),
        "change": (
            "change_control_id",
            "change_control_fingerprint",
            "p11e-change",
        ),
        "chain": ("chain_id", "chain_fingerprint", "p11e-chain"),
        "coverage": ("coverage_id", "coverage_fingerprint", "p11e-coverage"),
        "policy": ("policy_id", "policy_fingerprint", "p11e-policy"),
    }
    id_field, fingerprint_field, prefix = fields[record_type]
    payload[id_field] = None
    payload[fingerprint_field] = None
    fingerprint = _phase11e_record_fingerprint(payload, record_type)
    payload[fingerprint_field] = fingerprint
    payload[id_field] = f"{prefix}-{fingerprint[:16]}"
    return payload


def _phase11e_record_fingerprint(
    value: Mapping[str, object],
    record_type: str,
) -> str:
    payload = dict(value)
    if record_type == "index":
        payload["index_id"] = None
        payload["index_fingerprint"] = None
    elif record_type == "change":
        payload["change_control_id"] = None
        payload["change_control_fingerprint"] = None
    elif record_type == "chain":
        payload["chain_id"] = None
        payload["chain_fingerprint"] = None
    elif record_type == "coverage":
        payload["coverage_id"] = None
        payload["coverage_fingerprint"] = None
    elif record_type == "policy":
        payload["policy_id"] = None
        payload["policy_fingerprint"] = None
    return _phase11_payload_sha256(payload)


def _finalize_phase11f_record(payload: dict[str, object]) -> dict[str, object]:
    payload["handoff_id"] = None
    payload["handoff_fingerprint"] = None
    fingerprint = _phase11f_record_fingerprint(payload)
    payload["handoff_fingerprint"] = fingerprint
    payload["handoff_id"] = f"p11f-handoff-{fingerprint[:16]}"
    return payload


def _phase11f_record_fingerprint(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["handoff_id"] = None
    payload["handoff_fingerprint"] = None
    return _phase11_payload_sha256(payload)


def _finalize_phase11g_record(payload: dict[str, object]) -> dict[str, object]:
    payload["acceptance_id"] = None
    payload["acceptance_fingerprint"] = None
    fingerprint = _phase11g_record_fingerprint(payload)
    payload["acceptance_fingerprint"] = fingerprint
    payload["acceptance_id"] = f"p11g-acceptance-{fingerprint[:16]}"
    return payload


def _phase11g_record_fingerprint(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["acceptance_id"] = None
    payload["acceptance_fingerprint"] = None
    return _phase11_payload_sha256(payload)


def _finalize_phase11h_record(payload: dict[str, object]) -> dict[str, object]:
    payload["followup_id"] = None
    payload["followup_id"] = _phase11h_record_id(payload)
    return payload


def _phase11h_record_id(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["followup_id"] = None
    fingerprint = _phase11_payload_sha256(payload)
    if not _looks_sha256(fingerprint):
        return ""
    return f"p11h-followup-{fingerprint[:16]}"


def _phase11f_contract_versions() -> dict[str, int]:
    return {
        "phase11a_contract_spec": PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION,
        "phase11b_review_record": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "phase11c_preflight_dossier": PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION,
        "phase11d_lifecycle_audit": PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
        "phase11e_audit_index": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "phase11f_audit_handoff": PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION,
    }


def _phase11g_contract_versions() -> dict[str, int]:
    versions = _phase11f_contract_versions()
    versions["phase11g_handoff_acceptance"] = PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION
    return versions


def _phase11h_contract_versions() -> dict[str, int]:
    versions = _phase11g_contract_versions()
    versions["phase11h_acceptance_followup"] = PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION
    return versions


def _phase11h_default_acceptance_record(domain: str) -> Mapping[str, object]:
    if domain in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}:
        return phase11_handoff_acceptance_record(domain=domain)
    return rejected_phase11_handoff_acceptance_record()


def _phase11h_default_followup_type(
    *,
    accepted: bool,
    stale: bool,
    unresolved_count: int,
    blocking_count: int,
    rejection_count: int,
) -> str:
    if stale:
        return PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE
    if rejection_count:
        return PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE
    if unresolved_count:
        return PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE
    if blocking_count:
        return PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE
    if accepted:
        return PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE
    return PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE


def _phase11h_followup_status(
    followup_type: str,
    *,
    accepted: bool,
    stale: bool,
    unresolved_count: int,
    blocking_count: int,
    rejection_count: int,
    source_rejected: bool,
) -> str:
    if source_rejected or rejection_count:
        return PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS
    if followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE:
        return (
            PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS
            if stale
            else PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS
        )
    if followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE:
        return (
            PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS
            if accepted and not stale and unresolved_count == 0 and blocking_count == 0
            else PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS
        )
    if followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE:
        return (
            PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS
            if unresolved_count
            else PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS
        )
    if followup_type == PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE:
        return (
            PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS
            if blocking_count
            else PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS
        )
    if unresolved_count or blocking_count or stale:
        return PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS
    return PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS


def _phase11h_blocker_summary(
    *,
    blocking_count: int,
    rejection_count: int,
    status: str,
) -> str:
    if rejection_count:
        return "source-rejected"
    if blocking_count or status == PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS:
        return "blockers-open"
    if status == PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS:
        return "blockers-dispositioned"
    return "no-blockers"


def _phase11h_reviewer_summary(
    *,
    unresolved_count: int,
    blocking_count: int,
    rejection_count: int,
    status: str,
) -> str:
    if rejection_count:
        return "needs-more-review"
    if unresolved_count:
        return "reviewer-queue-open"
    if blocking_count or status == PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS:
        return "reviewer-queue-blocked"
    return "reviews-clear"


def _phase11h_stale_summary(
    *,
    stale: bool,
    blocking_count: int,
    status: str,
) -> str:
    if not stale:
        return "source-current"
    if blocking_count > 1 or status == PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS:
        return "source-stale-renewal-blocked"
    return "source-stale-renewal-open"


def _phase11i_sanitized_followups(
    followups: Mapping[str, object] | tuple[object, ...] | list[object] | None,
    *,
    domain: str,
) -> tuple[dict[str, object], ...] | None:
    if followups is None:
        source = phase11_acceptance_followup_fixture_bundle()["followup_records"]
        values = tuple(source.values())
    elif isinstance(followups, Mapping):
        values = tuple(followups.values())
    elif isinstance(followups, (tuple, list)):
        values = tuple(followups)
    else:
        values = ()
    safe: list[dict[str, object]] = []
    for item in values:
        result = validate_phase11_acceptance_followup_record(item)
        if not result.compatible:
            return None
        record = dict(result.sanitized_record)
        if domain == "unknown" or _safe_domain(record.get("domain")) == domain:
            safe.append(record)
    return tuple(
        sorted(
            safe,
            key=lambda record: (
                _safe_phase11h_record_id(record.get("followup_id")),
                _phase11h_record_hash(record),
            ),
        )
    )


def _phase11i_queue_index_from_followups(
    followups: tuple[Mapping[str, object], ...],
    *,
    domain: str,
) -> dict[str, object]:
    status_counts = _phase11i_status_counts_from_followups(followups)
    blocker_counts = _phase11i_followup_summary_counts(
        followups,
        "blocker_disposition_summary",
        PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_SUMMARIES,
    )
    reviewer_counts = _phase11i_followup_summary_counts(
        followups,
        "reviewer_queue_summary",
        PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_SUMMARIES,
    )
    stale_counts = _phase11i_followup_summary_counts(
        followups,
        "stale_renewal_summary",
        PHASE11_ACCEPTANCE_FOLLOWUP_STALE_SUMMARIES,
    )
    payload = {
        "schema_version": 1,
        "queue_index_contract_version": PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION,
        "queue_index_kind": PHASE11_FOLLOWUP_QUEUE_INDEX_KIND,
        "queue_id": None,
        "queue_fingerprint": None,
        "domain": _safe_domain(domain),
        "status": None,
        "contract_versions": _phase11i_contract_versions(),
        "included_followup_labels": [
            _safe_phase11h_record_id(record.get("followup_id")) for record in followups
        ],
        "included_followup_hashes": [_phase11h_record_hash(record) for record in followups],
        "queue_status_counts": status_counts,
        "blocker_disposition_counts": blocker_counts,
        "reviewer_queue_counts": reviewer_counts,
        "stale_renewal_counts": stale_counts,
        "entry_count": len(followups),
        "open_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS],
        "blocked_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS],
        "stale_count": sum(
            1
            for record in followups
            if record.get("followup_type") == PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE
        ),
        "unresolved_review_count": sum(
            _safe_int(record.get("unresolved_review_count")) for record in followups
        ),
        "blocking_count": sum(_safe_int(record.get("blocking_count")) for record in followups),
        "blocker_disposition_count": sum(
            1
            for record in followups
            if record.get("followup_type") == PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE
        ),
        "reviewer_queue_count": sum(
            1
            for record in followups
            if record.get("followup_type") == PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE
        ),
        "stale_renewal_count": sum(
            1
            for record in followups
            if record.get("followup_type") == PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE
        ),
        "needs_more_review_count": sum(
            1
            for record in followups
            if record.get("followup_type") == PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE
        ),
        "archived_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS],
        "rejected_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS],
        "resolved_for_planning_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS],
        "deterministic_ordering": "sanitized-followup-label-hash-v1",
        "planning_only": True,
        "metadata_only": True,
        "sanitized": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    payload["status"] = _phase11i_queue_status_from_counts(payload)
    return _finalize_phase11i_queue_index(payload)


def _phase11i_contract_versions() -> dict[str, int]:
    versions = _phase11h_contract_versions()
    versions["phase11i_followup_queue_index"] = PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION
    return versions


def _phase11i_zero_status_counts() -> dict[str, int]:
    return {status: 0 for status in PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_VALUES}


def _phase11i_status_counts_from_followups(
    followups: tuple[Mapping[str, object], ...],
) -> dict[str, int]:
    counts = _phase11i_zero_status_counts()
    for record in followups:
        status = _safe_acceptance_followup_status(record.get("status"))
        counts[status] += 1
    return counts


def _phase11i_followup_summary_counts(
    followups: tuple[Mapping[str, object], ...],
    field: str,
    values: tuple[str, ...],
) -> dict[str, int]:
    counts = {value: 0 for value in values}
    for record in followups:
        text = _safe_category(record.get(field))
        if text in counts:
            counts[text] += 1
    return counts


def _phase11i_status_counts(value: object) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return _phase11i_zero_status_counts()
    return {
        status: _safe_int(value.get(status)) for status in PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_VALUES
    }


def _phase11i_summary_counts(
    value: object,
    allowed: tuple[str, ...],
) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {item: 0 for item in allowed}
    return {item: _safe_int(value.get(item)) for item in allowed}


def _phase11i_queue_status_from_counts(value: Mapping[str, object]) -> str:
    entry_count = _safe_int(value.get("entry_count"))
    rejected_count = _safe_int(value.get("rejected_count"))
    archived_count = _safe_int(value.get("archived_count"))
    stale_count = _safe_int(value.get("stale_count"))
    needs_more_review_count = _safe_int(value.get("needs_more_review_count"))
    reviewer_queue_count = _safe_int(value.get("reviewer_queue_count"))
    unresolved_count = _safe_int(value.get("unresolved_review_count"))
    blocking_count = _safe_int(value.get("blocking_count"))
    blocked_count = _safe_int(value.get("blocked_count"))
    resolved_count = _safe_int(value.get("resolved_for_planning_count"))
    if rejected_count:
        return PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS
    if archived_count and archived_count == entry_count:
        return PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS
    if stale_count:
        return PHASE11_FOLLOWUP_QUEUE_STALE_STATUS
    if needs_more_review_count or (reviewer_queue_count and unresolved_count):
        return PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS
    if blocking_count or blocked_count:
        return PHASE11_FOLLOWUP_QUEUE_BLOCKED_STATUS
    if entry_count and resolved_count == entry_count:
        return PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS
    if archived_count:
        return PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS
    return PHASE11_FOLLOWUP_QUEUE_BLOCKED_STATUS


def _phase11i_queue_count_errors(
    value: Mapping[str, object],
    *,
    include_summary_counts: bool = True,
) -> tuple[str, ...]:
    errors: list[str] = []
    status_counts = _phase11i_status_counts(value.get("queue_status_counts"))
    if value.get("queue_status_counts") != status_counts:
        errors.append("phase11i_queue_status_counts_invalid")
    entry_count = _safe_int(value.get("entry_count"))
    if sum(status_counts.values()) != entry_count:
        errors.append("phase11i_queue_status_counts_contradiction")
    expected_top_counts = {
        "open_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS],
        "blocked_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS],
        "archived_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS],
        "rejected_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS],
        "resolved_for_planning_count": status_counts[PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS],
    }
    for field, expected in expected_top_counts.items():
        if field in value and _safe_int(value.get(field)) != expected:
            errors.append("phase11i_queue_top_count_contradiction")
            break
    for field in (
        "entry_count",
        "unresolved_review_count",
        "blocking_count",
        "stale_count",
        "blocker_disposition_count",
        "reviewer_queue_count",
        "stale_renewal_count",
        "needs_more_review_count",
    ):
        if field in value and _safe_int(value.get(field)) != value.get(field):
            errors.append("phase11i_queue_count_invalid")
            break
    if include_summary_counts:
        summaries = (
            (
                "blocker_disposition_counts",
                PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_SUMMARIES,
            ),
            (
                "reviewer_queue_counts",
                PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_SUMMARIES,
            ),
            (
                "stale_renewal_counts",
                PHASE11_ACCEPTANCE_FOLLOWUP_STALE_SUMMARIES,
            ),
        )
        for field, allowed in summaries:
            counts = _phase11i_summary_counts(value.get(field), allowed)
            if value.get(field) != counts or sum(counts.values()) != entry_count:
                errors.append("phase11i_queue_summary_counts_contradiction")
                break
    if (
        _safe_int(value.get("resolved_for_planning_count")) == entry_count
        and entry_count
        and (
            _safe_int(value.get("blocking_count"))
            or _safe_int(value.get("unresolved_review_count"))
            or _safe_int(value.get("rejected_count"))
            or _safe_int(value.get("stale_count"))
        )
    ):
        errors.append("phase11i_queue_accepted_runtime_contradiction")
    return tuple(errors)


def _phase11i_ordering_errors(value: Mapping[str, object]) -> tuple[str, ...]:
    errors: list[str] = []
    if value.get("deterministic_ordering") != "sanitized-followup-label-hash-v1":
        errors.append("phase11i_queue_ordering_contract_invalid")
    labels = value.get("included_followup_labels")
    hashes = value.get("included_followup_hashes")
    if isinstance(labels, list) and isinstance(hashes, list) and len(labels) == len(hashes):
        pairs = list(zip(labels, hashes, strict=False))
        if pairs != sorted(pairs, key=lambda item: (str(item[0]), str(item[1]))):
            errors.append("phase11i_queue_ordering_contradiction")
        if len(pairs) != len(set(pairs)):
            errors.append("phase11i_queue_duplicate_followup_ref")
    return tuple(errors)


def _phase11i_queue_label_matches_fingerprint(
    *,
    label: object,
    domain: object,
    fingerprint: object,
) -> bool:
    safe_label = _safe_phase11i_queue_id(label)
    safe_domain = _safe_domain(domain)
    safe_fingerprint = _safe_sha256(fingerprint)
    if not safe_fingerprint:
        return False
    return safe_label == f"p11i-queue-{safe_domain}-{safe_fingerprint[:16]}"


def _phase11h_record_hash(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["followup_id"] = None
    return _phase11_payload_sha256(payload)


def _finalize_phase11i_queue_index(payload: dict[str, object]) -> dict[str, object]:
    payload["queue_id"] = None
    payload["queue_fingerprint"] = None
    fingerprint = _phase11i_queue_index_fingerprint(payload)
    payload["queue_fingerprint"] = fingerprint
    payload["queue_id"] = f"p11i-queue-{_safe_domain(payload.get('domain'))}-{fingerprint[:16]}"
    return payload


def _phase11i_queue_index_fingerprint(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["queue_id"] = None
    payload["queue_fingerprint"] = None
    return _phase11_payload_sha256(payload)


def _finalize_phase11i_acceptance_check(payload: dict[str, object]) -> dict[str, object]:
    payload["acceptance_id"] = None
    payload["acceptance_fingerprint"] = None
    fingerprint = _phase11i_acceptance_fingerprint(payload)
    payload["acceptance_fingerprint"] = fingerprint
    payload["acceptance_id"] = f"p11i-check-{fingerprint[:16]}"
    return payload


def _phase11i_acceptance_fingerprint(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["acceptance_id"] = None
    payload["acceptance_fingerprint"] = None
    return _phase11_payload_sha256(payload)


def _phase11j_contract_versions() -> dict[str, int]:
    versions = _phase11i_contract_versions()
    versions["phase11j_decision_closeout"] = PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION
    return versions


def _phase11j_queue_acceptance_matches_index(
    queue: Mapping[str, object],
    acceptance: Mapping[str, object],
) -> bool:
    if acceptance.get("queue_label") != queue.get("queue_id"):
        return False
    if acceptance.get("queue_fingerprint") != queue.get("queue_fingerprint"):
        return False
    fields = (
        "domain",
        "status",
        "entry_count",
        "unresolved_review_count",
        "blocking_count",
        "stale_count",
        "archived_count",
        "rejected_count",
        "resolved_for_planning_count",
        "reviewer_queue_count",
        "blocker_disposition_count",
        "needs_more_review_count",
    )
    return all(acceptance.get(field) == queue.get(field) for field in fields)


def _phase11j_decision_from_source_queue(value: Mapping[str, object]) -> str:
    status = _safe_followup_queue_status(value.get("status"))
    if status == PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS:
        return PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION
    if status == PHASE11_FOLLOWUP_QUEUE_STALE_STATUS:
        return PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION
    if status == PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS:
        return PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION
    if status == PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS:
        return PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION
    if status == PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS:
        return PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION
    return PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION


def _phase11j_status_from_decision(decision: str) -> str:
    if decision == PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION:
        return PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS
    if decision == PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION:
        return PHASE11_DECISION_CLOSEOUT_BLOCKED_STATUS
    if decision == PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION:
        return PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS
    if decision == PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION:
        return PHASE11_DECISION_CLOSEOUT_ARCHIVED_STATUS
    return PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS


def _phase11j_reviewer_disposition_summary(decision: str) -> str:
    summaries = {
        PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION: ("all-queue-items-resolved-for-planning"),
        PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION: "stale-items-deferred",
        PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION: "queue-rejected",
        PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION: "queue-archived",
        PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION: "reviewer-queue-open",
        PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION: "blockers-remain",
    }
    return summaries.get(decision, "queue-rejected")


def _phase11j_count_errors(value: Mapping[str, object]) -> tuple[str, ...]:
    errors: list[str] = []
    for field in (
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
        "archived_count",
        "rejected_count",
        "deferred_count",
    ):
        if not _is_phase11j_count(value.get(field)):
            errors.append("phase11j_closeout_count_invalid")
            break
    if _safe_int(value.get("deferred_count")) != _safe_int(value.get("stale_count")):
        errors.append("phase11j_closeout_count_contradiction")
    return tuple(errors)


def _phase11j_decision_count_contradictions(
    value: Mapping[str, object],
) -> tuple[str, ...]:
    decision = _safe_phase11j_decision(value.get("closeout_decision"))
    unresolved_count = _safe_int(value.get("unresolved_review_count"))
    blocker_count = _safe_int(value.get("blocker_count"))
    stale_count = _safe_int(value.get("stale_count"))
    archived_count = _safe_int(value.get("archived_count"))
    rejected_count = _safe_int(value.get("rejected_count"))
    deferred_count = _safe_int(value.get("deferred_count"))
    errors: list[str] = []
    if decision == PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION:
        if any(
            (
                unresolved_count,
                blocker_count,
                stale_count,
                archived_count,
                rejected_count,
                deferred_count,
            )
        ):
            errors.append("phase11j_closeout_decision_count_contradiction")
    elif decision == PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION:
        if stale_count == 0 or deferred_count == 0:
            errors.append("phase11j_closeout_decision_count_contradiction")
    elif decision == PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION:
        if rejected_count == 0:
            errors.append("phase11j_closeout_decision_count_contradiction")
    elif decision == PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION:
        if archived_count == 0:
            errors.append("phase11j_closeout_decision_count_contradiction")
    elif decision == PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION:
        if unresolved_count == 0:
            errors.append("phase11j_closeout_decision_count_contradiction")
    elif decision == PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION and blocker_count == 0:
        errors.append("phase11j_closeout_decision_count_contradiction")
    return tuple(errors)


def _is_phase11j_count(value: object) -> bool:
    return type(value) is int and value >= 0


def _finalize_phase11j_closeout(payload: dict[str, object]) -> dict[str, object]:
    payload["closeout_id"] = None
    payload["closeout_id"] = _phase11j_closeout_id(payload)
    return payload


def _phase11j_closeout_id(value: Mapping[str, object]) -> str:
    fingerprint = _phase11j_closeout_payload_hash(value)
    if not _looks_sha256(fingerprint):
        return ""
    return f"p11j-closeout-{fingerprint[:16]}"


def _phase11j_closeout_payload_hash(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["closeout_id"] = None
    return _phase11_payload_sha256(payload)


def _phase11k_domain_labels() -> list[str]:
    return [PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN]


def _phase11k_domain_closeout_summary(
    closeout: Mapping[str, object],
) -> dict[str, object]:
    return {
        "domain_label": _safe_domain(closeout.get("domain")),
        "final_closeout_decision": _safe_phase11j_decision(closeout.get("closeout_decision")),
        "final_closeout_status": _safe_phase11j_status(closeout.get("closeout_status")),
        "unresolved_review_count": _safe_int(closeout.get("unresolved_review_count")),
        "blocker_count": _safe_int(closeout.get("blocker_count")),
        "stale_count": _safe_int(closeout.get("stale_count")),
    }


def _phase11k_domain_closeout_for(
    closeouts: object,
    domain: str,
) -> Mapping[str, object]:
    if isinstance(closeouts, list):
        for item in closeouts:
            if isinstance(item, Mapping) and _safe_domain(item.get("domain_label")) == domain:
                return item
    return rejected_phase11_review_trail_export_bundle()["domain_closeouts"][0]


def _phase11k_domain_closeout_errors(
    closeouts: list[object],
) -> tuple[str, ...]:
    errors: list[str] = []
    if len(closeouts) != len(_phase11k_domain_labels()):
        errors.append("phase11k_review_trail_export_domain_count_invalid")
    labels: list[str] = []
    for item in closeouts:
        if not isinstance(item, Mapping):
            errors.append("phase11k_review_trail_export_domain_closeout_not_object")
            continue
        if PHASE11_REVIEW_TRAIL_EXPORT_DOMAIN_REQUIRED_FIELDS - set(item):
            errors.append("phase11k_review_trail_export_domain_field_missing")
        if set(str(key) for key in item) - PHASE11_REVIEW_TRAIL_EXPORT_DOMAIN_ALLOWED_FIELDS:
            errors.append("phase11k_review_trail_export_domain_unknown_field")
        domain = _safe_domain(item.get("domain_label"))
        labels.append(domain)
        if domain not in _phase11k_domain_labels():
            errors.append("phase11k_review_trail_export_domain_invalid")
        decision = _safe_phase11j_decision(item.get("final_closeout_decision"))
        if decision != item.get("final_closeout_decision"):
            errors.append("phase11k_review_trail_export_decision_invalid")
        status = _safe_phase11j_status(item.get("final_closeout_status"))
        if status != item.get("final_closeout_status"):
            errors.append("phase11k_review_trail_export_status_invalid")
        if _phase11j_status_from_decision(decision) != status:
            errors.append("phase11k_review_trail_export_status_contradiction")
        for field in (
            "unresolved_review_count",
            "blocker_count",
            "stale_count",
        ):
            if not _is_phase11j_count(item.get(field)):
                errors.append("phase11k_review_trail_export_count_invalid")
                break
    if labels != _phase11k_domain_labels() or len(labels) != len(set(labels)):
        errors.append("phase11k_review_trail_export_domain_order_invalid")
    return tuple(errors)


def _phase11k_privacy_violation_count(value: object) -> int:
    if isinstance(value, Mapping):
        safe = dict(value)
        if safe.get("readiness_gap_summary") == PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP:
            safe["readiness_gap_summary"] = "readiness-gap-missing"
        return _privacy_violation_count(safe)
    return _privacy_violation_count(value)


def _finalize_phase11k_review_trail_export(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["export_id"] = None
    payload["export_id"] = _phase11k_export_id(payload)
    return payload


def _phase11k_export_id(value: Mapping[str, object]) -> str:
    fingerprint = _phase11k_export_payload_hash(value)
    if not _looks_sha256(fingerprint):
        return ""
    return f"p11k-export-{fingerprint[:16]}"


def _phase11k_export_payload_hash(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["export_id"] = None
    return _phase11_payload_sha256(payload)


def _phase11l_domain_gap_summary(
    closeout: Mapping[str, object],
) -> dict[str, object]:
    return {
        "domain_label": _safe_domain(closeout.get("domain_label")),
        "source_closeout_decision": _safe_phase11j_decision(
            closeout.get("final_closeout_decision")
        ),
        "source_closeout_status": _safe_phase11j_status(closeout.get("final_closeout_status")),
        "unresolved_review_count": _safe_int(closeout.get("unresolved_review_count")),
        "blocker_count": _safe_int(closeout.get("blocker_count")),
        "stale_count": _safe_int(closeout.get("stale_count")),
        "missing_future_gate_count": len(PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES),
    }


def _phase11l_domain_gap_for(
    domain_summaries: object,
    domain: str,
) -> Mapping[str, object]:
    if isinstance(domain_summaries, list):
        for item in domain_summaries:
            if isinstance(item, Mapping) and _safe_domain(item.get("domain_label")) == domain:
                return item
    return rejected_phase11_runtime_authorization_gap_ledger()["domain_gap_summaries"][0]


def _phase11l_domain_gap_errors(
    domain_summaries: list[object],
) -> tuple[str, ...]:
    errors: list[str] = []
    if len(domain_summaries) != len(_phase11k_domain_labels()):
        errors.append("phase11l_runtime_gap_ledger_domain_count_invalid")
    labels: list[str] = []
    for item in domain_summaries:
        if not isinstance(item, Mapping):
            errors.append("phase11l_runtime_gap_ledger_domain_summary_not_object")
            continue
        if PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_DOMAIN_REQUIRED_FIELDS - set(item):
            errors.append("phase11l_runtime_gap_ledger_domain_field_missing")
        if (
            set(str(key) for key in item)
            - PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_DOMAIN_ALLOWED_FIELDS
        ):
            errors.append("phase11l_runtime_gap_ledger_domain_unknown_field")
        domain = _safe_domain(item.get("domain_label"))
        labels.append(domain)
        if domain not in _phase11k_domain_labels():
            errors.append("phase11l_runtime_gap_ledger_domain_invalid")
        decision = _safe_phase11j_decision(item.get("source_closeout_decision"))
        if decision != item.get("source_closeout_decision"):
            errors.append("phase11l_runtime_gap_ledger_decision_invalid")
        status = _safe_phase11j_status(item.get("source_closeout_status"))
        if status != item.get("source_closeout_status"):
            errors.append("phase11l_runtime_gap_ledger_status_invalid")
        if _phase11j_status_from_decision(decision) != status:
            errors.append("phase11l_runtime_gap_ledger_status_contradiction")
        for field in (
            "unresolved_review_count",
            "blocker_count",
            "stale_count",
            "missing_future_gate_count",
        ):
            if not _is_phase11j_count(item.get(field)):
                errors.append("phase11l_runtime_gap_ledger_count_invalid")
                break
        if item.get("missing_future_gate_count") != len(
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES
        ):
            errors.append("phase11l_runtime_gap_ledger_missing_gate_count_invalid")
    if labels != _phase11k_domain_labels() or len(labels) != len(set(labels)):
        errors.append("phase11l_runtime_gap_ledger_domain_order_invalid")
    return tuple(errors)


def _phase11m_count_total(records: object, field: str) -> int:
    if not isinstance(records, list):
        return 0
    return sum(_safe_int(item.get(field)) for item in records if isinstance(item, Mapping))


def _phase11m_privacy_violation_count(value: object) -> int:
    if isinstance(value, Mapping):
        masked: dict[str, object] = {}
        for key, item in value.items():
            safe_key = str(key)
            if safe_key == "runtime_authorization_status":
                safe_key = "runtime_status"
            masked[safe_key] = _phase11m_privacy_safe_value(item)
        return _privacy_violation_count(masked)
    if isinstance(value, list):
        return sum(_phase11m_privacy_violation_count(item) for item in value)
    return _privacy_violation_count(_phase11m_privacy_safe_value(value))


def _phase11m_privacy_safe_value(value: object) -> object:
    if value == PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP:
        return "readiness-gap-missing"
    if value == PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS:
        return "runtime-gap-status-missing"
    if isinstance(value, list):
        return [_phase11m_privacy_safe_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _phase11m_privacy_safe_value(item) for key, item in value.items()}
    return value


def _phase11m_authorization_wording_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase11m_authorization_wording_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase11m_authorization_wording_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    if lowered in (
        PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS,
        PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
    ):
        return 0
    fragments = (
        "authorization",
        "authorized",
        "approval",
        "approved",
        "permission",
        "permitted",
        "grant",
        "granted",
    )
    return sum(1 for fragment in fragments if fragment in lowered)


def _finalize_phase11m_governance_closeout(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["closeout_index_id"] = None
    payload["closeout_index_id"] = _phase11m_closeout_id(payload)
    return payload


def _phase11m_closeout_id(value: Mapping[str, object]) -> str:
    fingerprint = _phase11m_closeout_payload_hash(value)
    if not _looks_sha256(fingerprint):
        return ""
    return f"p11m-closeout-{fingerprint[:16]}"


def _phase11m_closeout_payload_hash(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["closeout_index_id"] = None
    return _phase11_payload_sha256(payload)


def _phase11l_privacy_violation_count(value: object) -> int:
    if isinstance(value, Mapping):
        masked: dict[str, object] = {}
        for key, item in value.items():
            safe_key = str(key)
            if safe_key == "runtime_authorization_gap_ledger_contract_version":
                safe_key = "runtime_gap_ledger_contract_version"
            elif safe_key == "authorization_status":
                safe_key = "runtime_gap_status"
            masked[safe_key] = _phase11l_privacy_safe_value(item)
        return _privacy_violation_count(masked)
    if isinstance(value, list):
        return sum(_phase11l_privacy_violation_count(item) for item in value)
    return _privacy_violation_count(_phase11l_privacy_safe_value(value))


def _phase11l_privacy_safe_value(value: object) -> object:
    if value == PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP:
        return "readiness-gap-missing"
    if value == PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS:
        return "runtime-gap-status-missing"
    if isinstance(value, list):
        return [_phase11l_privacy_safe_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _phase11l_privacy_safe_value(item) for key, item in value.items()}
    return value


def _phase11l_authorization_wording_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase11l_authorization_wording_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase11l_authorization_wording_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    if lowered in (
        PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS,
        PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
    ):
        return 0
    fragments = (
        "authorization",
        "authorized",
        "approval",
        "approved",
        "permission",
        "permitted",
        "grant",
        "granted",
    )
    return sum(1 for fragment in fragments if fragment in lowered)


def _finalize_phase11l_runtime_gap_ledger(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["ledger_id"] = None
    payload["ledger_id"] = _phase11l_ledger_id(payload)
    return payload


def _phase11l_ledger_id(value: Mapping[str, object]) -> str:
    fingerprint = _phase11l_ledger_payload_hash(value)
    if not _looks_sha256(fingerprint):
        return ""
    return f"p11l-ledger-{fingerprint[:16]}"


def _phase11l_ledger_payload_hash(value: Mapping[str, object]) -> str:
    payload = dict(value)
    payload["ledger_id"] = None
    return _phase11_payload_sha256(payload)


def _phase11f_domain_entries(
    audit_index: Mapping[str, object],
    domain: str,
) -> list[Mapping[str, object]]:
    entries = audit_index.get("entries")
    if not isinstance(entries, list):
        return []
    return [
        entry
        for entry in entries
        if isinstance(entry, Mapping) and _safe_domain(entry.get("domain")) == domain
    ]


def _phase11f_lifecycle_status_counts(
    entries: list[Mapping[str, object]],
) -> dict[str, int]:
    return {
        stage: sum(
            1 for entry in entries if _safe_lifecycle_stage(entry.get("lifecycle_stage")) == stage
        )
        for stage in PHASE11_LIFECYCLE_STAGE_VALUES
    }


def _phase11f_coverage_summary(
    audit_index: Mapping[str, object],
    domain: str,
    entries: list[Mapping[str, object]],
) -> dict[str, object]:
    coverage = next(
        (
            item
            for item in audit_index.get("reviewer_scope_coverage", ())
            if isinstance(item, Mapping) and _safe_domain(item.get("domain")) == domain
        ),
        None,
    )
    if coverage is not None:
        covered_gates = coverage.get("covered_gates")
        missing_gates = coverage.get("missing_gates")
        covered_count = len(covered_gates) if isinstance(covered_gates, list) else 0
        missing_count = (
            len(missing_gates) if isinstance(missing_gates, list) else len(REAL_MODE_REQUIRED_GATES)
        )
        return {
            "reviewer_scope_label": _safe_category(coverage.get("reviewer_scope_label")),
            "required_gate_count": len(REAL_MODE_REQUIRED_GATES),
            "covered_gate_count": covered_count,
            "missing_gate_count": missing_count,
            "coverage_complete": bool(coverage.get("coverage_complete")),
        }
    return {
        "reviewer_scope_label": "planning-review-missing",
        "required_gate_count": len(REAL_MODE_REQUIRED_GATES),
        "covered_gate_count": max(
            (_safe_int(entry.get("reviewed_gate_count")) for entry in entries),
            default=0,
        ),
        "missing_gate_count": min(
            len(REAL_MODE_REQUIRED_GATES),
            sum(_safe_int(entry.get("missing_gate_count")) for entry in entries)
            or len(REAL_MODE_REQUIRED_GATES),
        ),
        "coverage_complete": False,
    }


def _phase11f_retention_summary(
    audit_index: Mapping[str, object],
    domain: str,
) -> dict[str, object]:
    policy = next(
        (
            item
            for item in audit_index.get("export_retention_policies", ())
            if isinstance(item, Mapping) and _safe_domain(item.get("domain")) == domain
        ),
        None,
    )
    return {
        "retention_label": _safe_category(
            (policy or {}).get("retention_label")
            if isinstance(policy, Mapping)
            else PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY
        ),
        "export_class": _safe_category(
            (policy or {}).get("export_class")
            if isinstance(policy, Mapping)
            else PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY
        ),
        "metadata_export_allowed": bool(
            (policy or {}).get("metadata_export_allowed", True)
            if isinstance(policy, Mapping)
            else True
        ),
        "deterministic_fixture_export_allowed": bool(
            (policy or {}).get("deterministic_fixture_export_allowed", True)
            if isinstance(policy, Mapping)
            else True
        ),
        "external_upload_prohibited": bool(
            (policy or {}).get("external_upload_prohibited", True)
            if isinstance(policy, Mapping)
            else True
        ),
        "network_export_prohibited": bool(
            (policy or {}).get("network_export_prohibited", True)
            if isinstance(policy, Mapping)
            else True
        ),
    }


def _phase11f_lifecycle_counts_valid(value: object, entry_count: int) -> bool:
    if not isinstance(value, Mapping):
        return False
    if set(str(key) for key in value) != set(PHASE11_LIFECYCLE_STAGE_VALUES):
        return False
    counts = [_safe_int(value.get(stage)) for stage in PHASE11_LIFECYCLE_STAGE_VALUES]
    if any(
        value.get(stage) != count
        for stage, count in zip(PHASE11_LIFECYCLE_STAGE_VALUES, counts, strict=False)
    ):
        return False
    return sum(counts) == entry_count


def _phase11f_coverage_summary_valid(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    if set(str(key) for key in value) != PHASE11_AUDIT_HANDOFF_COVERAGE_SUMMARY_REQUIRED_FIELDS:
        return False
    required = _safe_int(value.get("required_gate_count"))
    covered = _safe_int(value.get("covered_gate_count"))
    missing = _safe_int(value.get("missing_gate_count"))
    if required != len(REAL_MODE_REQUIRED_GATES):
        return False
    if covered + missing != required:
        return False
    if value.get("covered_gate_count") != covered or value.get("missing_gate_count") != missing:
        return False
    if bool(value.get("coverage_complete")) != (missing == 0):
        return False
    if _safe_category(value.get("reviewer_scope_label")) != value.get("reviewer_scope_label"):
        return False
    return True


def _phase11f_retention_summary_valid(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    if set(str(key) for key in value) != PHASE11_AUDIT_HANDOFF_RETENTION_SUMMARY_REQUIRED_FIELDS:
        return False
    if value.get("retention_label") != PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY:
        return False
    if value.get("export_class") != PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY:
        return False
    return (
        value.get("metadata_export_allowed") is True
        and value.get("deterministic_fixture_export_allowed") is True
        and value.get("external_upload_prohibited") is True
        and value.get("network_export_prohibited") is True
    )


def _phase11f_count_from_mapping(value: object, key: str) -> int:
    if not isinstance(value, Mapping):
        return 0
    return _safe_int(value.get(key))


def _phase11g_reason_list_valid(value: object) -> bool:
    if not isinstance(value, list):
        return False
    for item in value:
        if _safe_category(item) != item:
            return False
    return True


def _phase11_lifecycle_ref(record: Mapping[str, object] | None) -> dict[str, object]:
    safe = record if isinstance(record, Mapping) else rejected_phase11_dossier_lifecycle_record()
    decision = safe.get("audit_decision") if isinstance(safe.get("audit_decision"), Mapping) else {}
    signoff = (
        safe.get("reviewer_signoff") if isinstance(safe.get("reviewer_signoff"), Mapping) else {}
    )
    return {
        "domain": _safe_domain(safe.get("domain")),
        "record_label": _safe_phase11d_record_id(safe.get("lifecycle_record_id")),
        "record_fingerprint": _safe_sha256(safe.get("lifecycle_record_fingerprint")),
        "dossier_packet_label": _safe_preflight_packet_id(safe.get("dossier_packet_id")),
        "dossier_packet_fingerprint": _safe_sha256(safe.get("dossier_packet_fingerprint")),
        "decision_record_label": _safe_phase11d_record_id(decision.get("decision_id")),
        "decision_record_fingerprint": _safe_sha256(decision.get("decision_fingerprint")),
        "lifecycle_stage": _safe_lifecycle_stage(safe.get("lifecycle_stage")),
        "audit_decision": _safe_lifecycle_decision(decision.get("decision")),
        "decision": _safe_lifecycle_decision(decision.get("decision")),
        "reviewer_scope_label": _safe_category(signoff.get("review_scope")),
        "preflight_status": _safe_preflight_status(safe.get("preflight_status")),
        "reviewed_gate_count": _safe_int(safe.get("preflight_reviewed_gate_count")),
        "missing_gate_count": _safe_int(safe.get("preflight_missing_gate_count")),
        "rejected_gate_count": _safe_int(safe.get("preflight_rejected_gate_count")),
        "blocking_reason_count": _safe_int(safe.get("blocking_reason_count")),
    }


def _phase11_audit_index_entry(ref: Mapping[str, object]) -> dict[str, object]:
    lifecycle_label = _safe_phase11e_link_label(ref.get("record_label"))
    lifecycle_hash = _safe_sha256(ref.get("record_fingerprint"))
    entry_label = f"p11e-entry-{_safe_domain(ref.get('domain'))}-{lifecycle_hash[:12]}"
    return {
        "entry_label": entry_label,
        "domain": _safe_domain(ref.get("domain")),
        "dossier_packet_label": _safe_preflight_packet_id(ref.get("dossier_packet_label")),
        "dossier_packet_fingerprint": _safe_sha256(ref.get("dossier_packet_fingerprint")),
        "lifecycle_record_label": lifecycle_label,
        "lifecycle_record_fingerprint": lifecycle_hash,
        "decision_record_label": _safe_phase11e_link_label(ref.get("decision_record_label")),
        "decision_record_fingerprint": _safe_sha256(ref.get("decision_record_fingerprint")),
        "lifecycle_stage": _safe_lifecycle_stage(ref.get("lifecycle_stage")),
        "audit_decision": _safe_lifecycle_decision(ref.get("audit_decision")),
        "reviewer_scope_label": _safe_category(ref.get("reviewer_scope_label")),
        "preflight_status": _safe_preflight_status(ref.get("preflight_status")),
        "reviewed_gate_count": _safe_int(ref.get("reviewed_gate_count")),
        "missing_gate_count": _safe_int(ref.get("missing_gate_count")),
        "rejected_gate_count": _safe_int(ref.get("rejected_gate_count")),
        "blocking_reason_count": _safe_int(ref.get("blocking_reason_count")),
        "retention_label": PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY,
        "export_class": PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY,
        "execution_permitted": False,
    }


def _phase11_first_lifecycle_record(
    records: tuple[Mapping[str, object], ...],
    *,
    stage: str,
) -> Mapping[str, object] | None:
    for record in records:
        if _phase11_lifecycle_ref(record)["lifecycle_stage"] == stage:
            return record
    return records[0] if records else None


def _phase11_default_change_control_records(
    records: tuple[Mapping[str, object], ...],
) -> list[dict[str, object]]:
    if not records:
        return []
    ordered = sorted(
        (
            record
            for record in records
            if _phase11_lifecycle_ref(record)["lifecycle_stage"]
            in {
                PHASE11_LIFECYCLE_STAGE_CREATED,
                PHASE11_LIFECYCLE_STAGE_REVIEWED,
                PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
                PHASE11_LIFECYCLE_STAGE_ARCHIVED,
            }
        ),
        key=lambda record: (
            _phase11_lifecycle_stage_order(_phase11_lifecycle_ref(record)["lifecycle_stage"]),
            _phase11_lifecycle_ref(record)["record_label"],
            _phase11_lifecycle_ref(record)["record_fingerprint"],
        ),
    )
    return [
        phase11_change_control_record(prior, current)
        for prior, current in zip(ordered, ordered[1:], strict=False)
    ]


def _phase11_lifecycle_stage_order(stage: object) -> int:
    order = {
        PHASE11_LIFECYCLE_STAGE_CREATED: 0,
        PHASE11_LIFECYCLE_STAGE_REVIEWED: 1,
        PHASE11_LIFECYCLE_STAGE_SUPERSEDED: 2,
        PHASE11_LIFECYCLE_STAGE_REJECTED: 3,
        PHASE11_LIFECYCLE_STAGE_ARCHIVED: 4,
        PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED: 5,
    }
    return order.get(_safe_lifecycle_stage(stage), 99)


def _phase11e_audit_index_entry_errors(
    entries: list[object],
) -> tuple[
    tuple[str, ...],
    dict[str, int],
    dict[str, int],
    int,
    int,
]:
    errors: list[str] = []
    stage_counts = {stage: 0 for stage in PHASE11_LIFECYCLE_STAGE_VALUES}
    decision_counts = {decision: 0 for decision in PHASE11_LIFECYCLE_DECISION_VALUES}
    blocking_count = 0
    rejection_count = 0
    labels: list[str] = []
    lifecycle_hashes: list[str] = []
    safe_entries: list[Mapping[str, object]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            errors.append("phase11e_audit_index_entry_malformed")
            continue
        safe_entries.append(entry)
        if PHASE11_AUDIT_INDEX_ENTRY_REQUIRED_FIELDS - set(entry):
            errors.append("phase11e_audit_index_entry_field_missing")
        if set(str(key) for key in entry) - PHASE11_AUDIT_INDEX_ENTRY_ALLOWED_FIELDS:
            errors.append("phase11e_audit_index_entry_unknown_field")
        if _safe_phase11e_link_label(entry.get("entry_label")) != entry.get("entry_label"):
            errors.append("phase11e_audit_index_entry_label_invalid")
        labels.append(str(entry.get("lifecycle_record_label") or ""))
        lifecycle_hashes.append(str(entry.get("lifecycle_record_fingerprint") or ""))
        for field in (
            "dossier_packet_fingerprint",
            "lifecycle_record_fingerprint",
            "decision_record_fingerprint",
        ):
            if not _looks_sha256(entry.get(field)):
                errors.append("phase11e_audit_index_entry_fingerprint_invalid")
                break
        domain = _safe_domain(entry.get("domain"))
        if domain not in {PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"}:
            errors.append("phase11e_audit_index_entry_domain_invalid")
        if _safe_preflight_packet_id(entry.get("dossier_packet_label")) != entry.get(
            "dossier_packet_label"
        ):
            errors.append("phase11e_audit_index_entry_packet_label_invalid")
        if _safe_phase11e_link_label(entry.get("lifecycle_record_label")) != entry.get(
            "lifecycle_record_label"
        ):
            errors.append("phase11e_audit_index_entry_lifecycle_label_invalid")
        if _safe_phase11e_link_label(entry.get("decision_record_label")) != entry.get(
            "decision_record_label"
        ):
            errors.append("phase11e_audit_index_entry_decision_label_invalid")
        stage = _safe_lifecycle_stage(entry.get("lifecycle_stage"))
        decision = _safe_lifecycle_decision(entry.get("audit_decision"))
        if stage != entry.get("lifecycle_stage"):
            errors.append("phase11e_audit_index_entry_stage_invalid")
        if decision != entry.get("audit_decision"):
            errors.append("phase11e_audit_index_entry_decision_invalid")
        if _safe_category(entry.get("reviewer_scope_label")) != entry.get("reviewer_scope_label"):
            errors.append("phase11e_audit_index_entry_scope_invalid")
        if _safe_preflight_status(entry.get("preflight_status")) != entry.get("preflight_status"):
            errors.append("phase11e_audit_index_entry_preflight_status_invalid")
        for field in (
            "reviewed_gate_count",
            "missing_gate_count",
            "rejected_gate_count",
            "blocking_reason_count",
        ):
            if _safe_int(entry.get(field)) != entry.get(field):
                errors.append("phase11e_audit_index_entry_count_invalid")
                break
        if _safe_int(entry.get("reviewed_gate_count")) + _safe_int(
            entry.get("missing_gate_count")
        ) + _safe_int(entry.get("rejected_gate_count")) != len(REAL_MODE_REQUIRED_GATES):
            errors.append("phase11e_audit_index_entry_gate_count_contradiction")
        if entry.get("retention_label") != PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY:
            errors.append("phase11e_audit_index_entry_retention_invalid")
        if entry.get("export_class") != PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY:
            errors.append("phase11e_audit_index_entry_export_class_invalid")
        if entry.get("execution_permitted") is not False:
            errors.append("phase11e_audit_index_entry_runtime_implied")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
        blocking_count += _safe_int(entry.get("blocking_reason_count"))
        if (
            stage == PHASE11_LIFECYCLE_STAGE_REJECTED
            or decision == PHASE11_LIFECYCLE_DECISION_REJECTED
            or _safe_int(entry.get("rejected_gate_count")) > 0
        ):
            rejection_count += 1
    expected_order = sorted(
        safe_entries,
        key=lambda entry: (
            str(entry.get("entry_label") or ""),
            str(entry.get("lifecycle_record_fingerprint") or ""),
        ),
    )
    if safe_entries != expected_order:
        errors.append("phase11e_audit_index_order_invalid")
    if len(labels) != len(set(labels)) or len(lifecycle_hashes) != len(set(lifecycle_hashes)):
        errors.append("phase11e_audit_index_duplicate_record")
    return (
        tuple(errors),
        stage_counts,
        decision_counts,
        blocking_count,
        rejection_count,
    )


def _phase11e_included_label_errors(
    audit_index: Mapping[str, object],
    entries: list[object],
) -> tuple[str, ...]:
    entry_maps = [entry for entry in entries if isinstance(entry, Mapping)]
    expected_packets = sorted(
        {str(entry.get("dossier_packet_label") or "") for entry in entry_maps}
    )
    expected_lifecycle = sorted(
        {str(entry.get("lifecycle_record_label") or "") for entry in entry_maps}
    )
    expected_decisions = sorted(
        {str(entry.get("decision_record_label") or "") for entry in entry_maps}
    )
    expected_hashes = sorted(
        {
            str(entry.get(field) or "")
            for entry in entry_maps
            for field in (
                "dossier_packet_fingerprint",
                "lifecycle_record_fingerprint",
                "decision_record_fingerprint",
            )
        }
    )
    errors: list[str] = []
    if audit_index.get("included_dossier_packet_labels") != expected_packets:
        errors.append("phase11e_audit_index_packet_labels_contradiction")
    if audit_index.get("included_lifecycle_record_labels") != expected_lifecycle:
        errors.append("phase11e_audit_index_lifecycle_labels_contradiction")
    if audit_index.get("included_decision_record_labels") != expected_decisions:
        errors.append("phase11e_audit_index_decision_labels_contradiction")
    if audit_index.get("included_record_fingerprints") != expected_hashes:
        errors.append("phase11e_audit_index_fingerprints_contradiction")
    return tuple(errors)


def _phase11_preflight_comparison_ref(
    dossier: Mapping[str, object] | None,
) -> dict[str, object]:
    built = (
        dossier
        if _looks_like_phase11_preflight_dossier(dossier)
        else rejected_phase11_preflight_dossier()
    )
    result = validate_phase11_preflight_dossier(built)
    safe = result.sanitized_dossier
    gates = safe.get("gates") if isinstance(safe.get("gates"), list) else []
    fingerprints = (
        safe.get("included_record_fingerprints")
        if isinstance(safe.get("included_record_fingerprints"), Mapping)
        else {}
    )
    reasons = _safe_phase11d_blocking_reasons(safe.get("blocking_reasons"))
    return {
        "domain": _safe_domain(safe.get("domain")),
        "packet_id": _safe_preflight_packet_id(safe.get("packet_id")),
        "packet_fingerprint": _safe_sha256(safe.get("packet_fingerprint")),
        "status": _safe_preflight_status(safe.get("status")),
        "blocking_reason_count": len(reasons),
        "contract_versions": {
            "preflight_dossier": PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION,
            "contract_spec": _safe_int(safe.get("contract_spec_version")),
            "review_record": _safe_int(safe.get("review_record_contract_version")),
        },
        "gate_statuses": {
            _safe_review_gate_id(gate.get("gate_id")): _safe_category(gate.get("preflight_status"))
            for gate in gates
            if isinstance(gate, Mapping)
        },
        "record_hashes": {
            field: _safe_sha256(fingerprints.get(field))
            for field in PHASE11_PREFLIGHT_FINGERPRINT_REQUIRED_FIELDS
        },
        "rejection_reasons": reasons,
    }


def _phase11d_comparison_errors(
    value: object,
    *,
    expected_domain: str | None = None,
) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase11d_comparison_missing",)
    errors: list[str] = []
    if PHASE11_COMPARISON_REQUIRED_FIELDS - set(value):
        errors.append("phase11d_comparison_required_field_missing")
    if set(str(key) for key in value) - PHASE11_COMPARISON_ALLOWED_FIELDS:
        errors.append("phase11d_comparison_unknown_field")
    if value.get("schema_version") != 1:
        errors.append("phase11d_comparison_schema_version_invalid")
    if value.get("comparison_contract_version") != PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION:
        errors.append("phase11d_comparison_contract_version_unsupported")
    if value.get("comparison_kind") != PHASE11_DOSSIER_COMPARISON_KIND:
        errors.append("phase11d_comparison_kind_invalid")
    comparison_domain = _safe_domain(value.get("domain"))
    if comparison_domain != value.get("domain"):
        errors.append("phase11d_comparison_domain_invalid")
    if expected_domain is not None and comparison_domain != _safe_domain(expected_domain):
        errors.append("phase11d_comparison_domain_mismatch")
    for field in ("left_packet_id", "right_packet_id"):
        if _safe_preflight_packet_id(value.get(field)) != value.get(field):
            errors.append("phase11d_comparison_packet_id_invalid")
            break
    left_domain = _phase11_preflight_domain_from_packet_id(value.get("left_packet_id"))
    right_domain = _phase11_preflight_domain_from_packet_id(value.get("right_packet_id"))
    if left_domain != "unknown" and left_domain != comparison_domain:
        errors.append("phase11d_comparison_left_domain_mismatch")
    if right_domain != comparison_domain:
        errors.append("phase11d_comparison_right_domain_mismatch")
    for field in ("left_packet_fingerprint", "right_packet_fingerprint"):
        if not _looks_sha256(value.get(field)):
            errors.append("phase11d_comparison_packet_fingerprint_invalid")
            break
    for field in ("left_status", "right_status"):
        if _safe_preflight_status(value.get(field)) != value.get(field):
            errors.append("phase11d_comparison_status_invalid")
            break
    if not isinstance(value.get("equal"), bool):
        errors.append("phase11d_comparison_equal_invalid")
    changed = value.get("changed_fields")
    if not isinstance(changed, list) or any(_safe_category(item) != item for item in changed):
        errors.append("phase11d_comparison_changed_fields_invalid")
    elif value.get("changed_field_count") != len(changed):
        errors.append("phase11d_comparison_changed_field_count_invalid")
    for field in (
        "left_blocking_reason_count",
        "right_blocking_reason_count",
        "gate_status_delta_count",
        "record_hash_delta_count",
        "rejection_reason_delta_count",
    ):
        if _safe_int(value.get(field)) != value.get(field):
            errors.append("phase11d_comparison_count_invalid")
            break
    reasons = value.get("right_rejection_reasons")
    if not isinstance(reasons, list) or tuple(reasons) != _safe_phase11d_blocking_reasons(reasons):
        errors.append("phase11d_comparison_rejection_reasons_invalid")
    _phase11_required_runtime_disabled_errors(value, errors, "phase11d_comparison")
    if _privacy_violation_count(value):
        errors.append("phase11d_comparison_privacy_boundary")
    return tuple(errors)


def _phase11_preflight_domain_from_packet_id(value: object) -> str:
    text = _safe_preflight_packet_id(value)
    for domain in (PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN, "unknown"):
        if text.startswith(f"p11c-preflight-{domain}-"):
            return domain
    return "unknown"


def _phase11_required_runtime_disabled_errors(
    record: Mapping[str, object],
    errors: list[str],
    prefix: str,
) -> None:
    for field in ("planning_only", "metadata_only", "sanitized"):
        if record.get(field) is not True:
            errors.append(f"{prefix}_required_true_flag_missing")
            break
    for field in ("execution_permitted", "real_mode_runtime_enabled"):
        if record.get(field) is not False:
            errors.append(f"{prefix}_runtime_implied")
            break
    if record.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append(f"{prefix}_runtime_stage_invalid")


def _phase11d_lifecycle_contradictions(
    *,
    stage: str,
    decision: str,
    verdict: str,
    preflight_status: str,
    reviewed_count: int,
) -> tuple[str, ...]:
    errors: list[str] = []
    if stage == PHASE11_LIFECYCLE_STAGE_CREATED:
        if decision != PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW:
            errors.append("phase11d_lifecycle_created_decision_contradiction")
        if verdict != PHASE11_SIGNOFF_VERDICT_BLOCKERS:
            errors.append("phase11d_lifecycle_created_verdict_contradiction")
    if stage == PHASE11_LIFECYCLE_STAGE_REVIEWED:
        if decision != PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING:
            errors.append("phase11d_lifecycle_reviewed_decision_contradiction")
        if verdict != PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS:
            errors.append("phase11d_lifecycle_reviewed_verdict_contradiction")
    if stage == PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED:
        if decision != PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED:
            errors.append("phase11d_lifecycle_decision_recorded_contradiction")
        if verdict != PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS:
            errors.append("phase11d_lifecycle_decision_recorded_verdict_contradiction")
    if stage == PHASE11_LIFECYCLE_STAGE_REJECTED:
        if decision != PHASE11_LIFECYCLE_DECISION_REJECTED:
            errors.append("phase11d_lifecycle_rejected_decision_contradiction")
        if verdict != PHASE11_SIGNOFF_VERDICT_REJECTED:
            errors.append("phase11d_lifecycle_rejected_verdict_contradiction")
    if stage in {PHASE11_LIFECYCLE_STAGE_SUPERSEDED, PHASE11_LIFECYCLE_STAGE_ARCHIVED}:
        if decision != PHASE11_LIFECYCLE_DECISION_BLOCKED:
            errors.append("phase11d_lifecycle_closed_decision_contradiction")
        if verdict != PHASE11_SIGNOFF_VERDICT_SUPERSEDED:
            errors.append("phase11d_lifecycle_closed_verdict_contradiction")
    if decision in {
        PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
        PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
    }:
        if preflight_status != PHASE11_PREFLIGHT_STATUS_REVIEWED:
            errors.append("phase11d_lifecycle_decision_preflight_contradiction")
        if verdict != PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS:
            errors.append("phase11d_lifecycle_decision_verdict_contradiction")
    if (
        decision == PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED
        and reviewed_count != len(REAL_MODE_REQUIRED_GATES)
    ):
        errors.append("phase11d_lifecycle_decision_gate_count_contradiction")
    return tuple(errors)


def _default_phase11d_verdict_for_stage(stage: str) -> str:
    if stage in {
        PHASE11_LIFECYCLE_STAGE_REVIEWED,
        PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
    }:
        return PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS
    if stage == PHASE11_LIFECYCLE_STAGE_REJECTED:
        return PHASE11_SIGNOFF_VERDICT_REJECTED
    if stage in {PHASE11_LIFECYCLE_STAGE_SUPERSEDED, PHASE11_LIFECYCLE_STAGE_ARCHIVED}:
        return PHASE11_SIGNOFF_VERDICT_SUPERSEDED
    return PHASE11_SIGNOFF_VERDICT_BLOCKERS


def _default_phase11d_decision_for_stage(
    stage: str,
    dossier: Mapping[str, object],
) -> str:
    status = _safe_preflight_status(dossier.get("status"))
    if stage == PHASE11_LIFECYCLE_STAGE_REVIEWED:
        if status == PHASE11_PREFLIGHT_STATUS_REVIEWED:
            return PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING
        return PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW
    if stage == PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED:
        if status == PHASE11_PREFLIGHT_STATUS_REVIEWED:
            return PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED
        return PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW
    if stage == PHASE11_LIFECYCLE_STAGE_REJECTED:
        return PHASE11_LIFECYCLE_DECISION_REJECTED
    if stage in {PHASE11_LIFECYCLE_STAGE_SUPERSEDED, PHASE11_LIFECYCLE_STAGE_ARCHIVED}:
        return PHASE11_LIFECYCLE_DECISION_BLOCKED
    return PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW


def _safe_phase11d_blocking_reasons(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    safe: list[str] = []
    for item in value:
        category = _safe_category(item)
        if category and _privacy_violation_count(category) == 0:
            safe.append(category)
    return tuple(safe)


def _looks_like_phase11_lifecycle_record(value: object) -> bool:
    return (
        isinstance(value, Mapping)
        and value.get("lifecycle_record_kind") == PHASE11_DOSSIER_LIFECYCLE_KIND
    )


def _looks_like_phase11_audit_index(value: object) -> bool:
    return isinstance(value, Mapping) and value.get("audit_index_kind") == PHASE11_AUDIT_INDEX_KIND


def _looks_like_phase11_audit_handoff(value: object) -> bool:
    return (
        isinstance(value, Mapping) and value.get("audit_handoff_kind") == PHASE11_AUDIT_HANDOFF_KIND
    )


def _looks_like_phase11_handoff_acceptance(value: object) -> bool:
    return (
        isinstance(value, Mapping)
        and value.get("handoff_acceptance_kind") == PHASE11_HANDOFF_ACCEPTANCE_KIND
    )


def _safe_phase11d_label(value: object) -> str:
    text = _safe_category(value)
    if not text.startswith("p11d-"):
        return "p11d-redacted-label"
    if _privacy_violation_count(text):
        return "p11d-redacted-label"
    return text


def _safe_phase11d_timestamp(value: object) -> str:
    text = str(value or "").strip()
    if _looks_phase11d_timestamp(text):
        return text
    return "2026-06-09T00:00:00Z"


def _looks_phase11d_timestamp(value: object) -> bool:
    text = str(value or "")
    if len(text) != 20 or not text.endswith("Z") or "T" not in text:
        return False
    allowed = set("0123456789TZ-:")
    if any(char not in allowed for char in text):
        return False
    return (
        text[4] == "-"
        and text[7] == "-"
        and text[10] == "T"
        and text[13] == ":"
        and text[16] == ":"
    )


def _safe_signoff_verdict(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_SIGNOFF_VERDICT_VALUES:
        return text
    return PHASE11_SIGNOFF_VERDICT_BLOCKERS


def _safe_lifecycle_decision(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_LIFECYCLE_DECISION_VALUES:
        return text
    return PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW


def _safe_lifecycle_stage(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_LIFECYCLE_STAGE_VALUES:
        return text
    return PHASE11_LIFECYCLE_STAGE_REJECTED


def _safe_phase11d_lifecycle_status(value: object) -> str:
    text = _safe_category(value)
    stage = text.removesuffix("-runtime-disabled")
    if stage in PHASE11_LIFECYCLE_STAGE_VALUES and text == f"{stage}-runtime-disabled":
        return text
    return f"{PHASE11_LIFECYCLE_STAGE_REJECTED}-runtime-disabled"


def _safe_phase11d_record_id(value: object) -> str:
    text = _safe_category(value)
    allowed_prefixes = ("p11d-lifecycle-", "p11d-signoff-", "p11d-decision-")
    if text.startswith(allowed_prefixes) and _privacy_violation_count(text) == 0:
        return text
    return "p11d-redacted-record"


def _safe_phase11e_record_id(value: object) -> str:
    text = _safe_category(value)
    allowed_prefixes = (
        "p11e-index-",
        "p11e-change-",
        "p11e-chain-",
        "p11e-coverage-",
        "p11e-policy-",
    )
    if text.startswith(allowed_prefixes) and _privacy_violation_count(text) == 0:
        return text
    return "p11e-redacted-record"


def _safe_phase11f_record_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11f-handoff-") and _privacy_violation_count(text) == 0:
        return text
    return "p11f-redacted-record"


def _safe_phase11g_record_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11g-acceptance-") and _privacy_violation_count(text) == 0:
        return text
    return "p11g-redacted-record"


def _safe_phase11h_record_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11h-followup-") and _privacy_violation_count(text) == 0:
        return text
    return "p11h-redacted-record"


def _safe_phase11i_queue_id(value: object) -> str:
    text = _safe_category(value)
    allowed_prefixes = (
        f"p11i-queue-{PHASE11_DOCUMENT_DOMAIN}-",
        f"p11i-queue-{PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN}-",
        "p11i-queue-unknown-",
    )
    if text.startswith(allowed_prefixes) and _privacy_violation_count(text) == 0:
        return text
    return "p11i-queue-unknown-redacted"


def _safe_phase11i_acceptance_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11i-check-") and _privacy_violation_count(text) == 0:
        return text
    return "p11i-check-redacted"


def _safe_phase11j_closeout_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11j-closeout-") and _privacy_violation_count(text) == 0:
        return text
    return "p11j-closeout-redacted"


def _safe_phase11k_export_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11k-export-") and _privacy_violation_count(text) == 0:
        return text
    return "p11k-export-redacted"


def _safe_phase11l_ledger_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11l-ledger-") and _privacy_violation_count(text) == 0:
        return text
    return "p11l-ledger-redacted"


def _safe_phase11m_closeout_id(value: object) -> str:
    text = _safe_category(value)
    if text.startswith("p11m-closeout-") and _privacy_violation_count(text) == 0:
        return text
    return "p11m-closeout-redacted"


def _safe_phase11e_link_label(value: object) -> str:
    text = _safe_category(value)
    allowed_prefixes = (
        "p11c-preflight-",
        "p11d-lifecycle-",
        "p11d-decision-",
        "p11d-signoff-",
        "p11d-redacted-record",
        "p11e-entry-",
    )
    if text.startswith(allowed_prefixes) and _privacy_violation_count(text) == 0:
        return text
    return "p11d-redacted-record"


def _safe_audit_index_status(value: object) -> str:
    text = _safe_category(value)
    if text in {PHASE11_AUDIT_INDEX_STATUS, PHASE11_AUDIT_INDEX_REJECTED_STATUS}:
        return text
    return PHASE11_AUDIT_INDEX_REJECTED_STATUS


def _safe_audit_handoff_status(value: object) -> str:
    text = _safe_category(value)
    if text in {
        PHASE11_AUDIT_HANDOFF_STATUS,
        PHASE11_AUDIT_HANDOFF_REJECTED_STATUS,
    }:
        return text
    return PHASE11_AUDIT_HANDOFF_REJECTED_STATUS


def _safe_handoff_acceptance_status(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_HANDOFF_ACCEPTANCE_STATUS_VALUES:
        return text
    return PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS


def _safe_acceptance_followup_type(value: object) -> str | None:
    text = _safe_category(value)
    if text in PHASE11_ACCEPTANCE_FOLLOWUP_TYPE_VALUES:
        return text
    return None


def _safe_acceptance_followup_status(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_VALUES:
        return text
    return PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS


def _safe_acceptance_followup_blocker_summary(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_SUMMARIES:
        return text
    return "source-rejected"


def _safe_acceptance_followup_reviewer_summary(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_SUMMARIES:
        return text
    return "needs-more-review"


def _safe_acceptance_followup_stale_summary(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_ACCEPTANCE_FOLLOWUP_STALE_SUMMARIES:
        return text
    return "source-stale-renewal-blocked"


def _safe_followup_queue_status(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_FOLLOWUP_QUEUE_STATUS_VALUES:
        return text
    return PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS


def _safe_phase11j_decision(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_DECISION_CLOSEOUT_DECISION_VALUES:
        return text
    return PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION


def _safe_phase11j_status(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_DECISION_CLOSEOUT_STATUS_VALUES:
        return text
    return PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS


def _safe_phase11j_reviewer_summary(value: object) -> str:
    text = _safe_category(value)
    if text in PHASE11_DECISION_CLOSEOUT_DISPOSITION_SUMMARIES:
        return text
    return "queue-rejected"


def _ordered_gate_subset(value: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    gates = {_safe_review_gate_id(item) for item in (value or ())}
    return tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate in gates)


def _safe_review_gate_id(value: object) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    return "-".join(part for part in safe.split("-") if part)


def _review_record_status(
    reviewed: tuple[str, ...],
    missing: tuple[str, ...],
    rejected: tuple[str, ...],
) -> str:
    if rejected:
        return PHASE11_REVIEW_RECORD_STATUS_REJECTED
    if not missing and len(reviewed) == len(REAL_MODE_REQUIRED_GATES):
        return PHASE11_REVIEW_RECORD_STATUS_REVIEWED
    return PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE


def _safe_review_record_status(value: object, default: str) -> str:
    text = _safe_domain(value)
    if text in PHASE11_REVIEW_RECORD_STATUS_VALUES:
        return text
    return default


def _looks_like_phase11_review_record(value: object) -> bool:
    return (
        isinstance(value, Mapping) and value.get("review_record_kind") == PHASE11_REVIEW_RECORD_KIND
    )


def _unknown_field_errors(value: object) -> tuple[str, ...]:
    if isinstance(value, Mapping):
        errors = []
        for key, item in value.items():
            if str(key) not in PHASE11_ALLOWED_KEYS:
                errors.append("phase11_contract_unknown_field")
            errors.extend(_unknown_field_errors(item))
        return tuple(errors)
    if isinstance(value, list):
        errors = []
        for item in value:
            errors.extend(_unknown_field_errors(item))
        return tuple(errors)
    return ()


def _privacy_violation_count(value: object) -> int:
    if isinstance(value, Mapping):
        violations = 0
        for key, item in value.items():
            if _unsafe_key(key):
                violations += 1
            violations += _privacy_violation_count(item)
        return violations
    if isinstance(value, list):
        return sum(_privacy_violation_count(item) for item in value)
    if isinstance(value, str):
        return _unsafe_string_count(value)
    return 0


def _execution_implying_wording_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_execution_implying_wording_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_execution_implying_wording_count(item) for item in value)
    if isinstance(value, str):
        return _unsafe_execution_string_count(value)
    return 0


def _unsafe_key(key: object) -> bool:
    text = str(key or "").lower()
    normalized = text.replace("-", "_").replace(" ", "_")
    if text in PHASE11_FORBIDDEN_KEYS or normalized in PHASE11_FORBIDDEN_KEYS:
        return True
    return any(
        fragment in text or fragment in normalized for fragment in PHASE11_FORBIDDEN_KEY_FRAGMENTS
    )


def _unsafe_string_count(value: str) -> int:
    lowered = value.lower().replace("\\", "/")
    normalized = lowered.replace("-", "_").replace(" ", "_")
    return sum(
        1
        for fragment in PHASE11_FORBIDDEN_VALUE_FRAGMENTS
        if fragment in lowered or fragment in normalized
    )


def _unsafe_execution_string_count(value: str) -> int:
    lowered = value.lower().replace("\\", "/")
    normalized = lowered.replace("-", "_").replace(" ", "_")
    fragments = (
        "accepted-for-runtime",
        "accepted_for_runtime",
        "accepted for runtime",
        "execution-permitted",
        "execution_permitted",
        "execution permitted",
        "runtime-enabled",
        "runtime_enabled",
        "runtime enabled",
        "enable-runtime",
        "enable_runtime",
        "enable runtime",
        "run-adapter",
        "run_adapter",
        "run adapter",
    )
    return sum(1 for fragment in fragments if fragment in lowered or fragment in normalized)


def _safe_domain(value: object) -> str:
    text = str(value or "unknown").strip().lower().replace("_", "-")
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    return "-".join(part for part in safe.split("-") if part) or "unknown"


def _safe_category(value: object) -> str:
    return _safe_domain(value)


def _safe_int(value: object) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 0
    return number if number >= 0 else 0


__all__ = [
    "PHASE11_AUDIT_INDEX_CONTRACT_VERSION",
    "PHASE11_AUDIT_INDEX_FIXTURE_KIND",
    "PHASE11_AUDIT_INDEX_KIND",
    "PHASE11_AUDIT_INDEX_REJECTED_STATUS",
    "PHASE11_AUDIT_INDEX_STATUS",
    "PHASE11_AUDIT_INDEX_STATUS_LABELS",
    "PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION",
    "PHASE11_AUDIT_HANDOFF_FIXTURE_KIND",
    "PHASE11_AUDIT_HANDOFF_KIND",
    "PHASE11_AUDIT_HANDOFF_REJECTED_STATUS",
    "PHASE11_AUDIT_HANDOFF_STATUS",
    "PHASE11_AUDIT_HANDOFF_STATUS_LABELS",
    "PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_NO_ACTION_TYPE",
    "PHASE11_ACCEPTANCE_FOLLOWUP_ARCHIVED_STATUS",
    "PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKED_STATUS",
    "PHASE11_ACCEPTANCE_FOLLOWUP_BLOCKER_DISPOSITION_TYPE",
    "PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION",
    "PHASE11_ACCEPTANCE_FOLLOWUP_FIXTURE_KIND",
    "PHASE11_ACCEPTANCE_FOLLOWUP_KIND",
    "PHASE11_ACCEPTANCE_FOLLOWUP_NEEDS_MORE_REVIEW_TYPE",
    "PHASE11_ACCEPTANCE_FOLLOWUP_OPEN_STATUS",
    "PHASE11_ACCEPTANCE_FOLLOWUP_REJECTED_STATUS",
    "PHASE11_ACCEPTANCE_FOLLOWUP_RESOLVED_STATUS",
    "PHASE11_ACCEPTANCE_FOLLOWUP_REVIEWER_QUEUE_TYPE",
    "PHASE11_ACCEPTANCE_FOLLOWUP_STALE_RENEWAL_TYPE",
    "PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_LABELS",
    "PHASE11_FOLLOWUP_QUEUE_ACCEPTED_STATUS",
    "PHASE11_FOLLOWUP_QUEUE_ACCEPTANCE_KIND",
    "PHASE11_FOLLOWUP_QUEUE_ARCHIVED_STATUS",
    "PHASE11_FOLLOWUP_QUEUE_BLOCKED_STATUS",
    "PHASE11_FOLLOWUP_QUEUE_FIXTURE_KIND",
    "PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION",
    "PHASE11_FOLLOWUP_QUEUE_INDEX_KIND",
    "PHASE11_FOLLOWUP_QUEUE_NEEDS_REVIEW_STATUS",
    "PHASE11_FOLLOWUP_QUEUE_REJECTED_STATUS",
    "PHASE11_FOLLOWUP_QUEUE_STALE_STATUS",
    "PHASE11_FOLLOWUP_QUEUE_STATUS_LABELS",
    "PHASE11_DECISION_CLOSEOUT_ARCHIVED_DECISION",
    "PHASE11_DECISION_CLOSEOUT_ARCHIVED_STATUS",
    "PHASE11_DECISION_CLOSEOUT_BLOCKED_DECISION",
    "PHASE11_DECISION_CLOSEOUT_BLOCKED_STATUS",
    "PHASE11_DECISION_CLOSEOUT_CLOSED_DECISION",
    "PHASE11_DECISION_CLOSEOUT_COMPLETE_STATUS",
    "PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION",
    "PHASE11_DECISION_CLOSEOUT_DEFERRED_DECISION",
    "PHASE11_DECISION_CLOSEOUT_FIXTURE_KIND",
    "PHASE11_DECISION_CLOSEOUT_INCOMPLETE_STATUS",
    "PHASE11_DECISION_CLOSEOUT_NEEDS_REVIEW_DECISION",
    "PHASE11_DECISION_CLOSEOUT_REJECTED_DECISION",
    "PHASE11_DECISION_CLOSEOUT_REJECTED_STATUS",
    "PHASE11_DECISION_CLOSEOUT_STATUS_LABELS",
    "PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS",
    "PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS",
    "PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION",
    "PHASE11_HANDOFF_ACCEPTANCE_FIXTURE_KIND",
    "PHASE11_HANDOFF_ACCEPTANCE_KIND",
    "PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS",
    "PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS",
    "PHASE11_HANDOFF_ACCEPTANCE_STATUS_LABELS",
    "PHASE11_CHANGE_CONTROL_KIND",
    "PHASE11_CHANGE_CONTROL_REASON",
    "PHASE11_CONTRACT_STATUS_LABELS",
    "PHASE11_DOSSIER_COMPARISON_KIND",
    "PHASE11_DOSSIER_DECISION_KIND",
    "PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION",
    "PHASE11_DOSSIER_LIFECYCLE_FIXTURE_KIND",
    "PHASE11_DOSSIER_LIFECYCLE_KIND",
    "PHASE11_DOCUMENT_DOMAIN",
    "PHASE11_DOCUMENT_REQUIRED_CONTRACTS",
    "PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED",
    "PHASE11_LIFECYCLE_DECISION_BLOCKED",
    "PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW",
    "PHASE11_LIFECYCLE_DECISION_REJECTED",
    "PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING",
    "PHASE11_LIFECYCLE_STAGE_ARCHIVED",
    "PHASE11_LIFECYCLE_STAGE_CREATED",
    "PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED",
    "PHASE11_LIFECYCLE_STAGE_REJECTED",
    "PHASE11_LIFECYCLE_STAGE_REVIEWED",
    "PHASE11_LIFECYCLE_STAGE_SUPERSEDED",
    "PHASE11_LIFECYCLE_STATUS_LABELS",
    "PHASE11_REAL_MODE_CONTRACT_PHASE",
    "PHASE11_REAL_MODE_CONTRACT_SPEC_KIND",
    "PHASE11_REAL_MODE_CONTRACT_SPEC_VERSION",
    "PHASE11_REAL_MODE_CONTRACT_STATUS",
    "PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION",
    "PHASE11_PREFLIGHT_DOSSIER_FIXTURE_KIND",
    "PHASE11_PREFLIGHT_DOSSIER_KIND",
    "PHASE11_PREFLIGHT_STATUS_LABELS",
    "PHASE11_PREFLIGHT_STATUS_MISSING",
    "PHASE11_PREFLIGHT_STATUS_REJECTED",
    "PHASE11_PREFLIGHT_STATUS_REVIEWED",
    "PHASE11_REVIEW_RECORD_CONTRACT_VERSION",
    "PHASE11_REVIEW_RECORD_FIXTURE_KIND",
    "PHASE11_REVIEW_RECORD_KIND",
    "PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE",
    "PHASE11_REVIEW_RECORD_STATUS_LABELS",
    "PHASE11_REVIEW_RECORD_STATUS_REJECTED",
    "PHASE11_REVIEW_RECORD_STATUS_REVIEWED",
    "PHASE11_REVIEW_RECORD_STATUS_VALUES",
    "PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION",
    "PHASE11_REVIEW_TRAIL_EXPORT_FIXTURE_KIND",
    "PHASE11_REVIEW_TRAIL_EXPORT_PHASE_COUNT",
    "PHASE11_REVIEW_TRAIL_EXPORT_PHASE_RANGE",
    "PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP",
    "PHASE11_REVIEW_TRAIL_EXPORT_STATUS_LABELS",
    "PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION",
    "PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_FIXTURE_KIND",
    "PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_MISSING_GATES",
    "PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_COUNT",
    "PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE",
    "PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS",
    "PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS_LABELS",
    "PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION",
    "PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_FIXTURE_KIND",
    "PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_NEXT_PHASE_REQUIREMENT",
    "PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_COUNT",
    "PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE",
    "PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS",
    "PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS_LABELS",
    "PHASE11_REVIEWER_SIGNOFF_KIND",
    "PHASE11_REVIEWER_SCOPE_COVERAGE_KIND",
    "PHASE11_RF_BOOTH_REQUIRED_CONTRACTS",
    "PHASE11_SIGNOFF_VERDICT_BLOCKERS",
    "PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS",
    "PHASE11_SIGNOFF_VERDICT_REJECTED",
    "PHASE11_SIGNOFF_VERDICT_SUPERSEDED",
    "PHASE11_SUPERSESSION_CHAIN_KIND",
    "PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN",
    "PHASE11_EXPORT_CLASS_LOCAL_METADATA_ONLY",
    "PHASE11_EXPORT_RETENTION_POLICY_KIND",
    "PHASE11_RETENTION_LABEL_AUDIT_METADATA_ONLY",
    "Phase11AuditHandoffValidationResult",
    "Phase11AuditIndexValidationResult",
    "Phase11AcceptanceFollowupValidationResult",
    "Phase11DecisionCloseoutValidationResult",
    "Phase11FollowupQueueAcceptanceValidationResult",
    "Phase11FollowupQueueValidationResult",
    "Phase11ContractSpecValidationResult",
    "Phase11HandoffAcceptanceValidationResult",
    "Phase11LifecycleAuditValidationResult",
    "Phase11PreflightDossierValidationResult",
    "Phase11ReviewRecordValidationResult",
    "Phase11ReviewTrailExportValidationResult",
    "Phase11RuntimeAuthorizationGapLedgerValidationResult",
    "Phase11PlanningGovernanceCloseoutValidationResult",
    "phase11_audit_index",
    "phase11_audit_index_fixture_bundle",
    "phase11_audit_index_status_summary",
    "phase11_audit_handoff_fixture_bundle",
    "phase11_audit_handoff_record",
    "phase11_audit_handoff_status_summary",
    "phase11_acceptance_followup_fixture_bundle",
    "phase11_acceptance_followup_record",
    "phase11_acceptance_followup_status_summary",
    "phase11_decision_closeout_fixture_bundle",
    "phase11_decision_closeout_record",
    "phase11_decision_closeout_status_summary",
    "phase11_followup_queue_acceptance_check",
    "phase11_followup_queue_index_fixture_bundle",
    "phase11_followup_queue_index_record",
    "phase11_followup_queue_index_status_summary",
    "phase11_change_control_record",
    "phase11_compare_preflight_dossiers",
    "phase11_document_ingestion_preflight_dossier",
    "phase11_document_ingestion_review_record",
    "phase11_handoff_acceptance_fixture_bundle",
    "phase11_handoff_acceptance_record",
    "phase11_handoff_acceptance_status_summary",
    "phase11_contract_status_summary",
    "phase11_document_ingestion_contract_spec",
    "phase11_dossier_decision_record",
    "phase11_dossier_lifecycle_fixture_bundle",
    "phase11_dossier_lifecycle_record",
    "phase11_dossier_lifecycle_status_summary",
    "phase11_export_retention_policy",
    "phase11_preflight_dossier",
    "phase11_preflight_dossier_fixture_bundle",
    "phase11_preflight_status_summary",
    "phase11_real_mode_contract_bundle",
    "phase11_rejected_review_record",
    "phase11_reviewer_signoff_metadata",
    "phase11_reviewer_scope_coverage_summary",
    "phase11_review_record",
    "phase11_review_record_fixture_bundle",
    "phase11_review_record_gate_acknowledgements",
    "phase11_review_record_schema",
    "phase11_review_record_status_summary",
    "phase11_review_trail_export_bundle",
    "phase11_review_trail_export_status_summary",
    "phase11_runtime_authorization_gap_ledger",
    "phase11_runtime_authorization_gap_ledger_status_summary",
    "phase11_planning_governance_closeout_index",
    "phase11_planning_governance_closeout_status_summary",
    "phase11_supersession_chain",
    "phase11_wifi_csi_rf_booth_preflight_dossier",
    "phase11_wifi_csi_rf_booth_contract_spec",
    "phase11_wifi_csi_rf_booth_review_record",
    "rejected_phase11_audit_index",
    "rejected_phase11_audit_handoff_record",
    "rejected_phase11_acceptance_followup_record",
    "rejected_phase11_decision_closeout_record",
    "rejected_phase11_followup_queue_acceptance_check",
    "rejected_phase11_followup_queue_index",
    "rejected_phase11_handoff_acceptance_record",
    "rejected_phase11_contract_spec",
    "rejected_phase11_change_control_record",
    "rejected_phase11_dossier_decision_record",
    "rejected_phase11_dossier_lifecycle_record",
    "rejected_phase11_export_retention_policy",
    "rejected_phase11_preflight_dossier",
    "rejected_phase11_reviewer_scope_coverage_summary",
    "rejected_phase11_reviewer_signoff_metadata",
    "rejected_phase11_review_record",
    "rejected_phase11_review_trail_export_bundle",
    "rejected_phase11_runtime_authorization_gap_ledger",
    "rejected_phase11_planning_governance_closeout_index",
    "rejected_phase11_supersession_chain",
    "validate_phase11_audit_index",
    "validate_phase11_audit_handoff_record",
    "validate_phase11_acceptance_followup_record",
    "validate_phase11_decision_closeout_record",
    "validate_phase11_followup_queue_acceptance_check",
    "validate_phase11_followup_queue_index_record",
    "validate_phase11_handoff_acceptance_record",
    "validate_phase11_change_control_record",
    "validate_phase11_contract_spec",
    "validate_phase11_dossier_decision_record",
    "validate_phase11_dossier_lifecycle_record",
    "validate_phase11_export_retention_policy",
    "validate_phase11_preflight_dossier",
    "validate_phase11_reviewer_scope_coverage",
    "validate_phase11_reviewer_signoff_metadata",
    "validate_phase11_review_record",
    "validate_phase11_review_trail_export_bundle",
    "validate_phase11_runtime_authorization_gap_ledger",
    "validate_phase11_planning_governance_closeout_index",
    "validate_phase11_supersession_chain",
]

install_builder_cache(globals())
