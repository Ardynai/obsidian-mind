"""Stdlib BM25 lexical retrieval. No runtime ranking dependency."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

from .corpus import Passage

_TOKEN = re.compile(r"[a-z0-9]+")
_K1 = 1.5
_B = 0.75
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "in",
        "on",
        "of",
        "and",
        "or",
        "to",
        "for",
        "this",
        "that",
        "with",
        "from",
        "at",
        "by",
        "as",
        "be",
        "are",
        "was",
        "were",
        "it",
        "no",
        "not",
        "such",
    }
)


def tokenize(text: str) -> list[str]:
    return [token for token in _TOKEN.findall(str(text or "").lower()) if token not in _STOPWORDS]


def retrieve(
    corpus: tuple[Passage, ...] | list[Passage],
    query: str,
    *,
    k: int = 5,
) -> tuple[Passage, ...]:
    """Return up to ``k`` passages with BM25 score > 0, highest first."""

    documents = list(corpus)
    if not documents or k <= 0:
        return ()
    query_tokens = tokenize(query)
    if not query_tokens:
        return ()

    tokenized = [tokenize(f"{item.title} {item.text}") for item in documents]
    df: dict[str, int] = defaultdict(int)
    for tokens in tokenized:
        for term in set(tokens):
            df[term] += 1
    n_docs = len(documents)
    avgdl = sum(len(tokens) for tokens in tokenized) / n_docs
    idf = {
        term: math.log((n_docs - count + 0.5) / (count + 0.5) + 1.0) for term, count in df.items()
    }

    scored: list[tuple[float, Passage]] = []
    query_counts = Counter(query_tokens)
    for passage, tokens in zip(documents, tokenized, strict=True):
        length = len(tokens) or 1
        tf = Counter(tokens)
        score = 0.0
        for term, qtf in query_counts.items():
            term_tf = tf.get(term, 0)
            if term_tf == 0:
                continue
            denom = term_tf + _K1 * (1.0 - _B + _B * length / avgdl)
            score += idf.get(term, 0.0) * (term_tf * (_K1 + 1.0) / denom) * qtf
        if score > 0:
            scored.append((score, passage))
    scored.sort(key=lambda item: item[0], reverse=True)
    return tuple(item[1] for item in scored[:k])
