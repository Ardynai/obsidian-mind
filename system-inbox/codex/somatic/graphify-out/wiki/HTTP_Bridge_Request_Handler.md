# HTTP Bridge Request Handler

> 13 nodes · cohesion 0.33

## Key Concepts

- **BridgeHandler** (15 connections) — `somatic/bridge/server.py`
- **._handle()** (9 connections) — `somatic/bridge/server.py`
- **._gate_request()** (7 connections) — `somatic/bridge/server.py`
- **._send_json()** (6 connections) — `somatic/bridge/server.py`
- **._serve_static()** (5 connections) — `somatic/bridge/server.py`
- **._cors_headers()** (4 connections) — `somatic/bridge/server.py`
- **.do_OPTIONS()** (4 connections) — `somatic/bridge/server.py`
- **._send_bytes()** (4 connections) — `somatic/bridge/server.py`
- **._read_json_body()** (3 connections) — `somatic/bridge/server.py`
- **.do_GET()** (2 connections) — `somatic/bridge/server.py`
- **.do_POST()** (2 connections) — `somatic/bridge/server.py`
- **BaseHTTPRequestHandler** (1 connections)
- **.log_message()** (1 connections) — `somatic/bridge/server.py`

## Relationships

- [Local UI HTTP Server](Local_UI_HTTP_Server.md) (4 shared connections)
- [Loopback Origin Validation](Loopback_Origin_Validation.md) (4 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (3 shared connections)

## Source Files

- `somatic/bridge/server.py`

## Audit Trail

- EXTRACTED: 57 (90%)
- INFERRED: 6 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*