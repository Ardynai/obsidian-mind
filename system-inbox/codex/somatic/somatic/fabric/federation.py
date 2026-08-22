"""Out-of-process Multiverse fabric federation connector.

This module deliberately uses only the Python standard library. The transport,
chunking, descriptor construction, peer routing, identity custody, and signing stay
inside the external Multiverse fabric-transport-d sidecar and registry services.
Somatic only calls those services, enforces an authenticated allowlist, and
re-verifies received bytes against the contentId before handing bytes to callers.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_DESCRIPTOR_BYTES = 2_000_000
DEFAULT_MAX_PAYLOAD_BYTES = 512 * 1024 * 1024

SIDECAR_PUT_CONTENT_PATH = "/v1/content"
SIDECAR_CONTENT_PATH_PREFIX = "/v1/content/"

DEFAULT_REGISTRY_REGISTER_PATH = "/systems/register"
DEFAULT_REGISTRY_ALLOWLIST_PATH = "/fabric/federation/allowlist"
DEFAULT_REGISTRY_DELIVERY_PATH = "/fabric/federation/deliveries"
DEFAULT_REGISTRY_INBOX_PATH = "/fabric/federation/inbox"

LOCALHOST_NAMES = {"localhost", "127.0.0.1", "::1"}


class FabricFederationError(Exception):
    """Base error for fail-closed federation connector failures."""


class FabricConfigError(FabricFederationError):
    """Raised when required local configuration is absent or unsafe."""


class FabricHttpError(FabricFederationError):
    """Raised when the sidecar or registry returns an unusable response."""


class FabricAuthError(FabricHttpError):
    """Raised when a sidecar or registry request is not authenticated."""


class FabricNotFoundError(FabricHttpError):
    """Raised when a configured registry or sidecar route is absent."""


class FabricAllowlistError(FabricFederationError):
    """Raised when a DID is not authenticated through the sibling allowlist."""


class FabricDescriptorError(FabricFederationError):
    """Raised when a content descriptor is malformed or unsafe."""


class FabricIntegrityError(FabricFederationError):
    """Raised when received bytes do not match the expected contentId."""


@dataclass(frozen=True)
class FabricFederationConfig:
    """Runtime configuration for the out-of-process fabric connector."""

    sidecar_base_url: str
    sidecar_token: str
    registry_base_url: str
    registry_token: str
    local_did: str
    system_id: str = "somatic"
    system_name: str = "Somatic"
    reachability_url: str = ""
    allowlisted_sibling_dids: tuple[str, ...] = ()
    registry_register_path: str = DEFAULT_REGISTRY_REGISTER_PATH
    registry_allowlist_path: str = DEFAULT_REGISTRY_ALLOWLIST_PATH
    registry_delivery_path: str = DEFAULT_REGISTRY_DELIVERY_PATH
    registry_inbox_path: str = DEFAULT_REGISTRY_INBOX_PATH
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_descriptor_bytes: int = DEFAULT_MAX_DESCRIPTOR_BYTES
    max_payload_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> FabricFederationConfig:
        env = os.environ if environ is None else environ
        allowlist = _split_csv(env.get("SOMATIC_FABRIC_ALLOWLIST_DIDS", ""))
        sidecar_token = env.get("SOMATIC_FABRIC_SIDECAR_TOKEN") or env.get(
            "FABRIC_TRANSPORT_D_AUTH_TOKEN", ""
        )
        return cls(
            sidecar_base_url=env.get("SOMATIC_FABRIC_SIDECAR_URL", ""),
            sidecar_token=sidecar_token,
            registry_base_url=env.get("SOMATIC_FABRIC_REGISTRY_URL", ""),
            registry_token=env.get("SOMATIC_FABRIC_REGISTRY_TOKEN", ""),
            local_did=env.get("SOMATIC_FABRIC_DID", ""),
            system_id=env.get("SOMATIC_FABRIC_SYSTEM_ID", "somatic"),
            system_name=env.get("SOMATIC_FABRIC_SYSTEM_NAME", "Somatic"),
            reachability_url=env.get("SOMATIC_FABRIC_REACHABILITY_URL", ""),
            allowlisted_sibling_dids=tuple(allowlist),
            registry_register_path=env.get(
                "SOMATIC_FABRIC_REGISTRY_REGISTER_PATH",
                DEFAULT_REGISTRY_REGISTER_PATH,
            ),
            registry_allowlist_path=env.get(
                "SOMATIC_FABRIC_REGISTRY_ALLOWLIST_PATH",
                DEFAULT_REGISTRY_ALLOWLIST_PATH,
            ),
            registry_delivery_path=env.get(
                "SOMATIC_FABRIC_REGISTRY_DELIVERY_PATH",
                DEFAULT_REGISTRY_DELIVERY_PATH,
            ),
            registry_inbox_path=env.get(
                "SOMATIC_FABRIC_REGISTRY_INBOX_PATH",
                DEFAULT_REGISTRY_INBOX_PATH,
            ),
            timeout_seconds=_float_env(env, "SOMATIC_FABRIC_TIMEOUT_SECONDS", 10.0),
            max_descriptor_bytes=_int_env(
                env,
                "SOMATIC_FABRIC_MAX_DESCRIPTOR_BYTES",
                DEFAULT_MAX_DESCRIPTOR_BYTES,
            ),
            max_payload_bytes=_int_env(
                env,
                "SOMATIC_FABRIC_MAX_PAYLOAD_BYTES",
                DEFAULT_MAX_PAYLOAD_BYTES,
            ),
        )

    def validate(self) -> None:
        if not self.sidecar_base_url:
            raise FabricConfigError("SOMATIC_FABRIC_SIDECAR_URL is required")
        if not self.sidecar_token:
            raise FabricConfigError("SOMATIC_FABRIC_SIDECAR_TOKEN is required")
        if not self.registry_base_url:
            raise FabricConfigError("SOMATIC_FABRIC_REGISTRY_URL is required")
        if not self.registry_token:
            raise FabricConfigError("SOMATIC_FABRIC_REGISTRY_TOKEN is required")
        if not self.local_did:
            raise FabricConfigError("SOMATIC_FABRIC_DID is required")
        if not self.system_id:
            raise FabricConfigError("SOMATIC_FABRIC_SYSTEM_ID is required")
        _validate_loopback_http_base_url(self.sidecar_base_url)
        _validate_http_base_url(self.registry_base_url)
        for did in self.allowlisted_sibling_dids:
            _validate_did(did, field_name="allowlisted sibling DID")
        _validate_did(self.local_did, field_name="local DID")


@dataclass(frozen=True)
class FabricContentReference:
    content_id: str
    descriptor: dict[str, Any]


@dataclass(frozen=True)
class FabricSendResult:
    to_did: str
    content_id: str
    descriptor: dict[str, Any]
    registry_response: dict[str, Any]
    secure: bool


@dataclass(frozen=True)
class ReceivedFabricContent:
    from_did: str
    to_did: str
    content_id: str
    descriptor: dict[str, Any]
    payload: bytes
    secure: bool


class FabricTransportSidecarClient:
    """Client for the loopback fabric-transport-d HTTP sidecar."""

    def __init__(self, config: FabricFederationConfig):
        config.validate()
        self._config = config

    def put_bytes(self, payload: bytes) -> FabricContentReference:
        if not isinstance(payload, bytes):
            raise FabricConfigError("fabric payload must be bytes")
        if len(payload) > self._config.max_payload_bytes:
            raise FabricConfigError("fabric payload exceeds configured maximum")
        response = self._request_json(
            "PUT",
            SIDECAR_PUT_CONTENT_PATH,
            payload,
            "application/octet-stream",
        )
        if not isinstance(response, dict):
            raise FabricHttpError("sidecar PUT response was not an object")
        content_id = _required_hex(response.get("contentId"), "sidecar contentId")
        descriptor = response.get("descriptor")
        validate_descriptor(descriptor, expected_content_id=content_id)
        return FabricContentReference(content_id=content_id, descriptor=descriptor)

    def get_descriptor(self, content_id: str) -> dict[str, Any]:
        content_id = _required_hex(content_id, "contentId")
        response = self._request_json(
            "GET",
            f"{SIDECAR_CONTENT_PATH_PREFIX}{content_id}/descriptor",
        )
        if not isinstance(response, dict):
            raise FabricHttpError("sidecar descriptor response was not an object")
        response_content_id = _required_hex(response.get("contentId"), "descriptor contentId")
        if response_content_id != content_id:
            raise FabricIntegrityError("sidecar descriptor contentId mismatch")
        descriptor = response.get("descriptor")
        validate_descriptor(descriptor, expected_content_id=content_id)
        return descriptor

    def get_bytes(self, content_id: str) -> tuple[bytes, dict[str, Any]]:
        content_id = _required_hex(content_id, "contentId")
        descriptor = self.get_descriptor(content_id)
        payload = self._request_bytes(
            "GET",
            f"{SIDECAR_CONTENT_PATH_PREFIX}{content_id}",
        )
        verify_payload_against_descriptor(payload, descriptor, expected_content_id=content_id)
        return payload, descriptor

    def _request_json(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        content_type: str = "application/json",
    ) -> Any:
        response_body = self._request_bytes(method, path, body, content_type)
        try:
            return json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FabricHttpError("sidecar returned malformed JSON") from exc

    def _request_bytes(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        content_type: str = "application/json",
    ) -> bytes:
        url = _join_base_url(self._config.sidecar_base_url, path)
        headers = {
            "Authorization": f"Bearer {self._config.sidecar_token}",
            "User-Agent": "somatic-fabric-federation/1",
        }
        if body is not None:
            headers["Content-Type"] = content_type
        return _urlopen_bytes(
            url=url,
            method=method,
            headers=headers,
            body=body,
            timeout=self._config.timeout_seconds,
            max_bytes=self._config.max_payload_bytes,
            system_name="sidecar",
        )


class FabricRegistryClient:
    """Client for the Multiverse registry HTTP API."""

    def __init__(self, config: FabricFederationConfig):
        config.validate()
        self._config = config

    def register(self) -> dict[str, Any]:
        body = {
            "id": self._config.system_id,
            "name": self._config.system_name,
            "did": self._config.local_did,
            "endpointUrl": self._config.reachability_url,
            "capabilities": [
                "fabric-federation",
                "fabric-ca-consumer",
                "fabric-ca-sender",
                "fabric-ca-receiver",
            ],
            "transport": "fabric-transport-d-loopback-sidecar",
        }
        return self._request_json("POST", self._config.registry_register_path, body)

    def keepalive(self) -> dict[str, Any]:
        return self.register()

    def fetch_allowlist(self) -> set[str]:
        try:
            response = self._request_json("GET", self._config.registry_allowlist_path)
        except FabricNotFoundError:
            response = None
        registry_dids = _allowlist_dids_from_response(response)
        configured_dids = set(self._config.allowlisted_sibling_dids)
        allowlist = registry_dids or configured_dids
        if not allowlist:
            raise FabricAllowlistError("no authenticated sibling DID allowlist available")
        allowlist.discard(self._config.local_did)
        if not allowlist:
            raise FabricAllowlistError("sibling DID allowlist cannot contain only local DID")
        return allowlist

    def send_delivery(
        self,
        to_did: str,
        reference: FabricContentReference,
        *,
        secure: bool = False,
    ) -> dict[str, Any]:
        _validate_did(to_did, field_name="recipient DID")
        body = {
            "type": "fabric-content-delivery",
            "fromDid": self._config.local_did,
            "toDid": to_did,
            "contentId": reference.content_id,
            "descriptor": reference.descriptor,
            "secure": bool(secure),
            "ciphertext": bool(secure),
            "transport": "fabric-ca",
            "transportRuntime": "fabric-transport-d-loopback-sidecar",
        }
        return self._request_json("POST", self._config.registry_delivery_path, body)

    def poll_inbound(self) -> list[dict[str, Any]]:
        path = _append_query(self._config.registry_inbox_path, {"did": self._config.local_did})
        response = self._request_json("GET", path)
        return _inbound_items_from_response(response)

    def _request_json(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        encoded_body = None
        headers = {
            "Authorization": f"Bearer {self._config.registry_token}",
            "Accept": "application/json",
            "User-Agent": "somatic-fabric-federation/1",
        }
        if body is not None:
            encoded_body = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
            headers["Content-Type"] = "application/json"
        url = _join_base_url(self._config.registry_base_url, path)
        response_body = _urlopen_bytes(
            url=url,
            method=method,
            headers=headers,
            body=encoded_body,
            timeout=self._config.timeout_seconds,
            max_bytes=self._config.max_descriptor_bytes,
            system_name="registry",
        )
        if not response_body:
            return {}
        try:
            return json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FabricHttpError("registry returned malformed JSON") from exc


class FabricFederationClient:
    """High-level send and receive facade for Somatic fabric federation."""

    def __init__(self, config: FabricFederationConfig):
        config.validate()
        self.config = config
        self.sidecar = FabricTransportSidecarClient(config)
        self.registry = FabricRegistryClient(config)

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> FabricFederationClient:
        return cls(FabricFederationConfig.from_env(environ))

    def connect(self) -> dict[str, Any]:
        register_response = self.registry.register()
        allowlist = sorted(self.registry.fetch_allowlist())
        return {
            "registered": True,
            "systemId": self.config.system_id,
            "localDid": self.config.local_did,
            "allowlistedSiblingDids": allowlist,
            "registryResponse": register_response,
        }

    def keepalive(self) -> dict[str, Any]:
        return self.registry.keepalive()

    def send(
        self,
        to_did: str,
        path_or_bytes: str | Path | bytes,
        *,
        secure: bool = False,
    ) -> FabricSendResult:
        _validate_did(to_did, field_name="recipient DID")
        allowlist = self.registry.fetch_allowlist()
        _require_allowlisted(to_did, allowlist)
        payload = _read_path_or_bytes(path_or_bytes, self.config.max_payload_bytes)
        reference = self.sidecar.put_bytes(payload)
        registry_response = self.registry.send_delivery(
            to_did,
            reference,
            secure=secure,
        )
        return FabricSendResult(
            to_did=to_did,
            content_id=reference.content_id,
            descriptor=reference.descriptor,
            registry_response=registry_response,
            secure=bool(secure),
        )

    def receive_once(
        self,
        handler: Callable[[ReceivedFabricContent], None] | None = None,
    ) -> list[ReceivedFabricContent]:
        allowlist = self.registry.fetch_allowlist()
        received: list[ReceivedFabricContent] = []
        for item in self.registry.poll_inbound():
            parsed = _parse_inbound_item(item)
            if parsed["to_did"] not in ("", self.config.local_did):
                raise FabricAllowlistError("inbound item is not addressed to the local DID")
            _require_allowlisted(parsed["from_did"], allowlist)
            payload, descriptor = self.sidecar.get_bytes(parsed["content_id"])
            inbound_descriptor = parsed.get("descriptor")
            if inbound_descriptor is not None:
                validate_descriptor(inbound_descriptor, expected_content_id=parsed["content_id"])
                if inbound_descriptor.get("contentId") != descriptor.get("contentId"):
                    raise FabricIntegrityError("inbound descriptor contentId mismatch")
            received_item = ReceivedFabricContent(
                from_did=parsed["from_did"],
                to_did=self.config.local_did,
                content_id=parsed["content_id"],
                descriptor=descriptor,
                payload=payload,
                secure=parsed["secure"],
            )
            if handler is not None:
                handler(received_item)
            received.append(received_item)
        return received


def verify_payload_against_descriptor(
    payload: bytes,
    descriptor: Any,
    *,
    expected_content_id: str | None = None,
) -> str:
    descriptor = validate_descriptor(descriptor, expected_content_id=expected_content_id)
    pieces = descriptor["pieces"]
    expected_total_size = descriptor["totalSize"]
    if len(payload) != expected_total_size:
        raise FabricIntegrityError("payload size does not match descriptor")

    leaf_hashes: list[bytes] = []
    cursor = 0
    for piece in pieces:
        piece_size = piece["size"]
        piece_bytes = payload[cursor : cursor + piece_size]
        if len(piece_bytes) != piece_size:
            raise FabricIntegrityError("payload ended before descriptor pieces completed")
        leaf_hex = _domain_leaf_hash(piece_bytes).hex()
        if leaf_hex != piece["sha256"]:
            raise FabricIntegrityError("payload piece hash does not match descriptor")
        leaf_hashes.append(bytes.fromhex(leaf_hex))
        cursor += piece_size

    if cursor != len(payload):
        raise FabricIntegrityError("payload contains bytes outside descriptor pieces")
    content_id = _merkle_root_hex_from_leaf_hashes(leaf_hashes)
    if content_id != descriptor["contentId"]:
        raise FabricIntegrityError("payload Merkle root does not match descriptor contentId")
    if expected_content_id is not None and content_id != expected_content_id:
        raise FabricIntegrityError("payload contentId does not match requested contentId")
    return content_id


def validate_descriptor(
    descriptor: Any,
    *,
    expected_content_id: str | None = None,
) -> dict[str, Any]:
    if not isinstance(descriptor, dict):
        raise FabricDescriptorError("descriptor must be an object")

    required_fields = {
        "schemaVersion",
        "transport",
        "hash",
        "merkle",
        "merkleRoot",
        "contentId",
        "pieceSize",
        "totalSize",
        "pieces",
    }
    unknown_fields = set(descriptor) - required_fields
    missing_fields = required_fields - set(descriptor)
    if unknown_fields:
        raise FabricDescriptorError("descriptor contains unknown fields")
    if missing_fields:
        raise FabricDescriptorError("descriptor is missing required fields")
    if descriptor["schemaVersion"] != "1.0.0":
        raise FabricDescriptorError("descriptor schemaVersion is unsupported")
    if descriptor["transport"] != "fabric-ca":
        raise FabricDescriptorError("descriptor transport is unsupported")
    if descriptor["hash"] != "sha256":
        raise FabricDescriptorError("descriptor hash is unsupported")
    if descriptor["merkle"] != "sha256-domain-separated-binary-pair-v1":
        raise FabricDescriptorError("descriptor Merkle mode is unsupported")

    content_id = _required_hex(descriptor["contentId"], "descriptor contentId")
    merkle_root = _required_hex(descriptor["merkleRoot"], "descriptor merkleRoot")
    if merkle_root != content_id:
        raise FabricIntegrityError("descriptor merkleRoot does not match contentId")
    if expected_content_id is not None and content_id != expected_content_id:
        raise FabricIntegrityError("descriptor contentId does not match expected contentId")

    piece_size = _non_negative_int(descriptor["pieceSize"], "pieceSize")
    total_size = _non_negative_int(descriptor["totalSize"], "totalSize")
    pieces = descriptor["pieces"]
    if piece_size <= 0:
        raise FabricDescriptorError("descriptor pieceSize must be positive")
    if not isinstance(pieces, list):
        raise FabricDescriptorError("descriptor pieces must be a list")
    piece_count = len(pieces)
    if piece_count <= 0:
        raise FabricDescriptorError("descriptor must contain at least one piece")
    expected_piece_count = 1 if total_size == 0 else (total_size + piece_size - 1) // piece_size
    if piece_count != expected_piece_count:
        raise FabricDescriptorError("descriptor piece count does not match totalSize")

    leaf_hashes: list[bytes] = []
    offset = 0
    for index, piece in enumerate(pieces):
        if not isinstance(piece, dict):
            raise FabricDescriptorError("descriptor piece must be an object")
        allowed_piece_fields = {"index", "offset", "size", "sha256"}
        if set(piece) != allowed_piece_fields:
            raise FabricDescriptorError("descriptor piece fields are invalid")
        if _non_negative_int(piece["index"], "piece index") != index:
            raise FabricDescriptorError("descriptor piece indexes must be contiguous")
        if _non_negative_int(piece["offset"], "piece offset") != offset:
            raise FabricDescriptorError("descriptor piece offsets must be contiguous")
        size = _non_negative_int(piece["size"], "piece size")
        if size == 0 and not (total_size == 0 and piece_count == 1):
            raise FabricDescriptorError("only an empty payload descriptor may use size zero")
        if size < 0:
            raise FabricDescriptorError("descriptor piece size must be positive")
        if size > piece_size:
            raise FabricDescriptorError("descriptor piece size exceeds pieceSize")
        if index < piece_count - 1 and size != piece_size:
            raise FabricDescriptorError("only the last descriptor piece may be short")
        piece_hash = _required_hex(piece["sha256"], "piece sha256")
        leaf_hashes.append(bytes.fromhex(piece_hash))
        offset += size

    if offset != total_size:
        raise FabricDescriptorError("descriptor totalSize does not match pieces")
    if _merkle_root_hex_from_leaf_hashes(leaf_hashes) != content_id:
        raise FabricIntegrityError("descriptor piece hashes do not match contentId")

    return descriptor


def _domain_leaf_hash(piece: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + piece).digest()


def _domain_node_hash(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _merkle_root_hex_from_leaf_hashes(leaf_hashes: list[bytes]) -> str:
    if not leaf_hashes:
        raise FabricDescriptorError("descriptor must contain at least one leaf hash")
    level = list(leaf_hashes)
    while len(level) > 1:
        next_level: list[bytes] = []
        for index in range(0, len(level), 2):
            left = level[index]
            right = level[index + 1] if index + 1 < len(level) else left
            next_level.append(_domain_node_hash(left, right))
        level = next_level
    return level[0].hex()


def _request_error_for_status(status: int, system_name: str) -> FabricHttpError:
    if status in (401, 403):
        return FabricAuthError(f"{system_name} authentication failed")
    if status == 404:
        return FabricNotFoundError(f"{system_name} route was not found")
    return FabricHttpError(f"{system_name} HTTP request failed with status {status}")


def _urlopen_bytes(
    *,
    url: str,
    method: str,
    headers: dict[str, str],
    body: bytes | None,
    timeout: float,
    max_bytes: int,
    system_name: str,
) -> bytes:
    request = urllib_request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib_request.urlopen(request, timeout=timeout) as response:  # nosec B310
            response_body = response.read(max_bytes + 1)
            if len(response_body) > max_bytes:
                raise FabricHttpError(f"{system_name} response exceeded configured maximum")
            return response_body
    except urllib_error.HTTPError as exc:
        raise _request_error_for_status(exc.code, system_name) from exc
    except urllib_error.URLError as exc:
        raise FabricHttpError(f"{system_name} HTTP request failed") from exc


def _join_base_url(base_url: str, path: str) -> str:
    parsed_path = urllib_parse.urlsplit(path)
    if parsed_path.scheme or parsed_path.netloc:
        raise FabricConfigError("fabric HTTP path must be relative")
    base = base_url.rstrip("/")
    suffix = path if path.startswith("/") else f"/{path}"
    return f"{base}{suffix}"


def _append_query(path: str, values: dict[str, str]) -> str:
    parsed = urllib_parse.urlsplit(path)
    query = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    query.update(values)
    return urllib_parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib_parse.urlencode(query),
            parsed.fragment,
        )
    )


def _validate_loopback_http_base_url(url: str) -> None:
    parsed = urllib_parse.urlsplit(url)
    if parsed.scheme != "http":
        raise FabricConfigError("fabric sidecar URL must use loopback http")
    if not parsed.hostname:
        raise FabricConfigError("fabric sidecar URL must include a host")
    hostname = parsed.hostname.lower()
    if hostname not in LOCALHOST_NAMES:
        raise FabricConfigError("fabric sidecar URL must target localhost or loopback")
    if parsed.username or parsed.password:
        raise FabricConfigError("fabric sidecar URL must not embed credentials")


def _validate_http_base_url(url: str) -> None:
    parsed = urllib_parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise FabricConfigError("fabric registry URL must use http or https")
    if not parsed.hostname:
        raise FabricConfigError("fabric registry URL must include a host")
    if parsed.username or parsed.password:
        raise FabricConfigError("fabric registry URL must not embed credentials")


def _validate_did(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value.startswith("did:multiverse:"):
        raise FabricConfigError(f"{field_name} must be a Multiverse DID")
    if any(char.isspace() for char in value):
        raise FabricConfigError(f"{field_name} must not contain whitespace")
    name_and_key = value.removeprefix("did:multiverse:")
    if "#" not in name_and_key:
        raise FabricConfigError(f"{field_name} must include a keyed DID fragment")
    name, key = name_and_key.split("#", 1)
    allowed_name_chars = "abcdefghijklmnopqrstuvwxyz0123456789._-"
    if not name or len(name) > 127:
        raise FabricConfigError(f"{field_name} repo label is invalid")
    if name[0] not in "abcdefghijklmnopqrstuvwxyz0123456789":
        raise FabricConfigError(f"{field_name} repo label is invalid")
    if any(char not in allowed_name_chars for char in name):
        raise FabricConfigError(f"{field_name} repo label is invalid")
    if len(key) != 64 or any(char not in "0123456789abcdef" for char in key):
        raise FabricConfigError(f"{field_name} key fragment must be lowercase sha256 hex")


def _required_hex(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise FabricDescriptorError(f"{field_name} must be a hex string")
    if len(value) != 64:
        raise FabricDescriptorError(f"{field_name} must be 64 hex characters")
    normalized = value.lower()
    if any(char not in "0123456789abcdef" for char in normalized):
        raise FabricDescriptorError(f"{field_name} must be lowercase sha256 hex")
    if value != normalized:
        raise FabricDescriptorError(f"{field_name} must be lowercase sha256 hex")
    return normalized


def _non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise FabricDescriptorError(f"{field_name} must be an integer")
    if value < 0:
        raise FabricDescriptorError(f"{field_name} must be non-negative")
    return value


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _float_env(env: dict[str, str], name: str, default: float) -> float:
    raw = env.get(name)
    if raw in (None, ""):
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise FabricConfigError(f"{name} must be a number") from exc
    if value <= 0:
        raise FabricConfigError(f"{name} must be positive")
    return value


def _int_env(env: dict[str, str], name: str, default: int) -> int:
    raw = env.get(name)
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise FabricConfigError(f"{name} must be an integer") from exc
    if value <= 0:
        raise FabricConfigError(f"{name} must be positive")
    return value


def _allowlist_dids_from_response(response: Any) -> set[str]:
    if response is None:
        return set()
    candidates: list[Any] = []
    if isinstance(response, list):
        candidates = response
    elif isinstance(response, dict):
        for key in ("allowlistedDids", "allowlist", "dids", "siblingDids"):
            value = response.get(key)
            if isinstance(value, list):
                candidates = value
                break
        else:
            systems = response.get("systems")
            if isinstance(systems, list):
                candidates = [system.get("did") for system in systems if isinstance(system, dict)]
    else:
        raise FabricAllowlistError("registry allowlist response must be an object or list")

    dids: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, str):
            raise FabricAllowlistError("registry allowlist contains a non-string DID")
        _validate_did(candidate, field_name="registry allowlist DID")
        dids.add(candidate)
    return dids


def _inbound_items_from_response(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, list):
        items = response
    elif isinstance(response, dict):
        items = None
        for key in ("items", "inbound", "deliveries", "messages"):
            value = response.get(key)
            if isinstance(value, list):
                items = value
                break
        if items is None:
            items = []
    else:
        raise FabricHttpError("registry inbound response must be an object or list")

    parsed_items: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            raise FabricHttpError("registry inbound item must be an object")
        parsed_items.append(item)
    return parsed_items


def _parse_inbound_item(item: dict[str, Any]) -> dict[str, Any]:
    from_did = item.get("fromDid") or item.get("from_did") or item.get("senderDid")
    to_did = item.get("toDid") or item.get("to_did") or item.get("recipientDid") or ""
    content_id = item.get("contentId") or item.get("content_id")
    _validate_did(from_did, field_name="inbound sender DID")
    if to_did:
        _validate_did(to_did, field_name="inbound recipient DID")
    content_id = _required_hex(content_id, "inbound contentId")
    return {
        "from_did": from_did,
        "to_did": to_did,
        "content_id": content_id,
        "descriptor": item.get("descriptor"),
        "secure": bool(item.get("secure") or item.get("encrypted") or item.get("ciphertext")),
    }


def _read_path_or_bytes(path_or_bytes: str | Path | bytes, max_payload_bytes: int) -> bytes:
    if isinstance(path_or_bytes, bytes):
        payload = path_or_bytes
    else:
        path = Path(path_or_bytes)
        payload = path.read_bytes()
    if len(payload) > max_payload_bytes:
        raise FabricConfigError("fabric payload exceeds configured maximum")
    return payload


def _require_allowlisted(did: str, allowlist: set[str]) -> None:
    if did not in allowlist:
        raise FabricAllowlistError("DID is not in the authenticated sibling allowlist")
