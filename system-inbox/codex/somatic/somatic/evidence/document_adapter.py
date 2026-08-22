"""Metadata-only document adapter boundary.

The adapter contract is intentionally narrower than the document evidence-pack
contract.  Future providers must cross this boundary with sanitized count/status
metadata only; unsafe adapter output is converted to a rejected metadata result
before an evidence pack is built.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from somatic.evidence.framework import (
    SENSOR_EVIDENCE_STATUS_VOCABULARY,
    evidence_pack_string_privacy_violation_count,
    evidence_readiness_status,
    evidence_score_int,
    evidence_status,
    evidence_status_count_dict,
    safe_evidence_category,
    safe_evidence_int,
)
from somatic.safety.adapter_readiness import evaluate_real_mode_readiness
from somatic.safety.phase11_contracts import (
    PHASE11_ACCEPTANCE_FOLLOWUP_STATUS_LABELS,
    PHASE11_AUDIT_HANDOFF_STATUS_LABELS,
    PHASE11_AUDIT_INDEX_STATUS_LABELS,
    PHASE11_CONTRACT_STATUS_LABELS,
    PHASE11_DECISION_CLOSEOUT_STATUS_LABELS,
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_FOLLOWUP_QUEUE_STATUS_LABELS,
    PHASE11_HANDOFF_ACCEPTANCE_STATUS_LABELS,
    PHASE11_LIFECYCLE_STATUS_LABELS,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS_LABELS,
    PHASE11_PREFLIGHT_STATUS_LABELS,
    PHASE11_REVIEW_RECORD_STATUS_LABELS,
    PHASE11_REVIEW_TRAIL_EXPORT_STATUS_LABELS,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS_LABELS,
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

DOCUMENT_ADAPTER_CONTRACT_VERSION = 1
DOCUMENT_ADAPTER_KIND = "metadata-document-adapter"
DOCUMENT_FIXTURE_ADAPTER_ID = "document-fixture-metadata-adapter-v1"
DOCUMENT_ADAPTER_CAPABILITY_LABELS = (
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
DOCUMENT_ADAPTER_ALLOWED_OUTPUT_FIELDS = frozenset(
    {
        "status",
        "fixture_count",
        "document_count",
        "total_word_count",
        "total_line_count",
        "total_char_count",
        "format_count",
        "status_counts",
        "parse_error_categories",
        "error_count",
        "warning_count",
        "evidence_quality",
        "replay_integrity",
    }
)
DOCUMENT_ADAPTER_FORBIDDEN_KEYS = frozenset(
    {
        "absolute_path",
        "absolute_paths",
        "access_token",
        "api_key",
        "authorization",
        "bearer",
        "body",
        "content",
        "credential",
        "credentials",
        "document_body",
        "document_bodies",
        "document_text",
        "file",
        "files",
        "filename",
        "filenames",
        "fixture_ref",
        "fixture_refs",
        "local_path",
        "parser_body",
        "parser_report_body",
        "parser_summary_body",
        "password",
        "path",
        "paths",
        "payload",
        "private_ref",
        "private_refs",
        "provider_body",
        "provider_payload",
        "provider_payload_body",
        "raw_document_text",
        "raw_text",
        "refresh_token",
        "secret",
        "secret_value",
        "source_id",
        "source_ids",
        "source_identifier",
        "source_identifiers",
        "source_path",
        "text",
        "token",
        "url",
        "urls",
        "uri",
        "uris",
    }
)
DOCUMENT_ADAPTER_FORBIDDEN_KEY_FRAGMENTS = (
    "absolute_path",
    "access_token",
    "api_key",
    "authorization",
    "credential",
    "document_body",
    "document_text",
    "filename",
    "fixture_ref",
    "local_path",
    "parser_body",
    "parser_report",
    "parser_summary",
    "provider_body",
    "provider_payload",
    "raw_",
    "refresh_token",
    "secret",
    "source_id",
    "source_identifier",
    "source_path",
)
DOCUMENT_ADAPTER_FORBIDDEN_VALUE_FRAGMENTS = (
    "document-parsed.json",
    "document-mixed.json",
    "fixture://",
    "fixtures/",
    "raw document text",
    "raw_document_text",
    "source_id",
    "source_ids",
    "provider_payload",
    "provider_payload_body",
    "parser_report_body",
    "parser_summary_body",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "bearer",
    "credential",
    "password",
    "example.invalid",
)


class MetadataOnlyDocumentAdapter(Protocol):
    """Interface for document providers that emit sanitized metadata only."""

    provider_id: str

    def status(self) -> dict[str, object]:
        """Return sanitized adapter/provider status metadata."""

    def evidence_pack(
        self,
        fixture_refs: object,
        *,
        repo_root: object,
        artifact_refs: dict[str, object] | None = None,
        artifact_hashes: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Return a sanitized document evidence pack."""


@dataclass(frozen=True)
class DocumentAdapterOutputValidationResult:
    """Sanitized fail-closed validation result for adapter output."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    sanitized_output: dict[str, object]
    sanitized: bool = True
    metadata_only: bool = True
    fixture_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_output.get("status") or "rejected")

    @property
    def readiness_status(self) -> str:
        return evidence_readiness_status(
            self.status,
            evidence_quality=self.sanitized_output.get("evidence_quality"),
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
            "readiness_status": self.readiness_status,
            "sanitized": self.sanitized,
            "metadata_only": self.metadata_only,
            "fixture_only": self.fixture_only,
        }


def document_fixture_adapter_status() -> dict[str, object]:
    """Return public status for the fixture-backed metadata adapter."""

    real_mode_gate = document_adapter_real_mode_readiness_gate()
    phase11_status = phase11_contract_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
        readiness_gate=real_mode_gate,
    )
    review_record_status = phase11_review_record_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    preflight_status = phase11_preflight_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    lifecycle_status = phase11_dossier_lifecycle_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    audit_index_status = phase11_audit_index_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    audit_handoff_status = phase11_audit_handoff_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    handoff_acceptance_status = phase11_handoff_acceptance_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    acceptance_followup_status = phase11_acceptance_followup_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    followup_queue_status = phase11_followup_queue_index_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    decision_closeout_status = phase11_decision_closeout_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    review_trail_export_status = phase11_review_trail_export_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    runtime_gap_ledger_status = phase11_runtime_authorization_gap_ledger_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    planning_governance_closeout_status = phase11_planning_governance_closeout_status_summary()
    return {
        "schema_version": 1,
        "adapter_contract_version": DOCUMENT_ADAPTER_CONTRACT_VERSION,
        "adapter_kind": DOCUMENT_ADAPTER_KIND,
        "status": "metadata-only-ready",
        "capability_labels": list(DOCUMENT_ADAPTER_CAPABILITY_LABELS),
        "metadata_only": True,
        "fixture_only": True,
        "offline": True,
        "sanitized": True,
        "fail_closed_output_validation": True,
        "file_crawling": False,
        "pdf_parsing": False,
        "real_ingestion": False,
        "network_calls": False,
        "document_bodies_exported": False,
        "origin_ids_exported": False,
        "absolute_paths_exported": False,
        "urls_exported": False,
        "provider_bodies_exported": False,
        "parser_bodies_exported": False,
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


def document_adapter_real_mode_readiness_gate(
    review_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the shared real-mode gate for the document adapter boundary."""

    return evaluate_real_mode_readiness(
        provider_kind="document-fixture",
        adapter_kind=DOCUMENT_ADAPTER_KIND,
        current_mode="fixture-only",
        review_record=review_record,
    ).to_dict()


def validate_document_adapter_output(
    output: object,
) -> DocumentAdapterOutputValidationResult:
    """Validate and sanitize metadata-only document adapter output."""

    if not isinstance(output, Mapping):
        return _invalid_result(("adapter_output_not_object",), classification="malformed")

    errors: list[str] = []
    unknown_fields = set(str(key) for key in output) - DOCUMENT_ADAPTER_ALLOWED_OUTPUT_FIELDS
    if unknown_fields:
        errors.append("adapter_output_unknown_field")

    privacy_violations = _adapter_privacy_violation_count(output)
    if privacy_violations:
        errors.append("adapter_output_privacy_boundary")

    if not isinstance(output.get("status_counts"), Mapping):
        errors.append("adapter_output_status_counts_missing")
    if not isinstance(output.get("parse_error_categories"), Mapping):
        errors.append("adapter_output_parse_categories_missing")

    missing_count_fields = [
        field
        for field in (
            "fixture_count",
            "document_count",
            "total_word_count",
            "total_line_count",
            "total_char_count",
            "format_count",
            "error_count",
            "warning_count",
            "evidence_quality",
            "replay_integrity",
        )
        if field not in output
    ]
    if missing_count_fields:
        errors.append("adapter_output_required_count_missing")

    if errors:
        return _invalid_result(
            tuple(sorted(set(errors))),
            privacy_violation_count=privacy_violations,
            classification="incompatible",
        )

    sanitized = _sanitize_document_adapter_output(output)
    return DocumentAdapterOutputValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        sanitized_output=sanitized,
    )


def sanitize_document_adapter_output(output: object) -> dict[str, object]:
    """Return safe adapter metadata, rejecting unsafe output fail-closed."""

    return validate_document_adapter_output(output).sanitized_output


def rejected_document_adapter_output(
    category: str = "adapter-output-rejected",
) -> dict[str, object]:
    """Return a deterministic rejected metadata-only adapter output."""

    safe_category = safe_evidence_category(category)
    return {
        "status": "rejected",
        "fixture_count": 0,
        "document_count": 0,
        "total_word_count": 0,
        "total_line_count": 0,
        "total_char_count": 0,
        "format_count": 0,
        "status_counts": {"parsed": 0, "partial": 0, "rejected": 1},
        "parse_error_categories": {safe_category: 1},
        "error_count": 1,
        "warning_count": 0,
        "evidence_quality": 0,
        "replay_integrity": 0,
    }


def _invalid_result(
    errors: tuple[str, ...],
    *,
    privacy_violation_count: int = 0,
    classification: str = "incompatible",
) -> DocumentAdapterOutputValidationResult:
    category = (
        "adapter-output-privacy-boundary" if privacy_violation_count else "adapter-output-invalid"
    )
    return DocumentAdapterOutputValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        sanitized_output=rejected_document_adapter_output(category),
    )


def _sanitize_document_adapter_output(
    output: Mapping[str, object],
) -> dict[str, object]:
    status = evidence_status(
        output.get("status"),
        status_vocabulary=SENSOR_EVIDENCE_STATUS_VOCABULARY,
    )
    status_counts = evidence_status_count_dict(output.get("status_counts"))
    categories: dict[str, int] = {}
    raw_categories = output.get("parse_error_categories")
    if isinstance(raw_categories, Mapping):
        for key, value in raw_categories.items():
            category = safe_evidence_category(key)
            count = safe_evidence_int(value)
            if count:
                categories[category] = categories.get(category, 0) + count
    categories = dict(sorted(categories.items()))
    parse_error_count = sum(categories.values())
    error_count = safe_evidence_int(output.get("error_count"), parse_error_count)
    warning_count = safe_evidence_int(output.get("warning_count"))
    document_count = safe_evidence_int(output.get("document_count"))
    quality = evidence_score_int(output.get("evidence_quality"))
    if document_count <= 0 or status == "rejected":
        quality = 0
    replay = evidence_score_int(output.get("replay_integrity", quality))
    if status == "rejected":
        replay = 0
    return {
        "status": status,
        "fixture_count": safe_evidence_int(output.get("fixture_count")),
        "document_count": document_count,
        "total_word_count": safe_evidence_int(output.get("total_word_count")),
        "total_line_count": safe_evidence_int(output.get("total_line_count")),
        "total_char_count": safe_evidence_int(output.get("total_char_count")),
        "format_count": safe_evidence_int(output.get("format_count")),
        "status_counts": status_counts,
        "parse_error_categories": categories,
        "error_count": error_count,
        "warning_count": warning_count,
        "evidence_quality": quality,
        "replay_integrity": replay,
    }


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
    if text in DOCUMENT_ADAPTER_FORBIDDEN_KEYS:
        return True
    return any(fragment in text for fragment in DOCUMENT_ADAPTER_FORBIDDEN_KEY_FRAGMENTS)


def _adapter_string_privacy_violation_count(value: str) -> int:
    lowered = value.lower().replace("\\", "/")
    return evidence_pack_string_privacy_violation_count(
        lowered,
        forbidden_value_fragments=DOCUMENT_ADAPTER_FORBIDDEN_VALUE_FRAGMENTS,
    )


__all__ = [
    "DOCUMENT_ADAPTER_ALLOWED_OUTPUT_FIELDS",
    "DOCUMENT_ADAPTER_CAPABILITY_LABELS",
    "DOCUMENT_ADAPTER_CONTRACT_VERSION",
    "DOCUMENT_ADAPTER_KIND",
    "DOCUMENT_FIXTURE_ADAPTER_ID",
    "DocumentAdapterOutputValidationResult",
    "MetadataOnlyDocumentAdapter",
    "document_adapter_real_mode_readiness_gate",
    "document_fixture_adapter_status",
    "rejected_document_adapter_output",
    "sanitize_document_adapter_output",
    "validate_document_adapter_output",
]
