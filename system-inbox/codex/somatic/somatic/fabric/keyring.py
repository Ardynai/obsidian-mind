from dataclasses import dataclass
from datetime import datetime, timezone

from somatic.fabric.crypto import (
    CRYPTO_AVAILABLE,
    CryptoUnavailableError,
    FabricCryptoError,
    public_key_from_base64,
)
from somatic.fabric.manifest import KEY_ID_PATTERN, RFC3339_UTC_PATTERN
from somatic.fabric.signing import signature_shape_errors, verify_object_signature
from somatic.fabric.spec import FABRIC_SCHEMA_VERSION


@dataclass(frozen=True)
class KeyringValidationResult:
    valid: bool
    errors: tuple[str, ...]


@dataclass(frozen=True)
class SignatureVerificationResult:
    trusted: bool
    required_signatures: int
    valid_signatures: int
    reason: str | None = None


def validate_keyring_shape(keyring):
    errors = []
    if not isinstance(keyring, dict):
        return KeyringValidationResult(False, ("keyring must be an object",))
    if keyring.get("schemaVersion") != FABRIC_SCHEMA_VERSION:
        errors.append("keyring schemaVersion must be 1.0.0")
    version = keyring.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        errors.append("keyring version must be a positive integer")
    expires = keyring.get("expires")
    if not isinstance(expires, str) or not RFC3339_UTC_PATTERN.match(expires):
        errors.append("keyring expires must be RFC 3339 UTC")
    root_keys = keyring.get("rootKeys")
    if not isinstance(root_keys, list) or not root_keys:
        errors.append("keyring rootKeys must be a non-empty array")
        root_keys = []
    root_threshold = keyring.get("rootThreshold")
    if (
        not isinstance(root_threshold, int)
        or isinstance(root_threshold, bool)
        or root_threshold < 1
        or root_threshold > len(root_keys)
    ):
        errors.append("keyring rootThreshold must be between 1 and rootKeys length")
    _validate_keys(root_keys, "rootKeys", errors)
    publishers = keyring.get("publishers")
    if not isinstance(publishers, list):
        errors.append("keyring publishers must be an array")
    else:
        for index, publisher in enumerate(publishers):
            _validate_publisher(publisher, index, errors)
    errors.extend(signature_shape_errors(keyring.get("signatures"), field="keyring.signatures"))
    return KeyringValidationResult(not errors, tuple(errors))


def verify_keyring_root_threshold(keyring, *, now=None):
    shape = validate_keyring_shape(keyring)
    required = keyring.get("rootThreshold", 0) if isinstance(keyring, dict) else 0
    if not shape.valid:
        return SignatureVerificationResult(False, required, 0, "; ".join(shape.errors))
    if not CRYPTO_AVAILABLE:
        return SignatureVerificationResult(
            False,
            required,
            0,
            "cryptographic verification unavailable; install the optional fabric extra",
        )
    if _timestamp_is_expired(keyring["expires"], now=now):
        return SignatureVerificationResult(False, required, 0, "keyring is expired")

    valid_key_ids = set()
    for signature in keyring["signatures"]:
        key = _find_key(keyring["rootKeys"], signature.get("keyId"))
        if not key or not _root_key_active(key, now=now):
            continue
        if _verify_signature_entry(keyring, signature, key):
            valid_key_ids.add(signature["keyId"])

    trusted = len(valid_key_ids) >= required
    return SignatureVerificationResult(
        trusted,
        required,
        len(valid_key_ids),
        None if trusted else "keyring did not meet root signature threshold",
    )


def verify_keyring_replacement(candidate, current_trusted, *, now=None):
    required = (
        current_trusted.get("rootThreshold", 0) if isinstance(current_trusted, dict) else 0
    )
    if not CRYPTO_AVAILABLE:
        return SignatureVerificationResult(
            False,
            required,
            0,
            "cryptographic verification unavailable; install the optional fabric extra",
        )

    current_shape = validate_keyring_shape(current_trusted)
    if not current_shape.valid:
        return SignatureVerificationResult(False, required, 0, "; ".join(current_shape.errors))
    candidate_shape = validate_keyring_shape(candidate)
    if not candidate_shape.valid:
        return SignatureVerificationResult(False, required, 0, "; ".join(candidate_shape.errors))

    current = verify_keyring_root_threshold(current_trusted, now=now)
    if not current.trusted:
        return SignatureVerificationResult(
            False,
            required,
            0,
            f"current trusted keyring is invalid: {current.reason}",
        )
    if candidate["version"] <= current_trusted["version"]:
        return SignatureVerificationResult(
            False,
            required,
            0,
            "replacement keyring version must strictly increase",
        )
    if _timestamp_is_expired(candidate["expires"], now=now):
        return SignatureVerificationResult(False, required, 0, "replacement keyring is expired")

    candidate_self = verify_keyring_root_threshold(candidate, now=now)
    if not candidate_self.trusted:
        return SignatureVerificationResult(
            False,
            candidate["rootThreshold"],
            candidate_self.valid_signatures,
            f"replacement keyring is not self-trusted: {candidate_self.reason}",
        )

    valid_key_ids = set()
    for signature in candidate["signatures"]:
        key = _find_key(current_trusted["rootKeys"], signature.get("keyId"))
        if not key or not _root_key_active(key, now=now):
            continue
        if _verify_signature_entry(candidate, signature, key):
            valid_key_ids.add(signature["keyId"])

    trusted = len(valid_key_ids) >= required
    return SignatureVerificationResult(
        trusted,
        required,
        len(valid_key_ids),
        None
        if trusted
        else "replacement keyring did not meet previous root signature threshold",
    )


def verify_pack_publisher_threshold(manifest, keyring):
    required = 1 if manifest.get("class") == "code" else 0
    if not CRYPTO_AVAILABLE:
        return SignatureVerificationResult(
            False,
            required,
            0,
            "cryptographic verification unavailable; install the optional fabric extra",
        )
    keyring_shape = validate_keyring_shape(keyring)
    if not keyring_shape.valid:
        return SignatureVerificationResult(False, required, 0, "; ".join(keyring_shape.errors))
    root = verify_keyring_root_threshold(keyring)
    if not root.trusted:
        return SignatureVerificationResult(
            False,
            required,
            0,
            f"keyring is not trusted: {root.reason}",
        )

    namespace = _manifest_namespace(manifest)
    publisher = _find_publisher(keyring, namespace)
    if not publisher:
        return SignatureVerificationResult(
            False,
            required,
            0,
            "publisher is not trusted by the keyring",
        )
    required = publisher["threshold"]
    signatures = manifest.get("signatures", [])
    if not isinstance(signatures, list) or not signatures:
        return SignatureVerificationResult(
            False,
            required,
            0,
            "manifest has no trusted publisher signature",
        )

    valid_key_ids = set()
    for signature in signatures:
        key = _find_key(publisher["keys"], signature.get("keyId"))
        if not key or not _key_usable_for_manifest(key, manifest.get("createdAt")):
            continue
        if _verify_signature_entry(manifest, signature, key):
            valid_key_ids.add(signature["keyId"])

    trusted = len(valid_key_ids) >= required
    return SignatureVerificationResult(
        trusted,
        required,
        len(valid_key_ids),
        None if trusted else "manifest did not meet publisher signature threshold",
    )


def _validate_publisher(publisher, index, errors):
    if not isinstance(publisher, dict):
        errors.append(f"publishers[{index}] must be an object")
        return
    if not isinstance(publisher.get("namespace"), str) or not publisher["namespace"]:
        errors.append(f"publishers[{index}].namespace is required")
    if not isinstance(publisher.get("displayName"), str) or not publisher["displayName"]:
        errors.append(f"publishers[{index}].displayName is required")
    keys = publisher.get("keys")
    if not isinstance(keys, list) or not keys:
        errors.append(f"publishers[{index}].keys must be a non-empty array")
        keys = []
    threshold = publisher.get("threshold")
    if (
        not isinstance(threshold, int)
        or isinstance(threshold, bool)
        or threshold < 1
        or threshold > len(keys)
    ):
        errors.append(f"publishers[{index}].threshold must be between 1 and keys length")
    _validate_keys(keys, f"publishers[{index}].keys", errors)


def _validate_keys(keys, label, errors):
    seen = set()
    if not isinstance(keys, list):
        errors.append(f"{label} must be an array")
        return
    for index, key in enumerate(keys):
        if not isinstance(key, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        key_id = key.get("keyId")
        if not isinstance(key_id, str) or not KEY_ID_PATTERN.match(key_id):
            errors.append(f"{label}[{index}].keyId must be 64 lowercase hex")
        elif key_id in seen:
            errors.append(f"{label} must not duplicate keyId")
        seen.add(key_id)
        if key.get("algo") != "ed25519":
            errors.append(f"{label}[{index}].algo must be ed25519")
        if key.get("status") not in {"active", "revoked"}:
            errors.append(f"{label}[{index}].status must be active or revoked")
        if not isinstance(key.get("publicKey"), str) or not key["publicKey"]:
            errors.append(f"{label}[{index}].publicKey is required")
        if not isinstance(key.get("validFrom"), str) or not RFC3339_UTC_PATTERN.match(key["validFrom"]):
            errors.append(f"{label}[{index}].validFrom must be RFC 3339 UTC")
        valid_until = key.get("validUntil")
        if valid_until is not None and (
            not isinstance(valid_until, str) or not RFC3339_UTC_PATTERN.match(valid_until)
        ):
            errors.append(f"{label}[{index}].validUntil must be RFC 3339 UTC or null")


def _find_publisher(keyring, namespace):
    for publisher in keyring.get("publishers", []):
        if publisher.get("namespace") == namespace:
            return publisher
    return None


def _find_key(keys, key_id):
    for key in keys:
        if key.get("keyId") == key_id:
            return key
    return None


def _verify_signature_entry(obj, signature, key):
    try:
        public_key = public_key_from_base64(key["publicKey"])
        return verify_object_signature(obj, signature, public_key)
    except (CryptoUnavailableError, FabricCryptoError):
        return False


def _manifest_namespace(manifest):
    manifest_id = manifest.get("id", "")
    return manifest_id.split("/", 1)[0] if isinstance(manifest_id, str) else ""


def _key_usable_for_manifest(key, created_at):
    created = _parse_utc(created_at)
    valid_from = _parse_utc(key.get("validFrom"))
    valid_until = _parse_utc(key.get("validUntil"))
    if not created or not valid_from or created < valid_from:
        return False
    if key.get("status") == "active":
        return valid_until is None or created <= valid_until
    if key.get("status") == "revoked":
        return valid_until is not None and created <= valid_until
    return False


def _root_key_active(key, *, now=None):
    current = now or datetime.now(timezone.utc)
    valid_from = _parse_utc(key.get("validFrom"))
    valid_until = _parse_utc(key.get("validUntil"))
    if key.get("status") != "active" or not valid_from or current < valid_from:
        return False
    return valid_until is None or current <= valid_until


def _timestamp_is_expired(value, *, now=None):
    timestamp = _parse_utc(value)
    if not timestamp:
        return True
    current = now or datetime.now(timezone.utc)
    return current >= timestamp


def _parse_utc(value):
    if value is None:
        return None
    if not isinstance(value, str) or not RFC3339_UTC_PATTERN.match(value):
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
