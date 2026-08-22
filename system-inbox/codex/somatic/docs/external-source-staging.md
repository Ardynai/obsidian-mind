# External Source Staging

Phase 5A.1 stages external science repositories outside the Somatic checkout for
read-only inspection. The staged sources are references only. They are not
vendored into Somatic, imported by Somatic tests, or wired into runtime
adapters.

## Staging Policy

- Staging root: `C:\AI\external-sources\somatic\`
- Clone mode: shallow source clone with LFS smudge disabled.
- Dependencies installed: no.
- Package managers run: no.
- Setup scripts run: no.
- Model weights or datasets downloaded: no.
- External APIs called by staged source: no.
- External repos modified: no; all inspected working trees were clean after staging.

The machine-readable record is
`fixtures/providers/external-source-inventory.json`.

## Staged Source Inventory

| Repo | Local path | Commit | License | Ecosystem | Entrypoint notes |
| --- | --- | --- | --- | --- | --- |
| `Future-House/paper-qa` | `C:\AI\external-sources\somatic\paper-qa` | `d2c3c698fdf06986aa021812ab3186d3696438d8` | Apache-2.0 via `LICENSE` | Python, `pyproject.toml`, `uv.lock` | `pqa = paperqa.agents:main`; `src/paperqa/agents/__init__.py` argparse CLI; `PaperSearch`, `GatherEvidence`, `GenerateAnswer`; metadata clients under `src/paperqa/clients/` |
| `Future-House/robin` | `C:\AI\external-sources\somatic\robin` | `4a5cce310f3bc7663a67117db88af43b84733ffe` | Apache-2.0 via `LICENSE` | Python, `pyproject.toml`, `uv.lock` | `robin/*.py` modules for assays, analyses, candidates, configuration, literature, ranking, and tools; notebook demos |
| `K-Dense-AI/scientific-agent-skills` | `C:\AI\external-sources\somatic\scientific-agent-skills` | `effb57c5699c1d400ef461a7aa80fc6693939805` | MIT via `LICENSE.md` | Agent Skills repo with Python helpers | `skills/*/SKILL.md`; `scan_skills.py`; `scan_pr_skills.py` |
| `mims-harvard/AutoScientists` | `C:\AI\external-sources\somatic\AutoScientists` | `c71a92343b9a488ed10134be805845b9473ad18f` | No license file found | Python scripts and markdown templates; `requirements.txt` | `launch.py` argparse launcher; `system/templates/*`; `task-*` directories |
| `Future-House/aviary` | `C:\AI\external-sources\somatic\aviary` | `826577f332a02ec2f5883cdb042fb12f14b4c7b3` | Apache-2.0 via `LICENSE` | Python, `pyproject.toml`, `uv.lock` | `aviary = aviary.main:cli`; `Environment`, `TaskDataset`, `Tool`, and environment server CLI |
| `Future-House/ldp` | `C:\AI\external-sources\somatic\ldp` | `d49850ff3addb8369df062d345ea99991b7b200c` | Apache-2.0 via `LICENSE` | Python, `pyproject.toml`, `uv.lock` | `src/ldp/main.py`; `Agent`, `ReActAgent`, `SimpleAgent`, `RolloutManager`, optimizer and callback modules |
| `jwohlwend/boltz` | `C:\AI\external-sources\somatic\boltz` | `b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc` | MIT via `LICENSE` | Python, `pyproject.toml` | `boltz = boltz.main:cli`; `boltz predict`; `src/boltz/main.py`; train/process/eval scripts |

## Per-Source Notes

### PaperQA2

PaperQA2 was the Phase 5B target for a disabled literature adapter. Somatic now
has a scaffold in `somatic.providers.paperqa2` that wraps deterministic mock
document search, context/citation extraction, and evidence drafting behind
`LiteratureProvider`. The adapter does not adopt PaperQA's agent loop, storage
paths, LLM configuration, metadata clients, or optional document-reader
integrations as Somatic defaults.

Dependency weight is medium to heavy for Somatic's basic install: `fhaviary`,
`fhlmi`, `httpx`, `numpy`, `pydantic`, `tantivy`, `tiktoken`, plus many optional
extras. Keep imports inside an optional adapter module.

### FutureHouse Robin

Robin is useful as a reference for disease-candidate planning and analysis
workflow shape. Somatic should map concepts from assay planning, literature,
candidate ranking, and analysis into existing Crow/Falcon/Finch and Evidence
Bus artifacts. It should not replace Somatic's local `robin-loop`, run
notebooks, or activate provider API configuration.

Robin references `fhaviary`, `fhlmi`, `openai`, `anthropic`, `edison-client`,
`pandas`, and `pydantic`, so any future adapter must remain optional and
disabled by default.

### Scientific Agent Skills

The repository is best treated as a static skill catalog. Phase 5C adds a
metadata-only scaffold in `somatic.providers.scientific_agent_skills` that
returns deterministic mock `ScienceSkillRecord` and database connector metadata.
It does not install the full collection, execute skill scripts, or assume
individual skill dependencies are safe or locally available.

Some skills describe public database APIs, scientific packages, cloud/lab
systems, or package installation flows. Somatic must keep lookup separate from
execution.

### AutoScientists

AutoScientists provides useful team-orchestration concepts: launch material,
roles, monitors, workspaces, queues, experiment claims, result files, and
reorganization loops. Somatic should map those into `TeamOrchestrationProvider`
plans and summaries.

Somatic should not adopt the launcher, AnonAPI/ClawInstitute service contract,
API-key trail, generated workspaces, task execution, or task-specific hardware
requirements. No license file was found in the staged source, so any future
usage needs explicit license review before implementation.

### Aviary

Aviary was staged because PaperQA2 and Robin reference `fhaviary`. It provides
environment, task dataset, message, and tool abstractions. Somatic may use those
as reference shapes for future benchmark or provider environment adapters, but
should not host Aviary servers or execute tools by default.

### LDP

LDP is referenced by PaperQA2 optional extras and builds on Aviary agent and
environment concepts. Somatic should treat it as optional reference material for
future agent-process or benchmark-provider work, not as the core orchestrator.

### Boltz

Boltz is the likely Boltz-2 upstream for Phase 6 biomodel planning. The
repository includes `boltz predict` and model/data download paths in
`src/boltz/main.py`. A Somatic adapter should first expose only
`BiomodelProvider.plan`: inputs, cache requirements, model version, output
artifacts, assumptions, and limitations.

Do not enable automatic Hugging Face model/data downloads, MSA server calls,
CUDA/GPU execution, training/evaluation scripts, or W&B logging by default.
