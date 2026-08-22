"""On-disk consent ledger store.

Persists :class:`~somatic.consent.ledger.ConsentLedger` as local JSON with
owner-only permissions (``0600``). Missing, unreadable, invalid, or
undecryptable files load as all-OFF. Stdlib only; plaintext under user file
permissions by default — opt-in encryption at rest via ``SOMATIC_ENCRYPT_STORES``
(see :mod:`somatic.local_crypto`). Override the path with ``SOMATIC_CONSENT_PATH``.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from somatic.local_crypto import decode_store_payload, encode_store_payload, erase_store_key

from .ledger import ConsentLedger

CONSENT_PATH_ENV = "SOMATIC_CONSENT_PATH"


def default_consent_path() -> Path:
    """Return the on-disk ledger path (env override or ``~/.somatic/consent.json``)."""

    override = os.environ.get(CONSENT_PATH_ENV, "").strip()
    if override:
        return Path(override)
    return Path.home() / ".somatic" / "consent.json"


def load_ledger(path: Path | None = None) -> ConsentLedger:
    """Load a ledger from disk. Missing or invalid files return all-OFF."""

    destination = path if path is not None else default_consent_path()
    try:
        raw = destination.read_bytes()
    except OSError:
        return ConsentLedger()
    payload = decode_store_payload(raw, destination)
    if payload is None:
        return ConsentLedger()
    return ConsentLedger.from_dict(payload)


def save_ledger(ledger: ConsentLedger, path: Path | None = None) -> Path:
    """Write ``ledger`` as JSON and chmod ``0600``. Creates parent dirs."""

    destination = path if path is not None else default_consent_path()
    encrypted = encode_store_payload(destination, ledger.to_dict(), prefix=".consent-")
    if encrypted is not None:
        return encrypted
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(ledger.to_dict(), indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=".consent-",
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


def erase_stored_ledger(path: Path | None = None) -> None:
    """Right-to-erasure: delete the on-disk ledger file (and key) if present."""

    destination = path if path is not None else default_consent_path()
    erase_store_key(destination)
    try:
        destination.unlink()
    except FileNotFoundError:
        return
