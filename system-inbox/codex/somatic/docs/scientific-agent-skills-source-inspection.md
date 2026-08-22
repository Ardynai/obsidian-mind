# Scientific Agent Skills Source Inspection

Phase 5C inspected the staged `K-Dense-AI/scientific-agent-skills` source
read-only before adding the Somatic provider scaffold.

## Source

- Repo: `K-Dense-AI/scientific-agent-skills`
- Local path: `C:\AI\external-sources\somatic\scientific-agent-skills`
- Commit inspected: `effb57c5699c1d400ef461a7aa80fc6693939805`
- License: MIT via `LICENSE.md`
- Inspection actions: file reads and static search only.
- Dependencies installed: no.
- Package managers, setup scripts, skill code, database calls, and APIs called: no.

## Package Shape

Top-level source files and directories include:

- `README.md`
- `LICENSE.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `pyproject.toml`
- `uv.lock`
- `docs/`
- `skills/`
- `scan_skills.py`
- `scan_pr_skills.py`

`pyproject.toml` defines a Python tooling project:

- package name: `scientific-agent-skills`
- version: `2.45.0`
- Python: `>=3.13`
- dependencies: `cisco-ai-skill-scanner`, `firecrawl-py`, `python-dotenv`
- dev dependency group: `skills-ref` from the Agent Skills reference repository

The staged checkout contains 143 `SKILL.md` files under `skills/`. The README
describes the collection as Agent Skills compatible and references 141/142
skills in different sections, so Somatic records the inspected file count rather
than treating README counts as a contract.

## Skill Format

All skills live under:

```text
skills/
  skill-name/
    SKILL.md
    references/
    scripts/
    assets/
```

Only `SKILL.md` is required. `CONTRIBUTING.md` defines the required
frontmatter:

- `name`: required and must match the parent directory.
- `description`: required and should explain what the skill does and when to use it.
- `metadata.version`: required by this repository.

Optional frontmatter includes `license`, `compatibility`, `metadata`, and
`allowed-tools`. Many staged skills include `allowed-tools: Read Write Edit Bash`,
which is a reminder that the upstream skills are executable agent instructions,
not metadata records.

## Database Connector Shape

The main database catalog is the `database-lookup` skill:

- `skills/database-lookup/SKILL.md`
- `skills/database-lookup/references/*.md`

The reference directory contains 78 database reference files, including
`pubchem.md`, `chembl.md`, `clinicaltrials.md`, `uniprot.md`, `pdb.md`,
`opentargets.md`, `cosmic.md`, `fda.md`, `zinc.md`, `materials-project.md`,
`fred.md`, `uspto.md`, and others.

The staged `paper-lookup` skill has a separate literature database catalog:

- `skills/paper-lookup/SKILL.md`
- `skills/paper-lookup/references/*.md`

Its references cover PubMed, PMC, bioRxiv, medRxiv, arXiv, OpenAlex, Crossref,
Semantic Scholar, CORE, and Unpaywall.

## Entrypoints And Usage Patterns

The repository is primarily an Agent Skills collection, not a Python runtime
library. README usage focuses on installing skills into an agent host via
Agent Skills tooling such as `npx skills add` or `gh skill install`. That
installation path is not used by Somatic Phase 5C.

The Python scripts are scanner utilities:

- `scan_skills.py`: scans all skills with Cisco AI Skill Scanner and writes
  `SECURITY.md`.
- `scan_pr_skills.py`: scans selected skill directories for PR comments.

Both scanner scripts import external scanner/runtime packages and can invoke
LLM-backed analysis. Somatic must not run them in normal tests or provider
lookup.

## Dependency And Runtime Weight

The repository itself has modest scanner dependencies, but individual skills
reference many heavy packages, public APIs, cloud systems, lab systems, and
scientific databases. Examples include RDKit, Scanpy, PyTorch Lightning,
BioPython, BioServices, OpenMM/MDAnalysis, Hugging Face, Benchling, DNAnexus,
Ginkgo Cloud Lab, OMERO, Protocols.io, Opentrons, and many public database APIs.

Because skills can instruct agents to run code, install packages, make network
requests, and write files, Somatic should treat the upstream source as a static
metadata catalog until a future phase adds explicit execution and safety gates.

## Safe Metadata Extraction Path

The safe future extraction path is:

1. Read `skills/*/SKILL.md` as plain text.
2. Parse only frontmatter fields needed for planning metadata.
3. Record optional `references/` filenames as connector hints.
4. Do not import or execute skill scripts.
5. Do not follow API instructions or make database calls.
6. Keep clinical or health-related inputs local unless the user explicitly
   configures and consents to an external connector.

Phase 5C implements only a deterministic mock subset of that catalog.
