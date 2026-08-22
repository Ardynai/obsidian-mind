"""Shared sanitized evidence-pack helpers across evidence domains.

The legacy names live in ``somatic.sensors.evidence``.  This module gives
sensor, CSI, and document evidence packs a neutral import surface for the
already-shared privacy, artifact-ref, compatibility, and fingerprint behavior.
"""

from somatic.sensors.evidence import (
    SENSOR_EVIDENCE_ARTIFACT_REF_CLASSIFICATIONS,
    SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS,
    SENSOR_EVIDENCE_COUNT_CATEGORIES,
    SENSOR_EVIDENCE_DIAGNOSTIC_CATEGORY_FIELDS,
    SENSOR_EVIDENCE_DIAGNOSTIC_COUNT_FIELDS,
    SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
    SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
    SENSOR_EVIDENCE_FORBIDDEN_KEYS,
    SENSOR_EVIDENCE_FORBIDDEN_VALUE_FRAGMENTS,
    SENSOR_EVIDENCE_READINESS_VOCABULARY,
    SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS,
    SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS,
    SENSOR_EVIDENCE_SCHEMA_VERSION,
    SENSOR_EVIDENCE_SCORE_FIELDS,
    SENSOR_EVIDENCE_STATUS_VOCABULARY,
    SensorEvidenceArtifactRef,
    SensorEvidenceCompatibilityResult,
    SensorEvidenceContract,
    SensorEvidenceContractIdentity,
    build_sensor_evidence_artifact_ref,
    classify_sensor_evidence_artifact_ref,
    classify_sensor_evidence_contract,
    compute_sensor_evidence_fingerprint,
    finalize_sensor_evidence_pack_identity,
    looks_sha256,
    safe_sensor_artifact_hashes,
    safe_sensor_artifact_ref,
    safe_sensor_artifact_refs,
    safe_sensor_evidence_category,
    sensor_evidence_forbidden_fragments,
    sensor_evidence_int,
    sensor_evidence_payload_sha256,
    sensor_evidence_privacy_violation_count,
    sensor_evidence_readiness_status,
    sensor_evidence_result_code,
    sensor_evidence_score_int,
    sensor_evidence_status,
    sensor_evidence_status_count_dict,
    sensor_evidence_string_privacy_violation_count,
    sensor_evidence_version_value,
)

EvidenceArtifactRef = SensorEvidenceArtifactRef
EvidenceCompatibilityResult = SensorEvidenceCompatibilityResult
EvidencePackContract = SensorEvidenceContract
EvidencePackContractIdentity = SensorEvidenceContractIdentity

build_evidence_pack_artifact_ref = build_sensor_evidence_artifact_ref
classify_evidence_artifact_ref = classify_sensor_evidence_artifact_ref
classify_evidence_pack_contract = classify_sensor_evidence_contract
compute_evidence_pack_fingerprint = compute_sensor_evidence_fingerprint
safe_evidence_artifact_hashes = safe_sensor_artifact_hashes
safe_evidence_artifact_ref = safe_sensor_artifact_ref
safe_evidence_artifact_refs = safe_sensor_artifact_refs
evidence_pack_payload_sha256 = sensor_evidence_payload_sha256
evidence_pack_privacy_violation_count = sensor_evidence_privacy_violation_count
evidence_pack_string_privacy_violation_count = sensor_evidence_string_privacy_violation_count
evidence_readiness_status = sensor_evidence_readiness_status
evidence_result_code = sensor_evidence_result_code
evidence_score_int = sensor_evidence_score_int
evidence_status = sensor_evidence_status
evidence_status_count_dict = sensor_evidence_status_count_dict
evidence_version_value = sensor_evidence_version_value
finalize_evidence_pack_identity = finalize_sensor_evidence_pack_identity
safe_evidence_category = safe_sensor_evidence_category


def safe_evidence_int(value: object, default: int = 0) -> int:
    return sensor_evidence_int(value, default=default)


evidence_forbidden_fragments = sensor_evidence_forbidden_fragments


__all__ = [
    "SENSOR_EVIDENCE_ARTIFACT_REF_CLASSIFICATIONS",
    "SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS",
    "SENSOR_EVIDENCE_COUNT_CATEGORIES",
    "SENSOR_EVIDENCE_DIAGNOSTIC_CATEGORY_FIELDS",
    "SENSOR_EVIDENCE_DIAGNOSTIC_COUNT_FIELDS",
    "SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM",
    "SENSOR_EVIDENCE_FINGERPRINT_SCOPE",
    "SENSOR_EVIDENCE_FORBIDDEN_KEYS",
    "SENSOR_EVIDENCE_FORBIDDEN_VALUE_FRAGMENTS",
    "SENSOR_EVIDENCE_READINESS_VOCABULARY",
    "SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS",
    "SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS",
    "SENSOR_EVIDENCE_SCHEMA_VERSION",
    "SENSOR_EVIDENCE_SCORE_FIELDS",
    "SENSOR_EVIDENCE_STATUS_VOCABULARY",
    "EvidenceArtifactRef",
    "EvidenceCompatibilityResult",
    "EvidencePackContract",
    "EvidencePackContractIdentity",
    "SensorEvidenceArtifactRef",
    "SensorEvidenceCompatibilityResult",
    "SensorEvidenceContract",
    "SensorEvidenceContractIdentity",
    "build_evidence_pack_artifact_ref",
    "build_sensor_evidence_artifact_ref",
    "classify_evidence_artifact_ref",
    "classify_evidence_pack_contract",
    "classify_sensor_evidence_artifact_ref",
    "classify_sensor_evidence_contract",
    "compute_evidence_pack_fingerprint",
    "compute_sensor_evidence_fingerprint",
    "evidence_forbidden_fragments",
    "evidence_pack_payload_sha256",
    "evidence_pack_privacy_violation_count",
    "evidence_pack_string_privacy_violation_count",
    "evidence_readiness_status",
    "evidence_result_code",
    "evidence_score_int",
    "evidence_status",
    "evidence_status_count_dict",
    "evidence_version_value",
    "finalize_evidence_pack_identity",
    "looks_sha256",
    "safe_evidence_artifact_hashes",
    "safe_evidence_artifact_ref",
    "safe_evidence_artifact_refs",
    "safe_evidence_category",
    "safe_evidence_int",
    "safe_sensor_artifact_hashes",
    "safe_sensor_artifact_ref",
    "safe_sensor_artifact_refs",
    "sensor_evidence_int",
    "sensor_evidence_payload_sha256",
    "sensor_evidence_privacy_violation_count",
    "sensor_evidence_readiness_status",
    "sensor_evidence_result_code",
    "sensor_evidence_score_int",
    "sensor_evidence_status",
    "sensor_evidence_string_privacy_violation_count",
    "sensor_evidence_version_value",
]
