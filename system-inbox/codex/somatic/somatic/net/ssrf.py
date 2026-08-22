"""URL safety helpers for optional network egress (stdlib only)."""

from __future__ import annotations

import ipaddress
import socket
import urllib.parse

__all__ = [
    "UnsafeUrlError",
    "assert_host_allowlisted",
    "assert_resolved_public",
    "is_blocked_ip",
    "parse_host_ip",
    "split_http_url",
]


class UnsafeUrlError(ValueError):
    """Raised when a URL is not safe to request."""


_METADATA_V4 = ipaddress.IPv4Address("169.254.169.254")
_METADATA_HOSTS = frozenset({"metadata.google.internal", "metadata", "metadata.google.com"})
_LINK_LOCAL_V4 = ipaddress.IPv4Network("169.254.0.0/16")


def split_http_url(url: str) -> urllib.parse.SplitResult:
    parsed = urllib.parse.urlsplit(str(url or "").strip())
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrlError("URL must use http or https")
    if not (parsed.hostname or "").strip():
        raise UnsafeUrlError("URL must include a host")
    return parsed


def parse_host_ip(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """Parse a literal IP, including decimal/hex/octal/IPv4-mapped encodings."""

    text = host.strip().lower()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    if "%" in text:
        text = text.split("%", 1)[0]
    try:
        parsed: ipaddress.IPv4Address | ipaddress.IPv6Address = ipaddress.ip_address(text)
    except ValueError:
        parsed_alt = _parse_ipv4_alternate(text)
        if parsed_alt is None:
            return None
        parsed = parsed_alt
    return _canonical_ip(parsed)


def is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address | None) -> bool:
    """True for private, link-local, metadata, multicast, and reserved addresses.

    Loopback is allowed (local vLLM / Ollama).
    """

    if ip is None:
        return False
    if ip.is_loopback:
        return False
    if ip == _METADATA_V4:
        return True
    if isinstance(ip, ipaddress.IPv4Address) and ip in _LINK_LOCAL_V4:
        return True
    if ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved:
        return True
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return is_blocked_ip(ip.ipv4_mapped)
    return False


def assert_host_allowlisted(host: str, allowed: frozenset[str]) -> None:
    name = host.strip().lower().rstrip(".")
    if name not in allowed:
        raise UnsafeUrlError(f"host is not allowlisted: {name}")


def assert_resolved_public(host: str) -> None:
    """Reject hosts that resolve to a blocked address (DNS rebinding / SSRF)."""

    ip = parse_host_ip(host)
    if ip is not None:
        if is_blocked_ip(ip):
            raise UnsafeUrlError("URL host is not allowed")
        return
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeUrlError(f"could not resolve host: {host}") from exc
    if not infos:
        raise UnsafeUrlError(f"could not resolve host: {host}")
    for info in infos:
        address = info[4][0]
        try:
            resolved = ipaddress.ip_address(address)
        except ValueError:
            continue
        if is_blocked_ip(_canonical_ip(resolved)):
            raise UnsafeUrlError("URL host resolved to a private or metadata address")


def _canonical_ip(
    parsed: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    if isinstance(parsed, ipaddress.IPv6Address):
        if parsed.ipv4_mapped is not None:
            return parsed.ipv4_mapped
        if parsed.sixtofour is not None:
            return parsed.sixtofour
    return parsed


def _parse_ipv4_alternate(host: str) -> ipaddress.IPv4Address | None:
    try:
        if host.startswith("0x"):
            return ipaddress.IPv4Address(int(host, 16))
        if host.isdigit():
            return ipaddress.IPv4Address(int(host, 10))
    except ValueError:
        return None
    if "." not in host:
        return None
    parts = host.split(".")
    if not 1 <= len(parts) <= 4:
        return None
    nums: list[int] = []
    for part in parts:
        try:
            if part.startswith("0x"):
                nums.append(int(part, 16))
            elif len(part) > 1 and part.startswith("0") and all(ch in "01234567" for ch in part):
                nums.append(int(part, 8))
            else:
                nums.append(int(part, 10))
        except ValueError:
            return None
    widths = {1: (32,), 2: (8, 24), 3: (8, 8, 16), 4: (8, 8, 8, 8)}[len(nums)]
    packed = 0
    for value, width in zip(nums, widths, strict=True):
        if value < 0 or value >= 1 << width:
            return None
        packed = (packed << width) | value
    try:
        return ipaddress.IPv4Address(packed)
    except ValueError:
        return None
