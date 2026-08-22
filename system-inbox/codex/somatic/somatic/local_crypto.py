"""Opt-in encryption at rest for local stores. Default stays plaintext + 0600.

Stores opt in with ``SOMATIC_ENCRYPT_STORES=1`` (also accepted: true/on/yes,
case-insensitive). Key material comes from ``SOMATIC_STORE_PASSPHRASE`` when
set, otherwise a per-store random key file next to the store
(``<store>.key``, created on first encrypted write, ``0600``).

Encryption uses the optional ``cryptography`` package (AES-256-GCM with an
scrypt-derived key) — never hand-rolled crypto. Core stays stdlib-only: this
module imports nothing non-stdlib until an encrypted write or decrypt is
actually attempted, and the plaintext default path never touches it.

On-disk envelope (JSON)::

    {"format": "somatic-encrypted-v1", "kdf": "scrypt", ...}

Failure policy matches every other store safeguard in this repo:
**undecryptable or corrupt files load as all-OFF / empty.** Erasure deletes
both the ciphertext and the key material.
"""

from __future__ import annotations

import json
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any

ENCRYPT_STORES_ENV = "SOMATIC_ENCRYPT_STORES"
STORE_PASSPHRASE_ENV = "SOMATIC_STORE_PASSPHRASE"
ENVELOPE_FORMAT = "somatic-encrypted-v1"
KDF_NAME = "scrypt"
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
KEY_BYTES = 32
NONCE_BYTES = 12

_TRUE_VALUES = frozenset({"1", "true", "on", "yes"})


def encryption_enabled() -> bool:
    """Whether stores should be written encrypted. Default OFF."""

    return os.environ.get(ENCRYPT_STORES_ENV, "").strip().lower() in _TRUE_VALUES


def is_envelope(raw: bytes) -> bool:
    """Cheap structural check for the encrypted-store envelope."""

    stripped = raw.lstrip()[:64]
    if not stripped.startswith(b"{"):
        return False
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return False
    return isinstance(payload, dict) and payload.get("format") == ENVELOPE_FORMAT


def key_path_for(store_path: Path | None) -> Path | None:
    if store_path is None:
        return None
    return Path(store_path).with_name(Path(store_path).name + ".key")


def _write_key_file(key_file: Path) -> bytes:
    material = secrets.token_bytes(KEY_BYTES)
    key_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(key_file.parent), prefix=".store-key-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(material)
        os.replace(tmp_name, key_file)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    try:
        os.chmod(key_file, 0o600)
    except OSError:
        pass
    return material


def key_material(store_path: Path | None, *, create: bool = False) -> bytes | None:
    """Passphrase bytes when configured, else the store's local key file.

    Returns None when no usable material exists (and ``create`` is False).
    """

    passphrase = os.environ.get(STORE_PASSPHRASE_ENV, "").strip()
    if passphrase:
        return b"somatic-passphrase:" + passphrase.encode("utf-8")
    key_file = key_path_for(store_path)
    if key_file is None:
        return None
    try:
        material = key_file.read_bytes()
    except OSError:
        material = b""
    if len(material) >= KEY_BYTES:
        return material
    if create:
        try:
            return _write_key_file(key_file)
        except OSError:
            return None
    return None


def erase_store_key(store_path: Path | None) -> None:
    """Right-to-erasure helper: delete the store's key file if it exists."""

    key_file = key_path_for(store_path)
    if key_file is None:
        return
    try:
        key_file.unlink()
    except FileNotFoundError:
        return


def _require_crypto():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    except ImportError as exc:
        raise RuntimeError(
            "SOMATIC_ENCRYPT_STORES is enabled but the optional 'cryptography' "
            "package is missing. Install an extra that provides it "
            "(e.g. pip install 'somatic[fabric]') or unset SOMATIC_ENCRYPT_STORES."
        ) from exc
    return AESGCM, Scrypt


def encrypt_bytes(material: bytes, plaintext: bytes) -> dict[str, Any]:
    """AES-256-GCM over ``plaintext`` with an scrypt-derived key."""

    AESGCM, Scrypt = _require_crypto()
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(NONCE_BYTES)
    kdf = Scrypt(salt=salt, length=KEY_BYTES, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
    key = kdf.derive(material)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    return {
        "format": ENVELOPE_FORMAT,
        "kdf": KDF_NAME,
        "kdf_params": {"n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P},
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex(),
    }


def decrypt_bytes(material: bytes, envelope: dict[str, Any]) -> bytes | None:
    """Inverse of :func:`encrypt_bytes`. None on any decryption failure."""

    try:
        AESGCM, Scrypt = _require_crypto()
        params = envelope.get("kdf_params")
        n = int(params.get("n")) if isinstance(params, dict) else SCRYPT_N
        r = int(params.get("r")) if isinstance(params, dict) else SCRYPT_R
        p = int(params.get("p")) if isinstance(params, dict) else SCRYPT_P
        salt = bytes.fromhex(str(envelope["salt"]))
        nonce = bytes.fromhex(str(envelope["nonce"]))
        ciphertext = bytes.fromhex(str(envelope["ciphertext"]))
        kdf = Scrypt(salt=salt, length=KEY_BYTES, n=n, r=r, p=p)
        key = kdf.derive(material)
        return AESGCM(key).decrypt(nonce, ciphertext, None)
    except Exception:
        return None


def decode_store_payload(raw: bytes, store_path: Path | None = None) -> dict[str, Any] | None:
    """Decode a store file body to its JSON object, encrypted or not.

    Encrypted envelopes are decrypted with the store's key material; wrong or
    unusable keys fail closed (None), matching the repo-wide all-OFF safeguard.
    Plaintext JSON decodes exactly as before. Any failure returns None.
    """

    if not isinstance(raw, (bytes, bytearray)):
        return None
    data = bytes(raw)
    if is_envelope(data):
        try:
            envelope = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            return None
        material = key_material(store_path, create=False)
        if material is None:
            return None
        plaintext = decrypt_bytes(material, envelope)
        if plaintext is None:
            return None
        try:
            payload = json.loads(plaintext.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            return None
        return payload if isinstance(payload, dict) else None
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def encode_store_payload(
    destination: Path,
    payload: dict[str, Any],
    *,
    prefix: str,
) -> Path | None:
    """Write ``payload`` encrypted when enabled; None means caller writes plaintext.

    Raises RuntimeError when encryption is enabled but ``cryptography`` is not
    importable, so an operator never believes a store is encrypted when it is
    not.
    """

    if not encryption_enabled():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    material = key_material(destination, create=True)
    if material is None:
        raise RuntimeError(f"cannot obtain key material for encrypted store: {destination}")
    envelope = encrypt_bytes(material, encoded.encode("utf-8"))
    envelope_encoded = json.dumps(envelope, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=prefix,
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(envelope_encoded)
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
