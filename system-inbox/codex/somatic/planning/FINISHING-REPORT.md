# Somatic finishing report (professional closeout)

Date: 2026-08-19
Builder: Grok 4.6 in `C:\AI\somatic-ui-work`
Charter: [CLOSEOUT.md](CLOSEOUT.md)
Identity honored: local-first, stdlib-only Python core, single-user, consent default-OFF. LICENSE untouched.

This file is the evidence pack for the Locus Evolution Lab finishing workflows that apply to Somatic. Layers that imply server-side custody, accounts, cloud, or hosted infra are **not-applicable**. They were not installed.

## Production readiness (18-layer gate)

Source: `locus-evolution-lab/docs/workflows/PRODUCTION_READINESS_CHECKLIST.md`.

| # | Layer | Status | One-line justification |
|---|---|---|---|
| 1 | Front-end | **ready** (local) | Quiet Instrument SPA: IBM Plex, token ramps, component states, light+dark screenshots. Not a hosted website. |
| 2 | API & backend | **verified** (local) | Stdlib JSON bridge reuses engine functions. DAST unit tests on the loopback surface. |
| 3 | Database & storage | **ready** (local files) | JSON under `~/.somatic/` with `chmod 0600`. Right-to-erasure unlinks them. |
| 4 | Auth & permissions | **not-applicable** (accounts) / **verified** (consent) | Seven default-OFF scopes + loopback Host/Origin. |
| 5 | Hosting & deployment | **not-applicable** | `python -m somatic ui` on the owner's machine. Public URL is founder-gated. |
| 6 | Cloud & compute | **not-applicable** | Optional local model URL. Optional live literature is public APIs, off by default. |
| 7 | CI/CD | **fixed in this pass** | `.github/workflows/ci.yml`: `ubuntu-22.04`, `workflow_dispatch`, job `unittest and doctor`. Merge waits for a real run (not ghost `startup_failure`). |
| 8 | Security | **ready** (local threat model) | Loopback bind, CSP `script-src 'self'`, shared SSRF helper, no raw sensor egress. |
| 9 | Rate limiting | **not-applicable** | Single-user loopback. |
| 10 | Caching & CDN | **not-applicable** / **ready** (no-store) | `Cache-Control: no-store`. No CDN. |
| 11 | Load balancing | **not-applicable** | One process, one user. |
| 12 | Error tracking | **partial** (by design) | In-page errors + stderr. No egress telemetry. Client sees `{error, message}`, not tracebacks. |
| 13 | Availability | **partial** (local) | Owner's machine. Recovery is copies of `~/.somatic/`. |
| 14 | Compliance framing | **partial** | Informational-not-medical, English-only, US 988, LICENSE unset. Local erasure exists. |
| 15 | Testing | **ready** | `python -m unittest` + doctor. Bridge DAST, SSRF, live-research mocks, axe 0 + token contrast. |
| 16 | Operations | **not-applicable** (on-call) | ThreadingHTTPServer for one user. |
| 17 | Maintenance | **partial** | High-risk paths never auto-approve. Fabric vectors and `phase12_contracts.py` untouched. |
| 18 | Secrets | **ready** | `.env` uncommitted. Model key from env only. |
| 19 | System discovery | **not-applicable** | No service mesh. |

**Claim:** finished as a **local v1 product**, not as hosted SaaS. Do not call it production-cloud-ready.

## Prelaunch hardening (actual work)

Source: `locus-evolution-lab/docs/workflows/PRELAUNCH_HARDENING_CHECKLIST.md`.

1. **Build/test** — targeted unittest green; `npm run a11y` 0 violations + 11 contrast pairs; ruff clean on changed Python.
2. **Static hardening** — ruff on changed modules only. Did not ruff-fix the monolith.
3. **App-sec review of the loopback bridge** — Host/Origin gate, CSP, `no-store`, `nosniff`, `no-referrer`, static path confined to `STATIC_ROOT`.
4. **DAST-style (127.0.0.1 only)** — oversized body 413; non-JSON content-type 415; malformed JSON 400; path traversal 404 and does not leak `pyproject.toml`; non-loopback Host/Origin 403. Unhandled exceptions return `{"error":"internal"}`.
5. **Abuse/resilience** — live sensor POST refused; literature fetch size-capped, no redirects, host allowlist; SSRF rejects RFC1918 / link-local / metadata encodings even without a model key.
6. **Observability** — `aria-live` slots; stderr access log; no analytics egress.
7. **Secrets** — no committed keys. Research live uses no API key.
8. **Availability** — corrupt JSON stores fail-closed to empty/all-OFF; erase unlinks first.
9. **Encryption at rest** — **known limitation.** Stores are plaintext JSON with `0600`. Optional `cryptography` extra was **not** added (would be a new extra, not a core dep; skipped to keep the v1 surface small). Documented here.
10. **Release** — **do not release / deploy / publish.** LICENSE unset.

## Safety fix-soons closed

| Item | Where | Evidence |
|---|---|---|
| SSRF helper | `somatic/net/ssrf.py` | Private, link-local, metadata, decimal/hex/mapped; tests in `tests/test_ssrf.py` |
| Adapter uses helper | `somatic/advisory/adapter.py` | Unkeyed `https://192.168.1.10/` rejected |
| Live literature | `somatic/research/live.py` | urllib, allowlist, https, no redirects, 256KiB, off by default |
| CI hermetic | `tests/test_research_live.py` | Injected `fetch`; never hits the network |
| `frame_advisory` residual | `somatic/safety/core.py` | Structural `Diagnosis:` / `Take N mg` |
| NaN/inf ingest | `parse_finite_value` | Existing tests still green |
| CLI graceful notes | ingest CLI | Existing tests still green |

## Praxis / ponytail

Changed Python formatted and ruff-clean. README is a product front page with architecture + gate diagrams. Phase archive stays in `docs/HISTORY.md`. No LICENSE file.

## Expert panel (closeout UI)

See [UI-READINESS.md](UI-READINESS.md). Craft **4.55/5**. Distinctiveness lives in the seven-tick meter and numbered consent protocol, not a card dashboard.

## Blocked / deferred

- LICENSE (founder)
- Public release / website / domain
- Encryption-at-rest beyond 0600
- Live hardware sensors
- GitHub Actions: workflow file fixed; a real green run on GitHub is the remaining proof (PRs #86/#87 hit ghost `startup_failure` checks)

## Rails re-probed

`dependencies == []`; loopback bind; CSP `script-src 'self'`; engine gates reused; no raw sensor egress; presence render-only; erasure complete; fabric / `phase12_contracts.py` untouched; no secrets committed.
