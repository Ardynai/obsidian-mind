# Robin Sandbox Loop

Phase 3A adds the first runnable Robin-shaped loop without adding Robin, PaperQA2, LangGraph, scientific-agent-skills, AutoScientists, Fabric runtime, biomodel runtime, real lab runtime, sensor runtime, or network code.

Phase 5A keeps that boundary intact. It adds external science intake docs and a
disabled Robin provider placeholder, but the runnable `robin-loop` mode still
uses Somatic's local Crow/Falcon/sandbox/Finch scaffold only.

Phase 5B adds a disabled PaperQA2 literature provider scaffold with
deterministic fake-backed mode. It is not wired into the Robin loop, does not
replace Crow, and does not fetch or index literature during `robin-loop` runs.

Phase 5C adds a disabled scientific-agent-skills metadata provider scaffold. It
is not wired into the Robin loop, does not execute skills, and does not call
external databases during `robin-loop` runs.

Phase 5D adds Finch's standard-library local analysis toolbelt. The runnable
`robin-loop` mode still stays offline and dependency-light, but Finch now
profiles local CSV fixture tables, emits preliminary dose-response summaries,
and records deterministic provenance hashes when sandbox raw evidence contains
local table references.

Phase 5F inspects staged FutureHouse Robin, Aviary, and LDP sources and maps
their concepts back onto Somatic-owned interfaces. Robin, Aviary, and LDP are
Apache-2.0 licensed in the staged sources, but Somatic still does not import,
vendor, execute, or depend on those runtimes. The current loop keeps Somatic's
own Evidence Bus and Crow/Falcon/Finch artifact shape.

Phase 5G adds disabled Finch optional-extras status metadata. Robin-loop runs
still use the standard-library Finch toolbelt, but
`finch_toolbelt_summary.json` records lazy availability status for pandas,
scipy, numpy, scanpy, and biopython under `optional_extras`.

Run it with:

```powershell
python -m somatic run fixtures/workflows/valid-robin-loop.yaml
```

The loop shape is:

1. Crow builds deterministic mock literature context from the workflow goal and evidence requirements.
2. Falcon converts that context into a local `MeasurementPlan`.
3. `SandboxEvidenceSource` acquires deterministic mock `RawEvidence` records for `literature`, `sim`, and `wetlab` modalities.
4. Finch analyzes the raw evidence, profiles local CSV table fixtures, emits a
   preliminary dose-response summary, records disabled optional-extras status,
   and emits a deterministic `StructuredVerdict`.
5. The runner writes a Markdown report and next-iteration hints.

All outputs are mock, offline, research-only, not medical advice, and not a real scientific conclusion. The current loop verifies Somatic's artifact shape and Evidence Bus wiring only.

## Artifacts

Robin mode preserves the baseline run files and adds:

- `artifacts/crow_literature_context.json`
- `artifacts/falcon_measurement_plan.json`
- `artifacts/raw_evidence.json`
- `artifacts/finch_analysis.json`
- `artifacts/finch_toolbelt_summary.json`
- `artifacts/table_profile.json`
- `artifacts/dose_response_summary.json`
- `artifacts/analysis_provenance.json`
- `artifacts/structured_verdict.json`
- `artifacts/robin_loop_summary.json`

`artifacts/hypotheses.json` remains present for compatibility and contains a single mock hypothesis describing the local loop capability.

## Safety Boundary

The Robin sandbox loop does not:

- call external APIs
- install dependencies
- fetch literature
- execute scientific-agent-skills skills
- call external scientific databases
- execute real lab actions
- run real sensors
- run biomodels
- run Fabric
- run pandas, scipy, numpy, scanpy, biopython, or package-backed analysis
- enable Finch optional extras beyond status metadata
- import or execute FutureHouse Robin, Aviary, or LDP
- call Edison, OpenAI, Anthropic, LiteLLM, fhlmi, or PaperQA2 real mode
- provide diagnosis, treatment, cure, emergency triage, or real scientific conclusions

Human review remains required before any downstream use of the report language.
Future Robin-style adapters must map into Somatic Evidence Bus artifacts and
must not replace the local run artifact, safety, or report boundaries.

See [futurehouse-robin-mapping.md](futurehouse-robin-mapping.md) for the Phase
5F mapping.
