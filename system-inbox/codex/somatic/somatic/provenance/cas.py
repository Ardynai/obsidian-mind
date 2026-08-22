"""Content-addressed evidence artifacts: hash is the id; verify from disk."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def hash_payload(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def address_record(payload: dict[str, object]) -> dict[str, object]:
    """Return ``payload`` with a content id equal to its canonical SHA-256."""

    body = dict(payload)
    body.pop("content_id", None)
    digest = hash_payload(body)
    body["content_id"] = digest
    return body


def verify_record(payload: dict[str, object]) -> dict[str, object]:
    claimed = str(payload.get("content_id") or "")
    body = dict(payload)
    body.pop("content_id", None)
    digest = hash_payload(body)
    ok = bool(claimed) and claimed == digest
    return {
        "ok": ok,
        "claimed": claimed,
        "computed": digest,
        "p2p_distribution": "disabled",
        "network": False,
    }


def verify_file(path: str | Path) -> dict[str, object]:
    destination = Path(path)
    try:
        raw = destination.read_text(encoding="utf-8")
        payload = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"could not read evidence file: {exc}"}
    if not isinstance(payload, dict):
        return {"ok": False, "error": "evidence file must contain a JSON object"}
    result = verify_record(payload)
    result["filename"] = destination.name
    return result
