"""Local n-of-1 intervention tag store. Invalid files load empty.

Opt-in encryption at rest via ``SOMATIC_ENCRYPT_STORES``; the default stays
plaintext under user-only file permissions (see :mod:`somatic.local_crypto`).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from somatic.ingest.packet import normalize_observed_at
from somatic.local_crypto import decode_store_payload, encode_store_payload, erase_store_key

from .n_of_1 import InterventionTag

EXPERIMENT_PATH_ENV = "SOMATIC_EXPERIMENT_PATH"


def default_experiment_path() -> Path:
    override = os.environ.get(EXPERIMENT_PATH_ENV, "").strip()
    if override:
        return Path(override)
    return Path.home() / ".somatic" / "experiments.json"


def load_tags(path: Path | None = None) -> tuple[InterventionTag, ...]:
    destination = path if path is not None else default_experiment_path()
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
    rows = payload.get("tags")
    if not isinstance(rows, list):
        return ()
    loaded: list[InterventionTag] = []
    for row in rows:
        if not isinstance(row, dict):
            return ()
        try:
            loaded.append(_tag_from_dict(row))
        except (KeyError, TypeError, ValueError):
            return ()
    return tuple(loaded)


def save_tags(
    tags: tuple[InterventionTag, ...] | list[InterventionTag], path: Path | None = None
) -> Path:
    destination = path if path is not None else default_experiment_path()
    payload = {
        "schema_version": 1,
        "tags": [tag.to_dict() for tag in tags],
    }
    encrypted = encode_store_payload(destination, payload, prefix=".experiments-")
    if encrypted is not None:
        return encrypted
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=".experiments-",
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


def append_tag(tag: InterventionTag, path: Path | None = None) -> tuple[InterventionTag, ...]:
    combined = list(load_tags(path))
    combined.append(tag)
    save_tags(tuple(combined), path)
    return tuple(combined)


def erase_stored_tags(path: Path | None = None) -> None:
    destination = path if path is not None else default_experiment_path()
    erase_store_key(destination)
    try:
        destination.unlink()
    except FileNotFoundError:
        return


def _tag_from_dict(payload: dict[str, object]) -> InterventionTag:
    name = str(payload.get("name") or "").strip()
    metric = str(payload.get("metric") or "").strip()
    if not name or not metric:
        raise ValueError("tag name and metric are required")
    started = normalize_observed_at(str(payload.get("started_at") or ""))
    ended_raw = str(payload.get("ended_at") or "").strip()
    ended = normalize_observed_at(ended_raw) if ended_raw else ""
    return InterventionTag(
        name=name,
        metric=metric,
        started_at=started,
        ended_at=ended,
        note=str(payload.get("note") or ""),
    )
