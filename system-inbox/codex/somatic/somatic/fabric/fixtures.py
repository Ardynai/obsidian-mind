from pathlib import Path

from somatic.fabric.canonical import loads_fabric_json


FABRIC_CONFORMANCE_FIXTURES = (
    "README.md",
    "sample-pack-signing-payload.json",
    "sample-pack-signed.json",
    "sample-keyring.json",
    "sample-catalog.json",
    "expected-digests.json",
    "invalid-float-pack.json",
    "invalid-path-pack.json",
    "invalid-code-unsigned-pack.json",
    "invalid-license-pack.json",
)


def conformance_fixture_root(repo_root=None):
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
    return root / "fixtures" / "fabric" / "conformance"


def load_conformance_fixture(filename, repo_root=None):
    if filename not in FABRIC_CONFORMANCE_FIXTURES:
        raise ValueError(f"Unknown Fabric conformance fixture: {filename}")
    path = conformance_fixture_root(repo_root) / filename
    return loads_fabric_json(path.read_text(encoding="utf-8"))
