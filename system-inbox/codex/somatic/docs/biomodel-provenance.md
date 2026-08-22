# Biomodel Provenance Packaging

Phase 6D adds deterministic biomodel artifact provenance and future Fabric pack
planning for the fake-backed `in-silico-screening` workflow. It records what was
produced locally, how each JSON artifact hashes, and how the bundle could later
map into a Fabric `data` pack after separate review.

This phase does not create, sign, publish, transport, install, or execute a
Fabric pack.

## Provider Helper

`somatic.providers.biomodel_provenance` is standard-library only. It provides:

- `BiomodelArtifactRef`: local artifact id, relative path, SHA-256, role, and
  research-only flags.
- `BiomodelProvenanceBundle`: deterministic provider/source metadata plus refs
  for request, readiness, consent, plan, result, raw evidence, and verdict
  artifacts.
- `BiomodelPackPlan`: planning metadata for a future Fabric `data` pack
  candidate.
- `hash_artifact_file` and `hash_artifact_payload`: SHA-256 helpers aligned
  with the run writer's sorted, indented JSON format.
- `collect_run_artifact_refs`: local run-folder artifact hashing.
- `build_biomodel_provenance_bundle`: bundle construction from in-silico
  artifact payloads.
- `build_biomodel_pack_plan`: maps a bundle to a future Fabric `data` candidate
  of type `dataset` or `document`.

The helper imports no Boltz runtime, scientific model package, network client,
Fabric transport, installer, or signing dependency.

## Run Artifacts

The `in-silico-screening` workflow now writes:

- `artifacts/biomodel_provenance_bundle.json`
- `artifacts/biomodel_pack_plan.json`

The provenance bundle records:

- provider id, provider version, and scaffold status
- staged source path, inspected commit, and license
- request, readiness, consent, plan, result, evidence-record, raw-evidence, and
  structured-verdict refs
- local SHA-256 hashes for those artifacts
- assumptions and limitations
- mock/offline/research-only status
- disabled runtime, download, MSA, network, GPU, Fabric publish, Fabric
  transport, and Fabric install flags

The pack plan records:

- `pack_class = "data"`
- `candidate_type = "dataset"` with `document` as the alternate candidate
- `code_pack = false`
- no executable files
- no draft `pack.json`
- no signing
- no signed pack
- no catalog publication
- no public seeding
- no transport or install runtime
- license, provenance, hash, safety, and explicit publication review
  requirements before any future public packaging

## Fabric Boundary

Phase 6D only plans a possible future Fabric `data` pack. It does not produce a
Content Fabric `pack.json`, signatures, publisher metadata, keyring reference,
catalog entry, torrent infohash, magnet, WebSeed, install target, or executable
payload.

The recommended future class is `data` because the artifacts are local research
outputs. The candidate type is `dataset` because the bundle is a structured
machine-readable collection. `document` remains the fallback if a later phase
packages the bundle as report material.

## Safety Boundary

The provenance and pack-planning artifacts are metadata only. They do not make
scientific, medical, clinical, lab, safety, binding, affinity, efficacy,
toxicity, mechanism, or therapeutic claims.

Future real biomodel output would still require explicit opt-in, resource
review, model/input provenance, output hashing, license review, safety review,
and publication approval before any Fabric packaging, seeding, cataloging,
transport, install, or execution path could be considered.
