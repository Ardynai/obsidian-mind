from .csi_formats import (
    CSI_PARSER_BOUNDARY_FALSE_FLAGS,
    CSI_PARSER_BOUNDARY_TRUE_FLAGS,
    CSI_PARSER_CONTRACT_VERSION,
    CSI_PARSER_ID,
)

CSI_EVIDENCE_SCORER_ID = "somatic-csi-evidence-scorer-v1"
CSI_EVIDENCE_SCORING_CONTRACT_VERSION = 1
CSI_SCORING_SUPPORTED_FORMAT_COUNT = 3
CSI_SCORING_STATUS_VOCABULARY = ("parsed", "partial", "rejected")


def score_csi_replay_evidence(
    report_payload: dict[str, object],
    summary_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    """Score sanitized CSI replay metadata without reading frame or sample values."""
    summary_payload = summary_payload or {}
    status_counts = _status_counts(report_payload)
    fixture_count = _int(report_payload.get("fixture_count"))
    frame_count = _int(report_payload.get("frame_count"))
    sample_count = _int(report_payload.get("sample_count"))
    malformed_rows = _int(report_payload.get("malformed_rows"))
    parse_error_count = len(_list(report_payload.get("parse_errors")))
    warning_count = len(_list(report_payload.get("warnings")))
    error_count = len(_list(report_payload.get("errors")))
    source_formats = sorted(
        str(item)
        for item in _list(
            summary_payload.get("source_formats") or report_payload.get("source_formats")
        )
    )
    supported_format_count = len([name for name in source_formats if name.startswith("csi-")])
    unsupported_format_count = len(source_formats) - supported_format_count
    format_coverage_ratio = round(
        min(supported_format_count, CSI_SCORING_SUPPORTED_FORMAT_COUNT)
        / CSI_SCORING_SUPPORTED_FORMAT_COUNT,
        3,
    )
    parsed_count = status_counts["parsed"]
    partial_count = status_counts["partial"]
    rejected_count = status_counts["rejected"]
    score = _bounded_score(
        fixture_count=fixture_count,
        frame_count=frame_count,
        partial_count=partial_count,
        rejected_count=rejected_count,
        parse_error_count=parse_error_count,
        warning_count=warning_count,
        unsupported_format_count=unsupported_format_count,
    )
    scoring_status = _scoring_status(
        aggregate_status=str(report_payload.get("status", "rejected")),
        frame_count=frame_count,
        partial_count=partial_count,
        rejected_count=rejected_count,
    )
    payload = {
        "schema_version": 1,
        "contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
        "id": "csi-evidence-scoring",
        "scorer_id": CSI_EVIDENCE_SCORER_ID,
        "parser_id": str(report_payload.get("parser_id") or CSI_PARSER_ID),
        "input_contract_version": int(
            report_payload.get("contract_version") or CSI_PARSER_CONTRACT_VERSION
        ),
        "status": scoring_status,
        "parser_status": str(report_payload.get("status", "rejected")),
        "score": score,
        "score_scale": "0-100",
        "evidence_quality": score,
        "replay_integrity": score,
        "bounded": True,
        "explainable": True,
        "fixture_count": fixture_count,
        "status_counts": dict(status_counts),
        "parsed_count": parsed_count,
        "partial_count": partial_count,
        "rejected_count": rejected_count,
        "frame_count": frame_count,
        "sample_count": sample_count,
        "malformed_rows": malformed_rows,
        "error_count": error_count,
        "parse_error_count": parse_error_count,
        "warning_count": warning_count,
        "source_formats": source_formats,
        "supported_format_count": supported_format_count,
        "unsupported_format_count": unsupported_format_count,
        "format_coverage_ratio": format_coverage_ratio,
        "score_basis": [
            "starts at 100 for sanitized fixture replay metadata",
            f"partial fixtures: {partial_count}",
            f"rejected fixtures: {rejected_count}",
            f"parse error count: {parse_error_count}",
            f"warning count: {warning_count}",
            f"unsupported format count: {unsupported_format_count}",
        ],
        "interpretation": (
            "Deterministic replay metadata quality only; no signal processing "
            "output and no medical or clinical claim."
        ),
        "scoring_inputs": [
            "parser status",
            "fixture count",
            "fixture status counts",
            "frame count",
            "sample count",
            "malformed row count",
            "error count",
            "parse error count",
            "warning count",
            "format coverage",
            "parser contract version",
        ],
        "raw_signal_values_exported": False,
    }
    payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return payload


def build_csi_tournament_readiness(
    scoring_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    payload = {
        "schema_version": 1,
        "contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
        "id": "csi-evidence-tournament-readiness",
        "scorer_id": CSI_EVIDENCE_SCORER_ID,
        "status": "not-configured",
        "metadata_only": True,
        "core_tournament_scores_modified": False,
        "ranking_input": False,
        "requires_sanitized_replay_metadata": True,
        "accepted_score_fields": ["evidence_quality", "replay_integrity"],
        "score_scale": "0-100",
        "fixture_only": True,
        "summary_output_only": True,
        "raw_signal_values_exported": False,
        "hardware_access": False,
        "network_calls": False,
        "medical_or_clinical_claim": False,
        "notes": [
            "Tournament readiness accepts sanitized CSI evidence scoring metadata only.",
            "CSI evidence scoring is not a core tournament ranking dimension.",
        ],
    }
    if scoring_payload:
        payload.update(
            {
                "status": str(scoring_payload.get("status", "metadata-ready")),
                "evidence_quality": _score_int(scoring_payload.get("evidence_quality", 0)),
                "replay_integrity": _score_int(scoring_payload.get("replay_integrity", 0)),
                "parser_status": str(scoring_payload.get("parser_status", "unknown")),
            }
        )
    payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return payload


def _status_counts(report_payload: dict[str, object]) -> dict[str, int]:
    counts = {status: 0 for status in CSI_SCORING_STATUS_VOCABULARY}
    fixtures = _list(report_payload.get("fixtures"))
    if fixtures:
        for fixture in fixtures:
            status = (
                str(fixture.get("status", "rejected")) if isinstance(fixture, dict) else "rejected"
            )
            if status not in counts:
                status = "rejected"
            counts[status] += 1
        return counts
    status = str(report_payload.get("status", "rejected"))
    if status not in counts:
        status = "rejected"
    counts[status] = _int(report_payload.get("fixture_count"), default=1)
    return counts


def _bounded_score(
    *,
    fixture_count: int,
    frame_count: int,
    partial_count: int,
    rejected_count: int,
    parse_error_count: int,
    warning_count: int,
    unsupported_format_count: int,
) -> int:
    if fixture_count <= 0 or frame_count <= 0:
        return 0
    score = (
        100
        - partial_count * 15
        - rejected_count * 35
        - parse_error_count * 5
        - warning_count * 2
        - unsupported_format_count * 10
    )
    return max(0, min(100, int(score)))


def _scoring_status(
    *,
    aggregate_status: str,
    frame_count: int,
    partial_count: int,
    rejected_count: int,
) -> str:
    if aggregate_status == "rejected" or frame_count <= 0:
        return "rejected"
    if partial_count or rejected_count or aggregate_status == "partial":
        return "partial"
    return "parsed"


def _list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _score_int(value: object) -> int:
    return max(0, min(100, _int(value)))


__all__ = [
    "CSI_EVIDENCE_SCORER_ID",
    "CSI_EVIDENCE_SCORING_CONTRACT_VERSION",
    "build_csi_tournament_readiness",
    "score_csi_replay_evidence",
]
