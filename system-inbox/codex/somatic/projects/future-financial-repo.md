# Future Financial Repo Workflow Plan

This document records Josh's plan for a future Ardynai financial/day-trading repo that may reuse the Somatic-style framework with different data and domain logic.

## Working concept

The future financial repo should act like a Somatic-style analytical system for markets:

- ingest market, news, fundamentals, technical, and user-preference data
- understand what the user is asking for
- screen stocks or assets against that request
- explain why candidates match
- compare strategies and risk
- support paper-trading and research workflows before any live trading

## Relationship to Somatic

Somatic may provide reusable framework ideas:

- state models
- signal/feedback loops
- agent memory patterns
- analysis-to-action gates
- human-in-the-loop review
- simulation-first behavior

The financial repo should reuse concepts only after Somatic is inspected. It should not blindly copy code or architecture.

## Relationship to Locus Evolution Lab

Locus will provide:

- workflow templates for financial screening
- prompt templates for research and analysis
- scoring systems for strategy quality
- language-port experiments for fast screeners/scoring engines
- GitNexus-first repo intelligence before mutation
- safety and provenance documentation
- user/AI install guidance

## Relationship to Content Fabric

Financial packs may eventually use Content Fabric for:

- indicator packs
- strategy templates
- screened watchlists
- research datasets
- model/eval fixtures
- paper-trading reports

Code packs must follow quarantine/signature/consent/sandbox/enable rules.

## First workflow candidates

| Workflow | Purpose | Notes |
| --- | --- | --- |
| User request to stock screen | Turn natural language criteria into a reproducible screen | Must show data sources and filters. |
| Watchlist generator | Produce candidate stocks/assets matching a user thesis | Requires risk labels and uncertainty. |
| Strategy backtest template | Test historical behavior before recommendations | Paper/research only by default. |
| Risk and catalyst summary | Summarize risks, catalysts, earnings, sector context | Cite sources when live web data is used. |
| Paper-trading planner | Build hypothetical trades and review outcomes | No live trading by default. |

## Language strategy

- Python for research, data science, notebooks, and quick prototyping.
- Rust for deterministic high-speed screeners, scoring engines, and local data processing.
- TypeScript for UI, API, dashboards, and integration with Ardynai apps.

## Safety and legal boundaries

The repo should default to research and paper trading. Any live brokerage integration must be explicit, gated, logged, and separated from research mode.

Required defaults:

- no live trades by default
- no financial advice claims without disclaimers and scope control
- all data sources documented
- uncertainty and risk surfaced
- user approval before any irreversible or money-moving action
- API keys isolated and never printed

## Initial inspection prompt for later

```text
Inspect the new financial repo as source only. Do not install dependencies, run live trading tools, connect broker APIs, or create cron jobs. Map the architecture, data sources, analysis pipeline, risk controls, and similarities to Somatic. Propose the first three Locus workflows: stock screen, watchlist generation, and paper-trading evaluation. Stop after reporting.
```
