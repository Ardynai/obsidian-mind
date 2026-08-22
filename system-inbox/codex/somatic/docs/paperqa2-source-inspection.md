# PaperQA2 Source Inspection

Phase 5B inspected the staged PaperQA2 source read-only before adding the
Somatic adapter scaffold.

## Source

- Repo: `Future-House/paper-qa`
- Local path: `C:\AI\external-sources\somatic\paper-qa`
- Commit inspected: `d2c3c698fdf06986aa021812ab3186d3696438d8`
- License: Apache-2.0 via `LICENSE`
- Inspection actions: file reads and static search only.
- Dependencies installed: no.
- Package managers, setup scripts, model/data downloads, and APIs called: no.

## Package Shape

Top-level source files and directories include:

- `README.md`
- `LICENSE`
- `CITATION.cff`
- `pyproject.toml`
- `uv.lock`
- `docs/`
- `packages/`
- `src/`
- `tests/`

`pyproject.toml` defines package name `paper-qa`, Python `>=3.11`, and the
console entrypoint:

```toml
pqa = "paperqa.agents:main"
```

Core dependencies include `fhaviary[llm]`, `fhlmi`, `httpx`,
`httpx-aiohttp`, `numpy`, `paper-qa-pypdf`, `pybtex`,
`pydantic-settings`, `pydantic`, `rich`, `tantivy`, `tenacity`, and
`tiktoken`. Optional extras cover Docling, image support, LDP, local embedding
models, memory, Nemotron, Office files, OpenReview, PyMuPDF, Qdrant, and Zotero.

## Entrypoints And Concepts

The main CLI and API entrypoints are under `src/paperqa/agents/`:

- `paperqa.agents.__init__.py`: CLI `main()`, `ask()`, `search_query()`,
  `build_index()`, and settings helpers.
- `paperqa.agents.main`: agent query and index search orchestration.
- `paperqa.agents.search`: directory index construction and search.
- `paperqa.agents.tools`: `PaperSearch`, `GatherEvidence`, and
  `GenerateAnswer` tool classes.
- `paperqa.docs.Docs`: document collection, text chunks, vector index, add-file,
  add-url, and query paths.
- `paperqa.clients`: metadata client abstractions for services such as
  Crossref, Semantic Scholar, OpenAlex, Unpaywall, and related processors.

The README describes two primary workflows:

- CLI: `pqa ask`, `pqa search`, and `pqa index` over a local paper directory.
- Library: `from paperqa import Settings, ask`, plus async `agent_query` and
  manual `Docs` usage.

Indexes are built from `IndexSettings.paper_directory`, default to the
PaperQA home directory, and can be reused. Manifest CSV files can provide
metadata such as file path, DOI, and title to reduce metadata uncertainty.

## Dependency And Runtime Weight

PaperQA2 is a medium-to-heavy optional dependency for Somatic. Even local paper
work may involve LLM settings, embedding models, vector indexes, metadata
clients, and document parsers. The source includes direct HTTP client usage and
metadata-provider integrations, and README installation notes mention API keys
for model providers, Crossref, and Semantic Scholar for larger workflows.

The staged test suite uses pytest, VCR cassettes, stub data, and HTTP client
patching. Those patterns are useful as a signal that real integration testing
must be fake-backed or cassette/local-fixture-backed, but Somatic Phase 5B does
not import or run the PaperQA2 tests.

## Somatic Boundary Conclusions

Somatic should wrap:

- document search results as `LiteratureDocument` metadata
- gathered contexts as Somatic evidence-record drafts
- answer/citation provenance as local run artifacts
- index and corpus references as explicit provider configuration

Somatic should not adopt wholesale:

- PaperQA2's agent loop as the Somatic workflow owner
- default metadata-provider calls
- default LLM or embedding-provider configuration
- PaperQA home/index storage as a Somatic global default
- document ingestion of user health or private data without explicit
  configuration and consent
- optional extras as basic-install dependencies

The Phase 5B code therefore adds only an optional-import scaffold and
deterministic mock mode.
