# Locus Operator Surface

This workflow defines the Locus-native operator surface for `locus-evolution-lab`.

The goal is to make Locus Evolution Lab more useful as a planner, evaluator, workflow library, and hardening system without changing its identity into another project's structure.

## Purpose

Locus Evolution Lab coordinates evolution, testing, hardening, scoring, and best-use workflows across the Ardynai project family:

- `Ardynai/locus`
- `Ardynai/locus-evolution-lab`
- `Ardynai/multiverse`
- `Ardynai/kortex-audio`
- `Ardynai/somatic`
- future financial/day-trading repo
- `ardynos`
- related local tools and content-generation systems

The repo should become a clean operator layer for:

- repo intelligence before mutation
- workflow templates
- install/use guidance
- gated execution doctrine
- scoring and evaluation
- conformance testing
- language-port experiments
- Content Fabric interop
- project-specific best-result workflows

## Non-goals

Do not turn this repository into a clone of any external operator repo.

Do not make it Claude-centric.

Do not add broad live hooks, gateway changes, installs, scans, or cron jobs by default.

Do not bury Locus's core purpose under generic agent boilerplate.

## Core surfaces

| Surface | Purpose |
| --- | --- |
| `workflows/` | Human-readable workflow plans and hardening/evolution playbooks. |
| `agents/` | Role definitions for systems that participate in workflows. |
| `manifests/` | Machine-readable workflow declarations. |
| `schemas/` | JSON schemas for manifests, scoring, gates, and reports. |
| `hooks/` | Planned hook contracts; disabled unless explicitly implemented and gated. |
| `scoring/` | Fitness, safety, quality, cost, and conformance scoring. |
| `registries/` | Repo, tool, content pack, workflow, and target classification. |
| `projects/` | Project-specific coordination plans. |
| `prompts/` | Short dispatch prompts for OpenClaw, GitNexus, Codex, KimiClaw, Hermes, Evolver, and other systems. |

## Design principles

1. **Locus-first**
   - Every surface must support Locus's actual role: evolution lab, hardening planner, workflow library, and project-family coordinator.

2. **GitNexus-first**
   - Source intelligence comes before code mutation, workflow conversion, rewrites, hardening, or installation.

3. **OpenClaw-led documentation**
   - OpenClaw coordinates and documents, but no workflow may assume automatic execution without Josh approval.

4. **Manifest after proof**
   - Do not create elaborate machine-readable manifests for unproven workflows. Start with human-readable workflow, prove it, then manifest it.

5. **Hooks are contracts before code**
   - Hook specs may be written before implementation. Live hooks require explicit approval, tests, rollback, and gating.

6. **Project-family specialization**
   - Templates should be specific enough for Multiverse, Kortex Audio, Somatic, finance, content creation, ArdynOS, and Content Fabric.

7. **No hidden side effects**
   - Any command, file, network, browser, trading, install, or gateway-changing action must surface a gate and be auditable.

## First operator-surface priorities

1. Add role definitions for participating agents/systems.
2. Add workflow manifest schema drafts.
3. Add scoring card schema drafts.
4. Add hook contract drafts for post-run summaries, audit capture, and conformance reports.
5. Convert only proven workflows into manifests.
6. Add project-specific best-use templates for Kortex Audio, Somatic, Multiverse, future finance, content creation, and ArdynOS.

## Gate

This operator surface is planning and structure only. It does not authorize live hooks, installs, scans, cron jobs, or code mutation.