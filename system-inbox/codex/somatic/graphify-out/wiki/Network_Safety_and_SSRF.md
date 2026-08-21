# Network Safety and SSRF

> 21 nodes · cohesion 0.17

## Key Concepts

- **ssrf.py** (11 connections) — `somatic/net/ssrf.py`
- **parse_host_ip()** (10 connections) — `somatic/net/ssrf.py`
- **assert_resolved_public()** (8 connections) — `somatic/net/ssrf.py`
- **is_blocked_ip()** (8 connections) — `somatic/net/ssrf.py`
- **SsrfTests** (6 connections) — `tests/test_ssrf.py`
- **_assert_model_host_allowed()** (5 connections) — `somatic/advisory/adapter.py`
- **_canonical_ip()** (5 connections) — `somatic/net/ssrf.py`
- **IPv4Address** (4 connections)
- **_parse_ipv4_alternate()** (3 connections) — `somatic/net/ssrf.py`
- **.test_loopback_http_is_not_blocked()** (3 connections) — `tests/test_ssrf.py`
- **.test_resolved_literal_private_is_rejected()** (3 connections) — `tests/test_ssrf.py`
- **.test_rfc1918_and_metadata_are_blocked()** (3 connections) — `tests/test_ssrf.py`
- **IPv6Address** (3 connections)
- **__init__.py** (2 connections) — `somatic/net/__init__.py`
- **test_ssrf.py** (2 connections) — `tests/test_ssrf.py`
- **Optional network helpers. Stdlib only. No default egress.** (1 connections) — `somatic/net/__init__.py`
- **URL safety helpers for optional network egress (stdlib only).** (1 connections) — `somatic/net/ssrf.py`
- **Parse a literal IP, including decimal/hex/octal/IPv4-mapped encodings.** (1 connections) — `somatic/net/ssrf.py`
- **True for private, link-local, metadata, multicast, and reserved addresses.** (1 connections) — `somatic/net/ssrf.py`
- **Reject hosts that resolve to a blocked address (DNS rebinding / SSRF).** (1 connections) — `somatic/net/ssrf.py`
- **SSRF helpers reject private, link-local, and metadata encodings.** (1 connections) — `tests/test_ssrf.py`

## Relationships

- [URL Safety and Redirection](URL_Safety_and_Redirection.md) (8 shared connections)
- [Advisory Model Client](Advisory_Model_Client.md) (3 shared connections)
- [CSI UDP Forwarder](CSI_UDP_Forwarder.md) (1 shared connections)

## Source Files

- `somatic/advisory/adapter.py`
- `somatic/net/__init__.py`
- `somatic/net/ssrf.py`
- `tests/test_ssrf.py`

## Audit Trail

- EXTRACTED: 65 (79%)
- INFERRED: 17 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*