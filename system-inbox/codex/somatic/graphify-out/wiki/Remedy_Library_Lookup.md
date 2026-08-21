# Remedy Library Lookup

> 24 nodes · cohesion 0.11

## Key Concepts

- **lookup_remedy()** (14 connections) — `somatic/remedy/library.py`
- **RemedyLibraryTests** (8 connections) — `tests/test_remedy_library.py`
- **library.py** (7 connections) — `somatic/remedy/library.py`
- **RemedyEntry** (7 connections) — `somatic/remedy/library.py`
- **RemedyReport** (6 connections) — `somatic/remedy/library.py`
- **_remedy()** (5 connections) — `somatic/cli/main.py`
- **_grade_for_claim()** (4 connections) — `somatic/remedy/library.py`
- **test_remedy_library.py** (4 connections) — `tests/test_remedy_library.py`
- **.test_requires_remedy_library_consent()** (4 connections) — `tests/test_remedy_library.py`
- **_cap_grade()** (3 connections) — `somatic/remedy/library.py`
- **.test_bound_entry_never_exceeds_limited_and_cites_passages()** (3 connections) — `tests/test_remedy_library.py`
- **.test_unknown_topic_is_honest_null_none_grade()** (3 connections) — `tests/test_remedy_library.py`
- **__init__.py** (2 connections) — `somatic/remedy/__init__.py`
- **_isolate_consent()** (2 connections) — `tests/test_remedy_library.py`
- **.test_cli_lookup()** (2 connections) — `tests/test_remedy_library.py`
- **Consent-gated evidence-graded remedy library (informational).** (1 connections) — `somatic/remedy/__init__.py`
- **Evidence-graded informational remedy library. Default grade NONE.** (1 connections) — `somatic/remedy/library.py`
- **Folk-remedy surface never inflates above LIMITED.** (1 connections) — `somatic/remedy/library.py`
- **One citation-bound library row. Grade defaults to NONE when unbound.** (1 connections) — `somatic/remedy/library.py`
- **Look up a remedy topic against the offline corpus. Requires REMEDY_LIBRARY.** (1 connections) — `somatic/remedy/library.py`
- **.to_dict()** (1 connections) — `somatic/remedy/library.py`
- **.to_dict()** (1 connections) — `somatic/remedy/library.py`
- **Tests for the evidence-graded informational remedy library.** (1 connections) — `tests/test_remedy_library.py`
- **.test_dependencies_stay_empty()** (1 connections) — `tests/test_remedy_library.py`

## Relationships

- [Consent Ledger Management](Consent_Ledger_Management.md) (9 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (4 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (4 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (3 shared connections)
- [Lexical Retrieval and Claims](Lexical_Retrieval_and_Claims.md) (2 shared connections)
- [Citation Binding and Grading](Citation_Binding_and_Grading.md) (1 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/remedy/__init__.py`
- `somatic/remedy/library.py`
- `tests/test_remedy_library.py`

## Audit Trail

- EXTRACTED: 63 (76%)
- INFERRED: 20 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*