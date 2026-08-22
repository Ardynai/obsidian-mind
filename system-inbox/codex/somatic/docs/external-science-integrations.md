# External Science Integrations

Phase 5A maps the external science systems Somatic may integrate next. Phase
5A.1 stages those sources under `C:\AI\external-sources\somatic\` for read-only
inspection. It does not install dependencies, run package managers, call APIs,
download model weights or datasets, vendor source, or enable live providers.
Phase 5B adds the first disabled optional adapter scaffold for PaperQA2.
Phase 5C adds a disabled metadata-only scaffold for scientific-agent-skills.
Phase 5E deepens the disabled AutoScientists-style team orchestration mapping.
Phase 5F deepens the disabled FutureHouse Robin/Aviary/LDP mapping.

## Local Inspection

Bounded local search across likely `C:\AI` paths looked for the requested
repository names and common variants:

- `paper-qa`, `paperqa`, `paper_qa`
- `robin`, `Future-House`, `futurehouse`
- `scientific-agent-skills`, `scientific_agent`
- `AutoScientists`, `autosci`
- `aviary`
- `ldp`
- `boltz`

Phase 5A found no local clones. Phase 5A.1 staged fresh shallow source clones
outside the Somatic repository. See `docs/external-source-staging.md` and
`fixtures/providers/external-source-inventory.json` for the exact machine
inventory.

## Integration Map

| Integration | Local path inspected or not found | Status | Role in Somatic | Risk/weight/dependency notes | Next phase recommendation |
| --- | --- | --- | --- | --- | --- |
| PaperQA2 / `Future-House/paper-qa` | `C:\AI\external-sources\somatic\paper-qa` at `d2c3c698fdf06986aa021812ab3186d3696438d8`; Apache-2.0 | scaffolded adapter | Literature retrieval, question answering over papers, and evidence-record drafting behind `LiteratureProvider` | Python `pyproject.toml`; `pqa = paperqa.agents:main`; dependencies include `fhaviary[llm]`, `fhlmi`, `httpx`, `numpy`, `tantivy`, and `tiktoken`; optional extras are broad; Phase 5B scaffold imports no PaperQA2 package at module import time | Phase 5B complete: disabled optional scaffold with deterministic fake-backed tests; future phase can add explicitly configured real mode |
| FutureHouse Robin / `Future-House/robin` | `C:\AI\external-sources\somatic\robin` at `4a5cce310f3bc7663a67117db88af43b84733ffe`; Apache-2.0 | reference-only scaffold | Reference mapping for planner/analyzer shape around Crow, Falcon, Finch, Evidence Bus, and StructuredVerdict | Python 3.12+; depends on `fhaviary`, `fhlmi`, `openai`, `anthropic`, `edison-client`, and `pandas`; no default runtime adoption; Phase 5F scaffold imports no Robin package | Phase 5F complete: disabled fake-backed Robin stack provider scaffold and source inspection docs |
| K-Dense-AI / `scientific-agent-skills` | `C:\AI\external-sources\somatic\scientific-agent-skills` at `effb57c5699c1d400ef461a7aa80fc6693939805`; MIT | scaffolded adapter | Metadata-only skill and database connector provider for task-to-method lookup, protocol references, and future scientific tool planning | Agent Skills catalog with 143 inspected `skills/*/SKILL.md` files; helper scripts use scanner dependencies; individual skills may require APIs, packages, cloud, or lab systems; Phase 5C does not execute or parse live skills | Phase 5C complete: disabled metadata-only scaffold with deterministic fake-backed catalog; future phase can add static frontmatter parsing |
| Harvard AutoScientists / `mims-harvard/AutoScientists` | `C:\AI\external-sources\somatic\AutoScientists` at `c71a92343b9a488ed10134be805845b9473ad18f`; no license file found | reference-only scaffold | Team orchestration reference for hypothesis critique, role assignment, evidence budgeting, blackboard state, stall detection, and reorganization | `launch.py` and templates assume a local ClawInstitute/AnonAPI service and API key trail; `requirements.txt` lists `requests` and `pyyaml`; Somatic does not import, execute, install, or copy it | Phase 5E complete: Somatic-owned deterministic TeamOrchestrator mapping and disabled fake-backed provider scaffold; live work remains blocked on license review |
| aviary / `Future-House/aviary` | `C:\AI\external-sources\somatic\aviary` at `826577f332a02ec2f5883cdb042fb12f14b4c7b3`; Apache-2.0 | reference-only fixture | Agent environment, task dataset, message, and tool-call reference for future benchmark/provider design | `aviary = aviary.main:cli`; optional extras include cloud, LLM, notebook, server, and benchmark/task packages; Somatic keeps this as execution-envelope metadata only | Phase 5F complete: placeholder fixture and source inspection docs |
| ldp / `Future-House/ldp` | `C:\AI\external-sources\somatic\ldp` at `d49850ff3addb8369df062d345ea99991b7b200c`; Apache-2.0 | reference-only fixture | Optional learning/agent-process reference for future benchmark or orchestration experiments | Depends on Aviary and LLM/agent libraries; contains agent, rollout, optimizer, monitoring, server, visualization, fhlmi/LiteLLM, and optional neural-network lanes | Phase 5F complete: placeholder fixture and source inspection docs |
| Boltz-2 / `jwohlwend/boltz` | `C:\AI\external-sources\somatic\boltz` at `b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc`; MIT | scaffolded adapter | Biomodel planning target for protein or molecular prediction workflows behind `BiomodelProvider` | Heavy stack: torch, PyTorch Lightning, RDKit, scipy, numba, fairscale, W&B, CUDA optional; `boltz predict` can download model/data and call MSA server; Phase 6A scaffold imports no Boltz package and runs no predictions | Phase 6A complete: disabled fake-backed plan/result metadata, doctor status, fixtures, and tests; future real mode needs explicit opt-in, downloads/MSA/resource gates, provenance hashes, and safety review |

## Safe Adapter Surface

Somatic should wrap useful external capabilities behind Somatic interfaces:

- Literature providers return document metadata and evidence-record drafts.
- Skill providers return static method or protocol metadata and never execute tools during lookup.
- Robin-style providers expose planner/analyzer steps through Evidence Bus artifacts.
- Team orchestration providers return reviewable plans and summaries before any live agent run.
- Biomodel providers separate run planning from model execution and declare all data, weight, license, and compute requirements.
- Benchmark providers operate on local fixtures and saved artifacts before any external leaderboard, cloud, or telemetry path exists.

## Non-Adoption Rules

Somatic should not adopt any external system wholesale as core runtime owner. In
particular, future integrations must not:

- Replace Somatic workflow manifests, Evidence Bus contracts, safety gates, or run artifacts.
- Make the basic install depend on heavy science, model, agent, or web stacks.
- Introduce default network calls, model downloads, telemetry, or external API credentials.
- Give providers raw health, patient, or private user data unless explicitly configured and consented.
- Execute lab actions, biomodels, code packs, or live agents without explicit enablement and human review.
- Import external packages from placeholder modules or tests.

## Current Artifacts

Phase 5A and Phase 5B add disabled provider metadata fixtures and scaffold docs for:

- `fixtures/providers/paperqa2-provider-placeholder.json`
- `fixtures/providers/paperqa2-provider-mock-config.json`
- `fixtures/providers/scientific-agent-skills-provider-placeholder.json`
- `fixtures/providers/scientific-agent-skills-provider-mock-config.json`
- `fixtures/providers/scientific-agent-skills-sample-catalog.json`
- `fixtures/providers/robin-provider-placeholder.json`
- `fixtures/providers/aviary-provider-placeholder.json`
- `fixtures/providers/ldp-provider-placeholder.json`
- `fixtures/providers/autoscientists-provider-placeholder.json`
- `fixtures/providers/boltz2-provider-placeholder.json`
- `fixtures/providers/boltz2-provider-mock-config.json`
- `fixtures/biomodel/biomodel-request-placeholder.json`
- `fixtures/biomodel/biomodel-plan-placeholder.json`
- `fixtures/biomodel/biomodel-result-placeholder.json`
- `fixtures/providers/external-source-inventory.json`
- `docs/paperqa2-source-inspection.md`
- `docs/paperqa2-adapter.md`
- `docs/scientific-agent-skills-source-inspection.md`
- `docs/scientific-agent-skills-adapter.md`
- `docs/autoscientists-source-inspection.md`
- `docs/autoscientists-mapping.md`
- `docs/robin-source-inspection.md`
- `docs/aviary-source-inspection.md`
- `docs/ldp-source-inspection.md`
- `docs/futurehouse-robin-mapping.md`
- `docs/boltz-source-inspection.md`
- `docs/biomodel-provider-boundary.md`
- `docs/boltz-adapter.md`

These fixtures and docs do not create default provider loading, dependency
installs, skill execution, or network/API surfaces. The PaperQA2 and
scientific-agent-skills scaffolds have deterministic mock modes only unless a
future real adapter is explicitly configured and consented. The AutoScientists
scaffold is reference-only and fake-backed because no license file was found.
The Robin/Aviary/LDP scaffolds are reference-only and fake-backed despite
Apache-2.0 source licenses because runtime adoption still needs explicit
optional extras, service, data-locality, and safety gates.
The Boltz scaffold is fake-backed despite MIT source licensing because model
downloads, MSA server calls, GPU/runtime execution, and scientific
interpretation require explicit future implementation and consent.
