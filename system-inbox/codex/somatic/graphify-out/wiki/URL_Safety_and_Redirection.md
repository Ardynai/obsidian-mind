# URL Safety and Redirection

> 10 nodes · cohesion 0.33

## Key Concepts

- **UnsafeUrlError** (13 connections) — `somatic/net/ssrf.py`
- **_http_get()** (7 connections) — `somatic/research/live.py`
- **LiveResearchError** (7 connections) — `somatic/research/live.py`
- **_NoRedirectHandler** (5 connections) — `somatic/research/live.py`
- **split_http_url()** (4 connections) — `somatic/net/ssrf.py`
- **assert_host_allowlisted()** (3 connections) — `somatic/net/ssrf.py`
- **.test_non_http_scheme_rejected()** (3 connections) — `tests/test_ssrf.py`
- **.redirect_request()** (2 connections) — `somatic/research/live.py`
- **Raised when a URL is not safe to request.** (1 connections) — `somatic/net/ssrf.py`
- **Live lookup failed closed (caller should fall back to offline corpus).** (1 connections) — `somatic/research/live.py`

## Relationships

- [Network Safety and SSRF](Network_Safety_and_SSRF.md) (8 shared connections)
- [Live Literature Research](Live_Literature_Research.md) (6 shared connections)
- [Lexical Retrieval and Claims](Lexical_Retrieval_and_Claims.md) (2 shared connections)

## Source Files

- `somatic/net/ssrf.py`
- `somatic/research/live.py`
- `tests/test_ssrf.py`

## Audit Trail

- EXTRACTED: 22 (48%)
- INFERRED: 24 (52%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*