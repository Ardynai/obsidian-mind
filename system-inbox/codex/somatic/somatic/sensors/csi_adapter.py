"""Metadata-only WiFi CSI source adapter boundary.

The boundary is for future CSI source/provider work only.  The current
implementation emits deterministic reference metadata and validates it before
CSI planning metadata consumes it; it never opens hardware, captures packets, or
runs external models.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from somatic.safety.adapter_readiness import evaluate_real_mode_readiness
from somatic.safety.phase11_contracts import (
    PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_LABELS,
    PHASE11_AUDIT_HANDOFF_STATUS_LABELS,
    PHASE11_AUDIT_INDEX_STATUS_LABELS,
    PHASE11_CONTRACT_STATUS_LABELS,
    PHASE11_DECISION_CLOSEOUT_STATUS_LABELS,
    PHASE11_FOLLOWUP_QUEUE_STATUS_LABELS,
    PHASE11_HANDOFF_ACCEPTANCE_STATUS_LABELS,
    PHASE11_LIFECYCLE_STATUS_LABELS,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS_LABELS,
    PHASE11_PREFLIGHT_STATUS_LABELS,
    PHASE11_REVIEW_RECORD_STATUS_LABELS,
    PHASE11_REVIEW_TRAIL_EXPORT_STATUS_LABELS,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS_LABELS,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_acceptance_followup_status_summary,
    phase11_audit_handoff_status_summary,
    phase11_audit_index_status_summary,
    phase11_contract_status_summary,
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

CSI_SOURCE_ADAPTER_CONTRACT_VERSION = 1
CSI_SOURCE_ADAPTER_KIND = "metadata-wifi-csi-source-adapter"
CSI_FIXTURE_SOURCE_ADAPTER_LABEL = "wifi-csi-fixture-source-boundary-v1"
CSI_RUVIEW_REFERENCE_STATUS = "conditional-reference-only"
CSI_RUVIEW_DEPENDENCY_STATUS = CSI_RUVIEW_REFERENCE_STATUS
CSI_BOOTH_PROFILE_LABEL = "booth-first-single-subject-v1"

CSI_SOURCE_ADAPTER_CAPABILITY_LABELS = (
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
    *PHASE11_CONTRACT_STATUS_LABELS,
    *PHASE11_REVIEW_RECORD_STATUS_LABELS,
    *PHASE11_PREFLIGHT_STATUS_LABELS,
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
CSI_SOURCE_ADAPTER_MANIFEST_LABELS = (
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
    *PHASE11_CONTRACT_STATUS_LABELS,
    *PHASE11_REVIEW_RECORD_STATUS_LABELS,
    *PHASE11_PREFLIGHT_STATUS_LABELS,
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
CSI_RUVIEW_WARNING_HISTORY = (
    "earlier-overclaims",
    "incompatible-model-loading-concerns",
    "unverified-deployment-claims",
    "self-published-v2-materials-only",
)
CSI_RUVIEW_REQUIRED_FALSE_FIELDS = (
    "runtime_dependency",
    "local_source_staged",
    "source_vendored",
    "source_copied",
    "source_imported",
    "source_executed",
)
CSI_BOOTH_REQUIRED_RESEARCH_NOTES = (
    "phase-variance",
    "conjugation",
    "temporal-embedding",
)
CSI_SOURCE_ADAPTER_ALLOWED_OUTPUT_FIELDS = frozenset(
    {
        "status",
        "ruview_reference",
        "booth_planning_profile",
        "metadata_only",
        "reference_only",
        "offline",
        "fixture_backed",
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
        "diagnosis",
        "treatment",
        "emergency_triage",
        "medical_or_clinical_claim",
        "raw_signal_export",
    }
)
CSI_SOURCE_ADAPTER_REQUIRED_TRUE_FLAGS = (
    "metadata_only",
    "reference_only",
    "offline",
    "fixture_backed",
)
CSI_SOURCE_ADAPTER_REQUIRED_FALSE_FLAGS = (
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
    "diagnosis",
    "treatment",
    "emergency_triage",
    "medical_or_clinical_claim",
    "raw_signal_export",
)
CSI_SOURCE_ADAPTER_FORBIDDEN_KEYS = frozenset(
    {
        "absolute_path",
        "absolute_paths",
        "access_token",
        "adapter_id",
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
        "local_path",
        "mac",
        "model_body",
        "model_weights",
        "password",
        "path",
        "paths",
        "payload",
        "private_ref",
        "private_refs",
        "provider_body",
        "provider_payload",
        "raw_csi",
        "raw_rf",
        "raw_signal",
        "raw_values",
        "refresh_token",
        "remote_url",
        "router_id",
        "secret",
        "secret_value",
        "source_id",
        "source_ids",
        "source_path",
        "ssid",
        "token",
        "url",
        "urls",
        "weights",
    }
)
CSI_SOURCE_ADAPTER_FORBIDDEN_KEY_FRAGMENTS = (
    "access_token",
    "api_key",
    "authorization",
    "credential",
    "fixture_ref",
    "local_path",
    "model_body",
    "model_weight",
    "private_ref",
    "provider_body",
    "provider_payload",
    "raw_",
    "refresh_token",
    "remote_url",
    "secret",
    "source_id",
    "source_path",
)
CSI_SOURCE_ADAPTER_FORBIDDEN_VALUE_FRAGMENTS = (
    "://",
    "c:/",
    "c:\\",
    "/home/",
    "\\home\\",
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "fixture://",
    "fixtures/",
    "raw_values",
    "raw_csi",
    "raw_rf",
    "raw signal",
    "source_id",
    "source_ids",
    "device_id",
    "router_id",
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
    "example.invalid",
)


@dataclass(frozen=True)
class CsiSourceAdapterOutputValidationResult:
    """Sanitized fail-closed validation result for CSI source metadata."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_output: dict[str, object]
    sanitized: bool = True
    metadata_only: bool = True
    fixture_backed: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_output.get("status") or "rejected")

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
            "metadata_only": self.metadata_only,
            "fixture_backed": self.fixture_backed,
        }


def wifi_csi_source_adapter_status() -> dict[str, object]:
    """Return public status for the fixture-backed CSI source boundary."""

    real_mode_gate = wifi_csi_real_mode_readiness_gate()
    phase11_status = phase11_contract_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        readiness_gate=real_mode_gate,
    )
    review_record_status = phase11_review_record_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    preflight_status = phase11_preflight_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    lifecycle_status = phase11_dossier_lifecycle_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    audit_index_status = phase11_audit_index_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    audit_handoff_status = phase11_audit_handoff_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    handoff_acceptance_status = phase11_handoff_acceptance_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    acceptance_followup_status = phase11_acceptance_followup_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    followup_queue_status = phase11_followup_queue_index_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    decision_closeout_status = phase11_decision_closeout_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    review_trail_export_status = phase11_review_trail_export_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    runtime_gap_ledger_status = phase11_runtime_authorization_gap_ledger_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    planning_governance_closeout_status = phase11_planning_governance_closeout_status_summary()
    return {
        "schema_version": 1,
        "adapter_contract_version": CSI_SOURCE_ADAPTER_CONTRACT_VERSION,
        "adapter_kind": CSI_SOURCE_ADAPTER_KIND,
        "status": "reference-only-ready",
        "capability_labels": list(CSI_SOURCE_ADAPTER_CAPABILITY_LABELS),
        "metadata_only": True,
        "reference_only": True,
        "fixture_backed": True,
        "offline": True,
        "sanitized": True,
        "fail_closed_output_validation": True,
        "hardware_access": False,
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
        "vitals_inference": False,
        "diagnosis": False,
        "treatment": False,
        "emergency_triage": False,
        "medical_or_clinical_claim": False,
        "raw_signal_export": False,
        "real_mode_readiness_gate": real_mode_gate,
        "real_mode_readiness_status": real_mode_gate["status"],
        "real_mode_execution_permitted": False,
        "p11a_contract_status": phase11_status,
        "p11b_review_record_status": review_record_status,
        "p11c_preflight_status": preflight_status,
        "p11d_lifecycle_audit_status": lifecycle_status,
        "p11e_audit_index_status": audit_index_status,
        "p11f_audit_handoff_status": audit_handoff_status,
        "p11g_handoff_acceptance_status": handoff_acceptance_status,
        "p11h_acceptance_followup_status": acceptance_followup_status,
        "p11i_followup_queue_index_status": followup_queue_status,
        "p11j_decision_closeout_status": decision_closeout_status,
        "p11k_review_trail_export_status": review_trail_export_status,
        "p11l_runtime_gap_ledger_status": runtime_gap_ledger_status,
        "p11m_planning_governance_closeout_status": (planning_governance_closeout_status),
    }


def wifi_csi_real_mode_readiness_gate(
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the shared real-mode gate for the WiFi CSI source boundary."""

    return evaluate_real_mode_readiness(
        provider_kind="wifi-csi",
        adapter_kind=CSI_SOURCE_ADAPTER_KIND,
        current_mode="reference-only",
        review_record=review_record,
    ).to_dict()


def ruview_reference_metadata() -> dict[str, object]:
    """Return sanitized RuView reassessment metadata."""

    return {
        "repo": "ruvnet/RuView",
        "status": CSI_RUVIEW_REFERENCE_STATUS,
        "reference_only": True,
        "reassessable": True,
        "runtime_dependency": False,
        "local_source_staged": False,
        "source_vendored": False,
        "source_copied": False,
        "source_imported": False,
        "source_executed": False,
        "v2_reassessment": {
            "rust_workspace_reported": True,
            "wifi_densepose_crates_reported": True,
            "signal_pipeline_crates_reported": True,
            "temporal_embedding_metric_reported": True,
            "downstream_accuracy_validated": False,
            "deployment_claims_verified": False,
        },
        "warning_history": [
            "earlier-overclaims",
            "incompatible-model-loading-concerns",
            "unverified-deployment-claims",
            "self-published-v2-materials-only",
        ],
        "somatic_posture": "track-only-do-not-run-or-depend",
    }


def booth_first_csi_planning_profile() -> dict[str, object]:
    """Return a future booth-first CSI architecture profile as metadata only."""

    return {
        "profile": CSI_BOOTH_PROFILE_LABEL,
        "status": "future-planning-metadata-only",
        "single_subject": True,
        "space": "small-controlled-booth",
        "future_topology": "fixed-ap-plus-4-to-6-receiver-nodes",
        "preferred_radio_family": "esp32-s3",
        "empty_booth_baseline": "planned-reference-concept",
        "room_adaptation_logic": "skipped",
        "research_note_labels": [
            "phase-variance",
            "conjugation",
            "temporal-embedding",
        ],
        "reference_only": True,
        "metadata_only": True,
        "hardware_access": False,
        "packet_capture": False,
        "model_execution": False,
        "vitals_inference": False,
    }


def fixture_csi_source_adapter_output() -> dict[str, object]:
    """Return deterministic CSI source metadata for the current fixture boundary."""

    return {
        "status": "accepted",
        "ruview_reference": ruview_reference_metadata(),
        "booth_planning_profile": booth_first_csi_planning_profile(),
        "metadata_only": True,
        "reference_only": True,
        "offline": True,
        "fixture_backed": True,
        "hardware_access": False,
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
        "vitals_inference": False,
        "diagnosis": False,
        "treatment": False,
        "emergency_triage": False,
        "medical_or_clinical_claim": False,
        "raw_signal_export": False,
    }


def validate_csi_source_adapter_output(
    output: object,
) -> CsiSourceAdapterOutputValidationResult:
    """Validate and sanitize metadata-only CSI source adapter output."""

    if not isinstance(output, Mapping):
        return _invalid_result(("csi_source_adapter_output_not_object",), "malformed")

    errors: list[str] = []
    unknown_fields = set(str(key) for key in output) - CSI_SOURCE_ADAPTER_ALLOWED_OUTPUT_FIELDS
    if unknown_fields:
        errors.append("csi_source_adapter_output_unknown_field")

    privacy_violations = _adapter_privacy_violation_count(output)
    if privacy_violations:
        errors.append("csi_source_adapter_output_privacy_boundary")

    if not isinstance(output.get("ruview_reference"), Mapping):
        errors.append("csi_source_adapter_ruview_missing")
    else:
        errors.extend(_ruview_reference_contract_errors(output["ruview_reference"]))
    if not isinstance(output.get("booth_planning_profile"), Mapping):
        errors.append("csi_source_adapter_booth_profile_missing")
    else:
        errors.extend(_booth_profile_contract_errors(output["booth_planning_profile"]))

    for field in CSI_SOURCE_ADAPTER_REQUIRED_TRUE_FLAGS:
        if output.get(field) is not True:
            errors.append("csi_source_adapter_required_true_flag_missing")
            break
    for field in CSI_SOURCE_ADAPTER_REQUIRED_FALSE_FLAGS:
        if output.get(field) is not False:
            errors.append("csi_source_adapter_closed_flag_not_preserved")
            break

    if errors:
        return _invalid_result(
            tuple(sorted(set(errors))),
            "incompatible",
            privacy_violation_count=privacy_violations,
        )

    return CsiSourceAdapterOutputValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_output=_sanitize_csi_source_adapter_output(output),
    )


def sanitize_csi_source_adapter_output(output: object) -> dict[str, object]:
    """Return safe CSI source metadata, rejecting unsafe output fail-closed."""

    return validate_csi_source_adapter_output(output).sanitized_output


def rejected_csi_source_adapter_output(
    category: str = "csi-source-adapter-output-rejected",
) -> dict[str, object]:
    safe_category = _safe_adapter_category(category)
    return {
        "status": "rejected",
        "ruview_reference": {
            "repo": "ruvnet/RuView",
            "status": "rejected-fail-closed",
            "reference_only": True,
            "reassessable": False,
            "runtime_dependency": False,
            "local_source_staged": False,
            "source_vendored": False,
        },
        "booth_planning_profile": {
            "profile": CSI_BOOTH_PROFILE_LABEL,
            "status": "rejected-fail-closed",
            "single_subject": True,
            "space": "small-controlled-booth",
            "future_topology": "metadata-withheld",
            "preferred_radio_family": "metadata-withheld",
            "empty_booth_baseline": "metadata-withheld",
            "room_adaptation_logic": "metadata-withheld",
            "research_note_labels": [],
        },
        "metadata_only": True,
        "reference_only": True,
        "offline": True,
        "fixture_backed": True,
        "hardware_access": False,
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
        "vitals_inference": False,
        "diagnosis": False,
        "treatment": False,
        "emergency_triage": False,
        "medical_or_clinical_claim": False,
        "raw_signal_export": False,
        "parse_error_categories": {safe_category: 1},
    }


def _invalid_result(
    errors: tuple[str, ...],
    classification: str,
    *,
    privacy_violation_count: int = 0,
) -> CsiSourceAdapterOutputValidationResult:
    category = (
        "csi-source-adapter-output-privacy-boundary"
        if privacy_violation_count
        else "csi-source-adapter-output-invalid"
    )
    return CsiSourceAdapterOutputValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_output=rejected_csi_source_adapter_output(category),
    )


def _sanitize_csi_source_adapter_output(
    output: Mapping[str, object],
) -> dict[str, object]:
    ruview = output.get("ruview_reference")
    booth = output.get("booth_planning_profile")
    return {
        "status": "accepted",
        "ruview_reference": _sanitize_ruview_reference(ruview),
        "booth_planning_profile": _sanitize_booth_profile(booth),
        "metadata_only": True,
        "reference_only": True,
        "offline": True,
        "fixture_backed": True,
        **{field: False for field in CSI_SOURCE_ADAPTER_REQUIRED_FALSE_FLAGS},
    }


def _sanitize_ruview_reference(value: object) -> dict[str, object]:
    payload = dict(value) if isinstance(value, Mapping) else {}
    reassessment = payload.get("v2_reassessment")
    if not isinstance(reassessment, Mapping):
        reassessment = {}
    return {
        "repo": "ruvnet/RuView",
        "status": CSI_RUVIEW_REFERENCE_STATUS,
        "reference_only": True,
        "reassessable": bool(payload.get("reassessable", True)),
        "runtime_dependency": False,
        "local_source_staged": False,
        "source_vendored": False,
        "source_copied": False,
        "source_imported": False,
        "source_executed": False,
        "v2_reassessment": {
            "rust_workspace_reported": bool(reassessment.get("rust_workspace_reported", True)),
            "wifi_densepose_crates_reported": bool(
                reassessment.get("wifi_densepose_crates_reported", True)
            ),
            "signal_pipeline_crates_reported": bool(
                reassessment.get("signal_pipeline_crates_reported", True)
            ),
            "temporal_embedding_metric_reported": bool(
                reassessment.get("temporal_embedding_metric_reported", True)
            ),
            "downstream_accuracy_validated": False,
            "deployment_claims_verified": False,
        },
        "warning_history": list(CSI_RUVIEW_WARNING_HISTORY),
        "somatic_posture": "track-only-do-not-run-or-depend",
    }


def _sanitize_booth_profile(value: object) -> dict[str, object]:
    return {
        "profile": CSI_BOOTH_PROFILE_LABEL,
        "status": "future-planning-metadata-only",
        "single_subject": True,
        "space": "small-controlled-booth",
        "future_topology": "fixed-ap-plus-4-to-6-receiver-nodes",
        "preferred_radio_family": "esp32-s3",
        "empty_booth_baseline": "planned-reference-concept",
        "room_adaptation_logic": "skipped",
        "research_note_labels": list(CSI_BOOTH_REQUIRED_RESEARCH_NOTES),
        "reference_only": True,
        "metadata_only": True,
        "hardware_access": False,
        "packet_capture": False,
        "model_execution": False,
        "vitals_inference": False,
    }


def _ruview_reference_contract_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("csi_source_adapter_ruview_missing",)
    errors: list[str] = []
    if value.get("repo") != "ruvnet/RuView":
        errors.append("csi_source_adapter_ruview_repo_not_reference")
    if _status_label(value.get("status"), "") != CSI_RUVIEW_REFERENCE_STATUS:
        errors.append("csi_source_adapter_ruview_status_not_reference_only")
    if value.get("reference_only") is not True:
        errors.append("csi_source_adapter_ruview_reference_only_missing")
    if value.get("reassessable") is not True:
        errors.append("csi_source_adapter_ruview_reassessable_missing")
    if value.get("somatic_posture") != "track-only-do-not-run-or-depend":
        errors.append("csi_source_adapter_ruview_posture_not_pinned")
    for field in CSI_RUVIEW_REQUIRED_FALSE_FIELDS:
        if value.get(field) is not False:
            errors.append("csi_source_adapter_ruview_closed_flag_not_preserved")
            break

    reassessment = value.get("v2_reassessment")
    if not isinstance(reassessment, Mapping):
        errors.append("csi_source_adapter_ruview_reassessment_missing")
    else:
        for field in (
            "rust_workspace_reported",
            "wifi_densepose_crates_reported",
            "signal_pipeline_crates_reported",
            "temporal_embedding_metric_reported",
        ):
            if reassessment.get(field) is not True:
                errors.append("csi_source_adapter_ruview_reassessment_not_reference")
                break
        for field in ("downstream_accuracy_validated", "deployment_claims_verified"):
            if reassessment.get(field) is not False:
                errors.append("csi_source_adapter_ruview_accuracy_claim_not_closed")
                break

    history = value.get("warning_history")
    if not isinstance(history, list) or set(history) != set(CSI_RUVIEW_WARNING_HISTORY):
        errors.append("csi_source_adapter_ruview_warning_history_not_preserved")
    return tuple(errors)


def _booth_profile_contract_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("csi_source_adapter_booth_profile_missing",)
    errors: list[str] = []
    expected_fields = {
        "profile": CSI_BOOTH_PROFILE_LABEL,
        "status": "future-planning-metadata-only",
        "space": "small-controlled-booth",
        "future_topology": "fixed-ap-plus-4-to-6-receiver-nodes",
        "preferred_radio_family": "esp32-s3",
        "empty_booth_baseline": "planned-reference-concept",
        "room_adaptation_logic": "skipped",
    }
    for field, expected in expected_fields.items():
        if value.get(field) != expected:
            errors.append("csi_source_adapter_booth_profile_not_pinned")
            break
    for field in ("single_subject", "reference_only", "metadata_only"):
        if value.get(field) is not True:
            errors.append("csi_source_adapter_booth_true_flag_missing")
            break
    for field in ("hardware_access", "packet_capture", "model_execution", "vitals_inference"):
        if value.get(field) is not False:
            errors.append("csi_source_adapter_booth_closed_flag_not_preserved")
            break
    notes = value.get("research_note_labels")
    if not isinstance(notes, list) or set(notes) != set(CSI_BOOTH_REQUIRED_RESEARCH_NOTES):
        errors.append("csi_source_adapter_booth_research_notes_not_pinned")
    return tuple(errors)


def _status_label(value: object, default: str) -> str:
    text = str(value or default).strip().lower().replace("_", "-")
    if not text:
        return default
    safe = []
    for char in text:
        if char.isalnum() or char == "-":
            safe.append(char)
        elif char in (" ", "/", "."):
            safe.append("-")
    compact = "-".join(part for part in "".join(safe).split("-") if part)
    return compact or default


def _adapter_privacy_violation_count(value: object) -> int:
    if isinstance(value, Mapping):
        violations = 0
        for key, item in value.items():
            if _unsafe_adapter_key(key):
                violations += 1
            violations += _adapter_privacy_violation_count(item)
        return violations
    if isinstance(value, list):
        return sum(_adapter_privacy_violation_count(item) for item in value)
    if isinstance(value, str):
        return _adapter_string_privacy_violation_count(value)
    return 0


def _unsafe_adapter_key(key: object) -> bool:
    text = str(key or "").lower()
    if text in CSI_SOURCE_ADAPTER_ALLOWED_OUTPUT_FIELDS:
        return False
    if text in CSI_SOURCE_ADAPTER_FORBIDDEN_KEYS:
        return True
    return any(fragment in text for fragment in CSI_SOURCE_ADAPTER_FORBIDDEN_KEY_FRAGMENTS)


def _adapter_string_privacy_violation_count(value: str) -> int:
    from somatic.evidence.framework import (
        evidence_pack_string_privacy_violation_count,
    )

    lowered = value.lower().replace("\\", "/")
    return evidence_pack_string_privacy_violation_count(
        lowered,
        forbidden_value_fragments=CSI_SOURCE_ADAPTER_FORBIDDEN_VALUE_FRAGMENTS,
    )


def _safe_adapter_category(category: str) -> str:
    from somatic.evidence.framework import safe_evidence_category

    return safe_evidence_category(category)


__all__ = [
    "CSI_BOOTH_PROFILE_LABEL",
    "CSI_FIXTURE_SOURCE_ADAPTER_LABEL",
    "CSI_RUVIEW_DEPENDENCY_STATUS",
    "CSI_RUVIEW_REFERENCE_STATUS",
    "CSI_SOURCE_ADAPTER_CAPABILITY_LABELS",
    "CSI_SOURCE_ADAPTER_CONTRACT_VERSION",
    "CSI_SOURCE_ADAPTER_KIND",
    "CSI_SOURCE_ADAPTER_MANIFEST_LABELS",
    "CsiSourceAdapterOutputValidationResult",
    "booth_first_csi_planning_profile",
    "fixture_csi_source_adapter_output",
    "rejected_csi_source_adapter_output",
    "ruview_reference_metadata",
    "sanitize_csi_source_adapter_output",
    "validate_csi_source_adapter_output",
    "wifi_csi_source_adapter_status",
    "wifi_csi_real_mode_readiness_gate",
]
