# FutureHouse Robin Stack Mapping

Phase 5F maps FutureHouse Robin, Aviary, and LDP concepts onto Somatic-owned
interfaces. This is architecture mapping only. Somatic does not import, vendor,
execute, or depend on Robin, Aviary, LDP, Edison, OpenAI, Anthropic, LiteLLM,
fhlmi, or PaperQA2 real mode.

## Mapping Table

| FutureHouse concept | Somatic-owned mapping | Current status |
| --- | --- | --- |
| Crow literature search and reports | Somatic literature providers plus evidence records | `LiteratureProvider`, PaperQA2 disabled scaffold, `crow_literature_context.json` |
| Falcon candidate/report planning | Measurement planning and Evidence Bus plan artifacts | `MeasurementPlan`, `falcon_measurement_plan.json` |
| Finch data analysis | Somatic Finch toolbelt and structured verdicts | standard-library CSV/profile/dose-response/provenance, `StructuredVerdict` |
| Aviary-like environments | Provider execution envelopes and future benchmark environments | reference-only fixture, no runtime |
| LDP-like agent process | Future optional optimization/evolution lane | reference-only fixture, no runtime |
| PaperQA2 | Disabled literature provider scaffold | fake-backed only, no real search/index |
| Edison platform | not used by Somatic core | no API keys, no calls |
| OpenAI/Anthropic/LiteLLM/fhlmi | not used by Somatic core | no provider calls |

## Crow

Robin uses Crow for literature search and some hypothesis/report generation
steps. Somatic keeps Crow as a local shape: `build_literature_context` emits a
deterministic artifact, and future real literature systems attach through
`somatic.providers.literature`.

The Phase 5F literature boundary adds `LiteratureEvidenceDraft` so future
literature providers can describe evidence-record drafts without owning the
workflow loop.

## Falcon

Robin uses Falcon-like report and candidate planning through Edison-backed
jobs. Somatic maps this to `MeasurementPlan` and Evidence Bus planning. Falcon
does not call external services in the current runtime; it creates local
artifact metadata that the sandbox source can consume.

## Finch

Robin treats Finch as a data-analysis agent, including optional Edison data
analysis trajectories. Somatic maps Finch to local standard-library analysis:

- table profiling
- preliminary dose-response summaries
- provenance hashes
- deterministic `StructuredVerdict`

Future code-interpreter or package-backed analysis remains optional and must
use explicit extras, safety review, and no-network tests.

## Aviary-Like Environments

Aviary's reset/step/message/tool-call abstractions are useful for future
provider execution envelopes and benchmark environments. Somatic should model:

- initial observation and available tools
- action/tool-call request
- observation/reward/done/truncated result
- task/environment identity
- local artifact recording of every step

No Aviary task server, environment client, LLM, PaperQA, or benchmark runtime is
enabled in Phase 5F.

## LDP-Like Agent And Learning Process

LDP's agent state/action/value and rollout concepts are useful for a future
optional optimization/evolution lane. Somatic should keep this separate from
core workflow execution and represent rollouts as auditable artifacts before
any learning process is enabled.

No LDP agent, rollout manager, optimizer, compute graph, neural network,
server, monitor, or training path is enabled in Phase 5F.

## Provider Scaffold

`somatic.providers.robin.RobinProvider` is a disabled, fake-backed, reference
scaffold. It returns a local mapping plan and summary only. It fails closed if a
caller requests real mode or live execution.

The scaffold records:

- Robin, Aviary, and LDP source paths and commits.
- Apache-2.0 license status.
- Crow/Falcon/Finch attachment points.
- Aviary environment and LDP learning-process boundaries.
- Edison/OpenAI/Anthropic/PaperQA2 non-use status.

## Future Real Work

Any real provider work requires:

- explicit opt-in and optional extras
- data-locality and consent review
- secret boundary review
- local fixture tests first
- no default network calls
- no clinical, lab, or scientific validity claims from scaffold output
