# Aviary Source Inspection

Phase 5F inspected the staged FutureHouse Aviary source as read-only reference
material. Somatic did not install dependencies, run package managers, import
fhaviary, start a server, execute environments, or copy Aviary source.

## Source

- Repository: `Future-House/aviary`
- Local path: `C:\AI\external-sources\somatic\aviary`
- Inspected commit: `826577f332a02ec2f5883cdb042fb12f14b4c7b3`
- License: Apache-2.0, `LICENSE` present
- Package name: `fhaviary`

## Core Concepts

Aviary is a gymnasium-style framework for language-agent environments. The
core source exposes:

- `Environment`: async `reset()` and `step(action)` contract.
- `Message`: OpenAI-style role/content message abstraction.
- `ToolRequestMessage`: assistant message carrying requested tool calls.
- `ToolResponseMessage`: tool response message tied to a tool call id.
- `Tool`: callable tool metadata and execution wrapper.
- `TaskDataset`: task/environment collection abstraction.
- Optional dataset and environment packages for GSM8K, HotpotQA, LabBench,
  LFRQA, and notebook environments.

## Dependency Weight

The base package depends on `httpx`, `httpx-aiohttp`, `pydantic`, and
`docstring_parser`. Optional extras add heavier or network-adjacent stacks:

- `llm`: `fhlmi`, `litellm`, and packaging helpers.
- `server`: `fastapi`, `uvicorn`, and related serialization dependencies.
- `cloud`: `boto3`.
- environment extras: math, HotpotQA, LabBench, literature, notebook, image,
  and typing dependencies.

The LabBench and literature-style packages visibly reference PaperQA/LDP and
recorded OpenAI API traffic in test cassettes. Somatic does not use those paths.

## Somatic-Reusable Concepts

Somatic can reimplement these ideas without adopting Aviary:

- Provider execution envelopes with explicit reset/step-like phases.
- Message and tool-call records as local artifacts.
- Benchmark environment metadata for future optional evaluation lanes.
- Clear separation between environment state, tools, observations, rewards,
  termination, and truncation.

## Non-Adoption Rules

Somatic does not adopt:

- fhaviary as a basic dependency.
- Aviary task servers or environment clients.
- PaperQA/LDP-backed Aviary environment packages.
- External HTTP, LLM, notebook, cloud, or benchmark runtime.
- Live tool execution through Aviary.

Aviary remains a reference for future provider execution envelopes and
benchmark environment design only.
