"""Local readings store. Missing or invalid files load empty. Stdlib only.

Opt-in encryption at rest via ``SOMATIC_ENCRYPT_STORES``; the default stays
plaintext under user-only file permissions (see :mod:`somatic.local_crypto`).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from somatic.local_crypto import decode_store_payload, encode_store_payload, erase_store_key

from .packet import Reading, reading_from_dict

INGEST_PATH_ENV = "SOMATIC_INGEST_PATH"


def default_ingest_path() -> Path:
    override = os.environ.get(INGEST_PATH_ENV, "").strip()
    if override:
        return Path(override)
    return Path.home() / ".somatic" / "readings.json"


def load_readings(path: Path | None = None) -> tuple[Reading, ...]:
    destination = path if path is not None else default_ingest_path()
    try:
        raw = destination.read_bytes()
    except OSError:
        return ()
    payload = decode_store_payload(raw, destination)
    if payload is None:
        return ()
    if not isinstance(payload, dict):
        return ()
    version = payload.get("schema_version")
    if type(version) is not int or version != 1:
        return ()
    rows = payload.get("readings")
    if not isinstance(rows, list):
        return ()
    loaded: list[Reading] = []
    for row in rows:
        if not isinstance(row, dict):
            return ()
        try:
            loaded.append(reading_from_dict(row))
        except (KeyError, TypeError, ValueError):
            return ()
    return tuple(loaded)


def save_readings(readings: tuple[Reading, ...] | list[Reading], path: Path | None = None) -> Path:
    destination = path if path is not None else default_ingest_path()
    payload = {
        "schema_version": 1,
        "readings": [reading.to_dict() for reading in readings],
    }
    encrypted = encode_store_payload(destination, payload, prefix=".readings-")
    if encrypted is not None:
        return encrypted
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=".readings-",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
        os.replace(tmp_name, destination)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    try:
        os.chmod(destination, 0o600)
    except OSError:
        pass
    return destination


def append_readings(
    new_readings: tuple[Reading, ...] | list[Reading],
    path: Path | None = None,
) -> tuple[Reading, ...]:
    combined = list(load_readings(path))
    combined.extend(new_readings)
    save_readings(tuple(combined), path)
    return tuple(combined)


def erase_stored_readings(path: Path | None = None) -> None:
    """Right-to-erasure: delete the on-disk readings file (and key) if present."""

    destination = path if path is not None else default_ingest_path()
    erase_store_key(destination)
    try:
        destination.unlink()
    except FileNotFoundError:
        return
