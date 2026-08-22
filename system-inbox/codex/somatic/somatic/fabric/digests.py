import hashlib
from pathlib import Path

from somatic.fabric.canonical import canonical_bytes


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def sha256_path(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_digest(manifest):
    return f"sha256:{sha256_hex(canonical_bytes(manifest))}"
