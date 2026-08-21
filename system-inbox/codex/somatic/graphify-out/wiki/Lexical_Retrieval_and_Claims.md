# Lexical Retrieval and Claims

> 16 nodes · cohesion 0.15

## Key Concepts

- **BoundClaim** (8 connections) — `somatic/research/bind.py`
- **Passage** (8 connections) — `somatic/research/corpus.py`
- **retrieve.py** (6 connections) — `somatic/research/retrieve.py`
- **retrieve()** (6 connections) — `somatic/research/retrieve.py`
- **bind_claims()** (5 connections) — `somatic/research/bind.py`
- **load_corpus()** (5 connections) — `somatic/research/corpus.py`
- **.test_unbound_claim_is_dropped()** (4 connections) — `tests/test_research_loop.py`
- **.test_bm25_ranks_magnesium_passage_first()** (3 connections) — `tests/test_research_loop.py`
- **tokenize()** (2 connections) — `somatic/research/retrieve.py`
- **.to_dict()** (1 connections) — `somatic/research/bind.py`
- **A user-facing claim that cites only retrieved passages.** (1 connections) — `somatic/research/bind.py`
- **Keep claims whose every cite resolves; drop the rest.** (1 connections) — `somatic/research/bind.py`
- **.to_dict()** (1 connections) — `somatic/research/corpus.py`
- **One retrieved text unit that may be cited by id.** (1 connections) — `somatic/research/corpus.py`
- **Stdlib BM25 lexical retrieval. No runtime ranking dependency.** (1 connections) — `somatic/research/retrieve.py`
- **Return up to ``k`` passages with BM25 score > 0, highest first.** (1 connections) — `somatic/research/retrieve.py`

## Relationships

- [Citation Binding and Grading](Citation_Binding_and_Grading.md) (7 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (5 shared connections)
- [Remedy Library Lookup](Remedy_Library_Lookup.md) (2 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (2 shared connections)
- [URL Safety and Redirection](URL_Safety_and_Redirection.md) (2 shared connections)

## Source Files

- `somatic/research/bind.py`
- `somatic/research/corpus.py`
- `somatic/research/retrieve.py`
- `tests/test_research_loop.py`

## Audit Trail

- EXTRACTED: 36 (67%)
- INFERRED: 18 (33%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*