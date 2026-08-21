# Content-Addressed Artifact Verification

> 17 nodes · cohesion 0.17

## Key Concepts

- **cas.py** (6 connections) — `somatic/provenance/cas.py`
- **address_record()** (5 connections) — `somatic/provenance/cas.py`
- **verify_file()** (5 connections) — `somatic/provenance/cas.py`
- **verify_record()** (4 connections) — `somatic/provenance/cas.py`
- **BenchAndProvenanceTests** (4 connections) — `tests/test_bench_and_provenance.py`
- **.test_cli_bench_and_verify()** (4 connections) — `tests/test_bench_and_provenance.py`
- **test_bench_and_provenance.py** (4 connections) — `tests/test_bench_and_provenance.py`
- **hash_payload()** (3 connections) — `somatic/provenance/cas.py`
- **.test_address_and_verify_round_trip()** (3 connections) — `tests/test_bench_and_provenance.py`
- **.test_ripasudil_sandbox_bench_scores()** (3 connections) — `tests/test_bench_and_provenance.py`
- **_evidence_verify()** (3 connections) — `somatic/cli/main.py`
- **__init__.py** (2 connections) — `somatic/provenance/__init__.py`
- **_isolate()** (2 connections) — `tests/test_bench_and_provenance.py`
- **Content-addressed evidence artifacts: hash is the id; verify from disk.** (1 connections) — `somatic/provenance/cas.py`
- **Return ``payload`` with a content id equal to its canonical SHA-256.** (1 connections) — `somatic/provenance/cas.py`
- **Content-addressed provenance helpers (stdlib). P2P distribution stays disabled.** (1 connections) — `somatic/provenance/__init__.py`
- **Sandbox bench + content-addressed evidence verify.** (1 connections) — `tests/test_bench_and_provenance.py`

## Relationships

- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (4 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (2 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/provenance/__init__.py`
- `somatic/provenance/cas.py`
- `tests/test_bench_and_provenance.py`

## Audit Trail

- EXTRACTED: 42 (81%)
- INFERRED: 10 (19%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*