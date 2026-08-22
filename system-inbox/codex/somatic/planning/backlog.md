# Somatic — Backlog (one batch at a time)

> The operator takes the **top unblocked** item, builds it to a green-CI PR, merges, then returns for the next. The planner (Fable 5) triages new findings into this queue. Keep batches small + additive. Full rationale for the re-sequencing + every finding below: **`planning/phase-13-advisory-review.md`** (2026-07-23 advisory review).
>
> **Autonomous mode:** for a continuous, self-reviewing, no-stop build of this whole queue (Grok 4.6 + Cursor), the operating charter is **`planning/AUTONOMOUS-BUILD-MODE.md`** — it wraps this queue with the safety gates, the self-review loop, and the hard-stops. **`planning/clinfusion-assessment.md`** = the "considered & declined" note on `alibaba-damo-academy/ClinFusion` (do not wire a GPU radiology MLLM into the stdlib spine).

## Shipped on `main` (verified 2026-07-23)
- **#75 analyze**, **#76 share**, **#77 docs/handoff** — MERGED. Spine tests green; `dependencies == []`; ruff clean on the spine.
- **#78 CI memoization (partial)** — MERGED (`b4c7f71`). Test-only: one shared `doctor` capture (`tests/doctor_fixture.py`) consumed by 7 suites. **CI ~33 → ~17 min.** The runtime builder cache was correctly deferred (see item 1b). Sol's operator advisory + finished-product sim confirmed findings F1–F18 (extensions folded in below).
- **Planner docs pending on `main`:** the advisory review, re-sequenced backlog, `current-plan.md` truth-up, `CLAUDE.md`/`AGENTS.md` updates are in the working tree but NOT yet committed to `main` (operator lands them as step 0 next run — see `.tmp/TASK-*`). A stale `.git/index.lock` + lingering git procs are on the host box; clear before committing from `C:\AI\somatic`, or build from a clean sibling clone.

## Why the order changed (2026-07-23, finalized with Josh)
The old queue led with the **research loop** — the highest-legal-exposure, most-external-dependency item — on top of two safety gates the advisory review **proved porous by execution** and a consent model that's currently theater. Re-sequenced so a velocity win opens, prerequisites lead, and every medical-content item is gated behind a hardened spine. Josh delegated the final sequencing to the planner: **lead with CI memoization** (compounds across every later batch), then the consent foundation, then the safety shield; **promote the N-of-1 experiment designer ahead of the research loop** (own-baseline math, no retrieval, lower risk). **Hard rule: do NOT start the medical-content items (research loop / remedy library / parasite ID, items 6–8) until safety-gate hardening (item 3) lands and "offline ⇒ honest null" is a tested invariant.**

## Queue (finalized order)

**1. CI memoization — test-replay dedup.** `[safe-now]` · **DONE — PR #78.** ✅
The 7 test suites that each replayed full `doctor` (~110s apiece) now share one capture (`tests/doctor_fixture.py`). CI ~33 → ~17 min; test-only, zero monolith/snapshot/dep change. Banked the bulk of the velocity win.

**1b. CI memoization — finish the runtime builder cache.** `[gated, snapshot-proven]` · **DONE — autonomous/roadmap.** ✅
Extended `tests/test_status_summary_snapshot.py` + `fixtures/snapshots/status-summaries-v1.json` to 33 entries (27 zero-arg + 3 doctor-invoked required-arg summaries × 2 canonical domains). Then memoized hashable-arg builders/`*_status_summary` via `somatic/safety/_builder_cache.py` (deepcopy on return). Snapshot matched after cache; no fixture edit post-cache. Monolith not rewritten.

**2. Consent persistence + `somatic consent` CLI.** `[safe-now]+[founder]` · **DONE — autonomous/roadmap.** ✅
On-disk JSON store (`~/.somatic/consent.json` or `SOMATIC_CONSENT_PATH`) with `0600`; `somatic consent grant|revoke|status|erase` (`erase` → `purge_user_data` + delete file). `analyze`/`share` load the store; `--grant` remains a session overlay. `from_dict` fail-closed: any invalid load → all-OFF. Encryption default: plaintext under user file perms (stdlib has no AES).

**3. Safety-gate hardening + stdlib adversarial eval harness.** `[gated]` · **DONE — autonomous/roadmap.** ✅
`frame_advisory` catches paraphrased dx/dosing and no longer over-matches "you have been sleeping" / `prescribed dose`. Insights skip the model denylist (engine templates) and analyze swallows leftover framing errors. `emergency_screen` broadened (faint/seizure/overdose/hemoptysis/melena/thunderclap/crushing pressure/SI paraphrases), does not halt risk-trend/"stroke rate", routes SI to US 988, NFKC+zero-width+spaced-letter normalize, re-screens model output. Adversarial corpus is a CI unittest. Language scope: English-only (documented).

**4. Data ingestion — CSV first, then Apple Health export.** `[gated]` (personal-data) · **DONE — autonomous/roadmap.** ✅
`somatic ingest csv|apple-health|status|erase` behind `data-ingestion` (default OFF). Timestamped `somatic.packet.v1` readings; analyze/share surface `observed_at`. Local readings store (`SOMATIC_INGEST_PATH` / `~/.somatic/readings.json`) is erased with `consent erase` and `ingest erase`.

**5. N-of-1 experiment designer.** `[gated]` · **DONE — autonomous/roadmap.** ✅
`somatic experiment evaluate|tag|status|erase`. Own-series split at a tagged timestamp; reuses `grade_metric` z-math; movement is toward/away/stable vs the user's pre-tag baseline. No retrieval, no population normals. Tags persist under `SOMATIC_EXPERIMENT_PATH` and erase with consent.

**6. Research loop / co-scientist (N-of-1).** `[gated]` · **DONE — autonomous/roadmap.** ✅
Offline-corpus v1 (`somatic research ask`). Stdlib BM25; citation-binding drops any claim whose cite does not resolve to a retrieved passage; no model memory. No source ⇒ `No evidence available; consult a professional` (tested). Live PubMed left off (scope still says offline/mock).

**7. Evidence-graded remedy library.** `[gated]` · **DONE — autonomous/roadmap.** ✅
`somatic remedy lookup`. Reuses citation-binding; default/unbound grade **NONE**; folk-remedy surface capped at LIMITED; always attaches non-prescription safety notes.

**8. Parasite research / identification (informational).** `[gated]` · **DONE — autonomous/roadmap.** ✅
`somatic parasite ask`. Same citation-binding substrate; emergency-screened; fixture states it does not identify species; unbound queries honest-null.

**Master-plan sandbox runtime (P1–P12 plugins, hardware closed).** `[gated]` · **DONE — autonomous/master-plan-runtime.** ✅
Stdlib sandbox plugins for the north-star in `SOMATIC_MASTER_PLAN.md`. Core `dependencies` stay `[]`. Optional extras (`video3d`, `thermal`, `presence`, existing `csi`/`video`/`audio`/`bench`) are listed but **never imported** by these paths.

- Evidence Bus: runnable sandbox adapters for every modality (`bus run`); `EvidenceSource` stays a record dataclass.
- Sensor roster: CSI / RGB / 3D-depth / thermal / audio / wearable / environmental; `sensor-roster list|scan|fuse`; `--live` refused; `LIVE_SENSOR_INTEGRATION_IMPLEMENTED` remains false; RF↔vision fusion of simulated joints only.
- Science harness: tournament + teams + bus + stdlib Beta belief + entropy/cost falsifier + name-only biosecurity refuse-list (`science run`). No NumPyro, no spend.
- Avatar: render-only Scientist/Doctor (`avatar speak`); TTS / talking-head / camera / mic disabled.
- Bench: sandbox ripasudil/dAMD scoring (`bench-run`); `dollars_spent: 0`.
- Provenance: content-addressed SHA-256 verify (`evidence-verify`); p2p distribution disabled.

Not built (hard-stop / extras / founder): live ESP32/webcam/BLE, Boltz-2, NumPyro, MiniCPM/Duix, scientific-agent-skills execution, live PubMed, LICENSE.

**Local graphical UI.** `[safe-now]` · **DONE.** `python -m somatic ui`. Stdlib loopback bridge + shipped SPA.

**Sensor Field visualization + ESP32 CSI ingest.** `[gated]` · **THIS BATCH.** Sandbox Field / Body view (pose + occupancy, no hardware). Loopback UDP CSI ingest (stdlib, 127.0.0.1:53721, off until live grant + subject consent). Firmware/booth how-to in `docs/hardware/esp32-csi.md`. Multi-unit occupancy fusion + founder-gated pose-model seam (wired, off, no weights). Status: sandbox-verified; needs a real ESP32 to validate live. Core `dependencies` stay `[]`.

Not built (hard-stop / extras / founder): webcam/BLE live capture, enabling the CSI pose model, Boltz-2, NumPyro, MiniCPM/Duix, scientific-agent-skills execution, live PubMed, LICENSE, buying hardware, public release.

## Parallel [safe-now] wins (interleave anytime — adoption + correctness)
- **F12 fail-loud on malformed input.** **DONE.** ✅ Clean-and-keep series; notes for dropped `n/a` and `min/max` refs.
- **F14 clinician-doc polish (share).** **DONE.** ✅ Generation timestamp; z-branch includes the flagged reading; small-n z annotated; one disclaimer + one routing line; sample-size labels (not GRADE); human provenance + debug appendix; optional `--fhir-out` sidecar. Per-reading dates land with item 4 timestamps.
- **F9 doctor spine-status.** **DONE.** ✅ Additive consent/adapter/emergency-screen section.
- **F15 docs truth-up.** **DONE.** ✅ README current-product lead + pre-pivot archive banner; ARCHITECTURE rows for the spine.
- **F13 `/v1/v1` fix** (adapter base-URL dedupe) · **F10 check share consent before the AI POST** · **F11 adapter SSRF/redirect/https-with-key hardening + F19 `--model-key` reads from env not argv** · **F17 share Markdown-injection escape** — **DONE on autonomous/roadmap.** ✅ · **F16 pick a LICENSE** (`pyproject` still "License not selected"; blocks OSS/monetization — founder; hard-stop, not chosen).
- **Promotion gates (Sol):** treat **F14 (clinician-doc dates/units/values)** and **F15 (docs truth-up)** as *gates on advertising the product as clinician-shareable / user-ready*, not optional polish — don't promote the artifact or the README claims until they land. Also: model-provided evidence grades should be labeled **"confidence"** (not "evidence") until citation-bound in item 6, and model output must be **emergency-re-screened** (batch 3), not only framed.
- **Hygiene:** `.claude/` + `.specify/` gitignored; `somatic/safety/__init__.py` no longer says scaffolded. Remaining: spine-scoped ruff CI ratchet; `packages/*` vs `somatic/*` taxonomy; prune stale `codex/phase-*` branches (not done — avoid remote branch deletion).

## Bold, on-mission (evaluate — review §7)
Signed portable "health-data capsule" (user-owned, clinician-verifiable) · one-command BYO-local-model (`analyze --local` → Ollama) · unified local store (ledger+data+audit under one erasure hook). *(The N-of-1 experiment designer graduated from this list to queue item 5.)*

## Monetization (founder — review §5)
Primary direction: signed evidence-graded content packs over a free OSS core + BYO-model (sell content, not a service; stays local; reuses `fabric/` signing). **Near-term honest path = donations/grants** — paid packs are not commercially ready yet (Sol): Fabric's "license gate" is redistribution-policy enforcement, NOT entitlement/payment/revocation infrastructure. Paid packs need, first: the LICENSE decision, entitlement + update + withdrawal + revocation mechanisms, required citation/evidence metadata, and hardened safety gates + offline-honest-null enforcement (item 3 + item 6). Rule OUT (identity change): hosted or clinician SaaS (custodies health data).

## Do NOT (without explicit Josh approval)
Add runtime deps; touch fabric byte-pinned interop vectors; rewrite the `phase12_contracts.py` monolith wholesale (memoize/quarantine, don't rewrite); make any diagnostic/prescriptive/dosing claim; enable a consent scope by default; ship live medical retrieval that cites from model memory; change CI or merge policy.
