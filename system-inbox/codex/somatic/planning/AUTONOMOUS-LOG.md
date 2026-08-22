# Somatic — Autonomous build log

Builder: Grok 4.6 (sole operator). Charter: `planning/AUTONOMOUS-BUILD-MODE.md`.
Branch: `autonomous/master-plan-runtime` from `origin/main` in sibling clone `C:\AI\somatic-autonomous` (did not build in `C:\AI\somatic`; left its `.git/index.lock` and git processes alone).
Pivot PR: https://github.com/Ardynai/somatic/pull/82 — **merged** to `main` (`6414413`). This follow-up is the master-plan sandbox runtime on top of that.

Host verification after the master-plan sandbox runtime: `python -m unittest` **873 tests OK**; `python -m somatic doctor` OK; `pyproject` `dependencies == []`. (846 after the Fable-5 review-fix round; 831 before that.)

## Defaults chosen (safe defaults; continue)

| Choice | Default | Why |
|---|---|---|
| Encryption-at-rest | Plaintext JSON + `chmod 0600` | Stdlib has no AES. |
| Crisis line | US **988** | Documented; other locales use local emergency services. |
| Language scope | **English-only** lexicons | Known limit, not a silent pass. |
| Research v1 | **Offline fixture corpus** | `autonomous-research` still says offline/mock only; live PubMed would need a scope revision (founder). |
| LICENSE | **Not selected** | Hard-stop. `pyproject` still "License not selected". |
| Remedy grades | Default **NONE**; cap **LIMITED** | Honest folk-remedy surface. |
| N-of-1 movement epsilon | 0.25 SD | Directional label only; not a clinical cutoff. |
| FHIR sidecar | FHIR-*shaped* Bundle wrapping `to_dict()` | Not a claim of FHIR R4 conformance. |
| Sensors | **Sandbox-simulated; hardware closed** | `--live` refused. No ESP32/webcam/BLE/CSI IQ/PCM/frames. |
| Belief ledger | **Stdlib Beta**, not NumPyro | NumPyro would be a runtime dep. |
| Biosecurity | Public **name refuse-list** only | No synthesis, uplift, or acquisition paths. |
| Avatar | **Text render-only** | TTS / talking-head / camera / mic extras unimported. |
| Bench pass rule | Fixture goal may echo `ripasudil` | Sandbox scoring, not a real Robin reproduction. |
| Provenance distribution | **P2P/BitTorrent disabled** | Hash verify only; CLI avoids the `bittorrent` token (fabric scan). |

## What landed (one commit per batch)

| Item | SHA | Summary |
|---|---|---|
| **1b** runtime builder cache | `eedae87` | Status-summary snapshot extended to 33 entries (incl. doctor required-arg summaries × 2 domains); memoize hashable-arg builders via `somatic/safety/_builder_cache.py`. Snapshot matched after cache; fixture not edited post-cache. Monolith not rewritten. `doctor` ~2s (was ~110s). |
| **2** consent persistence + CLI | `88d3178` | `~/.somatic/consent.json` / `SOMATIC_CONSENT_PATH`; `somatic consent grant\|revoke\|status\|erase`. `from_dict` any invalid load → all-OFF. `analyze`/`share` load the store; `--grant` is session overlay. |
| **3** safety-gate hardening | `4872507` | Paraphrase-robust `frame_advisory`; stop over-match on benign text; NFKC/zero-width/spaced-letter normalize; broader `emergency_screen` without "stroke rate" false hits; SI → 988; re-screen model output; adversarial corpus as CI. |
| Adapter/share (F10/F11/F13/F17/F19) | `c271657` | Share consent before AI POST; `--model-key` refused (env only); https-or-loopback with key; no metadata IPs; no auth-following redirects; `/v1/v1` dedupe; Markdown field escape. |
| F12/F9/F15/hygiene | `99d4efa` | Fail-loud analyze notes; doctor spine-status (defaults OFF, not live home ledger); README/ARCHITECTURE truth-up; gitignore `.claude/` `.specify/`; safety package status `live-spine`. |
| **F14** clinician-doc polish | `2887735` | Generation timestamp; z-branch includes the flagged reading; small-n z annotated; one disclaimer + routing; sample-size labels (not GRADE); provenance appendix; `--fhir-out`. |
| **4** data ingestion | `05720dc` | `somatic ingest csv\|apple-health\|status\|erase` behind `data-ingestion` (default OFF). Timestamped `somatic.packet.v1`. Readings store erased with consent erase. |
| **5** n-of-1 designer | `b2fd97a` | `somatic experiment evaluate\|tag\|status\|erase`. Own-series split at tag; reuses insights z-math; no retrieval, no population normals. |
| **6** research loop | `71ae216` | Stdlib BM25 + citation-binding. Unbound claims dropped. No source ⇒ `No evidence available; consult a professional` (tested). No model memory. No live PubMed. |
| **7** remedy library | `eaf6ffa` | `somatic remedy lookup`. Same substrate; default NONE; cap LIMITED; safety notes always. |
| **8** parasite Q&A | `d56b5c9` | `somatic parasite ask`. Emergency-screened; fixture does not identify species; honest null when unbound. |
| This log | `c631ebd` | `planning/AUTONOMOUS-LOG.md`. |

Head: `9a34158` at the original stop; review-fix commits below.

## Fable-5 review fixes (this round; PR still open)

| Item | SHA | Summary |
|---|---|---|
| **B1** emergency flags | `77b45e2` | Bare `stroke` / `heart attack` fire again; benign `stroke rate`, `heart attack risk/score`, `rowing stroke` still pass. Both-direction corpus cases. |
| **B2** store erase | `c0e9fe0` | Non-UTF-8/invalid consent, ingest, and experiment files load fail-closed. `consent erase` unlinks before load so a corrupt file cannot crash erasure. |
| Adapter SSRF | `d5ae810` | With a model key, `ipaddress` rejects private/link-local/ULA and metadata-IP encodings (decimal/hex/IPv6-mapped/6to4). Redirects raise and do not follow `Authorization`. |
| CLI degrade | `836f1a7` | `analyze`/`share` malformed `--data`/`--references` and a non-zip `.zip` ingest print a note (exit 2), not a traceback. |
| Ingest NaN/units | `661273f` | NaN/inf rejected at ingest; mixed nonempty units within one metric are noted, not converted. |

Left for Josh (unchanged): LICENSE, plaintext encryption-at-rest, live PubMed/scope revision, English-only lexicons, FHIR-shaped sidecar.

## Master-plan sandbox runtime (follow-up on `main`)

North-star phases from `planning/SOMATIC_MASTER_PLAN.md` are wired as **stdlib sandbox plugins**. Advanced lanes stay optional extras and are never imported by these paths. Live hardware, live literature HTTP, Boltz-2, NumPyro, MiniCPM/Duix, and scientific-agent-skills execution were **not** turned on.

| Area | SHA | What landed | Defaults / rails |
|---|---|---|---|
| **Evidence Bus** | `cf09110` | `EvidenceAdapter` Protocol + `SandboxModalityAdapter` for every modality; `bus run`. `EvidenceSource` remains a record dataclass (not turned into a Protocol). | `ANALYSIS_INSIGHT`; emergency short-circuit; `frame_advisory`; dollars 0; hardware_required false. |
| **Sensor roster** | `cf09110` | CSI, RGB video, 3D/depth, thermal, audio, wearable, environmental. `sensor-roster list\|scan\|fuse`. Live-scan = synthetic ticks. | Needs `data-ingestion` + `analysis-insight`. `--live` raises `SensorHardwareDisabled`. `LIVE_SENSOR_INTEGRATION_IMPLEMENTED` stays **False**. Features only (no frames/PCM/CSI IQ/BLE ids). |
| **RF↔vision fusion** | `cf09110` | Averages simulated CSI + video3d pose joints. | Same two consents; labeled simulated. |
| **Science harness** | `cf09110` | Tournament + existing team orchestrator + bus + Beta belief + entropy/cost falsifier. `science run`. | `autonomous-research` **and** `analysis-insight` before spend. Emergency + biosecurity name-gate first. |
| **Avatar** | `cf09110` | Scientist/Doctor render-only restatement. `avatar speak`. | `ai-advisory`; emergency screen; verdict text preserved; TTS/head/camera/mic off. Presence `STATUS` stays `scaffolded`. |
| **Bench** | `cf09110` | `bench-run` scores `fixtures/bench/ripasudil-damd.json`. | Leaderboard `dollars_spent: 0`, `hardware_used: False`. Not a claim of real ripasudil/dAMD reproduction. |
| **Provenance** | `cf09110` | `evidence-verify` content-addressed SHA-256. | P2P distribution disabled. |
| Docs / extras | `cf09110` | `docs/how-it-works/master-plan-runtime.md`; doctor master-plan lines; optional extras `video3d`/`thermal`/`presence`. | `dependencies == []` unchanged. |
| This log | `6c26c4b` | `planning/AUTONOMOUS-LOG.md` updated for the master-plan round. | — |

CLI: additive subcommands only; **0 deletions** in existing `somatic/cli/main.py` dispatch. Doctor prints sandbox/hardware-closed status without forbidden sensor tokens.

## Hard-stops honored (did not do)

- Did **not** pick a LICENSE.
- Did **not** add a runtime dependency.
- Did **not** touch fabric JCS/Merkle vectors or rewrite `phase12_contracts.py` (memoize only).
- Did **not** enable any consent scope by default.
- Did **not** merge a duplicate of already-landed #82 history; this follow-up is cherry-picked onto `origin/main`.
- Did **not** delete remote `codex/phase-*` branches.
- Did **not** add a repo-wide ruff CI gate (legacy tree still has hundreds of ruff hits).
- Did **not** enable live literature HTTP (scope text is still offline/mock).
- Did **not** open cameras, microphones, BLE, WiFi CSI capture, or any live sensor.
- Did **not** import OpenCV, NeuroKit2, librosa, NumPyro, MiniCPM, or Duix in core.
- Did **not** mount `scientific-agent-skills` execution or Boltz-2.
- Did **not** implement BitTorrent/WebSeed transport.

## Uncertainties / follow-ups for Josh

1. **LICENSE (F16)** — still founder. Blocks OSS/monetization.
2. **Offline corpus is a fixture**, not PubMed. Bound claims are extracts of those fixtures. Real literature needs a scope revision plus live retrieval + cache.
3. **Optional `/v1/embeddings` ranking** was not wired; BM25 only.
4. **Apple Health** imports quantity `Record`s only (skips sleep-analysis categories and non-numeric values). Mixed units for one metric are not converted.
5. **Encryption-at-rest** remains plaintext. Founder call if AES (would be a new dep or an OS keychain design).
6. **English-only** emergency/framing lexicons. Spanish (and other) red flags still will not trigger.
7. **Share FHIR sidecar** is shaped like a Bundle/Observation list for portability, not validated FHIR.
8. **Hygiene left:** spine-scoped ruff CI ratchet; `packages/*` vs `somatic/*` taxonomy; prune stale remote branches (needs explicit approval).
9. **CI on this PR** should be the GitHub `unittest` job + doctor; confirm green on GitHub before merge.
10. **Host `C:\AI\somatic`** still has a stale index lock — not touched.
11. **Master-plan remaining (not in this sandbox slice):** live ESP32/webcam/depth/thermal/BLE, Boltz-2 GPU, NumPyro belief, MiniCPM-V/o + talking-head, DSPy/GEPA mutation loop, Chronos TrendReader, 140 scientific-agent-skills wrappers, live bio APIs / PDF lake. Those stay extras/founder.
12. **Sandbox bench** can pass because the fixture goal contains `ripasudil`; it does not prove a Nature-paper reproduction.
13. **Biosecurity** is substring-on-public-names (e.g. `variola` inside other words). Refuse+log only.

## Safety rules (spot-check)

Consent default-OFF and fail-closed; `require_consent` on ingest/analyze/share/research/remedy/experiment/parasite **and** bus/sensor-roster/science/avatar/bench. Emergency screen before insights/advice/network, on model output, and on bus/science/avatar inputs. Advisory output framed; no diagnosis/prescription/dosing wording in new surfaces. **`frame_advisory` is defense-in-depth, not a complete diagnosis filter on the live-model path** (system prompt + `temperature=0` + SAFE_FALLBACK still carry residual risk if a model paraphrases past the denylist). No hardcoded medical normals (own baseline or caller ranges only; sandbox numbers labeled simulated / `not_a_clinical_normal`). Citation-binding on items 6–8. Adapter key from env, https-or-loopback when set; keyed URLs also reject private/link-local/ULA and metadata-IP encodings. `consent erase` unlinks ledger/readings/tags first. `dependencies == []`. Sensor privacy: no raw frames/PCM/CSI IQ/BLE identifiers; hardware closed. Biosecurity: name refuse-list, no uplift.

## Local graphical UI (`python -m somatic ui`)

Builder: Grok 4.6. Clone: `C:\AI\somatic-ui-work` from `origin/main`. Did not write in `C:\AI\somatic`. Charter: `planning/UI-BUILD.md`. Readiness: `planning/UI-READINESS.md`.

| Choice | Default | Why |
|---|---|---|
| Bind | **127.0.0.1 only** | Local-first; public bind is a hard-stop. |
| Shipped frontend | **Vanilla SPA** in `somatic/bridge/static/` | CSP `script-src 'self'`. Next.js hydration needs inline scripts. |
| Next.js + Tailwind | `ui/` authoring package | Not a Python dep. `npm run dev` proxies `/api` to the stdlib bridge. |
| Fonts | System UI / Segoe UI | No runtime CDN. |
| Theme | Moss primary, white / near-black | Impeccable seed; not cream wellness. |
| Charts | None in shipped app | Engine summaries already include z-scores. |
| 3D presence | **Not shipped** | Render-only speech from `render_presence`. r3f deferred. |
| Adaptive UI | **Not implemented** | Gated later; local/opt-in/reversible if revisited. |
| Native mobile | **Not implemented** | PWA manifest only. |
| Crisis line | US **988** | Already in the engine. |

| Surface | Path | Notes |
|---|---|---|
| Status | `/` | All-off is a valid, legible state. Full `doctor` stays CLI. |
| Consent | `/consent` | All 7 scopes, default OFF, ledger. |
| Analyze / Share / Ingest / Experiments | `/analyze` `/share` `/ingest` `/experiments` | Same gates as CLI. Ingest preview before save. |
| Research / Remedy / Parasite | `/research` `/remedy` `/parasite` | Honest-null, local passages (URLs not fetched). Parasite does not name species. |
| Sensors | `/sensors` | Features only. Go-live greyed. |
| Science / Bench / Presence | `/science` `/bench` `/presence` | Sandbox / render-only. |
| Suggestions | `/suggestions` | Scope reserved; no unsolicited suggestions implemented. |
| CLI tools / Replay | `/tools` `/replay` | Fabric / csi-parse / doctor / run remain CLI. |
| Privacy | `/privacy` | Always reachable; right-to-erasure. |

Hard-stops honored: no Python core dep, no public bind, no LICENSE change, no live hardware, no fabric vector rewrite.

## Enrich UI + README + finishing suite (2026-08-19)

Builder: Grok 4.6. Clone: `C:\AI\somatic-ui-work`. Did not write in `C:\AI\somatic`. Charter: `planning/ENRICH-AND-FINISH.md`.

| Choice | Default | Why |
|---|---|---|
| Charts | Local SVG in `app.js` | CSP `script-src 'self'`; no CDN library |
| Axe | `ui/` + jsdom | Node is allowed for authoring; color-contrast skipped in jsdom |
| Diagram | committed SVG | No external image host |
| Theme screenshots | light (moss-on-white) | Founder palette; dark still works |
| LICENSE | unchanged | Founder-gated |
| Public URL | not published | Hard-stop |

| Lens | Before | After |
|---|---|---|
| UI craft | ~3/5 | 4/5 |
| A11y | usable | AA-audited (axe 0 violations on fixture; landmarks/CSP tests kept) |
| README | phase archive | product front page |
| Finishing suite | not run | `planning/FINISHING-REPORT.md` |

Rails re-probed via `python -m unittest tests.test_ui_bridge` (24 OK): deps `[]`, loopback Host/Origin, CSP, analyze 403 when off, honest-null, live sensors refused, erasure, no diagnosis copy.

Founder-gated leftovers: LICENSE, release/deploy/public website, live literature, live hardware.

Unsure: GitHub Actions empty-workflow-name flake seen on PR #86; host verification is the merge gate if CI fails to start.

## Closeout (professional-grade) — 2026-08-19

Charter: `planning/CLOSEOUT.md`. Branch: `closeout/professional` from `origin/main` in `C:\AI\somatic-ui-work`.

| Item | What shipped |
|---|---|
| UI | Quiet Instrument: IBM Plex self-hosted, token ramps, spine + seven-tick meter, numbered consent, light+dark screenshots of every surface |
| Design audit | `ui/DESIGN.md`, `ui/DESIGN-NOTES.md`, `ui/contrast-tokens.json`; `npm run a11y` 0 + 11 contrast pairs |
| README | Product front page + architecture SVG + gate SVG |
| Live literature | Europe PMC via stdlib urllib; `SOMATIC_RESEARCH_LIVE` off by default; CI mocked |
| SSRF | `somatic/net/ssrf.py` shared by adapter + live lookup |
| frame_advisory | Structural `Diagnosis:` / `Take N mg` |
| DAST | 413 / 415 / 400 / traversal 404 on loopback |
| CI workflow | `ubuntu-22.04` + `workflow_dispatch`; await a real GitHub run |
| Encryption at rest | Not added; 0600 + documented limitation |
| LICENSE | untouched |

| Lens | Enrich (#87) | Closeout |
|---|---|---|
| UI craft | 4/5 (rejected) | **4.55/5** |
| Contrast | skipped in jsdom | token math gate |
| Literature | offline only | optional live, CI offline |

Defaults: IBM Plex Sans; Europe PMC first; US 988; no core deps.

Founder-gated leftovers: LICENSE, release/deploy/public website, live hardware.

## README to the kortex-audio bar (2026-08-19)

Charter: [planning/README-FINISH.md](README-FINISH.md). Branch: `docs/readme-kortex-bar` from `origin/main` in `C:\AI\somatic-ui-work`. Did not write in locked `C:\AI\somatic`. PR: https://github.com/Ardynai/somatic/pull/89. Head at open: `9ca6ed5`.

What shipped (docs / diagrams only):

- `README.md` rewritten to the kortex-audio structure: hero + Figure 1, emoji sections, honest real/sandbox/off-by-default/founder-gated Status, Surface / Owns / First-files table, Figure 2 with `Source:` provenance, verified quickstart, existing env toggles only, strong Security/Privacy, honest License (no LICENSE file added).
- Quiet Instrument identity on Figure 1 SVG (moss / ink / paper). Draw.io + Mermaid source alternates for both architecture SVGs.
- Phase archive remains in `docs/HISTORY.md`. `docs/ARCHITECTURE.md` now points at the product figures first.

Host gates: `python -m somatic doctor` OK; `python -m somatic consent status` all-OFF; `pyproject` `dependencies == []`. Every README image and relative link resolves. GitHub Actions still `startup_failure` in 0s on push/PR (same ghost as #86–#88). Merged after host verification, not a green Actions job.

Hard-stops honored: LICENSE untouched; no public site/URL; no website runtime deps; no invented live-hardware or live-corpus claims; screenshots captioned as local / all-scopes-off / blocked research / sandbox sensors.

## Sensor Field visualization + ESP32 CSI ingest (2026-08-19)

Builder: Grok 4.6. Clone: `C:\AI\somatic-sensor-viz`. Branch: `feat/sensor-viz-and-csi` from `origin/main`. Did **not** write in locked `C:\AI\somatic`. Charter: `planning/SENSOR-VIZ-AND-CSI.md`.

### What is real vs sandbox vs needs-hardware

| Layer | Status |
|---|---|
| Field / Body view | **Real UI**, sandbox data. Renders existing `pose3d.joints` (head/torso) + envelope/occupancy. Banner: `Sandbox · synthetic · not a real person.` |
| Loopback UDP CSI ingest | **Real software**, stdlib `socket`, bind `127.0.0.1:53721`. JSON / CSI_DATA / simple CSV. Features only. Off until live grant + subject consent. |
| Host serial forwarder | **Real sketch** (`examples/hardware/`). Optional `pyserial` extra. |
| Physical ESP32 capture | **Not validated.** `sandbox-verified; needs a real ESP32 to validate live.` |
| Body pose from CSI | **Wired, off.** `pose_model.py` returns empty joints. No weights in-repo. Founder-gated. |
| Webcam / BLE / other live modalities | Still refused. `LIVE_SENSOR_INTEGRATION_IMPLEMENTED` remains False. |

### Defaults chosen (continue)

| Choice | Default | Why |
|---|---|---|
| UDP port | **53721** (`SOMATIC_CSI_UDP_PORT`; `0` = ephemeral for tests) | Unprivileged, documented. |
| Bind | **127.0.0.1 only** | Off-loopback bind and non-loopback senders fail. ESP32 USB serial → host forwarder → loopback UDP (the ESP32 cannot target the PC's localhost). |
| Heatmap | Quiet Instrument green OKLCH ramp | Token system; not rainbow. |
| Live grant | `~/.somatic/sensor-live.json`, default OFF | Not an 8th core scope. Requires `subject_consent`. |
| Feature store | `~/.somatic/csi-features.json`, 128 frames, `0600` | Derived keys only; erased with consent erase. |
| Pose model | Off unless env + weights file + numpy extra | Founder-gated; still returns empty joints until a real model is supplied. |
| LICENSE | untouched | Hard-stop. |

### Host gates

- `python -m unittest` **930 tests OK**
- `python -m somatic doctor` OK
- `python -m ruff check` + format on changed Python files OK
- `pyproject` `dependencies == []` (`pyserial` only in extras `csi` / `sensors` / `all`)
- `npm run a11y` in `ui/`: axe 0 violations
- Adversarial: raw CSI keys stripped; live without grant 403; bind `0.0.0.0` raises; live Field hides skeleton

### Founder-gated leftovers

LICENSE; buying / validating a physical ESP32; enabling the pose model and shipping weights; public release / public URL.

## UI-rich rebuild (2026-08-19)

Builder: Grok 4.6. Clone: `C:\AI\somatic-ui-rich`. Branch: `feat/ui-rich` from `origin/main` at `a182a4f`. Did **not** write in locked `C:\AI\somatic`. Charter: `planning/UI-RICH.md`. Map: `ui/DESIGN-NOTES.md` v2.

### What shipped

Vite + React **IIFE** compiles to `somatic/bridge/static/{index.html,app.js,styles.css}`. Next hydration was skipped because it needs `unsafe-inline`. Users still run `python -m somatic ui` with no Node at runtime.

Frontend stack actually in the bundle and on screen:

| Skill | Surface |
|---|---|
| R3F + Drei + postprocessing Bloom + maath + troika + Theatre core | Field 3D stage; Presence avatar (interactive browsers) |
| GSAP | Route reveals (`immediateRender: false`; not opacity-gated) |
| Lenis | Smooth scroll; skipped under `prefers-reduced-motion` |
| Zustand | Path, consent, palette, inspector |
| Tailwind v4 (no preflight) | Utility layer on Quiet Instrument tokens |
| lil-gui | Field occupancy inspector (auto-rotate / bloom / scale / grid) |
| xterm.js | CLI tools read-only replica |
| yocto-spinner | Braille frames in the React skeleton only (Node TTY not imported) |

Skipped (honest): Rapier (WASM CSP), OpenTUI (native), StableAvatar/GaussianTalker/Audio2Face (founder-gated), Howler/use-sound (health: no surprise audio). Astryx was not present.

Headless Chrome cannot paint WebGL here. Field/Presence use a labeled SVG `StagePoster` when `navigator.webdriver` or UA `HeadlessChrome`. Interactive browsers still get Canvas. `?palette=1` captures the command palette.

### Rails / CSP

- **No Python core dep.** `pyproject` `dependencies == []`.
- **No bridge API / engine edits.** Consent, emergency, citation, biosecurity, no-raw-sensor, loopback, erasure unchanged.
- **CSP unchanged:** `script-src 'self'`. **No** `wasm-unsafe-eval`. No CDN. No remote fonts.
- LICENSE untouched. Pose model still founder-gated. Field is sandbox/synthetic or loopback features, labeled.

### Host gates

- `python -m unittest` **930 tests OK** (81s)
- `python -m somatic doctor` OK
- `python -m ruff check` + format on changed Python (`docs/ui-screenshots/capture.py`) OK
- `npm run a11y`: axe **0** violations; 11 token contrast pairs OK
- Screenshots: light + dark for surfaces 01–21 including granted Field, Presence, and Ctrl+K palette

### Design-director score

**4.6 / 5** on depth (rich + dense + optioned). Does not read as a minimal vanilla SPA.

### Founder-gated leftovers (unchanged)

LICENSE; public release / public URL; live-sensor pose model weights; buying / validating a physical ESP32.

## UI Bioluminescence re-skin (2026-08-19)

Builder: Grok 4.6. Clone: `C:\AI\somatic-ui-bold`. Branch: `feat/ui-bioluminescence` from `origin/main` at `9aa7458`. Did **not** write in locked `C:\AI\somatic`. Charter: `planning/UI-BOLD.md`. Spec: `planning/UI-BOLD-DIRECTION.md`. Visual target: `docs/ui-mockups/somatic-bold-mockup.html`. Map: `ui/DESIGN-NOTES.md` v3.

### What shipped

Re-theme of the Vite/React cockpit (not a re-architecture). Dark **Bioluminescence** is the new default; light remains a first-class sibling. Self-hosted OFL fonts: Space Grotesk, IBM Plex Sans, IBM Plex Mono. Layered translucent panels, emerald hairlines, glow-as-elevation, masked 44px instrument grid, capability ring, KPI tiles + sparklines, Field bloom / SVG poster, xterm pine-black.

### Rails / CSP

- **No Python core dep.** `pyproject` `dependencies == []`.
- **No bridge API / engine / consent / safety edits.** Rails re-proved in unittest (no-consent blocked, live CSI off without grant, loopback-only, honest-null, erasure).
- **CSP unchanged:** `script-src 'self'`. **No** `wasm-unsafe-eval`. No CDN. No remote fonts.
- Coral/red used only for emergency routing. Honest-null stays large muted type.
- LICENSE untouched. Pose model still founder-gated. Field is sandbox/synthetic or loopback features, labeled.

### Host gates

- `python -m unittest` **931 tests OK** (87s)
- `python -m somatic doctor` OK
- `python -m ruff check` + format on changed Python OK
- `npm run a11y`: axe **0** violations; 12 token contrast pairs OK
- Screenshots: light + dark for surfaces 01–21 refreshed

### Design-director score

**4.7 / 5** against the Bioluminescence mockup (dark luminous cockpit, not flat/minimal).

### Founder-gated leftovers (unchanged)

LICENSE; public release / public URL; live-sensor pose model weights; buying / validating a physical ESP32.

## README Bioluminescence refresh (2026-08-19)

Builder: Grok 4.6. Clone: `C:\AI\somatic-ui-bold`. Branch: `feat/readme-bioluminescence` from `origin/main` at `ccbbab8`. Did **not** write in locked `C:\AI\somatic`. Docs/images only.

### What shipped

- Authored bold SVGs from `planning/somatic-architecture-bold.svg` and `planning/somatic-dataflow-bold.svg` overwrite `docs/diagrams/somatic-local-architecture.svg` and `docs/diagrams/somatic-data-flow-gates.svg` (filenames kept).
- Draw.io + Mermaid are **simplified** alternates of the new content (dark instrument; 403 / clinician / honest-null branches). Captions say the SVG is the authored source.
- README hero is `docs/ui-screenshots/dark/19-field.png`. Screenshots section uses live Bioluminescence captures (status light/dark, palette light/dark, Field light/dark, consent dark). Seven-tick / Quiet Instrument captions dropped.
- Prose names the designed Bioluminescence cockpit (⌘K, inspector, R3F Field, `script-src 'self'`). LICENSE section unchanged (no license picked).

### Gates

Docs/images only. `pyproject` `dependencies == []`. `python -m somatic doctor` OK.

### Founder-gated leftovers (unchanged)

LICENSE; public release / public URL; live-sensor pose model weights; buying / validating a physical ESP32.


