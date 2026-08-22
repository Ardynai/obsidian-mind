# Fabric Conformance

Phase 3B defined Somatic's Content Fabric conformance targets and fixtures. Phase 4B added the first deterministic, dependency-free runtime primitives for local validation, digesting, signing payload construction, and shape checks. Phase 4C adds an optional local Ed25519/keyring foundation for deterministic test vectors. Phase 4D adds Locus interop preparation docs and placeholders. Phase 4E closes the first byte-conformance gaps with raw JSON numeric lexeme checks, keyring replacement continuity, signed catalog vectors, context license decisions, and Somatic-generated interop fixtures. Phase 4F runs partial local mutual verification with Locus fixtures and records the result in [fabric-mutual-verification-report.md](fabric-mutual-verification-report.md). Phase 4G.1 replaces the canonicalization scaffold with local RFC 8785/JCS canonicalization for the Fabric-supported JSON domain and adds local JCS vectors. Phase 4G.2 adds Somatic-generated shared interop fixtures and local Somatic self-certification. Phase 4G.3 verifies the shared fixture set with Locus. Full runtime conformance is still future work.

Partial Fabric implementations must not claim full Content Fabric runtime conformance. As of Phase 4G.3, Somatic claims local RFC 8785/JCS canonicalization for the Fabric-supported JSON domain plus Locus-certified shared Somatic-origin fixtures. Objects, arrays, strings, booleans, null, and non-negative safe integers in `[0, 2^53-1]` are supported; duplicate object names and invalid Unicode surrogate strings are rejected; object names sort by UTF-16 code units; arrays preserve order; canonical bytes are UTF-8 with no insignificant whitespace. Locus-origin companion fixtures, runtime transport, install/quarantine behavior, catalog servers, and production signing policy remain uncertified.

## Targets

Somatic Fabric must conform to:

- RFC 8785 JCS canonicalization.
- Integers-only JSON in `[0, 2^53-1]`.
- UTF-8 with no BOM.
- SHA-256 lowercase hex digests.
- Ed25519 signatures.
- `keyId = lowercasehex(sha256(raw 32-byte public key))`.
- Signing payload exactly equal to `JCS(object with top-level signatures set to [])`.
- TUF-style keyring verification.
- Keyring rotation continuity using previous active root keys.
- Exact `pack.json` field table in [content-fabric.md](content-fabric.md).
- Data vs code pack safety semantics.
- Code pack quarantine, explicit consent, sandboxed install, and explicit enablement.
- Code packs never execute at install time.
- Path confinement for payload paths and install targets.
- BitTorrent v1 infohash plus magnet/WebSeed transport metadata.
- Per-file SHA-256 verification after fetch.
- Signed catalog verification.
- HTTP catalog endpoints.
- WebSocket catalog events.
- Federation conflict rules.
- License gates at publish, seed, catalog, and install.

## Future Implementation Checklist

- Add Locus-origin companion fixtures and Somatic-side verification before making a broader interop certification claim.
- Keep raw JSON acceptance behind `loads_fabric_json()`, which rejects floats, exponents, leading-zero numbers, plus-signed numbers, negative numbers, and integers outside `[0, 2^53-1]` before accepting raw Fabric JSON text.
- Promote the Phase 4C optional Ed25519 helpers into full conformance once canonicalization and cross-implementation vectors are complete.
- Extend keyring rotation continuity only if future Locus vectors expose additional replacement policy cases beyond the current previous-root threshold and strict version checks.
- Enforce resolved path confinement with realpath checks.
- Reject symlink payload escapes.
- Verify observed BitTorrent v1 infohash.
- Verify every `files[].sha256`.
- Require trusted threshold signatures for all code packs.
- Quarantine code packs before install.
- Require explicit consent and sandboxing for code install.
- Keep code disabled until explicit enablement.
- Enforce license policy at publish, seed, catalog, and install.
- Extend signed catalog generation and verification with copied or independently generated Locus vectors.
- Implement `GET /fabric/catalog`, `GET /fabric/pack/{id}/{version}`, and `GET /fabric/keyring`.
- Implement WebSocket `fabric_subscribe`, `fabric_catalog`, `fabric_pack_published`, and `fabric_unsubscribe` messages.
- Reject federation conflicts where the same `id@version` has different `manifestDigest`.
- Expand cross-verification beyond the Phase 4F checked fixtures until Locus `electron/content-fabric/` and Somatic agree across the full vector set.

## Implemented Through Phase 4G.3

The current runtime foundation under `somatic/fabric/` provides:

- constants for schema version, classes, types, harness names, license allowlist, install directories, and required fields
- recursive integer-only JSON value validation with clear exception types
- raw JSON numeric lexeme validation for floats, exponents, leading zeros, plus signs, negatives, and out-of-range integers before parse
- RFC 8785/JCS canonicalization for the Fabric-supported JSON domain, including UTF-16 object-key ordering, preserved array order, JSON string escaping, UTF-8 bytes, and no insignificant whitespace
- duplicate object-name rejection when loading raw Fabric JSON
- Unicode scalar string validation that rejects invalid surrogate code points
- signing payload construction by setting top-level `signatures` to `[]`
- SHA-256 lowercase hex helpers for bytes and files
- scaffold manifest digests as `sha256:` plus SHA-256 over current canonical bytes
- path safety and install-target prechecks
- license gate prechecks and context decisions for publish, seed, catalog, and install
- manifest shape validation
- keyring shape validation
- catalog shape validation
- basic code-signature threshold precheck
- optional Ed25519 raw-key helpers when the Fabric crypto backend is installed
- deterministic `keyId = sha256(raw 32-byte public key)` derivation
- local object signing over the Fabric-supported JCS signing payload
- local signature verification over the Fabric-supported JCS signing payload
- signed keyring root-threshold verification for active root keys
- signed keyring replacement verification using previous active root threshold signatures and strict version increase
- publisher-threshold verification for signed pack manifests
- signed catalog publisher-key threshold verification for local catalog fixtures
- fixture loading helpers
- local CLI check: `python -m somatic fabric check <path>`
- optional CLI keyring verification for packs and catalogs: `python -m somatic fabric check <path> --keyring <keyring>`
- signing payload digest CLI: `python -m somatic fabric payload <path>`
- canonical JSON CLI: `python -m somatic fabric canonicalize <path>`
- manifest digest CLI: `python -m somatic fabric digest <path>`
- signed catalog verification CLI: `python -m somatic fabric check-catalog <catalog> --keyring <keyring>`
- shared fixture self-certification CLI: `python -m somatic fabric check-shared-fixtures <fixture-dir>`
- keyring rotation CLI: `python -m somatic fabric check-keyring-rotation <old> <new>`
- interop preparation helpers, placeholder fixture locations, and Somatic-generated exchange fixtures that do not import Locus
- partial local mutual verification report and metadata for checked Locus/Somatic pack, keyring, catalog, and rotation vectors
- shared Somatic-generated interop fixtures for Phase 4G.3 certification: signed data pack, signed code pack, signed keyring, signed catalog, expected digest metadata, and invalid rejection cases
- Locus verification evidence for the shared Somatic-origin fixtures at Locus commit `5f81ee360834dc6451c4ea35d7509325813d9d10`

Phase 4G.3 shared fixture certification is local, offline, and fixture-backed. It certifies the Somatic-origin shared fixture set with Locus but does not certify full Locus/Somatic runtime interop. Phase 4F, Phase 4G.2, and Phase 4G.3 cryptographic checks are local/offline and depend on the optional Fabric crypto backend or Locus's local Node crypto path. The Fabric layer still does not implement BitTorrent, WebSeed download, catalog serving, install, quarantine, sandbox, explicit enablement, or production signing policy.

## Fixtures

Conformance fixtures live in `fixtures/fabric/conformance/`.

The conformance fixtures use placeholder signatures. `expected-digests.json` records deterministic Phase 4B scaffold digests and explicitly marks them as non-final cross-implementation conformance vectors until full RFC 8785 and cross-harness crypto vectors are implemented.

Crypto test vectors live in `fixtures/fabric/crypto/`. They include a signed keyring, signed data/code packs, and an invalid signature pack. The private keys in `test-root-key.json` and `test-publisher-key.json` are checked in only as deterministic test material and must never be used for production Fabric signing.

Raw JSON numeric fixtures live in `fixtures/fabric/raw-json/`.

Local JCS canonicalization fixtures live in `fixtures/fabric/jcs/`. These cover basic objects, nested objects, UTF-16 key ordering, string escaping, signing-payload `signatures: []`, and safe integer boundaries. They are local Somatic vectors, not Locus mutual-certification fixtures.

Keyring rotation vectors live in `fixtures/fabric/crypto/rotation/`.

Signed catalog vectors live in `fixtures/fabric/crypto/signed-catalog.json` and `fixtures/fabric/crypto/invalid-catalog-signature.json`.

Interop placeholders, Somatic-generated exchange fixtures, and verification metadata live in `fixtures/fabric/interop/`. Phase 4G.3 Locus-verified shared fixtures live in `fixtures/fabric/interop/shared/`. Phase 4F through Phase 4G.3 did not copy Locus files because copied fixture licensing and repo context have not been explicitly recorded.

## Content Scope

The Fabric layer is for verified datasets, PDF lakes, model weights, CSI sample packs, workflow packs, adapter/plugin packs, benchmark packs, and result/provenance bundles.

Data packs and code packs have different safety semantics. Data packs are passive bytes. Code packs can execute or inject behavior and therefore require stronger trust, quarantine, consent, sandboxing, and explicit enablement.
