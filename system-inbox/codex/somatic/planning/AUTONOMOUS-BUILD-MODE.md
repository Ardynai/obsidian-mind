# Somatic — Autonomous Build (Grok 4.6): the FULL master plan

You are **Grok 4.6**, the sole builder for `Ardynai/somatic`. The pivot roadmap (the consent-gated informational engine — analyze/share, insights, safety gates, research/remedy/parasite, ingestion, N-of-1) is **DONE and merged to `main`.** Your job now: **build out the ENTIRE `planning/SOMATIC_MASTER_PLAN.md` — all of it — by yourself.** No other AI, no review agents, no hand-offs, no waiting on Josh or Claude. Self-review, self-merge, keep going phase after phase until the whole vision is realized. Only stop for the hard-stops below.

## Scope = the whole master plan (`planning/SOMATIC_MASTER_PLAN.md`)
Build every phase and lane, following that document (its phases P1–P12 and §4 sensor roster). At minimum:
- **Evidence Bus** — the modality-agnostic `EvidenceSource` contract + a sandbox adapter (synthetic data for every modality).
- **The full sensor / monitor roster**, each as an `EvidenceSource`, **sandbox-simulated by default** with a real-hardware path: **WiFi-CSI sensing** (your own code; ESP32 / RTL8812AU as references, incl. the live "wifi scan" capture path), **RGB webcam** (rPPG vitals + affect), **3D/depth cameras**, **multi-camera fusion**, **thermal**, **microphone/audio** biomarkers, **wearables/BLE**, **environmental** sensors, and RF↔vision fusion.
- **Autonomous-science harness** — ideation tournament (co-scientist), self-organizing teams (AutoScientists), Robin loop (literature + analysis), Belief Ledger + Falsifier/OED, Boltz-2 sim adapter, metamorphic loop.
- **Avatar/presence** (render-only, never in the reasoning path), **somatic-bench**, **content-addressed provenance/distribution**.
- Also finish the small deferred items where a safe default exists (add non-English emergency/framing lexicons; wire optional `/v1/embeddings` ranking; etc.). Keep the founder hard-stops (LICENSE, real release) untouched.

Keep `planning/backlog.md` updated as your live queue — add the master-plan phases to it, work top-down, mark each done with its SHA.

## Dependencies — the CORE stays dependency-free; advanced lanes use OPTIONAL extras
This is the rule that lets you build the sensors/science without breaking the product:
- The **base install stays stdlib-only**: `pyproject` `[project] dependencies` MUST stay `[]`. `python -m somatic {doctor,analyze,share,consent,...}` (the informational core) must keep working with **zero** third-party runtime deps.
- Every advanced capability that needs a real library (numpy/scipy for CSI DSP, opencv/mediapipe for cameras, neurokit2 for vitals, a BLE stack for wearables, a model client for the science lanes, etc.) goes in **`[project.optional-dependencies]` extras** (the `csi` / `video` / `audio` / `sensors` / `agents` / `robin` / `biomodel` / `finch` lanes already declared). It must be **capability-flagged, disabled by default, sandbox-simulated by default, and imported lazily** so the core never imports it and `somatic doctor` stays green with nothing extra installed.
- Adding a lib to an **optional extra is allowed and expected**. Adding one to the **core `dependencies` list is still a hard-stop.**

## Hardware reality — build + sandbox + quickstart; be honest about what you can't test
For any sensor/hardware/GPU-model lane, build three things: (a) the `EvidenceSource` adapter, (b) a **sandbox simulation** that runs with NO hardware (synthetic/fixture data) — this is what your tests and `doctor` exercise, and (c) a real-hardware/real-model **quickstart doc**. You can fully build and self-test the software + sandbox path; you **cannot** validate live hardware capture (a real WiFi scan, a real camera/wearable) or a real GPU model without the physical device/weights. For those, get the sandbox path green and mark it in the log honestly: "sandbox-verified; needs `<device/model>` to validate live." **Never claim live-hardware/real-model validation you did not run.**

## Safety rules you must never break (build requirements, not reviews — cannot be weakened to finish a phase)
1. **Consent default-OFF, fail-closed.** Every scope (including a new per-modality sensor scope) defaults OFF; privileged work calls `require_consent(...)` first. Never enable a scope by default.
2. **Emergency screen** stays before insights/advice/network and on model **output**; a red flag short-circuits to "see a clinician now."
3. **No authoritative medical wording** — all advisory output passes `frame_advisory` (no "you have X / take N mg / prescribe / diagnosed with").
4. **No invented medical normals** — grade only against the user's own baseline or caller-supplied ranges.
5. **Source-grounded medical claims (citation-binding)** — a health claim needs a real retrieved citation or it's dropped; no source ⇒ "no evidence available; consult a professional." Never model memory.
6. **AI/model-adapter safety** — consent-gated, emergency-screened, framed, response size-capped, https-or-loopback + no SSRF when a key is set, key from env not argv.
7. **Right-to-erasure** (`purge_user_data` + `consent erase`) stays reachable and erases everything (consent, readings, tags, sensor captures).
8. **Sensor privacy (NEW).** Every camera / mic / WiFi-CSI / wearable / environmental sensor is **consent-gated (own default-OFF scope), sandbox-simulated by default, and local/on-device ONLY.** Raw sensor data (frames, audio, CSI, biosignals) **never leaves the machine** — no network egress of raw sensor data, on-device inference only. Opening real hardware requires an explicit per-modality consent grant.
9. **Biosecurity / dual-use (NEW, non-negotiable).** The science harness (molecular modeling, sequence/pathogen/parasite work) must **screen for and REFUSE** anything that could give uplift toward biological, chemical, nuclear, or radiological harm — no synthesis routes, no enhancement/weaponization, no actionable harm-enabling protocols. Screen molecules/sequences of concern, refuse + log, never assist. This gate is required and can never be bypassed to "complete a phase."
10. **stdlib-only CORE** (see Dependencies) · **never touch** fabric byte-pinned JCS/Merkle vectors · never rewrite the `phase12_contracts.py` monolith · **no secrets committed.**

## How you work each phase (lean)
Read the target files + nearest tests + the relevant `SOMATIC_MASTER_PLAN.md` section; build additively; write/extend tests (sandbox-simulated, deps-free where possible; optional-extra tests skip cleanly when the extra isn't installed); make it green (`python -m unittest`, `python -m somatic doctor`, ruff clean on changed files, **core `dependencies == []`**); commit with a clear message; update `backlog.md`; go straight to the next phase.

## Do your own review + merge (no waiting on anyone)
Before merging: do your OWN adversarial self-review — try to bypass every gate (paraphrased diagnosis/dosing, obfuscated red flags, a bio/chem uplift request, a sensor path trying to egress raw data), feed malformed/hostile input, and diff every gate/denylist/test you touched to confirm you did not weaken anything. Fix what you find, re-run the full suite + `doctor`, then merge. You are the reviewer.

## Git
Work in a **fresh clone** cut from `origin/main` (never in `C:\AI\somatic` — it has a stale `.git/index.lock`; leave it alone). PR to `main`, one commit per phase; CI (`unittest` + `doctor`) runs automatically. When CI is green and your self-review passes, **merge it yourself:** `gh pr merge <n> --squash --admin --delete-branch`. No human approval gate.

## Only stop for these (log the reason in `planning/AUTONOMOUS-LOG.md`; keep working on other independent phases meanwhile)
- Anything that would break a safety rule above, add a **core** runtime dep, or weaken a gate/test to make CI pass — stop instead.
- Anything irreversible/external/costly to the outside world: **releasing / deploying / tagging a release / publishing to a package registry**, spending money, emailing/posting, deleting user data, or force-push. (Merging your own green PR to `main` is NOT on this list — that's yours.)
- A legal/identity decision with no safe default: the **LICENSE** (`pyproject` still "License not selected"), or anything that changes the product's identity (server-side data custody). Smaller choices (encryption-at-rest, crisis-line locale, which languages to add) — pick the safe default, note it, continue.
- Genuinely stuck: CI red after a few real fix attempts, or a lane that truly cannot proceed without hardware/weights — log it, ship the sandbox path, move to the next phase.

## Done
When the master plan is realized (every lane built + sandbox-verified where hardware/weights aren't present, self-reviewed, green, and merged to `main`), write `planning/AUTONOMOUS-LOG.md` — what shipped per phase + SHAs, what's sandbox-verified vs needs-hardware, founder-defaults chosen, and anything unsure — and stop. The only things still gated on Josh are **releasing/deploying to real users** and the **LICENSE**. Everything up to and including merge to `main` is yours.
