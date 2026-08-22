"""Sanitized neutral environment fixture evidence-pack contract."""

from collections.abc import Mapping

from .evidence import (
    SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS,
    SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
    SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
    SENSOR_EVIDENCE_READINESS_VOCABULARY,
    SENSOR_EVIDENCE_SCHEMA_VERSION,
    SENSOR_EVIDENCE_STATUS_VOCABULARY,
    SensorEvidenceCompatibilityResult,
    SensorEvidenceContract,
    SensorEvidenceContractIdentity,
    build_sensor_evidence_artifact_ref,
    classify_sensor_evidence_contract,
    compute_sensor_evidence_fingerprint,
    sensor_evidence_payload_sha256,
    sensor_evidence_readiness_status,
    sensor_evidence_score_int,
    sensor_evidence_status,
)

ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION = 1
ENVIRONMENT_EVIDENCE_PACK_EXPORTER_ID = "somatic-environment-evidence-pack-exporter-v1"
ENVIRONMENT_EVIDENCE_PROVIDER_KIND = "environment-fixture"
ENVIRONMENT_EVIDENCE_KIND = "environment-tabular-evidence-pack"
ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_NAME = "environment_evidence_pack"
ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_REF = "artifacts/environment_evidence_pack.json"
ENVIRONMENT_EVIDENCE_PACK_STATUS_VOCABULARY = SENSOR_EVIDENCE_STATUS_VOCABULARY
ENVIRONMENT_EVIDENCE_PACK_READINESS_VOCABULARY = SENSOR_EVIDENCE_READINESS_VOCABULARY
ENVIRONMENT_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS = (
    SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS
)
ENVIRONMENT_EVIDENCE_PACK_VERSION_FIELDS = {
    "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
    "contract_version": ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
    "evidence_contract_version": ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
}
ENVIRONMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS = (
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
ENVIRONMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS = (
    "core_tournament_scores_modified",
    "tournament_rankings_modified",
    "ranking_input",
    "hardware_access",
    "network_calls",
    "serial_access",
    "mqtt_udp_listener",
    "packet_capture",
    "monitor_mode",
    "live_capture",
    "live_sensor_access",
    "raw_sensor_data_collected",
    "personal_data_exported",
    "database_access",
    "effectiveness_claim",
    "claim_effectiveness",
    "real_scheduling",
    "notification_automation",
    "reminder_automation",
    "external_memory",
)
ENVIRONMENT_EVIDENCE_PACK_REQUIRED_FIELDS = (
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
ENVIRONMENT_EVIDENCE_PACK_REQUIRED_OBJECT_FIELDS = (
    "generated_from",
    "artifact_refs",
    "artifact_hashes",
    "counts",
    "scores",
    "status_counts",
    "diagnostic_counts",
)
ENVIRONMENT_EVIDENCE_PACK_GENERATED_FROM = {
    "provider_id": "somatic-environment-fixture-provider-v1",
    "provider_contract_version": 1,
}
ENVIRONMENT_EVIDENCE_PACK_KNOWN_TOP_LEVEL_FIELDS = frozenset(
    set(ENVIRONMENT_EVIDENCE_PACK_REQUIRED_FIELDS)
    | set(ENVIRONMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS)
    | set(ENVIRONMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS)
    | {
        "candidate_type",
        "pack_class_recommendation",
        "privacy_boundary",
        "non_goals",
        "score_scale",
    }
)
ENVIRONMENT_EVIDENCE_PACK_CONTRACT = SensorEvidenceContract(
    identity=SensorEvidenceContractIdentity(
        provider_kind=ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
        evidence_kind=ENVIRONMENT_EVIDENCE_KIND,
        contract_version=ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        exporter_id=ENVIRONMENT_EVIDENCE_PACK_EXPORTER_ID,
    ),
    version_fields=ENVIRONMENT_EVIDENCE_PACK_VERSION_FIELDS,
    required_fields=ENVIRONMENT_EVIDENCE_PACK_REQUIRED_FIELDS,
    required_object_fields=ENVIRONMENT_EVIDENCE_PACK_REQUIRED_OBJECT_FIELDS,
    expected_identity_fields={
        "id": "environment-sanitized-evidence-pack",
        "exporter_id": ENVIRONMENT_EVIDENCE_PACK_EXPORTER_ID,
        "provider_kind": ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
        "evidence_kind": ENVIRONMENT_EVIDENCE_KIND,
        "mode": "fixture-tabular-evidence-pack",
    },
    expected_generated_from=ENVIRONMENT_EVIDENCE_PACK_GENERATED_FROM,
    required_true_flags=ENVIRONMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS,
    required_false_flags=ENVIRONMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS,
    known_top_level_fields=ENVIRONMENT_EVIDENCE_PACK_KNOWN_TOP_LEVEL_FIELDS,
    pack_id_prefix="environment-evidence-pack-",
)


def build_environment_evidence_pack(
    *,
    fixture_evaluation: dict[str, object] | None = None,
    artifact_hashes: dict[str, object] | None = None,
    artifact_refs: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build deterministic portable environment fixture metadata only."""
    evaluation = dict(fixture_evaluation or {})
    counts = _counts(evaluation)
    scores = _scores(evaluation, counts)
    status = _status(evaluation.get("status"))
    readiness_status = sensor_evidence_readiness_status(
        status,
        evidence_quality=scores.get("evidence_quality"),
        status_vocabulary=ENVIRONMENT_EVIDENCE_PACK_STATUS_VOCABULARY,
    )
    payload = {
        "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
        "contract_version": ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        "evidence_contract_version": ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
        "id": "environment-sanitized-evidence-pack",
        "pack_id": None,
        "pack_fingerprint": None,
        "fingerprint_algorithm": SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
        "fingerprint_scope": SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
        "exporter_id": ENVIRONMENT_EVIDENCE_PACK_EXPORTER_ID,
        "provider_kind": ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
        "evidence_kind": ENVIRONMENT_EVIDENCE_KIND,
        "mode": "fixture-tabular-evidence-pack",
        "status": status,
        "readiness_status": readiness_status,
        "metadata_only": True,
        "portable_json": True,
        "deterministic": True,
        "bounded": True,
        "explainable": True,
        "non_diagnostic": True,
        "generated_from": dict(ENVIRONMENT_EVIDENCE_PACK_GENERATED_FROM),
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
        "privacy_boundary": "sanitized environment row/count/status metadata only",
        "non_goals": [
            "no live capture",
            "no hardware access",
            "no network calls",
            "no row body export",
            "no ranking input",
        ],
    }
    for field in ENVIRONMENT_EVIDENCE_PACK_REQUIRED_TRUE_FLAGS:
        payload[field] = True
    for field in ENVIRONMENT_EVIDENCE_PACK_REQUIRED_FALSE_FLAGS:
        payload[field] = False
    fingerprint = sensor_evidence_payload_sha256(dict(payload, pack_id=None, pack_fingerprint=None))
    payload["pack_fingerprint"] = fingerprint
    payload["pack_id"] = f"environment-evidence-pack-{fingerprint[:16]}"
    return payload


def environment_evidence_pack_artifact_metadata(
    evidence_pack: dict[str, object],
    *,
    artifact_ref: str = ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_REF,
    artifact_sha256: str | None = None,
) -> dict[str, object]:
    """Return a compact sanitized reference to an environment evidence pack."""
    generic_ref = build_sensor_evidence_artifact_ref(
        ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_NAME,
        artifact_ref,
        artifact_sha256=artifact_sha256,
        evidence_pack=evidence_pack,
        provider_kind=ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
        evidence_kind=ENVIRONMENT_EVIDENCE_KIND,
        require_hash=artifact_sha256 is not None,
    )
    return {
        "schema_version": generic_ref["schema_version"],
        "evidence_contract_version": ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
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


def compute_environment_evidence_pack_fingerprint(
    payload: Mapping[str, object],
) -> str:
    """Compute the v1 fingerprint over a persisted environment pack."""
    return compute_sensor_evidence_fingerprint(payload)


def classify_environment_evidence_pack_compatibility(
    payload: object,
    *,
    verify_fingerprint: bool = True,
) -> SensorEvidenceCompatibilityResult:
    """Classify an environment evidence pack with fail-closed semantics."""
    return classify_sensor_evidence_contract(
        payload,
        contract=ENVIRONMENT_EVIDENCE_PACK_CONTRACT,
        verify_fingerprint=verify_fingerprint,
    )


def validate_environment_evidence_pack_v1(
    payload: object,
    *,
    verify_fingerprint: bool = True,
) -> SensorEvidenceCompatibilityResult:
    """Validate a persisted v1 environment evidence pack."""
    return classify_environment_evidence_pack_compatibility(
        payload,
        verify_fingerprint=verify_fingerprint,
    )


def _counts(evaluation: dict[str, object]) -> dict[str, int]:
    status_counts = _status_counts(evaluation)
    return {
        "fixture_count": _int(evaluation.get("fixture_count")),
        "row_count": _int(evaluation.get("row_count")),
        "parsed_row_count": status_counts["parsed"],
        "partial_row_count": status_counts["partial"],
        "rejected_row_count": status_counts["rejected"],
        "malformed_rows": _int(evaluation.get("malformed_rows")),
        "category_count": _int(evaluation.get("category_count")),
    }


def _scores(
    evaluation: dict[str, object],
    counts: dict[str, int],
) -> dict[str, int]:
    quality = _score_int(evaluation.get("evidence_quality"))
    if counts.get("row_count", 0) <= 0:
        quality = 0
    return {
        "score": quality,
        "evidence_quality": quality,
        "replay_integrity": _score_int(evaluation.get("replay_integrity", quality)),
        "aggregate_evidence_quality": quality,
        "aggregate_replay_integrity": _score_int(evaluation.get("replay_integrity", quality)),
    }


def _status_counts(evaluation: dict[str, object]) -> dict[str, int]:
    raw = evaluation.get("status_counts")
    counts = {status: 0 for status in ENVIRONMENT_EVIDENCE_PACK_STATUS_VOCABULARY}
    if isinstance(raw, Mapping):
        for status in ENVIRONMENT_EVIDENCE_PACK_STATUS_VOCABULARY:
            counts[status] = _int(raw.get(status))
    return counts


def _diagnostic_counts(evaluation: dict[str, object]) -> dict[str, object]:
    raw_categories = evaluation.get("parse_error_categories")
    categories = {}
    if isinstance(raw_categories, Mapping):
        for key, value in raw_categories.items():
            category = _safe_category(key)
            categories[category] = categories.get(category, 0) + _int(value)
    categories = {key: value for key, value in sorted(categories.items()) if value}
    parse_error_count = sum(categories.values())
    return {
        "error_count": _int(evaluation.get("error_count"), parse_error_count),
        "parse_error_count": parse_error_count,
        "warning_count": _int(evaluation.get("warning_count")),
        "parse_error_categories": categories,
    }


def _safe_artifact_refs(value: dict[str, object] | None) -> dict[str, str]:
    from .evidence import safe_sensor_artifact_refs

    return safe_sensor_artifact_refs(value)


def _safe_hashes(value: dict[str, object] | None) -> dict[str, str | None]:
    from .evidence import safe_sensor_artifact_hashes

    return safe_sensor_artifact_hashes(value)


def _safe_category(value: object) -> str:
    text = str(value or "unknown").lower()
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in text).strip(
        "-"
    )
    return safe or "unknown"


def _status(value: object) -> str:
    return sensor_evidence_status(
        value,
        status_vocabulary=ENVIRONMENT_EVIDENCE_PACK_STATUS_VOCABULARY,
    )


def _score_int(value: object) -> int:
    return sensor_evidence_score_int(value)


def _int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


__all__ = [
    "ENVIRONMENT_EVIDENCE_KIND",
    "ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_NAME",
    "ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_REF",
    "ENVIRONMENT_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS",
    "ENVIRONMENT_EVIDENCE_PACK_CONTRACT",
    "ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION",
    "ENVIRONMENT_EVIDENCE_PACK_EXPORTER_ID",
    "ENVIRONMENT_EVIDENCE_PROVIDER_KIND",
    "build_environment_evidence_pack",
    "classify_environment_evidence_pack_compatibility",
    "compute_environment_evidence_pack_fingerprint",
    "environment_evidence_pack_artifact_metadata",
    "validate_environment_evidence_pack_v1",
]
