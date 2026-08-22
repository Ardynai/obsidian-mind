"""Sanitized CSI evidence-pack export contract."""

from collections.abc import Mapping
from dataclasses import dataclass

from .csi_batch import (
    CSI_BATCH_EVALUATION_CONTRACT_VERSION,
    CSI_BATCH_EVALUATOR_ID,
)
from .csi_formats import (
    CSI_PARSER_BOUNDARY_FALSE_FLAGS,
    CSI_PARSER_BOUNDARY_TRUE_FLAGS,
    CSI_PARSER_CONTRACT_VERSION,
    CSI_PARSER_ID,
)
from .csi_scoring import (
    CSI_EVIDENCE_SCORER_ID,
    CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
)
from .evidence import (
    SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS,
    SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
    SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
    SENSOR_EVIDENCE_FORBIDDEN_KEYS,
    SENSOR_EVIDENCE_READINESS_VOCABULARY,
    SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS,
    SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS,
    SENSOR_EVIDENCE_SCHEMA_VERSION,
    SENSOR_EVIDENCE_STATUS_VOCABULARY,
    SensorEvidenceCompatibilityResult,
    SensorEvidenceContract,
    SensorEvidenceContractIdentity,
)
from .evidence import (
    build_sensor_evidence_artifact_ref as build_evidence_pack_artifact_ref,
)
from .evidence import (
    classify_sensor_evidence_contract as classify_evidence_pack_contract,
)
from .evidence import (
    compute_sensor_evidence_fingerprint as compute_evidence_pack_fingerprint,
)
from .evidence import (
    finalize_sensor_evidence_pack_identity as finalize_evidence_pack_identity,
)
from .evidence import (
    safe_sensor_artifact_hashes as safe_evidence_artifact_hashes,
)
from .evidence import (
    safe_sensor_artifact_refs as safe_evidence_artifact_refs,
)
from .evidence import (
    safe_sensor_evidence_category as safe_evidence_category,
)
from .evidence import (
    sensor_evidence_forbidden_fragments as evidence_forbidden_fragments,
)
from .evidence import (
    sensor_evidence_int as safe_evidence_int,
)
from .evidence import (
    sensor_evidence_readiness_status as evidence_readiness_status,
)
from .evidence import (
    sensor_evidence_score_int as evidence_score_int,
)
from .evidence import (
    sensor_evidence_status as evidence_status,
)
from .evidence import (
    sensor_evidence_status_count_dict as evidence_status_count_dict,
)

CSI_EVIDENCE_PACK_CONTRACT_VERSION = 1
CSI_EVIDENCE_PACK_EXPORTER_ID = "somatic-csi-evidence-pack-exporter-v1"
CSI_EVIDENCE_PACK_STATUS_VOCABULARY = SENSOR_EVIDENCE_STATUS_VOCABULARY
CSI_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS = SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS
CSI_EVIDENCE_PACK_READINESS_VOCABULARY = SENSOR_EVIDENCE_READINESS_VOCABULARY
CSI_EVIDENCE_PACK_DEFAULT_ARTIFACT_REFS = {
    "parser_metadata": "artifacts/csi_parser_report.json",
    "parsed_metadata": "artifacts/csi_parsed_summary.json",
    "sensor_evidence_metadata": "artifacts/sensor_evidence_record.json",
}
CSI_EVIDENCE_PACK_VERSION_FIELDS = {
    "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
    "contract_version": CSI_EVIDENCE_PACK_CONTRACT_VERSION,
    "evidence_pack_contract_version": CSI_EVIDENCE_PACK_CONTRACT_VERSION,
    "parser_contract_version": CSI_PARSER_CONTRACT_VERSION,
    "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
    "batch_contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
}
CSI_EVIDENCE_PACK_REQUIRED_FIELDS = (
    "schema_version",
    "contract_version",
    "evidence_pack_contract_version",
    "id",
    "pack_id",
    "pack_fingerprint",
    "fingerprint_algorithm",
    "fingerprint_scope",
    "exporter_id",
    "mode",
    "status",
    "readiness_status",
    "metadata_only",
    "portable_json",
    "deterministic",
    "bounded",
    "explainable",
    "non_diagnostic",
    "parser_id",
    "parser_contract_version",
    "scorer_id",
    "scoring_contract_version",
    "batch_evaluator_id",
    "batch_contract_version",
    "generated_from",
    "artifact_refs",
    "artifact_hashes",
    "counts",
    "scores",
    "status_counts",
    "group_status_counts",
    "diagnostic_counts",
    "group_summaries",
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
    "raw_csi_data_collected",
    "raw_csi_data_exported",
    "raw_signal_values_exported",
)
CSI_EVIDENCE_PACK_REQUIRED_OBJECT_FIELDS = (
    "generated_from",
    "artifact_refs",
    "artifact_hashes",
    "counts",
    "scores",
    "status_counts",
    "group_status_counts",
    "diagnostic_counts",
)
CSI_EVIDENCE_PACK_REQUIRED_LIST_FIELDS = ("group_summaries",)
CSI_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS = SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS
CSI_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS = SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS
CSI_EVIDENCE_PACK_EXPECTED_IDENTITY_FIELDS = {
    "id": "csi-sanitized-evidence-pack",
    "exporter_id": CSI_EVIDENCE_PACK_EXPORTER_ID,
    "mode": "fixture-replay-evidence-pack",
    "parser_id": CSI_PARSER_ID,
    "scorer_id": CSI_EVIDENCE_SCORER_ID,
    "batch_evaluator_id": CSI_BATCH_EVALUATOR_ID,
}
CSI_EVIDENCE_PACK_EXPECTED_GENERATED_FROM = {
    "parser_id": CSI_PARSER_ID,
    "parser_contract_version": CSI_PARSER_CONTRACT_VERSION,
    "scorer_id": CSI_EVIDENCE_SCORER_ID,
    "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
    "batch_evaluator_id": CSI_BATCH_EVALUATOR_ID,
    "batch_contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
}
CSI_EVIDENCE_PACK_KNOWN_TOP_LEVEL_FIELDS = frozenset(
    set(CSI_EVIDENCE_PACK_REQUIRED_FIELDS)
    | set(CSI_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS)
    | set(CSI_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS)
    | {
        "artifact_hashes",
        "artifact_refs",
        "average_group_score",
        "baseline_data_exported",
        "candidate_type",
        "claim_effectiveness",
        "clinical_interpretation",
        "database_access",
        "diagnosis",
        "effectiveness_claim",
        "emergency_triage",
        "external_memory",
        "fake_backed",
        "generated_from",
        "group_status_counts",
        "live_sensor_access",
        "medical_advice",
        "medical_or_clinical_claim",
        "mock",
        "mode",
        "monitor_mode",
        "mqtt_udp_listener",
        "network_calls",
        "no_effectiveness_claim",
        "non_goals",
        "notification_automation",
        "packet_capture",
        "pack_class_recommendation",
        "parser_id",
        "personal_data_exported",
        "personal_health_data_exported",
        "prescription_generated",
        "privacy_boundary",
        "raw_sensor_data_collected",
        "readiness_status",
        "real_health_data_loaded",
        "real_intervention_performed",
        "real_monitoring",
        "real_profile_storage",
        "real_response_monitoring",
        "real_scheduling",
        "recommendation_generated",
        "reminder_automation",
        "research_only",
        "sandbox_only",
        "score_scale",
        "serial_access",
        "simulated",
        "status_counts",
        "treatment_recommendation",
        "wifi_network_probing",
    }
)
CSI_EVIDENCE_PACK_FORBIDDEN_KEYS = SENSOR_EVIDENCE_FORBIDDEN_KEYS
CSI_EVIDENCE_PACK_FORBIDDEN_VALUE_FRAGMENTS = evidence_forbidden_fragments(
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "invalid-utf8-csi",
)
CSI_EVIDENCE_PACK_COUNT_FIELDS = (
    "fixture_count",
    "group_count",
    "evaluated_group_count",
    "parsed_group_count",
    "partial_group_count",
    "rejected_group_count",
    "frame_count",
    "sample_count",
    "malformed_rows",
    "format_class_count",
)
CSI_EVIDENCE_PACK_STATUS_COUNT_FIELDS = (
    "status_counts",
    "group_status_counts",
)
CSI_EVIDENCE_PACK_SCORE_FIELDS = (
    "score",
    "evidence_quality",
    "replay_integrity",
    "aggregate_evidence_quality",
    "aggregate_replay_integrity",
    "minimum_group_score",
    "average_group_score",
)
CSI_EVIDENCE_PACK_CONTRACT = SensorEvidenceContract(
    identity=SensorEvidenceContractIdentity(
        provider_kind="wifi-csi",
        evidence_kind="csi-evidence-pack",
        contract_version=CSI_EVIDENCE_PACK_CONTRACT_VERSION,
        exporter_id=CSI_EVIDENCE_PACK_EXPORTER_ID,
    ),
    version_fields=CSI_EVIDENCE_PACK_VERSION_FIELDS,
    required_fields=CSI_EVIDENCE_PACK_REQUIRED_FIELDS,
    expected_identity_fields=CSI_EVIDENCE_PACK_EXPECTED_IDENTITY_FIELDS,
    expected_generated_from=CSI_EVIDENCE_PACK_EXPECTED_GENERATED_FROM,
    required_object_fields=CSI_EVIDENCE_PACK_REQUIRED_OBJECT_FIELDS,
    required_list_fields=CSI_EVIDENCE_PACK_REQUIRED_LIST_FIELDS,
    count_fields=CSI_EVIDENCE_PACK_COUNT_FIELDS,
    required_count_fields=CSI_EVIDENCE_PACK_COUNT_FIELDS,
    count_status_count_fields=CSI_EVIDENCE_PACK_STATUS_COUNT_FIELDS,
    score_fields=CSI_EVIDENCE_PACK_SCORE_FIELDS,
    required_score_fields=CSI_EVIDENCE_PACK_SCORE_FIELDS,
    required_true_flags=CSI_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS,
    required_false_flags=CSI_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS,
    status_vocabulary=CSI_EVIDENCE_PACK_STATUS_VOCABULARY,
    readiness_vocabulary=CSI_EVIDENCE_PACK_READINESS_VOCABULARY,
    status_count_fields=CSI_EVIDENCE_PACK_STATUS_COUNT_FIELDS,
    known_top_level_fields=CSI_EVIDENCE_PACK_KNOWN_TOP_LEVEL_FIELDS,
    forbidden_keys=CSI_EVIDENCE_PACK_FORBIDDEN_KEYS,
    forbidden_value_fragments=CSI_EVIDENCE_PACK_FORBIDDEN_VALUE_FRAGMENTS,
    pack_id_prefix="csi-evidence-pack-",
    evidence_contract_version_field="evidence_pack_contract_version",
)


@dataclass(frozen=True)
class CsiEvidencePackCompatibilityResult:
    """Sanitized compatibility decision for an already-exported CSI pack."""

    classification: str
    valid: bool
    compatible: bool
    contract_version: int | None
    evidence_pack_contract_version: int | None
    status: str
    readiness_status: str
    fingerprint_verified: bool
    error_count: int
    warning_count: int
    missing_required_field_count: int = 0
    unknown_field_count: int = 0
    privacy_violation_count: int = 0
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "valid": self.valid,
            "compatible": self.compatible,
            "contract_version": self.contract_version,
            "evidence_pack_contract_version": self.evidence_pack_contract_version,
            "status": self.status,
            "readiness_status": self.readiness_status,
            "fingerprint_verified": self.fingerprint_verified,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "missing_required_field_count": self.missing_required_field_count,
            "unknown_field_count": self.unknown_field_count,
            "privacy_violation_count": self.privacy_violation_count,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "metadata_only": True,
            "fixture_only": True,
            "raw_signal_values_exported": False,
            "readiness_status_if_rejected": "rejected-fail-closed",
        }


def build_csi_evidence_pack(
    *,
    parser_report_payload: dict[str, object] | None = None,
    parsed_summary_payload: dict[str, object] | None = None,
    scoring_payload: dict[str, object] | None = None,
    batch_payload: dict[str, object] | None = None,
    artifact_hashes: dict[str, object] | None = None,
    artifact_refs: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build deterministic portable CSI evidence metadata without raw CSI values."""
    parser_report_payload = _dict(parser_report_payload)
    parsed_summary_payload = _dict(parsed_summary_payload)
    scoring_payload = _dict(
        scoring_payload
        or parser_report_payload.get("csi_evidence_scoring")
        or parsed_summary_payload.get("csi_evidence_scoring")
    )
    batch_payload = _dict(batch_payload)
    artifact_hashes = _safe_hashes(artifact_hashes)
    artifact_refs = _safe_artifact_refs(artifact_refs)
    if not artifact_refs and parser_report_payload:
        artifact_refs = dict(CSI_EVIDENCE_PACK_DEFAULT_ARTIFACT_REFS)

    counts = _counts(
        parser_report_payload=parser_report_payload,
        parsed_summary_payload=parsed_summary_payload,
        scoring_payload=scoring_payload,
        batch_payload=batch_payload,
    )
    scores = _scores(scoring_payload=scoring_payload, batch_payload=batch_payload)
    status = _status(
        batch_payload.get("status")
        or scoring_payload.get("status")
        or parser_report_payload.get("status")
    )
    payload = {
        "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
        "contract_version": CSI_EVIDENCE_PACK_CONTRACT_VERSION,
        "evidence_pack_contract_version": CSI_EVIDENCE_PACK_CONTRACT_VERSION,
        "id": "csi-sanitized-evidence-pack",
        "pack_id": None,
        "pack_fingerprint": None,
        "fingerprint_algorithm": SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
        "fingerprint_scope": SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
        "exporter_id": CSI_EVIDENCE_PACK_EXPORTER_ID,
        "mode": "fixture-replay-evidence-pack",
        "status": status,
        "readiness_status": _readiness_status(status, scores),
        "metadata_only": True,
        "portable_json": True,
        "deterministic": True,
        "bounded": True,
        "explainable": True,
        "non_diagnostic": True,
        "parser_id": CSI_PARSER_ID,
        "parser_contract_version": CSI_PARSER_CONTRACT_VERSION,
        "scorer_id": CSI_EVIDENCE_SCORER_ID,
        "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
        "batch_evaluator_id": CSI_BATCH_EVALUATOR_ID,
        "batch_contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
        "generated_from": {
            "parser_id": CSI_PARSER_ID,
            "parser_contract_version": CSI_PARSER_CONTRACT_VERSION,
            "scorer_id": CSI_EVIDENCE_SCORER_ID,
            "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
            "batch_evaluator_id": CSI_BATCH_EVALUATOR_ID,
            "batch_contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
        },
        "artifact_refs": artifact_refs,
        "artifact_hashes": artifact_hashes,
        "counts": counts,
        "scores": scores,
        "status_counts": dict(counts["status_counts"]),
        "group_status_counts": dict(counts["group_status_counts"]),
        "diagnostic_counts": _diagnostic_counts(
            parser_report_payload=parser_report_payload,
            scoring_payload=scoring_payload,
            batch_payload=batch_payload,
        ),
        "group_summaries": _group_summaries(batch_payload),
        "core_tournament_scores_modified": False,
        "tournament_rankings_modified": False,
        "ranking_input": False,
        "fabric_pack_reference_safe": True,
        "pack_class_recommendation": "data",
        "candidate_type": "dataset",
        "score_scale": "0-100",
        "privacy_boundary": (
            "sanitized CSI parser, replay, scoring, and batch readiness metadata only"
        ),
        "non_goals": [
            "no live capture",
            "no hardware access",
            "no packet capture",
            "no signal processing output",
            "no vital-sign inference",
            "no medical or clinical claim",
        ],
        "raw_signal_values_exported": False,
        "sandbox_only": True,
        "simulated": True,
        "fake_backed": True,
        "live_sensor_access": False,
        "personal_data_exported": False,
        "personal_health_data_exported": False,
        "baseline_data_exported": False,
        "real_health_data_loaded": False,
        "real_profile_storage": False,
        "database_access": False,
        "raw_sensor_data_collected": False,
        "recommendation_generated": False,
        "prescription_generated": False,
        "medical_advice": False,
        "effectiveness_claim": False,
        "no_effectiveness_claim": True,
        "claim_effectiveness": False,
        "real_intervention_performed": False,
        "real_response_monitoring": False,
        "real_scheduling": False,
        "notification_automation": False,
        "reminder_automation": False,
        "external_memory": False,
        "diagnosis": False,
        "treatment_recommendation": False,
        "emergency_triage": False,
        "real_monitoring": False,
    }
    payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return finalize_evidence_pack_identity(
        payload,
        pack_id_prefix="csi-evidence-pack-",
    )


def csi_evidence_pack_artifact_metadata(
    evidence_pack: dict[str, object],
    *,
    artifact_ref: str = "artifacts/csi_evidence_pack.json",
    artifact_sha256: str | None = None,
) -> dict[str, object]:
    """Return a compact sanitized reference to an evidence pack artifact."""
    generic_ref = build_evidence_pack_artifact_ref(
        "csi_evidence_pack",
        artifact_ref,
        artifact_sha256=artifact_sha256,
        evidence_pack=evidence_pack,
        provider_kind="wifi-csi",
        evidence_kind="csi-evidence-pack",
        require_hash=artifact_sha256 is not None,
    )
    return {
        "schema_version": generic_ref["schema_version"],
        "evidence_pack_contract_version": CSI_EVIDENCE_PACK_CONTRACT_VERSION,
        "pack_id": generic_ref["pack_id"],
        "pack_fingerprint": generic_ref["pack_fingerprint"],
        "artifact_ref": generic_ref["artifact_ref"],
        "artifact_sha256": generic_ref["artifact_sha256"],
        "status": generic_ref["status"],
        "readiness_status": generic_ref["readiness_status"],
        "metadata_only": generic_ref["metadata_only"],
        "fixture_only": generic_ref["fixture_only"],
        "summary_output_only": generic_ref["summary_output_only"],
        "raw_signal_values_exported": generic_ref["raw_signal_values_exported"],
    }


def compute_csi_evidence_pack_fingerprint(payload: Mapping[str, object]) -> str:
    """Compute the v1 fingerprint over a persisted CSI evidence pack payload."""
    return compute_evidence_pack_fingerprint(payload)


def classify_csi_evidence_pack_compatibility(
    payload: object,
    *,
    verify_fingerprint: bool = True,
) -> CsiEvidencePackCompatibilityResult:
    """Classify an exported CSI evidence pack without exposing private fields."""
    return _csi_compatibility_result(
        classify_evidence_pack_contract(
            payload,
            contract=CSI_EVIDENCE_PACK_CONTRACT,
            verify_fingerprint=verify_fingerprint,
        )
    )


def validate_csi_evidence_pack_v1(
    payload: object,
    *,
    verify_fingerprint: bool = True,
) -> CsiEvidencePackCompatibilityResult:
    """Validate a persisted v1 CSI evidence pack with fail-closed semantics."""
    return classify_csi_evidence_pack_compatibility(
        payload,
        verify_fingerprint=verify_fingerprint,
    )


def _csi_compatibility_result(
    result: SensorEvidenceCompatibilityResult,
) -> CsiEvidencePackCompatibilityResult:
    return CsiEvidencePackCompatibilityResult(
        classification=result.classification,
        valid=result.valid,
        compatible=result.compatible,
        contract_version=result.contract_version,
        evidence_pack_contract_version=result.evidence_contract_version,
        status=result.status,
        readiness_status=result.readiness_status,
        fingerprint_verified=result.fingerprint_verified,
        error_count=result.error_count,
        warning_count=result.warning_count,
        missing_required_field_count=result.missing_required_field_count,
        unknown_field_count=result.unknown_field_count,
        privacy_violation_count=result.privacy_violation_count,
        errors=result.errors,
        warnings=result.warnings,
    )


def _counts(
    *,
    parser_report_payload: dict[str, object],
    parsed_summary_payload: dict[str, object],
    scoring_payload: dict[str, object],
    batch_payload: dict[str, object],
) -> dict[str, object]:
    if batch_payload:
        status_counts = _status_count_dict(batch_payload.get("status_counts"))
        group_status_counts = _status_count_dict(batch_payload.get("group_status_counts"))
        return {
            "fixture_count": _int(batch_payload.get("fixture_count")),
            "group_count": _int(batch_payload.get("group_count")),
            "evaluated_group_count": _int(batch_payload.get("evaluated_group_count")),
            "parsed_group_count": _int(batch_payload.get("parsed_group_count")),
            "partial_group_count": _int(batch_payload.get("partial_group_count")),
            "rejected_group_count": _int(batch_payload.get("rejected_group_count")),
            "frame_count": _int(batch_payload.get("frame_count")),
            "sample_count": _int(batch_payload.get("sample_count")),
            "malformed_rows": _int(batch_payload.get("malformed_rows")),
            "status_counts": status_counts,
            "group_status_counts": group_status_counts,
            "format_class_count": len(_list(batch_payload.get("source_formats"))),
        }
    status_counts = _status_count_dict(
        scoring_payload.get("status_counts") or parser_report_payload.get("status_counts")
    )
    return {
        "fixture_count": _int(
            scoring_payload.get("fixture_count")
            or parser_report_payload.get("fixture_count")
            or parsed_summary_payload.get("fixture_count")
        ),
        "group_count": 0,
        "evaluated_group_count": 0,
        "parsed_group_count": 0,
        "partial_group_count": 0,
        "rejected_group_count": 0,
        "frame_count": _int(
            scoring_payload.get("frame_count")
            or parser_report_payload.get("frame_count")
            or parsed_summary_payload.get("frame_count")
        ),
        "sample_count": _int(
            scoring_payload.get("sample_count")
            or parser_report_payload.get("sample_count")
            or parsed_summary_payload.get("sample_count")
        ),
        "malformed_rows": _int(
            scoring_payload.get("malformed_rows")
            or parser_report_payload.get("malformed_rows")
            or parsed_summary_payload.get("malformed_rows")
        ),
        "status_counts": status_counts,
        "group_status_counts": _status_count_dict(None),
        "format_class_count": len(
            _list(
                parsed_summary_payload.get("source_formats")
                or parser_report_payload.get("source_formats")
                or scoring_payload.get("source_formats")
            )
        ),
    }


def _scores(
    *,
    scoring_payload: dict[str, object],
    batch_payload: dict[str, object],
) -> dict[str, object]:
    if batch_payload:
        score = _score_int(batch_payload.get("score"))
        evidence_quality = _score_int(
            batch_payload.get("aggregate_evidence_quality")
            or batch_payload.get("evidence_quality")
            or score
        )
        replay_integrity = _score_int(
            batch_payload.get("aggregate_replay_integrity")
            or batch_payload.get("replay_integrity")
            or score
        )
        return {
            "score": score,
            "evidence_quality": evidence_quality,
            "replay_integrity": replay_integrity,
            "aggregate_evidence_quality": evidence_quality,
            "aggregate_replay_integrity": replay_integrity,
            "minimum_group_score": _score_int(batch_payload.get("minimum_group_score")),
            "average_group_score": _float(batch_payload.get("average_group_score")),
        }
    score = _score_int(scoring_payload.get("score"))
    evidence_quality = _score_int(scoring_payload.get("evidence_quality") or score)
    replay_integrity = _score_int(scoring_payload.get("replay_integrity") or score)
    return {
        "score": score,
        "evidence_quality": evidence_quality,
        "replay_integrity": replay_integrity,
        "aggregate_evidence_quality": evidence_quality,
        "aggregate_replay_integrity": replay_integrity,
        "minimum_group_score": 0,
        "average_group_score": 0.0,
    }


def _diagnostic_counts(
    *,
    parser_report_payload: dict[str, object],
    scoring_payload: dict[str, object],
    batch_payload: dict[str, object],
) -> dict[str, object]:
    error_count = _int(
        batch_payload.get("error_count")
        if batch_payload
        else scoring_payload.get("error_count") or len(_list(parser_report_payload.get("errors")))
    )
    parse_error_count = _int(
        batch_payload.get("parse_error_count")
        if batch_payload
        else scoring_payload.get("parse_error_count")
        or len(_list(parser_report_payload.get("parse_errors")))
    )
    warning_count = _int(
        batch_payload.get("warning_count")
        if batch_payload
        else scoring_payload.get("warning_count")
        or len(_list(parser_report_payload.get("warnings")))
    )
    return {
        "error_count": error_count,
        "parse_error_count": parse_error_count,
        "warning_count": warning_count,
        "parse_error_categories": _parse_error_categories(parser_report_payload),
    }


def _group_summaries(batch_payload: dict[str, object]) -> list[dict[str, object]]:
    groups = []
    for group in _list(batch_payload.get("groups")):
        if not isinstance(group, dict):
            continue
        groups.append(
            {
                "group_id": str(group.get("group_id", "")),
                "status": _status(group.get("status")),
                "parser_status": _status(group.get("parser_status")),
                "fixture_count": _int(group.get("fixture_count")),
                "frame_count": _int(group.get("frame_count")),
                "sample_count": _int(group.get("sample_count")),
                "malformed_rows": _int(group.get("malformed_rows")),
                "error_count": _int(group.get("error_count")),
                "parse_error_count": _int(group.get("parse_error_count")),
                "warning_count": _int(group.get("warning_count")),
                "format_class_count": len(_list(group.get("source_formats"))),
                "score": _score_int(group.get("score")),
                "evidence_quality": _score_int(group.get("evidence_quality")),
                "replay_integrity": _score_int(group.get("replay_integrity")),
                "ref_limit_exceeded": bool(group.get("ref_limit_exceeded")),
            }
        )
    return groups


def _parse_error_categories(payload: dict[str, object]) -> dict[str, int]:
    categories = {}
    for item in _list(payload.get("parse_errors")):
        if not isinstance(item, dict):
            continue
        category = _safe_category(item.get("code"))
        categories[category] = categories.get(category, 0) + 1
    return dict(sorted(categories.items()))


def _safe_category(value: object) -> str:
    return safe_evidence_category(value)


def _safe_artifact_refs(value: dict[str, object] | None) -> dict[str, str]:
    return safe_evidence_artifact_refs(value)


def _safe_hashes(value: dict[str, object] | None) -> dict[str, str | None]:
    return safe_evidence_artifact_hashes(value)


def _readiness_status(status: str, scores: dict[str, object]) -> str:
    return evidence_readiness_status(
        status,
        evidence_quality=scores.get("evidence_quality"),
        status_vocabulary=CSI_EVIDENCE_PACK_STATUS_VOCABULARY,
    )


def _status(value: object) -> str:
    return evidence_status(
        value,
        status_vocabulary=CSI_EVIDENCE_PACK_STATUS_VOCABULARY,
    )


def _status_count_dict(value: object) -> dict[str, int]:
    return evidence_status_count_dict(
        value,
        status_vocabulary=CSI_EVIDENCE_PACK_STATUS_VOCABULARY,
    )


def _dict(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, dict) else {}


def _list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _int(value: object, default: int = 0) -> int:
    return safe_evidence_int(value, default=default)


def _float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _score_int(value: object) -> int:
    return evidence_score_int(value)


__all__ = [
    "CSI_EVIDENCE_PACK_CONTRACT_VERSION",
    "CSI_EVIDENCE_PACK_CONTRACT",
    "CSI_EVIDENCE_PACK_EXPORTER_ID",
    "CSI_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS",
    "CsiEvidencePackCompatibilityResult",
    "build_csi_evidence_pack",
    "classify_csi_evidence_pack_compatibility",
    "compute_csi_evidence_pack_fingerprint",
    "csi_evidence_pack_artifact_metadata",
    "validate_csi_evidence_pack_v1",
]
