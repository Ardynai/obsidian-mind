import base64
import hashlib


class FabricCryptoError(ValueError):
    """Raised when Fabric cryptographic input is malformed."""


class CryptoUnavailableError(RuntimeError):
    """Raised when optional Fabric crypto support is not installed."""


try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )

    CRYPTO_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only when optional extra is absent
    InvalidSignature = None
    Ed25519PrivateKey = None
    Ed25519PublicKey = None
    Encoding = None
    NoEncryption = None
    PrivateFormat = None
    PublicFormat = None
    CRYPTO_AVAILABLE = False


def require_crypto_backend():
    if not CRYPTO_AVAILABLE:
        raise CryptoUnavailableError(
            "Fabric cryptographic verification requires the optional fabric extra."
        )


def private_key_from_raw_bytes(raw_private_key):
    require_crypto_backend()
    if not isinstance(raw_private_key, bytes) or len(raw_private_key) != 32:
        raise FabricCryptoError("Ed25519 private key must be raw 32 bytes")
    return Ed25519PrivateKey.from_private_bytes(raw_private_key)


def private_key_raw_bytes(private_key):
    require_crypto_backend()
    return private_key.private_bytes(
        encoding=Encoding.Raw,
        format=PrivateFormat.Raw,
        encryption_algorithm=NoEncryption(),
    )


def public_key_raw_bytes(public_key):
    require_crypto_backend()
    return public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)


def public_key_base64(public_key):
    return base64.b64encode(public_key_raw_bytes(public_key)).decode("ascii")


def public_key_from_base64(value):
    require_crypto_backend()
    raw = _decode_base64(value, "Ed25519 public key")
    if len(raw) != 32:
        raise FabricCryptoError("Ed25519 public key must decode to raw 32 bytes")
    return Ed25519PublicKey.from_public_bytes(raw)


def key_id_for_public_key_bytes(raw_public_key):
    if not isinstance(raw_public_key, bytes) or len(raw_public_key) != 32:
        raise FabricCryptoError("Ed25519 public key must be raw 32 bytes")
    return hashlib.sha256(raw_public_key).hexdigest()


def key_id_for_public_key(public_key):
    return key_id_for_public_key_bytes(public_key_raw_bytes(public_key))


def signature_to_base64(signature):
    if not isinstance(signature, bytes) or len(signature) != 64:
        raise FabricCryptoError("Ed25519 signature must be raw 64 bytes")
    return base64.b64encode(signature).decode("ascii")


def signature_from_base64(value):
    signature = _decode_base64(value, "Ed25519 signature")
    if len(signature) != 64:
        raise FabricCryptoError("Ed25519 signature must decode to raw 64 bytes")
    return signature


def sign_bytes(private_key, payload):
    require_crypto_backend()
    if not isinstance(payload, bytes):
        raise FabricCryptoError("Payload to sign must be bytes")
    return private_key.sign(payload)


def verify_signature_bytes(public_key, payload, signature):
    require_crypto_backend()
    if not isinstance(payload, bytes):
        raise FabricCryptoError("Payload to verify must be bytes")
    if not isinstance(signature, bytes) or len(signature) != 64:
        raise FabricCryptoError("Ed25519 signature must be raw 64 bytes")
    try:
        public_key.verify(signature, payload)
        return True
    except InvalidSignature:
        return False


def _decode_base64(value, label):
    if not isinstance(value, str):
        raise FabricCryptoError(f"{label} must be base64 text")
    try:
        return base64.b64decode(value, validate=True)
    except Exception as exc:
        raise FabricCryptoError(f"{label} must be base64 standard with padding") from exc
