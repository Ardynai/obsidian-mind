from .csi_formats import (
    CSI_PARSER_BOUNDARY_FALSE_FLAGS,
    CSI_PARSER_BOUNDARY_TRUE_FLAGS,
    CSI_PARSER_ID,
)
from .csi_scoring import (
    CSI_EVIDENCE_SCORER_ID,
    CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
)

CSI_BATCH_EVALUATOR_ID = "somatic-csi-batch-replay-evaluator-v1"
CSI_BATCH_EVALUATION_CONTRACT_VERSION = 1
CSI_BATCH_STATUS_VOCABULARY = ("parsed", "partial", "rejected")
CSI_BATCH_GROUP_INPUT_KIND = "csi-replay-evaluation-groups"
CSI_BATCH_MAX_GROUPS = 8
CSI_BATCH_MAX_REFS_PER_GROUP = 8


def evaluate_csi_replay_batch(
    fixture_groups,
    *,
    repo_root=None,
    provider=None,
) -> dict[str, object]:
    """Evaluate CSI fixture groups through sanitized provider replay metadata only."""
    if provider is None:
        from .sandbox import SandboxSensorProvider

        provider = SandboxSensorProvider()
    groups = _normalize_groups(fixture_groups)
    if len(groups) > CSI_BATCH_MAX_GROUPS:
        payload = _batch_payload(
            group_summaries=[],
            provider_id=str(getattr(provider, "provider_id", "sandbox-sensor-provider")),
            requested_group_count=len(groups),
            group_limit_exceeded=True,
        )
        payload["tournament_readiness"] = _readiness_reference(payload)
        return payload
    group_summaries = []
    for index, group_refs in enumerate(groups, start=1):
        if len(group_refs) > CSI_BATCH_MAX_REFS_PER_GROUP:
            group_summaries.append(_ref_limit_group_summary(index, len(group_refs)))
            continue
        replay = provider.replay_csi_fixtures(group_refs, repo_root=repo_root)
        group_summaries.append(_group_summary(index, replay))
    payload = _batch_payload(
        group_summaries=group_summaries,
        provider_id=str(getattr(provider, "provider_id", "sandbox-sensor-provider")),
        requested_group_count=len(groups),
    )
    payload["tournament_readiness"] = _readiness_reference(payload)
    return payload


def build_csi_batch_tournament_readiness(
    batch_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    payload = {
        "schema_version": 1,
        "contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
        "id": "csi-batch-tournament-readiness",
        "csi_batch_evaluation_contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
        "evaluator_id": CSI_BATCH_EVALUATOR_ID,
        "parser_id": CSI_PARSER_ID,
        "scorer_id": CSI_EVIDENCE_SCORER_ID,
        "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
        "status": "not-configured",
        "metadata_only": True,
        "core_tournament_scores_modified": False,
        "tournament_rankings_modified": False,
        "ranking_input": False,
        "requires_sanitized_replay_metadata": True,
        "accepted_score_fields": ["evidence_quality", "replay_integrity"],
        "score_scale": "0-100",
        "group_count": 0,
        "evaluated_group_count": 0,
        "rejected_group_count": 0,
        "max_group_count": CSI_BATCH_MAX_GROUPS,
        "max_refs_per_group": CSI_BATCH_MAX_REFS_PER_GROUP,
        "group_limit_exceeded": False,
        "ref_limit_exceeded": False,
        "aggregate_evidence_quality": 0,
        "aggregate_replay_integrity": 0,
        "group_summaries": [],
        "fixture_only": True,
        "summary_output_only": True,
        "raw_signal_values_exported": False,
        "notes": [
            "CSI batch replay readiness accepts sanitized fixture replay metadata only.",
            "CSI batch replay metadata is not a core tournament ranking dimension.",
        ],
    }
    if batch_payload:
        group_summaries = [
            dict(group) for group in _list(batch_payload.get("groups")) if isinstance(group, dict)
        ]
        payload.update(
            {
                "status": _status(batch_payload.get("status")),
                "group_count": _int(batch_payload.get("group_count")),
                "evaluated_group_count": _int(batch_payload.get("evaluated_group_count")),
                "parsed_group_count": _int(batch_payload.get("parsed_group_count")),
                "partial_group_count": _int(batch_payload.get("partial_group_count")),
                "rejected_group_count": _int(batch_payload.get("rejected_group_count")),
                "fixture_count": _int(batch_payload.get("fixture_count")),
                "status_counts": _status_count_dict(batch_payload.get("status_counts")),
                "group_status_counts": _status_count_dict(batch_payload.get("group_status_counts")),
                "aggregate_evidence_quality": _score_int(
                    batch_payload.get("aggregate_evidence_quality")
                ),
                "aggregate_replay_integrity": _score_int(
                    batch_payload.get("aggregate_replay_integrity")
                ),
                "score": _score_int(batch_payload.get("score")),
                "minimum_group_score": _score_int(batch_payload.get("minimum_group_score")),
                "average_group_score": _float(batch_payload.get("average_group_score")),
                "source_formats": sorted(
                    str(item) for item in _list(batch_payload.get("source_formats"))
                ),
                "aggregation_method": str(batch_payload.get("aggregation_method", "")),
                "max_group_count": _int(batch_payload.get("max_group_count")),
                "max_refs_per_group": _int(batch_payload.get("max_refs_per_group")),
                "group_limit_exceeded": bool(batch_payload.get("group_limit_exceeded")),
                "ref_limit_exceeded": bool(batch_payload.get("ref_limit_exceeded")),
                "group_summaries": group_summaries,
            }
        )
    payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return payload


def _normalize_groups(fixture_groups) -> list[tuple[str, ...]]:
    if fixture_groups is None:
        return []
    if isinstance(fixture_groups, dict):
        fixture_groups = fixture_groups.get("groups", [])
    if not isinstance(fixture_groups, (list, tuple)):
        return [tuple()]
    groups = []
    for item in fixture_groups:
        refs = _group_refs(item)
        groups.append(tuple(str(ref) for ref in refs))
    return groups


def _group_refs(item) -> tuple[object, ...]:
    if isinstance(item, dict):
        refs = item.get("refs")
        if refs is None:
            refs = item.get("fixture_refs")
        if refs is None:
            refs = item.get("items")
        return _refs_tuple(refs)
    return _refs_tuple(item)


def _refs_tuple(value) -> tuple[object, ...]:
    if value is None:
        return tuple()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return tuple()


def _group_summary(index: int, replay: dict[str, object]) -> dict[str, object]:
    scoring = dict(replay.get("csi_evidence_scoring", {}))
    status_counts = _status_count_dict(scoring.get("status_counts"))
    score = _score_int(scoring.get("score"))
    payload = {
        "schema_version": 1,
        "group_id": f"csi-fixture-group-{index:03d}",
        "status": _status(scoring.get("status") or replay.get("status")),
        "parser_status": _status(scoring.get("parser_status") or replay.get("status")),
        "fixture_count": _int(replay.get("fixture_count")),
        "source_formats": sorted(str(item) for item in _list(replay.get("source_formats"))),
        "frame_count": _int(replay.get("frame_count")),
        "sample_count": _int(replay.get("sample_count")),
        "malformed_rows": _int(replay.get("malformed_rows")),
        "status_counts": status_counts,
        "error_count": _int(scoring.get("error_count")),
        "parse_error_count": _int(scoring.get("parse_error_count")),
        "warning_count": _int(scoring.get("warning_count")),
        "score": score,
        "evidence_quality": _score_int(scoring.get("evidence_quality", score)),
        "replay_integrity": _score_int(scoring.get("replay_integrity", score)),
        "score_scale": "0-100",
        "scorer_id": CSI_EVIDENCE_SCORER_ID,
        "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
        "ref_limit_exceeded": False,
        "raw_signal_values_exported": False,
    }
    payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return payload


def _ref_limit_group_summary(index: int, ref_count: int) -> dict[str, object]:
    payload = {
        "schema_version": 1,
        "group_id": f"csi-fixture-group-{index:03d}",
        "status": "rejected",
        "parser_status": "rejected",
        "fixture_count": ref_count,
        "source_formats": [],
        "frame_count": 0,
        "sample_count": 0,
        "malformed_rows": 0,
        "status_counts": {"parsed": 0, "partial": 0, "rejected": ref_count},
        "error_count": 1,
        "parse_error_count": 1,
        "warning_count": 0,
        "score": 0,
        "evidence_quality": 0,
        "replay_integrity": 0,
        "score_scale": "0-100",
        "scorer_id": CSI_EVIDENCE_SCORER_ID,
        "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
        "ref_limit_exceeded": True,
        "raw_signal_values_exported": False,
    }
    payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return payload


def _batch_payload(
    *,
    group_summaries: list[dict[str, object]],
    provider_id: str,
    requested_group_count: int | None = None,
    group_limit_exceeded: bool = False,
) -> dict[str, object]:
    group_status_counts = {status: 0 for status in CSI_BATCH_STATUS_VOCABULARY}
    fixture_status_counts = {status: 0 for status in CSI_BATCH_STATUS_VOCABULARY}
    source_formats = set()
    scores = []
    for group in group_summaries:
        group_status_counts[_status(group.get("status"))] += 1
        for status, count in _status_count_dict(group.get("status_counts")).items():
            fixture_status_counts[status] += count
        source_formats.update(str(item) for item in _list(group.get("source_formats")))
        scores.append(_score_int(group.get("score")))
    evaluated_group_count = len(group_summaries)
    group_count = (
        requested_group_count if requested_group_count is not None else evaluated_group_count
    )
    if group_limit_exceeded:
        group_status_counts["rejected"] = group_count
    minimum_group_score = min(scores) if scores else 0
    average_group_score = (
        round(sum(scores) / evaluated_group_count, 3) if evaluated_group_count else 0.0
    )
    status = _batch_status(group_count, group_status_counts)
    ref_limit_exceeded = any(bool(group.get("ref_limit_exceeded")) for group in group_summaries)
    payload = {
        "schema_version": 1,
        "contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
        "csi_batch_evaluation_contract_version": CSI_BATCH_EVALUATION_CONTRACT_VERSION,
        "id": "csi-batched-fixture-replay-evaluation",
        "evaluator_id": CSI_BATCH_EVALUATOR_ID,
        "provider_id": provider_id,
        "mode": "fixture-replay-batch",
        "parser_id": CSI_PARSER_ID,
        "scorer_id": CSI_EVIDENCE_SCORER_ID,
        "scoring_contract_version": CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
        "status": status,
        "group_count": group_count,
        "evaluated_group_count": evaluated_group_count,
        "parsed_group_count": group_status_counts["parsed"],
        "partial_group_count": group_status_counts["partial"],
        "rejected_group_count": group_status_counts["rejected"],
        "max_group_count": CSI_BATCH_MAX_GROUPS,
        "max_refs_per_group": CSI_BATCH_MAX_REFS_PER_GROUP,
        "group_limit_exceeded": group_limit_exceeded,
        "ref_limit_exceeded": ref_limit_exceeded,
        "fixture_count": sum(_int(group.get("fixture_count")) for group in group_summaries),
        "status_counts": fixture_status_counts,
        "group_status_counts": group_status_counts,
        "frame_count": sum(_int(group.get("frame_count")) for group in group_summaries),
        "sample_count": sum(_int(group.get("sample_count")) for group in group_summaries),
        "malformed_rows": sum(_int(group.get("malformed_rows")) for group in group_summaries),
        "error_count": sum(_int(group.get("error_count")) for group in group_summaries),
        "parse_error_count": sum(_int(group.get("parse_error_count")) for group in group_summaries),
        "warning_count": sum(_int(group.get("warning_count")) for group in group_summaries),
        "source_formats": sorted(source_formats),
        "score": minimum_group_score,
        "score_scale": "0-100",
        "evidence_quality": minimum_group_score,
        "replay_integrity": minimum_group_score,
        "aggregate_evidence_quality": minimum_group_score,
        "aggregate_replay_integrity": minimum_group_score,
        "minimum_group_score": minimum_group_score,
        "average_group_score": average_group_score,
        "aggregation_method": "deterministic-min-score-with-summary-counts",
        "bounded": True,
        "explainable": True,
        "score_basis": [
            "runs each configured CSI fixture group through sandbox provider replay",
            "uses sanitized replay status/count/scoring metadata only",
            "batch score is the minimum group score to fail closed for readiness",
            f"group count: {group_count}",
            f"evaluated group count: {evaluated_group_count}",
            f"rejected group count: {group_status_counts['rejected']}",
        ],
        "groups": [dict(group) for group in group_summaries],
        "group_summaries": [dict(group) for group in group_summaries],
        "core_tournament_scores_modified": False,
        "tournament_rankings_modified": False,
        "ranking_input": False,
        "fixture_only": True,
        "summary_output_only": True,
        "raw_signal_values_exported": False,
    }
    payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return payload


def _batch_status(group_count: int, group_status_counts: dict[str, int]) -> str:
    if group_count <= 0:
        return "rejected"
    if group_status_counts["rejected"] == group_count:
        return "rejected"
    if group_status_counts["partial"] or group_status_counts["rejected"]:
        return "partial"
    return "parsed"


def _readiness_reference(batch_payload: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": _status(batch_payload.get("status")),
        "metadata_only": True,
        "core_tournament_scores_modified": False,
        "tournament_rankings_modified": False,
        "ranking_input": False,
        "aggregate_evidence_quality": _score_int(batch_payload.get("aggregate_evidence_quality")),
        "aggregate_replay_integrity": _score_int(batch_payload.get("aggregate_replay_integrity")),
        "group_count": _int(batch_payload.get("group_count")),
        "evaluated_group_count": _int(batch_payload.get("evaluated_group_count")),
        "rejected_group_count": _int(batch_payload.get("rejected_group_count")),
        "group_limit_exceeded": bool(batch_payload.get("group_limit_exceeded")),
        "ref_limit_exceeded": bool(batch_payload.get("ref_limit_exceeded")),
    }


def _status(value: object) -> str:
    status = str(value or "rejected")
    if status not in CSI_BATCH_STATUS_VOCABULARY:
        return "rejected"
    return status


def _status_count_dict(value: object) -> dict[str, int]:
    counts = {status: 0 for status in CSI_BATCH_STATUS_VOCABULARY}
    if isinstance(value, dict):
        for status in CSI_BATCH_STATUS_VOCABULARY:
            counts[status] = _int(value.get(status))
    return counts


def _list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _score_int(value: object) -> int:
    return max(0, min(100, _int(value)))


__all__ = [
    "CSI_BATCH_EVALUATION_CONTRACT_VERSION",
    "CSI_BATCH_EVALUATOR_ID",
    "CSI_BATCH_GROUP_INPUT_KIND",
    "CSI_BATCH_MAX_GROUPS",
    "CSI_BATCH_MAX_REFS_PER_GROUP",
    "build_csi_batch_tournament_readiness",
    "evaluate_csi_replay_batch",
]
