import re
from dataclasses import dataclass

from somatic.fabric.canonical import FabricJsonError, validate_integer_only_json
from somatic.fabric.pathing import path_confinement_errors
from somatic.fabric.signing import code_signature_threshold_errors, signature_shape_errors
from somatic.fabric.spec import (
    FABRIC_CLASSES,
    FABRIC_CODE_TYPES,
    FABRIC_DATA_TYPES,
    FABRIC_HARNESSES,
    FABRIC_SCHEMA_VERSION,
    PACK_REQUIRED_FIELDS,
    PUBLIC_LICENSE_ALLOWLIST,
)


ID_SEGMENT_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9._-]{0,126}[a-z0-9])$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
RFC3339_UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
INFOHASH_PATTERN = re.compile(r"^[a-f0-9]{40}$")
KEY_ID_PATTERN = re.compile(r"^[a-f0-9]{64}$")
SPDX_OR_LICENSE_REF_PATTERN = re.compile(r"^(?:[A-Za-z0-9.-]+|LicenseRef-[A-Za-z0-9.-]+)$")


@dataclass(frozen=True)
class FabricValidationResult:
    valid: bool
    errors: tuple[str, ...]


def validate_pack_manifest(manifest, *, allow_unsigned_code=False, keyring=None, verify_crypto=False):
    errors = []
    if not isinstance(manifest, dict):
        return FabricValidationResult(False, ("manifest must be an object",))

    try:
        validate_integer_only_json(manifest)
    except FabricJsonError as exc:
        errors.append(str(exc))

    for field in PACK_REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"{field} is required")

    schema_version = manifest.get("schemaVersion")
    if schema_version != FABRIC_SCHEMA_VERSION:
        errors.append("schemaVersion must be 1.0.0")

    _validate_id(manifest.get("id"), "id", errors)
    _validate_string(manifest.get("name"), "name", errors)
    _validate_semver(manifest.get("version"), "version", errors)
    _validate_class_type(manifest, errors)
    _validate_license(manifest, errors)
    _validate_publisher(manifest, errors)
    _validate_harnesses(manifest.get("harnesses"), errors)
    _validate_transport(manifest.get("transport"), errors)
    _validate_files(manifest, errors)
    _validate_timestamp(manifest.get("createdAt"), "createdAt", errors)
    errors.extend(signature_shape_errors(manifest.get("signatures")))
    if not allow_unsigned_code:
        errors.extend(code_signature_threshold_errors(manifest))
    errors.extend(path_confinement_errors(manifest))
    if verify_crypto or keyring is not None:
        if keyring is None:
            errors.append("keyring is required for cryptographic verification")
        else:
            from somatic.fabric.keyring import verify_pack_publisher_threshold

            result = verify_pack_publisher_threshold(manifest, keyring)
            if not result.trusted:
                errors.append(f"publisher signature verification failed: {result.reason}")

    return FabricValidationResult(not errors, tuple(errors))


def license_gate_errors(manifest):
    policy = evaluate_license_policy(manifest)
    if policy["publish"]["allowed"]:
        return []
    return [policy["publish"]["reason"]]


def evaluate_license_policy(manifest):
    license_id = manifest.get("license")
    obligation = _obligation_for(license_id)
    public_allowed = license_id in PUBLIC_LICENSE_ALLOWLIST
    private_allowed = _private_license_allowed(manifest)
    internal_install_allowed = isinstance(license_id, str) and license_id.startswith(
        "LicenseRef-Internal-"
    )

    if public_allowed:
        return {
            "publish": _allowed(obligation),
            "seed": _allowed(obligation),
            "catalog": _allowed(obligation),
            "install": _allowed(obligation),
        }
    if private_allowed:
        return {
            "publish": _allowed(obligation),
            "seed": _blocked("Private-only licenses must not be seeded into public swarms."),
            "catalog": _blocked("Private-only licenses must not appear in public catalogs."),
            "install": _allowed(obligation),
        }

    reason = f"license {license_id!r} is not redistribution-allowlisted"
    return {
        "publish": _blocked(reason),
        "seed": _blocked(reason),
        "catalog": _blocked(reason),
        "install": _allowed(obligation)
        if internal_install_allowed
        else _blocked(f"License {license_id!r} is not allowed for install."),
    }


def _validate_id(value, field, errors):
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return
    parts = value.split("/")
    if len(parts) != 2 or not all(ID_SEGMENT_PATTERN.match(part) for part in parts):
        errors.append(f"{field} must be <namespace>/<name> with canonical id segments")


def _validate_string(value, field, errors):
    if not isinstance(value, str) or not value:
        errors.append(f"{field} is required")


def _validate_semver(value, field, errors):
    if not isinstance(value, str) or not SEMVER_PATTERN.match(value):
        errors.append(f"{field} must be SemVer 2.0.0")


def _validate_timestamp(value, field, errors):
    if not isinstance(value, str) or not RFC3339_UTC_PATTERN.match(value):
        errors.append(f"{field} must be RFC 3339 UTC with second precision")


def _validate_class_type(manifest, errors):
    pack_class = manifest.get("class")
    pack_type = manifest.get("type")
    if pack_class not in FABRIC_CLASSES:
        errors.append('class must be "data" or "code"')
    if pack_class == "data" and pack_type not in FABRIC_DATA_TYPES:
        errors.append("type must be legal for its class")
    if pack_class == "code" and pack_type not in FABRIC_CODE_TYPES:
        errors.append("type must be legal for its class")


def _validate_license(manifest, errors):
    license_id = manifest.get("license")
    if not isinstance(license_id, str) or not SPDX_OR_LICENSE_REF_PATTERN.match(license_id):
        errors.append("license must be one SPDX id or LicenseRef token")
        return
    errors.extend(license_gate_errors(manifest))


def _validate_publisher(manifest, errors):
    publisher = manifest.get("publisher")
    if not isinstance(publisher, dict):
        errors.append("publisher is required")
        return
    namespace = publisher.get("namespace")
    if not isinstance(namespace, str) or not ID_SEGMENT_PATTERN.match(namespace):
        errors.append("publisher.namespace must be a lowercase id token")
    if isinstance(manifest.get("id"), str) and manifest["id"].split("/", 1)[0] != namespace:
        errors.append("publisher.namespace must equal manifest id namespace")
    _validate_string(publisher.get("displayName"), "publisher.displayName", errors)
    key_id = publisher.get("keyId")
    if not isinstance(key_id, str) or not KEY_ID_PATTERN.match(key_id):
        errors.append("publisher.keyId must be 64 lowercase hex")


def _validate_harnesses(value, errors):
    if not isinstance(value, list) or not value:
        errors.append("harnesses must be a non-empty array")
        return
    seen = set()
    for harness in value:
        if harness not in FABRIC_HARNESSES:
            errors.append(f"unknown harness {harness!r}")
        if harness in seen:
            errors.append("harnesses must not contain duplicates")
        seen.add(harness)
    if "*" in seen and len(seen) > 1:
        errors.append('harness wildcard "*" must appear alone')


def _validate_transport(value, errors):
    if not isinstance(value, dict):
        errors.append("transport is required")
        return
    infohash = value.get("infohash")
    if not isinstance(infohash, str) or not INFOHASH_PATTERN.match(infohash):
        errors.append("transport.infohash must be a 40-char lowercase hex BitTorrent v1 infohash")
    magnet = value.get("magnet")
    if not isinstance(magnet, str) or not magnet.startswith("magnet:?"):
        errors.append("transport.magnet must be a magnet URI")
        return
    params = _parse_magnet_params(magnet[len("magnet:?") :])
    xt = params.get("xt", [""])[0]
    if isinstance(infohash, str) and xt.lower() != f"urn:btih:{infohash}":
        errors.append("transport.magnet xt must match transport.infohash")
    webseeds = params.get("ws", [])
    if not webseeds or any(not seed.lower().startswith("https://") for seed in webseeds):
        errors.append("transport.magnet must include an https WebSeed ws parameter")
    trackers = params.get("tr", [])
    if any(not tracker.lower().startswith("wss://") for tracker in trackers):
        errors.append("transport.magnet tr parameters must use wss://")


def _validate_files(manifest, errors):
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        errors.append("files must be a non-empty array")
        return
    previous = ""
    seen = set()
    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            errors.append(f"files[{index}] must be an object")
            continue
        path = entry.get("path")
        if isinstance(path, str):
            if path in seen:
                errors.append(f"duplicate file path {path}")
            if previous and path < previous:
                errors.append("files must be sorted by path ascending")
            seen.add(path)
            previous = path
        sha256 = entry.get("sha256")
        if not isinstance(sha256, str) or not SHA256_PATTERN.match(sha256):
            errors.append("files[].sha256 must be 64 lowercase hex")
        size = entry.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            errors.append("files[].size must be a non-negative integer byte count")
        if "executable" in entry and not isinstance(entry["executable"], bool):
            errors.append("files[].executable must be boolean when present")


def _private_license_allowed(manifest):
    license_id = manifest.get("license")
    if license_id != "proprietary" and not (
        isinstance(license_id, str) and license_id.startswith("LicenseRef-Internal-")
    ):
        return False
    harnesses = manifest.get("harnesses", [])
    if not isinstance(harnesses, list) or not harnesses or "*" in harnesses:
        return False
    transport = manifest.get("transport", {})
    if not isinstance(transport, dict):
        return False
    magnet = transport.get("magnet", "")
    if "tr=" in magnet:
        return False
    return not transport.get("ipfsCid")


def _allowed(obligation=None):
    decision = {"allowed": True}
    if obligation:
        decision["obligation"] = obligation
    return decision


def _blocked(reason):
    return {"allowed": False, "reason": reason}


def _obligation_for(license_id):
    if not isinstance(license_id, str):
        return None
    hints = []
    if "CC-BY" in license_id:
        hints.append("Attribution required.")
    if "-NC" in license_id:
        hints.append("Non-commercial use restriction applies.")
    if license_id.startswith(("GPL", "AGPL", "LGPL")):
        hints.append("Copyleft license obligations apply.")
    if "CC-BY-SA" in license_id:
        hints.append("Share-alike obligations apply.")
    return " ".join(hints) or None


def _parse_magnet_params(query):
    params = {}
    for pair in query.split("&"):
        if not pair:
            continue
        if "=" in pair:
            key, value = pair.split("=", 1)
        else:
            key, value = pair, ""
        params.setdefault(key, []).append(_percent_decode(value))
    return params


def _percent_decode(value):
    output = []
    index = 0
    while index < len(value):
        if value[index] == "%" and index + 2 < len(value):
            token = value[index + 1 : index + 3]
            try:
                output.append(chr(int(token, 16)))
                index += 3
                continue
            except ValueError:
                pass
        output.append(value[index])
        index += 1
    return "".join(output)
