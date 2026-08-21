# Local UI HTTP Server

> 16 nodes · cohesion 0.17

## Key Concepts

- **server.py** (10 connections) — `somatic/bridge/server.py`
- **start_background_server()** (7 connections) — `somatic/bridge/server.py`
- **make_server()** (6 connections) — `somatic/bridge/server.py`
- **serve_ui()** (6 connections) — `somatic/bridge/server.py`
- **bind_host_is_allowed()** (5 connections) — `somatic/bridge/origin.py`
- **BridgeHTTPServer** (5 connections) — `somatic/bridge/server.py`
- **_ui()** (3 connections) — `somatic/cli/main.py`
- **__init__.py** (2 connections) — `somatic/bridge/__init__.py`
- **_query_dict()** (2 connections) — `somatic/bridge/server.py`
- **_safe_static_file()** (2 connections) — `somatic/bridge/server.py`
- **Local-only UI bridge: stdlib HTTP on 127.0.0.1 plus static assets.  This packa** (1 connections) — `somatic/bridge/__init__.py`
- **True when the requested bind address is loopback-only.** (1 connections) — `somatic/bridge/origin.py`
- **Stdlib loopback HTTP server for the local Somatic UI.** (1 connections) — `somatic/bridge/server.py`
- **Bind 127.0.0.1 and serve the local UI until interrupted.** (1 connections) — `somatic/bridge/server.py`
- **Start a daemon server for tests. Caller must shutdown.** (1 connections) — `somatic/bridge/server.py`
- **Thread** (1 connections)

## Relationships

- [HTTP Bridge Request Handler](HTTP_Bridge_Request_Handler.md) (4 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (3 shared connections)
- [Loopback Origin Validation](Loopback_Origin_Validation.md) (2 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (2 shared connections)
- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (1 shared connections)
- [UI Screenshot Capture](UI_Screenshot_Capture.md) (1 shared connections)
- [UI Bridge Isolation](UI_Bridge_Isolation.md) (1 shared connections)

## Source Files

- `somatic/bridge/__init__.py`
- `somatic/bridge/origin.py`
- `somatic/bridge/server.py`
- `somatic/cli/main.py`

## Audit Trail

- EXTRACTED: 46 (85%)
- INFERRED: 8 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*