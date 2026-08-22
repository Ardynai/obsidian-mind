# Safety And Governance

## Owns

Blocked-runtime safety surfaces and Phase 11/12 planning contracts:

- `somatic/safety/adapter_readiness.py`
- `somatic/safety/biomodel.py`
- `somatic/safety/phase11_contracts.py`
- `somatic/safety/phase12_contracts.py`
- `fixtures/reviews/`

## Main Flow

The shared readiness gate records review status for future real adapter modes. It can report required gates, satisfied gates, missing gates, and sanitized review metadata, but it never authorizes execution.

The live spine (`somatic/safety/core.py`) emergency-screens English text (NFKC-normalized) before insights or network calls, re-screens model output, routes suicidal ideation to US 988, and frames advisory text as informational. Language coverage is English-only; that is a documented limit.

Phase 11 contracts model review records, preflight dossiers, lifecycle audits, audit indexes, handoffs, acceptances, follow-up queues, decision closeouts, review exports, runtime gap ledgers, and planning-governance closeout. Phase 12 contracts model future runtime-authorization planning surfaces and capability profiles.

## Gotchas

- Reviewed does not mean authorized.
- Public outputs must preserve `execution_permitted: false`, `runtime_stage: not-implemented`, and `real_mode_runtime_enabled: false`.
- `phase12_contracts.py` is too dense to use as a first read. Treat it as contract backing and read the focused phase docs first.
- Do not widen docs language from metadata-only planning to runtime readiness.

## Start Reading

Start with `somatic/safety/adapter_readiness.py`, then `docs/safety-boundaries.md`, `docs/adapter-boundaries.md`, and only then the phase-specific docs.
