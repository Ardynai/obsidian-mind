"""Registry and config validation for fixture-only sensor evidence providers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from somatic.safety.adapter_readiness import (
    REAL_MODE_READINESS_GATE_CONTRACT_VERSION,
    REAL_MODE_READINESS_GATE_KIND,
    evaluate_real_mode_readiness,
)
from somatic.safety.phase11_contracts import (
    PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION,
    PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_LABELS,
    PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION,
    PHASE11_AUDIT_HANDOFF_STATUS_LABELS,
    PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
    PHASE11_AUDIT_INDEX_STATUS_LABELS,
    PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION,
    PHASE11_DECISION_CLOSEOUT_STATUS_LABELS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION,
    PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION,
    PHASE11_FOLLOWUP_QUEUE_STATUS_LABELS,
    PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION,
    PHASE11_HANDOFF_ACCEPTANCE_STATUS_LABELS,
    PHASE11_LIFECYCLE_STATUS_LABELS,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS_LABELS,
    PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION,
    PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
    PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION,
    PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
    PHASE11_REVIEW_TRAIL_EXPORT_STATUS_LABELS,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS_LABELS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_acceptance_followup_status_summary,
    phase11_audit_handoff_status_summary,
    phase11_audit_index_status_summary,
    phase11_decision_closeout_status_summary,
    phase11_dossier_lifecycle_status_summary,
    phase11_followup_queue_index_status_summary,
    phase11_handoff_acceptance_status_summary,
    phase11_planning_governance_closeout_status_summary,
    phase11_preflight_status_summary,
    phase11_review_record_status_summary,
    phase11_review_trail_export_status_summary,
    phase11_runtime_authorization_gap_ledger_status_summary,
)

from .csi_adapter import (
    CSI_SOURCE_ADAPTER_CONTRACT_VERSION,
    CSI_SOURCE_ADAPTER_KIND,
    CSI_SOURCE_ADAPTER_MANIFEST_LABELS,
)
from .csi_batch import (
    CSI_BATCH_GROUP_INPUT_KIND,
    CSI_BATCH_MAX_GROUPS,
    CSI_BATCH_MAX_REFS_PER_GROUP,
)
from .csi_evidence_pack import CSI_EVIDENCE_PACK_CONTRACT_VERSION
from .csi_parser import SUPPORTED_CSI_FIXTURE_EXTENSIONS
from .environment import (
    ENVIRONMENT_FIXTURE_INPUT_KINDS,
    ENVIRONMENT_FIXTURE_PROVIDER_ID,
    MAX_ENVIRONMENT_FIXTURE_REFS,
)
from .environment_evidence_pack import (
    ENVIRONMENT_EVIDENCE_KIND,
    ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_NAME,
    ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_REF,
    ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
    ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
)
from .evidence import sensor_evidence_result_code
from .toy_counter import (
    MAX_TOY_COUNTER_FIXTURE_REFS,
    TOY_COUNTER_FIXTURE_INPUT_KINDS,
)
from .toy_counter_evidence_pack import (
    TOY_COUNTER_EVIDENCE_KIND,
    TOY_COUNTER_EVIDENCE_PACK_ARTIFACT_NAME,
    TOY_COUNTER_EVIDENCE_PACK_ARTIFACT_REF,
    TOY_COUNTER_EVIDENCE_PACK_CONTRACT_VERSION,
    TOY_COUNTER_EVIDENCE_PROVIDER_KIND,
)

# Phase 10A: inline document-evidence constants to avoid circular import
# (somatic.sensors.__init__ -> registry -> somatic.evidence.document_evidence_pack
#  -> somatic.sensors.evidence -> somatic.sensors.__init__)
_DOCUMENT_EVIDENCE_PROVIDER_KIND = "document-fixture"
_DOCUMENT_EVIDENCE_KIND = "document-evidence-pack"
_DOCUMENT_EVIDENCE_PACK_ARTIFACT_NAME = "document_evidence_pack"
_DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF = "artifacts/document_evidence_pack.json"
_DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION = 1
_DOCUMENT_FIXTURE_INPUT_KINDS = ("document-fixture-metadata", "document-fixture-files")
_MAX_DOCUMENT_FIXTURE_REFS = 3
_DOCUMENT_ADAPTER_CONTRACT_VERSION = 1
_DOCUMENT_ADAPTER_KIND = "metadata-document-adapter"
_DOCUMENT_ADAPTER_BOUNDARY_LABELS = (
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
    "review-evidence-only",
    "runtime-disabled-after-review",
    "p11c-preflight-dossier",
    "preflight-evidence-only",
    "runtime-disabled-after-preflight",
    *PHASE11_LIFECYCLE_STATUS_LABELS,
    *PHASE11_AUDIT_INDEX_STATUS_LABELS,
    *PHASE11_AUDIT_HANDOFF_STATUS_LABELS,
    *PHASE11_HANDOFF_ACCEPTANCE_STATUS_LABELS,
    *PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_LABELS,
    *PHASE11_FOLLOWUP_QUEUE_STATUS_LABELS,
    *PHASE11_DECISION_CLOSEOUT_STATUS_LABELS,
    *PHASE11_REVIEW_TRAIL_EXPORT_STATUS_LABELS,
    *PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS_LABELS,
    *PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS_LABELS,
)


def _real_mode_gate_entry_fields(
    *,
    provider_kind: str,
    adapter_kind: str,
    current_mode: str,
) -> dict[str, object]:
    gate = evaluate_real_mode_readiness(
        provider_kind=provider_kind,
        adapter_kind=adapter_kind,
        current_mode=current_mode,
    ).to_dict()
    return {
        "readiness_gate_status": gate["status"],
        "readiness_gate_required_gates": tuple(gate["required_gates"]),
        "readiness_gate_missing_gates": tuple(gate["missing_gates"]),
        "readiness_gate_ready": bool(gate["ready"]),
        "real_mode_execution_permitted": False,
    }


def _phase11_review_record_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_review_record_status_summary(domain=domain)
    return {
        "review_record_contract_version": PHASE11_REVIEW_RECORD_CONTRACT_VERSION,
        "review_record_status": status["review_record_status"],
        "review_record_reviewed_gate_count": status["reviewed_gate_count"],
        "review_record_missing_gate_count": status["missing_gate_count"],
        "review_record_rejected_gate_count": status["rejected_gate_count"],
        "review_record_runtime_stage": status["runtime_stage"],
        "review_record_execution_permitted": False,
    }


def _phase11_preflight_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_preflight_status_summary(domain=domain)
    return {
        "preflight_packet_contract_version": (PHASE11_PREFLIGHT_DOSSIER_CONTRACT_VERSION),
        "preflight_packet_id": status["preflight_packet_id"],
        "preflight_packet_fingerprint": status["preflight_packet_fingerprint"],
        "preflight_packet_status": status["preflight_status"],
        "preflight_packet_reviewed_gate_count": status["reviewed_gate_count"],
        "preflight_packet_missing_gate_count": status["missing_gate_count"],
        "preflight_packet_rejected_gate_count": status["rejected_gate_count"],
        "preflight_packet_runtime_stage": status["runtime_stage"],
        "preflight_packet_execution_permitted": False,
    }


def _phase11_lifecycle_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_dossier_lifecycle_status_summary(domain=domain)
    return {
        "lifecycle_audit_contract_version": (PHASE11_DOSSIER_LIFECYCLE_CONTRACT_VERSION),
        "lifecycle_audit_record_id": status["lifecycle_record_id"],
        "lifecycle_audit_record_fingerprint": (status["lifecycle_record_fingerprint"]),
        "lifecycle_audit_stage": status["lifecycle_stage"],
        "lifecycle_audit_status": status["lifecycle_status"],
        "lifecycle_audit_decision": status["audit_decision"],
        "lifecycle_audit_signoff_verdict": status["signoff_verdict"],
        "lifecycle_audit_signoff_count": status["signoff_count"],
        "lifecycle_audit_decision_count": status["decision_count"],
        "lifecycle_audit_runtime_stage": status["runtime_stage"],
        "lifecycle_audit_execution_permitted": False,
    }


def _phase11_audit_index_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_audit_index_status_summary(domain=domain)
    return {
        "audit_index_contract_version": PHASE11_AUDIT_INDEX_CONTRACT_VERSION,
        "audit_index_id": status["index_id"],
        "audit_index_fingerprint": status["index_fingerprint"],
        "audit_index_status": status["status"],
        "audit_index_entry_count": status["entry_count"],
        "audit_index_blocking_count": status["blocking_count"],
        "audit_index_rejection_count": status["rejection_count"],
        "audit_index_supersession_chain_count": status["supersession_chain_count"],
        "audit_index_change_control_record_count": status["change_control_record_count"],
        "audit_index_export_retention_policy_count": status["export_retention_policy_count"],
        "audit_index_runtime_stage": status["runtime_stage"],
        "audit_index_execution_permitted": False,
    }


def _phase11_audit_handoff_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_audit_handoff_status_summary(domain=domain)
    return {
        "handoff_contract_version": PHASE11_AUDIT_HANDOFF_CONTRACT_VERSION,
        "handoff_id": status["handoff_id"],
        "handoff_fingerprint": status["handoff_fingerprint"],
        "handoff_status": status["status"],
        "handoff_entry_count": status["audit_index_entry_count"],
        "handoff_blocking_count": status["blocking_count"],
        "handoff_rejection_count": status["rejection_count"],
        "handoff_unresolved_review_count": status["unresolved_review_count"],
        "handoff_runtime_stage": status["runtime_stage"],
        "handoff_execution_permitted": False,
    }


def _phase11_handoff_acceptance_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_handoff_acceptance_status_summary(domain=domain)
    return {
        "handoff_acceptance_contract_version": (PHASE11_HANDOFF_ACCEPTANCE_CONTRACT_VERSION),
        "handoff_acceptance_id": status["acceptance_id"],
        "handoff_acceptance_fingerprint": status["acceptance_fingerprint"],
        "handoff_acceptance_status": status["status"],
        "handoff_acceptance_handoff_label": status["source_handoff_label"],
        "handoff_acceptance_handoff_hash": status["source_handoff_hash"],
        "handoff_acceptance_handoff_fingerprint": status["handoff_fingerprint"],
        "handoff_accepted_for_planning": status["accepted_for_planning"],
        "handoff_acceptance_blocked": status["blocked"],
        "handoff_acceptance_stale": status["stale"],
        "handoff_acceptance_missing_review_count": status["missing_review_count"],
        "handoff_acceptance_unresolved_review_count": (status["unresolved_review_count"]),
        "handoff_acceptance_rejection_reason_count": (status["rejection_reason_count"]),
        "handoff_acceptance_blocking_reason_count": (status["blocking_reason_count"]),
        "handoff_acceptance_runtime_stage": status["runtime_stage"],
        "handoff_acceptance_execution_permitted": False,
    }


def _phase11_acceptance_followup_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_acceptance_followup_status_summary(domain=domain)
    return {
        "acceptance_followup_contract_version": (PHASE11_ACCEPTANCE_FOLLOWUP_CONTRACT_VERSION),
        "acceptance_followup_id": status["followup_id"],
        "acceptance_followup_type": status["followup_type"],
        "acceptance_followup_status": status["status"],
        "acceptance_followup_acceptance_label": status["source_acceptance_label"],
        "acceptance_followup_acceptance_hash": status["source_acceptance_hash"],
        "acceptance_followup_blocker_summary": (status["blocker_disposition_summary"]),
        "acceptance_followup_reviewer_summary": status["reviewer_queue_summary"],
        "acceptance_followup_stale_summary": status["stale_renewal_summary"],
        "acceptance_followup_unresolved_review_count": (status["unresolved_review_count"]),
        "acceptance_followup_blocking_count": status["blocking_count"],
        "acceptance_followup_rejection_count": status["rejection_count"],
        "acceptance_followup_runtime_stage": status["runtime_stage"],
        "acceptance_followup_execution_permitted": False,
    }


def _phase11_followup_queue_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_followup_queue_index_status_summary(domain=domain)
    return {
        "followup_queue_index_contract_version": (PHASE11_FOLLOWUP_QUEUE_INDEX_CONTRACT_VERSION),
        "followup_queue_id": status["queue_id"],
        "followup_queue_fingerprint": status["queue_fingerprint"],
        "followup_queue_status": status["status"],
        "followup_queue_acceptance_status": status["acceptance_status"],
        "followup_queue_acceptance_id": status["acceptance_id"],
        "followup_queue_acceptance_fingerprint": status["acceptance_fingerprint"],
        "followup_queue_entry_count": status["entry_count"],
        "followup_queue_open_count": status["open_count"],
        "followup_queue_blocked_count": status["blocked_count"],
        "followup_queue_stale_count": status["stale_count"],
        "followup_queue_unresolved_review_count": (status["unresolved_review_count"]),
        "followup_queue_blocking_count": status["blocking_count"],
        "followup_queue_archived_count": status["archived_count"],
        "followup_queue_rejected_count": status["rejected_count"],
        "followup_queue_resolved_for_planning_count": (status["resolved_for_planning_count"]),
        "followup_queue_runtime_stage": status["runtime_stage"],
        "followup_queue_execution_permitted": False,
    }


def _phase11_decision_closeout_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_decision_closeout_status_summary(domain=domain)
    return {
        "decision_closeout_contract_version": (PHASE11_DECISION_CLOSEOUT_CONTRACT_VERSION),
        "decision_closeout_id": status["closeout_id"],
        "decision_closeout_queue_label": status["source_queue_label"],
        "decision_closeout_queue_hash": status["source_queue_hash"],
        "decision_closeout_decision": status["closeout_decision"],
        "decision_closeout_status": status["closeout_status"],
        "decision_closeout_reviewer_disposition_summary": (status["reviewer_disposition_summary"]),
        "decision_closeout_unresolved_review_count": (status["unresolved_review_count"]),
        "decision_closeout_blocker_count": status["blocker_count"],
        "decision_closeout_stale_count": status["stale_count"],
        "decision_closeout_archived_count": status["archived_count"],
        "decision_closeout_rejected_count": status["rejected_count"],
        "decision_closeout_deferred_count": status["deferred_count"],
        "decision_closeout_runtime_stage": status["runtime_stage"],
        "decision_closeout_execution_permitted": False,
    }


def _phase11_review_trail_export_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_review_trail_export_status_summary(domain=domain)
    return {
        "review_trail_export_contract_version": (PHASE11_REVIEW_TRAIL_EXPORT_CONTRACT_VERSION),
        "review_trail_export_id": status["export_id"],
        "review_trail_phase_range": status["phase_range"],
        "review_trail_covered_phase_count": status["covered_phase_count"],
        "review_trail_domain_label": status["domain_label"],
        "review_trail_closeout_decision": status["final_closeout_decision"],
        "review_trail_closeout_status": status["final_closeout_status"],
        "review_trail_unresolved_review_count": (status["unresolved_review_count"]),
        "review_trail_blocker_count": status["blocker_count"],
        "review_trail_stale_count": status["stale_count"],
        "review_trail_readiness_gap_summary": status["readiness_gap_summary"],
        "review_trail_runtime_stage": status["runtime_stage"],
        "review_trail_execution_permitted": False,
    }


def _phase11_runtime_gap_ledger_entry_fields(*, domain: str) -> dict[str, object]:
    status = phase11_runtime_authorization_gap_ledger_status_summary(domain=domain)
    return {
        "runtime_gap_ledger_contract_version": (
            PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION
        ),
        "runtime_gap_ledger_id": status["ledger_id"],
        "runtime_gap_phase_range": status["source_phase_range"],
        "runtime_gap_covered_phase_count": status["covered_phase_count"],
        "runtime_gap_domain_label": status["domain_label"],
        "runtime_gap_authorization_status": status["authorization_status"],
        "runtime_gap_readiness_gap": status["readiness_gap"],
        "runtime_gap_missing_future_gate_count": (status["missing_future_gate_count"]),
        "runtime_gap_unresolved_review_count": (status["unresolved_review_count"]),
        "runtime_gap_blocker_count": status["blocker_count"],
        "runtime_gap_stale_count": status["stale_count"],
        "runtime_gap_adapter_execution_granted": False,
        "runtime_gap_provider_execution_granted": False,
        "runtime_gap_model_execution_granted": False,
        "runtime_gap_runtime_stage": status["runtime_stage"],
        "runtime_gap_execution_permitted": False,
        "runtime_gap_real_mode_runtime_enabled": False,
    }


def _phase11_governance_closeout_entry_fields() -> dict[str, object]:
    status = phase11_planning_governance_closeout_status_summary()
    return {
        "governance_closeout_contract_version": (
            PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION
        ),
        "governance_closeout_id": status["closeout_index_id"],
        "governance_closeout_phase_range": status["phase_range"],
        "governance_closeout_covered_phase_count": (status["covered_phase_count"]),
        "governance_closeout_final_status": status["final_status"],
        "governance_closeout_runtime_authorization_status": (
            status["runtime_authorization_status"]
        ),
        "governance_closeout_readiness_gap": status["readiness_gap"],
        "governance_closeout_next_phase_requirement": (status["next_phase_requirement"]),
        "governance_closeout_gap_ledger_id": status["gap_ledger_id"],
        "governance_closeout_domain_count": status["domain_count"],
        "governance_closeout_unresolved_review_count": (status["unresolved_review_count"]),
        "governance_closeout_blocker_count": status["blocker_count"],
        "governance_closeout_stale_count": status["stale_count"],
        "governance_closeout_missing_future_gate_count": (status["missing_future_gate_count"]),
        "governance_closeout_adapter_execution_granted": False,
        "governance_closeout_provider_execution_granted": False,
        "governance_closeout_model_execution_granted": False,
        "governance_closeout_runtime_stage": status["runtime_stage"],
        "governance_closeout_execution_permitted": False,
        "governance_closeout_real_mode_runtime_enabled": False,
    }


CSI_EVIDENCE_PROVIDER_ID = "wifi-csi"
CSI_EVIDENCE_PROVIDER_KIND = "wifi-csi"
CSI_EVIDENCE_KIND = "csi-evidence-pack"
CSI_EVIDENCE_PACK_ARTIFACT_NAME = "csi_evidence_pack"
CSI_EVIDENCE_PACK_ARTIFACT_REF = "artifacts/csi_evidence_pack.json"
CSI_PARSER_INPUT_KINDS = (
    "csi-parser-fixtures",
    "csi-parser-fixture-set",
    "wifi-csi-parser-fixtures",
)
CSI_EVIDENCE_INPUT_KINDS = CSI_PARSER_INPUT_KINDS + (CSI_BATCH_GROUP_INPUT_KIND,)
CSI_PARSER_MAX_FIXTURE_REFS = CSI_BATCH_MAX_REFS_PER_GROUP
SENSOR_EVIDENCE_PROVIDER_MANIFEST_CONTRACT_VERSION = 1
SENSOR_EVIDENCE_PROVIDER_MANIFEST_KIND = "sensor-evidence-provider-registry-manifest"
SENSOR_EVIDENCE_PROVIDER_MANIFEST_COMPATIBILITY_CLASSIFICATIONS = (
    "compatible",
    "incompatible",
    "unsupported_version",
    "malformed",
)
SENSOR_EVIDENCE_PROVIDER_MANIFEST_REQUIRED_FIELDS = frozenset(
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
    }
)
SENSOR_EVIDENCE_PROVIDER_MANIFEST_REQUIRED_PROVIDER_FIELDS = frozenset(
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
    }
)
SENSOR_EVIDENCE_PROVIDER_MANIFEST_BLOCKED_FIELDS = frozenset(
    {
        "allowed_fixture_ref_formats",
        "artifact_ref",
        "fixture_refs",
        "group_input_kinds",
        "input_kinds",
        "max_fixture_groups",
        "max_fixture_refs",
        "max_refs_per_group",
        "parser_report_bodies_exported",
        "parser_summary_bodies_exported",
        "private_artifact_boundary",
        "provider_id_aliases",
        "provider_payload_bodies_exported",
        "value_payloads_exported",
    }
)
SENSOR_EVIDENCE_PROVIDER_MANIFEST_FORBIDDEN_KEY_FRAGMENTS = (
    "absolute",
    "credential",
    "device",
    "endpoint",
    "hardware",
    "host",
    "live",
    "network",
    "payload",
    "private",
    "raw",
    "secret",
    "source",
    "token",
    "unsafe",
    "url",
)
SENSOR_EVIDENCE_PROVIDER_MANIFEST_FORBIDDEN_VALUE_FRAGMENTS = (
    "amplitude",
    "clinical",
    "diagnosis",
    "health",
    "medical",
    "parser_report_body",
    "parser_summary_body",
    "phase",
    "provider_payload",
    "raw_csi",
    "raw_rf",
    "raw_signal",
    "raw_values",
    "rssi",
    "signal_values",
    "source_id",
    "source_ids",
    "treatment",
)

SENSOR_EVIDENCE_PROVIDER_ID_FIELDS = (
    "provider_id",
    "sensor_evidence_provider_id",
)
SENSOR_EVIDENCE_CONFIG_CREDENTIAL_KEYS = frozenset(
    {
        "access_token",
        "api_key",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "password",
        "refresh_token",
        "secret",
        "secret_value",
        "token",
    }
)
SENSOR_EVIDENCE_CONFIG_LIVE_DEVICE_NETWORK_KEYS = frozenset(
    {
        "adapter_id",
        "bssid",
        "capture_device",
        "device_id",
        "device_ids",
        "device_selector",
        "endpoint",
        "host",
        "hostname",
        "hardware_selector",
        "ip_address",
        "live_capture",
        "mac",
        "mqtt_topic",
        "network_endpoint",
        "pcap",
        "router_id",
        "serial_port",
        "ssid",
        "udp_port",
        "url",
    }
)
SENSOR_EVIDENCE_CONFIG_PRIVATE_FIELD_KEYS = frozenset(
    {
        "account_id",
        "email",
        "geolocation",
        "gps",
        "latitude",
        "local_path",
        "location",
        "longitude",
        "name",
        "participant_id",
        "patient_id",
        "phone",
        "private_ref",
        "private_refs",
        "profile_id",
        "run_dir",
        "session_id",
        "source_path",
        "staging_root",
        "subject_id",
        "unsafe_ref",
        "unsafe_refs",
        "user_id",
    }
)
SENSOR_EVIDENCE_CONFIG_PAYLOAD_FIELD_KEYS = frozenset(
    {
        "parser_report_body",
        "parser_summary_body",
        "provider_payload_body",
        "raw_values",
        "source_id",
        "source_ids",
    }
)
SENSOR_EVIDENCE_CONFIG_FORBIDDEN_KEYS = (
    SENSOR_EVIDENCE_CONFIG_CREDENTIAL_KEYS
    | SENSOR_EVIDENCE_CONFIG_LIVE_DEVICE_NETWORK_KEYS
    | SENSOR_EVIDENCE_CONFIG_PRIVATE_FIELD_KEYS
    | SENSOR_EVIDENCE_CONFIG_PAYLOAD_FIELD_KEYS
)
SENSOR_EVIDENCE_PRIVATE_VALUE_FRAGMENTS = (
    "fixture://",
    "fixtures/",
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "environment-parsed.csv",
    "environment-mixed.csv",
    "toy-counter-parsed.csv",
    "toy-counter-mixed.csv",
    "example.invalid",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "bearer ",
    "credential",
    "sk-",
)
SENSOR_EVIDENCE_REQUIRED_SENSOR_CONSTRAINTS = (
    "offline_required",
    "mock_only",
    "fixture_only",
    "research_only",
)
SENSOR_EVIDENCE_REQUIRED_FALSE_SENSOR_CONSTRAINTS = (
    "allow_hardware_access",
    "allow_live_capture",
    "allow_network_calls",
)
SENSOR_EVIDENCE_BLOCKED_TRUTHY_SENSOR_CONSTRAINTS = (
    "allow_audio_capture",
    "allow_baseline_export",
    "allow_ble",
    "allow_camera",
    "allow_clinician_action",
    "allow_clinician_review_action",
    "allow_database",
    "allow_driver_access",
    "allow_emergency_triage",
    "allow_external_memory",
    "allow_follow_up_capture",
    "allow_hardware_access",
    "allow_health_data_import",
    "allow_intervention_effectiveness_claim",
    "allow_intervention_recommendation",
    "allow_live_capture",
    "allow_medical_advice",
    "allow_medication_action",
    "allow_medication_recommendation",
    "allow_microphone",
    "allow_monitor_mode",
    "allow_network_calls",
    "allow_notification_automation",
    "allow_packet_capture",
    "allow_personal_data_export",
    "allow_personal_health_data_export",
    "allow_prescription",
    "allow_profile_storage",
    "allow_raw_csi_collection",
    "allow_raw_csi_export",
    "allow_raw_rf_collection",
    "allow_raw_rf_export",
    "allow_real_health_data",
    "allow_real_intervention",
    "allow_real_monitoring",
    "allow_real_profile_storage",
    "allow_real_response_monitoring",
    "allow_real_scheduling",
    "allow_recommendation",
    "allow_reminder_automation",
    "allow_response_effectiveness_claim",
    "allow_treatment_recommendation",
    "allow_wifi_csi_capture",
    "allow_wifi_network_probing",
)


@dataclass(frozen=True)
class SensorEvidenceProviderRegistryEntry:
    """Sanitized metadata for a fixture-only sensor evidence provider."""

    provider_id: str
    provider_kind: str
    evidence_kind: str
    contract_version: int
    artifact_name: str
    artifact_ref: str
    input_kinds: tuple[str, ...]
    supported_fixture_formats: tuple[str, ...]
    fixture_mode_labels: tuple[str, ...]
    offline_fixture_only: bool
    public_artifact_boundary: str
    private_artifact_boundary: str
    max_fixture_refs: int
    max_fixture_groups: int | None = None
    max_refs_per_group: int | None = None
    provider_id_aliases: tuple[str, ...] = ()
    group_input_kinds: tuple[str, ...] = ()
    allowed_fixture_ref_formats: tuple[str, ...] | None = None
    adapter_contract_version: int | None = None
    adapter_kind: str | None = None
    adapter_boundary_labels: tuple[str, ...] = ()
    readiness_gate_status: str | None = None
    readiness_gate_required_gates: tuple[str, ...] = ()
    readiness_gate_missing_gates: tuple[str, ...] = ()
    readiness_gate_ready: bool = False
    real_mode_execution_permitted: bool = False
    review_record_contract_version: int | None = None
    review_record_status: str | None = None
    review_record_reviewed_gate_count: int | None = None
    review_record_missing_gate_count: int | None = None
    review_record_rejected_gate_count: int | None = None
    review_record_runtime_stage: str | None = None
    review_record_execution_permitted: bool = False
    preflight_packet_contract_version: int | None = None
    preflight_packet_id: str | None = None
    preflight_packet_fingerprint: str | None = None
    preflight_packet_status: str | None = None
    preflight_packet_reviewed_gate_count: int | None = None
    preflight_packet_missing_gate_count: int | None = None
    preflight_packet_rejected_gate_count: int | None = None
    preflight_packet_runtime_stage: str | None = None
    preflight_packet_execution_permitted: bool = False
    lifecycle_audit_contract_version: int | None = None
    lifecycle_audit_record_id: str | None = None
    lifecycle_audit_record_fingerprint: str | None = None
    lifecycle_audit_stage: str | None = None
    lifecycle_audit_status: str | None = None
    lifecycle_audit_decision: str | None = None
    lifecycle_audit_signoff_verdict: str | None = None
    lifecycle_audit_signoff_count: int | None = None
    lifecycle_audit_decision_count: int | None = None
    lifecycle_audit_runtime_stage: str | None = None
    lifecycle_audit_execution_permitted: bool = False
    audit_index_contract_version: int | None = None
    audit_index_id: str | None = None
    audit_index_fingerprint: str | None = None
    audit_index_status: str | None = None
    audit_index_entry_count: int | None = None
    audit_index_blocking_count: int | None = None
    audit_index_rejection_count: int | None = None
    audit_index_supersession_chain_count: int | None = None
    audit_index_change_control_record_count: int | None = None
    audit_index_export_retention_policy_count: int | None = None
    audit_index_runtime_stage: str | None = None
    audit_index_execution_permitted: bool = False
    handoff_contract_version: int | None = None
    handoff_id: str | None = None
    handoff_fingerprint: str | None = None
    handoff_status: str | None = None
    handoff_entry_count: int | None = None
    handoff_blocking_count: int | None = None
    handoff_rejection_count: int | None = None
    handoff_unresolved_review_count: int | None = None
    handoff_runtime_stage: str | None = None
    handoff_execution_permitted: bool = False
    handoff_acceptance_contract_version: int | None = None
    handoff_acceptance_id: str | None = None
    handoff_acceptance_fingerprint: str | None = None
    handoff_acceptance_status: str | None = None
    handoff_acceptance_handoff_label: str | None = None
    handoff_acceptance_handoff_hash: str | None = None
    handoff_acceptance_handoff_fingerprint: str | None = None
    handoff_accepted_for_planning: bool = False
    handoff_acceptance_blocked: bool = True
    handoff_acceptance_stale: bool = False
    handoff_acceptance_missing_review_count: int | None = None
    handoff_acceptance_unresolved_review_count: int | None = None
    handoff_acceptance_rejection_reason_count: int | None = None
    handoff_acceptance_blocking_reason_count: int | None = None
    handoff_acceptance_runtime_stage: str | None = None
    handoff_acceptance_execution_permitted: bool = False
    acceptance_followup_contract_version: int | None = None
    acceptance_followup_id: str | None = None
    acceptance_followup_type: str | None = None
    acceptance_followup_status: str | None = None
    acceptance_followup_acceptance_label: str | None = None
    acceptance_followup_acceptance_hash: str | None = None
    acceptance_followup_blocker_summary: str | None = None
    acceptance_followup_reviewer_summary: str | None = None
    acceptance_followup_stale_summary: str | None = None
    acceptance_followup_unresolved_review_count: int | None = None
    acceptance_followup_blocking_count: int | None = None
    acceptance_followup_rejection_count: int | None = None
    acceptance_followup_runtime_stage: str | None = None
    acceptance_followup_execution_permitted: bool = False
    followup_queue_index_contract_version: int | None = None
    followup_queue_id: str | None = None
    followup_queue_fingerprint: str | None = None
    followup_queue_status: str | None = None
    followup_queue_acceptance_status: str | None = None
    followup_queue_acceptance_id: str | None = None
    followup_queue_acceptance_fingerprint: str | None = None
    followup_queue_entry_count: int | None = None
    followup_queue_open_count: int | None = None
    followup_queue_blocked_count: int | None = None
    followup_queue_stale_count: int | None = None
    followup_queue_unresolved_review_count: int | None = None
    followup_queue_blocking_count: int | None = None
    followup_queue_archived_count: int | None = None
    followup_queue_rejected_count: int | None = None
    followup_queue_resolved_for_planning_count: int | None = None
    followup_queue_runtime_stage: str | None = None
    followup_queue_execution_permitted: bool = False
    decision_closeout_contract_version: int | None = None
    decision_closeout_id: str | None = None
    decision_closeout_queue_label: str | None = None
    decision_closeout_queue_hash: str | None = None
    decision_closeout_decision: str | None = None
    decision_closeout_status: str | None = None
    decision_closeout_reviewer_disposition_summary: str | None = None
    decision_closeout_unresolved_review_count: int | None = None
    decision_closeout_blocker_count: int | None = None
    decision_closeout_stale_count: int | None = None
    decision_closeout_archived_count: int | None = None
    decision_closeout_rejected_count: int | None = None
    decision_closeout_deferred_count: int | None = None
    decision_closeout_runtime_stage: str | None = None
    decision_closeout_execution_permitted: bool = False
    review_trail_export_contract_version: int | None = None
    review_trail_export_id: str | None = None
    review_trail_phase_range: str | None = None
    review_trail_covered_phase_count: int | None = None
    review_trail_domain_label: str | None = None
    review_trail_closeout_decision: str | None = None
    review_trail_closeout_status: str | None = None
    review_trail_unresolved_review_count: int | None = None
    review_trail_blocker_count: int | None = None
    review_trail_stale_count: int | None = None
    review_trail_readiness_gap_summary: str | None = None
    review_trail_runtime_stage: str | None = None
    review_trail_execution_permitted: bool = False
    runtime_gap_ledger_contract_version: int | None = None
    runtime_gap_ledger_id: str | None = None
    runtime_gap_phase_range: str | None = None
    runtime_gap_covered_phase_count: int | None = None
    runtime_gap_domain_label: str | None = None
    runtime_gap_authorization_status: str | None = None
    runtime_gap_readiness_gap: str | None = None
    runtime_gap_missing_future_gate_count: int | None = None
    runtime_gap_unresolved_review_count: int | None = None
    runtime_gap_blocker_count: int | None = None
    runtime_gap_stale_count: int | None = None
    runtime_gap_adapter_execution_granted: bool = False
    runtime_gap_provider_execution_granted: bool = False
    runtime_gap_model_execution_granted: bool = False
    runtime_gap_runtime_stage: str | None = None
    runtime_gap_execution_permitted: bool = False
    runtime_gap_real_mode_runtime_enabled: bool = False
    governance_closeout_contract_version: int | None = None
    governance_closeout_id: str | None = None
    governance_closeout_phase_range: str | None = None
    governance_closeout_covered_phase_count: int | None = None
    governance_closeout_final_status: str | None = None
    governance_closeout_runtime_authorization_status: str | None = None
    governance_closeout_readiness_gap: str | None = None
    governance_closeout_next_phase_requirement: str | None = None
    governance_closeout_gap_ledger_id: str | None = None
    governance_closeout_domain_count: int | None = None
    governance_closeout_unresolved_review_count: int | None = None
    governance_closeout_blocker_count: int | None = None
    governance_closeout_stale_count: int | None = None
    governance_closeout_missing_future_gate_count: int | None = None
    governance_closeout_adapter_execution_granted: bool = False
    governance_closeout_provider_execution_granted: bool = False
    governance_closeout_model_execution_granted: bool = False
    governance_closeout_runtime_stage: str | None = None
    governance_closeout_execution_permitted: bool = False
    governance_closeout_real_mode_runtime_enabled: bool = False

    def matches_provider_id(self, provider_id: object) -> bool:
        text = _safe_identifier(provider_id)
        return text == self.provider_id or text in self.provider_id_aliases

    def matches_input_kind(self, input_kind: object) -> bool:
        return str(input_kind or "") in self.input_kinds

    def is_group_input_kind(self, input_kind: object) -> bool:
        return str(input_kind or "") in self.group_input_kinds

    def artifact_ref_spec(self) -> dict[str, str]:
        return {
            "provider_kind": self.provider_kind,
            "evidence_kind": self.evidence_kind,
        }

    def to_public_dict(self) -> dict[str, object]:
        payload = {
            "provider_id": self.provider_id,
            "provider_kind": self.provider_kind,
            "evidence_kind": self.evidence_kind,
            "contract_version": self.contract_version,
            "artifact_name": self.artifact_name,
            "artifact_ref": self.artifact_ref,
            "input_kinds": list(self.input_kinds),
            "supported_fixture_formats": list(self.supported_fixture_formats),
            "fixture_mode_labels": list(self.fixture_mode_labels),
            "offline_fixture_only": self.offline_fixture_only,
            "public_artifact_boundary": self.public_artifact_boundary,
            "private_artifact_boundary": self.private_artifact_boundary,
            "max_fixture_refs": self.max_fixture_refs,
            "max_fixture_groups": self.max_fixture_groups,
            "max_refs_per_group": self.max_refs_per_group,
            "metadata_only": True,
            "value_payloads_exported": False,
            "provider_bodies_exported": False,
        }
        if self.adapter_boundary_labels:
            payload["adapter_contract_version"] = self.adapter_contract_version
            payload["adapter_kind"] = self.adapter_kind or ""
            payload["adapter_boundary_labels"] = list(self.adapter_boundary_labels)
        if self.readiness_gate_status:
            payload["readiness_gate_contract_version"] = REAL_MODE_READINESS_GATE_CONTRACT_VERSION
            payload["readiness_gate_kind"] = REAL_MODE_READINESS_GATE_KIND
            payload["readiness_gate_status"] = self.readiness_gate_status
            payload["readiness_gate_required_gates"] = list(self.readiness_gate_required_gates)
            payload["readiness_gate_missing_gates"] = list(self.readiness_gate_missing_gates)
            payload["readiness_gate_ready"] = self.readiness_gate_ready
            payload["real_mode_execution_permitted"] = False
        if self.review_record_status:
            payload["review_record_contract_version"] = self.review_record_contract_version
            payload["review_record_status"] = self.review_record_status
            payload["review_record_reviewed_gate_count"] = self.review_record_reviewed_gate_count
            payload["review_record_missing_gate_count"] = self.review_record_missing_gate_count
            payload["review_record_rejected_gate_count"] = self.review_record_rejected_gate_count
            payload["review_record_runtime_stage"] = self.review_record_runtime_stage or ""
            payload["review_record_execution_permitted"] = False
        if self.preflight_packet_status:
            payload["preflight_packet_contract_version"] = self.preflight_packet_contract_version
            payload["preflight_packet_id"] = self.preflight_packet_id or ""
            payload["preflight_packet_fingerprint"] = self.preflight_packet_fingerprint or ""
            payload["preflight_packet_status"] = self.preflight_packet_status
            payload["preflight_packet_reviewed_gate_count"] = (
                self.preflight_packet_reviewed_gate_count
            )
            payload["preflight_packet_missing_gate_count"] = (
                self.preflight_packet_missing_gate_count
            )
            payload["preflight_packet_rejected_gate_count"] = (
                self.preflight_packet_rejected_gate_count
            )
            payload["preflight_packet_runtime_stage"] = self.preflight_packet_runtime_stage or ""
            payload["preflight_packet_execution_permitted"] = False
        if self.lifecycle_audit_status:
            payload["lifecycle_audit_contract_version"] = self.lifecycle_audit_contract_version
            payload["lifecycle_audit_record_id"] = self.lifecycle_audit_record_id or ""
            payload["lifecycle_audit_record_fingerprint"] = (
                self.lifecycle_audit_record_fingerprint or ""
            )
            payload["lifecycle_audit_stage"] = self.lifecycle_audit_stage or ""
            payload["lifecycle_audit_status"] = self.lifecycle_audit_status
            payload["lifecycle_audit_decision"] = self.lifecycle_audit_decision or ""
            payload["lifecycle_audit_signoff_verdict"] = self.lifecycle_audit_signoff_verdict or ""
            payload["lifecycle_audit_signoff_count"] = self.lifecycle_audit_signoff_count
            payload["lifecycle_audit_decision_count"] = self.lifecycle_audit_decision_count
            payload["lifecycle_audit_runtime_stage"] = self.lifecycle_audit_runtime_stage or ""
            payload["lifecycle_audit_execution_permitted"] = False
        if self.audit_index_status:
            payload["audit_index_contract_version"] = self.audit_index_contract_version
            payload["audit_index_id"] = self.audit_index_id or ""
            payload["audit_index_fingerprint"] = self.audit_index_fingerprint or ""
            payload["audit_index_status"] = self.audit_index_status
            payload["audit_index_entry_count"] = self.audit_index_entry_count
            payload["audit_index_blocking_count"] = self.audit_index_blocking_count
            payload["audit_index_rejection_count"] = self.audit_index_rejection_count
            payload["audit_index_supersession_chain_count"] = (
                self.audit_index_supersession_chain_count
            )
            payload["audit_index_change_control_record_count"] = (
                self.audit_index_change_control_record_count
            )
            payload["audit_index_export_retention_policy_count"] = (
                self.audit_index_export_retention_policy_count
            )
            payload["audit_index_runtime_stage"] = self.audit_index_runtime_stage or ""
            payload["audit_index_execution_permitted"] = False
        if self.handoff_status:
            payload["handoff_contract_version"] = self.handoff_contract_version
            payload["handoff_id"] = self.handoff_id or ""
            payload["handoff_fingerprint"] = self.handoff_fingerprint or ""
            payload["handoff_status"] = self.handoff_status
            payload["handoff_entry_count"] = self.handoff_entry_count
            payload["handoff_blocking_count"] = self.handoff_blocking_count
            payload["handoff_rejection_count"] = self.handoff_rejection_count
            payload["handoff_unresolved_review_count"] = self.handoff_unresolved_review_count
            payload["handoff_runtime_stage"] = self.handoff_runtime_stage or ""
            payload["handoff_execution_permitted"] = False
        if self.handoff_acceptance_status:
            payload["handoff_acceptance_contract_version"] = (
                self.handoff_acceptance_contract_version
            )
            payload["handoff_acceptance_id"] = self.handoff_acceptance_id or ""
            payload["handoff_acceptance_fingerprint"] = self.handoff_acceptance_fingerprint or ""
            payload["handoff_acceptance_status"] = self.handoff_acceptance_status
            payload["handoff_acceptance_handoff_label"] = (
                self.handoff_acceptance_handoff_label or ""
            )
            payload["handoff_acceptance_handoff_hash"] = self.handoff_acceptance_handoff_hash or ""
            payload["handoff_acceptance_handoff_fingerprint"] = (
                self.handoff_acceptance_handoff_fingerprint or ""
            )
            payload["handoff_accepted_for_planning"] = bool(self.handoff_accepted_for_planning)
            payload["handoff_acceptance_blocked"] = bool(self.handoff_acceptance_blocked)
            payload["handoff_acceptance_stale"] = bool(self.handoff_acceptance_stale)
            payload["handoff_acceptance_missing_review_count"] = (
                self.handoff_acceptance_missing_review_count
            )
            payload["handoff_acceptance_unresolved_review_count"] = (
                self.handoff_acceptance_unresolved_review_count
            )
            payload["handoff_acceptance_rejection_reason_count"] = (
                self.handoff_acceptance_rejection_reason_count
            )
            payload["handoff_acceptance_blocking_reason_count"] = (
                self.handoff_acceptance_blocking_reason_count
            )
            payload["handoff_acceptance_runtime_stage"] = (
                self.handoff_acceptance_runtime_stage or ""
            )
            payload["handoff_acceptance_execution_permitted"] = False
        if self.acceptance_followup_status:
            payload["acceptance_followup_contract_version"] = (
                self.acceptance_followup_contract_version
            )
            payload["acceptance_followup_id"] = self.acceptance_followup_id or ""
            payload["acceptance_followup_type"] = self.acceptance_followup_type or ""
            payload["acceptance_followup_status"] = self.acceptance_followup_status or ""
            payload["acceptance_followup_acceptance_label"] = (
                self.acceptance_followup_acceptance_label or ""
            )
            payload["acceptance_followup_acceptance_hash"] = (
                self.acceptance_followup_acceptance_hash or ""
            )
            payload["acceptance_followup_blocker_summary"] = (
                self.acceptance_followup_blocker_summary or ""
            )
            payload["acceptance_followup_reviewer_summary"] = (
                self.acceptance_followup_reviewer_summary or ""
            )
            payload["acceptance_followup_stale_summary"] = (
                self.acceptance_followup_stale_summary or ""
            )
            payload["acceptance_followup_unresolved_review_count"] = (
                self.acceptance_followup_unresolved_review_count
            )
            payload["acceptance_followup_blocking_count"] = self.acceptance_followup_blocking_count
            payload["acceptance_followup_rejection_count"] = (
                self.acceptance_followup_rejection_count
            )
            payload["acceptance_followup_runtime_stage"] = (
                self.acceptance_followup_runtime_stage or ""
            )
            payload["acceptance_followup_execution_permitted"] = False
        if self.followup_queue_status:
            payload["followup_queue_index_contract_version"] = (
                self.followup_queue_index_contract_version
            )
            payload["followup_queue_id"] = self.followup_queue_id or ""
            payload["followup_queue_fingerprint"] = self.followup_queue_fingerprint or ""
            payload["followup_queue_status"] = self.followup_queue_status or ""
            payload["followup_queue_acceptance_status"] = (
                self.followup_queue_acceptance_status or ""
            )
            payload["followup_queue_acceptance_id"] = self.followup_queue_acceptance_id or ""
            payload["followup_queue_acceptance_fingerprint"] = (
                self.followup_queue_acceptance_fingerprint or ""
            )
            payload["followup_queue_entry_count"] = self.followup_queue_entry_count
            payload["followup_queue_open_count"] = self.followup_queue_open_count
            payload["followup_queue_blocked_count"] = self.followup_queue_blocked_count
            payload["followup_queue_stale_count"] = self.followup_queue_stale_count
            payload["followup_queue_unresolved_review_count"] = (
                self.followup_queue_unresolved_review_count
            )
            payload["followup_queue_blocking_count"] = self.followup_queue_blocking_count
            payload["followup_queue_archived_count"] = self.followup_queue_archived_count
            payload["followup_queue_rejected_count"] = self.followup_queue_rejected_count
            payload["followup_queue_resolved_for_planning_count"] = (
                self.followup_queue_resolved_for_planning_count
            )
            payload["followup_queue_runtime_stage"] = self.followup_queue_runtime_stage or ""
            payload["followup_queue_execution_permitted"] = False
        if self.decision_closeout_status:
            payload["decision_closeout_contract_version"] = self.decision_closeout_contract_version
            payload["decision_closeout_id"] = self.decision_closeout_id or ""
            payload["decision_closeout_queue_label"] = self.decision_closeout_queue_label or ""
            payload["decision_closeout_queue_hash"] = self.decision_closeout_queue_hash or ""
            payload["decision_closeout_decision"] = self.decision_closeout_decision or ""
            payload["decision_closeout_status"] = self.decision_closeout_status or ""
            payload["decision_closeout_reviewer_disposition_summary"] = (
                self.decision_closeout_reviewer_disposition_summary or ""
            )
            payload["decision_closeout_unresolved_review_count"] = (
                self.decision_closeout_unresolved_review_count
            )
            payload["decision_closeout_blocker_count"] = self.decision_closeout_blocker_count
            payload["decision_closeout_stale_count"] = self.decision_closeout_stale_count
            payload["decision_closeout_archived_count"] = self.decision_closeout_archived_count
            payload["decision_closeout_rejected_count"] = self.decision_closeout_rejected_count
            payload["decision_closeout_deferred_count"] = self.decision_closeout_deferred_count
            payload["decision_closeout_runtime_stage"] = self.decision_closeout_runtime_stage or ""
            payload["decision_closeout_execution_permitted"] = False
        if self.review_trail_export_id:
            payload["review_trail_export_contract_version"] = (
                self.review_trail_export_contract_version
            )
            payload["review_trail_export_id"] = self.review_trail_export_id or ""
            payload["review_trail_phase_range"] = self.review_trail_phase_range or ""
            payload["review_trail_covered_phase_count"] = self.review_trail_covered_phase_count
            payload["review_trail_domain_label"] = self.review_trail_domain_label or ""
            payload["review_trail_closeout_decision"] = self.review_trail_closeout_decision or ""
            payload["review_trail_closeout_status"] = self.review_trail_closeout_status or ""
            payload["review_trail_unresolved_review_count"] = (
                self.review_trail_unresolved_review_count
            )
            payload["review_trail_blocker_count"] = self.review_trail_blocker_count
            payload["review_trail_stale_count"] = self.review_trail_stale_count
            payload["review_trail_readiness_gap_summary"] = (
                self.review_trail_readiness_gap_summary or ""
            )
            payload["review_trail_runtime_stage"] = self.review_trail_runtime_stage or ""
            payload["review_trail_execution_permitted"] = False
        if self.runtime_gap_ledger_id:
            payload["runtime_gap_ledger_contract_version"] = (
                self.runtime_gap_ledger_contract_version
            )
            payload["runtime_gap_ledger_id"] = self.runtime_gap_ledger_id or ""
            payload["runtime_gap_phase_range"] = self.runtime_gap_phase_range or ""
            payload["runtime_gap_covered_phase_count"] = self.runtime_gap_covered_phase_count
            payload["runtime_gap_domain_label"] = self.runtime_gap_domain_label or ""
            payload["runtime_gap_authorization_status"] = (
                self.runtime_gap_authorization_status or ""
            )
            payload["runtime_gap_readiness_gap"] = self.runtime_gap_readiness_gap or ""
            payload["runtime_gap_missing_future_gate_count"] = (
                self.runtime_gap_missing_future_gate_count
            )
            payload["runtime_gap_unresolved_review_count"] = (
                self.runtime_gap_unresolved_review_count
            )
            payload["runtime_gap_blocker_count"] = self.runtime_gap_blocker_count
            payload["runtime_gap_stale_count"] = self.runtime_gap_stale_count
            payload["runtime_gap_adapter_execution_granted"] = False
            payload["runtime_gap_provider_execution_granted"] = False
            payload["runtime_gap_model_execution_granted"] = False
            payload["runtime_gap_runtime_stage"] = self.runtime_gap_runtime_stage or ""
            payload["runtime_gap_execution_permitted"] = False
            payload["runtime_gap_real_mode_runtime_enabled"] = False
        if self.governance_closeout_id:
            payload["governance_closeout_contract_version"] = (
                self.governance_closeout_contract_version
            )
            payload["governance_closeout_id"] = self.governance_closeout_id or ""
            payload["governance_closeout_phase_range"] = self.governance_closeout_phase_range or ""
            payload["governance_closeout_covered_phase_count"] = (
                self.governance_closeout_covered_phase_count
            )
            payload["governance_closeout_final_status"] = (
                self.governance_closeout_final_status or ""
            )
            payload["governance_closeout_runtime_authorization_status"] = (
                self.governance_closeout_runtime_authorization_status or ""
            )
            payload["governance_closeout_readiness_gap"] = (
                self.governance_closeout_readiness_gap or ""
            )
            payload["governance_closeout_next_phase_requirement"] = (
                self.governance_closeout_next_phase_requirement or ""
            )
            payload["governance_closeout_gap_ledger_id"] = (
                self.governance_closeout_gap_ledger_id or ""
            )
            payload["governance_closeout_domain_count"] = self.governance_closeout_domain_count
            payload["governance_closeout_unresolved_review_count"] = (
                self.governance_closeout_unresolved_review_count
            )
            payload["governance_closeout_blocker_count"] = self.governance_closeout_blocker_count
            payload["governance_closeout_stale_count"] = self.governance_closeout_stale_count
            payload["governance_closeout_missing_future_gate_count"] = (
                self.governance_closeout_missing_future_gate_count
            )
            payload["governance_closeout_adapter_execution_granted"] = False
            payload["governance_closeout_provider_execution_granted"] = False
            payload["governance_closeout_model_execution_granted"] = False
            payload["governance_closeout_runtime_stage"] = (
                self.governance_closeout_runtime_stage or ""
            )
            payload["governance_closeout_execution_permitted"] = False
            payload["governance_closeout_real_mode_runtime_enabled"] = False
        return payload


@dataclass(frozen=True)
class SensorEvidenceWorkflowValidationResult:
    """Sanitized workflow-level validation result for evidence-provider config."""

    valid: bool
    error_count: int
    errors: tuple[str, ...]
    provider_count: int
    input_count: int
    sanitized: bool = True
    offline_fixture_only: bool = True
    metadata_only: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "error_categories": sensor_evidence_validation_error_categories(self.errors),
            "provider_count": self.provider_count,
            "input_count": self.input_count,
            "sanitized": self.sanitized,
            "offline_fixture_only": self.offline_fixture_only,
            "metadata_only": self.metadata_only,
        }


@dataclass(frozen=True)
class SensorEvidenceProviderManifestCompatibilityResult:
    """Sanitized compatibility result for provider registry manifests."""

    classification: str
    errors: tuple[str, ...]
    manifest_contract_version: int | None
    provider_count: int
    sanitized: bool = True
    metadata_only: bool = True
    offline_fixture_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.classification == "compatible"

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "error_count": len(self.errors),
            "errors": list(self.errors),
            "manifest_contract_version": self.manifest_contract_version,
            "provider_count": self.provider_count,
            "sanitized": self.sanitized,
            "metadata_only": self.metadata_only,
            "offline_fixture_only": self.offline_fixture_only,
        }


SENSOR_EVIDENCE_PROVIDER_REGISTRY = (
    SensorEvidenceProviderRegistryEntry(
        provider_id=CSI_EVIDENCE_PROVIDER_ID,
        provider_kind=CSI_EVIDENCE_PROVIDER_KIND,
        evidence_kind=CSI_EVIDENCE_KIND,
        contract_version=CSI_EVIDENCE_PACK_CONTRACT_VERSION,
        artifact_name=CSI_EVIDENCE_PACK_ARTIFACT_NAME,
        artifact_ref=CSI_EVIDENCE_PACK_ARTIFACT_REF,
        input_kinds=CSI_EVIDENCE_INPUT_KINDS,
        supported_fixture_formats=tuple(
            suffix.removeprefix(".") for suffix in SUPPORTED_CSI_FIXTURE_EXTENSIONS
        ),
        fixture_mode_labels=("parser-fixtures", "batch-replay-groups"),
        offline_fixture_only=True,
        public_artifact_boundary=(
            "run-relative pack ref, sha256, status, readiness, and fingerprint only"
        ),
        private_artifact_boundary="local parser diagnostics stay outside portable refs",
        max_fixture_refs=CSI_PARSER_MAX_FIXTURE_REFS,
        max_fixture_groups=CSI_BATCH_MAX_GROUPS,
        max_refs_per_group=CSI_BATCH_MAX_REFS_PER_GROUP,
        group_input_kinds=(CSI_BATCH_GROUP_INPUT_KIND,),
        allowed_fixture_ref_formats=("csv", "jsonl", "npz"),
        adapter_contract_version=CSI_SOURCE_ADAPTER_CONTRACT_VERSION,
        adapter_kind=CSI_SOURCE_ADAPTER_KIND,
        adapter_boundary_labels=CSI_SOURCE_ADAPTER_MANIFEST_LABELS,
        **_real_mode_gate_entry_fields(
            provider_kind=CSI_EVIDENCE_PROVIDER_ID,
            adapter_kind=CSI_SOURCE_ADAPTER_KIND,
            current_mode="reference-only",
        ),
        **_phase11_review_record_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_preflight_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_lifecycle_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_audit_index_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_audit_handoff_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_handoff_acceptance_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_acceptance_followup_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_followup_queue_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_decision_closeout_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_review_trail_export_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_runtime_gap_ledger_entry_fields(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        ),
        **_phase11_governance_closeout_entry_fields(),
    ),
    SensorEvidenceProviderRegistryEntry(
        provider_id=ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
        provider_kind=ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
        evidence_kind=ENVIRONMENT_EVIDENCE_KIND,
        contract_version=ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        artifact_name=ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_NAME,
        artifact_ref=ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_REF,
        input_kinds=ENVIRONMENT_FIXTURE_INPUT_KINDS,
        supported_fixture_formats=("csv",),
        fixture_mode_labels=("tabular-rows",),
        offline_fixture_only=True,
        public_artifact_boundary=(
            "run-relative pack ref, sha256, status, readiness, and fingerprint only"
        ),
        private_artifact_boundary="local row bodies stay outside portable refs",
        max_fixture_refs=MAX_ENVIRONMENT_FIXTURE_REFS,
        provider_id_aliases=(ENVIRONMENT_FIXTURE_PROVIDER_ID,),
    ),
    SensorEvidenceProviderRegistryEntry(
        provider_id=TOY_COUNTER_EVIDENCE_PROVIDER_KIND,
        provider_kind=TOY_COUNTER_EVIDENCE_PROVIDER_KIND,
        evidence_kind=TOY_COUNTER_EVIDENCE_KIND,
        contract_version=TOY_COUNTER_EVIDENCE_PACK_CONTRACT_VERSION,
        artifact_name=TOY_COUNTER_EVIDENCE_PACK_ARTIFACT_NAME,
        artifact_ref=TOY_COUNTER_EVIDENCE_PACK_ARTIFACT_REF,
        input_kinds=TOY_COUNTER_FIXTURE_INPUT_KINDS,
        supported_fixture_formats=("csv",),
        fixture_mode_labels=("count-status-rows",),
        offline_fixture_only=True,
        public_artifact_boundary=(
            "run-relative pack ref, sha256, status, readiness, and fingerprint only"
        ),
        private_artifact_boundary="local toy fixture row bodies stay outside portable refs",
        max_fixture_refs=MAX_TOY_COUNTER_FIXTURE_REFS,
    ),
    SensorEvidenceProviderRegistryEntry(
        provider_id=_DOCUMENT_EVIDENCE_PROVIDER_KIND,
        provider_kind=_DOCUMENT_EVIDENCE_PROVIDER_KIND,
        evidence_kind=_DOCUMENT_EVIDENCE_KIND,
        contract_version=_DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        artifact_name=_DOCUMENT_EVIDENCE_PACK_ARTIFACT_NAME,
        artifact_ref=_DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF,
        input_kinds=_DOCUMENT_FIXTURE_INPUT_KINDS,
        supported_fixture_formats=("json",),
        fixture_mode_labels=("document-count-status-metadata",),
        offline_fixture_only=True,
        public_artifact_boundary=(
            "run-relative pack ref, sha256, status, readiness, and fingerprint only"
        ),
        private_artifact_boundary="local document fixture bodies stay outside portable refs",
        max_fixture_refs=_MAX_DOCUMENT_FIXTURE_REFS,
        adapter_contract_version=_DOCUMENT_ADAPTER_CONTRACT_VERSION,
        adapter_kind=_DOCUMENT_ADAPTER_KIND,
        adapter_boundary_labels=_DOCUMENT_ADAPTER_BOUNDARY_LABELS,
        **_real_mode_gate_entry_fields(
            provider_kind=_DOCUMENT_EVIDENCE_PROVIDER_KIND,
            adapter_kind=_DOCUMENT_ADAPTER_KIND,
            current_mode="fixture-only",
        ),
        **_phase11_review_record_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_preflight_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_lifecycle_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_audit_index_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_audit_handoff_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_handoff_acceptance_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_acceptance_followup_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_followup_queue_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_decision_closeout_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_review_trail_export_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_runtime_gap_ledger_entry_fields(
            domain=PHASE11_DOCUMENT_DOMAIN,
        ),
        **_phase11_governance_closeout_entry_fields(),
    ),
)


def list_sensor_evidence_providers() -> tuple[SensorEvidenceProviderRegistryEntry, ...]:
    return SENSOR_EVIDENCE_PROVIDER_REGISTRY


def sensor_evidence_provider_metadata() -> tuple[dict[str, object], ...]:
    return tuple(entry.to_public_dict() for entry in SENSOR_EVIDENCE_PROVIDER_REGISTRY)


def sensor_evidence_provider_manifest() -> dict[str, object]:
    """Return the public, deterministic provider registry manifest."""

    providers = tuple(
        _sensor_evidence_provider_manifest_entry(entry)
        for entry in SENSOR_EVIDENCE_PROVIDER_REGISTRY
    )
    provider_order = [str(provider["provider_id"]) for provider in providers]
    return {
        "schema_version": SENSOR_EVIDENCE_PROVIDER_MANIFEST_CONTRACT_VERSION,
        "manifest_contract_version": (SENSOR_EVIDENCE_PROVIDER_MANIFEST_CONTRACT_VERSION),
        "manifest_kind": SENSOR_EVIDENCE_PROVIDER_MANIFEST_KIND,
        "provider_count": len(providers),
        "provider_order": provider_order,
        "providers": [dict(provider) for provider in providers],
        "sanitized": True,
        "metadata_only": True,
        "offline_fixture_only": all(
            bool(provider["offline_fixture_only"]) for provider in providers
        ),
        "public_boundary_label": "sanitized-provider-metadata-only",
    }


def classify_sensor_evidence_provider_manifest_compatibility(
    manifest: object,
) -> SensorEvidenceProviderManifestCompatibilityResult:
    """Validate a public provider manifest without echoing private values."""

    if not isinstance(manifest, Mapping):
        return SensorEvidenceProviderManifestCompatibilityResult(
            classification="malformed",
            errors=("manifest:sensor_provider_manifest_not_object",),
            manifest_contract_version=None,
            provider_count=0,
        )

    version = manifest.get("manifest_contract_version")
    if not isinstance(version, int):
        return SensorEvidenceProviderManifestCompatibilityResult(
            classification="malformed",
            errors=("manifest:sensor_provider_manifest_version_malformed",),
            manifest_contract_version=None,
            provider_count=_manifest_provider_count(manifest),
        )
    if version != SENSOR_EVIDENCE_PROVIDER_MANIFEST_CONTRACT_VERSION:
        return SensorEvidenceProviderManifestCompatibilityResult(
            classification="unsupported_version",
            errors=("manifest:sensor_provider_manifest_version_unsupported",),
            manifest_contract_version=version,
            provider_count=_manifest_provider_count(manifest),
        )

    errors = list(_sensor_evidence_manifest_shape_errors(manifest))
    errors.extend(_sensor_evidence_manifest_privacy_errors(manifest, "manifest"))
    classification = "compatible" if not errors else "incompatible"
    return SensorEvidenceProviderManifestCompatibilityResult(
        classification=classification,
        errors=tuple(sorted(set(errors))),
        manifest_contract_version=version,
        provider_count=_manifest_provider_count(manifest),
    )


def validate_sensor_evidence_provider_manifest(
    manifest: object,
) -> SensorEvidenceProviderManifestCompatibilityResult:
    return classify_sensor_evidence_provider_manifest_compatibility(manifest)


def _sensor_evidence_provider_manifest_entry(
    entry: SensorEvidenceProviderRegistryEntry,
) -> dict[str, object]:
    payload = {
        "provider_id": entry.provider_id,
        "provider_kind": entry.provider_kind,
        "evidence_kind": entry.evidence_kind,
        "contract_version": entry.contract_version,
        "contract_identity": f"{entry.evidence_kind}/v{entry.contract_version}",
        "artifact_name": entry.artifact_name,
        "fixture_mode_labels": list(entry.fixture_mode_labels),
        "supported_fixture_formats": list(entry.supported_fixture_formats),
        "offline_fixture_only": entry.offline_fixture_only,
        "metadata_only": True,
        "sanitized": True,
        "public_artifact_boundary": ("sanitized-pack-metadata-status-readiness-fingerprint"),
    }
    if entry.adapter_boundary_labels:
        payload["adapter_contract_version"] = entry.adapter_contract_version
        payload["adapter_kind"] = entry.adapter_kind or ""
        payload["adapter_boundary_labels"] = list(entry.adapter_boundary_labels)
    if entry.readiness_gate_status:
        payload["readiness_gate_contract_version"] = REAL_MODE_READINESS_GATE_CONTRACT_VERSION
        payload["readiness_gate_kind"] = REAL_MODE_READINESS_GATE_KIND
        payload["readiness_gate_status"] = entry.readiness_gate_status
        payload["readiness_gate_required_gates"] = list(entry.readiness_gate_required_gates)
        payload["readiness_gate_missing_gates"] = list(entry.readiness_gate_missing_gates)
        payload["readiness_gate_ready"] = entry.readiness_gate_ready
        payload["real_mode_execution_permitted"] = False
    if entry.review_record_status:
        payload["review_record_contract_version"] = entry.review_record_contract_version
        payload["review_record_status"] = entry.review_record_status
        payload["review_record_reviewed_gate_count"] = entry.review_record_reviewed_gate_count
        payload["review_record_missing_gate_count"] = entry.review_record_missing_gate_count
        payload["review_record_rejected_gate_count"] = entry.review_record_rejected_gate_count
        payload["review_record_runtime_stage"] = entry.review_record_runtime_stage or ""
        payload["review_record_execution_permitted"] = False
    if entry.preflight_packet_status:
        payload["preflight_packet_contract_version"] = entry.preflight_packet_contract_version
        payload["preflight_packet_id"] = entry.preflight_packet_id or ""
        payload["preflight_packet_fingerprint"] = entry.preflight_packet_fingerprint or ""
        payload["preflight_packet_status"] = entry.preflight_packet_status
        payload["preflight_packet_reviewed_gate_count"] = entry.preflight_packet_reviewed_gate_count
        payload["preflight_packet_missing_gate_count"] = entry.preflight_packet_missing_gate_count
        payload["preflight_packet_rejected_gate_count"] = entry.preflight_packet_rejected_gate_count
        payload["preflight_packet_runtime_stage"] = entry.preflight_packet_runtime_stage or ""
        payload["preflight_packet_execution_permitted"] = False
    if entry.lifecycle_audit_status:
        payload["lifecycle_audit_contract_version"] = entry.lifecycle_audit_contract_version
        payload["lifecycle_audit_record_id"] = entry.lifecycle_audit_record_id or ""
        payload["lifecycle_audit_record_fingerprint"] = (
            entry.lifecycle_audit_record_fingerprint or ""
        )
        payload["lifecycle_audit_stage"] = entry.lifecycle_audit_stage or ""
        payload["lifecycle_audit_status"] = entry.lifecycle_audit_status
        payload["lifecycle_audit_decision"] = entry.lifecycle_audit_decision or ""
        payload["lifecycle_audit_signoff_verdict"] = entry.lifecycle_audit_signoff_verdict or ""
        payload["lifecycle_audit_signoff_count"] = entry.lifecycle_audit_signoff_count
        payload["lifecycle_audit_decision_count"] = entry.lifecycle_audit_decision_count
        payload["lifecycle_audit_runtime_stage"] = entry.lifecycle_audit_runtime_stage or ""
        payload["lifecycle_audit_execution_permitted"] = False
    if entry.audit_index_status:
        payload["audit_index_contract_version"] = entry.audit_index_contract_version
        payload["audit_index_id"] = entry.audit_index_id or ""
        payload["audit_index_fingerprint"] = entry.audit_index_fingerprint or ""
        payload["audit_index_status"] = entry.audit_index_status
        payload["audit_index_entry_count"] = entry.audit_index_entry_count
        payload["audit_index_blocking_count"] = entry.audit_index_blocking_count
        payload["audit_index_rejection_count"] = entry.audit_index_rejection_count
        payload["audit_index_supersession_chain_count"] = entry.audit_index_supersession_chain_count
        payload["audit_index_change_control_record_count"] = (
            entry.audit_index_change_control_record_count
        )
        payload["audit_index_export_retention_policy_count"] = (
            entry.audit_index_export_retention_policy_count
        )
        payload["audit_index_runtime_stage"] = entry.audit_index_runtime_stage or ""
        payload["audit_index_execution_permitted"] = False
    if entry.handoff_status:
        payload["handoff_contract_version"] = entry.handoff_contract_version
        payload["handoff_id"] = entry.handoff_id or ""
        payload["handoff_fingerprint"] = entry.handoff_fingerprint or ""
        payload["handoff_status"] = entry.handoff_status
        payload["handoff_entry_count"] = entry.handoff_entry_count
        payload["handoff_blocking_count"] = entry.handoff_blocking_count
        payload["handoff_rejection_count"] = entry.handoff_rejection_count
        payload["handoff_unresolved_review_count"] = entry.handoff_unresolved_review_count
        payload["handoff_runtime_stage"] = entry.handoff_runtime_stage or ""
        payload["handoff_execution_permitted"] = False
    if entry.handoff_acceptance_status:
        payload["handoff_acceptance_contract_version"] = entry.handoff_acceptance_contract_version
        payload["handoff_acceptance_id"] = entry.handoff_acceptance_id or ""
        payload["handoff_acceptance_fingerprint"] = entry.handoff_acceptance_fingerprint or ""
        payload["handoff_acceptance_status"] = entry.handoff_acceptance_status
        payload["handoff_acceptance_handoff_label"] = entry.handoff_acceptance_handoff_label or ""
        payload["handoff_acceptance_handoff_hash"] = entry.handoff_acceptance_handoff_hash or ""
        payload["handoff_acceptance_handoff_fingerprint"] = (
            entry.handoff_acceptance_handoff_fingerprint or ""
        )
        payload["handoff_accepted_for_planning"] = bool(entry.handoff_accepted_for_planning)
        payload["handoff_acceptance_blocked"] = bool(entry.handoff_acceptance_blocked)
        payload["handoff_acceptance_stale"] = bool(entry.handoff_acceptance_stale)
        payload["handoff_acceptance_missing_review_count"] = (
            entry.handoff_acceptance_missing_review_count
        )
        payload["handoff_acceptance_unresolved_review_count"] = (
            entry.handoff_acceptance_unresolved_review_count
        )
        payload["handoff_acceptance_rejection_reason_count"] = (
            entry.handoff_acceptance_rejection_reason_count
        )
        payload["handoff_acceptance_blocking_reason_count"] = (
            entry.handoff_acceptance_blocking_reason_count
        )
        payload["handoff_acceptance_runtime_stage"] = entry.handoff_acceptance_runtime_stage or ""
        payload["handoff_acceptance_execution_permitted"] = False
    if entry.acceptance_followup_status:
        payload["acceptance_followup_contract_version"] = entry.acceptance_followup_contract_version
        payload["acceptance_followup_id"] = entry.acceptance_followup_id or ""
        payload["acceptance_followup_type"] = entry.acceptance_followup_type or ""
        payload["acceptance_followup_status"] = entry.acceptance_followup_status or ""
        payload["acceptance_followup_acceptance_label"] = (
            entry.acceptance_followup_acceptance_label or ""
        )
        payload["acceptance_followup_acceptance_hash"] = (
            entry.acceptance_followup_acceptance_hash or ""
        )
        payload["acceptance_followup_blocker_summary"] = (
            entry.acceptance_followup_blocker_summary or ""
        )
        payload["acceptance_followup_reviewer_summary"] = (
            entry.acceptance_followup_reviewer_summary or ""
        )
        payload["acceptance_followup_stale_summary"] = entry.acceptance_followup_stale_summary or ""
        payload["acceptance_followup_unresolved_review_count"] = (
            entry.acceptance_followup_unresolved_review_count
        )
        payload["acceptance_followup_blocking_count"] = entry.acceptance_followup_blocking_count
        payload["acceptance_followup_rejection_count"] = entry.acceptance_followup_rejection_count
        payload["acceptance_followup_runtime_stage"] = entry.acceptance_followup_runtime_stage or ""
        payload["acceptance_followup_execution_permitted"] = False
    if entry.followup_queue_status:
        payload["followup_queue_index_contract_version"] = (
            entry.followup_queue_index_contract_version
        )
        payload["followup_queue_id"] = entry.followup_queue_id or ""
        payload["followup_queue_fingerprint"] = entry.followup_queue_fingerprint or ""
        payload["followup_queue_status"] = entry.followup_queue_status or ""
        payload["followup_queue_acceptance_status"] = entry.followup_queue_acceptance_status or ""
        payload["followup_queue_acceptance_id"] = entry.followup_queue_acceptance_id or ""
        payload["followup_queue_acceptance_fingerprint"] = (
            entry.followup_queue_acceptance_fingerprint or ""
        )
        payload["followup_queue_entry_count"] = entry.followup_queue_entry_count
        payload["followup_queue_open_count"] = entry.followup_queue_open_count
        payload["followup_queue_blocked_count"] = entry.followup_queue_blocked_count
        payload["followup_queue_stale_count"] = entry.followup_queue_stale_count
        payload["followup_queue_unresolved_review_count"] = (
            entry.followup_queue_unresolved_review_count
        )
        payload["followup_queue_blocking_count"] = entry.followup_queue_blocking_count
        payload["followup_queue_archived_count"] = entry.followup_queue_archived_count
        payload["followup_queue_rejected_count"] = entry.followup_queue_rejected_count
        payload["followup_queue_resolved_for_planning_count"] = (
            entry.followup_queue_resolved_for_planning_count
        )
        payload["followup_queue_runtime_stage"] = entry.followup_queue_runtime_stage or ""
        payload["followup_queue_execution_permitted"] = False
    if entry.decision_closeout_status:
        payload["decision_closeout_contract_version"] = entry.decision_closeout_contract_version
        payload["decision_closeout_id"] = entry.decision_closeout_id or ""
        payload["decision_closeout_queue_label"] = entry.decision_closeout_queue_label or ""
        payload["decision_closeout_queue_hash"] = entry.decision_closeout_queue_hash or ""
        payload["decision_closeout_decision"] = entry.decision_closeout_decision or ""
        payload["decision_closeout_status"] = entry.decision_closeout_status or ""
        payload["decision_closeout_reviewer_disposition_summary"] = (
            entry.decision_closeout_reviewer_disposition_summary or ""
        )
        payload["decision_closeout_unresolved_review_count"] = (
            entry.decision_closeout_unresolved_review_count
        )
        payload["decision_closeout_blocker_count"] = entry.decision_closeout_blocker_count
        payload["decision_closeout_stale_count"] = entry.decision_closeout_stale_count
        payload["decision_closeout_archived_count"] = entry.decision_closeout_archived_count
        payload["decision_closeout_rejected_count"] = entry.decision_closeout_rejected_count
        payload["decision_closeout_deferred_count"] = entry.decision_closeout_deferred_count
        payload["decision_closeout_runtime_stage"] = entry.decision_closeout_runtime_stage or ""
        payload["decision_closeout_execution_permitted"] = False
    if entry.review_trail_export_id:
        payload["review_trail_export_contract_version"] = entry.review_trail_export_contract_version
        payload["review_trail_export_id"] = entry.review_trail_export_id or ""
        payload["review_trail_phase_range"] = entry.review_trail_phase_range or ""
        payload["review_trail_covered_phase_count"] = entry.review_trail_covered_phase_count
        payload["review_trail_domain_label"] = entry.review_trail_domain_label or ""
        payload["review_trail_closeout_decision"] = entry.review_trail_closeout_decision or ""
        payload["review_trail_closeout_status"] = entry.review_trail_closeout_status or ""
        payload["review_trail_unresolved_review_count"] = entry.review_trail_unresolved_review_count
        payload["review_trail_blocker_count"] = entry.review_trail_blocker_count
        payload["review_trail_stale_count"] = entry.review_trail_stale_count
        payload["review_trail_readiness_gap_summary"] = (
            entry.review_trail_readiness_gap_summary or ""
        )
        payload["review_trail_runtime_stage"] = entry.review_trail_runtime_stage or ""
        payload["review_trail_execution_permitted"] = False
    if entry.runtime_gap_ledger_id:
        payload["runtime_gap_ledger_contract_version"] = entry.runtime_gap_ledger_contract_version
        payload["runtime_gap_ledger_id"] = entry.runtime_gap_ledger_id or ""
        payload["runtime_gap_phase_range"] = entry.runtime_gap_phase_range or ""
        payload["runtime_gap_covered_phase_count"] = entry.runtime_gap_covered_phase_count
        payload["runtime_gap_domain_label"] = entry.runtime_gap_domain_label or ""
        payload["runtime_gap_authorization_status"] = entry.runtime_gap_authorization_status or ""
        payload["runtime_gap_readiness_gap"] = entry.runtime_gap_readiness_gap or ""
        payload["runtime_gap_missing_future_gate_count"] = (
            entry.runtime_gap_missing_future_gate_count
        )
        payload["runtime_gap_unresolved_review_count"] = entry.runtime_gap_unresolved_review_count
        payload["runtime_gap_blocker_count"] = entry.runtime_gap_blocker_count
        payload["runtime_gap_stale_count"] = entry.runtime_gap_stale_count
        payload["runtime_gap_adapter_execution_granted"] = False
        payload["runtime_gap_provider_execution_granted"] = False
        payload["runtime_gap_model_execution_granted"] = False
        payload["runtime_gap_runtime_stage"] = entry.runtime_gap_runtime_stage or ""
        payload["runtime_gap_execution_permitted"] = False
        payload["runtime_gap_real_mode_runtime_enabled"] = False
    if entry.governance_closeout_id:
        payload["governance_closeout_contract_version"] = entry.governance_closeout_contract_version
        payload["governance_closeout_id"] = entry.governance_closeout_id or ""
        payload["governance_closeout_phase_range"] = entry.governance_closeout_phase_range or ""
        payload["governance_closeout_covered_phase_count"] = (
            entry.governance_closeout_covered_phase_count
        )
        payload["governance_closeout_final_status"] = entry.governance_closeout_final_status or ""
        payload["governance_closeout_runtime_authorization_status"] = (
            entry.governance_closeout_runtime_authorization_status or ""
        )
        payload["governance_closeout_readiness_gap"] = entry.governance_closeout_readiness_gap or ""
        payload["governance_closeout_next_phase_requirement"] = (
            entry.governance_closeout_next_phase_requirement or ""
        )
        payload["governance_closeout_gap_ledger_id"] = entry.governance_closeout_gap_ledger_id or ""
        payload["governance_closeout_domain_count"] = entry.governance_closeout_domain_count
        payload["governance_closeout_unresolved_review_count"] = (
            entry.governance_closeout_unresolved_review_count
        )
        payload["governance_closeout_blocker_count"] = entry.governance_closeout_blocker_count
        payload["governance_closeout_stale_count"] = entry.governance_closeout_stale_count
        payload["governance_closeout_missing_future_gate_count"] = (
            entry.governance_closeout_missing_future_gate_count
        )
        payload["governance_closeout_adapter_execution_granted"] = False
        payload["governance_closeout_provider_execution_granted"] = False
        payload["governance_closeout_model_execution_granted"] = False
        payload["governance_closeout_runtime_stage"] = entry.governance_closeout_runtime_stage or ""
        payload["governance_closeout_execution_permitted"] = False
        payload["governance_closeout_real_mode_runtime_enabled"] = False
    return payload


def _sensor_evidence_manifest_shape_errors(
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    errors: list[str] = []
    expected = sensor_evidence_provider_manifest()
    missing = SENSOR_EVIDENCE_PROVIDER_MANIFEST_REQUIRED_FIELDS - set(manifest)
    if missing:
        errors.append("manifest:sensor_provider_manifest_required_field_missing")

    for field in (
        "schema_version",
        "manifest_kind",
        "provider_count",
        "provider_order",
        "sanitized",
        "metadata_only",
        "offline_fixture_only",
        "public_boundary_label",
    ):
        if field in manifest and manifest.get(field) != expected[field]:
            errors.append(f"manifest:sensor_provider_manifest_{field}_invalid")

    providers = manifest.get("providers")
    if not isinstance(providers, list):
        errors.append("manifest.providers:sensor_provider_manifest_providers_malformed")
        return tuple(errors)
    if len(providers) != len(SENSOR_EVIDENCE_PROVIDER_REGISTRY):
        errors.append("manifest.providers:sensor_provider_manifest_provider_count_invalid")

    provider_ids = [
        provider.get("provider_id") for provider in providers if isinstance(provider, Mapping)
    ]
    if tuple(provider_ids) != sensor_evidence_provider_ids():
        errors.append("manifest.providers:sensor_provider_manifest_order_invalid")
    if len(provider_ids) != len(set(provider_ids)):
        errors.append("manifest.providers:sensor_provider_manifest_provider_duplicate")

    expected_by_id = {str(provider["provider_id"]): provider for provider in expected["providers"]}
    for provider in providers:
        if not isinstance(provider, Mapping):
            errors.append("manifest.providers:sensor_provider_manifest_provider_malformed")
            continue
        provider_missing = SENSOR_EVIDENCE_PROVIDER_MANIFEST_REQUIRED_PROVIDER_FIELDS - set(
            provider
        )
        if provider_missing:
            errors.append("manifest.providers:sensor_provider_manifest_provider_field_missing")
        expected_provider = expected_by_id.get(str(provider.get("provider_id")))
        if expected_provider is None:
            errors.append("manifest.providers:sensor_provider_manifest_provider_unknown")
            continue
        for field, expected_value in expected_provider.items():
            if field not in provider:
                errors.append(
                    f"manifest.providers:sensor_provider_manifest_provider_{field}_missing"
                )
                continue
            if provider.get(field) != expected_value:
                errors.append(
                    f"manifest.providers:sensor_provider_manifest_provider_{field}_invalid"
                )
    return tuple(errors)


def _sensor_evidence_manifest_privacy_errors(
    value: object,
    path: str,
) -> tuple[str, ...]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            if _sensor_evidence_manifest_key_is_private(key):
                errors.append(f"{path}:sensor_provider_manifest_private_field_present")
                continue
            errors.extend(_sensor_evidence_manifest_privacy_errors(item, path))
        return tuple(errors)
    if isinstance(value, list):
        for item in value:
            errors.extend(_sensor_evidence_manifest_privacy_errors(item, path))
        return tuple(errors)
    if _sensor_evidence_manifest_scalar_is_private(value):
        errors.append(f"{path}:sensor_provider_manifest_private_scalar_present")
    return tuple(errors)


def _sensor_evidence_manifest_key_is_private(key: object) -> bool:
    text = str(key or "").lower()
    if text in SENSOR_EVIDENCE_PROVIDER_MANIFEST_BLOCKED_FIELDS:
        return True
    if text in SENSOR_EVIDENCE_CONFIG_FORBIDDEN_KEYS:
        return True
    return any(
        fragment in text for fragment in SENSOR_EVIDENCE_PROVIDER_MANIFEST_FORBIDDEN_KEY_FRAGMENTS
    )


def _sensor_evidence_manifest_scalar_is_private(value: object) -> bool:
    if value == PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP:
        return False
    if value in (
        "phase-11-planning-governance-complete",
        "explicit-future-phase-required-before-runtime-work",
    ):
        return False
    if _unsafe_scalar_value_code(value):
        return True
    if not isinstance(value, str):
        return False
    lowered = value.lower().replace("\\", "/")
    return any(
        fragment in lowered
        for fragment in SENSOR_EVIDENCE_PROVIDER_MANIFEST_FORBIDDEN_VALUE_FRAGMENTS
    )


def _manifest_provider_count(manifest: Mapping[str, object]) -> int:
    providers = manifest.get("providers")
    return len(providers) if isinstance(providers, list) else 0


def sensor_evidence_provider_ids() -> tuple[str, ...]:
    return tuple(entry.provider_id for entry in SENSOR_EVIDENCE_PROVIDER_REGISTRY)


def sensor_evidence_provider_by_id(
    provider_id: object,
) -> SensorEvidenceProviderRegistryEntry | None:
    for entry in SENSOR_EVIDENCE_PROVIDER_REGISTRY:
        if entry.matches_provider_id(provider_id):
            return entry
    return None


def sensor_evidence_provider_by_input_kind(
    input_kind: object,
) -> SensorEvidenceProviderRegistryEntry | None:
    for entry in SENSOR_EVIDENCE_PROVIDER_REGISTRY:
        if entry.matches_input_kind(input_kind):
            return entry
    return None


def sensor_evidence_provider_by_artifact_name(
    artifact_name: object,
) -> SensorEvidenceProviderRegistryEntry | None:
    text = str(artifact_name or "")
    for entry in SENSOR_EVIDENCE_PROVIDER_REGISTRY:
        if text == entry.artifact_name:
            return entry
    return None


def sensor_evidence_artifact_specs() -> dict[str, dict[str, str]]:
    return {
        entry.artifact_name: entry.artifact_ref_spec()
        for entry in SENSOR_EVIDENCE_PROVIDER_REGISTRY
    }


def sensor_evidence_validation_error_category(error: object) -> str:
    code = str(error or "unknown").rsplit(":", 1)[-1]
    return {
        "sensor_provider_unknown": "unknown_provider",
        "sensor_provider_kind_mismatch": "provider_kind_mismatch",
        "sensor_fixture_mode_unsupported": "unsupported_fixture_mode",
        "sensor_fixture_ref_count_exceeded": "excessive_count",
        "sensor_fixture_group_count_exceeded": "excessive_count",
        "sensor_fixture_ref_unsafe": "unsafe_ref",
        "sensor_fixture_ref_url_rejected": "unsafe_ref",
        "sensor_fixture_ref_absolute_path_rejected": "unsafe_ref",
        "sensor_fixture_ref_parent_traversal_rejected": "unsafe_ref",
        "sensor_fixture_ref_unsupported_format": "unsupported_fixture_format",
        "sensor_credential_field_present": "credential_like_field",
        "sensor_live_device_or_network_field_present": "live_device_network_field",
        "sensor_private_field_present": "private_field",
        "sensor_payload_body_field_present": "payload_body_field",
        "sensor_private_scalar_field_present": "private_scalar",
        "sensor_provider_constraints_missing": "offline_boundary_flag",
        "sensor_provider_required_flag_missing": "offline_boundary_flag",
        "sensor_provider_required_false_flag_missing": "offline_boundary_flag",
        "sensor_provider_blocked_flag_enabled": "offline_boundary_flag",
        "sensor_workflow_not_object": "workflow_shape",
    }.get(code, "workflow_shape")


def sensor_evidence_validation_error_categories(
    errors: tuple[str, ...],
) -> list[str]:
    return sorted({sensor_evidence_validation_error_category(error) for error in errors})


def validate_sensor_evidence_workflow_config(
    workflow: object,
) -> SensorEvidenceWorkflowValidationResult:
    if not isinstance(workflow, Mapping):
        return _validation_result(("workflow:sensor_workflow_not_object",), 0, 0)

    inputs = _list(workflow.get("inputs"))
    providers = _list(workflow.get("providers"))
    sensor_inputs = [
        (index, item)
        for index, item in enumerate(inputs)
        if isinstance(item, Mapping) and _sensor_evidence_input_entry(item) is not None
    ]
    explicit_provider_inputs = [
        (index, item)
        for index, item in enumerate(inputs)
        if isinstance(item, Mapping)
        and any(field in item for field in SENSOR_EVIDENCE_PROVIDER_ID_FIELDS)
        and (index, item) not in sensor_inputs
    ]
    all_sensor_inputs = sensor_inputs + explicit_provider_inputs
    if not all_sensor_inputs:
        return _validation_result((), _sensor_provider_count(providers), 0)

    errors: list[str] = []
    entries = set()
    for index, input_spec in all_sensor_inputs:
        entry = _sensor_evidence_input_entry(input_spec)
        if entry is not None:
            entries.add(entry.provider_id)
        errors.extend(_validate_sensor_input(input_spec, index, entry))

    sensor_providers = [
        (index, provider)
        for index, provider in enumerate(providers)
        if isinstance(provider, Mapping) and provider.get("class") == "sensor"
    ]
    if not sensor_providers:
        errors.append("providers:sensor_provider_missing")
    for index, provider in sensor_providers:
        errors.extend(_validate_sensor_provider(provider, index))

    return _validation_result(
        tuple(sorted(set(errors))),
        len(sensor_providers),
        len(all_sensor_inputs),
    )


def assert_sensor_evidence_workflow_config(workflow: object) -> None:
    result = validate_sensor_evidence_workflow_config(workflow)
    if not result.valid:
        raise ValueError("sensor evidence workflow config invalid: " + ", ".join(result.errors))


def workflow_sensor_evidence_fixture_refs(
    workflow: Mapping[str, object],
    provider_id: object,
) -> tuple[str, ...]:
    entry = sensor_evidence_provider_by_id(provider_id)
    if entry is None:
        return ()
    refs: list[str] = []
    for input_spec in _list(workflow.get("inputs")):
        if not isinstance(input_spec, Mapping):
            continue
        if not _input_matches_entry(input_spec, entry):
            continue
        if entry.is_group_input_kind(input_spec.get("kind")):
            continue
        refs.extend(_refs_tuple(input_spec))
    return tuple(refs)


def workflow_sensor_evidence_groups(
    workflow: Mapping[str, object],
    provider_id: object,
) -> tuple[dict[str, object], ...]:
    entry = sensor_evidence_provider_by_id(provider_id)
    if entry is None:
        return ()
    groups: list[dict[str, object]] = []
    for input_spec in _list(workflow.get("inputs")):
        if not isinstance(input_spec, Mapping):
            continue
        if not _input_matches_entry(input_spec, entry):
            continue
        if not entry.is_group_input_kind(input_spec.get("kind")):
            continue
        for group in _list(input_spec.get("groups")):
            groups.append(dict(group) if isinstance(group, Mapping) else {})
    return tuple(groups)


def sanitize_sensor_evidence_input_spec(
    input_spec: Mapping[str, object],
) -> dict[str, object]:
    entry = _sensor_evidence_input_entry(input_spec)
    if entry is None:
        return dict(input_spec)
    payload: dict[str, object] = {}
    if "id" in input_spec:
        payload["id"] = sensor_evidence_result_code(input_spec.get("id"))
    if "kind" in input_spec:
        payload["kind"] = sensor_evidence_result_code(input_spec.get("kind"))
    if "required" in input_spec:
        payload["required"] = bool(input_spec.get("required"))
    if "sensitivity" in input_spec:
        payload["sensitivity"] = sensor_evidence_result_code(input_spec.get("sensitivity"))
    payload["provider_id"] = entry.provider_id
    payload["evidence_kind"] = entry.evidence_kind
    payload["artifact_name"] = entry.artifact_name
    payload["artifact_ref"] = entry.artifact_ref
    payload["offline_fixture_only"] = entry.offline_fixture_only
    payload["refs_sanitized"] = True
    if entry.is_group_input_kind(input_spec.get("kind")):
        groups = _list(input_spec.get("groups"))
        group_id_prefix = (
            "csi-fixture-group"
            if entry.provider_id == CSI_EVIDENCE_PROVIDER_ID
            else f"{entry.provider_id}-fixture-group"
        )
        payload["group_count"] = len(groups)
        payload["max_group_count"] = entry.max_fixture_groups
        payload["max_refs_per_group"] = entry.max_refs_per_group
        payload["groups"] = [
            {
                "id": f"{group_id_prefix}-{index:03d}",
                "ref_count": len(_group_refs(group)),
            }
            for index, group in enumerate(
                groups[: entry.max_fixture_groups or len(groups)],
                start=1,
            )
        ]
    else:
        payload["ref_count"] = len(_refs_tuple(input_spec))
        payload["max_ref_count"] = entry.max_fixture_refs
    payload.pop("refs", None)
    payload.pop("ref", None)
    return payload


def _validate_sensor_input(
    input_spec: Mapping[str, object],
    index: int,
    entry: SensorEvidenceProviderRegistryEntry | None,
) -> tuple[str, ...]:
    path = f"inputs[{index}]"
    errors: list[str] = []
    explicit = _explicit_provider_id(input_spec)
    explicit_entry = sensor_evidence_provider_by_id(explicit) if explicit else None
    if explicit and explicit_entry is None:
        errors.append(f"{path}:sensor_provider_unknown")
    if explicit_entry is not None and entry is not None and explicit_entry != entry:
        errors.append(f"{path}:sensor_provider_kind_mismatch")
    if entry is None:
        return tuple(errors)
    if explicit_entry is not None and not explicit_entry.matches_input_kind(input_spec.get("kind")):
        errors.append(f"{path}:sensor_fixture_mode_unsupported")
    if _fixture_mode_value(input_spec) and not _entry_supports_fixture_mode(
        entry,
        _fixture_mode_value(input_spec),
    ):
        errors.append(f"{path}:sensor_fixture_mode_unsupported")

    errors.extend(_forbidden_key_errors(input_spec, path))
    if entry.is_group_input_kind(input_spec.get("kind")):
        groups = _list(input_spec.get("groups"))
        if len(groups) > (entry.max_fixture_groups or 0):
            errors.append(f"{path}:sensor_fixture_group_count_exceeded")
        for group_index, group in enumerate(groups):
            group_path = f"{path}.groups[{group_index}]"
            errors.extend(_forbidden_key_errors(group, group_path))
            refs = _group_refs(group)
            if len(refs) > (entry.max_refs_per_group or entry.max_fixture_refs):
                errors.append(f"{group_path}:sensor_fixture_ref_count_exceeded")
            errors.extend(_ref_errors(entry, refs, group_path))
        return tuple(errors)

    refs = _refs_tuple(input_spec)
    if len(refs) > entry.max_fixture_refs:
        errors.append(f"{path}:sensor_fixture_ref_count_exceeded")
    errors.extend(_ref_errors(entry, refs, path))
    return tuple(errors)


def _validate_sensor_provider(
    provider: Mapping[str, object],
    index: int,
) -> tuple[str, ...]:
    path = f"providers[{index}]"
    errors: list[str] = []
    errors.extend(_forbidden_key_errors(provider, path, allow_provider_constraints=True))
    constraints = provider.get("constraints")
    if not isinstance(constraints, Mapping):
        errors.append(f"{path}.constraints:sensor_provider_constraints_missing")
        constraints = {}
    for key in SENSOR_EVIDENCE_REQUIRED_SENSOR_CONSTRAINTS:
        if constraints.get(key) is not True:
            errors.append(f"{path}.constraints:sensor_provider_required_flag_missing")
    for key in SENSOR_EVIDENCE_REQUIRED_FALSE_SENSOR_CONSTRAINTS:
        if constraints.get(key) is not False:
            errors.append(f"{path}.constraints:sensor_provider_required_false_flag_missing")
    for key in SENSOR_EVIDENCE_BLOCKED_TRUTHY_SENSOR_CONSTRAINTS:
        if constraints.get(key) not in (False, None):
            errors.append(f"{path}.constraints:sensor_provider_blocked_flag_enabled")
    for key, value in constraints.items():
        if str(key).startswith("allow_") and value not in (False, None):
            errors.append(f"{path}.constraints:sensor_provider_blocked_flag_enabled")
    capabilities = provider.get("capabilities")
    if isinstance(capabilities, list):
        for capability in capabilities:
            errors.extend(_capability_errors(capability, path))
    return tuple(errors)


def _capability_errors(capability: object, path: str) -> tuple[str, ...]:
    text = str(capability or "")
    if "." not in text:
        return ()
    prefix = text.split(".", 1)[0]
    if prefix in {"sensor", "report"}:
        return ()
    if sensor_evidence_provider_by_id(prefix) is not None:
        return ()
    if text.endswith(("evidence-pack", "fixture-replay", "batch-replay-evaluation")):
        return (f"{path}.capabilities:sensor_provider_unknown",)
    return ()


def _ref_errors(
    entry: SensorEvidenceProviderRegistryEntry,
    refs: tuple[object, ...],
    path: str,
) -> tuple[str, ...]:
    errors = []
    for ref_index, ref in enumerate(refs):
        code = _fixture_ref_error_code(entry, ref)
        if code:
            errors.append(f"{path}.refs[{ref_index}]:{code}")
    return tuple(errors)


def _fixture_ref_error_code(
    entry: SensorEvidenceProviderRegistryEntry,
    ref: object,
) -> str:
    text = str(ref or "").strip()
    if not text:
        return "sensor_fixture_ref_unsafe"
    normalized = text.replace("\\", "/")
    if "://" in normalized:
        if entry.provider_id == CSI_EVIDENCE_PROVIDER_ID and normalized.startswith(
            "fixture://sensors/csi/"
        ):
            normalized = normalized.removeprefix("fixture://sensors/csi/")
        else:
            return "sensor_fixture_ref_url_rejected"
    if Path(normalized).is_absolute() or _looks_windows_absolute(normalized):
        return "sensor_fixture_ref_absolute_path_rejected"
    path = Path(normalized)
    if any(part in ("", ".", "..") for part in path.parts):
        return "sensor_fixture_ref_parent_traversal_rejected"
    if len(path.parts) != 1:
        return "sensor_fixture_ref_unsafe"
    suffix = path.suffix.lower().removeprefix(".")
    allowed_formats = entry.allowed_fixture_ref_formats or entry.supported_fixture_formats
    if suffix not in allowed_formats:
        return "sensor_fixture_ref_unsupported_format"
    return ""


def _forbidden_key_errors(
    value: object,
    path: str,
    *,
    allow_provider_constraints: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ()
    errors = []
    for key, item in value.items():
        safe_key = str(key).lower()
        if allow_provider_constraints and safe_key == "constraints":
            if isinstance(item, Mapping):
                errors.extend(
                    _forbidden_key_errors(
                        {
                            nested_key: nested_value
                            for nested_key, nested_value in item.items()
                            if not str(nested_key).startswith("allow_")
                        },
                        f"{path}.constraints",
                    )
                )
            continue
        if safe_key in {"ref", "refs", "groups", "description"}:
            if safe_key == "description" and _unsafe_scalar_value_code(item):
                errors.append(f"{path}:sensor_private_scalar_field_present")
            continue
        if safe_key in SENSOR_EVIDENCE_CONFIG_FORBIDDEN_KEYS:
            errors.append(f"{path}:{_forbidden_key_error_code(safe_key)}")
            continue
        if isinstance(item, Mapping):
            errors.extend(_forbidden_key_errors(item, path))
        elif isinstance(item, list):
            for nested in item:
                if isinstance(nested, Mapping):
                    errors.extend(_forbidden_key_errors(nested, path))
                elif _unsafe_scalar_value_code(nested):
                    errors.append(f"{path}:sensor_private_scalar_field_present")
        else:
            if _unsafe_scalar_value_code(item):
                errors.append(f"{path}:sensor_private_scalar_field_present")
    return tuple(errors)


def _forbidden_key_error_code(key: str) -> str:
    if key in SENSOR_EVIDENCE_CONFIG_CREDENTIAL_KEYS:
        return "sensor_credential_field_present"
    if key in SENSOR_EVIDENCE_CONFIG_LIVE_DEVICE_NETWORK_KEYS:
        return "sensor_live_device_or_network_field_present"
    if key in SENSOR_EVIDENCE_CONFIG_PAYLOAD_FIELD_KEYS:
        return "sensor_payload_body_field_present"
    return "sensor_private_field_present"


def _sensor_evidence_input_entry(
    input_spec: Mapping[str, object],
) -> SensorEvidenceProviderRegistryEntry | None:
    explicit = _explicit_provider_id(input_spec)
    explicit_entry = sensor_evidence_provider_by_id(explicit) if explicit else None
    kind_entry = sensor_evidence_provider_by_input_kind(input_spec.get("kind"))
    return kind_entry or explicit_entry


def _fixture_mode_value(input_spec: Mapping[str, object]) -> str:
    for field in ("fixture_mode", "fixture_mode_label", "fixture_mode_kind"):
        value = input_spec.get(field)
        if value:
            return _safe_identifier(value)
    return ""


def _entry_supports_fixture_mode(
    entry: SensorEvidenceProviderRegistryEntry,
    fixture_mode: str,
) -> bool:
    return fixture_mode in {_safe_identifier(label) for label in entry.fixture_mode_labels}


def _input_matches_entry(
    input_spec: Mapping[str, object],
    entry: SensorEvidenceProviderRegistryEntry,
) -> bool:
    explicit = _explicit_provider_id(input_spec)
    if explicit and not entry.matches_provider_id(explicit):
        return False
    return entry.matches_input_kind(input_spec.get("kind")) or bool(explicit)


def _explicit_provider_id(input_spec: Mapping[str, object]) -> str:
    for field in SENSOR_EVIDENCE_PROVIDER_ID_FIELDS:
        if field in input_spec:
            return _safe_identifier(input_spec.get(field))
    return ""


def _refs_tuple(value: Mapping[str, object]) -> tuple[object, ...]:
    refs = value.get("refs")
    if refs is None:
        refs = value.get("ref")
    if isinstance(refs, str):
        return (refs,)
    if isinstance(refs, list):
        return tuple(refs)
    return ()


def _group_refs(value: object) -> tuple[object, ...]:
    if not isinstance(value, Mapping):
        return ()
    refs = value.get("refs")
    if refs is None:
        refs = value.get("fixture_refs")
    if refs is None:
        refs = value.get("items")
    if isinstance(refs, str):
        return (refs,)
    if isinstance(refs, list):
        return tuple(refs)
    return ()


def _list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _sensor_provider_count(providers: list[object]) -> int:
    return len(
        [
            provider
            for provider in providers
            if isinstance(provider, Mapping) and provider.get("class") == "sensor"
        ]
    )


def _validation_result(
    errors: tuple[str, ...],
    provider_count: int,
    input_count: int,
) -> SensorEvidenceWorkflowValidationResult:
    safe_errors = tuple(_safe_error(error) for error in errors)
    return SensorEvidenceWorkflowValidationResult(
        valid=not safe_errors,
        error_count=len(safe_errors),
        errors=safe_errors,
        provider_count=provider_count,
        input_count=input_count,
    )


def _safe_error(value: object) -> str:
    text = str(value or "unknown")
    if ":" in text:
        path, code = text.rsplit(":", 1)
    else:
        path, code = "workflow", text
    safe_path = "".join(
        char if char.isalnum() or char in {"[", "]", ".", "_"} else "_" for char in path
    ).strip("_")
    return f"{safe_path or 'workflow'}:{sensor_evidence_result_code(code)}"


def _safe_identifier(value: object) -> str:
    text = str(value or "").lower()
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in text).strip(
        "-"
    )


def _looks_windows_absolute(value: str) -> bool:
    return len(value) >= 3 and value[1:3] == ":/" and value[0].isalpha()


def _unsafe_scalar_value_code(value: object) -> str:
    if not isinstance(value, str):
        return ""
    lowered = value.lower().replace("\\", "/")
    if "://" in lowered:
        return "sensor_private_scalar_field_present"
    if _looks_windows_absolute(lowered):
        return "sensor_private_scalar_field_present"
    if any(fragment in lowered for fragment in SENSOR_EVIDENCE_PRIVATE_VALUE_FRAGMENTS):
        return "sensor_private_scalar_field_present"
    return ""


__all__ = [
    "CSI_EVIDENCE_KIND",
    "CSI_EVIDENCE_PACK_ARTIFACT_NAME",
    "CSI_EVIDENCE_PACK_ARTIFACT_REF",
    "CSI_EVIDENCE_PROVIDER_ID",
    "CSI_EVIDENCE_PROVIDER_KIND",
    "CSI_EVIDENCE_INPUT_KINDS",
    "CSI_PARSER_INPUT_KINDS",
    "SensorEvidenceProviderRegistryEntry",
    "SensorEvidenceProviderManifestCompatibilityResult",
    "SensorEvidenceWorkflowValidationResult",
    "SENSOR_EVIDENCE_PROVIDER_MANIFEST_COMPATIBILITY_CLASSIFICATIONS",
    "SENSOR_EVIDENCE_PROVIDER_MANIFEST_CONTRACT_VERSION",
    "SENSOR_EVIDENCE_PROVIDER_MANIFEST_KIND",
    "TOY_COUNTER_EVIDENCE_KIND",
    "TOY_COUNTER_EVIDENCE_PACK_ARTIFACT_NAME",
    "TOY_COUNTER_EVIDENCE_PACK_ARTIFACT_REF",
    "TOY_COUNTER_EVIDENCE_PROVIDER_KIND",
    "assert_sensor_evidence_workflow_config",
    "classify_sensor_evidence_provider_manifest_compatibility",
    "list_sensor_evidence_providers",
    "sanitize_sensor_evidence_input_spec",
    "sensor_evidence_artifact_specs",
    "sensor_evidence_provider_by_artifact_name",
    "sensor_evidence_provider_by_id",
    "sensor_evidence_provider_by_input_kind",
    "sensor_evidence_provider_ids",
    "sensor_evidence_provider_manifest",
    "sensor_evidence_provider_metadata",
    "sensor_evidence_validation_error_categories",
    "sensor_evidence_validation_error_category",
    "validate_sensor_evidence_provider_manifest",
    "validate_sensor_evidence_workflow_config",
    "workflow_sensor_evidence_fixture_refs",
    "workflow_sensor_evidence_groups",
]
