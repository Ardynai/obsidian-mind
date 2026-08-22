# Evidence Bus Sandbox

`somatic/simulator/sandbox_source.py` provides a deterministic offline EvidenceSource for Phase 3A. It exists to exercise the Evidence Bus contracts before any provider, lab, sensor, or model integration is enabled.

## Supported Modalities

- `literature`
- `sim`
- `wetlab`

The `wetlab` modality is only a wetlab-shaped fixture record. It does not represent a real lab action.

## Behavior

`SandboxEvidenceSource.acquire(measurement_plan)` accepts a `MeasurementPlan` and returns `RawEvidence` records. Each record includes:

- stable `id`
- `EvidenceSource`
- `payload_ref`
- SHA-256 digest
- mock/offline/research-only metadata
- deterministic payload metadata
- optional local table fixture references for Finch toolbelt analysis

The source raises `ValueError` for unsupported modalities. It uses only Python standard-library JSON and hashing utilities and makes no external calls.

Phase 5D adds local CSV table references to the `sim` and `wetlab`-shaped
payloads. Those references point to files under `fixtures/evidence/tables/` and
are consumed by Finch's standard-library toolbelt. They are local sandbox
fixtures only and do not represent real simulation output or wetlab results.

Phase 5F maps FutureHouse Robin, Aviary, and LDP concepts to this local
sandbox shape. Aviary-like reset/step environments and LDP-like rollouts remain
future optional provider envelopes; the sandbox source does not import,
execute, or depend on them.

## Determinism

The payload for each modality is fixed and hashed with sorted JSON keys.
Re-running the same plan produces identical raw evidence, Finch toolbelt,
structured verdict, and provenance artifacts.

## Boundary

The sandbox source is a local test harness. It does not fetch literature,
operate lab equipment, connect to sensors, execute simulations, run
Robin/Aviary/LDP, call Edison or external LLM providers, or make scientific
claims.
