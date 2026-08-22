"""Consent-gated personal insights over a user's own numeric data.

Reference ranges are caller-supplied only. Baseline deviations use the user's
own history. This module never invents population medical normals.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from somatic.analysis.statistics import descriptive_stats, to_float
from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT
from somatic.safety.core import (
    AdvisoryResult,
    EvidenceGrade,
    frame_advisory,
    require_consent,
)


def _frame_insight(
    summary: str,
    evidence_grade: str,
    sources: tuple[str, ...] | list[str],
) -> AdvisoryResult:
    """Frame engine-authored text without the model-output denylist."""

    return frame_advisory(
        summary=summary,
        evidence_grade=evidence_grade,
        sources=sources,
        consent_scope=ANALYSIS_INSIGHT,
        authoritative_scan=False,
    )


WITHIN_REFERENCE = "within"
ABOVE_REFERENCE = "above"
BELOW_REFERENCE = "below"

TREND_RISING = "rising"
TREND_FALLING = "falling"
TREND_STABLE = "stable"

# Relative change below this fraction of series span is treated as stable.
_STABLE_RELATIVE_THRESHOLD = 0.05
# Absolute z-score at or above this flags a baseline deviation.
_BASELINE_OUTLIER_Z = 2.0


@dataclass(frozen=True)
class ReferenceRange:
    """Caller-supplied reference bounds for one metric.

    ``low`` and ``high`` must be provided by the caller or user. This type does
    not embed any population medical normals.
    """

    metric: str
    low: float
    high: float
    unit: str
    source: str

    def __post_init__(self) -> None:
        if not str(self.metric).strip():
            raise ValueError("ReferenceRange.metric must be non-empty")
        if not str(self.source).strip():
            raise ValueError("ReferenceRange.source must be non-empty")
        low = float(self.low)
        high = float(self.high)
        if not math.isfinite(low) or not math.isfinite(high):
            raise ValueError("ReferenceRange bounds must be finite")
        if low > high:
            raise ValueError("ReferenceRange.low must be <= high")
        object.__setattr__(self, "low", low)
        object.__setattr__(self, "high", high)
        object.__setattr__(self, "metric", str(self.metric).strip())
        object.__setattr__(self, "unit", str(self.unit))
        object.__setattr__(self, "source", str(self.source).strip())


def grade_metric(
    ledger: ConsentLedger,
    metric: str,
    value: float | int | str,
    *,
    reference: ReferenceRange | None = None,
    baseline_values: Sequence[float | int | str] | None = None,
    observed_at: str | None = None,
) -> AdvisoryResult:
    """Grade one reading against a provided reference and/or own baseline.

    Requires ``ANALYSIS_INSIGHT`` consent. All user-facing text is framed through
    :func:`~somatic.safety.core.frame_advisory`.
    """

    require_consent(ledger, ANALYSIS_INSIGHT)
    metric_name = str(metric).strip() or "metric"
    parsed = to_float(value)
    if parsed is None:
        return _frame_insight(
            summary=(
                f"No numeric value was available for {metric_name}, so no "
                f"informational comparison could be produced."
            ),
            evidence_grade=EvidenceGrade.NONE,
            sources=("personal-insights", f"metric:{metric_name}"),
        )
    if reference is None and baseline_values is None:
        raise ValueError("grade_metric requires a caller-provided reference and/or baseline_values")

    parts: list[str] = []
    sources: list[str] = ["personal-insights", f"metric:{metric_name}"]
    sample_strength = 1
    observed = str(observed_at or "").strip()
    if observed:
        parts.append(f"Recorded {observed}.")
        sources.append(f"observed:{observed}")

    if reference is not None:
        classification = _classify_against_reference(parsed, reference)
        unit_suffix = f" {reference.unit}".rstrip()
        if classification == ABOVE_REFERENCE:
            parts.append(
                f"Your {metric_name} value ({_fmt(parsed)}{unit_suffix}) is above "
                f"the reference range you provided "
                f"({_fmt(reference.low)}–{_fmt(reference.high)}{unit_suffix}; "
                f"source: {reference.source})."
            )
        elif classification == BELOW_REFERENCE:
            parts.append(
                f"Your {metric_name} value ({_fmt(parsed)}{unit_suffix}) is below "
                f"the reference range you provided "
                f"({_fmt(reference.low)}–{_fmt(reference.high)}{unit_suffix}; "
                f"source: {reference.source})."
            )
        else:
            parts.append(
                f"Your {metric_name} value ({_fmt(parsed)}{unit_suffix}) is within "
                f"the reference range you provided "
                f"({_fmt(reference.low)}–{_fmt(reference.high)}{unit_suffix}; "
                f"source: {reference.source})."
            )
        sources.append(f"reference-source:{reference.source}")

    if baseline_values is not None:
        baseline = _clean_series(baseline_values)
        sample_strength = max(sample_strength, len(baseline))
        if len(baseline) < 2:
            parts.append(
                f"Fewer than two baseline readings were available for {metric_name}, "
                f"so a personal baseline deviation could not be estimated."
            )
            sources.append("baseline:insufficient")
        else:
            stats = descriptive_stats(baseline)
            mean = stats["mean"]
            stdev = stats["stdev"]
            sources.append(f"baseline-n:{len(baseline)}")
            if mean is None or stdev is None or stdev == 0:
                median = stats["median"]
                if median is None:
                    parts.append(f"Baseline statistics for {metric_name} were unavailable.")
                else:
                    delta = parsed - float(median)
                    direction = "above" if delta > 0 else "below" if delta < 0 else "at"
                    parts.append(
                        f"Your {metric_name} value ({_fmt(parsed)}) is {direction} "
                        f"your own baseline median ({_fmt(median)}; n={len(baseline)}). "
                        f"Baseline spread was too small for a z-score estimate."
                    )
            else:
                z_score = (parsed - float(mean)) / float(stdev)
                abs_z = abs(z_score)
                reading = f"Your {metric_name} value ({_fmt(parsed)})"
                if abs_z >= _BASELINE_OUTLIER_Z:
                    parts.append(
                        f"{reading} is {_fmt(abs_z)} SD "
                        f"{'above' if z_score > 0 else 'below'} your own "
                        f"{metric_name} baseline (mean {_fmt(mean)}, "
                        f"n={len(baseline)}) — may be worth discussing with a "
                        f"licensed professional."
                    )
                else:
                    parts.append(
                        f"{reading} is within "
                        f"{_fmt(abs_z)} SD of your own baseline "
                        f"(mean {_fmt(mean)}, n={len(baseline)})."
                    )
                if len(baseline) < 6:
                    parts.append(
                        f"This z-score uses a small personal series "
                        f"(n={len(baseline)}) and is descriptive of your own "
                        f"readings only, not a population statistic."
                    )

    parts.append(
        "This is informational only and is not a diagnosis; confirm with a "
        "licensed professional if concerns remain."
    )
    grade = _evidence_grade_for_strength(sample_strength, has_signal=_has_signal(parts))
    return _frame_insight(
        summary=" ".join(parts),
        evidence_grade=grade,
        sources=tuple(sources),
    )


def summarize_series(
    ledger: ConsentLedger,
    metric: str,
    values: Sequence[float | int | str],
    *,
    observed_ats: Sequence[str] | None = None,
) -> AdvisoryResult:
    """Summarize trend and magnitude over the user's own series."""

    require_consent(ledger, ANALYSIS_INSIGHT)
    metric_name = str(metric).strip() or "metric"
    series = _clean_series(values)
    if len(series) < 2:
        return _frame_insight(
            summary=(
                f"Fewer than two numeric readings were available for {metric_name}, "
                f"so no trend summary could be produced."
            ),
            evidence_grade=EvidenceGrade.NONE,
            sources=("personal-insights", f"metric:{metric_name}", "series:insufficient"),
        )

    stats = descriptive_stats(series)
    trend, magnitude = _trend_and_magnitude(series)
    grade = (
        EvidenceGrade.MODERATE
        if len(series) >= 6 and trend != TREND_STABLE
        else EvidenceGrade.LIMITED
        if len(series) >= 3
        else EvidenceGrade.PRELIMINARY
    )
    dates = [str(item).strip() for item in (observed_ats or ()) if str(item).strip()]
    window = ""
    sources: list[str] = [
        "personal-insights",
        f"metric:{metric_name}",
        f"series-n:{len(series)}",
        f"trend:{trend}",
    ]
    if dates:
        window = f" from {dates[0]} to {dates[-1]}"
        sources.append(f"observed:{dates[0]}")
        if dates[-1] != dates[0]:
            sources.append(f"observed:{dates[-1]}")
    summary = (
        f"Over your own {metric_name} series (n={len(series)}, "
        f"latest {_fmt(series[-1])}, "
        f"min {_fmt(stats['min'])}, max {_fmt(stats['max'])}, "
        f"mean {_fmt(stats['mean'])}){window}, the trend appears {trend} "
        f"with a net change of {_fmt(magnitude)}. "
        f"This is informational only and may be worth discussing with a "
        f"licensed professional."
    )
    return _frame_insight(
        summary=summary,
        evidence_grade=grade,
        sources=tuple(sources),
    )


def _classify_against_reference(value: float, reference: ReferenceRange) -> str:
    if value > reference.high:
        return ABOVE_REFERENCE
    if value < reference.low:
        return BELOW_REFERENCE
    return WITHIN_REFERENCE


def _clean_series(values: Sequence[float | int | str]) -> list[float]:
    cleaned: list[float] = []
    for value in values:
        parsed = to_float(value)
        if parsed is not None:
            cleaned.append(parsed)
    return cleaned


def _trend_and_magnitude(series: list[float]) -> tuple[str, float]:
    first = series[0]
    last = series[-1]
    magnitude = last - first
    span = max(series) - min(series)
    if span == 0:
        return TREND_STABLE, 0.0
    relative = abs(magnitude) / span
    if relative < _STABLE_RELATIVE_THRESHOLD:
        return TREND_STABLE, round(magnitude, 6)
    if magnitude > 0:
        return TREND_RISING, round(magnitude, 6)
    return TREND_FALLING, round(magnitude, 6)


def _evidence_grade_for_strength(sample_strength: int, *, has_signal: bool) -> str:
    if sample_strength <= 1:
        return EvidenceGrade.PRELIMINARY
    if sample_strength >= 6 and has_signal:
        return EvidenceGrade.MODERATE
    if sample_strength >= 3:
        return EvidenceGrade.LIMITED
    return EvidenceGrade.PRELIMINARY


def _has_signal(parts: list[str]) -> bool:
    joined = " ".join(parts).lower()
    return any(
        token in joined
        for token in (
            "above the reference",
            "below the reference",
            "sd above",
            "sd below",
        )
    )


def _fmt(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.4g}"
