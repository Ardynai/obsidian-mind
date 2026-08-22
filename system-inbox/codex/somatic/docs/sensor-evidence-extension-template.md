# Sensor Evidence Extension Template

Phase 9E makes the sanitized sensor-evidence extension pattern public. A
provider added through this template must stay fixture-only, standard-library
only, deterministic, metadata-only, and fail closed. It must not add live
capture, hardware access, network listeners, credentials, raw value export,
provider payload export, ranking input, Fabric publishing, or runtime
installation.

## Provider Module Shape

Use a small module under `somatic/sensors/` that reads only checked-in fixture
files. The toy provider is the concrete template:

- `somatic/sensors/toy_counter.py`
- `fixtures/sensors/toy-counter/toy-counter-parsed.csv`
- `fixtures/sensors/toy-counter/toy-counter-mixed.csv`

Provider modules should expose:

- stable provider ID and contract-version constants
- input-kind constants
- fixture base and max-ref/max-row limits
- a provider class with `status()` and `evidence_pack(...)`
- a fixture evaluator that returns sanitized count/status metadata only
- fail-closed handling for missing, unsafe, malformed, or unsupported fixtures

Fixture refs accepted by registry validation are bare filenames. Do not accept
absolute paths, parent traversal, URLs, device selectors, endpoints, credentials,
or live-capture fields.

## Evidence-Pack Module Shape

Use a sibling module named `<provider>_evidence_pack.py`. It should define:

- `PROVIDER_KIND`, `EVIDENCE_KIND`, `ARTIFACT_NAME`, and `ARTIFACT_REF`
- contract version, exporter ID, required fields, and known top-level fields
- a `SensorEvidenceContract`
- `build_<provider>_evidence_pack(...)`
- `compute_<provider>_evidence_pack_fingerprint(...)`
- `classify_<provider>_evidence_pack_compatibility(...)`
- `validate_<provider>_evidence_pack_v1(...)`
- compact artifact metadata via the shared framework artifact-ref helper

Phase 10E exposes `somatic.evidence.framework` as the neutral import surface
for shared evidence-pack helpers. New providers should reuse
`SensorEvidenceContract`, deterministic fingerprint finalization, run-relative
artifact refs, status-count helpers, and compatibility classification from that
framework while keeping provider-specific counts, status behavior, and fixture
evaluation in the provider module.

Fingerprints must be deterministic over the persisted payload shape with
`pack_id` and `pack_fingerprint` nulled before hashing. Changing a public pack
shape, fingerprint scope, artifact name, or compatibility behavior requires an
explicit contract-version decision and tests.

## Registry Entry Fields

Register the provider in `somatic/sensors/registry.py` with sanitized metadata
only:

- `provider_id`
- `provider_kind`
- `evidence_kind`
- `contract_version`
- `artifact_name`
- `artifact_ref`
- `input_kinds`
- `supported_fixture_formats`
- `fixture_mode_labels`
- `offline_fixture_only=True`
- public/private artifact boundary notes
- bounded fixture ref and group limits

The registry validates workflow config before runtime dispatch. Unknown
providers, excessive refs, unsafe refs, URLs, absolute paths, credentials,
device/live/network fields, and truthy `allow_*` sensor constraints must fail
closed with sanitized error codes.

## Provider Manifest Snapshot

Phase 9G exports a deterministic public provider manifest from the registry via
`sensor_evidence_provider_manifest()` and:

```powershell
python -m somatic sensor-evidence providers --format json
```

The manifest is the stable machine-readable discovery contract. It contains
only provider IDs/kinds, evidence kinds, contract identities, artifact names,
fixture-only/offline flags, fixture mode labels, supported fixture formats,
provider order, provider count, and public boundary labels. It intentionally
omits fixture refs, local paths, provider aliases, private boundary notes,
fixture limits, run-artifact hashes, provider internals, parser internals, and
runtime config values.

When adding or intentionally changing a provider, regenerate and review
`fixtures/providers/sensor-evidence-provider-manifest-v1.json`, then update
tests and docs in the same change. Safe additive public metadata must still
pass `validate_sensor_evidence_provider_manifest(...)`; unsafe/private fields
fail closed with sanitized manifest compatibility errors.

For release closeout, update `docs/phase-9h-release-summary.md` and
`fixtures/reports/sensor-evidence-subsystem-summary-v1.json` when the public
provider list, artifact names, compatibility contract, commands, or extension
path intentionally changes.

## Fixture Config Shape

A provider input should look like this:

```yaml
- id: toy_counter_fixture_rows
  kind: toy-counter-fixture-rows
  provider_id: toy-counter-fixture
  required: false
  sensitivity: local
  refs:
    - toy-counter-parsed.csv
  description: Local toy count/status fixture rows for sanitized metadata only.
```

The sensor provider constraints must keep the offline boundary closed:

```yaml
constraints:
  offline_required: true
  mock_only: true
  fixture_only: true
  research_only: true
  allow_live_capture: false
  allow_hardware_access: false
  allow_network_calls: false
```

See `examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml`.

## CLI Verification

Before running a workflow, use the Phase 9F discovery and validation commands
from the repository root:

```powershell
python -m somatic sensor-evidence providers
python -m somatic sensor-evidence providers --format json
python -m somatic sensor-evidence validate --workflow examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml
python -m somatic sensor-evidence validate --workflow examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml --format json
```

Provider discovery is a read-only registry view. Workflow validation checks
configured sensor-evidence provider IDs, fixture mode labels, bounded counts,
fixture-only refs, and closed sensor constraints before runtime dispatch. It
returns sanitized categories for unknown providers, unsafe refs, excessive
counts, live/device/network fields, credential-like fields, unsupported fixture
modes, and unsupported fixture formats.

Accepted fixture refs remain bare filenames only. Validation output must not
echo fixture refs, absolute paths, URLs, credentials, device selectors, or
private config values.

## Artifact Naming Rules

Evidence-pack artifact names are stable public contract names:

- Python artifact name: `toy_counter_evidence_pack`
- Run-relative path: `artifacts/toy_counter_evidence_pack.json`
- Generic refs: `sensor_evidence_artifact_refs.toy_counter_evidence_pack`
- SHA-256 field: `sha256` / `artifact_sha256`

Run manifests, n-of-1 report packets, tournament summaries, and planning-only
Fabric pack plans should reference packs by run-relative path plus SHA-256.
They must not inline fixture bodies or provider payloads.

## Privacy Checklist

Before adding a provider, add tests proving no portable artifacts contain:

- raw values, row bodies, payloads, source IDs, or fixture refs
- private fixture filenames outside local config validation
- unsafe refs, URLs, absolute paths, or parent traversal
- credentials, tokens, endpoint selectors, or device selectors
- provider payload bodies, parser report bodies, or parser summary bodies
- live capture, hardware access, network calls, ranking input, or score changes
- claims, advice, action, monitoring, or intervention-effectiveness language

The toy provider is intentionally generic and harmless. It proves extension
mechanics only; it is not a new sensor runtime.
