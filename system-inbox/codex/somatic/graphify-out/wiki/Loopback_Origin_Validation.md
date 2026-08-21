# Loopback Origin Validation

> 8 nodes · cohesion 0.29

## Key Concepts

- **is_loopback_hostname()** (5 connections) — `somatic/bridge/origin.py`
- **origin_is_loopback()** (5 connections) — `somatic/bridge/origin.py`
- **origin.py** (5 connections) — `somatic/bridge/origin.py`
- **hostname_from_host_header()** (3 connections) — `somatic/bridge/origin.py`
- **Loopback-only origin and Host checks for the local UI bridge.** (1 connections) — `somatic/bridge/origin.py`
- **Return the hostname from an HTTP Host header (no port).** (1 connections) — `somatic/bridge/origin.py`
- **True when ``hostname`` is a loopback name we will serve.** (1 connections) — `somatic/bridge/origin.py`
- **True when Origin is absent or a loopback http(s) origin.      Missing Origin i** (1 connections) — `somatic/bridge/origin.py`

## Relationships

- [HTTP Bridge Request Handler](HTTP_Bridge_Request_Handler.md) (4 shared connections)
- [Local UI HTTP Server](Local_UI_HTTP_Server.md) (2 shared connections)

## Source Files

- `somatic/bridge/origin.py`

## Audit Trail

- EXTRACTED: 18 (82%)
- INFERRED: 4 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*