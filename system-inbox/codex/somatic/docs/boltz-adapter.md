# Boltz Adapter Scaffold

Phase 6A adds a disabled, fake-backed Boltz-2 biomodel planning scaffold in
`somatic.providers.boltz`. Phase 6B wires that scaffold into the local
`in-silico-screening` mock workflow. Phase 6C attaches biomodel readiness gates
and consent metadata. Phase 6D records local artifact provenance and a
planning-only Fabric `data` pack recommendation for the generated biomodel
artifacts. It imports without Boltz installed and does not import, execute,
download, or call any upstream Boltz runtime path.

## Status

- Provider id: `boltz2-biomodel-provider`
- Source: `C:\AI\external-sources\somatic\boltz`
- Inspected commit: `b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc`
- Source license: MIT
- Upstream entrypoint: `boltz = boltz.main:cli`
- Upstream command shape: `boltz predict <INPUT_PATH> [OPTIONS]`
- Somatic mode: disabled by default, deterministic mock metadata only

## Provider Config

`BoltzProviderConfig` defaults to:

- `enabled=False`
- `mode="mock"`
- `package_name="boltz"`
- `default_model="boltz2"`
- `output_format="mmcif"`
- `allow_runtime_execution=False`
- `allow_model_downloads=False`
- `allow_msa_server=False`
- `allow_network_calls=False`
- `allow_gpu_execution=False`
- `require_explicit_consent=True`
- `fake_backed=True`
- `runtime_policy=None` (safe default used)
- `consent_record=None` (placeholder no-consent record used)

Availability detection uses `importlib.util.find_spec("boltz")`; it never
imports `boltz`.

## Plan Mode

`BoltzProvider.plan(BiomodelRequest)` returns a deterministic `BiomodelPlan`
that records:

- request id derived from objective, targets, inputs, constraints, and metadata
- expected `boltz predict` command shape
- input artifact refs
- planned output refs for predictions, confidence JSON, and affinity JSON
- required local artifacts such as YAML input and precomputed MSA
- blocked actions such as model downloads, MSA server calls, and GPU runtime
- consent requirements
- source path, commit, license, and optional dependency availability

The plan does not validate a real Boltz YAML file and does not touch model
runtime code. Phase 6C adds `readiness_report`, `runtime_policy`, and
`consent_record` metadata to the plan.

## Mock Result Mode

`BoltzProvider.run(BiomodelRequest)` remains fake-backed in mock mode. It
returns deterministic `BiomodelResult` metadata with mock artifact refs and a
SHA-256 over the plan metadata. It does not run a prediction.
The result carries the same Phase 6C readiness report and consent metadata as
the plan.

`BoltzProvider.evidence_record(...)` maps the mock result into:

- `RawEvidence` with modality `sim` and metadata `submodality: biomodel`
- `StructuredVerdict` with `confidence: not-applicable`

This is a planning artifact, not a structure or affinity prediction.

## In-Silico Workflow Integration

`python -m somatic run fixtures/workflows/valid-in-silico-screening.yaml`
uses `BoltzProvider(BoltzProviderConfig(enabled=True, mode="mock"))` to produce
deterministic biomodel planning artifacts. The runtime writes request, plan,
readiness report, consent record, result, Evidence Bus record, raw evidence,
structured verdict, provenance bundle, pack plan, and summary JSON files under
`artifacts/`.

This workflow still uses fake-backed metadata only. It does not validate Boltz
input files, import Boltz, run `boltz predict`, download weights or molecule
data, call MSA servers, use GPU/runtime execution, or produce structure or
affinity predictions. It also does not create, sign, publish, transport,
install, or execute a Fabric pack.

## Real Mode

Real mode fails closed.

Failed readiness gates raise `BoltzReadinessGateError`. Unsafe provider config
raises `BoltzConfigurationError`, including any attempt to probe a package name
other than the literal top-level package `boltz`. If readiness gates pass but
`boltz` is unavailable, the provider raises `BoltzOptionalDependencyError`. If
`boltz` is detectable, the provider still raises `BoltzRuntimeNotEnabledError`
because Phase 6C does not implement runtime prediction.

The scaffold also rejects config flags that would enable:

- runtime execution
- model downloads
- MSA server calls
- network calls
- GPU execution

## Upstream Behaviors Kept Disabled

The inspected Boltz source can:

- download molecule/CCD data and checkpoints into a cache
- call a remote MSA server when `--use_msa_server` is set
- use MSA server username/password or API-key auth
- default to GPU execution
- load PyTorch Lightning checkpoints
- emit structure and confidence artifacts
- emit affinity JSON artifacts
- run training, evaluation, and processing scripts

All of these remain outside Somatic Phase 6A, Phase 6B, Phase 6C, and Phase 6D
runtime.

## Fixtures

Phase 6A adds or updates:

- `fixtures/providers/boltz2-provider-placeholder.json`
- `fixtures/providers/boltz2-provider-mock-config.json`
- `fixtures/biomodel/biomodel-request-placeholder.json`
- `fixtures/biomodel/biomodel-plan-placeholder.json`
- `fixtures/biomodel/biomodel-result-placeholder.json`
- `fixtures/biomodel/biomodel-runtime-policy-safe-default.json`
- `fixtures/biomodel/biomodel-consent-record-placeholder.json`
- `fixtures/biomodel/biomodel-readiness-report-placeholder.json`
- `fixtures/biomodel/biomodel-runtime-policy-dangerous-enabled.json`
- `fixtures/biomodel/biomodel-provenance-bundle-placeholder.json`
- `fixtures/biomodel/biomodel-pack-plan-placeholder.json`
- `fixtures/workflows/valid-in-silico-screening.yaml`

These fixtures are mock metadata only. They contain no real predictions.

## Future Real Adapter Requirements

Before real Boltz support can be considered, Somatic needs:

- explicit optional install documentation
- source/package version pin and license review
- local cache and model provenance checks
- no-download mode and explicit download consent
- MSA strategy and no-server default
- hardware/resource review
- output hashing and provenance capture
- safety review for research-only presentation
- license, provenance, hash, safety, and explicit publication review before
  any future Fabric packaging
- tests proving default offline behavior remains intact
