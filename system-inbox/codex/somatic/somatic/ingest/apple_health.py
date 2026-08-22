"""Apple Health export importer (local XML or zip). Stdlib only."""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree

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

# Identifier suffix → packet metric. Mapping is naming only, not clinical normals.
_HK_METRIC_NAMES = {
    "HeartRate": "heart_rate",
    "RestingHeartRate": "resting_hr",
    "WalkingHeartRateAverage": "walking_hr",
    "HeartRateVariabilitySDNN": "hrv_sdnn",
    "StepCount": "steps",
    "DistanceWalkingRunning": "distance_walking_running",
    "FlightsClimbed": "flights_climbed",
    "ActiveEnergyBurned": "active_energy",
    "BasalEnergyBurned": "basal_energy",
    "BloodGlucose": "blood_glucose",
    "BodyMass": "body_mass",
    "BodyMassIndex": "body_mass_index",
    "BodyFatPercentage": "body_fat_percentage",
    "OxygenSaturation": "oxygen_saturation",
    "RespiratoryRate": "respiratory_rate",
    "BloodPressureSystolic": "blood_pressure_systolic",
    "BloodPressureDiastolic": "blood_pressure_diastolic",
    "DietaryWater": "dietary_water",
    "DietaryCaffeine": "dietary_caffeine",
}


def ingest_apple_health(
    ledger: ConsentLedger,
    source: str | Path,
) -> IngestedPacket:
    """Parse a local Apple Health ``export.xml`` or export zip. Requires DATA_INGESTION."""

    require_consent(ledger, DATA_INGESTION)
    path = Path(source)
    if not path.exists():
        raise ValueError(f"Apple Health export not found: {path}")
    if path.suffix.lower() == ".zip" or zipfile.is_zipfile(path):
        xml_text = _xml_from_zip(path)
        origin = f"{path}!export.xml"
    else:
        try:
            xml_text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"could not read Apple Health export: {exc}") from exc
        origin = str(path)
    return ingest_apple_health_xml(ledger, xml_text, origin=origin)


def ingest_apple_health_xml(
    ledger: ConsentLedger,
    xml_text: str,
    *,
    origin: str = "apple-health-xml",
) -> IngestedPacket:
    require_consent(ledger, DATA_INGESTION)
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        raise ValueError(f"Apple Health XML is not well-formed: {exc}") from exc

    readings: list[Reading] = []
    notes: list[str] = []
    skipped = 0
    for element in root.iter("Record"):
        record_type = str(element.attrib.get("type") or "")
        metric = _metric_for_hk_type(record_type)
        if metric is None:
            skipped += 1
            continue
        raw_value = element.attrib.get("value")
        raw_date = element.attrib.get("startDate") or element.attrib.get("creationDate")
        try:
            value = parse_finite_value(str(raw_value).strip())
            observed_at = normalize_observed_at(str(raw_date or ""))
        except (TypeError, ValueError):
            skipped += 1
            continue
        readings.append(
            Reading(
                metric=metric,
                value=value,
                observed_at=observed_at,
                unit=str(element.attrib.get("unit") or ""),
                source="apple-health",
            )
        )
    if skipped:
        notes.append(f"{origin}: skipped {skipped} non-numeric or unmapped Record(s)")
    if not readings:
        raise ValueError("Apple Health export contained no usable numeric records")
    notes.extend(notes_for_mixed_units(readings))
    return IngestedPacket(
        readings=tuple(readings),
        notes=tuple(notes),
        source_kind="apple-health",
    )


def _metric_for_hk_type(record_type: str) -> str | None:
    if not record_type.startswith("HKQuantityTypeIdentifier"):
        return None
    suffix = record_type.removeprefix("HKQuantityTypeIdentifier")
    if not suffix:
        return None
    return _HK_METRIC_NAMES.get(suffix, _to_snake(suffix))


def _to_snake(name: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index and name[index - 1].islower():
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars) or name.lower()


def _xml_from_zip(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            candidates = [
                name for name in names if name.replace("\\", "/").rstrip("/").endswith("export.xml")
            ]
            if not candidates:
                raise ValueError("zip does not contain export.xml")
            with archive.open(candidates[0]) as handle:
                return handle.read().decode("utf-8")
    except zipfile.BadZipFile as exc:
        raise ValueError(f"file is not a valid zip archive: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError("zip export.xml is not valid UTF-8") from exc
