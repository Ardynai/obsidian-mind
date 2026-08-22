# Fabric Pack Schema

Somatic Fabric packs are verified bundles for distributing scientific content and provider extensions. They are intended for datasets, PDF lakes, model weights, CSI samples, workflow templates, adapter packs, plugin packs, benchmark packs, and result/provenance bundles.

The normative schema is Content Fabric v1.0.0 in [content-fabric.md](content-fabric.md). Somatic implements local shape validation, raw numeric JSON rejection, duplicate object-name rejection, integer-only JSON validation, Fabric-supported JCS canonicalization, signing payload construction, SHA-256 helpers, path prechecks, context license decisions, manifest/keyring/catalog validators, optional Ed25519 signing/verification, keyring replacement continuity, publisher threshold checks, signed catalog checks for local JSON fixtures, Phase 4G.2 shared fixture self-certification, and Phase 4G.3 Locus verification for the Somatic-origin shared fixture set. It does not implement torrent transport, WebSeed downloads, full runtime conformance, catalog serving, quarantine, sandboxing, explicit enablement, or plugin loading.

## `pack.json`

A pack manifest should include:

- `schemaVersion`
- `id`
- `name`
- `version`
- `description`
- `class`: `data` or `code`
- `type`: canonical data/code type
- `publisher`
- `license`
- `harnesses`
- `transport`
- `files`
- `createdAt`
- `signatures`

## Files and SHA-256 Verification

Each file entry should include:

- `path`
- `sha256`
- `size`
- `installTarget`
- `executable`

Somatic should verify every required file with SHA-256 before cataloging a pack. Phase 4B includes byte/path digest helpers only; full payload verification after fetch is future work. A file mismatch should block ingest.

## Ed25519 Signatures

The `signatures` array should include Ed25519 signatures over `JCS(object with top-level signatures set to [])`.

Signature fields should include:

- `algo`: `ed25519`
- `keyId`
- `sig`

Signature verification establishes publisher identity only when the key is trusted through the TUF-style keyring. Phase 4E can verify local Ed25519 signatures, publisher thresholds, keyring replacement continuity, and signed catalog thresholds when the optional Fabric crypto backend and a keyring are supplied. File hashes are still required.

Example local check:

```powershell
python -m somatic fabric check fixtures/fabric/crypto/signed-data-pack.json --keyring fixtures/fabric/crypto/keyring-signed.json
```

The fixtures under `fixtures/fabric/crypto/` are deterministic test vectors. Checked-in private keys are test-only material and must not be reused for real publishing.

## Transport

Transport entries may include:

- BitTorrent v1 magnet links.
- BitTorrent v1 info hashes.
- WebSeed URLs.
- Local file paths for offline fixtures.

Transport is not trust. Trust depends on hash verification, signature verification, quarantine policy, license gates, and local catalog policy.

## Data Packs and Code Packs

Data packs may include documents, datasets, model weights, CSI samples, workflow fixtures, and report examples. They should be verified before indexing or use.

Code packs may include adapters, plugins, skills, MCP servers, connectors, or agents. Code packs must be quarantined by default and must require explicit consent, sandboxing, and explicit enablement before execution. Code packs must never execute at install time.

Phase 4G.3 verifies that signed shared code/data pack manifests meet the configured publisher threshold in Somatic and Locus. That verification does not install, load, enable, sandbox, or execute the pack.

## Quarantine and Enablement

Code-pack manifests should declare:

- `quarantine_required: true`
- Requested permission scopes.
- Network, filesystem, sensor, lab, model, and export capabilities.
- Human-readable risk notes.
- Explicit enablement state.

Enablement should be local policy, not an automatic effect of downloading a pack.

## License Gates

License metadata should include:

- SPDX id or license label.
- Attribution requirements.
- Redistribution restrictions.
- Commercial-use restrictions.
- Data-use restrictions.
- Required acknowledgements.

Somatic should block ingest, indexing, execution, or export when required license gates are not satisfied.

## Catalogs

The local catalog should record:

- Verified pack metadata.
- File availability and hashes.
- Signature state.
- License gate state.
- Quarantine state.
- Enablement state.
- Provenance and ingest run id.

Remote catalog federation can let publishers advertise pack manifests without a central private registry. Local policy decides which remote catalogs, publishers, and pack types are trusted.

Phase 4G.3 validates catalog JSON shape locally and records Locus validation of the shared signed catalog fixture. Locus verifies the shared catalog signature through its Ed25519 primitive because no high-level catalog threshold verifier is exposed. HTTP catalog endpoints, WebSocket catalog events, and federation merge rules are future work.

## Somatic Use Cases

- PDF lakes for literature-only workflows.
- Biomedical datasets for hypothesis tournaments.
- Model weights for in-silico screening.
- CSI sample packs for WiFi CSI observation workflows.
- Workflow packs for reusable research modes.
- Adapter and plugin packs for provider integrations.
- Report fixture packs for reproducibility and review.
