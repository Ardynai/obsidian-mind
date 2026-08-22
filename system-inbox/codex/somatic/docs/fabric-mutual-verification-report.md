# Fabric Mutual Verification Report

Current status: Phase 4G.3 shared fixture certification achieved for Somatic-origin fixtures. Full Content Fabric runtime interop is not certified.

Phase 4F ran local, offline checks between Somatic and Locus Content Fabric test fixtures. No Locus source files were modified. No Locus files were copied into Somatic. No dependencies were installed, no packs were downloaded, no packs were installed, no code packs were executed or enabled, no HTTP or WebSocket catalog servers were added, and no production secrets were used.

## Implementations

| Field | Value |
| --- | --- |
| Somatic repo | `C:\AI\somatic` |
| Somatic commit at verification | `ec74d1b31edc0e52e02f1a73cb65b61fa6484931` |
| Locus repo | `C:\AI\locus` |
| Locus implementation path | `C:\AI\locus\electron\content-fabric\` |
| Locus commit inspected | `79f480d592ec82e879b7588a25bad6b4ea2536ca` |
| Locus commit used for Phase 4G.3 shared fixture verification | `5f81ee360834dc6451c4ea35d7509325813d9d10` |
| Previously documented Locus commit | `a600ce1caad8efd1178966146f6fcb39aa846fc9` |

The Locus checkout was newer than the previously inspected commit. Phase 4F records the actual local commit used for verification.

## Locus Entry Points Found

| Area | Entry point |
| --- | --- |
| Package tests | `npm run test:content`, `npm run test:connectivity`, `npm run test:security` |
| Test runner | `node scripts/run-electron-node-tests.cjs .tmp-tests/tests/<area>/*.test.js` after `tsc -p tsconfig.test.json` |
| Existing Locus-owned Somatic fixture | `C:\AI\locus\tests\fixtures\somatic-fabric\pack.json` and `keyring.json` |
| Raw JSON and canonicalization | `electron/content-fabric/manifest.ts`: `parseFabricJson`, `canonicalize`, `signingPayload`, `manifestDigest` |
| Pack validation | `electron/content-fabric/manifest.ts`: `validatePackManifest` |
| Catalog validation | `electron/content-fabric/manifest.ts`: `validateCatalog` |
| Pack signature verification | `electron/content-fabric/signing.ts`: `verifyPackManifest` |
| Keyring verification | `electron/content-fabric/signing.ts`: `verifyKeyring`, `assertTrustedKeyring` |
| Ed25519 primitive | `electron/content-fabric/signing.ts`: `verifyEd25519Signature` |

No dedicated Fabric CLI was found in Locus. The reproducible local entrypoint is the test harness plus compiled test modules under `.tmp-tests/` after the TypeScript test build.

## Commands Attempted

Locus-side commands:

```powershell
npm run test:connectivity
npm run test:content
npm run test:security
node -e "<verify Somatic interop fixtures with Locus compiled Fabric modules>"
node -e "<verify Locus-owned fixture digests with Locus compiled Fabric modules>"
node -e "<verify Somatic rotation fixtures with Locus verifyKeyring>"
```

Somatic-side commands against Locus-owned fixtures:

```powershell
python -m somatic fabric check "C:\AI\locus\tests\fixtures\somatic-fabric\pack.json" --keyring "C:\AI\locus\tests\fixtures\somatic-fabric\keyring.json"
python -m somatic fabric payload "C:\AI\locus\tests\fixtures\somatic-fabric\pack.json"
```

Somatic-side commands against Somatic fixtures:

```powershell
python -m somatic fabric check fixtures/fabric/interop/somatic-generated-pack.json --keyring fixtures/fabric/interop/somatic-generated-keyring.json
python -m somatic fabric check fixtures/fabric/interop/somatic-generated-catalog.json --keyring fixtures/fabric/interop/somatic-generated-keyring.json
```

## Results

| Direction | Artifact | Result | Evidence |
| --- | --- | --- | --- |
| Somatic-generated fixtures -> Locus | `somatic-generated-pack.json` with `somatic-generated-keyring.json` | Verified | Locus `validatePackManifest` returned valid, `verifyPackManifest` returned trusted with required/valid signatures `1/1`. |
| Somatic-generated fixtures -> Locus | `somatic-generated-keyring.json` | Verified | Locus `verifyKeyring` returned trusted with required/valid signatures `1/1`. |
| Somatic-generated fixtures -> Locus | `somatic-generated-catalog.json` shape | Verified | Locus `validateCatalog` returned valid with no errors. |
| Somatic-generated fixtures -> Locus | `somatic-generated-catalog.json` signature | Verified with primitive, not high-level catalog verifier | Locus `verifyEd25519Signature(signingPayload(catalog), signature, publisherKey)` returned true. Locus does not expose a catalog signature threshold verifier equivalent to Somatic's `verify_catalog_signature_threshold`. |
| Locus-owned fixtures -> Somatic | `C:\AI\locus\tests\fixtures\somatic-fabric\pack.json` with `keyring.json` | Verified | Somatic CLI returned `Fabric check: valid pack.json` and `crypto: publisher threshold verified`. |
| Locus-owned fixtures -> Somatic | Locus-owned fixture keyring | Verified | Somatic `verify_keyring_root_threshold` returned trusted with required/valid signatures `1/1`. |
| Locus-owned fixtures -> Somatic | Locus-owned catalog fixture | Not attempted | No Locus-owned catalog fixture was found under `tests\fixtures\somatic-fabric`. |
| Somatic rotation vectors -> Locus | `fixtures/fabric/crypto/rotation/*` | Verified | Locus `verifyKeyring` accepted the valid rotation and rejected equal-version, expired, and under-threshold replacement vectors. |

## Byte-Level Checks

| Artifact | Derived value | Somatic | Locus | Result |
| --- | --- | --- | --- | --- |
| Somatic generated pack | signing payload SHA-256 | `6236ece6053407088933ed2b9a7fd59fa171885a1e94d16d7c68e65229cd4e4b` | `6236ece6053407088933ed2b9a7fd59fa171885a1e94d16d7c68e65229cd4e4b` | Match |
| Somatic generated pack | manifest digest | `sha256:5690816743f63a8ecdf3ea8209ba998ec73d710ae25a70fc773491240b8cf465` | `sha256:5690816743f63a8ecdf3ea8209ba998ec73d710ae25a70fc773491240b8cf465` | Match |
| Somatic generated catalog | signing payload SHA-256 | `c1aee1b7cfb78107e77a48ce0b30323886bcfd80d32cebf7df843e6cdb3241a9` | `c1aee1b7cfb78107e77a48ce0b30323886bcfd80d32cebf7df843e6cdb3241a9` | Match |
| Locus-owned pack fixture | signing payload SHA-256 | `04ec1d7c8217a563f880aefa3b0f65b84b730ed14dbb6e00364e854a2f044ce6` | `04ec1d7c8217a563f880aefa3b0f65b84b730ed14dbb6e00364e854a2f044ce6` | Match |
| Locus-owned pack fixture | manifest digest | `sha256:e6bb73a7c7ab08b4019a7a5c1cc6323bc5b71c0e59ffc4e7d4e44020dcbf4788` | `sha256:e6bb73a7c7ab08b4019a7a5c1cc6323bc5b71c0e59ffc4e7d4e44020dcbf4788` | Match |

No canonical byte or signing payload byte mismatch was observed for the checked pack and catalog fixtures. This is not a full RFC 8785/JCS certification because the vector set is still narrow.

## Mismatch Analysis

No pack, keyring, signature, or checked signing-payload mismatch was observed.

Known incomplete areas:

- Locus exposes catalog shape validation and Ed25519 signature primitives, but no high-level signed catalog threshold verifier was found.
- No Locus-owned catalog fixture was found for Somatic to verify.
- Full RFC 8785/JCS edge vectors for Unicode normalization, escaping, and broader numeric/parser behavior remain incomplete.
- Somatic still has no transport, download, install, quarantine, enablement, HTTP catalog server, or WebSocket catalog runtime.

## Certification Boundary

This report records verified local fixture compatibility for the checked vectors only. It does not certify full Content Fabric interop, full RFC 8785 conformance, transport compatibility, install behavior, catalog-server behavior, or production signing policy.

## Phase 4G.2 Addendum

Phase 4G.2 adds Somatic-generated shared fixtures under `fixtures/fabric/interop/shared/` and self-certifies them locally with Somatic. This is a successor fixture-generation pass, not a new Locus verification pass. Locus mutual verification of the shared fixtures remains Phase 4G.3.

The added shared set includes a signed code pack, signed data pack, signed keyring, signed catalog, expected digest metadata, and invalid rejection fixtures for pack signature, catalog signature, and keyring threshold behavior. The deterministic private keys are test-vector-only material in `fixtures/fabric/crypto/` and must not be used for production signing.

The Phase 4G.2 addendum does not copy Locus files, import Locus code, start Locus services, add networking, download or install packs, quarantine or enable code packs, expose HTTP/WS catalog servers, use external APIs, or introduce production secrets.

## Phase 4G.3 Shared Fixture Certification

Phase 4G.3 verified the Somatic shared fixtures through the current local Locus checkout:

| Field | Value |
| --- | --- |
| Locus commit used | `5f81ee360834dc6451c4ea35d7509325813d9d10` |
| Locus branch | `fabric/cross-impl-fixture` |
| Locus implementation path | `C:\AI\locus\electron\content-fabric\` |
| Somatic shared fixture path | `fixtures/fabric/interop/shared/` |
| Result | shared fixture certification achieved |

Locus commands run:

```powershell
cd C:\AI\locus
npm run test:content
npm run test:security
npm run test:connectivity
@'<PowerShell here-string verifier>'@ | node -
```

The stdin verifier loaded `.tmp-tests/electron/content-fabric/manifest.js` and `.tmp-tests/electron/content-fabric/signing.js`, then used Locus `parseFabricJson`, `canonicalize`, `signingPayload`, `manifestDigest`, `validatePackManifest`, `validateCatalog`, `verifyPackManifest`, `verifyKeyring`, and `verifyEd25519Signature` against the shared fixture files.

Somatic commands run for symmetry:

```powershell
python -m somatic fabric check fixtures/fabric/interop/shared/shared-pack.json --keyring fixtures/fabric/interop/shared/shared-keyring.json
python -m somatic fabric check-catalog fixtures/fabric/interop/shared/shared-catalog.json --keyring fixtures/fabric/interop/shared/shared-keyring.json
python -m somatic fabric check-shared-fixtures fixtures/fabric/interop/shared
python -m somatic fabric payload fixtures/fabric/interop/shared/shared-pack.json
python -m somatic fabric digest fixtures/fabric/interop/shared/shared-pack.json
```

| Fixture | Locus result | Evidence |
| --- | --- | --- |
| `shared-pack.json` | Verified | canonical SHA-256, signing-payload SHA-256, manifest digest, shape validation, and publisher threshold signature all matched or passed. |
| `shared-data-pack.json` | Verified | canonical SHA-256, signing-payload SHA-256, manifest digest, shape validation, and publisher threshold signature all matched or passed. |
| `shared-keyring.json` | Verified | canonical SHA-256 and signing-payload SHA-256 matched; `verifyKeyring` trusted the keyring with required/valid root signatures `1/1`. |
| `shared-catalog.json` | Verified with primitive | canonical SHA-256, signing-payload SHA-256, and shape validation matched or passed; catalog signature was `verified-with-locus-ed25519-primitive-no-high-level-catalog-verifier`. |
| invalid shared signature pack | Rejected | `verifyPackManifest` returned untrusted with required/valid signatures `1/0`. |
| invalid shared catalog signature | Rejected with primitive | `validateCatalog` still accepted the shape; `verifyEd25519Signature(signingPayload(catalog), signature, publisherKey)` returned false. |
| invalid shared keyring threshold | Rejected | `verifyKeyring` rejected `rootThreshold` greater than root key count. |

## Phase 4G.3 Byte-Level Checks

| Artifact | Derived value | Somatic expected | Locus result | Result |
| --- | --- | --- | --- | --- |
| `shared-pack.json` | canonical SHA-256 | `37e1bd59cd6877c236e4aa1500368f5fd17322dadd2063f95bebe76175856b69` | `37e1bd59cd6877c236e4aa1500368f5fd17322dadd2063f95bebe76175856b69` | Match |
| `shared-pack.json` | signing payload SHA-256 | `1920e5c9fcf6bec88befebb9be4f7046790b04111db34f92b8f1fe01d1af8dd9` | `1920e5c9fcf6bec88befebb9be4f7046790b04111db34f92b8f1fe01d1af8dd9` | Match |
| `shared-pack.json` | manifest digest | `sha256:37e1bd59cd6877c236e4aa1500368f5fd17322dadd2063f95bebe76175856b69` | `sha256:37e1bd59cd6877c236e4aa1500368f5fd17322dadd2063f95bebe76175856b69` | Match |
| `shared-data-pack.json` | canonical SHA-256 | `31c66ec2c9b86c07241fec3b3fea7e6d7fcfce9656fce8e63738d23d93d3a7e6` | `31c66ec2c9b86c07241fec3b3fea7e6d7fcfce9656fce8e63738d23d93d3a7e6` | Match |
| `shared-data-pack.json` | signing payload SHA-256 | `b8331c8b3cb061ba95481c954df8f9145becb801c0b5af188e54d729f39971da` | `b8331c8b3cb061ba95481c954df8f9145becb801c0b5af188e54d729f39971da` | Match |
| `shared-data-pack.json` | manifest digest | `sha256:31c66ec2c9b86c07241fec3b3fea7e6d7fcfce9656fce8e63738d23d93d3a7e6` | `sha256:31c66ec2c9b86c07241fec3b3fea7e6d7fcfce9656fce8e63738d23d93d3a7e6` | Match |
| `shared-keyring.json` | canonical SHA-256 | `5bb06368f9eef50e8bd62d5cf7ef58e7a2dc11faf7cb9da8de54a0ed92658069` | `5bb06368f9eef50e8bd62d5cf7ef58e7a2dc11faf7cb9da8de54a0ed92658069` | Match |
| `shared-keyring.json` | signing payload SHA-256 | `f87b6364ee09b822ac5ac88e1e1982a102e88f156737c334c9f9ed08dfba6ffa` | `f87b6364ee09b822ac5ac88e1e1982a102e88f156737c334c9f9ed08dfba6ffa` | Match |
| `shared-catalog.json` | canonical SHA-256 | `a2bd9191a781831859ad9db7c88d225d930f8939bf8f53b1dd53d79749f26a40` | `a2bd9191a781831859ad9db7c88d225d930f8939bf8f53b1dd53d79749f26a40` | Match |
| `shared-catalog.json` | signing payload SHA-256 | `5ffd423264ab31edb03015183d4c828f51c9de0bc76083a0adab5146534b3d74` | `5ffd423264ab31edb03015183d4c828f51c9de0bc76083a0adab5146534b3d74` | Match |
| `shared-catalog.json` | catalog digest | `sha256:a2bd9191a781831859ad9db7c88d225d930f8939bf8f53b1dd53d79749f26a40` | `sha256:a2bd9191a781831859ad9db7c88d225d930f8939bf8f53b1dd53d79749f26a40` | Match |

No byte or digest mismatch was observed in Phase 4G.3.

## Next Actions

1. Add Locus-owned companion shared fixtures and verify them from Somatic.
2. Add a Locus-owned signed catalog fixture and a high-level Locus catalog signature threshold verifier, or explicitly document catalog signatures as caller-enforced.
3. Expand shared canonicalization vectors for control characters, Unicode, key ordering, raw JSON rejection, manifests, keyrings, and catalogs.
4. Add optional Somatic tests that run live Locus interop checks only when explicitly enabled and the local Locus checkout is present.
5. Add revoked-key, duplicate-signature, namespace mismatch, expired publisher key, and timestamp-boundary mutual vectors.
6. Keep transport, pack download/install, quarantine, enablement, and catalog server runtime in later explicitly scoped phases.
