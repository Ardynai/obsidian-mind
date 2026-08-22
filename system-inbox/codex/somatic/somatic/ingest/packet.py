"""Timestamped personal-data packet produced by local importers.

Analyze accepts either legacy scalars/lists or lists of reading objects
with ``value`` and ``observed_at``. This module never invents medical normals.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class Reading:
    """One user-owned numeric observation with an ISO-8601 timestamp."""

    metric: str
    value: float
    observed_at: str
    unit: str = ""
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "value": self.value,
            "observed_at": self.observed_at,
            "unit": self.unit,
            "source": self.source,
        }


@dataclass(frozen=True)
class IngestedPacket:
    """Grouped readings plus importer notes."""

    readings: tuple[Reading, ...]
    notes: tuple[str, ...]
    source_kind: str

    def to_analyze_packet(self) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for reading in self.readings:
            grouped[reading.metric].append(
                {
                    "value": reading.value,
                    "observed_at": reading.observed_at,
                    "unit": reading.unit,
                    "source": reading.source,
                }
            )
        return {metric: rows for metric, rows in grouped.items()}

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "somatic.packet.v1",
            "source_kind": self.source_kind,
            "readings": [reading.to_dict() for reading in self.readings],
            "notes": list(self.notes),
            "metrics": self.to_analyze_packet(),
        }


def reading_from_dict(payload: dict[str, Any]) -> Reading:
    metric = str(payload.get("metric") or "").strip()
    if not metric:
        raise ValueError("reading.metric must be non-empty")
    value = parse_finite_value(payload["value"])
    observed_at = normalize_observed_at(str(payload.get("observed_at") or ""))
    return Reading(
        metric=metric,
        value=value,
        observed_at=observed_at,
        unit=str(payload.get("unit") or ""),
        source=str(payload.get("source") or ""),
    )


def parse_finite_value(raw: object) -> float:
    """Parse a numeric reading and reject NaN/inf."""

    try:
        value = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError("value is not numeric") from exc
    if not math.isfinite(value):
        raise ValueError("value must be a finite number")
    return value


def notes_for_mixed_units(readings: tuple[Reading, ...] | list[Reading]) -> tuple[str, ...]:
    """Note when one metric's series uses two or more nonempty units."""

    units_by_metric: dict[str, set[str]] = defaultdict(set)
    for reading in readings:
        unit = str(reading.unit or "").strip()
        if unit:
            units_by_metric[reading.metric].add(unit)
    notes: list[str] = []
    for metric, units in sorted(units_by_metric.items()):
        if len(units) > 1:
            joined = ", ".join(sorted(units))
            notes.append(f"metric {metric} uses mixed units ({joined}); values were not converted")
    return tuple(notes)


def normalize_observed_at(raw: str) -> str:
    """Parse a timestamp into UTC ``YYYY-MM-DDTHH:MM:SSZ``. Required."""

    text = " ".join(str(raw or "").strip().split())
    if not text:
        raise ValueError("observed_at is required")
    candidates = (
        text,
        text.replace("Z", "+00:00"),
        text.replace(" ", "T", 1),
    )
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    raise ValueError(f"unrecognized observed_at: {raw}")
