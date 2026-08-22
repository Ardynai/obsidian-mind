"""Loopback-only origin and Host checks for the local UI bridge."""

from __future__ import annotations

from urllib.parse import urlparse

LOOPBACK_NAMES = frozenset({"127.0.0.1", "localhost"})
ALLOWED_SCHEMES = frozenset({"http", "https"})


def hostname_from_host_header(value: str) -> str:
    """Return the hostname from an HTTP Host header (no port)."""

    text = str(value or "").strip()
    if not text:
        return ""
    if text.startswith("["):
        end = text.find("]")
        if end == -1:
            return ""
        return text[1:end].lower()
    return text.split(":", 1)[0].lower()


def is_loopback_hostname(hostname: str) -> bool:
    """True when ``hostname`` is a loopback name we will serve."""

    return str(hostname or "").strip().lower() in LOOPBACK_NAMES


def origin_is_loopback(origin: str) -> bool:
    """True when Origin is absent or a loopback http(s) origin.

    Missing Origin is allowed for same-machine tools (the CLI test client).
    A present non-loopback Origin is always refused.
    """

    text = str(origin or "").strip()
    if not text:
        return True
    parsed = urlparse(text)
    host = (parsed.hostname or "").lower()
    return parsed.scheme in ALLOWED_SCHEMES and is_loopback_hostname(host)


def bind_host_is_allowed(host: str) -> bool:
    """True when the requested bind address is loopback-only."""

    return is_loopback_hostname(host)
