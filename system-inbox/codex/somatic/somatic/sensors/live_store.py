"""Local ring buffer of *derived* CSI features. Raw IQ is never written.

Opt-in encryption at rest via ``SOMATIC_ENCRYPT_STORES``; the default stays
plaintext under user-only file permissions (see :mod:`somatic.local_crypto`).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from somatic.local_crypto import decode_store_payload, encode_store_payload, erase_store_key

CSI_FEATURES_PATH_ENV = "SOMATIC_CSI_FEATURES_PATH"
MAX_STORED_FRAMES = 128
_FORBIDDEN = frozenset(
    {
        "raw_values",
        "samples",
        "imag",
        "amplitude",
        "phase",
        "rssi",
        "pcm",
        "frames",
        "waveform",
        "iq",
        "source_ids",
        "raw_frames",
        "raw_audio",
        "audio_bytes",
        "wav_bytes",
        "transcript",
        "raw_csi",
        "csi_iq",
        "csi_data",
        "real",
    }
)


def default_csi_features_path() -> Path:
    override = os.environ.get(CSI_FEATURES_PATH_ENV, "").strip()
    if override:
        return Path(override)
    return Path.home() / ".somatic" / "csi-features.json"


def _clean_frame(frame: object) -> dict[str, Any] | None:
    if not isinstance(frame, dict):
        return None
    cleaned: dict[str, Any] = {}
    for key, value in frame.items():
        name = str(key)
        if name.lower() in _FORBIDDEN:
            continue
        cleaned[name] = value
    if not cleaned:
        return None
    return cleaned


def load_csi_features(path: Path | None = None) -> tuple[dict[str, Any], ...]:
    destination = path if path is not None else default_csi_features_path()
    try:
        raw = destination.read_bytes()
    except OSError:
        return ()
    payload = decode_store_payload(raw, destination)
    if not isinstance(payload, dict):
        return ()
    if type(payload.get("schema_version")) is not int or payload.get("schema_version") != 1:
        return ()
    rows = payload.get("frames")
    if not isinstance(rows, list):
        return ()
    frames: list[dict[str, Any]] = []
    for row in rows[-MAX_STORED_FRAMES:]:
        cleaned = _clean_frame(row)
        if cleaned is not None:
            frames.append(cleaned)
    return tuple(frames)


def save_csi_features(
    frames: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    path: Path | None = None,
) -> Path:
    destination = path if path is not None else default_csi_features_path()
    cleaned = [item for item in (_clean_frame(frame) for frame in frames) if item]
    payload = {"schema_version": 1, "frames": cleaned[-MAX_STORED_FRAMES:]}
    encrypted = encode_store_payload(destination, payload, prefix=".csi-features-")
    if encrypted is not None:
        return encrypted
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=".csi-features-",
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


def append_csi_features(
    frame: dict[str, Any], path: Path | None = None
) -> tuple[dict[str, Any], ...]:
    frames = list(load_csi_features(path))
    cleaned = _clean_frame(frame)
    if cleaned is not None:
        frames.append(cleaned)
    save_csi_features(frames, path)
    return tuple(frames[-MAX_STORED_FRAMES:])


def erase_csi_features(path: Path | None = None) -> None:
    destination = path if path is not None else default_csi_features_path()
    erase_store_key(destination)
    try:
        destination.unlink()
    except FileNotFoundError:
        return
