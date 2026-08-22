"""Local, user-owned consent ledger.

Grants and revocations are recorded with UTC timestamps. Persistence uses
stdlib ``json`` only. There is no network I/O and no third-party dependency.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .scopes import CONSENT_SCOPES, ConsentScope, resolve_scope

_GRANT_RECORD_FIELDS = frozenset({"scope_id", "actor", "granted_at"})
_EVENT_RECORD_FIELDS = frozenset({"action", "scope_id", "actor", "timestamp"})
_EVENT_ACTIONS = frozenset({"grant", "revoke"})


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _valid_utc_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _validated_actor(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("consent actor must be a non-empty string")
    return value


def _validated_grant_record(scope_id: str, record: object) -> dict[str, str]:
    if not isinstance(record, dict):
        raise TypeError("consent grant record must be an object")
    if set(record) != _GRANT_RECORD_FIELDS:
        raise ValueError("consent grant record fields invalid")
    if record.get("scope_id") != scope_id:
        raise ValueError("consent grant scope_id mismatch")
    granted_at = record.get("granted_at")
    if not _valid_utc_timestamp(granted_at):
        raise ValueError("consent grant timestamp invalid")
    return {
        "scope_id": scope_id,
        "actor": _validated_actor(record.get("actor")),
        "granted_at": str(granted_at),
    }


def _validated_event_record(event: object) -> dict[str, str]:
    if not isinstance(event, dict):
        raise TypeError("consent event must be an object")
    if set(event) != _EVENT_RECORD_FIELDS:
        raise ValueError("consent event fields invalid")
    action = event.get("action")
    if action not in _EVENT_ACTIONS:
        raise ValueError("consent event action invalid")
    scope_id = event.get("scope_id")
    if not isinstance(scope_id, str):
        raise TypeError("consent event scope_id must be a string")
    resolve_scope(scope_id)
    timestamp = event.get("timestamp")
    if not _valid_utc_timestamp(timestamp):
        raise ValueError("consent event timestamp invalid")
    return {
        "action": str(action),
        "scope_id": scope_id,
        "actor": _validated_actor(event.get("actor")),
        "timestamp": str(timestamp),
    }


class ConsentLedger:
    """In-memory consent ledger with JSON round-trip helpers.

    All catalog scopes start ungranted (default OFF). ``purge_user_data`` is the
    right-to-erasure hook: it clears every grant and event from this ledger.
    """

    def __init__(self) -> None:
        self._grants: dict[str, dict[str, str]] = {}
        self._events: list[dict[str, str]] = []

    def grant(self, scope: ConsentScope | str, actor: str = "user") -> None:
        """Grant ``scope`` and append a grant event with a UTC timestamp."""

        resolved = resolve_scope(scope)
        timestamp = _utc_now_iso()
        self._grants[resolved.id] = {
            "scope_id": resolved.id,
            "actor": str(actor),
            "granted_at": timestamp,
        }
        self._events.append(
            {
                "action": "grant",
                "scope_id": resolved.id,
                "actor": str(actor),
                "timestamp": timestamp,
            }
        )

    def revoke(self, scope: ConsentScope | str) -> None:
        """Revoke ``scope`` if present and append a revoke event."""

        resolved = resolve_scope(scope)
        timestamp = _utc_now_iso()
        self._grants.pop(resolved.id, None)
        self._events.append(
            {
                "action": "revoke",
                "scope_id": resolved.id,
                "actor": "user",
                "timestamp": timestamp,
            }
        )

    def is_granted(self, scope: ConsentScope | str) -> bool:
        """Return True only when ``scope`` is currently granted."""

        resolved = resolve_scope(scope)
        return resolved.id in self._grants

    def granted_scopes(self) -> tuple[ConsentScope, ...]:
        """Return currently granted scopes in catalog order."""

        granted_ids = set(self._grants)
        return tuple(scope for scope in CONSENT_SCOPES if scope.id in granted_ids)

    def to_dict(self) -> dict[str, Any]:
        """Serialize ledger state for local JSON persistence."""

        return {
            "schema_version": 1,
            "grants": deepcopy(self._grants),
            "events": deepcopy(self._events),
        }

    @classmethod
    def from_dict(cls, payload: object) -> ConsentLedger:
        """Restore a ledger from :meth:`to_dict` output.

        Any schema, type, timestamp, or scope failure returns a fresh all-OFF
        ledger. Partial or garbage restores are never applied.
        """

        try:
            return cls._from_dict_strict(payload)
        except (TypeError, ValueError, KeyError):
            return cls()

    @classmethod
    def _from_dict_strict(cls, payload: object) -> ConsentLedger:
        if not isinstance(payload, dict):
            raise TypeError("consent payload must be an object")
        extra = set(payload) - {"schema_version", "grants", "events"}
        if extra:
            raise ValueError("unknown consent payload field")
        version = payload.get("schema_version")
        if not isinstance(version, int) or isinstance(version, bool) or version != 1:
            raise ValueError("unsupported consent schema_version")
        grants = payload.get("grants")
        events = payload.get("events")
        if not isinstance(grants, dict) or not isinstance(events, list):
            raise TypeError("consent grants/events have the wrong type")
        ledger = cls()
        for scope_id, record in grants.items():
            resolved = resolve_scope(str(scope_id))
            grant = _validated_grant_record(resolved.id, record)
            ledger._grants[resolved.id] = grant
        for event in events:
            ledger._events.append(_validated_event_record(event))
        return ledger

    def purge_user_data(self) -> None:
        """Right-to-erasure hook: clear all grants and event history."""

        self._grants.clear()
        self._events.clear()
