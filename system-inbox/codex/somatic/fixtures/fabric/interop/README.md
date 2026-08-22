# Fabric Interop Fixtures

This folder is reserved for Content Fabric fixture exchange with Locus.

Current status: Phase 4G.3 shared fixture certification achieved for Somatic-origin fixtures, not full runtime interop certification.

No Locus files are copied here in Phase 4F. Before copying any fixture from another repository, record:

- source repository and commit
- source path
- license or permission basis
- copied file names
- SHA-256 digest for each copied file
- whether private keys are test-only material

Phase 4G.2 adds Somatic-origin shared fixtures in `shared/`:

- `shared-pack.json`
- `shared-data-pack.json`
- `shared-keyring.json`
- `shared-catalog.json`
- `shared-expected.json`
- `shared-invalid-signature-pack.json`
- `shared-invalid-catalog-signature.json`
- `shared-invalid-keyring-threshold.json`

These files use deterministic test-only keys and are self-certified locally by Somatic. Phase 4G.3 verified them through Locus commit `5f81ee360834dc6451c4ea35d7509325813d9d10`. This certifies the shared Somatic-origin fixture set only; full interop still requires Locus-origin companion fixtures and broader runtime coverage.

The next fixture exchange should include:

- a Locus-generated signed data pack manifest
- a Locus-generated signed code pack manifest
- a Locus-generated signed keyring
- a Locus-generated invalid signature case
- the matching Somatic-generated versions for mutual verification

Phase 4E adds Somatic-generated exchange candidates only:

- `somatic-generated-pack.json`
- `somatic-generated-keyring.json`
- `somatic-generated-catalog.json`
- `somatic-generated-metadata.json`

These files use deterministic test-only keys. Phase 4F records local verification evidence for them, but does not certify full interop.

Phase 4F updates `somatic-generated-metadata.json` after local verification against Locus commit `79f480d592ec82e879b7588a25bad6b4ea2536ca`. Locus verified the Somatic-generated pack/keyring, validated the catalog shape, and verified the catalog signature with its Ed25519 primitive. Somatic verified Locus-owned pack/keyring fixtures in place. No Locus files were copied here.

Phase 4G.3 adds no BitTorrent/WebSeed transport runtime, HTTP/WS catalog server, pack download, pack install, code-pack quarantine, enablement runtime, external API, production secret, or Locus runtime dependency.

Do not place production keys or real secrets in this folder.
