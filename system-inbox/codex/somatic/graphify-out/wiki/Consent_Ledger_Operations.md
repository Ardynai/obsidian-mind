# Consent Ledger Operations

> 26 nodes · cohesion 0.12

## Key Concepts

- **ledger.py** (10 connections) — `somatic/consent/ledger.py`
- **ConsentScope** (10 connections) — `somatic/consent/scopes.py`
- **resolve_scope()** (10 connections) — `somatic/consent/scopes.py`
- **get_scope()** (8 connections) — `somatic/consent/scopes.py`
- **store.py** (7 connections) — `somatic/consent/store.py`
- **scopes.py** (6 connections) — `somatic/consent/scopes.py`
- **._from_dict_strict()** (5 connections) — `somatic/consent/ledger.py`
- **_validated_event_record()** (5 connections) — `somatic/consent/ledger.py`
- **__init__.py** (4 connections) — `somatic/consent/__init__.py`
- **.grant()** (4 connections) — `somatic/consent/ledger.py`
- **.revoke()** (4 connections) — `somatic/consent/ledger.py`
- **_validated_grant_record()** (4 connections) — `somatic/consent/ledger.py`
- **.is_granted()** (3 connections) — `somatic/consent/ledger.py`
- **_utc_now_iso()** (3 connections) — `somatic/consent/ledger.py`
- **_valid_utc_timestamp()** (3 connections) — `somatic/consent/ledger.py`
- **_validated_actor()** (3 connections) — `somatic/consent/ledger.py`
- **User-owned granular consent catalog and local ledger.** (1 connections) — `somatic/consent/__init__.py`
- **Local, user-owned consent ledger.  Grants and revocations are recorded with UT** (1 connections) — `somatic/consent/ledger.py`
- **Revoke ``scope`` if present and append a revoke event.** (1 connections) — `somatic/consent/ledger.py`
- **Return True only when ``scope`` is currently granted.** (1 connections) — `somatic/consent/ledger.py`
- **Grant ``scope`` and append a grant event with a UTC timestamp.** (1 connections) — `somatic/consent/ledger.py`
- **Frozen catalog of granular consent scopes.  Every scope defaults OFF. Callers** (1 connections) — `somatic/consent/scopes.py`
- **One granular consent capability the user may grant or revoke.** (1 connections) — `somatic/consent/scopes.py`
- **Return the catalog entry for ``scope_id``, or None if unknown.** (1 connections) — `somatic/consent/scopes.py`
- **Resolve a scope object or id string to a catalog :class:`ConsentScope`.** (1 connections) — `somatic/consent/scopes.py`
- *... and 1 more nodes in this community*

## Relationships

- [Consent Ledger Management](Consent_Ledger_Management.md) (8 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (7 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (5 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (2 shared connections)
- [UI Bridge Security Tests](UI_Bridge_Security_Tests.md) (1 shared connections)

## Source Files

- `somatic/consent/__init__.py`
- `somatic/consent/ledger.py`
- `somatic/consent/scopes.py`
- `somatic/consent/store.py`

## Audit Trail

- EXTRACTED: 91 (92%)
- INFERRED: 8 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*