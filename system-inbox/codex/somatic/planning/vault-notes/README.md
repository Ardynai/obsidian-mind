---
title: Somatic — Review Hub
status: living note
owner: Josh (Ardynai)
reviewer: Fable 5
last_updated: 2026-07-02
tags: [somatic, review, index]
---

# Somatic — Review Hub

Standalone body/health/somatic AI system. Currently **metadata / contracts / fixtures / docs / tests only** — no runtime. This folder holds the Fable 5 review of the repo at `main = ac4d622` with **[[Workflow Mode Chain 12N-12T|Phase 12T]]** open as draft PR #65.

## Map of this folder
- [[Phase Map]] — full phase timeline 0 → 12T
- [[Safety Invariants]] — what fail-closed guarantees hold, and where they're fragile
- [[Runtime Blockers]] — the list of things that must stay off
- [[Fabric Consumer Boundary]] — why Somatic does NOT rebuild transport
- [[Workflow Mode Chain 12N-12T]] — the review-pipeline mini-architecture
- [[Open Questions]] — decisions for Josh / orchestrator
- [[Recommended Next Phases]] — 12U → 12V → … with tags

## One-line state (2026-07-02)
Local = origin = live `main` = `ac4d622`; worktree clean. **PR #65 (Phase 12T)** = OPEN / draft / MERGEABLE / CLEAN, CI `unittest` pass, +2837/−93 over 5 files. Genuinely metadata-only & fail-closed. **Not yet sent to Jules.**

## The core seam
Somatic is **standalone-first**: it must stay usable without [[Locus]] or [[Multiverse]]. Those are peers/consumers/orchestrators, never mandatory owners. Every runnable path ends fail-closed (`execution_permitted = False`). See the vault [[SOMATIC_MASTER_PLAN]] for product vision (autonomous-science harness fusing Robin + AI co-scientist + AutoScientists).

## Roles (from Master Plan)
- **ChatGPT** = planner/PM · **Codex** = builder (one phase at a time) · **Fable 5 / Claude** = architect / verifier · **Jules** = security/medical-safety gate · **Claude Code** = visual/UI + subagent flows.
