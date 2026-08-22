import base64
import re

from somatic.fabric.canonical import signing_payload
from somatic.fabric.crypto import (
    key_id_for_public_key,
    sign_bytes,
    signature_from_base64,
    signature_to_base64,
    verify_signature_bytes,
)


SIGNATURE_ALGORITHM = "ed25519"
KEY_ID_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def signature_shape_errors(signatures, field="signatures"):
    errors = []
    if not isinstance(signatures, list):
        return [f"{field} must be an array"]
    previous = ""
    for index, signature in enumerate(signatures):
        if not isinstance(signature, dict):
            errors.append(f"{field}[{index}] must be an object")
            continue
        if signature.get("algo") != SIGNATURE_ALGORITHM:
            errors.append(f"{field}[{index}].algo must be ed25519")
        key_id = signature.get("keyId")
        if not isinstance(key_id, str) or not KEY_ID_PATTERN.match(key_id):
            errors.append(f"{field}[{index}].keyId must be 64 lowercase hex")
        elif previous and key_id < previous:
            errors.append(f"{field} must be sorted by keyId")
        previous = key_id if isinstance(key_id, str) else previous
        sig = signature.get("sig")
        if not _is_base64_signature(sig):
            errors.append(f"{field}[{index}].sig must be base64 for a 64-byte Ed25519 signature")
    return errors


def code_signature_threshold_errors(manifest):
    if manifest.get("class") != "code":
        return []
    signatures = manifest.get("signatures")
    if not isinstance(signatures, list) or not signatures:
        return ["code packs require at least one trusted publisher signature"]
    return []


def sign_object(obj, private_key):
    public_key = private_key.public_key()
    key_id = key_id_for_public_key(public_key)
    signature = sign_bytes(private_key, signing_payload(obj))
    entry = {
        "algo": SIGNATURE_ALGORITHM,
        "keyId": key_id,
        "sig": signature_to_base64(signature),
    }
    signed = dict(obj)
    existing = [
        signature_entry
        for signature_entry in signed.get("signatures", [])
        if signature_entry.get("keyId") != key_id
    ]
    signed["signatures"] = sorted(existing + [entry], key=lambda item: item["keyId"])
    return signed


def verify_object_signature(obj, signature_entry, public_key):
    if signature_shape_errors([signature_entry]):
        return False
    if signature_entry["keyId"] != key_id_for_public_key(public_key):
        return False
    signature = signature_from_base64(signature_entry["sig"])
    return verify_signature_bytes(public_key, signing_payload(obj), signature)


def _is_base64_signature(value):
    if not isinstance(value, str):
        return False
    try:
        decoded = base64.b64decode(value, validate=True)
    except Exception:
        return False
    return len(decoded) == 64
