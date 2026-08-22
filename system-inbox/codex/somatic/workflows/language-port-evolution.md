# Language Port Evolution Workflow

This workflow records Josh's plan to use Locus Evolution Lab for selective rewrites, language-port experiments, and implementation diversity across Ardynai repos.

## Purpose

Language-port evolution is not a blanket rewrite mandate. It is a controlled workflow for comparing implementations across languages and using the best language for each subsystem.

Primary goals:

- improve performance, safety, and maintainability
- train Ardynai coding agents across multiple languages
- produce better implementation alternatives through artificial selection
- harden critical modules through independent implementations
- reduce copyability of private implementation details where practical
- preserve clean provenance and ownership records

## Rule: do not rewrite everything

Do not rewrite full repositories just because Rust or another language is available. Rewrites are expensive, risky, and can slow product delivery.

Use language ports for modules where the tradeoff is worth it.

## Good Rust candidates

Rust is preferred for:

- Content Fabric canonicalization, signing, verification, keyring, and installer logic
- pack quarantine, sandbox, and enablement code
- path-confinement and file-integrity code
- high-throughput protocol bridge components
- registry hot paths that need deterministic performance
- WASM modules shared between desktop, web, and local agents
- financial screening/scoring engines
- audio DSP and waveform/feature analysis
- local data pipelines that need safety and speed

## Good TypeScript/Next.js candidates

TypeScript stays preferred for:

- web UI
- dashboards
- marketplace/admin panels
- SDK ergonomics
- plugin/harness glue
- rapid product iteration
- API surface where developer adoption matters

## Good Python candidates

Python stays preferred for:

- ML experimentation
- notebooks/research
- data science
- quick financial research prototypes
- model wrappers
- agent orchestration experiments

## Good Go/Zig candidates

Go or Zig may be considered for:

- standalone services
- CLIs
- single-binary utilities
- network daemons
- deployment agents

## Private-code protection note

Language ports can make direct copying harder and can allow binary/WASM distribution, but language choice alone is not legal protection.

Use these protections together:

- private repos
- signed commits/releases
- clear license/provenance headers
- commit history showing original authorship
- internal design docs
- reproducible fixtures and tests
- no leaked secrets/prompts
- no copied third-party code without license review

## Evolution loop

For each candidate module:

1. GitNexus maps the existing implementation.
2. Locus defines invariants, tests, fixtures, and scoring metrics.
3. Codex/KimiClaw/Hermes creates one or more language-port candidates.
4. Test outputs must match existing behavior.
5. Score candidates on correctness, speed, safety, maintainability, binary size, deployability, and interop.
6. Keep the winner or preserve the port as a reference implementation.
7. Document why the selected language was chosen.

## First targets

| Target | Candidate language strategy | Reason |
| --- | --- | --- |
| Content Fabric | Rust core + TS bindings/WASM | Byte-exact canonicalization and signing require deterministic shared behavior. |
| Multiverse protocol bridge | TS shell + Rust hot-path modules where useful | Keeps SDK ergonomics while improving core transport reliability. |
| Kortex Audio DSP/analysis | Rust/Python comparison | Rust for production DSP, Python for research. |
| Future financial repo | Rust/Python comparison | Python for research, Rust for fast deterministic screeners/scoring. |
| Somatic | Inspect first | Port only after architecture is known. |

## OpenClaw/Codex starter prompt

```text
Inspect the target repo/module first. Do not rewrite the whole repo. Identify 1-3 modules where a Rust, Go, Python, or TypeScript implementation would materially improve performance, safety, determinism, deployability, or agent-training value. Propose a language-port experiment with invariants, tests, scoring metrics, and rollback plan. Do not implement until Josh approves one target.
```
