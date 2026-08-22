---
title: Somatic — Workflow Mode Chain 12N–12T
reviewer: Fable 5
last_updated: 2026-07-02
tags: [somatic, workflow, review-chain]
---

# Somatic — Workflow Mode Chain 12N–12T

Back to [[README]] · [[Phase Map]]. A self-contained "review pipeline that authorizes nothing" — the most sophisticated non-authorizing structure in the repo.

## The chain
| Phase | Role in the pipeline |
|---|---|
| **12N** | Registry of future mode labels (`normal-mode`, `fusion-mode`, `scientist-evolution-mode`) — metadata only |
| **12O** | Safety-gate **runtime-prerequisite matrix** — gates that must stay unsatisfied |
| **12P** | **Activation-request review packet** shape a future human/Jules review would need (`review-request-only`) |
| **12Q** | **Non-authorizing decision record** (only non-authorizing statuses allowed) |
| **12R** | **Audit-trail index** tying 12N–12Q together |
| **12S** | **Closeout summary** of the 12N–12R chain |
| **12T** | **Fabric transport consumer-readiness intake** (sources 12L + 12S) → [[Fabric Consumer Boundary]] |

## Why it matters
It models the *shape* of a human approval process — registry → prerequisites → request packet → decision → audit → closeout → next boundary — **without ever executing or authorizing anything**. Every phase re-asserts the same runtime-blocked trio (see [[Runtime Blockers]]).

## Observations
- Clean, legible, well-tested; a good template for future review chains.
- 12Q naming nit: its `rejected_` helper drops the `non_authorizing` infix the builder uses.
- Natural cap: a **12U master index / series closeout** over the whole 12A–12T arc → [[Recommended Next Phases]].
