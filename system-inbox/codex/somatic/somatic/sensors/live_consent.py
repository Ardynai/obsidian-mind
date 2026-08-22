"""Per-modality live-sensor grants. All default OFF. Not one of the seven scopes.

Each live modality is a hardware-privacy grant on top of data-ingestion +
analysis-insight. Corrupt files load as all-OFF. Erased with consent erase.
"""

from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LIVE_SENSOR_MODALITIES = ("csi", "audio", "video", "video3d")
LIVE_CONSENT_PATH_ENV = "SOMATIC_SENSOR_LIVE_PATH"


def default_live_consent_path() -> Path:
    override = os.environ.get(LIVE_CONSENT_PATH_ENV, "").strip()
    if override:
        return Path(override)
    return Path.home() / ".somatic" / "sensor-live.json"


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class LiveSensorConsent:
    """In-memory per-modality live grants. Every modality starts ungranted."""

    def __init__(self) -> None:
        self._grants: dict[str, dict[str, str]] = {}

    def is_granted(self, modality: str) -> bool:
        return str(modality) in self._grants

    def subject_consent(self, modality: str) -> bool:
        record = self._grants.get(str(modality))
        if not record:
            return False
        return record.get("subject_consent") == "true"

    def grant(
        self,
        modality: str,
        *,
        actor: str = "user",
        subject_consent: bool = False,
    ) -> None:
        name = str(modality)
        if name not in LIVE_SENSOR_MODALITIES:
            raise ValueError(f"no live adapter for modality: {name}")
        if not subject_consent:
            raise ValueError(
                f"live {name} requires subject consent (operator is the only subject, "
                "or every person in the field consented)"
            )
        self._grants[name] = {
            "modality": name,
            "actor": str(actor or "user"),
            "granted_at": _utc_now_iso(),
            "subject_consent": "true",
        }

    def revoke(self, modality: str) -> None:
        self._grants.pop(str(modality), None)

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": 1, "grants": deepcopy(self._grants)}

    @classmethod
    def from_dict(cls, payload: object) -> LiveSensorConsent:
        try:
            return cls._from_dict_strict(payload)
        except (TypeError, ValueError, KeyError):
            return cls()

    @classmethod
    def _from_dict_strict(cls, payload: object) -> LiveSensorConsent:
        if not isinstance(payload, dict):
            raise TypeError("live consent payload must be an object")
        extra = set(payload) - {"schema_version", "grants"}
        if extra:
            raise ValueError("unknown live consent field")
        version = payload.get("schema_version")
        if type(version) is not int or version != 1:
            raise ValueError("unsupported live consent schema_version")
        grants = payload.get("grants")
        if not isinstance(grants, dict):
            raise TypeError("live consent grants must be an object")
        ledger = cls()
        for modality, record in grants.items():
            name = str(modality)
            if name not in LIVE_SENSOR_MODALITIES:
                raise ValueError("unknown live modality")
            if not isinstance(record, dict):
                raise TypeError("live grant record must be an object")
            if record.get("modality") != name:
                raise ValueError("live grant modality mismatch")
            if record.get("subject_consent") != "true":
                raise ValueError("live grant missing subject consent")
            actor = record.get("actor")
            granted_at = record.get("granted_at")
            if not isinstance(actor, str) or not actor.strip():
                raise ValueError("live grant actor invalid")
            if not isinstance(granted_at, str) or not granted_at.endswith("Z"):
                raise ValueError("live grant timestamp invalid")
            ledger._grants[name] = {
                "modality": name,
                "actor": actor,
                "granted_at": granted_at,
                "subject_consent": "true",
            }
        return ledger


def load_live_consent(path: Path | None = None) -> LiveSensorConsent:
    destination = path if path is not None else default_live_consent_path()
    try:
        raw = destination.read_text(encoding="utf-8")
        payload = json.loads(raw)
    except (OSError, UnicodeDecodeError, ValueError):
        return LiveSensorConsent()
    return LiveSensorConsent.from_dict(payload)


def save_live_consent(ledger: LiveSensorConsent, path: Path | None = None) -> Path:
    destination = path if path is not None else default_live_consent_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(ledger.to_dict(), indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=".sensor-live-",
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


def erase_live_consent(path: Path | None = None) -> None:
    destination = path if path is not None else default_live_consent_path()
    try:
        destination.unlink()
    except FileNotFoundError:
        return
