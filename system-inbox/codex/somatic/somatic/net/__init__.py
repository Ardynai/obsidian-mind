"""Optional network helpers. Stdlib only. No default egress."""

from .ssrf import UnsafeUrlError, assert_host_allowlisted, assert_resolved_public

__all__ = ["UnsafeUrlError", "assert_host_allowlisted", "assert_resolved_public"]
