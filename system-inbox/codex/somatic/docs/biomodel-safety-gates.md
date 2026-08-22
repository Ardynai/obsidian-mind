# Biomodel Safety Gates

Phase 6C adds a standard-library-only readiness gate for future real biomodel
runtimes. The gate lives in `somatic/safety/biomodel.py` and is policy
metadata only; it does not import Boltz, run models, download data, call MSA
servers, call networks, or probe hardware.

## Runtime Policy

`BiomodelRuntimePolicy` defaults to the safe state:

- runtime execution disabled
- model downloads disabled
- MSA server use disabled
- network calls disabled
- GPU execution disabled
- resource review missing
- provenance plan missing
- explicit user consent required
- research-only acknowledgement required

`evaluate_biomodel_readiness(...)` returns a `BiomodelReadinessReport` with
deterministic block reasons:

- `runtime-execution-disabled`
- `model-downloads-disabled`
- `msa-server-disabled`
- `network-calls-disabled`
- `gpu-execution-disabled`
- `missing-resource-review`
- `missing-provenance-plan`
- `missing-user-consent`
- `research-only-boundary-not-acknowledged`

Even when every readiness gate is satisfied by a test fixture, Phase 6C still
sets `execution_permitted=false` and `phase_runtime=not-implemented`. Real
runtime execution is future work only.

## Consent Record

`BiomodelConsentRecord` records placeholder consent state for future real
runtime work. The checked-in placeholder records no user consent and no
research-only acknowledgement. This is intentional: fake-backed in-silico mode
can emit planning artifacts, but real biomodel runtime remains blocked.

## Boltz Integration

`BoltzProvider` attaches the readiness report, runtime policy, and consent
record to fake-backed plan/result metadata. Real mode fails closed:

- failed readiness gates raise `BoltzReadinessGateError`
- unsafe provider config raises `BoltzConfigurationError`
- a missing optional Boltz package raises `BoltzOptionalDependencyError` only
  after readiness gates pass
- a detectable Boltz package still raises `BoltzRuntimeNotEnabledError`

The provider locks optional dependency probing to the literal top-level package
name `boltz`.

## Run Artifacts

The `in-silico-screening` workflow now writes:

- `artifacts/biomodel_readiness_report.json`
- `artifacts/biomodel_consent_record.json`

The plan, result, raw evidence metadata, summary, and report all preserve the
same boundary: fake-backed planning only, research-only, no runtime execution,
and no real scientific, clinical, lab, structure, affinity, efficacy, or safety
claim.
