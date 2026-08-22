"""Consent-gated end-to-end analyze flow.

Runs emergency screening, optional deterministic insights, and an optional AI
read behind explicit consent scopes. Stdlib only.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from somatic.advisory.adapter import (
    AdvisoryConfigError,
    AdvisoryHttpError,
    AdvisoryModelClient,
    AdvisoryModelConfig,
)
from somatic.analysis.statistics import to_float
from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import AI_ADVISORY, ANALYSIS_INSIGHT
from somatic.insights.engine import ReferenceRange, grade_metric, summarize_series
from somatic.safety.core import (
    EMERGENCY_GUIDANCE,
    INFORMATIONAL_NOTICE,
    PROFESSIONAL_ROUTING,
    AdvisoryFramingError,
    AdvisoryResult,
    EvidenceGrade,
    emergency_screen,
)


@dataclass(frozen=True)
class AnalysisReport:
    """Aggregated informational advisory results and skip notes."""

    results: tuple[AdvisoryResult, ...]
    notes: tuple[str, ...]
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "results": [result.to_dict() for result in self.results],
            "notes": list(self.notes),
            "generated_at": self.generated_at,
        }


def _utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def analyze_user_data(
    ledger: ConsentLedger,
    data_packet: dict[str, Any],
    question: str,
    *,
    references: Mapping[str, Any] | None = None,
    baselines: Mapping[str, Any] | None = None,
    model_config: AdvisoryModelConfig | None = None,
) -> AnalysisReport:
    """Run the consent-gated analyze spine over a user's own data packet."""

    if not isinstance(data_packet, dict):
        raise TypeError("data_packet must be a dict")
    packet_json = json.dumps(data_packet, sort_keys=True, ensure_ascii=False, default=str)
    screen_text = f"{question}\n{packet_json}"
    emergency = emergency_screen(screen_text)
    generated_at = _utc_now_iso()
    if emergency.triggered:
        return AnalysisReport(
            results=(
                AdvisoryResult(
                    summary=emergency.guidance or EMERGENCY_GUIDANCE,
                    evidence_grade=EvidenceGrade.NONE,
                    sources=("emergency-screen", "analyze-flow"),
                    professional_routing=PROFESSIONAL_ROUTING,
                    informational_notice=INFORMATIONAL_NOTICE,
                    consent_scope="emergency-screen",
                ),
            ),
            notes=("emergency screen triggered; further analysis stopped",),
            generated_at=generated_at,
        )

    results: list[AdvisoryResult] = []
    notes: list[str] = []
    working_packet, packet_notes = _unwrap_data_packet(data_packet)
    notes.extend(packet_notes)
    reference_map, reference_notes = _normalize_references(references)
    baseline_map, baseline_notes = _normalize_baselines(baselines)
    notes.extend(reference_notes)
    notes.extend(baseline_notes)

    if ledger.is_granted(ANALYSIS_INSIGHT):
        insight_results, insight_notes = _run_insights(
            ledger,
            working_packet,
            reference_map=reference_map,
            baseline_map=baseline_map,
        )
        results.extend(insight_results)
        notes.extend(insight_notes)
        if not any(
            source.startswith("personal-insights")
            for result in results
            for source in result.sources
        ):
            notes.append("insights: no numeric metrics with a provided reference or baseline")
    else:
        notes.append("insights skipped: consent not granted")

    if ledger.is_granted(AI_ADVISORY) and model_config is not None:
        try:
            client = AdvisoryModelClient(model_config)
            results.append(client.analyze(ledger, working_packet, question))
        except (AdvisoryConfigError, AdvisoryHttpError) as exc:
            notes.append(f"AI read unavailable: {exc}")
    elif not ledger.is_granted(AI_ADVISORY):
        notes.append("AI read skipped: consent not granted")
    else:
        notes.append("AI read skipped: no model_config provided")

    return AnalysisReport(
        results=tuple(results),
        notes=tuple(notes),
        generated_at=generated_at,
    )


def _run_insights(
    ledger: ConsentLedger,
    data_packet: dict[str, Any],
    *,
    reference_map: dict[str, ReferenceRange],
    baseline_map: dict[str, list[float]],
) -> tuple[list[AdvisoryResult], list[str]]:
    results: list[AdvisoryResult] = []
    notes: list[str] = []
    graded_metrics: set[str] = set()

    for metric, value in data_packet.items():
        metric_name = str(metric)
        reference = reference_map.get(metric_name)
        baseline = baseline_map.get(metric_name)
        series, series_note, observed_ats = _as_numeric_series(value)
        if series_note:
            notes.append(f"{metric_name}: {series_note}")

        if series is not None and len(series) >= 2:
            summarized = _safe_insight(
                summarize_series,
                ledger,
                metric_name,
                series,
                observed_ats=observed_ats,
            )
            if summarized is not None:
                results.append(summarized)
            latest = series[-1]
            latest_observed = ""
            if observed_ats:
                latest_observed = str(observed_ats[-1] or "").strip()
            if reference is not None or baseline is not None:
                graded = _safe_insight(
                    grade_metric,
                    ledger,
                    metric_name,
                    latest,
                    reference=reference,
                    baseline_values=baseline,
                    observed_at=latest_observed or None,
                )
                if graded is not None:
                    results.append(graded)
                    graded_metrics.add(metric_name)
            continue

        parsed = series[0] if series else to_float(value)
        if parsed is None:
            continue
        if reference is None and baseline is None:
            continue
        latest_observed = ""
        if observed_ats:
            latest_observed = str(observed_ats[-1] or "").strip()
        graded = _safe_insight(
            grade_metric,
            ledger,
            metric_name,
            parsed,
            reference=reference,
            baseline_values=baseline,
            observed_at=latest_observed or None,
        )
        if graded is None:
            continue
        results.append(graded)
        graded_metrics.add(metric_name)

    for metric_name, baseline in baseline_map.items():
        if metric_name in graded_metrics:
            continue
        if metric_name in data_packet:
            continue
        if len(baseline) >= 2:
            summarized = _safe_insight(summarize_series, ledger, metric_name, baseline)
            if summarized is not None:
                results.append(summarized)

    return results, notes


def _safe_insight(fn, *args, **kwargs):
    """Return ``fn(...)`` or None when engine text cannot be framed."""

    try:
        return fn(*args, **kwargs)
    except AdvisoryFramingError:
        return None


def _normalize_references(
    references: Mapping[str, Any] | None,
) -> tuple[dict[str, ReferenceRange], list[str]]:
    if not references:
        return {}, []
    normalized: dict[str, ReferenceRange] = {}
    notes: list[str] = []
    for key, payload in references.items():
        metric = str(key)
        if isinstance(payload, ReferenceRange):
            normalized[payload.metric or metric] = payload
            continue
        if not isinstance(payload, Mapping):
            notes.append(f"reference {metric}: skipped (not an object)")
            continue
        if "min" in payload or "max" in payload:
            notes.append(f"reference {metric}: use low/high (min/max is not accepted)")
            continue
        try:
            range_obj = ReferenceRange(
                metric=str(payload.get("metric", metric)),
                low=float(payload["low"]),
                high=float(payload["high"]),
                unit=str(payload.get("unit", "")),
                source=str(payload.get("source", "caller-provided")),
            )
        except (KeyError, TypeError, ValueError):
            notes.append(f"reference {metric}: malformed; skipped")
            continue
        normalized[range_obj.metric] = range_obj
    return normalized, notes


def _normalize_baselines(
    baselines: Mapping[str, Any] | None,
) -> tuple[dict[str, list[float]], list[str]]:
    if not baselines:
        return {}, []
    normalized: dict[str, list[float]] = {}
    notes: list[str] = []
    for key, payload in baselines.items():
        series, series_note, _observed = _as_numeric_series(payload)
        if series_note:
            notes.append(f"baseline {key}: {series_note}")
        if series is None or len(series) < 2:
            if series is not None and len(series) == 1:
                notes.append(f"baseline {key}: need at least two numeric readings")
            continue
        normalized[str(key)] = series
    return normalized, notes


def _unwrap_data_packet(
    data_packet: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if data_packet.get("schema") != "somatic.packet.v1":
        return data_packet, []
    metrics = data_packet.get("metrics")
    if not isinstance(metrics, dict):
        return {}, ["packet: somatic.packet.v1 missing metrics object"]
    notes = []
    extra = data_packet.get("notes")
    if isinstance(extra, list):
        notes.extend(str(item) for item in extra)
    return metrics, notes


def _as_numeric_series(
    value: object,
) -> tuple[list[float] | None, str | None, list[str]]:
    if isinstance(value, Mapping):
        if "value" in value:
            parsed = to_float(value.get("value"))
            if parsed is None:
                return None, None, []
            observed = str(value.get("observed_at") or "").strip()
            return [parsed], None, [observed]
        return None, "skipped (object is not a reading)", []
    if isinstance(value, (str, bytes)):
        parsed = to_float(value)
        return ([parsed], None, [""]) if parsed is not None else (None, None, [])
    if isinstance(value, Sequence):
        cleaned: list[float] = []
        observed_ats: list[str] = []
        dropped = 0
        for item in value:
            if isinstance(item, Mapping) and "value" in item:
                parsed = to_float(item.get("value"))
                observed = str(item.get("observed_at") or "").strip()
            else:
                parsed = to_float(item)
                observed = ""
            if parsed is None:
                dropped += 1
                continue
            cleaned.append(parsed)
            observed_ats.append(observed)
        note = f"dropped {dropped} non-numeric value(s)" if dropped else None
        if not cleaned:
            return None, note, []
        return cleaned, note, observed_ats
    parsed = to_float(value)
    if parsed is None:
        return None, None, []
    return [parsed], None, [""]
