"""CSV importer for user-owned numeric readings."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from io import StringIO
from pathlib import Path

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import DATA_INGESTION
from somatic.safety.core import require_consent

from .packet import (
    IngestedPacket,
    Reading,
    normalize_observed_at,
    notes_for_mixed_units,
    parse_finite_value,
)

REQUIRED_COLUMNS = ("metric", "value", "observed_at")


def ingest_csv(
    ledger: ConsentLedger,
    source: str | Path,
    *,
    default_source: str = "csv",
) -> IngestedPacket:
    """Parse a local CSV into a timestamped packet. Requires DATA_INGESTION."""

    require_consent(ledger, DATA_INGESTION)
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError(f"could not read CSV: {exc}") from exc
    return ingest_csv_text(ledger, text, default_source=default_source, origin=str(path))


def ingest_csv_text(
    ledger: ConsentLedger,
    text: str,
    *,
    default_source: str = "csv",
    origin: str = "csv-text",
) -> IngestedPacket:
    """Parse CSV text. Requires DATA_INGESTION (callers that already checked may reuse)."""

    require_consent(ledger, DATA_INGESTION)
    reader = csv.DictReader(StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("CSV has no header row")
    fields = {name.strip().lower(): name for name in reader.fieldnames if name}
    missing = [column for column in REQUIRED_COLUMNS if column not in fields]
    if missing:
        raise ValueError(
            f"CSV header must include metric,value,observed_at (missing: {', '.join(missing)})"
        )

    readings: list[Reading] = []
    notes: list[str] = []
    for index, row in enumerate(reader, start=2):
        mapped = _lower_row(row, fields)
        try:
            metric = str(mapped.get("metric") or "").strip()
            if not metric:
                raise ValueError("metric is empty")
            value = parse_finite_value(str(mapped.get("value") or "").strip())
            observed_at = normalize_observed_at(str(mapped.get("observed_at") or ""))
        except (TypeError, ValueError) as exc:
            notes.append(f"{origin} row {index}: skipped ({exc})")
            continue
        readings.append(
            Reading(
                metric=metric,
                value=value,
                observed_at=observed_at,
                unit=str(mapped.get("unit") or "").strip(),
                source=str(mapped.get("source") or default_source).strip() or default_source,
            )
        )
    if not readings:
        raise ValueError("CSV contained no usable numeric readings")
    notes.extend(notes_for_mixed_units(readings))
    return IngestedPacket(
        readings=tuple(readings),
        notes=tuple(notes),
        source_kind="csv",
    )


def _lower_row(row: Mapping[str, str | None], fields: dict[str, str]) -> dict[str, str]:
    lowered: dict[str, str] = {}
    for key, original in fields.items():
        lowered[key] = str(row.get(original) or "")
    return lowered
