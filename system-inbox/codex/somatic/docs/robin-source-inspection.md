# Robin Source Inspection

Phase 5F inspected the staged FutureHouse Robin source as read-only reference
material. Somatic did not install dependencies, run package managers, execute
Robin notebooks, import Robin modules, call Edison, call external LLM providers,
or copy Robin source.

## Source

- Repository: `Future-House/robin`
- Local path: `C:\AI\external-sources\somatic\robin`
- Inspected commit: `4a5cce310f3bc7663a67117db88af43b84733ffe`
- License: Apache-2.0, `LICENSE` present
- Inspection mode: static file review

## Entry Points And Runtime Shape

The README presents Robin as a multi-agent system for automating scientific
discovery. The user-facing flow is notebook driven through `robin_demo.ipynb`
and `robin_full.ipynb`, with programmatic functions exposed from the `robin`
package:

- `experimental_assay`
- `therapeutic_candidates`
- `data_analysis`

The runtime writes structured output folders under `robin_output/`, including
literature reviews, detailed hypotheses, ranking CSVs, summaries, and optional
Finch data-analysis outputs.

## Roles And Dependencies

`robin/configuration.py` defines Edison-backed agent role defaults:

- Crow for assay literature search.
- Crow for assay hypothesis reports.
- Crow for candidate literature search.
- Falcon for candidate hypothesis reports.

The README and package metadata show these non-core Somatic dependencies:

- `edison-client` and `EDISON_API_KEY`
- `openai`, `anthropic`, and LiteLLM-style provider configuration
- `fhaviary`
- `fhlmi`
- `pandas`
- `pydantic`
- `aiofiles`, `choix`, `python-dotenv`, and `tqdm`

`multitrajectory_runner.py` defines `StepConfig`, `Step`, and
`MultiTrajectoryRunner` around Edison task requests, prompt templates, file
uploads/downloads, parallel tasks, and saved result JSON.

## Somatic-Reusable Concepts

Somatic can reimplement these ideas behind its own contracts:

- Crow-style literature context as `LiteratureProvider` metadata and Evidence
  Bus records.
- Falcon-style measurement and candidate planning as local `MeasurementPlan`
  artifacts.
- Finch-style analysis as the existing standard-library Finch toolbelt and
  `StructuredVerdict`.
- Step plans as reviewable local artifacts before any execution envelope is
  enabled.
- Ranking and summaries as deterministic reports with explicit limitations.

## Non-Adoption Rules

Somatic does not adopt:

- Edison platform calls.
- API-key runtime or provider spend.
- Robin notebooks as a workflow runtime.
- Robin source code, prompts, or task runner internals.
- External LLM/provider calls through OpenAI, Anthropic, LiteLLM, or fhlmi.
- pandas or other package-backed analysis as a basic dependency.
- Clinical, lab, or therapeutic claims from scaffold output.

Robin remains a reference for architecture only in Phase 5F.
