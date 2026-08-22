# Master Plan

Somatic is a standalone open scientific discovery harness. Phase 1C upgrades the repository from docs plus a local mock runner into a Python monorepo scaffold aligned with the master plan.

## Build Philosophy

Somatic follows Option C:

- Basic install stays lightweight and runnable for normal users.
- Advanced lanes are represented as real package boundaries and optional extras.
- Heavy scientific, sensor, agent, biomodel, and Fabric integrations stay optional.
- A future all-extras / FutureCube path can use the `all` extra for power-user setups.
- No advanced lane runs unless explicitly configured.

## Foundation Lanes

- `somatic.core`: workflow loading, contracts, run writing, and local mock runtime.
- `somatic.evidence_bus`: shared evidence source, measurement, raw evidence, and structured verdict contracts.
- `somatic.agents`: future orchestration and scientific-agent lane.
- `somatic.engines`: literature, Robin, Finch, hypothesis, and biomodel engine lane.
- `somatic.sensors`: local-first sensor lane.
- `somatic.safety`: safety gate and evaluation lane.
- `somatic.memory`: local-first run and evidence memory lane.
- `somatic.presence`: render-only avatar and presence lane.
- `somatic.fabric`: verified pack and catalog lane.
- `somatic.bench`: benchmark and regression lane.
- `somatic.cli`: command-line entrypoint.
- `somatic.reports`: safety-gated report lane.
- `somatic.simulator`: sandbox and dry-run simulation lane.

## Current Runtime

The current runtime is intentionally small:

- `python -m somatic run fixtures/workflows/valid-literature-only.yaml`
- local fixture workflow parsing
- local mock provider metadata
- mock hypotheses
- sample evidence and safety response attachment
- run artifact folder writing

No real provider, lab, sensor, biomodel, clinical, Fabric, or network runtime exists in Phase 1C.

## Safety Position

Somatic outputs remain research-only and decision-support oriented. Health-related output must be safety-gated and human-reviewed. Somatic does not provide diagnosis, treatment, cure, emergency triage, or clinician replacement.

Presence and avatar features are render-only and never part of the reasoning path.
