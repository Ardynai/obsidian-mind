---
title: SOMATIC — Master Plan (v2)
status: living document
owner: Josh (Ardynai)
authored_with: Claude (Cowork) — executed by ChatGPT (planner) + Codex (builder)
last_updated: 2026-05-31
---

# SOMATIC — Master Plan & Build Bible (v2)

> **Vision:** An open-source *execution engine for autonomous science* — the most advanced practical hybrid of **FutureHouse's Robin** (closed-loop hypothesis → experiment → analysis), **Google's AI co-scientist** (generate / debate / evolve tournament), and **Harvard's AutoScientists** (self-organizing agent teams) — built so **any evidence source** (in-silico simulation, wet-lab, WiFi-CSI, 2D/3D/thermal video, audio, wearables) can substitute for a physical experiment, and so it can **evolve into a private, embodied, multi-sensor personal-health reasoning engine.**

This file is the single source of truth. ChatGPT reads it and issues the per-phase Codex prompts in §11; Claude is on call for architecture, research, verification. **v2 changes are marked 🆕.**

---

## 0. Roles
- **ChatGPT = planner/PM.** Reads this, picks the current phase (§10), pastes the matching Codex prompt (§11), adapts it with Codex's reports.
- **Codex = builder.** Works in `C:\AI\obsidian-mind\.codex`. One phase at a time.
- **Claude (Cowork) = architect/researcher/verifier.** Call for ambiguous design, fact-checks, deeper specs, broken builds. Can read `.claude`, `.codex`, and (once GitHub is authed) the `somatic` repo.
- **Vault (`obsidian-mind`) = memory + provenance.** SOMATIC writes its reasoning trail here for auditability.

---

## 1. Ground truth: the systems we're fusing 🆕 (now four)

| System | What it is | Status | What we take |
|---|---|---|---|
| **Robin** (FutureHouse) | Crow + Falcon + Finch closed loop; found **ripasudil for dAMD** | **Nature 2026** (`s41586-026-10652-y`); core open (PaperQA2, aviary, ldp) | Agent roles + open code as skeleton. **NOTE 🆕:** treat Robin's *own orchestration* as reference/ideas, not a hard dependency — we use its open components (PaperQA2 etc.), not a wholesale fork. |
| **Google "AI co-scientist"** | generate→reflect→rank(Elo)→evolve→meta-review, scaled test-time compute | Blog + arXiv preprint Feb 2025; **closed** | We reimplement the tournament. |
| **🆕 AutoScientists** (Harvard, Zitnik Lab) | **Self-organizing agent teams** for long-running experimentation: agents form teams around promising hypotheses, critique before spending compute, share wins/failures, re-org when stalled. Beats a central planner. Ships as **Claude Code subagents over a local server**; +8.33% over prior best on BioML-Bench | arXiv `2605.28655`; **open** (`mims-harvard/AutoScientists`) | **The orchestration upgrade** — replaces co-scientist's *central* planner with decentralized self-organizing teams. This is now our top-layer coordination model. |
| **Coscientist** (CMU) | GPT-4 driving physical lab hardware | Nature 2023 | Lab-instrument control pattern (only when real hardware is wired). |

**The hybrid (v2):** **AutoScientists-style self-organizing teams** run a **co-scientist-style idea tournament**, feed a **Robin-style evidence loop**, all over the **Evidence Bus**, wrapped in a **metamorphic outer loop**. Skills come from a shared library (§1a).

### 1a. 🆕 Shared skill + database layer — `scientific-agent-skills` (K-Dense-AI)
`K-Dense-AI/scientific-agent-skills` (MIT) is **140 ready-to-use science skills + 100+ scientific database connectors** (biology, chemistry, medicine, drug discovery), **compatible with Codex, Claude Code, Cursor, and the open Agent Skills standard** — i.e. it drops straight into your stack. **Decision: adopt it as SOMATIC's skill/DB substrate.** Crow/Falcon/Finch and the team agents call these skills instead of us re-coding 140 wrappers. This single choice removes months of glue work.

---

## 2. The core
```
        ┌────────────────────────── SOMATIC CORE ──────────────────────────┐
        │  SELF-ORGANIZING TEAMS (AutoScientists)                           │
        │     │  spawn teams around hypotheses, critique, share state       │
        │     ▼                                                             │
        │  IDEATION TOURNAMENT (co-scientist)   EVIDENCE LOOP (Robin)        │
        │   Generation→Reflection→Falsifier*→   Falcon: plan measurement    │
        │   Ranking(Elo) ─► ranked hypotheses ─► EVIDENCE BUS* ──┐          │
        │        ▲                                  (any modality)│          │
        │        │                                                ▼          │
        │   Evolution ◄─ Belief Ledger* ◄────── Finch: analyze (code interp) │
        │    (DSPy/GEPA)   [Bayesian]            using scientific-agent-skills│
        └───────────────────────────┬───────────────────────────────────────┘
                                    │ metamorphic outer loop (git-versioned)
                                    ▼   success template | failure template
```
\* = net-new (§7). **Hard rule:** the core must run **end-to-end in sandbox on a laptop with one API key** before any advanced lane is switched on (§9).

---

## 3. Keystone: the Evidence Bus
"Run an experiment" → "request evidence." One contract; many modalities.
```python
class EvidenceSource(Protocol):
    modality: Literal["sim","wetlab","csi","video","video3d","thermal","audio","wearable","literature"]  # 🆕 expanded
    def plan(self, hypothesis: Hypothesis) -> MeasurementPlan: ...
    def acquire(self, plan: MeasurementPlan) -> RawEvidence: ...
    def cost(self, plan: MeasurementPlan) -> Cost: ...
    def confidence(self, raw: RawEvidence) -> float: ...
# Finch consumes RawEvidence (any modality) → StructuredVerdict → Belief Ledger
```
Tiers so nobody is blocked: **Tier 0 sandbox** (synthetic noisy data for every modality, default) · **Tier 1 local** (Boltz-2 GPU, webcam, depth cam, ESP32 CSI, wearable CSV) · **Tier 2 cloud/lab** (cloud GPU, cloud lab, clinical feeds).

---

## 4. 🆕 The full sensor / monitor roster (the "use every monitor" requirement)

All implement `EvidenceSource`. All optional, capability-flagged, sandbox-simulated by default. The goal: **give the AI the richest possible multi-sensor view of a person or environment.**

| Sensor | Signal it yields | Library / hardware | Modality | Notes |
|---|---|---|---|---|
| **RGB webcam** | rPPG heart rate, HRV, resp; facial affect/AUs; pallor/jaundice/eye cues | rPPG-Toolbox, pyVHR, py-feat, MediaPipe | `video` | Baseline, zero extra hardware |
| **🆕 3D / depth camera (RGB-D)** | True 3D pose & gait, fall detection, distance-normalized rPPG ROI, breathing volume, posture | Intel RealSense D4xx, Stereolabs ZED 2, Luxonis OAK-D (on-device AI), Orbbec, ToF | `video3d` | **"3D layered camera"** Josh asked for — depth makes every video metric more accurate and enables true volumetric breathing/gait |
| **🆕 Multi-camera fusion** | Best-angle video, stereo depth from 2+ RGB cams, occlusion robustness | OpenCV multi-view, OAK-D arrays | `video3d` | "Best video for the AI" = fuse views; depth + multiview beats single 2D frame |
| **🆕 Thermal camera** | Skin/febrile temperature, perfusion, breathing plume | FLIR Lepton, Seek | `thermal` | Fever/inflammation signal; privacy-friendly |
| **WiFi CSI** | Resp rate, heart rate, sleep stage, posture, **3D human pose**, fall — no camera | own code (see §4a) | `csi` | Through-wall, privacy-preserving, works in the dark |
| **🆕 Microphone / audio** | Cough/breath sounds, speech prosody, vocal biomarkers, sleep apnea | librosa, openSMILE; MiniCPM-o for speech | `audio` | Respiratory + affective biomarkers; also the avatar's ear |
| **Wearables / BLE** | HR, SpO₂, HRV, temp, CGM glucose, steps, sleep | BLE GATT, Apple Health / Google Fit export, Polar SDK | `wearable` | CSV import in sandbox; live BLE in Tier 1 |
| **Environmental** | Air quality, pollen, CO₂, humidity, light | BLE/serial sensors | `wearable` | Context for the n-of-1 reasoning (e.g. asthma + pollen) |

**🆕 Vision LLM for "reading" the person:** default **MiniCPM-V 4.5** (on-device, GPT-4V-level image+video, runs local — no frames leave the machine) for expression/visual-ailment interpretation, with **MiniCPM-o 2.6** (omnimodal: real-time **speech + live video** in, **speech** out) powering the doctor avatar's perception *and* conversation. Clinical cross-checks via **LLaVA-Med / BioMedCLIP**. All pluggable behind one `VisionReasoner` interface so any LLM (incl. cloud Med-Gemini) can slot in.

### 4a. 🆕 WiFi-CSI = our own code, these as references (per Josh)
Do **not** take a hard dependency on existing CSI repos. Study them, then write a clean SOMATIC `sensors/csi` package:
- **`NTUMARS/Awesome-WiFi-CSI-Sensing`** — curated survey/taxonomy of methods, datasets, models. Use as the **literature/method map** (what features, what models, what's SOTA).
- **`thu4n/ESP32-WiFi-Sensing`** — practical ESP32 CSI capture. Reference for the **cheap-hardware ingestion path** (firmware → CSI stream).
- **`MaliosDark/wifi-3d-fusion`** — real-time **3D human pose from CSI + deep learning + CV fusion** (RTL8812AU USB or ESP32). Reference for the **3D-pose-from-WiFi** capability and the RF↔CV fusion idea — pairs beautifully with the 3D camera (fuse WiFi pose + depth pose).
Our implementation: clean DSP (bandpass/wavelet) + NeuroKit2 for vitals, a small pose model for 3D pose, all behind `EvidenceSource(modality="csi")`. Sandbox synthesizes CSI; ESP32 + RTL8812AU quickstart for real capture.

> **🚫 REJECTED — do NOT use `ruvnet/RuView`.** It targets exactly this WiFi-CSI / vital-signs space and has high star counts, but the community (Hacker News, Mar 2026) flagged it as **non-functional, AI-generated "slop" running on mock data** with no demonstrated working pipeline. Codex/ChatGPT must not add it as a dependency or copy its code. It's fine to skim for ideas only; trust the three reference repos above instead, and verify any CSI claim against the `Awesome-WiFi-CSI-Sensing` survey + real datasets.

---

## 5. Workflow templates (same engine, different loop shapes)
- **`discovery`** (Robin-shaped): hypothesis "molecule/target X does Y" → Boltz-2 + assay/sandbox evidence → stats. Reproduces ripasudil/dAMD.
- **`n-of-1`** (the sensing/health loop, first-class): the *person* is the hypothesis; the **continuous multi-sensor stream is the assay**; success = vitals return to baseline after a tagged intervention. A real single-subject clinical method.
- **`multimodal-sensing`** (general): any monitor → observe→hypothesize→verify→mutate. Health is the flagship; the loop is general (also fits home/elder monitoring, environment mapping).

n-of-1 loop with the full roster:
```
[CSI + 3D/RGB/thermal video + audio + wearables]
   → Finch extracts vitals/affect/gait/3D-pose (NeuroKit2 + MiniCPM-V + pose models)
   → TrendReader (Chronos default; Kronos optional) flags anomaly vs personal baseline
   → Self-organizing team + medical VLM hypothesize vs history + medical PDF lake (bio APIs §12)
   → Safety gate (§8) → Avatar delivers (§6.5) → tag timestamp
   → re-measure later: baseline restored? success-reinforce : escalate-to-human
```

---

## 6. Layers around the core
- **6.1 Memory/provenance:** `brain/` (git-versioned) + Hindsight/mem0 hot recall.
- **6.2 Knowledge ("PDF lake"):** pre-indexed open biomed corpora + 🆕 live bio APIs (§12).
- **6.3 Simulation:** Boltz-2 (structure **and** affinity; supersedes Boltz-1), Chai-1, ESM3, DiffDock.
- **6.4 Safety/biosecurity:** load-bearing (§8).
- **6.5 🆕 Embodiment / Presence (avatar):** render-only persona over the gated verdict — never in the reasoning path.
  ```
  StructuredVerdict → Persona LLM (Scientist | Doctor, safety-gated)
    → speech: MiniCPM-o 2.6 (real-time S2S) or TTS (Piper/XTTS/Bark)
    → talking head: Duix-Avatar | GaussianTalker | Audio2Face-3D ; optional VTubeStudio rig
    ← the avatar's camera+mic ALSO register as video/audio EvidenceSources
  ```
  Two personas: **"The Scientist"** (discovery) and **"The Doctor"** (n-of-1; always ends clinical items with the §8 disclaimer). v1 = text+TTS; 3D head + omnimodal speech = Tier-1 plugins.

---

## 7. Net-new, groundbreaking pieces (what makes it *yours*)
1. **Evidence Bus** (§3) — modality-agnostic evidence; neither reference system has it. Headline novelty.
2. **Falsifier agent + Optimal Experiment Design** — designs the cheapest measurement that would *kill* the leading hypothesis, chosen by **expected information gain** (BoTorch/Ax). Spends evidence budget where it most cuts uncertainty.
3. **Belief Ledger** — a **Bayesian posterior over hypotheses** (NumPyro); every verdict from *any* modality (depth cam, WiFi, Boltz, wearable) updates the *same* posterior with modality-appropriate likelihoods. Makes multi-sensor fusion rigorous. → repo `somatic-belief`.
4. **Content-addressed provenance + distribution** — artifact hash = its provenance; optional BitTorrent for verifiable dataset/checkpoint sharing.
5. **`somatic-bench`** — open benchmark/leaderboard for autonomous discovery (canonical task: reproduce ripasudil/dAMD in sandbox). Highest-traction artifact you can ship.
6. **Kronos & TS foundation models** — pluggable `TrendReader`; **Chronos-Bolt/TimesFM/MOMENT default** (built for general/clinical time-series), **Kronos droppable in** as one adapter (honest caveat: it's trained on financial candlesticks, so it's optional, not the medical default).
7. **🆕 RF↔Vision fusion** — fuse WiFi-CSI 3D pose with depth-camera 3D pose into one body-state estimate (more robust than either; works through occlusion *and* in the dark). Inspired by `wifi-3d-fusion`, implemented as a fusion node in the Belief Ledger.

---

## 8. Safety, biosecurity, medical disclaimers — required, first-class
- **Bio-safety gate:** screen molecules-of-concern before they leave ideation; refuse + log (design the gate; never build uplift).
- **Medical-advice gate:** never diagnose/prescribe; wellness/observation framing; mandatory "not medical advice — consult a clinician"; **red-flag → "see a human clinician now"**; human-in-the-loop for anything clinical.
- **Privacy:** CSI/video/audio/health data local by default; sharing opt-in + anonymized; never in URLs/third-party calls without consent. The 3D camera and mic are powerful — default to on-device inference (MiniCPM-V/o local), no raw frames leave the machine.
- Test the gates with `promptfoo` + `garak`; Decepticon-pattern adversaries (Toxicologist, Synthesizer) for the molecule gate.

---

## 9. Why I (Claude) resequenced rather than removed (reconciliation)
The risk was never *having* features — it's *coupling* them. Behind the Evidence Bus + capability flags, every advanced lane (CSI, 3D/thermal video, audio, avatar, quantum, BitTorrent) is a **plugin with a stable contract, defaulting off**. So we **wire everything from the start** without forcing anyone to run all of it. Self-rewriting prompts are **kept but made reproducible** (DSPy/GEPA + git-versioned mutation log). The safety gate is **required**, not optional. Kronos is **included as an adapter** with a caveat. v1 stays **Python** (your whole scientific + sensor stack is Python; add Rust sidecars only for hot paths like CSI ingestion later). Net: **nothing meaningful is cut** — it's decoupled so it survives contact with reality.

---

## 10. Roadmap (every phase ends in a runnable sandbox demo)
| Phase | Deliverable | Done = |
|---|---|---|
| **P0** | `somatic` monorepo scaffold (Python, uv, ruff, pytest, docker-compose, CI) | `docker compose up`; `somatic --help` |
| **P1** | Core state machine + **Evidence Bus** + **sandbox adapter** | `somatic launch --config examples/sandbox.yaml` runs fake loop |
| **P2** | Ideation tournament (generate/reflect/rank Elo, LangGraph) | ranks N synthetic hypotheses, logs to vault |
| **P2.5** 🆕 | **AutoScientists self-organizing team layer** over the tournament | teams spawn/critique/merge around hypotheses; shared state |
| **P3** | Robin loop: PaperQA2 (Crow/Falcon) + Finch code-interpreter; mount **scientific-agent-skills** | real lit review + data analysis over sandbox evidence |
| **P4** | **Belief Ledger** (NumPyro) + **Falsifier/OED** | posterior updates; Falsifier picks next test; uncertainty drops |
| **P5** | Simulation tier: **Boltz-2** adapter | `discovery` runs a real affinity prediction |
| **P6** | Metamorphic loop via **DSPy/GEPA**, git-versioned mutations; `somatic replay` | mutation is reproducible |
| **P7** | **WiFi-CSI (own code)** + NeuroKit2 + TrendReader (Chronos default/Kronos opt) + `n-of-1` template | live RR/HR loop vs baseline (sandbox + real ESP32) |
| **P8** | **Video EvidenceSource**: rPPG + py-feat/MediaPipe + **MiniCPM-V** reader | webcam → vitals + affect into the bus |
| **P8.5** 🆕 | **3D/depth + thermal + audio + multi-cam fusion**; **RF↔vision 3D-pose fusion** | depth/thermal/audio sources + fused body-state into Belief Ledger |
| **P9** | **Safety + biosecurity gates** (promptfoo/garak, Decepticon-pattern) | blocks unsafe molecule + unsafe advice in tests |
| **P10** | **Avatar/presence**: persona LLM + speech (**MiniCPM-o**/TTS) + talking head | Doctor & Scientist avatars deliver gated output |
| **P11** | **`somatic-bench`** + ripasudil/dAMD reproduction + leaderboard | another harness can be scored |
| **P12** | Content-addressed provenance + optional BitTorrent sharing | any result re-verifiable from its hash |

P7–P12 are independent plugins — any order after P6, parallelizable across Codex sessions.

---

## 11. Codex prompt library (ChatGPT pastes one per phase; require tests + `--sandbox` + a `PHASE_REPORT.md`)

**P0 — scaffold**
```
Create a Python monorepo `somatic` (uv, ruff, pytest, mypy, docker-compose, GitHub Actions CI).
Packages: core, evidence_bus, agents, engines, sensors, safety, memory, presence, cli, bench.
CLI (Typer): `launch --config <yaml>`, `doctor` (env check), `replay <commit>`.
Add examples/sandbox.yaml. Skeleton only + passing smoke test + README of package boundaries. PHASE_REPORT.md.
```
**P1 — Evidence Bus + sandbox**
```
Implement EvidenceSource Protocol (modalities: sim,wetlab,csi,video,video3d,thermal,audio,wearable,literature) and pydantic schemas MeasurementPlan/RawEvidence/StructuredVerdict.
SandboxSource: noisy synthetic data for EVERY modality (configurable variance, negative-rate, seed).
Core state machine: hypothesis→plan→acquire→verdict, logging each step as a markdown note in vault `brain/` style. Tests + sandbox demo. PHASE_REPORT.md.
```
**P2 — tournament**
```
LangGraph agents: Generation, Reflection, Ranking (Elo via pairwise debate). Input research goal → ranked hypotheses + rationales. Batch scorer as interface (LocalBatchScorer now; CloudBatchScorer stub). Tests over synthetic goals. PHASE_REPORT.md.
```
**P2.5 — self-organizing teams (AutoScientists)** 🆕
```
Study mims-harvard/AutoScientists (self-organizing teams: form around hypotheses, critique before spending compute, share wins/failures in common state, reorganize when stalled). Implement a TeamOrchestrator over the P2 tournament: spawn N teams per top hypothesis, peer-critique gate before evidence spend, shared blackboard state, re-org on stall. Keep it modality-agnostic via the Evidence Bus. Tests show teams avoiding redundant evidence requests. PHASE_REPORT.md.
```
**P3 — Robin loop + skills**
```
Integrate PaperQA2 as Crow (concise QA) and Falcon (deep review). Finch = sandboxed code-interpreter (pandas/scipy/scanpy) consuming RawEvidence → StructuredVerdict with real stats. Mount K-Dense-AI/scientific-agent-skills as the shared skill/DB library for all science agents. Falcon fills MeasurementPlan. Tests vs sandbox source. PHASE_REPORT.md.
```
**P4 — belief ledger + falsifier**
```
Package somatic-belief: Bayesian posterior over hypotheses (NumPyro), updated by StructuredVerdicts with per-modality likelihoods. Falsifier agent proposes next measurement by expected information gain (BoTorch/Ax) under EvidenceSource.cost. Orchestrator consumes Falsifier output. Tests: uncertainty decreases across loops. PHASE_REPORT.md.
```
**P5 — Boltz-2**
```
engines/boltz2 adapter EvidenceSource(modality="sim"): SMILES/FASTA → Boltz-2 (local GPU; CPU/mock fallback for CI) → structure + binding affinity verdict. examples/dAMD.yaml. PHASE_REPORT.md.
```
**P6 — metamorphic loop**
```
Success/failure templates that mutate generation prompts + thresholds via DSPy + GEPA (optimized against a metric). Commit every mutation as a git diff in the vault linked to triggering evidence. `somatic replay <commit>` restores a past prompt/param state. Test: a mutation is reproducible. PHASE_REPORT.md.
```
**P7 — WiFi-CSI (own code) + n-of-1**
```
Write sensors/csi from scratch (do NOT depend on external CSI repos; reference NTUMARS/Awesome-WiFi-CSI-Sensing, thu4n/ESP32-WiFi-Sensing, MaliosDark/wifi-3d-fusion only as method references). Ingest CSI from ESP32 (esp-csi) or RTL8812AU/router; extract RR, HR, HRV, sleep stage, posture/fall (NeuroKit2 + bandpass/wavelet); small model for 3D pose. EvidenceSource(modality="csi"). TrendReader interface: Chronos-Bolt default, Kronos optional adapter. Implement `n-of-1` template (continuous stream = assay; success = return-to-baseline after tagged intervention). Sandbox synthesizes CSI; ESP32 quickstart doc. PHASE_REPORT.md.
```
**P8 — video EvidenceSource**
```
sensors/video: rPPG HR-from-webcam (rPPG-Toolbox/pyVHR), facial affect/AUs (py-feat), pose/gait (MediaPipe/MoveNet), and a VisionReasoner interface with a MiniCPM-V 4.5 local adapter (expression + visual-ailment reading) — frames never leave the device. Feed signals to the Belief Ledger. PHASE_REPORT.md.
```
**P8.5 — 3D/depth + thermal + audio + fusion** 🆕
```
sensors/video3d: RGB-D adapter (RealSense/ZED/OAK-D/Orbbec; sandbox synth depth) for 3D pose, gait, depth-normalized rPPG ROI, breathing volume. sensors/thermal (FLIR Lepton). sensors/audio (cough/breath/voice biomarkers via librosa/openSMILE). Multi-camera fusion util. RF↔vision fusion node: combine CSI 3D pose + depth 3D pose into one body-state estimate in the Belief Ledger. All sandbox-simulated; real-hardware quickstarts. PHASE_REPORT.md.
```
**P9 — safety gates**
```
safety/: (1) bio-safety molecule-of-concern screen (refuse+log, no uplift); (2) medical-advice gate (no diagnosis/prescription; mandatory disclaimer; red-flag escalation). Harness with promptfoo + garak; Decepticon-pattern adversaries (Toxicologist, Synthesizer). Verdicts pass gates before the presence layer. PHASE_REPORT.md.
```
**P10 — avatar/presence**
```
presence/: persona LLM rephrasing a gated StructuredVerdict in "Scientist"/"Doctor" voice; speech via MiniCPM-o 2.6 (real-time S2S) or TTS (Piper/XTTS/Bark); talking-head adapter interface with a Duix-Avatar impl (GaussianTalker/Audio2Face-3D alternates); optional VTubeStudio rig. Text+TTS default; 3D head Tier-1. Avatar camera/mic register as video/audio EvidenceSources. Persona layer is render-only — never alters the verdict. PHASE_REPORT.md.
```
**P11 — somatic-bench**
```
Package bench: task-spec format; runner scoring any harness on closed-loop tasks (final-answer correctness, evidence efficiency, reproducibility); canonical task reproducing Robin's ripasudil/dAMD in sandbox. Leaderboard JSON + static site. PHASE_REPORT.md.
```
**P12 — provenance/distribution**
```
Content-addressed storage for every evidence artifact (hash=id). Optional BitTorrent distribution adapter (magnet index + signed manifest verification). `somatic verify <result>` re-checks from hash. PHASE_REPORT.md.
```

---

## 12. Integration matrix (the one piece to use + how it plugs in)
| Capability | Repo / model | Use *one* piece as… | Tier |
|---|---|---|---|
| 🆕 Self-organizing teams | **mims-harvard/AutoScientists** | TeamOrchestrator over the tournament (P2.5) | 1 |
| 🆕 Science skills + 100+ DBs | **K-Dense-AI/scientific-agent-skills** | Shared skill/DB substrate for all agents | 0 |
| Lit review (Crow/Falcon) | **PaperQA2** | literature EvidenceSource + Falcon planner | 1 |
| Agent env | **aviary**, **ldp** | Finch's tool-use env | 1 |
| Tournament graphs | **LangGraph** | sub-swarm state machines only | 0 |
| Prompt evolution | **DSPy**, **GEPA** (`hermes-agent`) | reproducible metamorphic mutations | 1 |
| Structure + affinity | **Boltz-2** | `sim` EvidenceSource (replaces Boltz-1) | 1 |
| Alt structure/docking | **Chai-1**, **ESM3**, **DiffDock** | extra `sim` adapters | 1/2 |
| Bio-signal processing | **NeuroKit2** | Finch's vitals toolbelt (any source) | 1 |
| 🆕 WiFi CSI (reference only) | **Awesome-WiFi-CSI-Sensing**, **ESP32-WiFi-Sensing**, **wifi-3d-fusion** | method references for our own `sensors/csi` | 1 |
| HR from video | **rPPG-Toolbox**, **pyVHR** | `video` vitals | 1 |
| Face affect/ailments | **py-feat**, MediaPipe | `video` affect/pose/gait | 1 |
| 🆕 Vision LLM (local) | **MiniCPM-V 4.5** | `VisionReasoner` (expression/visual-ailment) | 1 |
| 🆕 Omnimodal speech+vision | **MiniCPM-o 2.6** | doctor avatar perception + real-time speech | 1 |
| Clinical multimodal | **LLaVA-Med**, **BioMedCLIP**, Med-Gemini (API) | clinical cross-check node | 1/2 |
| 🆕 3D/depth camera | RealSense / ZED / OAK-D / Orbbec | `video3d` EvidenceSource | 1 |
| 🆕 Thermal / audio | FLIR Lepton; librosa/openSMILE | `thermal`/`audio` EvidenceSources | 1 |
| Time-series foundation | **Chronos-Bolt/TimesFM/MOMENT** (default), **Kronos** (optional) | `TrendReader` adapter | 1 |
| Bayesian belief/OED | **NumPyro/Pyro**, **BoTorch/Ax** | `somatic-belief` + Falsifier | 1 |
| 🆕 Live science data | **PubMed, ChEMBL, ClinicalTrials.gov, bioRxiv, Open Targets, Consensus** | live literature/drug/target EvidenceSources + PDF-lake seed | 1 |
| Safety eval/red-team | **promptfoo**, **garak**, **Decepticon** (pattern) | gate harness + adversaries | 1 |
| Memory daemon | **Hindsight/mem0/zep** | hot recall over the vault | 1 |
| Knowledge vault | **obsidian-mind** (this repo) | git-versioned reasoning trail | 0 |
| Avatar / TTS | **Duix-Avatar/GaussianTalker/Audio2Face-3D/VTubeStudio**; Bark/Piper/XTTS; vosk | render-only presence + voice | 1 |
| Self-improvement ideas | **ASI-Evolve**, **Evolver** | folded into DSPy/GEPA (don't run whole frameworks) | ref |
| Dataset distribution | BitTorrent (librqbit) | content-addressed store (P12) | 2 |

**Rule:** wrap the one useful function/agent/idea behind a SOMATIC interface; never adopt a whole framework's runtime. (Exceptions where we adopt wholesale: `scientific-agent-skills` as the skill substrate, and AutoScientists' team pattern reimplemented in our core.)

### 12a. 🆕 Bio-research data — do you need to authenticate them?
**For building the repo: no.** PubMed (E-utilities), ChEMBL, ClinicalTrials.gov, bioRxiv, and Open Targets are **open public APIs** — SOMATIC's code calls them directly, no login. Authenticating the Cowork bio plugins only matters if you want **me** to query them live *in this chat* while we design, or to use the paywalled ones (**Consensus, Wiley, Synapse, BioRender**) which need accounts. So: auth them if you want me doing live literature pulls now; otherwise the code is built against the open APIs regardless.

---

## 13. New repos to create
- **`somatic`** — the engine/monorepo.
- **`somatic-belief`** — Bayesian hypothesis ledger + optimal experiment design (publishable alone).
- **`somatic-bench`** — open benchmark + leaderboard (traction magnet).
- **`somatic-sensors`** — (optional split) CSI / 2D+3D+thermal video / audio / wearable adapters if they outgrow the monorepo.

---

## 14. Open questions for Josh
1. **Flagship demo:** `discovery` (ripasudil reproduction) or `n-of-1` (multi-sensor health monitor) — which to polish first?
2. **RuView (resolved):** `ruvnet/RuView` is **rejected** — community-flagged as non-functional AI-generated mock-data (§4a). WiFi-CSI is our own code. No action needed.
3. **License:** MIT (matches obsidian-mind / scientific-agent-skills) or AGPL?
4. **Avatar default:** stylized (VTubeStudio) or photoreal (Duix/Audio2Face)?
5. **3D camera target:** which RGB-D first — OAK-D (on-device AI, cheapest path) vs RealSense (best ecosystem) vs ZED (best outdoor depth)?

---

## 15. GitHub & bio-plugin auth (how to connect)
- **GitHub:** plugin is installed; auto-OAuth isn't supported by GitHub's server. In Cowork type **`/mcp`**, pick **github** (engineering plugin), choose **Authenticate**, and either complete the browser OAuth **or paste a Personal Access Token** when prompted (a fine-scoped, short-lived PAT for these repos is enough). Then tell Claude "github's connected."
- **Bio plugins:** same `/mcp` flow per connector — but only needed for live in-chat queries or the paywalled ones; the open APIs need no auth in code (§12a).

*End v2. ChatGPT: start at P0. Claude on call for P2.5 (team design), P4 (belief/OED math), P8.5 (fusion), P9 (safety).*
