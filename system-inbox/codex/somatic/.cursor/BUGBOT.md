# Somatic — Bugbot review contract

Somatic is a standalone, **stdlib-only Python** engine that turns a user's own health data into **consent-gated, _informational_ decision support** — never diagnosis, prescription, or dosing. The whole product promise is that it is safe + private by construction. **Review through that lens: a change that quietly weakens the consent / medical-safety spine is more serious than a functional bug.**

Priority order (lead your report with anything in tiers 1–2):
1. **Consent + medical-safety spine** (the invariants below) — blocking.
2. **Correctness of the gated flows** (`analyze` / `share`, insights) — blocking on data-loss or unsafe output.
3. **Cost & scale** (per-user compute; network in the AI adapter) — non-blocking warning unless egregious.
4. **Code quality / conventions** (stdlib-only, ruff-clean, additive) — non-blocking.

Ground every finding in a `file:line`. Read the diff *and* enough surrounding code to judge whether a called gate actually gates.

## Invariants (each a blocking gate)
1. **Consent default-OFF + fail-closed.** Every scope defaults OFF; privileged work calls `require_consent(ledger, scope)` FIRST and raises if not granted. Flag any capability that runs without a consent check, or any scope enabled by default.
2. **Emergency screen in the path.** `emergency_screen` runs before insights / advice / any network call; a red-flag short-circuits to see-a-clinician-now. Flag any advice path that skips it.
3. **No authoritative medical wording.** Advisory output must pass `frame_advisory`. Flag any "you have X / take N mg / prescribe / stop taking / diagnosed with", or any diagnosis / dosing that bypasses framing.
4. **No invented medical normals.** Insights grade only against the user's OWN baseline or CALLER-supplied reference ranges. Flag any hardcoded clinical threshold or "normal range" in code.
5. **Evidence-graded + source-grounded claims.** Any health claim carries an evidence grade + a real citation via retrieval (PubMed / ChEMBL / ClinicalTrials / bioRxiv / Consensus) — never model memory. Flag ungraded or uncited health assertions.
6. **AI adapter safety.** `analyze()` requires `ai-advisory` consent, emergency-screens before the network call, frames the response, and returns SAFE_FALLBACK (evidence NONE) rather than raw unsafe text. Response is size-capped; no credentials in the URL; http/https only. Flag any raw-model-output path or creds-in-URL.
7. **Right-to-erasure preserved.** `purge_user_data()` must remain able to erase a user's consent + data. Flag changes that strand user data.
8. **stdlib-only; `dependencies = []`.** Flag ANY new runtime dependency in `pyproject.toml` — the list must stay empty.
9. **Fabric byte-interop frozen.** Additive only; Somatic consumes the fabric via the out-of-process sidecar and never reimplements identity / transport / P2P / DHT. Flag edits to byte-pinned JCS / Merkle vectors or any in-repo transport/DHT.
10. **No secrets committed.** `.env` stays uncommitted (`.env.example` only). Flag tokens / keys in source, fixtures, or logs.

If the PR touches none of the above, say so briefly and pass. Do not re-flag pre-existing issues.
