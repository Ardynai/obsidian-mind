# UI Bridge Isolation

> 4 nodes · cohesion 0.50

## Key Concepts

- **test_ui_bridge.py** (6 connections) — `tests/test_ui_bridge.py`
- **.setUp()** (3 connections) — `tests/test_ui_bridge.py`
- **_isolate_stores()** (2 connections) — `tests/test_ui_bridge.py`
- **Gate tests for the local-only UI bridge (stdlib, loopback).** (1 connections) — `tests/test_ui_bridge.py`

## Relationships

- [UI Bridge Security Tests](UI_Bridge_Security_Tests.md) (3 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (1 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (1 shared connections)
- [Local UI HTTP Server](Local_UI_HTTP_Server.md) (1 shared connections)

## Source Files

- `tests/test_ui_bridge.py`

## Audit Trail

- EXTRACTED: 11 (92%)
- INFERRED: 1 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*