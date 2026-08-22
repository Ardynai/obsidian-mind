"""Optional live literature lookup. Stdlib urllib. Off unless env-enabled.

CI and default runs stay on the offline fixture corpus. This module never
sends sensor payloads; it queries public literature APIs with the question
string only.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

from somatic.net.ssrf import (
    UnsafeUrlError,
    assert_host_allowlisted,
    assert_resolved_public,
    split_http_url,
)

from .corpus import Passage

LIVE_ENV = "SOMATIC_RESEARCH_LIVE"
MAX_RESPONSE_BYTES = 262_144
DEFAULT_TIMEOUT_SECONDS = 8
ALLOWED_HOSTS = frozenset(
    {
        "www.ebi.ac.uk",
        "europepmc.org",
        "www.europepmc.org",
        "eutils.ncbi.nlm.nih.gov",
        "www.ncbi.nlm.nih.gov",
        "clinicaltrials.gov",
        "www.clinicaltrials.gov",
        "api.clinicaltrials.gov",
        "api.biorxiv.org",
        "api.medrxiv.org",
    }
)
EUROPE_PMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

FetchFn = Callable[[str], bytes]


class LiveResearchError(RuntimeError):
    """Live lookup failed closed (caller should fall back to offline corpus)."""


def live_enabled(env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(LIVE_ENV, "")).strip().lower() in {"1", "true", "yes", "on"}


def retrieve_live(
    query: str,
    *,
    k: int = 5,
    fetch: FetchFn | None = None,
) -> tuple[Passage, ...]:
    """Search Europe PMC and return passages. Empty on failure or miss."""

    q = " ".join(str(query or "").split())
    if not q or k <= 0:
        return ()
    try:
        raw = (fetch or _http_get)(_europe_pmc_url(q, k=k))
    except (LiveResearchError, UnsafeUrlError, TimeoutError, OSError, urllib.error.URLError):
        return ()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return ()
    return _passages_from_europe_pmc(payload, limit=k)


def _europe_pmc_url(query: str, *, k: int) -> str:
    params = urllib.parse.urlencode(
        {
            "query": query,
            "format": "json",
            "resultType": "core",
            "pageSize": str(min(max(k, 1), 10)),
        }
    )
    return f"{EUROPE_PMC_SEARCH}?{params}"


def _http_get(url: str) -> bytes:
    parsed = split_http_url(url)
    if parsed.scheme != "https":
        raise UnsafeUrlError("live literature lookup requires https")
    host = (parsed.hostname or "").lower().rstrip(".")
    assert_host_allowlisted(host, ALLOWED_HOSTS)
    assert_resolved_public(host)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "somatic-local-research/1"},
        method="GET",
    )
    opener = urllib.request.build_opener(_NoRedirectHandler)
    try:
        with opener.open(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:  # nosec B310
            return response.read(MAX_RESPONSE_BYTES + 1)[:MAX_RESPONSE_BYTES]
    except urllib.error.HTTPError as exc:
        raise LiveResearchError(f"literature HTTP {exc.code}") from exc


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802
        raise LiveResearchError("literature HTTP redirects are not followed")


def _passages_from_europe_pmc(payload: Any, *, limit: int) -> tuple[Passage, ...]:
    if not isinstance(payload, dict):
        return ()
    listing = payload.get("resultList")
    if not isinstance(listing, dict):
        return ()
    rows = listing.get("result")
    if not isinstance(rows, list):
        return ()
    passages: list[Passage] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        abstract = str(row.get("abstractText") or "").strip()
        title = str(row.get("title") or "").strip()
        if not abstract:
            continue
        source_id = str(row.get("pmid") or row.get("pmcid") or row.get("id") or "").strip()
        if not source_id:
            continue
        passage_id = f"epmc:{source_id}"
        if passage_id in seen:
            continue
        seen.add(passage_id)
        year_raw = row.get("pubYear")
        try:
            year = int(year_raw) if year_raw not in (None, "") else None
        except (TypeError, ValueError):
            year = None
        doi = str(row.get("doi") or "").strip()
        url = f"https://doi.org/{doi}" if doi else ""
        passages.append(
            Passage(
                id=passage_id,
                title=title or passage_id,
                text=abstract,
                source_id=source_id,
                year=year,
                study_type=str(row.get("pubType") or "unknown").split(";")[0].strip().lower()
                or "unknown",
                url=url,
            )
        )
        if len(passages) >= limit:
            break
    return tuple(passages)
