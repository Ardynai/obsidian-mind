from dataclasses import dataclass
from datetime import datetime, timezone

from somatic.fabric.crypto import (
    CRYPTO_AVAILABLE,
    CryptoUnavailableError,
    FabricCryptoError,
    public_key_from_base64,
)
from somatic.fabric.manifest import (
    INFOHASH_PATTERN,
    KEY_ID_PATTERN,
    RFC3339_UTC_PATTERN,
    SEMVER_PATTERN,
    validate_pack_manifest,
)
from somatic.fabric.signing import signature_shape_errors
from somatic.fabric.signing import verify_object_signature
from somatic.fabric.spec import FABRIC_CLASSES, FABRIC_HARNESSES, FABRIC_SCHEMA_VERSION, FABRIC_TYPES


@dataclass(frozen=True)
class CatalogValidationResult:
    valid: bool
    errors: tuple[str, ...]


def validate_catalog_shape(catalog):
    errors = []
    if not isinstance(catalog, dict):
        return CatalogValidationResult(False, ("catalog must be an object",))
    if catalog.get("schemaVersion") != FABRIC_SCHEMA_VERSION:
        errors.append("catalog schemaVersion must be 1.0.0")
    harness = catalog.get("harness")
    if harness not in (FABRIC_HARNESSES - {"*"}):
        errors.append("catalog harness must be a known concrete harness")
    published_at = catalog.get("publishedAt")
    if not isinstance(published_at, str) or not RFC3339_UTC_PATTERN.match(published_at):
        errors.append("catalog publishedAt must be RFC 3339 UTC")
    packs = catalog.get("packs")
    if not isinstance(packs, list):
        errors.append("catalog packs must be an array")
        packs = []
    seen = set()
    previous = ""
    for index, entry in enumerate(packs):
        if not isinstance(entry, dict):
            errors.append(f"packs[{index}] must be an object")
            continue
        key = f"{entry.get('id')}@{entry.get('version')}"
        if key in seen:
            errors.append(f"duplicate catalog entry {key}")
        if previous and key < previous:
            errors.append("catalog packs must be sorted by id/version")
        seen.add(key)
        previous = key
        _validate_catalog_entry(entry, index, errors)
    errors.extend(signature_shape_errors(catalog.get("signatures"), field="catalog.signatures"))
    return CatalogValidationResult(not errors, tuple(errors))


def verify_catalog_signature_threshold(catalog, keyring, *, required_signatures=1, now=None):
    from somatic.fabric.keyring import (
        SignatureVerificationResult,
        validate_keyring_shape,
        verify_keyring_root_threshold,
    )

    if not CRYPTO_AVAILABLE:
        return SignatureVerificationResult(
            False,
            required_signatures,
            0,
            "cryptographic verification unavailable; install the optional fabric extra",
        )
    catalog_shape = validate_catalog_shape(catalog)
    if not catalog_shape.valid:
        return SignatureVerificationResult(
            False, required_signatures, 0, "; ".join(catalog_shape.errors)
        )
    keyring_shape = validate_keyring_shape(keyring)
    if not keyring_shape.valid:
        return SignatureVerificationResult(
            False, required_signatures, 0, "; ".join(keyring_shape.errors)
        )
    root = verify_keyring_root_threshold(keyring, now=now)
    if not root.trusted:
        return SignatureVerificationResult(
            False,
            required_signatures,
            0,
            f"keyring is not trusted: {root.reason}",
        )

    valid_key_ids = set()
    for signature in catalog.get("signatures", []):
        key = _find_catalog_key(keyring, signature.get("keyId"), now=now)
        if key and _verify_catalog_signature(catalog, signature, key):
            valid_key_ids.add(signature["keyId"])

    trusted = len(valid_key_ids) >= required_signatures
    return SignatureVerificationResult(
        trusted,
        required_signatures,
        len(valid_key_ids),
        None if trusted else "catalog did not meet trusted signature threshold",
    )


def catalog_entry_from_manifest(manifest):
    result = validate_pack_manifest(manifest, allow_unsigned_code=True)
    if not result.valid:
        raise ValueError("; ".join(result.errors))
    return {
        "id": manifest["id"],
        "version": manifest["version"],
        "class": manifest["class"],
        "type": manifest["type"],
        "license": manifest["license"],
        "manifestDigest": "sha256:pending",
        "infohash": manifest["transport"]["infohash"],
        "size": sum(file["size"] for file in manifest["files"]),
        "publisherKeyId": manifest["publisher"]["keyId"],
    }


def _validate_catalog_entry(entry, index, errors):
    if not isinstance(entry.get("id"), str) or "/" not in entry.get("id", ""):
        errors.append(f"packs[{index}].id must be <namespace>/<name>")
    if not isinstance(entry.get("version"), str) or not SEMVER_PATTERN.match(entry["version"]):
        errors.append(f"packs[{index}].version must be SemVer")
    if entry.get("class") not in FABRIC_CLASSES:
        errors.append(f"packs[{index}].class must be data or code")
    if entry.get("type") not in FABRIC_TYPES:
        errors.append(f"packs[{index}].type must be a known Fabric type")
    if not isinstance(entry.get("license"), str) or not entry["license"]:
        errors.append(f"packs[{index}].license is required")
    digest = entry.get("manifestDigest")
    if not isinstance(digest, str) or not digest.startswith("sha256:") or len(digest) != 71:
        errors.append(f"packs[{index}].manifestDigest must be sha256:<64hex>")
    infohash = entry.get("infohash")
    if not isinstance(infohash, str) or not INFOHASH_PATTERN.match(infohash):
        errors.append(f"packs[{index}].infohash must be 40 lowercase hex")
    size = entry.get("size")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        errors.append(f"packs[{index}].size must be a non-negative integer")
    publisher_key_id = entry.get("publisherKeyId")
    if not isinstance(publisher_key_id, str) or not KEY_ID_PATTERN.match(publisher_key_id):
        errors.append(f"packs[{index}].publisherKeyId must be 64 lowercase hex")


def _find_catalog_key(keyring, key_id, *, now=None):
    for publisher in keyring.get("publishers", []):
        for key in publisher.get("keys", []):
            if key.get("keyId") == key_id and _publisher_key_active(key, now=now):
                return key
    return None


def _verify_catalog_signature(catalog, signature, key):
    try:
        public_key = public_key_from_base64(key["publicKey"])
        return verify_object_signature(catalog, signature, public_key)
    except (CryptoUnavailableError, FabricCryptoError):
        return False


def _publisher_key_active(key, *, now=None):
    if key.get("status") != "active":
        return False
    current = now or datetime.now(timezone.utc)
    valid_from = _parse_utc(key.get("validFrom"))
    valid_until = _parse_utc(key.get("validUntil"))
    if not valid_from or current < valid_from:
        return False
    return valid_until is None or current <= valid_until


def _parse_utc(value):
    if value is None:
        return None
    if not isinstance(value, str) or not RFC3339_UTC_PATTERN.match(value):
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
