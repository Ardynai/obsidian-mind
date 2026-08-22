# LDP Source Inspection

Phase 5F inspected the staged FutureHouse LDP source as read-only reference
material. Somatic did not install dependencies, run package managers, import
ldp, execute rollouts, train models, start servers, call external providers, or
copy LDP source.

## Source

- Repository: `Future-House/ldp`
- Local path: `C:\AI\external-sources\somatic\ldp`
- Inspected commit: `d49850ff3addb8369df062d345ea99991b7b200c`
- License: Apache-2.0, `LICENSE` present
- Package name: `ldp`

## Core Concepts

LDP models language decision processes around agents, environments, rollouts,
and optimization. The inspected source exposes:

- `Agent`: async `init_state(tools)` and `get_asv(agent_state, obs)`.
- Agent action/state/value triples for language-agent decisions.
- `RolloutManager`: samples trajectories from environment factories or
  concrete environments.
- Callback hooks around environment reset, agent state initialization, and
  rollout steps.
- `compute_graph` and operation abstractions for stochastic computation graph
  style execution.
- Optimizer and memory modules for optional learning/optimization lanes.

## Dependency Weight

The base project depends on `fhaviary`, `fhlmi`, `httpx-aiohttp`, `numpy`,
`pydantic`, `tenacity`, and `tqdm`. Optional extras add materially heavier
stacks:

- `nn`: torch, transformers, accelerate, dask, distributed, and CUDA-adjacent
  dependencies.
- `monitor`: W&B.
- `server`: FastAPI.
- `visualization`: pydot and graph visualization.
- bundled `fhlmi`: LiteLLM/OpenAI/orjson and provider-facing helpers.

The source and fixtures include OpenAI and Anthropic provider paths through
fhlmi/LiteLLM. Somatic does not use those paths.

## Somatic-Reusable Concepts

Somatic can reimplement these ideas behind optional future lanes:

- Agent process metadata with explicit state/action/value records.
- Rollout summaries as local artifacts.
- Callback/event timelines for auditability.
- Optional optimization/evolution planning after deterministic fixtures exist.
- Compute-graph lineage as provenance metadata, not as a required runtime.

## Non-Adoption Rules

Somatic does not adopt:

- LDP as a basic dependency.
- LDP agents, rollout managers, servers, monitors, or optimizers as runtime.
- fhlmi, LiteLLM, OpenAI, Anthropic, torch, transformers, W&B, or CUDA paths.
- Any training or live optimization behavior.

LDP remains a reference for future optional optimization and evolution lanes
only.
