# In-Silico Screening Workflow

Phase 6B adds a runnable `in-silico-screening` fixture to the local mock
runtime. Phase 6C adds biomodel readiness and consent artifacts to that same
fake-backed path without enabling any model runtime. Phase 6D adds biomodel
artifact provenance and future Fabric `data` pack planning without publishing,
transporting, signing, installing, or executing a pack.

Run it with:

```powershell
python -m somatic run fixtures/workflows/valid-in-silico-screening.yaml
```

## Runtime Shape

The workflow:

- loads `fixtures/workflows/valid-in-silico-screening.yaml`
- loads biomodel provider metadata from
  `fixtures/providers/boltz2-provider-mock-config.json`
- constructs a `BiomodelRequest`
- evaluates the Phase 6C biomodel readiness gates
- calls `BoltzProvider.plan` in mock mode
- calls `BoltzProvider.run` only in fake-backed mock mode
- maps the mock result into Evidence Bus `RawEvidence` and
  `StructuredVerdict`
- builds a deterministic biomodel provenance bundle over local artifact hashes
- builds a future Fabric `data` pack plan for the bundle
- writes the biomodel artifacts into the run folder
- renders a research-only report

## Artifacts

The run preserves the baseline local mock runner layout:

- `manifest.json`
- `workflow.json`
- `inputs/README.md`
- `evidence/evidence.json`
- `artifacts/hypotheses.json`
- `safety/safety-response.json`
- `reports/report.md`
- `next_iteration.json`

It also writes:

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

The manifest records these artifact paths and hashes.

## Evidence Bus Mapping

Biomodel output remains simulation-shaped research evidence:

- `EvidenceSource.modality = "sim"`
- `EvidenceSource.metadata.submodality = "biomodel"`
- `RawEvidence.payload_ref = "artifacts/biomodel_result.json"`
- `StructuredVerdict.confidence = "not-applicable"`

The raw evidence keeps the provider mock payload ref in metadata for provenance,
but the run artifact boundary points at the local `biomodel_result.json` file.

## Phase 6D Provenance And Fabric Pack Planning

The workflow writes a deterministic `biomodel_provenance_bundle.json` with
provider id/version/scaffold status, staged source path, inspected commit,
license, assumptions, limitations, and SHA-256 refs for request, readiness,
consent, plan, result, evidence-record, raw-evidence, and structured-verdict
artifacts.

It also writes `biomodel_pack_plan.json`, a planning-only mapping for a future
Fabric `data` pack candidate. The candidate type is `dataset`, with `document`
as the alternate type. The plan records no code pack, no executable files, no
draft manifest, no signing, no signed pack, no catalog publishing, no public
seeding, no Fabric publishing, no Fabric transport, and no Fabric install.

The pack plan is not a Content Fabric `pack.json`. It is only a local
research-output planning artifact for later license, provenance, hash, safety,
and explicit publication review.

## Phase 6C Readiness Gates

The workflow uses `BiomodelRuntimePolicy` and `BiomodelConsentRecord` from
`somatic/safety/biomodel.py`. The default policy blocks runtime execution,
model downloads, MSA server calls, network calls, GPU execution, missing
resource review, missing provenance planning, missing user consent, and missing
research-only acknowledgement.

The readiness report is included in the plan/result metadata and written as a
separate artifact. `execution_permitted` remains `false` in Phase 6C even if a
test fixture marks every individual gate enabled. Any workflow/provider
constraint that tries to enable runtime, downloads, MSA, network, or GPU use is
rejected before fake-backed artifacts are written.

## Boundaries

The workflow is fake-backed planning only:

- no Boltz execution
- no Boltz import
- no model weights, molecule data, datasets, or MSA downloads
- no MSA server calls
- no external APIs or network calls
- no GPU/runtime execution
- no real structure prediction
- no real affinity prediction
- no Fabric publishing, cataloging, signing, transport, install, or execution
- no medical, lab, clinical, efficacy, safety, or scientific conclusion

Future real mode requires explicit opt-in, resource checks, model and input
provenance, output hashing, consent gates, license review, and safety review
before any model runtime or Fabric packaging can be considered.
