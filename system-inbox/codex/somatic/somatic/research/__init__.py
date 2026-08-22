"""Citation-bound research loop (offline corpus by default; optional live APIs)."""

from .bind import HONEST_NULL, BoundClaim, bind_claims, claims_from_passages
from .corpus import DEFAULT_CORPUS_PATH, Passage, load_corpus
from .grade import grade_from_passages, grade_study_type
from .live import live_enabled, retrieve_live
from .loop import ResearchReport, run_research_loop
from .retrieve import retrieve, tokenize

__all__ = [
    "DEFAULT_CORPUS_PATH",
    "HONEST_NULL",
    "BoundClaim",
    "Passage",
    "ResearchReport",
    "bind_claims",
    "claims_from_passages",
    "grade_from_passages",
    "grade_study_type",
    "live_enabled",
    "load_corpus",
    "retrieve",
    "retrieve_live",
    "run_research_loop",
    "tokenize",
]
