# Content Fabric

## Owns

Local Content Fabric fixture validation and signing helpers:

- `somatic/fabric/spec.py`
- `somatic/fabric/canonical.py`
- `somatic/fabric/manifest.py`
- `somatic/fabric/signing.py`
- `somatic/fabric/keyring.py`
- `somatic/fabric/catalog.py`
- `fixtures/fabric/`

## Main Flow

`python -m somatic fabric check <pack.json>` loads Fabric JSON, rejects unsupported number forms and duplicate keys, validates the manifest shape, checks license/path/transport/signature policy, and optionally verifies publisher signatures against a local keyring.

Catalog and keyring commands use the same primitives: canonical bytes, signing payloads, SHA-256 digests, Ed25519 verification when the optional crypto backend is available, and fixture-driven threshold checks.

## Gotchas

- Fabric here is metadata and fixture validation, not a pack runtime.
- There is no BitTorrent/WebSeed downloader, catalog server, install/quarantine runtime, plugin enablement, sandbox execution, external API call, or production signing path.
- Test private keys in fixtures are deterministic vectors only. Never use them for real publishing.
- Private or non-allowlisted licenses are intentionally blocked from public publish/seed/catalog contexts.

## Start Reading

Read `docs/content-fabric.md`, then `somatic/fabric/spec.py`, `canonical.py`, `manifest.py`, `keyring.py`, and `catalog.py`.
