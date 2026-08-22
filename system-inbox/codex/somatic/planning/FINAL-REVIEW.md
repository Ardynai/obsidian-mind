# Somatic — Final Review Loop (started 2026-08-22)

Base for loop: `origin/main` @ 583956f (#100). Method per round:
(1) adversarial safety re-probe of every gate on current code,
(2) finishing lenses + expert-user personas vs final state,
(3) correctness + coverage pass,
(4) docs/consistency pass.
Every working bypass or real gap is a finding; findings are fixed via
admin-merged PRs (CI down, founder billing). Loop ends after two
consecutive full rounds with **zero actionable findings**.

## Founder-only list (never actioned here)

- LICENSE adoption; CI/Actions billing; buying + validating an ESP32;
  enabling the CSI pose model (weights); any public release/deploy.

## Round 1 — findings (2026-08-22, base 583956f)

Adversarial probe battery (scripted): privileged surfaces with scopes OFF
(8 endpoints), emergency obfuscation battery (zero-width / NBSP / fullwidth
NFKC / uppercase / letter-spaced / tab-split, en+es+fr), frame_advisory
es/fr battery (9 variants incl. no-space mg, unaccented, upper), raw-key
scrubbing through both feature stores + bridge sanitizer, loopback
Origin/Host guard, live grant without subject consent, tampered-envelope
fail-closed, SSRF private/metadata/redirect guards.

| ID | Finding | Fix |
| --- | --- | --- |
| F1 | `/api/analyze` validated payload before the consent gate: empty body with scopes OFF returned **400 invalid_request** instead of 403; crisis text with no `data` field returned 400 instead of routing to help | Consent gate + pre-consent emergency screen moved ahead of `_data_packet`; packet errors suppressed only on the emergency path; deep screen on the built packet kept (`somatic/bridge/api.py`) |
| F2 | Zero-width chars were *deleted* by `normalize_scan_text`, so invisible chars could fuse non-English red-flag words ("dolorⱷenⱷelⱷpecho") past the screen; letter-squeezer missed accented-letter runs; FR apostrophe fusion "j e n'arrive" evaded | Zero-width now normalizes to a separator; squeezer uses Unicode letter classes; additive FR variant `je\s*n'?arrive`; corpus cases `zw-fused-es-chest-pain`, `spaced-apostrophe-fr-breath` added as CI gate (`somatic/safety/core.py`, corpus) |
| F3 | Raw-key scrub lists diverged between stores: CSI cleaner kept `transcript`/`raw_audio`-family keys (and audio cleaner kept CSI-family keys) if ever present | Both cleaners now share one superset denylist (`somatic/sensors/live_store.py`, imported by `live_audio.py`) |

Not findings (probed, held): share/research/science/bench/sensors/experiments
avatar all 403 with scopes OFF; origin/host loopback guard holds for
evil.example / RFC1918 / link-local metadata; live grants refuse without
subject consent; tampered/wrong-key encrypted store fails closed all-OFF;
bridge sanitizer strips pcm/pixels; SSRF allowlist model refuses
loopback/link-local/private literals.

Fix PR: fix/closeout-round1 (tests: analyze-ordering x2, corpus +2,
cross-family scrub). Full suite green before merge.
Merged as #101 (`1b1724b`).

## Round 2 — findings (base 1b1724b, after #101–#103)

Extended probes: unknown-modality live grant (400 mapped), live scan of a
non-live modality with scopes granted (403), right-to-erasure without any
grant (works, by design), CSP verified as a live response header
(`script-src 'self'`; probe initially looked for a meta tag — probe error,
not a finding), shipped bundle ↔ `ui/src` marker parity ("Live lane access",
field-modality selector, Audio biomarkers), no em-dash regression in the
bundle, README staleness scan clean.

| ID | Finding | Fix |
| --- | --- | --- |
| F4 | `docs/HISTORY.md` archive carried ~70 relative links to per-phase docs that were consolidated away (and one root-file link broken by docs/-relative resolution) | Archive links de-linked to code text or re-rooted (`../LICENSE-DISCUSSION.md`); repo-wide md link check now reports 0 missing |

Also merged this round: #102 repo-wide lint zero (ruff check . clean,
zero behavior change proven via AST constant/name comparison + byte-exact
vector tests), #103 coverage raise (+12 tests on audio model plumbing,
WAV variants, encryption keyfile/envelope edges, bridge payloads).

Fix PR: docs/closeout-round2. Suite 993 OK, doctor green, ruff zero.
