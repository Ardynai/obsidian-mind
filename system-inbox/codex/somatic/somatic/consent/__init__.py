"""User-owned granular consent catalog and local ledger."""

from .ledger import ConsentLedger
from .scopes import (
    AI_ADVISORY,
    ANALYSIS_INSIGHT,
    AUTONOMOUS_RESEARCH,
    CONSENT_SCOPES,
    DATA_INGESTION,
    PROACTIVE_SUGGESTIONS,
    PROFESSIONAL_SHARING,
    REMEDY_LIBRARY,
    ConsentScope,
    get_scope,
    resolve_scope,
)
from .store import (
    CONSENT_PATH_ENV,
    default_consent_path,
    erase_stored_ledger,
    load_ledger,
    save_ledger,
)

__all__ = [
    "AI_ADVISORY",
    "ANALYSIS_INSIGHT",
    "AUTONOMOUS_RESEARCH",
    "CONSENT_PATH_ENV",
    "CONSENT_SCOPES",
    "ConsentLedger",
    "ConsentScope",
    "DATA_INGESTION",
    "PROACTIVE_SUGGESTIONS",
    "PROFESSIONAL_SHARING",
    "REMEDY_LIBRARY",
    "default_consent_path",
    "erase_stored_ledger",
    "get_scope",
    "load_ledger",
    "resolve_scope",
    "save_ledger",
]
