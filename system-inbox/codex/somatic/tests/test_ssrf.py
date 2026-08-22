"""SSRF helpers reject private, link-local, and metadata encodings."""

from __future__ import annotations

import unittest

from somatic.net.ssrf import UnsafeUrlError, is_blocked_ip, parse_host_ip, split_http_url


class SsrfTests(unittest.TestCase):
    def test_loopback_http_is_not_blocked(self):
        ip = parse_host_ip("127.0.0.1")
        self.assertIsNotNone(ip)
        self.assertFalse(is_blocked_ip(ip))

    def test_rfc1918_and_metadata_are_blocked(self):
        blocked = (
            "10.1.2.3",
            "192.168.1.10",
            "172.16.0.1",
            "169.254.169.254",
            "169.254.1.1",
            "2852039166",
            "0xa9fea9fe",
        )
        for host in blocked:
            with self.subTest(host=host):
                ip = parse_host_ip(host)
                self.assertTrue(is_blocked_ip(ip), host)

    def test_non_http_scheme_rejected(self):
        with self.assertRaises(UnsafeUrlError):
            split_http_url("file:///etc/passwd")

    def test_resolved_literal_private_is_rejected(self):
        from somatic.net.ssrf import assert_resolved_public

        with self.assertRaises(UnsafeUrlError):
            assert_resolved_public("192.168.1.10")


if __name__ == "__main__":
    unittest.main()
