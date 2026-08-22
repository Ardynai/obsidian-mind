"""Sanitized document-fixture evidence-pack contract.

Phase 10A non-sensor evidence domain using the same sanitized artifact-ref
pattern as sensor-evidence packs.  Emits deterministic count/status metadata
only — no raw document bodies, private refs, absolute paths, URLs,
credentials, source IDs, or health/medical claims.
"""

from collections.abc import Mapping

from somatic.evidence.document_adapter import (
    DocumentAdapterOutputValidationResult,
    document_fixture_adapter_status,
    validate_document_adapter_output,
)
from somatic.evidence.framework import (
    SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS,
    SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
    SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
    SENSOR_EVIDENCE_FORBIDDEN_KEYS,
    SENSOR_EVIDENCE_READINESS_VOCABULARY,
    SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS,
    SENSOR_EVIDENCE_SCHEMA_VERSION,
    SENSOR_EVIDENCE_STATUS_VOCABULARY,
    SensorEvidenceCompatibilityResult,
    SensorEvidenceContract,
    SensorEvidenceContractIdentity,
    build_evidence_pack_artifact_ref,
    classify_evidence_pack_contract,
    compute_evidence_pack_fingerprint,
    evidence_forbidden_fragments,
    evidence_readiness_status,
    evidence_score_int,
    evidence_status,
    evidence_status_count_dict,
    finalize_evidence_pack_identity,
    safe_evidence_artifact_hashes,
    safe_evidence_artifact_refs,
    safe_evidence_category,
    safe_evidence_int,
)
from somatic.safety.adapter_readiness import (
    REAL_MODE_PHASE_RUNTIME,
    real_mode_readiness_gate_summary,
)
from somatic.safety.phase11_contracts import (
    PHASE11_AUDIT_HANDOFF_REJECTED_STATUS,
    PHASE11_AUDIT_HANDOFF_STATUS,
    PHASE11_AUDIT_INDEX_REJECTED_STATUS,
    PHASE11_AUDIT_INDEX_STATUS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS,
    PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS,
    PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
    PHASE11_LIFECYCLE_DECISION_BLOCKED,
    PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
    PHASE11_LIFECYCLE_DECISION_REJECTED,
    PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
    PHASE11_LIFECYCLE_STAGE_ARCHIVED,
    PHASE11_LIFECYCLE_STAGE_CREATED,
    PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
    PHASE11_LIFECYCLE_STAGE_REJECTED,
    PHASE11_LIFECYCLE_STAGE_REVIEWED,
    PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
    PHASE11_PREFLIGHT_STATUS_MISSING,
    PHASE11_PREFLIGHT_STATUS_REJECTED,
    PHASE11_PREFLIGHT_STATUS_REVIEWED,
    PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
    PHASE11_REVIEW_RECORD_STATUS_REJECTED,
    PHASE11_REVIEW_RECORD_STATUS_REVIEWED,
    PHASE11_SIGNOFF_VERDICT_BLOCKERS,
    PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
    PHASE11_SIGNOFF_VERDICT_REJECTED,
    PHASE11_SIGNOFF_VERDICT_SUPERSEDED,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
)

DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION = 1
DOCUMENT_EVIDENCE_PACK_EXPORTER_ID = "somatic-document-evidence-pack-exporter-v1"
DOCUMENT_EVIDENCE_PROVIDER_KIND = "document-fixture"
DOCUMENT_EVIDENCE_KIND = "document-evidence-pack"
DOCUMENT_EVIDENCE_PACK_ARTIFACT_NAME = "document_evidence_pack"
DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF = "artifacts/document_evidence_pack.json"
DOCUMENT_EVIDENCE_PACK_STATUS_VOCABULARY = SENSOR_EVIDENCE_STATUS_VOCABULARY
DOCUMENT_EVIDENCE_PACK_READINESS_VOCABULARY = SENSOR_EVIDENCE_READINESS_VOCABULARY
DOCUMENT_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS = SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS
DOCUMENT_EVIDENCE_PACK_VERSION_FIELDS = {
    "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
    "contract_version": DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
    "evidence_contract_version": DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
}
DOCUMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS = (
    "metadata_only",
    "portable_json",
    "deterministic",
    "bounded",
    "explainable",
    "non_diagnostic",
    "fabric_pack_reference_safe",
    "mock",
    "research_only",
    "fixture_only",
    "offline",
    "local_only",
    "summary_output_only",
    "sandbox_only",
    "simulated",
    "fake_backed",
    "no_effectiveness_claim",
)
DOCUMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS = SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS
DOCUMENT_EVIDENCE_PACK_FORBIDDEN_VALUE_FRAGMENTS = evidence_forbidden_fragments(
    "document-parsed",
    "document-mixed",
    "fixtures/",
    "fixture://",
    "raw document text",
    "raw_document_text",
)
DOCUMENT_EVIDENCE_PACK_FORBIDDEN_KEYS = frozenset(
    set(SENSOR_EVIDENCE_FORBIDDEN_KEYS)
    | {
        "absolute_path",
        "absolute_paths",
        "document_body",
        "document_bodies",
        "document_text",
        "parser_body",
        "provider_body",
        "raw_document_text",
        "source_identifier",
        "source_identifiers",
        "url",
        "urls",
    }
)
DOCUMENT_EVIDENCE_PHASE11_REVIEW_DOMAINS = frozenset(
    {
        PHASE11_DOCUMENT_DOMAIN,
        PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    }
)
DOCUMENT_EVIDENCE_PHASE11_REVIEW_STATUSES = frozenset(
    {
        PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
        PHASE11_REVIEW_RECORD_STATUS_REVIEWED,
        PHASE11_REVIEW_RECORD_STATUS_REJECTED,
    }
)
DOCUMENT_EVIDENCE_PHASE11_PREFLIGHT_STATUSES = frozenset(
    {
        PHASE11_PREFLIGHT_STATUS_MISSING,
        PHASE11_PREFLIGHT_STATUS_REVIEWED,
        PHASE11_PREFLIGHT_STATUS_REJECTED,
    }
)
DOCUMENT_EVIDENCE_PHASE11_LIFECYCLE_STAGES = frozenset(
    {
        PHASE11_LIFECYCLE_STAGE_CREATED,
        PHASE11_LIFECYCLE_STAGE_REVIEWED,
        PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
        PHASE11_LIFECYCLE_STAGE_REJECTED,
        PHASE11_LIFECYCLE_STAGE_ARCHIVED,
        PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
    }
)
DOCUMENT_EVIDENCE_PHASE11_LIFECYCLE_DECISIONS = frozenset(
    {
        PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
        PHASE11_LIFECYCLE_DECISION_BLOCKED,
        PHASE11_LIFECYCLE_DECISION_REJECTED,
        PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
        PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
    }
)
DOCUMENT_EVIDENCE_PHASE11_SIGNOFF_VERDICTS = frozenset(
    {
        PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
        PHASE11_SIGNOFF_VERDICT_BLOCKERS,
        PHASE11_SIGNOFF_VERDICT_REJECTED,
        PHASE11_SIGNOFF_VERDICT_SUPERSEDED,
    }
)
DOCUMENT_EVIDENCE_PHASE11_AUDIT_INDEX_STATUSES = frozenset(
    {
        PHASE11_AUDIT_INDEX_STATUS,
        PHASE11_AUDIT_INDEX_REJECTED_STATUS,
    }
)
DOCUMENT_EVIDENCE_PHASE11_AUDIT_HANDOFF_STATUSES = frozenset(
    {
        PHASE11_AUDIT_HANDOFF_STATUS,
        PHASE11_AUDIT_HANDOFF_REJECTED_STATUS,
    }
)
DOCUMENT_EVIDENCE_PHASE11_HANDOFF_ACCEPTANCE_STATUSES = frozenset(
    {
        PHASE11_HANDOFF_ACCEPTANCE_ACCEPTED_STATUS,
        PHASE11_HANDOFF_ACCEPTANCE_BLOCKED_STATUS,
        PHASE11_HANDOFF_ACCEPTANCE_STALE_STATUS,
        PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS,
    }
)
DOCUMENT_EVIDENCE_PACK_REQUIRED_FIELDS = (
    "schema_version",
    "contract_version",
    "evidence_contract_version",
    "id",
    "pack_id",
    "pack_fingerprint",
    "fingerprint_algorithm",
    "fingerprint_scope",
    "exporter_id",
    "provider_kind",
    "evidence_kind",
    "mode",
    "status",
    "readiness_status",
    "metadata_only",
    "portable_json",
    "deterministic",
    "bounded",
    "explainable",
    "non_diagnostic",
    "generated_from",
    "adapter_status",
    "adapter_output_validation",
    "artifact_refs",
    "artifact_hashes",
    "counts",
    "scores",
    "status_counts",
    "diagnostic_counts",
    "core_tournament_scores_modified",
    "tournament_rankings_modified",
    "ranking_input",
    "fabric_pack_reference_safe",
    "fixture_only",
    "offline",
    "local_only",
    "summary_output_only",
    "hardware_access",
    "network_calls",
    "live_capture",
)
DOCUMENT_EVIDENCE_PACK_REQUIRED_OBJECT_FIELDS = (
    "generated_from",
    "adapter_status",
    "adapter_output_validation",
    "artifact_refs",
    "artifact_hashes",
    "counts",
    "scores",
    "status_counts",
    "diagnostic_counts",
)
DOCUMENT_EVIDENCE_PACK_GENERATED_FROM = {
    "provider_id": "somatic-document-fixture-provider-v1",
    "provider_contract_version": 1,
}
DOCUMENT_EVIDENCE_PACK_COUNT_CATEGORIES = (
    "fixture_count",
    "document_count",
    "parsed_document_count",
    "partial_document_count",
    "rejected_document_count",
    "total_word_count",
    "total_line_count",
    "total_char_count",
    "format_count",
)
DOCUMENT_EVIDENCE_PACK_KNOWN_TOP_LEVEL_FIELDS = frozenset(
    set(DOCUMENT_EVIDENCE_PACK_REQUIRED_FIELDS)
    | set(DOCUMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS)
    | set(DOCUMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS)
    | {
        "adapter_output_validation",
        "adapter_status",
        "candidate_type",
        "pack_class_recommendation",
        "privacy_boundary",
        "non_goals",
        "score_scale",
        "evidence_domain",
    }
)
DOCUMENT_EVIDENCE_PACK_CONTRACT = SensorEvidenceContract(
    identity=SensorEvidenceContractIdentity(
        provider_kind=DOCUMENT_EVIDENCE_PROVIDER_KIND,
        evidence_kind=DOCUMENT_EVIDENCE_KIND,
        contract_version=DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        exporter_id=DOCUMENT_EVIDENCE_PACK_EXPORTER_ID,
    ),
    version_fields=DOCUMENT_EVIDENCE_PACK_VERSION_FIELDS,
    required_fields=DOCUMENT_EVIDENCE_PACK_REQUIRED_FIELDS,
    required_object_fields=DOCUMENT_EVIDENCE_PACK_REQUIRED_OBJECT_FIELDS,
    expected_identity_fields={
        "id": "document-sanitized-evidence-pack",
        "exporter_id": DOCUMENT_EVIDENCE_PACK_EXPORTER_ID,
        "provider_kind": DOCUMENT_EVIDENCE_PROVIDER_KIND,
        "evidence_kind": DOCUMENT_EVIDENCE_KIND,
        "mode": "fixture-document-count-status-evidence-pack",
    },
    expected_generated_from=DOCUMENT_EVIDENCE_PACK_GENERATED_FROM,
    required_true_flags=DOCUMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS,
    required_false_flags=DOCUMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS,
    known_top_level_fields=DOCUMENT_EVIDENCE_PACK_KNOWN_TOP_LEVEL_FIELDS,
    forbidden_keys=DOCUMENT_EVIDENCE_PACK_FORBIDDEN_KEYS,
    forbidden_value_fragments=DOCUMENT_EVIDENCE_PACK_FORBIDDEN_VALUE_FRAGMENTS,
    count_fields=DOCUMENT_EVIDENCE_PACK_COUNT_CATEGORIES,
    pack_id_prefix="document-evidence-pack-",
)


def build_document_evidence_pack(
    *,
    fixture_evaluation: dict[str, object] | None = None,
    artifact_hashes: dict[str, object] | None = None,
    artifact_refs: dict[str, object] | None = None,
    adapter_output_validation: DocumentAdapterOutputValidationResult | None = None,
) -> dict[str, object]:
    """Build deterministic portable document count/status metadata only."""
    adapter_validation = (
        adapter_output_validation
        if adapter_output_validation is not None
        else validate_document_adapter_output(fixture_evaluation or {})
    )
    evaluation = dict(adapter_validation.sanitized_output)
    adapter_status = document_fixture_adapter_status()
    counts = _counts(evaluation)
    scores = _scores(evaluation, counts)
    status = evidence_status(
        evaluation.get("status"),
        status_vocabulary=DOCUMENT_EVIDENCE_PACK_STATUS_VOCABULARY,
    )
    readiness_status = evidence_readiness_status(
        status,
        evidence_quality=scores.get("evidence_quality"),
        status_vocabulary=DOCUMENT_EVIDENCE_PACK_STATUS_VOCABULARY,
    )
    payload: dict[str, object] = {
        "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
        "contract_version": DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        "evidence_contract_version": DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        "id": "document-sanitized-evidence-pack",
        "pack_id": None,
        "pack_fingerprint": None,
        "fingerprint_algorithm": SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
        "fingerprint_scope": SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
        "exporter_id": DOCUMENT_EVIDENCE_PACK_EXPORTER_ID,
        "provider_kind": DOCUMENT_EVIDENCE_PROVIDER_KIND,
        "evidence_kind": DOCUMENT_EVIDENCE_KIND,
        "evidence_domain": "document",
        "mode": "fixture-document-count-status-evidence-pack",
        "status": status,
        "readiness_status": readiness_status,
        "metadata_only": True,
        "portable_json": True,
        "deterministic": True,
        "bounded": True,
        "explainable": True,
        "non_diagnostic": True,
        "generated_from": dict(DOCUMENT_EVIDENCE_PACK_GENERATED_FROM),
        "adapter_status": adapter_status,
        "adapter_output_validation": adapter_validation.to_dict(),
        "artifact_refs": _safe_artifact_refs(artifact_refs),
        "artifact_hashes": _safe_hashes(artifact_hashes),
        "counts": counts,
        "scores": scores,
        "status_counts": _status_counts(evaluation),
        "diagnostic_counts": _diagnostic_counts(evaluation),
        "core_tournament_scores_modified": False,
        "tournament_rankings_modified": False,
        "ranking_input": False,
        "fabric_pack_reference_safe": True,
        "pack_class_recommendation": "data",
        "candidate_type": "dataset",
        "score_scale": "0-100",
        "privacy_boundary": ("sanitized document count/status metadata only"),
        "non_goals": [
            "no live capture",
            "no hardware access",
            "no network calls",
            "no document body export",
            "no document adapter ingestion",
            "no ranking input",
        ],
    }
    for flag in DOCUMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS:
        payload[flag] = True
    for flag in DOCUMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS:
        payload[flag] = False
    return finalize_evidence_pack_identity(
        payload,
        pack_id_prefix="document-evidence-pack-",
    )


def document_evidence_pack_artifact_metadata(
    evidence_pack: dict[str, object],
    *,
    artifact_ref: str = DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF,
    artifact_sha256: str | None = None,
) -> dict[str, object]:
    """Return a compact sanitized reference to a document evidence pack."""
    generic_ref = build_evidence_pack_artifact_ref(
        DOCUMENT_EVIDENCE_PACK_ARTIFACT_NAME,
        artifact_ref,
        artifact_sha256=artifact_sha256,
        evidence_pack=evidence_pack,
        provider_kind=DOCUMENT_EVIDENCE_PROVIDER_KIND,
        evidence_kind=DOCUMENT_EVIDENCE_KIND,
        require_hash=artifact_sha256 is not None,
    )
    metadata = {
        "schema_version": generic_ref["schema_version"],
        "evidence_contract_version": DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        "provider_kind": generic_ref["provider_kind"],
        "evidence_kind": generic_ref["evidence_kind"],
        "pack_id": generic_ref["pack_id"],
        "pack_fingerprint": generic_ref["pack_fingerprint"],
        "artifact_ref": generic_ref["artifact_ref"],
        "artifact_sha256": generic_ref["artifact_sha256"],
        "status": generic_ref["status"],
        "readiness_status": generic_ref["readiness_status"],
        "metadata_only": generic_ref["metadata_only"],
        "fixture_only": generic_ref["fixture_only"],
        "summary_output_only": generic_ref["summary_output_only"],
    }
    adapter_status = _safe_adapter_status_metadata(evidence_pack.get("adapter_status"))
    if adapter_status:
        metadata["adapter_status"] = adapter_status
    adapter_validation = _safe_adapter_validation_metadata(
        evidence_pack.get("adapter_output_validation")
    )
    if adapter_validation:
        metadata["adapter_output_validation"] = adapter_validation
    return metadata


def compute_document_evidence_pack_fingerprint(
    payload: Mapping[str, object],
) -> str:
    """Compute the v1 fingerprint over a persisted document evidence pack."""
    return compute_evidence_pack_fingerprint(payload)


def classify_document_evidence_pack_compatibility(
    payload: object,
    *,
    verify_fingerprint: bool = True,
) -> SensorEvidenceCompatibilityResult:
    """Classify a document evidence pack with fail-closed semantics."""
    return classify_evidence_pack_contract(
        payload,
        contract=DOCUMENT_EVIDENCE_PACK_CONTRACT,
        verify_fingerprint=verify_fingerprint,
    )


def validate_document_evidence_pack_v1(
    payload: object,
    *,
    verify_fingerprint: bool = True,
) -> SensorEvidenceCompatibilityResult:
    """Validate a persisted v1 document evidence pack."""
    return classify_document_evidence_pack_compatibility(
        payload,
        verify_fingerprint=verify_fingerprint,
    )


# -- internal helpers -------------------------------------------------------


def _counts(evaluation: dict[str, object]) -> dict[str, int]:
    status_counts = _status_counts(evaluation)
    return {
        "fixture_count": safe_evidence_int(evaluation.get("fixture_count")),
        "document_count": safe_evidence_int(evaluation.get("document_count")),
        "parsed_document_count": status_counts["parsed"],
        "partial_document_count": status_counts["partial"],
        "rejected_document_count": status_counts["rejected"],
        "total_word_count": safe_evidence_int(evaluation.get("total_word_count")),
        "total_line_count": safe_evidence_int(evaluation.get("total_line_count")),
        "total_char_count": safe_evidence_int(evaluation.get("total_char_count")),
        "format_count": safe_evidence_int(evaluation.get("format_count")),
    }


def _scores(
    evaluation: dict[str, object],
    counts: dict[str, int],
) -> dict[str, int]:
    quality = evidence_score_int(evaluation.get("evidence_quality"))
    if counts.get("document_count", 0) <= 0:
        quality = 0
    replay = evidence_score_int(evaluation.get("replay_integrity", quality))
    return {
        "score": quality,
        "evidence_quality": quality,
        "replay_integrity": replay,
        "aggregate_evidence_quality": quality,
        "aggregate_replay_integrity": replay,
    }


def _status_counts(evaluation: dict[str, object]) -> dict[str, int]:
    return evidence_status_count_dict(
        evaluation.get("status_counts"),
        status_vocabulary=DOCUMENT_EVIDENCE_PACK_STATUS_VOCABULARY,
    )


def _diagnostic_counts(evaluation: dict[str, object]) -> dict[str, object]:
    raw_categories = evaluation.get("parse_error_categories")
    categories: dict[str, int] = {}
    if isinstance(raw_categories, Mapping):
        for key, value in raw_categories.items():
            category = safe_evidence_category(key)
            categories[category] = categories.get(category, 0) + safe_evidence_int(value)
    categories = {key: value for key, value in sorted(categories.items()) if value}
    parse_error_count = sum(categories.values())
    return {
        "error_count": safe_evidence_int(evaluation.get("error_count"), parse_error_count),
        "parse_error_count": parse_error_count,
        "warning_count": safe_evidence_int(evaluation.get("warning_count")),
        "parse_error_categories": categories,
    }


def _safe_artifact_refs(
    value: dict[str, object] | None,
) -> dict[str, str]:
    return safe_evidence_artifact_refs(value)


def _safe_hashes(
    value: dict[str, object] | None,
) -> dict[str, str | None]:
    return safe_evidence_artifact_hashes(value)


def _safe_adapter_status_metadata(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        return {}
    labels = value.get("capability_labels")
    safe_labels = (
        [
            str(label)
            for label in labels
            if isinstance(label, str) and label and "://" not in label and "_" not in label
        ]
        if isinstance(labels, list)
        else []
    )
    metadata = {
        "adapter_contract_version": safe_evidence_int(value.get("adapter_contract_version")),
        "adapter_kind": str(value.get("adapter_kind") or ""),
        "status": str(value.get("status") or ""),
        "capability_labels": safe_labels,
        "metadata_only": bool(value.get("metadata_only")),
        "fixture_only": bool(value.get("fixture_only")),
        "offline": bool(value.get("offline")),
        "fail_closed_output_validation": bool(value.get("fail_closed_output_validation")),
        "network_calls": bool(value.get("network_calls")),
        "document_bodies_exported": bool(value.get("document_bodies_exported")),
        "origin_ids_exported": bool(value.get("origin_ids_exported")),
        "absolute_paths_exported": bool(value.get("absolute_paths_exported")),
        "urls_exported": bool(value.get("urls_exported")),
    }
    gate = real_mode_readiness_gate_summary(value.get("real_mode_readiness_gate"))
    if gate:
        metadata["real_mode_readiness_gate"] = gate
        metadata["real_mode_readiness_status"] = gate["status"]
        metadata["real_mode_execution_permitted"] = False
    review_status = value.get("p11b_review_record_status")
    if isinstance(review_status, Mapping):
        metadata["p11b_review_record_status"] = {
            "schema_version": safe_evidence_int(review_status.get("schema_version")),
            "review_record_contract_version": safe_evidence_int(
                review_status.get("review_record_contract_version")
            ),
            "domain": _safe_phase11_review_domain(review_status.get("domain")),
            "review_record_status": _safe_phase11_review_status(
                review_status.get("review_record_status")
            ),
            "reviewed_gate_count": safe_evidence_int(review_status.get("reviewed_gate_count")),
            "missing_gate_count": safe_evidence_int(review_status.get("missing_gate_count")),
            "rejected_gate_count": safe_evidence_int(review_status.get("rejected_gate_count")),
            "planning_only": bool(review_status.get("planning_only")),
            "metadata_only": bool(review_status.get("metadata_only")),
            "sanitized": bool(review_status.get("sanitized")),
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
    preflight_status = value.get("p11c_preflight_status")
    if isinstance(preflight_status, Mapping):
        metadata["p11c_preflight_status"] = {
            "schema_version": safe_evidence_int(preflight_status.get("schema_version")),
            "preflight_packet_contract_version": safe_evidence_int(
                preflight_status.get("preflight_packet_contract_version")
            ),
            "domain": _safe_phase11_review_domain(preflight_status.get("domain")),
            "preflight_packet_label": _safe_phase11_public_label(
                preflight_status.get("preflight_packet_label")
            ),
            "preflight_packet_id": _safe_phase11_public_label(
                preflight_status.get("preflight_packet_id")
            ),
            "preflight_packet_fingerprint": _safe_phase11_sha256(
                preflight_status.get("preflight_packet_fingerprint")
            ),
            "preflight_status": _safe_phase11_preflight_status(
                preflight_status.get("preflight_status")
            ),
            "reviewed_gate_count": safe_evidence_int(preflight_status.get("reviewed_gate_count")),
            "missing_gate_count": safe_evidence_int(preflight_status.get("missing_gate_count")),
            "rejected_gate_count": safe_evidence_int(preflight_status.get("rejected_gate_count")),
            "blocking_reason_count": safe_evidence_int(
                preflight_status.get("blocking_reason_count")
            ),
            "planning_only": bool(preflight_status.get("planning_only")),
            "metadata_only": bool(preflight_status.get("metadata_only")),
            "sanitized": bool(preflight_status.get("sanitized")),
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
    lifecycle_status = value.get("p11d_lifecycle_audit_status")
    if isinstance(lifecycle_status, Mapping):
        metadata["p11d_lifecycle_audit_status"] = {
            "schema_version": safe_evidence_int(lifecycle_status.get("schema_version")),
            "lifecycle_contract_version": safe_evidence_int(
                lifecycle_status.get("lifecycle_contract_version")
            ),
            "domain": _safe_phase11_review_domain(lifecycle_status.get("domain")),
            "lifecycle_record_id": _safe_phase11d_public_label(
                lifecycle_status.get("lifecycle_record_id")
            ),
            "lifecycle_record_fingerprint": _safe_phase11_sha256(
                lifecycle_status.get("lifecycle_record_fingerprint")
            ),
            "lifecycle_stage": _safe_phase11_lifecycle_stage(
                lifecycle_status.get("lifecycle_stage")
            ),
            "lifecycle_status": _safe_phase11_lifecycle_status(
                lifecycle_status.get("lifecycle_status")
            ),
            "audit_decision": _safe_phase11_lifecycle_decision(
                lifecycle_status.get("audit_decision")
            ),
            "signoff_verdict": _safe_phase11_signoff_verdict(
                lifecycle_status.get("signoff_verdict")
            ),
            "signoff_count": safe_evidence_int(lifecycle_status.get("signoff_count")),
            "decision_count": safe_evidence_int(lifecycle_status.get("decision_count")),
            "comparison_changed_field_count": safe_evidence_int(
                lifecycle_status.get("comparison_changed_field_count")
            ),
            "blocking_reason_count": safe_evidence_int(
                lifecycle_status.get("blocking_reason_count")
            ),
            "planning_only": bool(lifecycle_status.get("planning_only")),
            "metadata_only": bool(lifecycle_status.get("metadata_only")),
            "sanitized": bool(lifecycle_status.get("sanitized")),
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
    audit_index_status = value.get("p11e_audit_index_status")
    if isinstance(audit_index_status, Mapping):
        metadata["p11e_audit_index_status"] = {
            "schema_version": safe_evidence_int(audit_index_status.get("schema_version")),
            "audit_index_contract_version": safe_evidence_int(
                audit_index_status.get("audit_index_contract_version")
            ),
            "domain_scope": safe_evidence_category(audit_index_status.get("domain_scope")),
            "index_id": _safe_phase11e_public_label(audit_index_status.get("index_id")),
            "index_fingerprint": _safe_phase11_sha256(audit_index_status.get("index_fingerprint")),
            "status": _safe_phase11_audit_index_status(audit_index_status.get("status")),
            "entry_count": safe_evidence_int(audit_index_status.get("entry_count")),
            "created_count": safe_evidence_int(audit_index_status.get("created_count")),
            "reviewed_count": safe_evidence_int(audit_index_status.get("reviewed_count")),
            "superseded_count": safe_evidence_int(audit_index_status.get("superseded_count")),
            "rejected_count": safe_evidence_int(audit_index_status.get("rejected_count")),
            "archived_count": safe_evidence_int(audit_index_status.get("archived_count")),
            "decision_recorded_count": safe_evidence_int(
                audit_index_status.get("decision_recorded_count")
            ),
            "blocking_count": safe_evidence_int(audit_index_status.get("blocking_count")),
            "rejection_count": safe_evidence_int(audit_index_status.get("rejection_count")),
            "coverage_summary_count": safe_evidence_int(
                audit_index_status.get("coverage_summary_count")
            ),
            "supersession_chain_count": safe_evidence_int(
                audit_index_status.get("supersession_chain_count")
            ),
            "change_control_record_count": safe_evidence_int(
                audit_index_status.get("change_control_record_count")
            ),
            "export_retention_policy_count": safe_evidence_int(
                audit_index_status.get("export_retention_policy_count")
            ),
            "planning_only": bool(audit_index_status.get("planning_only")),
            "metadata_only": bool(audit_index_status.get("metadata_only")),
            "sanitized": bool(audit_index_status.get("sanitized")),
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
    audit_handoff_status = value.get("p11f_audit_handoff_status")
    if isinstance(audit_handoff_status, Mapping):
        metadata["p11f_audit_handoff_status"] = {
            "schema_version": safe_evidence_int(audit_handoff_status.get("schema_version")),
            "audit_handoff_contract_version": safe_evidence_int(
                audit_handoff_status.get("audit_handoff_contract_version")
            ),
            "domain": _safe_phase11_review_domain(audit_handoff_status.get("domain")),
            "handoff_id": _safe_phase11f_public_label(audit_handoff_status.get("handoff_id")),
            "handoff_fingerprint": _safe_phase11_sha256(
                audit_handoff_status.get("handoff_fingerprint")
            ),
            "status": _safe_phase11_audit_handoff_status(audit_handoff_status.get("status")),
            "audit_index_label": _safe_phase11e_public_label(
                audit_handoff_status.get("audit_index_label")
            ),
            "audit_index_fingerprint": _safe_phase11_sha256(
                audit_handoff_status.get("audit_index_fingerprint")
            ),
            "audit_index_entry_count": safe_evidence_int(
                audit_handoff_status.get("audit_index_entry_count")
            ),
            "created_count": safe_evidence_int(audit_handoff_status.get("created_count")),
            "reviewed_count": safe_evidence_int(audit_handoff_status.get("reviewed_count")),
            "superseded_count": safe_evidence_int(audit_handoff_status.get("superseded_count")),
            "rejected_count": safe_evidence_int(audit_handoff_status.get("rejected_count")),
            "archived_count": safe_evidence_int(audit_handoff_status.get("archived_count")),
            "decision_recorded_count": safe_evidence_int(
                audit_handoff_status.get("decision_recorded_count")
            ),
            "coverage_required_gate_count": safe_evidence_int(
                audit_handoff_status.get("coverage_required_gate_count")
            ),
            "coverage_covered_gate_count": safe_evidence_int(
                audit_handoff_status.get("coverage_covered_gate_count")
            ),
            "coverage_missing_gate_count": safe_evidence_int(
                audit_handoff_status.get("coverage_missing_gate_count")
            ),
            "blocking_count": safe_evidence_int(audit_handoff_status.get("blocking_count")),
            "rejection_count": safe_evidence_int(audit_handoff_status.get("rejection_count")),
            "unresolved_review_count": safe_evidence_int(
                audit_handoff_status.get("unresolved_review_count")
            ),
            "planning_only": bool(audit_handoff_status.get("planning_only")),
            "metadata_only": bool(audit_handoff_status.get("metadata_only")),
            "sanitized": bool(audit_handoff_status.get("sanitized")),
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
    handoff_acceptance_status = value.get("p11g_handoff_acceptance_status")
    if isinstance(handoff_acceptance_status, Mapping):
        metadata["p11g_handoff_acceptance_status"] = {
            "schema_version": safe_evidence_int(handoff_acceptance_status.get("schema_version")),
            "handoff_acceptance_contract_version": safe_evidence_int(
                handoff_acceptance_status.get("handoff_acceptance_contract_version")
            ),
            "domain": _safe_phase11_review_domain(handoff_acceptance_status.get("domain")),
            "acceptance_id": _safe_phase11g_public_label(
                handoff_acceptance_status.get("acceptance_id")
            ),
            "acceptance_fingerprint": _safe_phase11_sha256(
                handoff_acceptance_status.get("acceptance_fingerprint")
            ),
            "status": _safe_phase11_handoff_acceptance_status(
                handoff_acceptance_status.get("status")
            ),
            "source_handoff_label": _safe_phase11f_public_label(
                handoff_acceptance_status.get("source_handoff_label")
            ),
            "source_handoff_hash": _safe_phase11_sha256(
                handoff_acceptance_status.get("source_handoff_hash")
            ),
            "handoff_fingerprint": _safe_phase11_sha256(
                handoff_acceptance_status.get("handoff_fingerprint")
            ),
            "accepted_for_planning": bool(handoff_acceptance_status.get("accepted_for_planning")),
            "blocked": bool(handoff_acceptance_status.get("blocked")),
            "stale": bool(handoff_acceptance_status.get("stale")),
            "missing_review_count": safe_evidence_int(
                handoff_acceptance_status.get("missing_review_count")
            ),
            "unresolved_review_count": safe_evidence_int(
                handoff_acceptance_status.get("unresolved_review_count")
            ),
            "rejection_reason_count": safe_evidence_int(
                handoff_acceptance_status.get("rejection_reason_count")
            ),
            "blocking_reason_count": safe_evidence_int(
                handoff_acceptance_status.get("blocking_reason_count")
            ),
            "planning_only": bool(handoff_acceptance_status.get("planning_only")),
            "metadata_only": bool(handoff_acceptance_status.get("metadata_only")),
            "sanitized": bool(handoff_acceptance_status.get("sanitized")),
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
    return metadata


def _safe_phase11_review_domain(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_REVIEW_DOMAINS:
        return text
    return "unknown"


def _safe_phase11_review_status(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_REVIEW_STATUSES:
        return text
    return PHASE11_REVIEW_RECORD_STATUS_REJECTED


def _safe_phase11_preflight_status(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_PREFLIGHT_STATUSES:
        return text
    return PHASE11_PREFLIGHT_STATUS_REJECTED


def _safe_phase11_lifecycle_stage(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_LIFECYCLE_STAGES:
        return text
    return PHASE11_LIFECYCLE_STAGE_REJECTED


def _safe_phase11_lifecycle_status(value: object) -> str:
    text = str(value or "")
    stage = text.removesuffix("-runtime-disabled")
    if stage in DOCUMENT_EVIDENCE_PHASE11_LIFECYCLE_STAGES:
        return text
    return f"{PHASE11_LIFECYCLE_STAGE_REJECTED}-runtime-disabled"


def _safe_phase11_lifecycle_decision(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_LIFECYCLE_DECISIONS:
        return text
    return PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW


def _safe_phase11_signoff_verdict(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_SIGNOFF_VERDICTS:
        return text
    return PHASE11_SIGNOFF_VERDICT_BLOCKERS


def _safe_phase11_audit_index_status(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_AUDIT_INDEX_STATUSES:
        return text
    return PHASE11_AUDIT_INDEX_REJECTED_STATUS


def _safe_phase11_audit_handoff_status(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_AUDIT_HANDOFF_STATUSES:
        return text
    return PHASE11_AUDIT_HANDOFF_REJECTED_STATUS


def _safe_phase11_handoff_acceptance_status(value: object) -> str:
    text = str(value or "")
    if text in DOCUMENT_EVIDENCE_PHASE11_HANDOFF_ACCEPTANCE_STATUSES:
        return text
    return PHASE11_HANDOFF_ACCEPTANCE_REJECTED_STATUS


def _safe_phase11_public_label(value: object) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11c-"):
        return ""
    for fragment in (
        "private",
        "source",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label


def _safe_phase11e_public_label(value: object) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11e-"):
        return ""
    for fragment in (
        "private",
        "source",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label


def _safe_phase11d_public_label(value: object) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11d-"):
        return ""
    for fragment in (
        "private",
        "source",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label


def _safe_phase11f_public_label(value: object) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11f-"):
        return ""
    for fragment in (
        "private",
        "source",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label


def _safe_phase11g_public_label(value: object) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11g-"):
        return ""
    for fragment in (
        "private",
        "source-id",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label


def _safe_phase11_sha256(value: object) -> str:
    text = str(value or "")
    if len(text) == 64 and all(char in "0123456789abcdef" for char in text):
        return text
    return ""


def _safe_adapter_validation_metadata(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        return {}
    return {
        "classification": str(value.get("classification") or "malformed"),
        "compatible": bool(value.get("compatible")),
        "valid": bool(value.get("valid")),
        "error_count": safe_evidence_int(value.get("error_count")),
        "privacy_violation_count": safe_evidence_int(value.get("privacy_violation_count")),
        "status": str(value.get("status") or "rejected"),
        "readiness_status": str(value.get("readiness_status") or "rejected-fail-closed"),
        "sanitized": bool(value.get("sanitized")),
        "metadata_only": bool(value.get("metadata_only")),
        "fixture_only": bool(value.get("fixture_only")),
    }


__all__ = [
    "DOCUMENT_EVIDENCE_KIND",
    "DOCUMENT_EVIDENCE_PACK_ARTIFACT_NAME",
    "DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF",
    "DOCUMENT_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS",
    "DOCUMENT_EVIDENCE_PACK_CONTRACT",
    "DOCUMENT_EVIDENCE_PACK_CONTRACT_VERSION",
    "DOCUMENT_EVIDENCE_PACK_EXPORTER_ID",
    "DOCUMENT_EVIDENCE_PACK_FORBIDDEN_KEYS",
    "DOCUMENT_EVIDENCE_PROVIDER_KIND",
    "build_document_evidence_pack",
    "classify_document_evidence_pack_compatibility",
    "compute_document_evidence_pack_fingerprint",
    "document_evidence_pack_artifact_metadata",
    "validate_document_evidence_pack_v1",
]
