# Fabric Locus Interop Preparation

Current status: Phase 4G.3 shared fixture certification achieved for Somatic-origin fixtures, with Phase 4F partial mutual verification preserved and full runtime interop not certified.

Phase 4D inspected the local Locus Content Fabric implementation and added Somatic-side planning docs, placeholder fixture locations, and dependency-free helper scaffolding. Phase 4E adds clean-room Somatic vectors for raw JSON numeric rejection, signing payload checks, signed catalogs, keyring rotation continuity, and fixture exchange metadata. Phase 4F runs actual local fixture verification in both directions and records the result in [fabric-mutual-verification-report.md](fabric-mutual-verification-report.md). Phase 4G.1 performs a local Somatic JCS implementation/vector pass only. Phase 4G.2 creates shared Somatic-origin fixtures and self-certifies them locally. Phase 4G.3 verifies those shared fixtures with Locus commit `5f81ee360834dc6451c4ea35d7509325813d9d10`. It does not copy Locus code, import Locus modules as a Somatic runtime dependency, start Locus services, add BitTorrent networking, download packs, install packs, execute code packs, or add HTTP/WS catalog servers to Somatic.

## Locus Implementation Inspected

Path inspected:

```text
C:\AI\locus\electron\content-fabric\
```

Local Locus commit used for Phase 4F verification:

```text
79f480d592ec82e879b7588a25bad6b4ea2536ca
```

Previously documented Locus commit: `a600ce1caad8efd1178966146f6fcb39aa846fc9`.

Phase 4G.1 read-only reference inspection observed the local Locus checkout at commit `94e6d3bf5ca35d7a99fdc94b85a836af2e94a6c8`. That checkout had unrelated working-tree changes, so it was used only as a behavior reference, not as mutual-verification evidence.

Phase 4G.3 used the current local Locus checkout at commit `5f81ee360834dc6451c4ea35d7509325813d9d10` for shared fixture verification.

Primary Locus files inspected:

- `manifest.ts`: Fabric constants, raw JSON integer lexeme checks, canonicalization scaffold, signing payload, manifest digest, pack validation, catalog validation, license policy, path syntax checks.
- `signing.ts`: Ed25519 signing/verification, raw public-key export, keyId derivation, first-party keyring, publisher threshold verification, root threshold verification, keyring expiration, and keyring replacement continuity.
- `storage.ts`: managed layout, keyring persistence gate, file SHA-256 verification, symlink rejection, storage quota, realpath confinement, code-pack quarantine/consent checks, and install records.
- `manager.ts`: local catalog generation, catalog entry publication, manifest lookup, and storage usage.
- `torrent-service.ts`: WebTorrent-backed add/seed/status scaffolding with quota/rate-limit hooks.
- `drop-folder.ts`: `.incoming` drop folder import path and data-pack confirmation boundary.
- `ipc.ts` and `index.ts`: Electron runtime creation and IPC handlers.
- `C:\AI\locus\electron\server\routes\fabric.ts`: local HTTP catalog/keyring/pack routes.
- `C:\AI\locus\electron\server\stream.ts`: WebSocket `fabric_subscribe`, `fabric_catalog`, `fabric_pack_published`, and `fabric_unsubscribe` handling.
- `C:\AI\locus\tests\content\content-fabric.test.ts` and `C:\AI\locus\tests\security\content-fabric-security.test.ts`: canonicalization, validation, signing, trust, path, license, quarantine, quota, drop-folder, and torrent option coverage.

## Somatic Implementation Modules

Somatic Fabric modules relevant to interop:

- `somatic/fabric/spec.py`
- `somatic/fabric/canonical.py`
- `somatic/fabric/digests.py`
- `somatic/fabric/pathing.py`
- `somatic/fabric/crypto.py`
- `somatic/fabric/signing.py`
- `somatic/fabric/manifest.py`
- `somatic/fabric/keyring.py`
- `somatic/fabric/catalog.py`
- `somatic/fabric/interop.py`
- `somatic/cli/main.py`

Somatic fixtures relevant to future exchange:

- `fixtures/fabric/conformance/`
- `fixtures/fabric/crypto/`
- `fixtures/fabric/interop/`

## Expected Interop Contract

Somatic and Locus must eventually agree on:

- byte-identical UTF-8 canonical JSON for the same Fabric object
- byte-identical signing payloads where top-level `signatures` is `[]`
- identical `manifestDigest` values for signed manifests
- identical Ed25519 public-key raw bytes and `keyId` derivation
- mutual acceptance of valid signed keyrings
- mutual rejection of expired, under-threshold, wrong-key, malformed, and revoked-key cases
- mutual acceptance of trusted publisher threshold signatures
- mutual rejection of unsigned code packs, mismatched publisher namespaces, bad paths, bad licenses, and malformed transport metadata
- catalog entry agreement for `id@version`, `manifestDigest`, `infohash`, publisher key id, size, type, class, and license

## Fixture Exchange Plan

No Locus fixtures were copied in Phase 4F because the licensing and repo-context basis for copying was not explicitly established.

Future fixture exchange should use `fixtures/fabric/interop/`. Phase 4G.2 adds the Somatic-origin shared fixture set under `fixtures/fabric/interop/shared/`; Phase 4G.3 certifies that set with Locus. Locus-owned fixture generation and Somatic-side certification remain future work.

The exchange should include:

1. Record the Locus source commit, source path, license basis, file names, and SHA-256 digest for each copied artifact.
2. Copy or derive a Locus signed data pack manifest, signed code pack manifest, signed keyring, expired/under-threshold keyring, wrong-key signature case, and invalid path/license cases.
3. Export the matching Somatic-generated shared vectors from `fixtures/fabric/interop/shared/` or regenerate them with the same deterministic test-only key material.
4. Add a metadata manifest that records which implementation generated each vector, whether private-key material is test-only, and which local verification was attempted. Phase 4F updates `somatic-generated-metadata.json` with local mutual-verification evidence for Somatic-origin vectors. Phase 4G.3 updates `shared-expected.json` with local Somatic self-certification and Locus verification evidence.
5. Add tests that skip when the Locus checkout is absent, but run mutual verification when `C:\AI\locus\electron\content-fabric\` is present.
6. Keep the exchange offline: no network calls, no downloads, no install, no code execution, no HTTP/WS servers.

## Mutual Verification

Mutual verification means both implementations independently verify the same artifacts without importing each other's runtime:

- Locus verifies Somatic-generated canonical bytes, signing payloads, manifest digests, signatures, keyrings, and rejection fixtures.
- Somatic verifies Locus-generated canonical bytes, signing payloads, manifest digests, signatures, keyrings, and rejection fixtures.
- Both sides produce the same pass/fail result and the same important derived values for every shared vector.

Importing Locus code into Somatic or importing Somatic code into Locus is not mutual verification. The two projects should exchange files and compare derived outputs.

## Future Test Command Shape

Future Somatic interop tests should remain optional and local:

```powershell
python -m unittest tests.test_fabric_interop_placeholders
python -m unittest tests.test_fabric_interop_locus_vectors
python -m unittest tests.test_fabric_shared_interop_fixtures
python -m somatic fabric check-shared-fixtures fixtures/fabric/interop/shared
```

The second command is future work. It should skip cleanly when the Locus checkout or copied fixtures are absent.

Local checks used in Phase 4F include:

```powershell
python -m unittest tests.test_fabric_interop_metadata
python -m somatic fabric payload fixtures/fabric/crypto/signed-code-pack.json
python -m somatic fabric check-keyring-rotation fixtures/fabric/crypto/rotation/previous-keyring.json fixtures/fabric/crypto/rotation/valid-rotated-keyring.json
```

Locus checks used in Phase 4F:

```powershell
npm run test:connectivity
npm run test:content
npm run test:security
```

## Current Status

Phase 4G.3 current status:

- Locus implementation path found and inspected.
- Locus commit `79f480d592ec82e879b7588a25bad6b4ea2536ca` used for actual verification.
- Locus commit `94e6d3bf5ca35d7a99fdc94b85a836af2e94a6c8` inspected read-only in Phase 4G.1 as behavior reference only.
- Locus commit `5f81ee360834dc6451c4ea35d7509325813d9d10` used for Phase 4G.3 shared fixture certification.
- Somatic modules and gaps mapped.
- Somatic now has local Fabric-supported JCS vectors under `fixtures/fabric/jcs/`.
- Somatic now has `python -m somatic fabric canonicalize <json-file>` for local canonical JSON output.
- Somatic now has shared Phase 4G.2 fixtures under `fixtures/fabric/interop/shared/`.
- Somatic now has `fabric digest`, `fabric check-catalog`, and `fabric check-shared-fixtures` CLI helpers for local shared fixture self-certification.
- Locus matched Phase 4G.2 shared fixture canonical bytes, signing payload hashes, manifest digests, keyring trust, pack signatures, catalog shape, catalog signature primitive verification, and invalid rejection vectors.
- Fixture placeholder folder created.
- Somatic-generated interop pack, keyring, catalog, and metadata fixtures added.
- Raw JSON, keyring rotation, and signed catalog vectors added for local tests.
- Locus verified the Somatic-generated pack/keyring and matched checked payload/digest values.
- Somatic verified Locus-owned pack/keyring fixtures.
- Somatic-generated catalog shape was verified by Locus, and its signature verified with Locus's Ed25519 primitive.
- High-level catalog signature threshold verification on the Locus side remains incomplete or caller-enforced.
- No Locus files copied.
- Shared fixture certification achieved for Somatic-origin fixtures only.
- No full runtime interop certification claim.
- No runtime dependency on Locus.
- No transport, catalog server, install, quarantine, or execution runtime added to Somatic.
- Locus-origin companion fixtures remain future work.
