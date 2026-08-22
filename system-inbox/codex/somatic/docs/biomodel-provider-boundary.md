# Biomodel Provider Boundary

Phase 6A makes the biomodel boundary explicit before any in-silico runtime is
enabled. Phase 6B integrates that boundary into the local mock workflow/run
artifact system. Phase 6C adds explicit readiness and consent gates for any
future real runtime. Phase 6D adds deterministic local artifact provenance and
planning-only Fabric `data` pack mapping. Biomodel outputs are research
artifacts only. They are not medical advice, lab conclusions, treatment
recommendations, clinical evidence, or scientific efficacy claims.

## Interfaces

`BiomodelProvider` is the Somatic-owned protocol for in-silico modeling
adapters. External tools such as Boltz, ESM, Chai, AlphaFold-compatible
providers, RDKit, or future model runtimes must map into this boundary instead
of owning the workflow.

The boundary types are:

- `BiomodelRequest`: objective, target refs, input artifact refs, constraints,
  and metadata.
- `BiomodelPlan`: pre-execution plan with provider id, model family/version,
  command shape, local artifacts, expected outputs, blocked actions, consent
  requirements, resources, provenance, assumptions, and limitations.
- `BiomodelResult`: result metadata with status, artifact refs, evidence refs,
  assumptions, limitations, and provenance metadata.
- `BiomodelEvidenceRecord`: Somatic Evidence Bus mapping for a biomodel result.
- `BiomodelRuntimePolicy`: future real-runtime policy flags.
- `BiomodelConsentRecord`: explicit consent and acknowledgement state.
- `BiomodelReadinessReport`: deterministic gate outcome and block reasons.
- `BiomodelProvenanceBundle`: Phase 6D local artifact refs, source metadata,
  assumptions, limitations, and disabled runtime/Fabric flags.
- `BiomodelPackPlan`: Phase 6D future Fabric `data` candidate planning metadata.
- `BiomodelProvider.plan`: must describe requirements before any execution,
  download, MSA generation, external call, or private data release.
- `BiomodelProvider.run`: reserved for future explicitly configured runtime
  execution. In Phase 6A, concrete providers remain disabled or fake-backed.

## Evidence Bus Mapping

The current Evidence Bus modality list does not add a new `biomodel` modality.
Phase 6A maps biomodel output into `RawEvidence` using modality `sim` with
metadata `submodality: biomodel`.

The mapping is:

- `EvidenceSource`: provider id, modality `sim`, submodality `biomodel`,
  research-only metadata, and no clinical/lab conclusion flag.
- `RawEvidence`: payload ref to a local or mock biomodel artifact, SHA-256,
  assumptions, limitations, and runtime-execution metadata.
- `StructuredVerdict`: summary of the biomodel result boundary with
  `confidence: not-applicable` for mock/planning mode.
- `BiomodelEvidenceRecord`: bundles the raw evidence and structured verdict so
  future report code can preserve provenance and limitations.

No current biomodel scaffold emits real model output. The evidence records are
metadata-only until a later phase implements an explicitly configured runtime.

Phase 6B writes the mapping into `in-silico-screening` run artifacts:

- `artifacts/biomodel_request.json`
- `artifacts/biomodel_readiness_report.json`
- `artifacts/biomodel_consent_record.json`
- `artifacts/biomodel_plan.json`
- `artifacts/biomodel_result.json`
- `artifacts/biomodel_evidence_record.json`
- `artifacts/biomodel_raw_evidence.json`
- `artifacts/biomodel_structured_verdict.json`
- `artifacts/biomodel_provenance_bundle.json`
- `artifacts/biomodel_pack_plan.json`
- `artifacts/in_silico_summary.json`

The local run artifact boundary points `RawEvidence.payload_ref` at
`artifacts/biomodel_result.json` while preserving provider mock refs in
metadata.

The Evidence Bus raw metadata now also preserves disabled model download, MSA
server, network, and GPU flags alongside runtime execution state.

## Local-Only And Cloud/Server-Backed Behavior

Default behavior is local planning only:

- no network calls
- no model downloads
- no MSA server calls
- no provider secrets
- no external package imports
- no GPU/TPU runtime
- no private data release

Future local runtime mode must still require explicit opt-in, local path review,
model provenance, cache location, resource checks, and output hashing. Future
cloud or server-backed mode must additionally require explicit consent,
redacted configuration, data-locality declaration, credential handling, and
audit records before any request leaves the machine.

## Consent Boundaries

The following actions require future explicit consent and implementation:

- model or data download
- remote MSA generation
- cloud/server-backed inference
- uploading molecular, sequence, clinical, patient, or private user data
- GPU/TPU execution
- long-running jobs or large cache writes
- interpreting model outputs as evidence for real-world action

Phase 6A fixtures and tests assert these actions are disabled. Phase 6B keeps
the runnable in-silico fixture on the same fake-backed boundary. Phase 6C records
the consent placeholder and blocks real runtime until the policy, consent,
resource review, provenance plan, and research-only acknowledgement gates pass;
even then, execution is not implemented in this phase.

## Resource Boundary

Biomodel providers must declare:

- expected model family and version
- package dependency weight
- model/data cache requirements
- CPU/GPU/TPU assumptions
- memory/storage expectations
- offline vs server-backed MSA strategy
- output artifact size and format expectations

The Boltz scaffold records upstream GPU defaults and cache/download behavior,
but it does not probe hardware or run a model.

## Provenance And Hashes

Every future biomodel result must record:

- provider id and version
- model family and version
- source path or package version
- inspected source commit when applicable
- input artifact refs and hashes
- output artifact refs and hashes
- cache/model artifact provenance
- MSA provenance or explicit no-MSA/single-sequence mode
- runtime configuration
- assumptions and limitations

Phase 6A mock results include a deterministic SHA-256 over plan metadata. This
hash is not a model-output hash; it only proves deterministic scaffold metadata.

Phase 6D adds run-level hashes for the fake-backed request, readiness, consent,
plan, result, raw evidence, and verdict artifacts. The provenance bundle is a
local research artifact and the pack plan is a future packaging recommendation
only. It does not create a Fabric manifest, signature, catalog entry, torrent,
transport, install target, code pack, or executable file.

## Safety Limitations

Biomodel outputs are not lab results. They are not clinical results. They do not
prove binding, efficacy, toxicity, mechanism, safety, or therapeutic value.
Reports must preserve this boundary even after future real runtime support is
added. Future Fabric packaging requires explicit publication approval, license
review, provenance review, hash verification, and safety review.
