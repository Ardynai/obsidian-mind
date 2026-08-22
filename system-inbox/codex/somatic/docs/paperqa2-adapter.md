# PaperQA2 Adapter Scaffold

Phase 5B adds a disabled-by-default PaperQA2 literature provider scaffold behind
Somatic's `LiteratureProvider` shape. It does not install PaperQA2, import it at
module import time, call APIs, fetch papers, build indexes, or send user data to
external services.

## Files

- Adapter module: `somatic/providers/paperqa2.py`
- Source inspection: `docs/paperqa2-source-inspection.md`
- Placeholder fixture: `fixtures/providers/paperqa2-provider-placeholder.json`
- Mock config fixture: `fixtures/providers/paperqa2-provider-mock-config.json`
- Tests: `tests/test_paperqa2_provider_scaffold.py`

## Runtime Boundary

`PaperQA2ProviderConfig` defaults to:

- `enabled = False`
- `mode = "mock"`
- `package_name = "paperqa"`
- `allow_external_calls = False`
- `require_explicit_consent = True`

`PaperQA2LiteratureProvider.is_available()` uses `importlib.util.find_spec` to
check whether the optional `paperqa` package is available. The provider module
itself imports only the Python standard library and Somatic-owned literature
dataclasses.

Mock mode is deterministic and local. It returns fixed
`LiteratureDocument` records and evidence-record drafts derived from Somatic
fixture metadata and the inspected PaperQA2 commit.

Real mode is fail-closed in Phase 5B:

- If `paperqa` is unavailable, real mode raises `PaperQA2OptionalDependencyError`.
- If `paperqa` is available, real mode raises `PaperQA2RuntimeNotEnabledError`
  because real search, indexing, and evidence extraction are future work.

## Provider Surface

The scaffold exposes:

- `provider_id`
- `capabilities`
- `is_available()`
- `validate_config()`
- `search(LiteratureQuery)`
- `extract_evidence(list[LiteratureDocument])`
- `retrieve_literature_context(LiteratureQuery | str)`

The Somatic-owned boundary remains `LiteratureQuery`,
`LiteratureDocument`, and evidence-record drafts. PaperQA2 concepts such as
`PaperSearch`, `GatherEvidence`, `GenerateAnswer`, `Docs`, and index reuse are
documented for future mapping but are not imported or executed.

## Doctor Output

`python -m somatic doctor` reports:

- PaperQA2 provider: scaffolded, disabled by default
- PaperQA2 optional dependency: available or unavailable

This is a local availability check only. It does not import PaperQA2, run
PaperQA2 code, call APIs, or enable a real provider.

## Data And Consent

No user health data, patient data, private notes, documents, or corpus contents
should be sent to PaperQA2 or any external literature provider unless a future
workflow explicitly configures that provider and records consent, data locality,
credential, and safety-review boundaries.

## Future Real Adapter Work

A future phase can map PaperQA2's API after adding an explicit optional install
note or extra and fake-backed tests for real-mode boundaries. That work should
still avoid making PaperQA2 the workflow owner. The likely mapping is:

- `PaperSearch` and directory/index search into `LiteratureProvider.search`
- `GatherEvidence` contexts into Somatic evidence-record drafts
- `GenerateAnswer` citations and answer text into run artifacts
- PaperQA2 index names and paper directories into explicit provider config

The basic Somatic install must continue to work without PaperQA2.
