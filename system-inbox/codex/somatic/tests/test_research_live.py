"""Live literature lookup stays off by default and never hits the network in CI."""

from __future__ import annotations

import json
import unittest

from somatic.consent import ConsentLedger
from somatic.research.live import live_enabled, retrieve_live
from somatic.research.loop import run_research_loop
from somatic.safety.core import ConsentRequiredError


class LiveResearchTests(unittest.TestCase):
    def test_live_env_defaults_off(self):
        self.assertFalse(live_enabled({}))
        self.assertTrue(live_enabled({"SOMATIC_RESEARCH_LIVE": "1"}))
        self.assertFalse(live_enabled({"SOMATIC_RESEARCH_LIVE": "0"}))

    def test_retrieve_live_uses_injected_fetch_and_binds_abstracts(self):
        payload = {
            "resultList": {
                "result": [
                    {
                        "pmid": "123",
                        "title": "Fixture magnesium review",
                        "abstractText": (
                            "Magnesium intake was associated with sleep quality in this fixture."
                        ),
                        "pubYear": "2020",
                        "doi": "10.1000/fixture",
                        "pubType": "review",
                    }
                ]
            }
        }

        def fetch(_url: str) -> bytes:
            return json.dumps(payload).encode("utf-8")

        passages = retrieve_live("magnesium sleep", k=5, fetch=fetch)
        self.assertEqual(len(passages), 1)
        self.assertEqual(passages[0].id, "epmc:123")
        self.assertIn("Magnesium", passages[0].text)
        self.assertTrue(passages[0].url.startswith("https://doi.org/"))

    def test_retrieve_live_empty_on_fetch_failure(self):
        def fetch(_url: str) -> bytes:
            raise TimeoutError("no network in tests")

        self.assertEqual(retrieve_live("magnesium", fetch=fetch), ())

    def test_live_path_still_requires_consent(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            run_research_loop(ledger, "magnesium")

    def test_http_host_not_allowlisted_is_empty_not_raised(self):
        from somatic.net.ssrf import UnsafeUrlError
        from somatic.research import live as live_mod

        def fetch(url: str) -> bytes:
            raise UnsafeUrlError("host is not allowlisted")

        self.assertEqual(live_mod.retrieve_live("query", fetch=fetch), ())


if __name__ == "__main__":
    unittest.main()
