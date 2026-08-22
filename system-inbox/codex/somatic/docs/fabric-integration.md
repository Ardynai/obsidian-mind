# Fabric Integration

Somatic's future fabric system will distribute and verify scientific content packs. The goal is to make datasets, model weights, documents, workflows, and adapter packs reproducible without tying Somatic to a private registry.

Somatic Fabric follows the normative Content Fabric v1.0.0 spec in [content-fabric.md](content-fabric.md). Future runtime work must interoperate with Locus `electron/content-fabric/` without adding a runtime dependency on Locus or any other harness.

## Pack Manifest

Each pack should contain a Content Fabric v1.0.0 `pack.json` manifest with:

- Pack id, name, version, class, type, creation time, and optional description.
- Pack class: `data` or `code`.
- Pack type from the canonical data/code taxonomy.
- Publisher identity and signing key id.
- File list with byte sizes, install targets, and SHA-256 hashes.
- License id.
- Harness compatibility list.
- BitTorrent v1 infohash and magnet with HTTPS WebSeed.
- Sorted Ed25519 signatures.

## File Verification

Every file listed in `pack.json` should be verified with SHA-256 before use. A pack should not enter the trusted local catalog if any required file is missing or mismatched.

## Signatures

Pack manifests should be signed with Ed25519 over `JCS(object with top-level signatures set to [])`. Signature verification should establish publisher identity through the TUF-style keyring, but file-level SHA-256 verification should still be required for content integrity.

## Transport

The initial transport model should support BitTorrent v1 magnet links and WebSeed URLs. BitTorrent provides resilient distribution, while WebSeed gives straightforward HTTP-backed availability.

Transport is not trust. Trust comes from manifest verification, file hashes, signatures, quarantine policy, and license gates.

## Data Packs and Code Packs

Data packs may include PDFs, biomedical datasets, model weights, CSI samples, workflow templates, benchmark packs, result/provenance bundles, and report fixtures. They should be verified before indexing or use.

Code packs may include adapters, plugins, skills, MCP servers, connectors, or agents. They must be quarantined by default. A user or administrator must explicitly consent to install and explicitly enable a code pack after reviewing its publisher, license, capabilities, and requested permissions. Code packs must never execute at install time.

## License Gates

Pack manifests should declare license terms, attribution requirements, redistribution restrictions, commercial-use restrictions, and data-use limits. Somatic should block ingest or execution when required gates are not satisfied.

## Catalogs

Somatic should maintain a local catalog with:

- Verified pack metadata.
- File availability.
- License gate state.
- Quarantine state.
- Enablement state for code packs.
- Provenance for reports and workflow runs.

Remote catalog federation can let multiple publishers advertise pack manifests without creating a central private registry. Local policy should decide which publishers, catalogs, and pack types are trusted.

## Use Cases

- PDF lakes for literature-only and evidence extraction workflows.
- Biomedical datasets for hypothesis tournaments and in-silico screening.
- Model weights for local or remote biomodel adapters.
- CSI sample packs for reproducible sensor-observation research.
- Workflow packs for reusable research modes.
- Adapter and plugin packs for provider integrations.

## Phase 4G.3 Status

Somatic has Fabric conformance docs, fixtures, dependency-free validation primitives, Fabric-supported JCS canonicalization, signing payload construction, digest helpers, manifest/keyring/catalog validators, optional Ed25519 helpers, local root/publisher threshold checks, signed catalog verification, keyring replacement continuity checks, context-specific license decisions, local Fabric CLI commands, Phase 4G.2 shared fixture self-certification, and Phase 4G.3 Locus verification evidence for those shared fixtures.

Use `--keyring` to verify a local signed pack fixture:

```powershell
python -m somatic fabric check fixtures/fabric/crypto/signed-code-pack.json --keyring fixtures/fabric/crypto/keyring-signed.json
python -m somatic fabric check fixtures/fabric/crypto/signed-catalog.json --keyring fixtures/fabric/crypto/keyring-signed.json
```

Self-certify the shared fixtures locally:

```powershell
python -m somatic fabric digest fixtures/fabric/interop/shared/shared-pack.json
python -m somatic fabric check-catalog fixtures/fabric/interop/shared/shared-catalog.json --keyring fixtures/fabric/interop/shared/shared-keyring.json
python -m somatic fabric check-shared-fixtures fixtures/fabric/interop/shared
```

Inspect a signing payload digest or a keyring replacement:

```powershell
python -m somatic fabric payload fixtures/fabric/crypto/signed-code-pack.json
python -m somatic fabric check-keyring-rotation fixtures/fabric/crypto/rotation/previous-keyring.json fixtures/fabric/crypto/rotation/valid-rotated-keyring.json
```

Phase 4D inspected the local Locus implementation at `C:\AI\locus\electron\content-fabric\` and recorded the interop plan in [fabric-locus-interop.md](fabric-locus-interop.md) and [fabric-implementation-gap-analysis.md](fabric-implementation-gap-analysis.md). Phase 4G.2 adds Somatic-generated shared fixture artifacts, and Phase 4G.3 verifies them with Locus commit `5f81ee360834dc6451c4ea35d7509325813d9d10`. Somatic still does not copy Locus fixtures or certify full runtime interop.

The current canonicalization is local RFC 8785/JCS for Fabric-supported JSON only; Locus verified the Somatic-origin shared fixture set, while copied Locus-origin fixtures remain future work. Torrent transport, WebSeed download, catalog server, install/quarantine runtime, sandbox, explicit enablement runtime, executable plugin loader, and copied Locus fixtures remain future work. Phase 4G.3 does not add network code, downloads, external APIs, real secrets, or a Locus runtime dependency.

## Phase 6D Biomodel Pack Planning

Phase 6D adds a planning-only bridge from fake-backed biomodel run artifacts to
a future Fabric `data` pack candidate. The `in-silico-screening` run writes
`artifacts/biomodel_provenance_bundle.json` and
`artifacts/biomodel_pack_plan.json`.

The pack plan recommends `pack_class = "data"` and `candidate_type = "dataset"`
for the provenance bundle, with `document` as the alternate candidate type. It
does not write `pack.json`, does not sign anything, does not create publisher or
keyring metadata, does not publish to a catalog, does not create torrent or
WebSeed transport metadata, does not install a pack, and does not execute code.

Future public packaging of biomodel artifacts requires license review,
provenance review, hash verification, safety review, and explicit publication
approval. A biomodel provenance bundle is local research metadata, not a model
weight pack, runtime adapter, clinical artifact, lab result, or efficacy claim.

## Phase 7G N-of-1 Pack Planning

Phase 7G adds `artifacts/n_of_1_fabric_pack_plan.json` for the fake-backed
n-of-1 workflow. It is a planning-only private Fabric `data` pack candidate for
the local n-of-1 report packet and its referenced artifact hashes.

This is not a Content Fabric `pack.json` manifest. It uses `file_plans`, not
manifest `files`, and it creates no publisher, keyring, catalog entry,
manifest digest, signatures, transport, magnet URI, WebSeed, infohash, install
target, code-pack permission surface, or executable file.

No Fabric signing, catalog publication, transport, magnet, WebSeed, seeding,
upload, install, or execution is enabled. The candidate is private-only by
default and does not export real personal data, personal health data, baseline
data, raw sensor data, or raw RF/CSI data.

Phase 9D keeps Fabric planning behind the generic sensor-evidence registry.
Configured CSI and environment evidence providers are validated as
fixture-only before run artifacts are written. Fabric plans receive only the
sanitized evidence-pack refs from report packets: run-relative paths,
SHA-256 hashes, provider/evidence kind, pack IDs, pack fingerprints, readiness
status, and compatibility classification. Provider/parser payload bodies,
fixture refs, absolute paths, URLs, credentials, transport metadata, signing
metadata, install targets, and execution surfaces remain absent.

Phase 9E extends the same planning surface to `toy-counter-fixture`. If an
example/test workflow emits `artifacts/toy_counter_evidence_pack.json`, Fabric
planning sees only the generic artifact ref and hash. It does not inline toy
fixture rows, publish, sign, transport, install, execute, or alter ranking
inputs.

Future real packaging requires explicit consent, redaction, license review,
privacy review, safety review, human review, local-first storage controls,
retention/export controls, and separate publication approval.
