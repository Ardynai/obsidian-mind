# Somatic — Advisory Review & Re-Plan (post-pivot)

**Prepared by:** Fable 5 (planner) — read-only advisory review; nothing implemented, no PR touched.
**Date:** 2026-07-23
**Repo:** `Ardynai/somatic` (private) · local `C:\AI\somatic` · vault `C:\AI\obsidian-mind`
**Method:** Full `main`-HEAD mirror analyzed in a sandbox; runtime spine executed and attacked adversarially; git + PR state verified via GitHub API + host `gh`; lab doctrine + scorecard templates read (`Ardynai/locus-evolution-lab`). Review fanned out across **five Fable-5 sub-agents** (security/medical-safety, correctness, architecture/CI, cost-scale-monetization, plan-strategy) + **two finished-product simulations** (N-of-1 self-tracker, receiving clinician). Every load-bearing claim below was checked against source or produced by running the code.

> Reading guide: **[safe-now]** = code/CI/docs, additive, no safety-semantic change · **[gated]** = changes a safety/consent gate → planner host-verify + review-stack (the "Jules" role is now the org Cursor stack + Fable 5 human backstop) · **[founder]** = a Josh decision. Effort **S/M/L**.

---

## 0. Headline

The pivot landed a **genuinely well-built spine**. The consent plumbing is fail-closed and default-OFF, insights invent **no** population normals (test-enforced), the emergency screen short-circuits, framing refuses authoritative wording, and it's clean stdlib with `dependencies == []`. Independent reviewers all rated the new code the best in the repo.

But the review found, and **confirmed by execution**, that the two gates the whole legal/safety promise rests on are currently **thin denylists that fail both ways**:

1. **`frame_advisory` is porous** — paraphrased diagnosis/dosing ("Your results indicate cancer", "I recommend 50 milligrams") passes the gate and reaches the user on the AI path; because it doesn't *raise*, SAFE_FALLBACK never fires. Simultaneously it **over-matches** on benign text ("you have been sleeping well", a metric literally named "prescribed dose"), which either nukes a legitimate AI read to SAFE_FALLBACK or **crashes the whole analyze flow**.
2. **`emergency_screen` misses real red flags** — fainting, seizure, overdose, hemoptysis, "worst headache of my life", "crushing pressure in my chest" (the pattern is literally `chest pain`), most suicide phrasings, and every non-English red flag — while **over-firing** on ordinary questions ("what's my long-term heart-attack risk?") and metric names ("stroke rate").

Layer on: the consent model is currently **theater** (4 of 7 scopes gate nothing; the ledger's persist / revoke / right-to-erasure are unreachable from the CLI; `--grant` is re-typed every run), the AI adapter **ships the full health packet to a remote endpoint under a scope whose text never says so**, and the ~33-minute CI gate is **one fixable performance bug** in the dead governance monolith.

None of this is an architectural failure — it's a young spine whose guarantees currently lean on the model's system prompt and happy-path inputs rather than on the gates themselves. All of it is fixable above an untouched core. The single most important consequence: **the current backlog leads with the research loop — the highest-legal-exposure, most-external-dependency item — built on top of these porous gates and theater consent. That ordering is backwards on risk and should change.**

---

## 1. Verified state (2026-07-23)

- **Branch/PRs:** `main` clean on Windows (host git `core.autocrlf=true`; the "42 modified files" seen through the Linux device-mount is a CRLF artifact, not real work). `.claude/` and `.specify/` untracked (gitignored intent — but see F-hygiene). **PR #75 (analyze), #76 (share), #77 (docs/handoff) all MERGED. Zero open PRs.** History caps at the spine; the pre-pivot phase arc ends at 12S (12T/#65 never merged).
- **Spine tests:** 38/38 spine tests pass in sandbox; `ruff check` clean on the spine (`consent/`, `safety/core.py`, `advisory/`, `insights/`, `flows/`). `dependencies == []` confirmed.
- **Caveat to surface to Josh (not acted on — external/possibly-live):** a stale 0-byte `.git/index.lock` (mtime 04:21) plus 2–3 lingering host `git` processes. If commits/merges act stuck, remove the lock and clear the dead git procs — left for Josh since a live IDE git op can't be ruled out from here.

---

## 2. Prioritized findings — ranked impact × (1/effort)

| # | Finding | Sev | Effort | Class | Batch |
|---|---|---|---|---|---|
| 1 | `frame_advisory` denylist porous → paraphrased dx/dosing reaches user on AI path; SAFE_FALLBACK never fires | **Blocking (promise)** | M | [gated][founder] | Safety-gate hardening |
| 2 | `frame_advisory` over-match → benign metric names crash analyze flow; benign AI text nuked to fallback | **High** | S | [gated] | Safety-gate hardening |
| 3 | `emergency_screen` misses real red flags (fainting/overdose/stroke/thunderclap/most SI/non-English) | **High** | M | [gated][founder] | Safety-gate hardening |
| 4 | `emergency_screen` over-fires on risk questions + metric names ("stroke rate") | **Medium** | M | [gated][founder] | Safety-gate hardening |
| 5 | No adversarial/obfuscation (NFKC/zero-width/homoglyph) coverage on the live regex gates | **High** | M | [gated] | Safety-gate hardening + eval harness |
| 6 | Consent is theater: 4/7 scopes gate nothing; ledger persist/revoke/`purge_user_data` unreachable from CLI; `--grant` re-typed each run | **High (promise)** | S–M | [safe-now]+[founder] | Consent persistence + `somatic consent` CLI |
| 7 | AI adapter sends full health packet to remote endpoint under a scope that never discloses egress | **High (privacy)** | S–M | [founder][gated] | Consent wording / model-locality split |
| 8 | 33-min CI = un-memoized builder cascade in the monolith (≈800M calls/`doctor`; 7 tests replay `doctor`) | **High (velocity)** | S–M | [gated]; test-dedup [safe-now] | CI/perf |
| 9 | `doctor` shows zero spine status; still hand-wired, ~1,150 lines | **Medium** | S–M | [safe-now] | CLI/doctor |
| 10 | `share` runs the AI network POST **before** checking `professional-sharing` consent | **Medium** | S | [gated] | Flows hardening |
| 11 | Adapter: no SSRF/redirect controls; `http`+bearer allowed; `Authorization` survives cross-origin redirect | Med (svc) / Low (local) | S–M | [gated][founder] | Adapter hardening |
| 12 | Silent input-dropping: bad refs (`min/max` vs `low/high`), `"n/a"` in a series, single-element lists → dropped with a *misleading* "no numeric metrics" note | **Medium** | S | [safe-now] | Flows correctness |
| 13 | `_join_base_url` doubles `/v1` for the standard Ollama/vLLM base URL → guaranteed first-run 404 | Low | S | [safe-now] | Adapter correctness |
| 14 | Clinician doc: no dates/units/values (z-branch omits the reading it flags); alarmist z at small n; debug tokens as "sources"; ~37% boilerplate | **High (adoption)** | M | [safe-now] | Share polish |
| 15 | README/docs describe the wrong product ("docs-first skeleton"; forbidden "clinical decision-support reports"); `analyze`/`share` appear zero times | **Medium (legal/legibility)** | S–M | [safe-now] | Docs truth-up |
| 16 | No LICENSE chosen (`pyproject`: "License not selected"); blocks OSS/monetization | Medium | S once decided | [founder] | — |
| 17 | Markdown injection in `share` (patient_label / model text lands verbatim; interior newlines survive `.strip()`) | Low–Med | S | [gated] | Share hardening |
| 18 | Repo hygiene: `.gitignore` misses `.claude/`+`.specify/`; dual `packages/*` vs `somatic/*` taxonomy; orphan lanes; `safety/__init__` still "scaffolded" | Low | S | [safe-now] | Hygiene |

---

## 3. Findings in detail

### A. Safety spine — the crown jewels, currently thin (findings 1–5, 10, 11, 17)

All confirmed by executing the real modules.

**F1 — `frame_advisory` denylist is porous.** `somatic/safety/core.py` `_AUTHORITATIVE_PATTERNS` is a small regex denylist and the *last* filter on model output. Confirmed passing (NOT rejected): "Your results indicate cancer.", "You likely have hypothyroidism.", "I recommend 50 milligrams of lisinopril daily.", "Start metformin 500mg tonight." On the AI path (`somatic/advisory/adapter.py`), emergency screen doesn't fire, `frame_advisory` doesn't raise → the text returns verbatim with a model-supplied grade. SAFE_FALLBACK only triggers when framing *raises*, so it never engages. The "never diagnosis/dosing" guarantee is currently carried by the system prompt + `temperature=0`, not by the gate. *Why it matters:* this is the legal shield. *Risk if ignored:* a configured model emitting authoritative wording ships it to the user. *Fix:* move from denylist to structural framing (always wrap output in an informational envelope regardless of content, and/or an allowlist of safe shapes) + require a resolved evidence grade. **[gated] + [founder]** on the framing model. Effort **M**.

**F2 — `frame_advisory` over-matches → crashes / destroys legit output.** The `\byou\s+have\s+…`, `prescribe[sd]?`, `stop\s+taking` patterns fire on benign text. Confirmed CRASH via `analyze_user_data` (ANALYSIS_INSIGHT granted) with packets `{"things you have logged":[1,2,3,4]}`, `{"meds you stop taking":[10,20]}`, `{"prescribed dose":[5,9]}` — because insights build summaries embedding the user-controlled **metric name**, `frame_advisory` raises `AdvisoryFramingError`, and `analyze.py` has no catch around `_run_insights`. On the AI path, benign model text ("You have been sleeping about 7 hours…") raises → the *entire* analysis is replaced by SAFE_FALLBACK (silent information destruction). *Fix:* don't run the authoritative-denylist over engine-authored templated text; wrap the insight framing in the same fallback the adapter uses; redesign the pattern set. **[gated]** (the fallback part is low-semantic-risk). Effort **S**.

**F3 — `emergency_screen` misses real emergencies.** Confirmed NOT triggered: "I passed out", "I am having a seizure", "sudden numbness on one side", "coughing up blood", "black and tarry stool", "I took 60 tylenol", "crushing pressure in my chest", "worst headache of my life", suicide paraphrases ("I want to end my life", "self-harm thoughts are back"), and all non-English ("dolor de pecho intenso"). The nested-value concern is *handled* (the flow screens the full `json.dumps` of the packet), so the gap is **vocabulary + language coverage**, not structure. *Fix:* expand the red-flag lexicon (synonyms + common lay phrasings), document language scope as a known limit, and route suicidal ideation to a crisis line (988 in the US), not just "call your emergency number." **[gated] + [founder]** (how wide; which languages; crisis-line policy). Effort **M**.

**F4 — `emergency_screen` over-fires.** Confirmed: "What is my long-term heart attack risk given these trends?" and packet key `"stroke rate"` (a rowing metric) both halt all analysis with emergency guidance. Risk-trend questions are a *core* use of an informational engine. *Fix:* screen the symptom-report phrasing / question, not raw metric names; require present-tense symptom context. **[gated] + [founder]**. Effort **M**.

**F5 — no obfuscation coverage on the live gates.** Both regex gates handle case (`re.IGNORECASE`) but not NFKC / zero-width / homoglyph / spaced-out evasion (`"chest\u200bpain"`, `"c h e s t p a i n"` both evade). The prior review's F2 concern **migrated from the frozen monolith to the live path**. Weak threat model for emergency (a user evading their own safety net), but real for framing (a model or adversarial input dodging the output gate). *Fix:* add an NFKC-normalized single scan pass + an adversarial test corpus wired as a CI gate. **[gated]**. Effort **M**. *This is the natural home for a stdlib eval/red-team harness — see §7.*

**F10 — `share` POSTs before it checks share consent.** `_share` (CLI) runs the full analysis — including the AI network POST of the user's packet — *before* `render_professional_summary` checks `professional-sharing`. A user who forgot `--grant professional-sharing` still ships data to the model endpoint, then gets refused. *Fix:* check share consent at the top of `_share`. **[gated]**, behavior-narrowing. Effort **S**.

**F11 — adapter network hardening.** No host/IP filtering (localhost, `169.254.169.254`, RFC-1918 all allowed); default `urlopen` follows redirects and carries `Authorization: Bearer` across a cross-origin redirect; `http://`+bearer accepted. Minor in the intended local/Ollama threat model (the `# nosec B310` is justified there), real if `model_url` ever comes from an untrusted source. *Fix:* deny/limit redirects, strip auth on cross-origin, require https-or-loopback when a key is set, optionally warn on link-local/metadata IPs. **[gated] + [founder]** on trust model. Effort **S–M**. (Response-size cap and error paths are already correct — no packet leakage in errors.)

**F17 — Markdown injection in `share`.** `patient_label`/`clinician_note` keep interior newlines (`.strip()` trims only ends) and `result.summary` is inserted verbatim, so `patient_label="demo\n# URGENT: administer 50mg now"` injects a top-level heading into the clinician doc. Low sev (user-authored, clinician-facing) but the doc goes to a third party. *Fix:* collapse newlines / escape leading `#`/`-` in interpolated fields; coerce `summary` with `str()`. **[gated]**. Effort **S**.

### B. Correctness (findings 12, 13; plus sharp edges)

**F12 — silent input-dropping with a misleading note.** `_as_numeric_series` is all-or-nothing: one `"n/a"` (or a bool) discards the whole metric; single-element lists are dropped even with a reference; a bad reference (`{"min":…, "max":…}` instead of `low/high`, or typo'd bounds, or a trailing space in the key) is swallowed by a bare `except … continue`. In every case the user sees "no numeric metrics with a provided reference or baseline" and believes their input was applied. Health exports routinely contain nulls — this is silent data loss on the one subsystem that must be trustworthy. *Fix:* clean-and-keep like the engine's `_clean_series`; treat len-1 as scalar; surface a note on every dropped/malformed input. **[safe-now]**. Effort **S**.

**F13 — `/v1/v1` base-URL trap.** `_join_base_url("http://localhost:11434/v1", "/v1/chat/completions")` → `…/v1/v1/chat/completions` → 404. `.../v1` is the standard OpenAI-compatible base URL for Ollama/vLLM, so this is a guaranteed first-run misconfig (degrades to a note, not a crash). *Fix:* dedupe the suffix/prefix overlap or document "host only." **[safe-now]**. Effort **S**.

**Sharp edges (record, mostly [safe-now] S):** z-flags at n=2–3 are noise ("10.61 SD above baseline" off n=7 is statistically real but reads as alarmist — cap/annotate small-n); `_has_signal` greps the human-readable summary so a metric named "sd above sea level" inflates its own grade; a missing/nonstandard model grade defaults to LIMITED (grade inflation) — consider NONE/PRELIMINARY; `json.dumps(packet)` crashes on a `datetime` value (`default=str` fixes); `analyze` emergency result labels `consent_scope="emergency-screen"` in the flow but `AI_ADVISORY.id` in the adapter (cosmetic inconsistency); `ConsentLedger.from_dict` on corrupt payload silently returns an empty (all-OFF, fail-safe) ledger; series order is assumed chronological with no timestamp support.

**Single highest-value missing test:** a robustness test asserting **`analyze_user_data` never raises on arbitrary user-shaped input** (numbers/strings/bools/None/datetimes/short lists; metric names and reference `source`/`unit` fields with realistic clinical free text like "diagnosed with…", "prescribed…") and that every degradation surfaces as a note. That one test catches F2, F12, the datetime crash, and the malformed-ref family — most of the blocking correctness surface.

### C. Architecture / CI / velocity (findings 8, 9, 15, 18)

**F8 — the 33-minute CI is one performance bug, not test volume.** Every phase12 builder defaults its inputs by re-calling and re-validating the *entire* upstream chain, recursively, with no caching. Measured: one `python -m somatic doctor` = ~1m50s / **~800M function calls** (`phase12a` builder invoked 352×, a phase11 summary 1,434×, `_privacy_violation_count` **13M** calls). Seven test files each run full `doctor` in-process (~110s apiece) → ~13 min of CI is the same computation seven times; single late-chain phase12 tests hit 34–82s. *This also explains the "doctor ~45s+" pain in CLAUDE.md.* Fix shape: `functools.cache` the zero-arg builder/summary paths (deepcopy on return) — **provably behavior-identical** via the existing golden snapshot (`tests/test_status_summary_snapshot.py` + `fixtures/snapshots/status-summaries-v1.json`). A **[safe-now]** first slice: make the 7 doctor tests share one captured `doctor` run (~11 min saved, test-only). The memoization touches `somatic/safety/**` → **[gated]** but low-risk with the snapshot as the equivalence proof. Effort **S–M**. *Highest impact-per-line in the repo.*

**F9 — `doctor` is blind to the product.** ~1,150 lines rendering 30+ frozen pre-pivot phase surfaces and **zero** lines on the live spine — no consent-scope status, no adapter-config check, no emergency-screen self-test, no scopes-default-OFF assertion. For a solo founder, "run doctor" should answer "is the consent-gated spine healthy and are all scopes OFF." *Fix:* add an additive spine-status section (safe — can't break the substring-asserting doctor tests); later, registry-drive the legacy prints (closes the old F3). **[safe-now]**. Effort **S–M**.

**Monolith verdict:** `phase12_contracts.py` (20,884 lines, ~70% duplicated) is imported inside `somatic/` by **exactly one module** — the CLI's `_doctor`. The spine imports it not at all. **Do NOT do the old 12X `validate_contract` rewrite** — the pivot demoted the monolith from "the product" to "doctor's museum exhibit." Safe quarantine path: (1) memoize [F8]; (2) optionally relocate to `somatic/safety/legacy/` behind a re-export shim (snapshot-verified); (3) [founder] endgame — have `doctor` render the golden-snapshot fixture instead of recomputing 30 phases live, with a scheduled CI job re-proving fixture freshness → `doctor` drops to <1s. Keep it meanwhile: it's frozen by policy and load-bearing for `doctor` + the phase11 sanitizers the evidence packs use.

**F15 — docs describe the wrong product.** `README.md` still says "docs-first skeleton only" and advertises "clinical decision-support reports" (the exact wording `frame_advisory` rejects) and a "BitTorrent/WebSeed content fabric"; `analyze`/`share` appear **zero** times in README or `docs/how-it-works/` (correction per Sol's operator review: "consent" *does* appear in README — my earlier "zero consent references" was wrong; the accurate gap is the analyze/share flows + the stale skeleton framing). The pivot PRs also skipped the repo's own `CONTRIBUTING.md` docs-upkeep rule. This misleads the very operators every prompt tells to "read the files first." *Fix:* truth-up README + an ARCHITECTURE row for `consent/advisory/insights/flows` + a "pre-pivot archive" banner over the 100+ legacy phase docs. **[safe-now]**. Effort **S–M**.

**F18 — hygiene.** `.gitignore` covers `.tmp/` but not `.claude/`/`.specify/` (the backlog calls them "gitignored" — half-wrong; one `git add -A` commits them). The repo is **not** ruff-clean overall (316 errors, all in pre-pivot code; spine is clean) — wire a spine-scoped ruff gate now (free), ratchet legacy later as its own reviewed batch. Dual `packages/*` (placeholder READMEs) vs `somatic/*` lanes; orphan lanes (`engines/`, `presence/`, `bench/`); `somatic/safety/__init__.py` still says "scaffolded" though it now holds the live core. All **[safe-now]** S.

---

## 4. Finished-product simulation — grades

Both personas assumed the product "done" per the current plan and used the **real** CLI/output.

**N-of-1 self-tracker (technical, privacy-conscious).** Delighted by: stdlib/no-network-by-default, **no invented normals** (every comparison attributed to "the reference range you provided" / "your own baseline"), sober evidence grades, clean gated `share`. Frustrated by: the `--question` is ignored by insights (feeds only the screen/model), findings come out unranked in dict order with no cross-metric synthesis (HR↑/HRV↓/ferritin↓ is obviously one story, shown as 9 bullets), alarmist uncapped z-scores, **silent-drop on a `min/max` typo**, consent re-typed every run, and **no docs/example packet** (found `analyze` only via `--help`).
- Scorecard mean **2.67/5** ("weekly consumer tool" bar not met; **Trust/Safety = 4/5** met). **Reviewer decision: conditional pass for its real scope** (a safe, honest pre-appointment summarizer) — every failing axis is UX/packaging, **not** safety.
- Blocks adoption: persistent+inspectable consent; docs + a copy-paste example; real ingestion (Apple Health/CSV); rank+synthesize findings; **fail loudly on malformed refs**.

**Receiving clinician (skeptical, time-poor).** This is the rare patient-brought AI doc they "don't have to defend against": title-level "not a diagnosis", no invented normals, cited reference provenance ("source: Quest lab report 2026-05"), honest "AI read skipped" note — chartable without liability sweat (**Safety/liability 5/5**). But can't do medicine with it: **no dates anywhere** (7 readings over a week vs a year = different visits), the z-branch **omits the actual reading it flags**, no units on HR findings, "10.61 SD" is theater at n=7, source labels are developer debug tokens, "moderate" grade means "≥6 readings" not GRADE evidence (and **inverts** clinical importance — a lab A1c scored "preliminary" below a noisy HR trend scored "moderate"), and ~half the page is repeated disclaimer.
- Scorecard: **Trustworthiness/provenance 2, Clinical legibility 2**, Time-efficiency 3, Actionability 3, Safety 5. **Reviewer decision: FAIL for promotion as a "doctor-shareable" artifact; PASS as safety spine.** Do not market it as clinician-facing until dates/units/values + one-disclaimer + provenance land.
- Top asks: dates on everything + a generation date; state the current value+units in every finding; plain-language comparison beside/instead of z; per-metric data-source line; one disclaimer; rename/legend the grades; a small raw-data table; optional FHIR-shaped JSON sidecar (the `to_dict` plumbing already exists).

**Cross-cutting:** the scary part is done right and should ship untouched. What stands between Somatic and daily use is a **front door** (docs+ingestion), a **memory** (persistent consent+history), and a **mouth** (ranking/synthesis + dates/units/values in the output).

---

## 5. Monetization (none defined today)

Local-first + single-user + privacy-first + never-diagnose **eliminates the obvious SaaS options** and any model that custodies health data server-side (hosted SaaS, clinician SaaS = HIPAA-adjacent, worst legal exposure — do not pursue without a deliberate identity change).

- **Recommended primary:** **signed, evidence-graded content packs** (the remedy/retrieval library) distributed as license-gated **Fabric packs** over a **free OSS local-first core with BYO-model** — you sell *content*, not a service; every byte stays local; it reuses the existing `fabric/` signing + license-gate machinery; residual risk is content liability, already mitigated by the safety core.
- **Fallback:** **donations/grants** (GitHub Sponsors + medical-OSS grants; the N-of-1/open-health mission is grant-friendly) + optionally a **one-time "pro" local unlock**. Both preserve every guarantee.
- **Blocker:** pick the **LICENSE first** (F16) — it gates open-core/content-pack; mixed MIT/Apache/"unclear" upstream provenance constrains the choice. **[founder].**

---

## 6. Research loop — ready to spec, not to prompt

Backlog #1 requires the source-grounded retrieval+grounding **spec designed first**. Scaffolding already exists and is reusable: `EvidenceGrade`, `frame_advisory`, the `AUTONOMOUS_RESEARCH` scope, a `LiteratureProvider` Protocol (`providers/literature.py`), `emergency_screen`, and the advisory adapter as a stdlib HTTP-client template (`urllib`, timeout, response-cap, fail-closed). **It is ready to spec now; it is not ready to quick-prompt** — resolve these 5 in the spec first:

1. **Grounding enforcement (the crux, net-new):** `frame_advisory` is a *negative* filter; nothing today stops the model citing from memory. Define **citation-binding**: retrieve → pass numbered passages → require cite-by-passage-id → **post-verify every citation resolves to a retrieved passage** → drop/fallback any unbound claim.
2. **`dependencies==[]` vs semantic retrieval:** HTTP retrieval is fine in stdlib (`urllib` + `xml.etree` for PubMed E-utilities, JSON for ClinicalTrials v2). Ranking/embeddings are the tension — default to a **stdlib lexical tier (BM25/TF-IDF)**, optionally delegate embeddings to the already-configured `/v1/embeddings` endpoint; avoid a default hard dep. **[founder].**
3. **Evidence-grade rubric from source metadata** (RCT/meta-analysis → STRONG/MODERATE; case report/preprint → LIMITED/PRELIMINARY; none → NONE) — owned as a **[gated] safety artifact** like the denylists.
4. **Live vs offline + cache:** the `AUTONOMOUS_RESEARCH` scope text currently says **"offline/mock research only"** — live PubMed retrieval *exceeds that stated limit*. Ship **offline-corpus-first v1**, or revise the scope (a governance change, **[gated]+[founder]**). The cache *is* the offline corpus and the fan-out cost mitigation.
5. **Output shape + where framing composes:** questions/tests/markers/experiments, each a framed `AdvisoryResult`, without tipping into prescriptive "get tested for X"; define exactly where `frame_advisory`/`emergency_screen` sit relative to cited claims.

**Cost note:** today per-user cost ≈ $0 (local, in-memory, one egress). The research loop moves cost to N literature calls + N synthesis completions and can fan out super-linearly (metrics × hypotheses × sources); bake in query dedup, per-run caps, and a content-addressed cache. Two cheap pre-loop wins: cache the deterministic (`temperature=0`) advisory result; guard outbound packet size.

---

## 7. Recommended re-sequenced roadmap + advice on the rest of the plan

The current backlog (research loop → remedy library → parasite ID) points the **highest-legal-exposure work at the weakest part of the shield**. Re-sequence so prerequisites lead and the medical-content items are gated behind a hardened spine:

1. **Consent persistence + `somatic consent` CLI** (grant/revoke/status/erase; wire the existing `to_dict`/`from_dict`; reach `purge_user_data`). Smallest, most legible, zero-medical-risk, pure stdlib; makes the shipped consent model stop being theater and lays the on-disk store every later item writes into. **[safe-now]+[founder]** S. *Recommended next batch.*
2. **Safety-gate hardening + stdlib adversarial eval harness** (broaden emergency lexicon incl. overdose/hemorrhage/thunderclap/passive-SI + crisis-line routing; make framing catch "indicate/consistent with/suggests X" and stop over-matching benign text; **re-screen model output**; NFKC-normalize; ship an adversarial corpus as a CI gate). Patches a demonstrated live hole and is the prerequisite for *every* medical-content item. **[gated]** M. *Hard gate: do not start #4–#6 until this lands and "offline ⇒ honest null" is a tested invariant.*
3. **Data ingestion — CSV first, then Apple Health export** (activate the inert `DATA_INGESTION` scope). The real on-ramp; turns the engine from a hand-authored-JSON demo into something usable. **[gated]** (personal-data) M.
4. **Research loop / co-scientist** — now on persisted consent + hardened gates + real data + the shared grounding substrate. Still the riskiest item; spec first per §6. **[gated]** L.
5. **Evidence-graded remedy library** — reuses #4's retrieval/grounding; grade honestly (default NONE). **[gated]** M–L.
6. **Parasite research/ID (informational)** — same substrate. **[gated]** M.

**Parallel [safe-now] wins that unblock velocity + adoption and can interleave:** F8 CI memoization (biggest velocity payoff), F12 fail-loud-on-malformed-input, F14 clinician-doc dates/units/values + de-duplicated disclaimer, F15 docs truth-up, F9 doctor spine-status, F13 `/v1/v1` fix.

**Strong candidate to promote:** an **N-of-1 experiment designer** — tag an intervention, auto-track return-to-baseline against the user's own series using the existing insights z-machinery. It's literally the master plan's first-class `n-of-1` template, is pure own-baseline math (no population normals, no network, no external claims), and is a **lower-risk, higher-value** near-term item than the research loop. Consider slotting it ahead of #4.

**Bold, on-mission ideas** (local-first, privacy-first, consent-gated): a **signed portable "health-data capsule"** the user owns and any clinician can verify (the trust artifact that makes the tool spread clinician↔patient; `hashlib`/`hmac` keep it dep-free, real public-key signing is a founder call); a **one-command BYO-local-model path** (`analyze --local` → Ollama at :11434 + a `doctor` reachability check) so the privacy promise is concrete; **citation-first "honest null"** remedy grading (absence of evidence as a first-class, prominent output); a **unified local store** (ledger + data + audit) under one `purge_user_data` erasure hook (encryption-at-rest is a founder call — stdlib has no AES).

**Advice on the rest of the plan.** The pivot was the right call and the spine proves it. Hold the line on the two invariants that matter (consent default-OFF + fail-closed; no invented normals) — both are genuinely enforced today. The master plan's grand multi-sensor/avatar/co-scientist vision remains a good north star but should stay behind the Evidence-Source boundary, sandbox-only; the pragmatic slice is the right focus. The two things that most change Somatic's trajectory are non-obvious: **(1) harden the two gates before any more medical content — they are the product**, and **(2) make the consent model real** — persistence + a `consent` CLI is the cheapest change that converts "user-owned, consent-gated" from a claim into a fact, and it's the foundation the audit log, ingestion, experiment designer, and signed capsule all build on. Everything else is packaging on top of a core that is, encouragingly, already sound.

---

## 8. What this review changed (planner config, conservative)

- **This document** — new `planning/phase-13-advisory-review.md` (additive).
- **`planning/backlog.md`** — re-sequenced to the risk-ordered queue above; findings triaged in as one-batch-at-a-time items; in-flight line corrected (#75/#76/#77 all merged).
- **`CLAUDE.md`** — root-caused the `doctor` slowness (un-memoized cascade, not import weight) in the host-tooling note; recorded the host `git core.autocrlf=true` gotcha (device-mount shows false CRLF churn) + the stale-lock caveat; pointer to this review.
- **Left unchanged (deliberately):** `AGENTS.md` and `.cursor/{BUGBOT.md,rules/…}` — the review confirms the operator manual and the review contract/routing are accurate and well-scoped; the finding is that the *gate implementations* are porous (a code batch), not that the *policy* is wrong. Per the conservative-change principle, no edit was warranted.

*A repo-specific GPT-5.6 Sol Max operator prompt carrying these findings is prepared at `.tmp/TASK-safety-hardening-and-review.md`, for the operator to build on.*

---

## 9. Addendum — batch 1 outcome + Sol's operator advisory (2026-07-23)

**Batch 1 (CI memoization) — PR #78 merged, partial by design.** Sol shipped only the safe test-replay dedup (7 suites → one shared `doctor` capture): **CI ~33 → ~17 min**, test-only, zero product/snapshot/dep change (host-verified: diff is 8 `tests/*.py`, +83/−163). The runtime builder cache was **correctly stopped** on a real proof-coverage gap — **independently verified:** the golden snapshot covers 27 of 31 status summaries (the collector skips required-arg summaries), and `_doctor` directly calls 3 of the 4 excluded ones (`phase11_{dossier_lifecycle,preflight,review_record}_status_summary`). Completing the cache is now a clean, ordered batch (see `backlog.md` 1b): extend the snapshot to those 3 paths → then cache with full equivalence.

**Sol confirmed F1–F18** and added value folded into the plan: (a) **F6+** — `ConsentLedger.from_dict` ignores `schema_version` and can restore semantically-corrupt known-scope grants → batch 2 adds strict schema/type/timestamp validation, any failure → all-OFF; (b) **F19** — `--model-key` leaks a credential in process args though `AdvisoryModelConfig.from_env` exists; (c) model output is framed but **not emergency-re-screened**, and model grades should be **"confidence" labels** until citation-bound; (d) **F14/F15 are promotion gates**, not optional polish; (e) monetization — Fabric's "license gate" is redistribution policy, **not** entitlement/payment/revocation infra, so near-term honest path = donations/grants (paid packs need the LICENSE + entitlement stack first).

**Sol's finished-product sim** (self-tracker 3.8/5 conditional beta; clinician 3.0/5 fail) agrees with the Fable-5 sims, with one fair recalibration: **the review's Trust/Safety 4/5 is too generous while F1–F5 are open** — the gates are demonstrably porous, so "safe by construction" is aspirational until batch 3 lands. Treat Trust/Safety as conditional on the gates actually holding.

**F15 correction** applied above (README does reference consent).

**Operator config (Sol, conservative):** two earned rules added to `AGENTS.md` — a clean-sibling-checkout rule (don't build in a dirty/locked working tree; a fresh clone off `origin/main`) and a proof-coverage rule (enumerate every touched call path before calling a fixture an "equivalence proof"). Sol followed both; this is why it built #78 in a sibling clone and stopped the cache.
