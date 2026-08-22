# Somatic — Current Plan (the pivot)

> This is the **active** plan. For the north-star vision see `SOMATIC_MASTER_PLAN.md`; for the deep repo review see `phase-12t-review-and-plan.md`; for the next queue see `backlog.md`.

## The reframe (2026-07)
Phases 1–12X built a large metadata/contracts + governance scaffold where runtime was fail-closed everywhere — nothing could actually run. Josh's intent is to build the **real, user-owned capability**: if the user consents, Somatic uses **their own** health data to (a) surface personal insights, (b) get an AI/second-opinion read, (c) produce a doctor-shareable summary, and later (d) run personalized research (suggest tests / markers / experiments), (e) offer an evidence-graded remedy library, (f) support parasite research / identification.

Keep the **small load-bearing safety core** (informational framing + professional routing + emergency screen + consent) — it *enables* this vision and protects Josh legally — and drop the ~20 phases of governance ceremony.

This is a **single-user, consent-gated, informational decision-support** engine. It is **NOT** diagnosis, prescription, or dosing.

## What is SHIPPED on `main` (verified)
- **Consent** (`somatic/consent/`): 7 granular scopes, all default **OFF** — `data-ingestion`, `analysis-insight`, `ai-advisory`, `autonomous-research`, `proactive-suggestions`, `professional-sharing`, `remedy-library`; local ledger with grant / revoke / right-to-erasure (`purge_user_data`).
- **Safety core** (`somatic/safety/core.py`): evidence grades (STRONG…NONE); `emergency_screen` (chest pain, can't-breathe, stroke/FAST, suicidal, anaphylaxis, severe bleeding → see-a-clinician-now); `require_consent` (fail-closed); `frame_advisory` (attaches informational notice + professional routing; raises on authoritative "you have X / take N mg / prescribe / stop taking / diagnosed with").
- **AI advisory adapter** (`somatic/advisory/`): OpenAI-compatible (Agents-A1 via vLLM/SGLang, or Ollama at `localhost:11434/v1`). `analyze()` requires `ai-advisory` consent, emergency-screens before any network call, frames the response, and returns SAFE_FALLBACK (evidence NONE) rather than raw unsafe text.
- **Personal insights** (`somatic/insights/engine.py`): grades a metric vs the user's **own** baseline (z-score) and/or **caller-supplied** `ReferenceRange`. **No hardcoded medical normals** (there's a dedicated test enforcing this).
- **Flows**: `python -m somatic analyze` (emergency → consent-gated insights → optional consent-gated AI read; missing consent → skip-note, never crash) and `python -m somatic share` (clinician-facing Markdown, `professional-sharing` gated; pure reformat, no new claims).
- **Local UI**: `python -m somatic ui` (stdlib loopback on 127.0.0.1; SPA in `somatic/bridge/static/`). See `planning/UI-BUILD.md`.

## Roadmap — RE-SEQUENCED 2026-07-23 after the advisory review (`phase-13-advisory-review.md`)
The old roadmap led with the research loop — the highest-legal-exposure item — on top of two safety gates the review **proved porous by execution** and a consent model that's currently theater. The **finalized, risk-ordered queue lives in `backlog.md`** (authoritative); summary:

1. **CI memoization** — kill the ~33-min gate (partially shipped: PR #78 halved CI via test-replay dedup; full builder cache pending a snapshot-coverage extension).
2. **Consent persistence + `somatic consent` CLI** — make the shipped consent model real (persist/revoke/erase); pure stdlib.
3. **Safety-gate hardening + adversarial eval harness** — `frame_advisory` + `emergency_screen` are the legal shield; **hard gate: no medical-content work until this lands and "offline ⇒ honest null" is a tested invariant.**
4. **Data ingestion** (activates `data-ingestion`) — the product's front door.
5. **N-of-1 experiment designer** (promoted ahead of the research loop) — own-baseline, no retrieval.
6. **Research loop / co-scientist** — source-grounded (PubMed / ClinicalTrials / Consensus), never model memory; spec the retrieval + grounding FIRST.
7. **Evidence-graded remedy library** (`remedy-library`) — grade honestly; default NONE.
8. **Parasite research / identification** — informational, source-grounded, emergency-screened.

Later / opt-in: **proactive suggestions** (`proactive-suggestions`). Full per-item detail, effort, and gating: `backlog.md`.

## Design guardrails for the whole roadmap
- Everything new is **consent-gated** (add/extend a scope; default OFF) and **emergency-screened**.
- Anything making a health claim is **evidence-graded + source-grounded** — cite real literature via retrieval; never invent. Prefer retrieval (PubMed / ChEMBL / ClinicalTrials / bioRxiv / Consensus) over model memory.
- Keep `frame_advisory` in the path — no diagnosis / prescription / dosing wording.
- stdlib-only; `dependencies` stays `[]`; additive.

## Capabilities Josh asked to fold in (assess, don't force)
- **Agents-A1** (35B agentic science model) — already wired as a model option in `somatic/advisory/models.py`; run it via vLLM/SGLang or point the adapter at any OpenAI-compatible endpoint.
- **brain2qwerty** (non-invasive neural decoding) and **microbubbles / Ultratrace ULM** (transcranial ultrasound) — research-stage sensing ideas from the master plan's sensor roster; keep behind the Evidence-Source boundary, sandbox-only, far future.
