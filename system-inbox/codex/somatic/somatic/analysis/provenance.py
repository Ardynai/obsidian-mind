import hashlib
import json
from pathlib import Path


def hash_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_payload(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_analysis_provenance(source_files, artifacts):
    files = [
        {
            "name": Path(path).name,
            "path": str(Path(path)),
            "sha256": hash_file(path),
        }
        for path in source_files
    ]
    artifact_hashes = {
        key: {
            "hash": hash_payload(value),
            "hash_algorithm": "sha256-json",
        }
        for key, value in sorted(artifacts.items())
    }
    return {
        "schema_version": 1,
        "agent_role": "Finch",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "dependencies": ["python-standard-library"],
        "network_calls": False,
        "external_api_calls": False,
        "package_downloads": False,
        "source_files": files,
        "artifacts": artifact_hashes,
    }
