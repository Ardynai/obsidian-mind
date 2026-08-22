"""Fixture-only document evidence provider.

Phase 10A non-sensor evidence domain.  Reads small checked-in JSON fixture
files containing document count/status metadata and emits a deterministic
sanitized evidence pack.  No raw document bodies, private refs, absolute
paths, URLs, credentials, or source IDs are exported.
"""

import json
from collections.abc import Mapping
from pathlib import Path

from .document_adapter import (
    DOCUMENT_ADAPTER_CAPABILITY_LABELS,
    DOCUMENT_ADAPTER_CONTRACT_VERSION,
    DOCUMENT_ADAPTER_KIND,
    document_fixture_adapter_status,
    validate_document_adapter_output,
)
from .document_evidence_pack import build_document_evidence_pack

DOCUMENT_FIXTURE_PROVIDER_ID = "somatic-document-fixture-provider-v1"
DOCUMENT_FIXTURE_PROVIDER_CONTRACT_VERSION = 1
DOCUMENT_FIXTURE_INPUT_KIND = "document-fixture-metadata"
DOCUMENT_FIXTURE_INPUT_KINDS = (
    DOCUMENT_FIXTURE_INPUT_KIND,
    "document-fixture-files",
)
DOCUMENT_FIXTURE_BASE = Path("fixtures") / "evidence" / "document"
DEFAULT_DOCUMENT_FIXTURE_REFS = ("document-parsed.json",)
MAX_DOCUMENT_FIXTURE_REFS = 3
MAX_DOCUMENT_ENTRIES = 64


class DocumentFixtureEvidenceProvider:
    """Reads local JSON document fixtures and returns sanitized pack metadata."""

    provider_id = DOCUMENT_FIXTURE_PROVIDER_ID

    def status(self) -> dict[str, object]:
        adapter_status = document_fixture_adapter_status()
        return {
            "provider_id": self.provider_id,
            "contract_version": DOCUMENT_FIXTURE_PROVIDER_CONTRACT_VERSION,
            "mode": "fixture-only",
            "adapter_kind": DOCUMENT_ADAPTER_KIND,
            "adapter_contract_version": DOCUMENT_ADAPTER_CONTRACT_VERSION,
            "adapter_boundary_labels": list(DOCUMENT_ADAPTER_CAPABILITY_LABELS),
            "adapter_status": adapter_status,
            "real_mode_readiness_gate": adapter_status["real_mode_readiness_gate"],
            "real_mode_readiness_status": adapter_status["real_mode_readiness_status"],
            "real_mode_execution_permitted": False,
            "metadata_only": True,
            "fixture_only": True,
            "offline": True,
            "mock": True,
            "fail_closed_output_validation": True,
            "hardware_access": False,
            "network_calls": False,
            "live_capture": False,
        }

    def evidence_pack(
        self,
        fixture_refs,
        *,
        repo_root: str | Path,
        artifact_refs: dict[str, object] | None = None,
        artifact_hashes: dict[str, object] | None = None,
    ) -> dict[str, object]:
        evaluation = evaluate_document_fixture_refs(
            fixture_refs,
            repo_root=repo_root,
        )
        adapter_validation = validate_document_adapter_output(evaluation)
        return build_document_evidence_pack(
            fixture_evaluation=adapter_validation.sanitized_output,
            adapter_output_validation=adapter_validation,
            artifact_refs=artifact_refs,
            artifact_hashes=artifact_hashes,
        )


def evaluate_document_fixture_refs(
    fixture_refs,
    *,
    repo_root: str | Path,
) -> dict[str, object]:
    """Evaluate document fixture refs and return sanitized count/status metadata."""
    refs = _fixture_ref_tuple(fixture_refs)
    if not refs:
        refs = DEFAULT_DOCUMENT_FIXTURE_REFS
    refs = refs[:MAX_DOCUMENT_FIXTURE_REFS]
    status_counts: dict[str, int] = {"parsed": 0, "partial": 0, "rejected": 0}
    categories: dict[str, int] = {}
    quality_total = 0
    document_count = 0
    accepted_refs = 0
    total_word_count = 0
    total_line_count = 0
    total_char_count = 0
    formats: set[str] = set()

    for ref in refs:
        safe_name = _safe_fixture_name(ref)
        if not safe_name:
            status_counts["rejected"] += 1
            _increment(categories, "unsafe-ref")
            continue
        path = Path(repo_root) / DOCUMENT_FIXTURE_BASE / safe_name
        try:
            path.resolve().relative_to((Path(repo_root) / DOCUMENT_FIXTURE_BASE).resolve())
        except ValueError:
            status_counts["rejected"] += 1
            _increment(categories, "unsafe-ref")
            continue
        if not path.exists():
            status_counts["rejected"] += 1
            _increment(categories, "missing-ref")
            continue
        accepted_refs += 1
        parsed = _read_fixture_documents(path)
        document_count += parsed["document_count"]
        quality_total += parsed["quality_total"]
        total_word_count += parsed["total_word_count"]
        total_line_count += parsed["total_line_count"]
        total_char_count += parsed["total_char_count"]
        formats.update(parsed["formats"])
        for s, count in parsed["status_counts"].items():
            status_counts[s] += count
        for category, count in parsed["parse_error_categories"].items():
            _increment(categories, category, count)

    status = _aggregate_status(status_counts, document_count)
    evidence_quality = quality_total // document_count if document_count else 0
    if status == "rejected":
        evidence_quality = 0
    return {
        "status": status,
        "fixture_count": accepted_refs,
        "document_count": document_count,
        "total_word_count": total_word_count,
        "total_line_count": total_line_count,
        "total_char_count": total_char_count,
        "format_count": len(formats),
        "status_counts": status_counts,
        "parse_error_categories": dict(sorted(categories.items())),
        "error_count": status_counts["rejected"],
        "warning_count": status_counts["partial"],
        "evidence_quality": evidence_quality,
        "replay_integrity": 100 if status == "parsed" else evidence_quality,
    }


def _read_fixture_documents(path: Path) -> dict[str, object]:
    """Read a single JSON fixture file and extract sanitized metadata."""
    status_counts: dict[str, int] = {"parsed": 0, "partial": 0, "rejected": 0}
    categories: dict[str, int] = {}
    document_count = 0
    quality_total = 0
    total_word_count = 0
    total_line_count = 0
    total_char_count = 0
    formats: set[str] = set()
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        _increment(categories, "invalid-json")
        return {
            "document_count": 0,
            "quality_total": 0,
            "total_word_count": 0,
            "total_line_count": 0,
            "total_char_count": 0,
            "formats": set(),
            "status_counts": dict(status_counts, rejected=1),
            "parse_error_categories": categories,
        }

    if not isinstance(data, Mapping):
        _increment(categories, "invalid-structure")
        return {
            "document_count": 0,
            "quality_total": 0,
            "total_word_count": 0,
            "total_line_count": 0,
            "total_char_count": 0,
            "formats": set(),
            "status_counts": dict(status_counts, rejected=1),
            "parse_error_categories": categories,
        }

    documents = data.get("documents")
    if not isinstance(documents, list):
        _increment(categories, "missing-documents-key")
        return {
            "document_count": 0,
            "quality_total": 0,
            "total_word_count": 0,
            "total_line_count": 0,
            "total_char_count": 0,
            "formats": set(),
            "status_counts": dict(status_counts, rejected=1),
            "parse_error_categories": categories,
        }

    for entry in documents:
        if document_count >= MAX_DOCUMENT_ENTRIES:
            break
        if not isinstance(entry, Mapping):
            status_counts["rejected"] += 1
            _increment(categories, "invalid-entry")
            document_count += 1
            continue
        doc_status = str(entry.get("status", "")).lower()
        if doc_status not in ("parsed", "partial", "rejected"):
            doc_status = "rejected"
            _increment(categories, "invalid-status")
        status_counts[doc_status] = status_counts.get(doc_status, 0) + 1
        document_count += 1
        word_count = _int(entry.get("word_count"))
        line_count = _int(entry.get("line_count"))
        char_count = _int(entry.get("char_count"))
        doc_format = _safe_format(entry.get("format"))
        if doc_status == "parsed":
            quality_total += 100
        elif doc_status == "partial":
            quality_total += 50
        total_word_count += word_count
        total_line_count += line_count
        total_char_count += char_count
        if doc_format:
            formats.add(doc_format)

    return {
        "document_count": document_count,
        "quality_total": quality_total,
        "total_word_count": total_word_count,
        "total_line_count": total_line_count,
        "total_char_count": total_char_count,
        "formats": formats,
        "status_counts": status_counts,
        "parse_error_categories": categories,
    }


def _aggregate_status(status_counts: dict[str, int], total: int) -> str:
    if total <= 0:
        return "rejected"
    if status_counts.get("rejected", 0) > 0 or status_counts.get("partial", 0) > 0:
        if status_counts.get("parsed", 0) > 0:
            return "partial"
        return "rejected"
    return "parsed"


def _safe_fixture_name(ref: object) -> str:
    text = str(ref or "").strip()
    if not text:
        return ""
    if "/" in text or "\\" in text:
        return ""
    if text.startswith("."):
        return ""
    if ":" in text:
        return ""
    if any(char in text for char in ("*", "?", "<", ">", "|", '"', "'")):
        return ""
    return text


def _safe_format(value: object) -> str:
    text = str(value or "").lower().strip()
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "" for char in text)
    return safe[:32] if safe else ""


def _fixture_ref_tuple(refs: object) -> tuple[str, ...]:
    if isinstance(refs, str):
        return (refs,)
    if isinstance(refs, (list, tuple)):
        return tuple(str(ref) for ref in refs if ref)
    return ()


def _increment(categories: dict[str, int], key: str, count: int = 1) -> None:
    categories[key] = categories.get(key, 0) + count


def _int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


__all__ = [
    "DEFAULT_DOCUMENT_FIXTURE_REFS",
    "DOCUMENT_FIXTURE_BASE",
    "DOCUMENT_FIXTURE_INPUT_KIND",
    "DOCUMENT_FIXTURE_INPUT_KINDS",
    "DOCUMENT_FIXTURE_PROVIDER_CONTRACT_VERSION",
    "DOCUMENT_FIXTURE_PROVIDER_ID",
    "DocumentFixtureEvidenceProvider",
    "MAX_DOCUMENT_ENTRIES",
    "MAX_DOCUMENT_FIXTURE_REFS",
    "evaluate_document_fixture_refs",
]
