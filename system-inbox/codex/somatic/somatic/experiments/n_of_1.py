"""N-of-1 experiment designer: own-baseline return-to-baseline tracking.

Uses the insights engine's z-score math on the user's own timestamped series.
No retrieval, no population medical normals.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from somatic.analysis.statistics import descriptive_stats
from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT
from somatic.ingest.packet import Reading, normalize_observed_at, reading_from_dict
from somatic.insights.engine import grade_metric
from somatic.safety.core import (
    EMERGENCY_GUIDANCE,
    INFORMATIONAL_NOTICE,
    PROFESSIONAL_ROUTING,
    AdvisoryResult,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
    require_consent,
)

TOWARD_BASELINE = "toward_baseline"
AWAY_FROM_BASELINE = "away_from_baseline"
STABLE = "stable"
AWAITING_FOLLOWUP = "awaiting_followup"
INSUFFICIENT_BASELINE = "insufficient_baseline"
SPREAD_TOO_SMALL = "baseline_spread_too_small"

_Z_MOVE_EPS = 0.25


@dataclass(frozen=True)
class InterventionTag:
    """User-authored tag for a personal experiment. Not a treatment plan."""

    name: str
    metric: str
    started_at: str
    ended_at: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "metric": self.metric,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "note": self.note,
        }


@dataclass(frozen=True)
class ExperimentReport:
    """Informational n-of-1 comparison against the user's own pre-tag baseline."""

    tag: InterventionTag
    movement: str
    baseline_n: int
    followup_n: int
    result: AdvisoryResult
    notes: tuple[str, ...]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tag": self.tag.to_dict(),
            "movement": self.movement,
            "baseline_n": self.baseline_n,
            "followup_n": self.followup_n,
            "result": self.result.to_dict(),
            "notes": list(self.notes),
            "generated_at": self.generated_at,
        }


def evaluate_n_of_1(
    ledger: ConsentLedger,
    data_packet: dict[str, Any],
    *,
    metric: str,
    started_at: str,
    name: str = "untagged-interval",
    ended_at: str = "",
    note: str = "",
) -> ExperimentReport:
    """Compare post-tag readings to the user's own pre-tag baseline.

    Requires ``ANALYSIS_INSIGHT``. Emergency-screens the tag text first.
    """

    require_consent(ledger, ANALYSIS_INSIGHT)
    metric_name = str(metric).strip()
    if not metric_name:
        raise ValueError("metric is required")
    started = normalize_observed_at(started_at)
    ended = normalize_observed_at(ended_at) if str(ended_at or "").strip() else ""
    tag = InterventionTag(
        name=str(name or "untagged-interval").strip() or "untagged-interval",
        metric=metric_name,
        started_at=started,
        ended_at=ended,
        note=str(note or "").strip(),
    )
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    screen = emergency_screen(f"{tag.name}\n{tag.note}\n{metric_name}")
    if screen.triggered:
        return ExperimentReport(
            tag=tag,
            movement=INSUFFICIENT_BASELINE,
            baseline_n=0,
            followup_n=0,
            result=AdvisoryResult(
                summary=screen.guidance or EMERGENCY_GUIDANCE,
                evidence_grade=EvidenceGrade.NONE,
                sources=("emergency-screen", "n-of-1"),
                professional_routing=PROFESSIONAL_ROUTING,
                informational_notice=INFORMATIONAL_NOTICE,
                consent_scope="emergency-screen",
            ),
            notes=("emergency screen triggered; experiment comparison stopped",),
            generated_at=generated_at,
        )

    readings = _readings_for_metric(data_packet, metric_name)
    baseline = [item for item in readings if item.observed_at < started]
    followup = [item for item in readings if item.observed_at >= started]
    if ended:
        followup = [item for item in followup if item.observed_at <= ended]
    notes: list[str] = []
    if len(readings) != len(baseline) + len(followup) and not ended:
        notes.append("some readings were not ordered relative to the tag timestamp")

    if len(baseline) < 2:
        result = _frame_experiment(
            f"Fewer than two pre-tag readings were available for {metric_name} "
            f"(baseline n={len(baseline)}), so return-to-baseline could not be "
            f"estimated against your own series."
        )
        return ExperimentReport(
            tag=tag,
            movement=INSUFFICIENT_BASELINE,
            baseline_n=len(baseline),
            followup_n=len(followup),
            result=result,
            notes=tuple(notes),
            generated_at=generated_at,
        )
    if not followup:
        result = _frame_experiment(
            f"No post-tag readings were available yet for {metric_name} after "
            f"{started}. The tagged interval is recorded against your own series "
            f"only; this is not a treatment plan."
        )
        return ExperimentReport(
            tag=tag,
            movement=AWAITING_FOLLOWUP,
            baseline_n=len(baseline),
            followup_n=0,
            result=result,
            notes=tuple(notes),
            generated_at=generated_at,
        )

    latest = followup[-1]
    graded = grade_metric(
        ledger,
        metric_name,
        latest.value,
        baseline_values=[item.value for item in baseline],
        observed_at=latest.observed_at,
    )
    first_z = _z_score(followup[0].value, [item.value for item in baseline])
    last_z = _z_score(latest.value, [item.value for item in baseline])
    movement = _movement_label(first_z, last_z)
    movement_text = _movement_sentence(movement, metric_name, tag.name, started)
    summary = f"{graded.summary} {movement_text}"
    combined = _frame_experiment(
        summary,
        evidence_grade=graded.evidence_grade,
        sources=list(graded.sources) + ["n-of-1", f"movement:{movement}"],
    )
    if len(baseline) < 6:
        notes.append(
            f"pre-tag baseline n={len(baseline)} is a small personal series; "
            "z-scores are descriptive of your own readings only"
        )
    return ExperimentReport(
        tag=tag,
        movement=movement,
        baseline_n=len(baseline),
        followup_n=len(followup),
        result=combined,
        notes=tuple(notes),
        generated_at=generated_at,
    )


def _frame_experiment(
    summary: str,
    *,
    evidence_grade: str = EvidenceGrade.PRELIMINARY,
    sources: list[str] | None = None,
) -> AdvisoryResult:
    return frame_advisory(
        summary=summary,
        evidence_grade=evidence_grade,
        sources=tuple(sources or ("n-of-1", "personal-insights")),
        consent_scope=ANALYSIS_INSIGHT,
        authoritative_scan=False,
    )


def _movement_label(first_z: float | None, last_z: float | None) -> str:
    if first_z is None or last_z is None:
        return SPREAD_TOO_SMALL
    delta = abs(last_z) - abs(first_z)
    if delta <= -_Z_MOVE_EPS:
        return TOWARD_BASELINE
    if delta >= _Z_MOVE_EPS:
        return AWAY_FROM_BASELINE
    return STABLE


def _movement_sentence(movement: str, metric: str, name: str, started: str) -> str:
    interval = f"tagged interval '{name}' starting {started}"
    if movement == TOWARD_BASELINE:
        return (
            f"Across the {interval}, later {metric} readings are closer to your "
            f"own pre-tag baseline than the first post-tag reading. "
            f"This is informational only and is not evidence that an intervention worked."
        )
    if movement == AWAY_FROM_BASELINE:
        return (
            f"Across the {interval}, later {metric} readings are further from your "
            f"own pre-tag baseline than the first post-tag reading. "
            f"This is informational only and is not a diagnosis."
        )
    if movement == SPREAD_TOO_SMALL:
        return (
            f"Pre-tag {metric} spread was too small for a z-score movement "
            f"estimate on the {interval}."
        )
    return (
        f"Across the {interval}, {metric} distance from your own pre-tag "
        f"baseline did not change enough to call a direction."
    )


def _z_score(value: float, baseline: list[float]) -> float | None:
    stats = descriptive_stats(baseline)
    mean = stats["mean"]
    stdev = stats["stdev"]
    if mean is None or stdev is None or float(stdev) == 0:
        return None
    return (float(value) - float(mean)) / float(stdev)


def _readings_for_metric(data_packet: dict[str, Any], metric: str) -> list[Reading]:
    metrics = data_packet
    if data_packet.get("schema") == "somatic.packet.v1" and isinstance(
        data_packet.get("metrics"), dict
    ):
        metrics = data_packet["metrics"]
    raw = metrics.get(metric)
    if raw is None:
        return []
    if not isinstance(raw, list):
        raw = [raw]
    readings: list[Reading] = []
    for item in raw:
        if isinstance(item, dict):
            payload = dict(item)
            payload.setdefault("metric", metric)
            readings.append(reading_from_dict(payload))
            continue
        raise ValueError(
            "n-of-1 requires timestamped readings "
            "(objects with value and observed_at), not bare numbers"
        )
    readings.sort(key=lambda item: item.observed_at)
    return readings
