"""Generic sanitized sensor-evidence contract primitives."""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

SENSOR_EVIDENCE_SCHEMA_VERSION = 1
SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM = "sha256"
SENSOR_EVIDENCE_FINGERPRINT_SCOPE = (
    "json-dumps-indent-2-sort-keys-newline-with-pack-id-and-fingerprint-null"
)
SENSOR_EVIDENCE_STATUS_VOCABULARY = ("parsed", "partial", "rejected")
SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS = (
    "compatible",
    "incompatible",
    "unsupported_version",
    "malformed",
)
SENSOR_EVIDENCE_ARTIFACT_REF_CLASSIFICATIONS = (
    "compatible",
    "missing",
    "malformed",
    "hash_mismatch",
    "unsafe_ref",
)
SENSOR_EVIDENCE_READINESS_VOCABULARY = (
    "ready-with-sanitized-metadata",
    "partial-sanitized-metadata",
    "rejected-fail-closed",
)
SENSOR_EVIDENCE_DIAGNOSTIC_COUNT_FIELDS = (
    "error_count",
    "parse_error_count",
    "warning_count",
)
SENSOR_EVIDENCE_DIAGNOSTIC_CATEGORY_FIELDS = ("parse_error_categories",)
SENSOR_EVIDENCE_COUNT_CATEGORIES = (
    "fixture_count",
    "group_count",
    "evaluated_group_count",
    "parsed_group_count",
    "partial_group_count",
    "rejected_group_count",
    "frame_count",
    "sample_count",
    "row_count",
    "parsed_row_count",
    "partial_row_count",
    "rejected_row_count",
    "malformed_rows",
    "category_count",
    "format_class_count",
)
SENSOR_EVIDENCE_SCORE_FIELDS = (
    "score",
    "evidence_quality",
    "replay_integrity",
    "aggregate_evidence_quality",
    "aggregate_replay_integrity",
    "minimum_group_score",
    "average_group_score",
)
SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS = (
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
SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS = (
    "core_tournament_scores_modified",
    "tournament_rankings_modified",
    "ranking_input",
    "hardware_access",
    "network_calls",
    "serial_access",
    "mqtt_udp_listener",
    "packet_capture",
    "monitor_mode",
    "wifi_network_probing",
    "live_capture",
    "live_sensor_access",
    "raw_csi_data_collected",
    "raw_csi_data_exported",
    "raw_signal_values_exported",
    "raw_sensor_data_collected",
    "clinical_interpretation",
    "medical_or_clinical_claim",
    "personal_data_exported",
    "personal_health_data_exported",
    "baseline_data_exported",
    "real_health_data_loaded",
    "real_profile_storage",
    "database_access",
    "recommendation_generated",
    "prescription_generated",
    "medical_advice",
    "effectiveness_claim",
    "claim_effectiveness",
    "real_intervention_performed",
    "real_response_monitoring",
    "real_scheduling",
    "notification_automation",
    "reminder_automation",
    "external_memory",
    "diagnosis",
    "treatment_recommendation",
    "emergency_triage",
    "real_monitoring",
)
SENSOR_EVIDENCE_FORBIDDEN_KEYS = frozenset(
    {
        "samples",
        "raw_values",
        "real",
        "imag",
        "amplitude",
        "phase",
        "rssi",
        "raw_csi",
        "raw_rf",
        "raw_signal",
        "csi_values",
        "signal_values",
        "subcarrier",
        "subcarriers",
        "subcarrier_values",
        "values",
        "payload",
        "source_id",
        "source_ids",
        "frame_id",
        "mac",
        "bssid",
        "ssid",
        "device_id",
        "adapter_id",
        "router_id",
        "ip_address",
        "report",
        "summary",
        "files",
        "fixtures",
        "fixture_refs",
        "private_ref",
        "private_refs",
        "unsafe_ref",
        "unsafe_refs",
        "parse_errors",
        "local_path",
        "source_path",
        "staging_root",
        "provider_payload",
        "provider_payload_body",
        "parser_report_payload",
        "parser_report_body",
        "parsed_summary_payload",
        "parser_summary_body",
        "api_key",
        "credential",
        "credentials",
        "access_token",
        "refresh_token",
        "secret",
        "secret_value",
        "password",
        "authorization",
        "bearer",
    }
)
SENSOR_EVIDENCE_FORBIDDEN_VALUE_FRAGMENTS = (
    "raw_values",
    "samples",
    "amplitude",
    "phase",
    "rssi",
    "raw_csi",
    "raw_rf",
    "raw_signal",
    "csi_values",
    "signal_values",
    "subcarrier",
    "subcarriers",
    "subcarrier_values",
    "source_id",
    "source_ids",
    "fixture_refs",
    "private_ref",
    "private_refs",
    "unsafe_ref",
    "unsafe_refs",
    "credential",
    "credentials",
    "example.invalid",
)
SENSOR_EVIDENCE_EXACT_SAFE_METADATA_VALUES = frozenset(
    {
        "phase-11-planning-governance-complete",
        "explicit-future-phase-required-before-runtime-work",
    }
)


@dataclass(frozen=True)
class SensorEvidenceContractIdentity:
    """Stable identity for a sanitized sensor evidence contract."""

    provider_kind: str
    evidence_kind: str
    contract_version: int
    exporter_id: str
    schema_version: int = SENSOR_EVIDENCE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "provider_kind": self.provider_kind,
            "evidence_kind": self.evidence_kind,
            "contract_version": self.contract_version,
            "exporter_id": self.exporter_id,
        }


@dataclass(frozen=True)
class SensorEvidenceContract:
    """Compatibility contract for sanitized, portable sensor evidence packs."""

    identity: SensorEvidenceContractIdentity
    version_fields: Mapping[str, int]
    required_fields: tuple[str, ...]
    expected_identity_fields: Mapping[str, object]
    expected_generated_from: Mapping[str, object] | None = None
    required_object_fields: tuple[str, ...] = ()
    required_list_fields: tuple[str, ...] = ()
    count_fields: tuple[str, ...] = SENSOR_EVIDENCE_COUNT_CATEGORIES
    required_count_fields: tuple[str, ...] = ()
    count_status_count_fields: tuple[str, ...] = ()
    diagnostic_count_fields: tuple[str, ...] = SENSOR_EVIDENCE_DIAGNOSTIC_COUNT_FIELDS
    diagnostic_category_fields: tuple[str, ...] = SENSOR_EVIDENCE_DIAGNOSTIC_CATEGORY_FIELDS
    score_fields: tuple[str, ...] = SENSOR_EVIDENCE_SCORE_FIELDS
    required_score_fields: tuple[str, ...] = ()
    status_count_fields: tuple[str, ...] = ()
    required_true_flags: tuple[str, ...] = SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS
    required_false_flags: tuple[str, ...] = SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS
    status_vocabulary: tuple[str, ...] = SENSOR_EVIDENCE_STATUS_VOCABULARY
    readiness_vocabulary: tuple[str, ...] = SENSOR_EVIDENCE_READINESS_VOCABULARY
    known_top_level_fields: frozenset[str] | None = None
    forbidden_keys: frozenset[str] = SENSOR_EVIDENCE_FORBIDDEN_KEYS
    forbidden_value_fragments: tuple[str, ...] = SENSOR_EVIDENCE_FORBIDDEN_VALUE_FRAGMENTS
    pack_id_field: str = "pack_id"
    fingerprint_field: str = "pack_fingerprint"
    fingerprint_algorithm_field: str = "fingerprint_algorithm"
    fingerprint_scope_field: str = "fingerprint_scope"
    pack_id_prefix: str = "sensor-evidence-pack-"
    evidence_contract_version_field: str = "evidence_contract_version"

    def known_fields(self) -> frozenset[str]:
        if self.known_top_level_fields is not None:
            return self.known_top_level_fields
        fields = (
            set(self.required_fields)
            | set(self.version_fields)
            | set(self.required_true_flags)
            | set(self.required_false_flags)
            | set(self.expected_identity_fields)
            | {
                self.pack_id_field,
                self.fingerprint_field,
                self.fingerprint_algorithm_field,
                self.fingerprint_scope_field,
            }
        )
        return frozenset(str(field) for field in fields)


@dataclass(frozen=True)
class SensorEvidenceCompatibilityResult:
    """Sanitized compatibility decision for a sensor evidence pack."""

    classification: str
    valid: bool
    compatible: bool
    contract_version: int | None
    evidence_contract_version: int | None
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
            "evidence_contract_version": self.evidence_contract_version,
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


@dataclass(frozen=True)
class SensorEvidenceArtifactRef:
    """Sanitized run-relative reference to a sensor evidence artifact."""

    name: str
    provider_kind: str
    evidence_kind: str
    relative_path: str
    sha256: str | None
    pack_id: str
    pack_fingerprint: str
    status: str
    readiness_status: str
    classification: str
    present: bool
    error_count: int = 0
    errors: tuple[str, ...] = ()
    metadata_only: bool = True
    fixture_only: bool = True
    summary_output_only: bool = True
    raw_signal_values_exported: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
            "name": self.name,
            "provider_kind": self.provider_kind,
            "evidence_kind": self.evidence_kind,
            "artifact_ref": self.relative_path,
            "relative_path": self.relative_path,
            "artifact_sha256": self.sha256,
            "sha256": self.sha256,
            "pack_id": self.pack_id,
            "pack_fingerprint": self.pack_fingerprint,
            "status": self.status,
            "readiness_status": self.readiness_status,
            "classification": self.classification,
            "present": self.present,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "metadata_only": self.metadata_only,
            "fixture_only": self.fixture_only,
            "summary_output_only": self.summary_output_only,
            "raw_signal_values_exported": self.raw_signal_values_exported,
            "readiness_status_if_rejected": "rejected-fail-closed",
        }


def sensor_evidence_payload_sha256(payload: Mapping[str, object]) -> str:
    encoded = (json.dumps(dict(payload), indent=2, sort_keys=True) + "\n").encode("utf-8")
    return sha256(encoded).hexdigest()


def compute_sensor_evidence_fingerprint(
    payload: Mapping[str, object],
    *,
    identity_field: str = "pack_id",
    fingerprint_field: str = "pack_fingerprint",
) -> str:
    if not isinstance(payload, Mapping):
        return ""
    normalized = dict(payload)
    normalized[identity_field] = None
    normalized[fingerprint_field] = None
    return sensor_evidence_payload_sha256(normalized)


def finalize_sensor_evidence_pack_identity(
    payload: dict[str, object],
    *,
    pack_id_prefix: str,
    pack_id_field: str = "pack_id",
    fingerprint_field: str = "pack_fingerprint",
) -> dict[str, object]:
    fingerprint = compute_sensor_evidence_fingerprint(
        payload,
        identity_field=pack_id_field,
        fingerprint_field=fingerprint_field,
    )
    payload[fingerprint_field] = fingerprint
    payload[pack_id_field] = f"{pack_id_prefix}{fingerprint[:16]}"
    return payload


def sensor_evidence_readiness_status(
    status: object,
    *,
    evidence_quality: object = 0,
    status_vocabulary: tuple[str, ...] = SENSOR_EVIDENCE_STATUS_VOCABULARY,
) -> str:
    safe_status = sensor_evidence_status(status, status_vocabulary=status_vocabulary)
    if safe_status == "parsed" and sensor_evidence_score_int(evidence_quality) > 0:
        return "ready-with-sanitized-metadata"
    if safe_status == "partial":
        return "partial-sanitized-metadata"
    return "rejected-fail-closed"


def classify_sensor_evidence_contract(
    payload: object,
    *,
    contract: SensorEvidenceContract,
    verify_fingerprint: bool = True,
) -> SensorEvidenceCompatibilityResult:
    if not isinstance(payload, Mapping):
        return _compatibility_result(
            "malformed",
            None,
            None,
            "rejected",
            "rejected-fail-closed",
            readiness_vocabulary=contract.readiness_vocabulary,
            status_vocabulary=contract.status_vocabulary,
            errors=("payload_not_object",),
        )

    pack = dict(payload)
    contract_version = sensor_evidence_version_value(pack.get("contract_version"))
    evidence_contract_version = sensor_evidence_version_value(
        pack.get(contract.evidence_contract_version_field)
    )
    missing_version_count = sum(1 for field in contract.version_fields if field not in pack)
    non_integer_version_count = sum(
        1
        for field in contract.version_fields
        if field in pack and sensor_evidence_version_value(pack.get(field)) is None
    )
    if missing_version_count or non_integer_version_count:
        return _compatibility_result(
            "malformed",
            contract_version,
            evidence_contract_version,
            sensor_evidence_status(
                pack.get("status"), status_vocabulary=contract.status_vocabulary
            ),
            "rejected-fail-closed",
            readiness_vocabulary=contract.readiness_vocabulary,
            status_vocabulary=contract.status_vocabulary,
            errors=("missing_or_invalid_version_fields",),
            missing_required_field_count=missing_version_count,
        )

    if any(
        sensor_evidence_version_value(pack.get(field)) != expected
        for field, expected in contract.version_fields.items()
    ):
        return _compatibility_result(
            "unsupported_version",
            contract_version,
            evidence_contract_version,
            sensor_evidence_status(
                pack.get("status"), status_vocabulary=contract.status_vocabulary
            ),
            "rejected-fail-closed",
            readiness_vocabulary=contract.readiness_vocabulary,
            status_vocabulary=contract.status_vocabulary,
            errors=("unsupported_contract_version",),
        )

    if _unsupported_generated_from_versions(pack, contract):
        return _compatibility_result(
            "unsupported_version",
            contract_version,
            evidence_contract_version,
            sensor_evidence_status(
                pack.get("status"), status_vocabulary=contract.status_vocabulary
            ),
            "rejected-fail-closed",
            readiness_vocabulary=contract.readiness_vocabulary,
            status_vocabulary=contract.status_vocabulary,
            errors=("unsupported_generated_from_version",),
        )

    missing_required = [field for field in contract.required_fields if field not in pack]
    if missing_required:
        return _compatibility_result(
            "malformed",
            contract_version,
            evidence_contract_version,
            sensor_evidence_status(
                pack.get("status"), status_vocabulary=contract.status_vocabulary
            ),
            "rejected-fail-closed",
            readiness_vocabulary=contract.readiness_vocabulary,
            status_vocabulary=contract.status_vocabulary,
            errors=("missing_required_fields",),
            missing_required_field_count=len(missing_required),
        )

    errors = []
    warnings = []
    privacy_violation_count = sensor_evidence_privacy_violation_count(
        pack,
        forbidden_keys=contract.forbidden_keys,
        forbidden_value_fragments=contract.forbidden_value_fragments,
    )
    if privacy_violation_count:
        errors.append("privacy_boundary_violation")
    if _invalid_required_container_count(pack, contract):
        errors.append("invalid_required_container_shape")
    if _invalid_status_fields(pack, contract):
        errors.append("invalid_status_vocabulary")
    if _invalid_status_count_fields(pack, contract):
        errors.append("invalid_status_counts")
    if _invalid_diagnostic_counts(pack.get("diagnostic_counts"), contract):
        errors.append("invalid_diagnostic_counts")
    if _invalid_count_payload(pack.get("counts"), contract):
        errors.append("invalid_count_payload")
    if _invalid_score_payload(pack.get("scores"), contract):
        errors.append("invalid_score_payload")
    if _invalid_artifact_refs(pack.get("artifact_refs")):
        errors.append("invalid_artifact_refs")
    if _invalid_artifact_hashes(pack.get("artifact_hashes")):
        errors.append("invalid_artifact_hashes")
    boundary_flag_violation_count = _boundary_flag_violation_count(pack, contract)
    if boundary_flag_violation_count:
        errors.append("closed_boundary_flags_not_preserved")
    if _invalid_pack_identity(
        pack,
        contract=contract,
        verify_fingerprint=verify_fingerprint,
    ):
        errors.append("invalid_fingerprint_or_pack_id")
    if _invalid_identity_fields(pack, contract):
        errors.append("invalid_contract_identity")

    known_fields = contract.known_fields()
    unknown_field_count = len([key for key in pack if str(key) not in known_fields])
    unsafe_unknown_field_count = _unsafe_unknown_field_payload_count(
        pack,
        known_fields=known_fields,
        forbidden_value_fragments=contract.forbidden_value_fragments,
    )
    if unsafe_unknown_field_count:
        errors.append("unsafe_unknown_field_payload")
    if unknown_field_count:
        warnings.append("additive_unknown_fields_ignored")

    if errors:
        return _compatibility_result(
            "incompatible",
            contract_version,
            evidence_contract_version,
            sensor_evidence_status(
                pack.get("status"), status_vocabulary=contract.status_vocabulary
            ),
            "rejected-fail-closed",
            readiness_vocabulary=contract.readiness_vocabulary,
            status_vocabulary=contract.status_vocabulary,
            errors=tuple(sorted(set(errors))),
            warnings=tuple(sorted(set(warnings))),
            unknown_field_count=unknown_field_count,
            privacy_violation_count=privacy_violation_count
            + unsafe_unknown_field_count
            + boundary_flag_violation_count,
        )

    return _compatibility_result(
        "compatible",
        contract_version,
        evidence_contract_version,
        sensor_evidence_status(pack.get("status"), status_vocabulary=contract.status_vocabulary),
        str(pack.get("readiness_status")),
        readiness_vocabulary=contract.readiness_vocabulary,
        status_vocabulary=contract.status_vocabulary,
        fingerprint_verified=verify_fingerprint,
        warnings=tuple(sorted(set(warnings))),
        unknown_field_count=unknown_field_count,
    )


def build_sensor_evidence_artifact_ref(
    name: object,
    artifact_ref: object,
    *,
    artifact_sha256: object | None = None,
    evidence_pack: object | None = None,
    provider_kind: object = "sensor",
    evidence_kind: object = "sanitized-evidence-pack",
    require_hash: bool = True,
) -> dict[str, object]:
    """Build a compact sanitized reference to a persisted sensor evidence pack."""
    pack = dict(evidence_pack) if isinstance(evidence_pack, Mapping) else {}
    candidate = {
        "name": name,
        "provider_kind": provider_kind,
        "evidence_kind": evidence_kind,
        "artifact_ref": artifact_ref,
        "artifact_sha256": artifact_sha256,
        "pack_id": pack.get("pack_id"),
        "pack_fingerprint": pack.get("pack_fingerprint"),
        "status": pack.get("status"),
        "readiness_status": pack.get("readiness_status"),
        "metadata_only": True,
        "fixture_only": True,
        "summary_output_only": True,
        "raw_signal_values_exported": False,
    }
    return classify_sensor_evidence_artifact_ref(
        candidate,
        require_hash=require_hash,
    ).to_dict()


def classify_sensor_evidence_artifact_ref(
    value: object,
    *,
    run_dir: str | Path | None = None,
    require_present: bool = False,
    verify_hash: bool = False,
    require_hash: bool = True,
) -> SensorEvidenceArtifactRef:
    """Classify a compact artifact ref without echoing unsafe paths or payloads."""
    if not isinstance(value, Mapping):
        return _artifact_ref_result(
            "malformed",
            errors=("artifact_ref_not_object",),
        )

    item = dict(value)
    name = _safe_sensor_evidence_identifier(item.get("name"), default="sensor_evidence")
    provider_kind = _safe_sensor_evidence_identifier(
        item.get("provider_kind"),
        default="sensor",
    )
    evidence_kind = _safe_sensor_evidence_identifier(
        item.get("evidence_kind"),
        default="sanitized-evidence-pack",
    )
    relative_path = safe_sensor_artifact_ref(
        item.get("artifact_ref")
        or item.get("relative_path")
        or item.get("path")
        or item.get("path_or_uri")
    )
    sha_value = item.get("artifact_sha256", item.get("sha256"))
    sha_text = str(sha_value) if sha_value is not None else None
    safe_sha = sha_text if sha_text and looks_sha256(sha_text) else None
    pack_id = _safe_sensor_evidence_identifier(item.get("pack_id"), default="")
    pack_fingerprint_value = item.get("pack_fingerprint")
    pack_fingerprint = (
        str(pack_fingerprint_value)
        if isinstance(pack_fingerprint_value, str) and looks_sha256(pack_fingerprint_value)
        else ""
    )
    status = sensor_evidence_status(item.get("status"))
    readiness_status = str(item.get("readiness_status") or "rejected-fail-closed")
    if readiness_status not in SENSOR_EVIDENCE_READINESS_VOCABULARY:
        readiness_status = "rejected-fail-closed"

    errors = []
    classification = "compatible"
    if sensor_evidence_privacy_violation_count(item):
        errors.append("privacy_boundary_violation")
        classification = "malformed"
    if not relative_path:
        errors.append("invalid_artifact_ref")
        classification = "unsafe_ref"
    if require_hash and not safe_sha:
        errors.append("invalid_artifact_sha256")
        if classification == "compatible":
            classification = "malformed"

    artifact_path: Path | None = None
    if run_dir is not None and relative_path:
        artifact_path = _run_relative_artifact_path(run_dir, relative_path)
        if artifact_path is None:
            errors.append("invalid_artifact_ref")
            classification = "unsafe_ref"

    if artifact_path is not None:
        if require_present and not artifact_path.exists():
            errors.append("missing_artifact")
            classification = "missing"
        elif verify_hash and safe_sha and artifact_path.exists():
            if _file_sha256(artifact_path) != safe_sha:
                errors.append("artifact_hash_mismatch")
                classification = "hash_mismatch"

    return _artifact_ref_result(
        classification,
        name=name,
        provider_kind=provider_kind,
        evidence_kind=evidence_kind,
        relative_path=relative_path,
        sha256=safe_sha,
        pack_id=pack_id,
        pack_fingerprint=pack_fingerprint,
        status=status,
        readiness_status=readiness_status,
        errors=tuple(sorted(set(errors))),
    )


def safe_sensor_artifact_ref(value: object) -> str:
    text = str(value or "").replace("\\", "/")
    if not text.startswith("artifacts/"):
        return ""
    if "://" in text or Path(text).is_absolute():
        return ""
    if any(part in ("", ".", "..") for part in Path(text).parts):
        return ""
    return text.replace("\\", "/")


def safe_sensor_artifact_refs(value: object) -> dict[str, str]:
    refs = {}
    if not isinstance(value, Mapping):
        return refs
    for key, item in sorted(value.items()):
        safe_ref = safe_sensor_artifact_ref(item)
        if safe_ref:
            refs[str(key)] = safe_ref
    return refs


def safe_sensor_artifact_hashes(value: object) -> dict[str, str | None]:
    hashes = {}
    if not isinstance(value, Mapping):
        return hashes
    for key, item in sorted(value.items()):
        text = str(item) if item is not None else None
        hashes[str(key)] = text if text and looks_sha256(text) else None
    return hashes


def looks_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def sensor_evidence_version_value(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def sensor_evidence_status(
    value: object,
    *,
    status_vocabulary: tuple[str, ...] = SENSOR_EVIDENCE_STATUS_VOCABULARY,
) -> str:
    status = str(value or "rejected")
    if status not in status_vocabulary:
        return "rejected"
    return status


def sensor_evidence_status_count_dict(
    value: object,
    *,
    status_vocabulary: tuple[str, ...] = SENSOR_EVIDENCE_STATUS_VOCABULARY,
) -> dict[str, int]:
    counts = {status: 0 for status in status_vocabulary}
    if isinstance(value, Mapping):
        for status in status_vocabulary:
            counts[status] = sensor_evidence_int(value.get(status))
    return counts


def sensor_evidence_score_int(value: object) -> int:
    return max(0, min(100, sensor_evidence_int(value)))


def sensor_evidence_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def sensor_evidence_result_code(value: object) -> str:
    text = str(value or "unknown")
    sanitized = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_" for char in text.lower()
    ).strip("_")
    return sanitized or "unknown"


def safe_sensor_evidence_category(value: object) -> str:
    text = str(value or "unknown").lower()
    sanitized = "".join(
        char if char.isalnum() or char in {"-", "_"} else "-" for char in text
    ).strip("-")
    return sanitized or "unknown"


def sensor_evidence_forbidden_fragments(
    *domain_fragments: str,
) -> tuple[str, ...]:
    return tuple(dict.fromkeys(SENSOR_EVIDENCE_FORBIDDEN_VALUE_FRAGMENTS + tuple(domain_fragments)))


def sensor_evidence_privacy_violation_count(
    value: object,
    *,
    forbidden_keys: frozenset[str] = SENSOR_EVIDENCE_FORBIDDEN_KEYS,
    forbidden_value_fragments: tuple[str, ...] = SENSOR_EVIDENCE_FORBIDDEN_VALUE_FRAGMENTS,
) -> int:
    if isinstance(value, Mapping):
        violations = 0
        for key, item in value.items():
            if str(key).lower() in forbidden_keys:
                violations += 1
            violations += sensor_evidence_privacy_violation_count(
                item,
                forbidden_keys=forbidden_keys,
                forbidden_value_fragments=forbidden_value_fragments,
            )
        return violations
    if isinstance(value, list):
        return sum(
            sensor_evidence_privacy_violation_count(
                item,
                forbidden_keys=forbidden_keys,
                forbidden_value_fragments=forbidden_value_fragments,
            )
            for item in value
        )
    if isinstance(value, str):
        return sensor_evidence_string_privacy_violation_count(
            value,
            forbidden_value_fragments=forbidden_value_fragments,
        )
    return 0


def sensor_evidence_string_privacy_violation_count(
    value: str,
    *,
    forbidden_value_fragments: tuple[str, ...] = SENSOR_EVIDENCE_FORBIDDEN_VALUE_FRAGMENTS,
) -> int:
    lowered = value.lower()
    if lowered in SENSOR_EVIDENCE_EXACT_SAFE_METADATA_VALUES:
        return 0
    normalized = value.replace("\\", "/")
    violations = sum(1 for fragment in forbidden_value_fragments if fragment in lowered)
    if "://" in value:
        violations += 1
    if re.match(r"^[A-Za-z]:/", normalized):
        violations += 1
    if normalized.startswith("/"):
        violations += 1
    return violations


def _artifact_ref_result(
    classification: str,
    *,
    name: str = "sensor_evidence",
    provider_kind: str = "sensor",
    evidence_kind: str = "sanitized-evidence-pack",
    relative_path: str = "",
    sha256: str | None = None,
    pack_id: str = "",
    pack_fingerprint: str = "",
    status: str = "rejected",
    readiness_status: str = "rejected-fail-closed",
    errors: tuple[str, ...] = (),
) -> SensorEvidenceArtifactRef:
    safe_classification = (
        classification
        if classification in SENSOR_EVIDENCE_ARTIFACT_REF_CLASSIFICATIONS
        else "malformed"
    )
    safe_errors = tuple(sensor_evidence_result_code(error) for error in errors)
    return SensorEvidenceArtifactRef(
        name=name,
        provider_kind=provider_kind,
        evidence_kind=evidence_kind,
        relative_path=relative_path if safe_classification == "compatible" else "",
        sha256=sha256 if safe_classification == "compatible" else None,
        pack_id=pack_id,
        pack_fingerprint=pack_fingerprint,
        status=sensor_evidence_status(status),
        readiness_status=(
            readiness_status
            if readiness_status in SENSOR_EVIDENCE_READINESS_VOCABULARY
            else "rejected-fail-closed"
        ),
        classification=safe_classification,
        present=safe_classification == "compatible",
        error_count=len(safe_errors),
        errors=safe_errors,
    )


def _safe_sensor_evidence_identifier(value: object, *, default: str) -> str:
    text = str(value or "")
    if not text:
        return default
    if sensor_evidence_string_privacy_violation_count(text):
        return default
    safe = "".join(
        char if char.isalnum() or char in {"-", "_"} else "-" for char in text.lower()
    ).strip("-")
    return safe or default


def _run_relative_artifact_path(run_dir: str | Path, relative_path: str) -> Path | None:
    base = Path(run_dir)
    candidate = base / relative_path
    try:
        candidate.resolve().relative_to(base.resolve())
    except ValueError:
        return None
    return candidate


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _compatibility_result(
    classification: str,
    contract_version: int | None,
    evidence_contract_version: int | None,
    status: str,
    readiness_status: str,
    *,
    readiness_vocabulary: tuple[str, ...],
    status_vocabulary: tuple[str, ...],
    fingerprint_verified: bool = False,
    errors: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
    missing_required_field_count: int = 0,
    unknown_field_count: int = 0,
    privacy_violation_count: int = 0,
) -> SensorEvidenceCompatibilityResult:
    safe_classification = (
        classification
        if classification in SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS
        else "malformed"
    )
    safe_errors = tuple(sensor_evidence_result_code(error) for error in errors)
    safe_warnings = tuple(sensor_evidence_result_code(warning) for warning in warnings)
    return SensorEvidenceCompatibilityResult(
        classification=safe_classification,
        valid=safe_classification == "compatible",
        compatible=safe_classification == "compatible",
        contract_version=contract_version,
        evidence_contract_version=evidence_contract_version,
        status=sensor_evidence_status(status, status_vocabulary=status_vocabulary),
        readiness_status=(
            readiness_status if readiness_status in readiness_vocabulary else "rejected-fail-closed"
        ),
        fingerprint_verified=bool(fingerprint_verified and safe_classification == "compatible"),
        error_count=len(safe_errors),
        warning_count=len(safe_warnings),
        missing_required_field_count=missing_required_field_count,
        unknown_field_count=unknown_field_count,
        privacy_violation_count=privacy_violation_count,
        errors=safe_errors,
        warnings=safe_warnings,
    )


def _invalid_required_container_count(
    pack: Mapping[str, object],
    contract: SensorEvidenceContract,
) -> int:
    invalid_count = 0
    for field in contract.required_object_fields:
        if not isinstance(pack.get(field), Mapping):
            invalid_count += 1
    for field in contract.required_list_fields:
        if not isinstance(pack.get(field), list):
            invalid_count += 1
    return invalid_count


def _invalid_status_fields(
    pack: Mapping[str, object],
    contract: SensorEvidenceContract,
) -> bool:
    status = pack.get("status")
    readiness_status = pack.get("readiness_status")
    if status not in contract.status_vocabulary:
        return True
    if readiness_status not in contract.readiness_vocabulary:
        return True
    scores = pack.get("scores") if isinstance(pack.get("scores"), Mapping) else {}
    expected = sensor_evidence_readiness_status(
        str(status),
        evidence_quality=dict(scores).get("evidence_quality", 0),
        status_vocabulary=contract.status_vocabulary,
    )
    return readiness_status != expected


def _invalid_diagnostic_counts(
    value: object,
    contract: SensorEvidenceContract,
) -> bool:
    if value is None:
        return False
    if not isinstance(value, Mapping):
        return True
    count_fields = set(contract.diagnostic_count_fields)
    category_fields = set(contract.diagnostic_category_fields)
    for key, item in value.items():
        if str(key) in count_fields:
            if isinstance(item, bool) or not isinstance(item, int) or item < 0:
                return True
            continue
        if str(key) in category_fields:
            if not isinstance(item, Mapping):
                return True
            for category, count in item.items():
                if not isinstance(category, str):
                    return True
                if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                    return True
            continue
        return True
    return False


def _invalid_status_count_fields(
    pack: Mapping[str, object],
    contract: SensorEvidenceContract,
) -> bool:
    for field in contract.status_count_fields:
        if field not in pack:
            continue
        if _invalid_status_count_dict(pack.get(field), contract):
            return True
    return False


def _invalid_status_count_dict(
    value: object,
    contract: SensorEvidenceContract,
) -> bool:
    if not isinstance(value, Mapping):
        return True
    for status in contract.status_vocabulary:
        item = value.get(status)
        if isinstance(item, bool) or not isinstance(item, int) or item < 0:
            return True
    return False


def _invalid_count_payload(
    value: object,
    contract: SensorEvidenceContract,
) -> bool:
    if value is None:
        return False
    if not isinstance(value, Mapping):
        return True
    count_fields = set(contract.count_fields)
    count_status_count_fields = set(contract.count_status_count_fields)
    for field in contract.required_count_fields:
        if field not in value:
            return True
    for field in count_status_count_fields:
        if field not in value:
            return True
    for key, item in value.items():
        key_text = str(key)
        if key_text in count_status_count_fields:
            if _invalid_status_count_dict(item, contract):
                return True
            continue
        if key_text not in count_fields:
            return True
        if isinstance(item, bool) or not isinstance(item, int) or item < 0:
            return True
    return False


def _invalid_score_payload(
    value: object,
    contract: SensorEvidenceContract,
) -> bool:
    if value is None:
        return False
    if not isinstance(value, Mapping):
        return True
    score_fields = set(contract.score_fields)
    for field in contract.required_score_fields:
        if field not in value:
            return True
    for key, item in value.items():
        if str(key) not in score_fields:
            return True
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            return True
        if item < 0 or item > 100:
            return True
    return False


def _invalid_artifact_refs(value: object) -> bool:
    if value is None:
        return False
    if not isinstance(value, Mapping):
        return True
    return safe_sensor_artifact_refs(value) != dict(value)


def _invalid_artifact_hashes(value: object) -> bool:
    if value is None:
        return False
    if not isinstance(value, Mapping):
        return True
    return safe_sensor_artifact_hashes(value) != dict(value)


def _invalid_boundary_flags(
    pack: Mapping[str, object],
    contract: SensorEvidenceContract,
) -> bool:
    return _boundary_flag_violation_count(pack, contract) > 0


def _boundary_flag_violation_count(
    pack: Mapping[str, object],
    contract: SensorEvidenceContract,
) -> int:
    violations = 0
    for field in contract.required_true_flags:
        if pack.get(field) is not True:
            violations += 1
    for field in contract.required_false_flags:
        if pack.get(field) is not False:
            violations += 1
    return violations


def _invalid_pack_identity(
    pack: Mapping[str, object],
    *,
    contract: SensorEvidenceContract,
    verify_fingerprint: bool,
) -> bool:
    fingerprint = pack.get(contract.fingerprint_field)
    pack_id = pack.get(contract.pack_id_field)
    if not isinstance(fingerprint, str) or not looks_sha256(fingerprint):
        return True
    if pack_id != f"{contract.pack_id_prefix}{fingerprint[:16]}":
        return True
    if str(pack.get(contract.fingerprint_algorithm_field)) != (
        SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM
    ):
        return True
    if str(pack.get(contract.fingerprint_scope_field)) != (SENSOR_EVIDENCE_FINGERPRINT_SCOPE):
        return True
    if (
        verify_fingerprint
        and compute_sensor_evidence_fingerprint(
            pack,
            identity_field=contract.pack_id_field,
            fingerprint_field=contract.fingerprint_field,
        )
        != fingerprint
    ):
        return True
    return False


def _invalid_identity_fields(
    pack: Mapping[str, object],
    contract: SensorEvidenceContract,
) -> bool:
    for field, expected in contract.expected_identity_fields.items():
        if pack.get(field) != expected:
            return True
    if contract.expected_generated_from is None:
        return False
    generated_from = pack.get("generated_from")
    if not isinstance(generated_from, Mapping):
        return True
    return dict(generated_from) != dict(contract.expected_generated_from)


def _unsupported_generated_from_versions(
    pack: Mapping[str, object],
    contract: SensorEvidenceContract,
) -> bool:
    if contract.expected_generated_from is None:
        return False
    generated_from = pack.get("generated_from")
    if not isinstance(generated_from, Mapping):
        return False
    for field, expected in contract.expected_generated_from.items():
        if not str(field).endswith("_version"):
            continue
        if sensor_evidence_version_value(generated_from.get(field)) != expected:
            return True
    return False


def _unsafe_unknown_field_payload_count(
    pack: Mapping[str, object],
    *,
    known_fields: frozenset[str],
    forbidden_value_fragments: tuple[str, ...],
) -> int:
    unsafe_count = 0
    for key, value in pack.items():
        if str(key) in known_fields:
            continue
        if not _safe_unknown_field_value(
            value,
            forbidden_value_fragments=forbidden_value_fragments,
        ):
            unsafe_count += 1
    return unsafe_count


def _safe_unknown_field_value(
    value: object,
    *,
    forbidden_value_fragments: tuple[str, ...],
) -> bool:
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, str):
        return (
            sensor_evidence_string_privacy_violation_count(
                value,
                forbidden_value_fragments=forbidden_value_fragments,
            )
            == 0
        )
    return False


__all__ = [
    "SENSOR_EVIDENCE_ARTIFACT_REF_CLASSIFICATIONS",
    "SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS",
    "SENSOR_EVIDENCE_COUNT_CATEGORIES",
    "SENSOR_EVIDENCE_DIAGNOSTIC_COUNT_FIELDS",
    "SENSOR_EVIDENCE_DIAGNOSTIC_CATEGORY_FIELDS",
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
    "SensorEvidenceCompatibilityResult",
    "SensorEvidenceArtifactRef",
    "SensorEvidenceContract",
    "SensorEvidenceContractIdentity",
    "build_sensor_evidence_artifact_ref",
    "classify_sensor_evidence_artifact_ref",
    "classify_sensor_evidence_contract",
    "compute_sensor_evidence_fingerprint",
    "finalize_sensor_evidence_pack_identity",
    "looks_sha256",
    "safe_sensor_artifact_hashes",
    "safe_sensor_artifact_ref",
    "safe_sensor_artifact_refs",
    "safe_sensor_evidence_category",
    "sensor_evidence_forbidden_fragments",
    "sensor_evidence_int",
    "sensor_evidence_payload_sha256",
    "sensor_evidence_privacy_violation_count",
    "sensor_evidence_readiness_status",
    "sensor_evidence_result_code",
    "sensor_evidence_score_int",
    "sensor_evidence_status",
    "sensor_evidence_status_count_dict",
    "sensor_evidence_string_privacy_violation_count",
    "sensor_evidence_version_value",
]
