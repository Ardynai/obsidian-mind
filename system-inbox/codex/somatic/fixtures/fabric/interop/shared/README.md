# Shared Fabric Interop Fixtures

Phase 4G.2 created Somatic-generated shared fixtures for Locus/Somatic verification. Phase 4G.3 verified these shared fixtures through the local Locus implementation at commit `5f81ee360834dc6451c4ea35d7509325813d9d10`.

Current result: shared fixture certification achieved for this Somatic-origin fixture set. This is not full Content Fabric runtime interop certification because Locus-origin companion fixtures, transport, install, quarantine, enablement, HTTP/WS catalog servers, and production signing policy remain outside this fixture set.

Contents:

- `shared-pack.json`: signed test-only code pack.
- `shared-data-pack.json`: signed test-only data pack included because this phase can cover both data and code pack classes without adding runtime behavior.
- `shared-keyring.json`: signed test-only keyring containing public root and publisher keys only.
- `shared-catalog.json`: signed catalog containing both shared pack entries.
- `shared-expected.json`: canonical/signing-payload/manifest/catalog digest metadata and self-certification status.
- `shared-invalid-signature-pack.json`: tampered pack that must fail publisher signature verification.
- `shared-invalid-catalog-signature.json`: tampered catalog that must fail catalog signature verification.
- `shared-invalid-keyring-threshold.json`: malformed threshold keyring that must fail validation.

The related deterministic private keys live in `fixtures/fabric/crypto/test-root-key.json` and `fixtures/fabric/crypto/test-publisher-key.json` and are marked test-vector-only. Do not use them for production Fabric signing.

Locus verified the shared pack/keyring/catalog bytes with its `parseFabricJson`, `canonicalize`, `signingPayload`, `manifestDigest`, `validatePackManifest`, `validateCatalog`, `verifyPackManifest`, `verifyKeyring`, and `verifyEd25519Signature` entrypoints. Locus rejected the invalid signature pack, rejected the invalid keyring threshold, and rejected the invalid catalog signature with the Ed25519 primitive.

These fixtures do not implement or exercise BitTorrent networking, pack download, install, quarantine, code execution, enablement, HTTP catalog servers, WebSocket catalog events, production secrets, or external APIs.
