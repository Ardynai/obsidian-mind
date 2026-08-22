"""Consent-gated local data ingestion (CSV and Apple Health)."""

from .apple_health import ingest_apple_health, ingest_apple_health_xml
from .csv import ingest_csv, ingest_csv_text
from .packet import IngestedPacket, Reading, normalize_observed_at
from .store import (
    INGEST_PATH_ENV,
    append_readings,
    default_ingest_path,
    erase_stored_readings,
    load_readings,
    save_readings,
)

__all__ = [
    "INGEST_PATH_ENV",
    "IngestedPacket",
    "Reading",
    "append_readings",
    "default_ingest_path",
    "erase_stored_readings",
    "ingest_apple_health",
    "ingest_apple_health_xml",
    "ingest_csv",
    "ingest_csv_text",
    "load_readings",
    "normalize_observed_at",
    "save_readings",
]
