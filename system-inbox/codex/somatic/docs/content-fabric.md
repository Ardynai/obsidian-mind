# Content Fabric v1.0.0

This document is Somatic's normative copy of the canonical Multiverse Content Fabric v1.0.0 standard. Somatic Fabric implementations must interoperate with the Locus implementation under `electron/content-fabric/` and with the shared harness family: Locus, Multiverse, kortex-audio, locus-evolution-lab, Somatic, and ardynos.

Interop is a protocol requirement, not a runtime dependency. Somatic must not depend on Locus, Multiverse, or any private harness to run.

Full runtime conformance is future work. Phase 3B added docs, fixtures, and lightweight precheck scaffolding. Phase 4B added local runtime prechecks. Phase 4C added optional local Ed25519/keyring verification for deterministic fixtures. Phase 4E adds raw JSON numeric rejection, keyring replacement continuity, signed catalog vectors, and Somatic-generated interop fixtures without certifying full conformance. Phase 4G.2 adds Somatic-generated shared fixtures and local self-certification. Phase 4G.3 verifies that shared fixture set with Locus.

## Fixed Primitives

- Text encoding is UTF-8 with no BOM.
- JSON canonicalization is RFC 8785 JCS.
- Fabric JSON uses integers only in `[0, 2^53-1]`; floats, exponents, leading-zero numbers, and plus-signed numbers are forbidden.
- Versions and SemVer values are strings.
- Hashes are SHA-256 lowercase hex unless a field explicitly says base64.
- Signatures are Ed25519.
- Signature bytes are encoded with base64 standard padding.
- Ed25519 public keys are raw 32-byte keys encoded with base64 standard padding.
- `keyId = lowercasehex(sha256(raw 32-byte public key))`.
- Timestamps are RFC 3339 UTC with `Z` and second precision.
- Pack ids are exactly `<namespace>/<name>`.
- `publisher.namespace` must equal the pack id namespace.
- Payload paths are POSIX relative paths with no empty, `.`, or `..` segment, no leading slash, no Windows drive, no backslash, and no NUL.

The signing payload for every signed Fabric object is `JCS(object with top-level signatures set to [])`, encoded as UTF-8 bytes. Signers must set the field to an empty array rather than removing it.

## `pack.json`

Every pack has a root `pack.json`. The file is part of the transported payload.

Required fields:

| Field | Rule |
| --- | --- |
| `schemaVersion` | SemVer string for this spec, currently `1.0.0` |
| `id` | `<namespace>/<name>` with canonical id segments |
| `name` | 1-200 character display name |
| `version` | SemVer 2.0.0 string; `id@version` is immutable once published |
| `class` | `data` or `code` |
| `type` | class-specific taxonomy |
| `license` | single SPDX id or `LicenseRef-*` |
| `publisher` | `{ namespace, displayName, keyId }` |
| `harnesses` | non-empty list of harness names or exactly `["*"]` |
| `transport` | BitTorrent v1 infohash and magnet metadata |
| `files` | non-empty array sorted by `path` |
| `createdAt` | RFC 3339 UTC timestamp |
| `signatures` | Ed25519 signatures sorted by `keyId`; may be empty only where policy permits |

Optional fields are `description` and sorted `dependencies`. Unknown fields are part of canonical signed bytes and must be preserved, but producers should not emit unknown top-level members in v1.

Data types are `model`, `asset-3d`, `asset-audio`, `asset-video`, `asset-image`, `dataset`, `document`, and `theme`.

Code types are `skill`, `mcp-server`, `plugin`, `connector`, and `agent`.

Each `files[]` entry includes:

```json
{
  "path": "relative/file.bin",
  "sha256": "64 lowercase hex",
  "size": 0,
  "installTarget": "publisher/pack/file.bin",
  "executable": false
}
```

`pack.json` itself is not listed in `files[]`.

`manifestDigest = "sha256:" + lowercasehex(sha256(JCS(pack.json with its real signatures)))`. Catalogs reference this fully signed manifest digest.

## Signing And Keyring

Fabric uses a TUF-style keyring. A `keyring.json` includes:

- `schemaVersion`
- positive integer `version`
- `expires`
- root keys
- `rootThreshold`
- publisher key sets and thresholds
- keyring signatures

Every key entry uses `algo: "ed25519"`, a 64-hex `keyId`, a base64 raw 32-byte `publicKey`, `status` of `active` or `revoked`, `validFrom`, and `validUntil`.

A replacement keyring is accepted only when:

- its version strictly increases
- it is not expired
- it meets its own active-root threshold
- it is signed by the previous keyring's active root keys at the previous `rootThreshold`

Publisher key rotation preserves signatures from revoked keys only when `pack.createdAt <= key.validUntil`.

## Data And Code Packs

Data packs are passive bytes and must never execute. They require path confinement, per-file SHA-256 verification, and transport infohash verification. Signatures are recommended; unsigned data may install only under explicit local policy and must be surfaced as unverified publisher content.

Code packs execute or inject behavior. They require publisher threshold signatures before install, quarantine before use, explicit user consent, sandboxed install, and explicit enablement. Code packs must never execute at install time.

Code state machine: `fetched -> verified -> quarantined -> consent -> installed -> enable -> enabled`. Verification failure goes to `rejected`.

## Transport

Content Fabric v1 uses BitTorrent v1 with WebTorrent-compatible magnets. `transport.infohash` is the 40-character lowercase hex v1 infohash. `transport.magnet` must include `xt=urn:btih:<infohash>` and an HTTPS `ws=` WebSeed. A `wss://` tracker is recommended when public swarm participation is allowed.

Transport is not trust. Consumers verify:

- observed torrent infohash equals `transport.infohash`
- every listed file matches `files[].sha256`
- manifest and catalog signatures meet local keyring policy
- license, quarantine, consent, and enablement policy pass

`infohashV2` and `ipfsCid` are optional or reserved metadata and never replace SHA-256 and v1 infohash checks in v1.

## Managed Layout

Harnesses may choose their own fabric root, but the logical layout is:

```text
fabric/
  keyring.json
  catalog.local.json
  keyring/
  catalog/
  quarantine/<namespace>/<name>/<version>/
  packs/<namespace>/<name>/<version>/
  .incoming/
  installed/
    skills/ mcp/ plugins/ connectors/ agents/
    models/ assets/ datasets/ documents/ themes/
```

Type directories:

| Type | Directory |
| --- | --- |
| `model` | `models/` |
| `asset-3d`, `asset-audio`, `asset-video`, `asset-image` | `assets/` |
| `dataset` | `datasets/` |
| `document` | `documents/` |
| `theme` | `themes/` |
| `skill` | `skills/` |
| `mcp-server` | `mcp/` |
| `plugin` | `plugins/` |
| `connector` | `connectors/` |
| `agent` | `agents/` |

`installTarget` resolves under the type directory and must remain strictly confined there. Payload symlinks must not escape the managed root.

## Catalog Protocol

Signed catalogs advertise packs but are not a trust root. Consumers verify catalog signatures, then verify each fetched pack independently.

Required HTTP bindings for future runtime conformance:

- `GET /fabric/catalog`
- `GET /fabric/pack/{id}/{version}` with the slash in `id` percent-encoded as `%2F`
- `GET /fabric/keyring`

Required WebSocket events for future runtime conformance:

```json
{ "type": "fabric_subscribe", "filter": { "class": null, "type": null, "harness": null } }
{ "type": "fabric_catalog", "packs": [] }
{ "type": "fabric_pack_published", "pack": {} }
{ "type": "fabric_unsubscribe" }
```

Federation merges remote catalog entries only as hints. Conflicting `id@version` entries with different `manifestDigest` values must be rejected.

## License Gate

Publicly publishable and seedable licenses are:

`MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `MPL-2.0`, `LGPL-3.0-or-later`, `GPL-2.0-or-later`, `GPL-3.0-or-later`, `AGPL-3.0-or-later`, `Unlicense`, `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `CC-BY-NC-4.0`, and `LicenseRef-Multiverse-Open`.

Private-only licenses such as `proprietary` and `LicenseRef-Internal-*` are allowed only for explicit first-party harness lists, without public trackers, and without IPFS CIDs. Private-only packs do not enter public catalogs and are not seeded.

License gates apply at publish, seed, catalog, and install.

## Conformance

Two implementations that conform to this standard over the same inputs must produce byte-identical canonical manifests, byte-identical signing payloads, and mutually verifiable signatures.

Somatic must later cross-verify generated manifests, signing payloads, keyrings, and catalogs against Locus `electron/content-fabric/` before claiming full Fabric conformance.

## Somatic Phase 4G.3 Status

Somatic currently implements local deterministic primitives for raw JSON numeric lexeme rejection, duplicate object-name rejection, integer-only JSON validation, Fabric-supported JCS canonicalization, signing payload construction, SHA-256 digesting, path prechecks, context license policy decisions, manifest/keyring/catalog shape validation, optional Ed25519 signature helpers, signed keyring root-threshold checks, signed keyring replacement continuity checks, signed pack publisher-threshold checks, signed catalog verification fixtures, shared fixture self-certification, and Locus verification evidence for the shared Somatic-origin fixture set.

Somatic must not claim full Content Fabric conformance until Locus-origin companion fixtures, broader runtime transport/catalog behavior, and install/quarantine policy are implemented. Phase 4G.3 does not implement BitTorrent/WebSeed networking, downloads, catalog servers, install/quarantine runtime, code execution, plugin enablement, external APIs, real secrets, or a Locus runtime dependency.
