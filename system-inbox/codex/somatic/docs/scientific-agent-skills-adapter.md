# Scientific Agent Skills Adapter Scaffold

Phase 5C adds a disabled-by-default `scientific-agent-skills` provider scaffold
behind Somatic's `ScienceSkillProvider` shape. It is metadata-only. It does not
install skills, import an external package, execute skill instructions, run
scanner scripts, call databases, or send user data anywhere.

## Files

- Adapter module: `somatic/providers/scientific_agent_skills.py`
- Source inspection: `docs/scientific-agent-skills-source-inspection.md`
- Placeholder fixture:
  `fixtures/providers/scientific-agent-skills-provider-placeholder.json`
- Mock config fixture:
  `fixtures/providers/scientific-agent-skills-provider-mock-config.json`
- Mock catalog fixture:
  `fixtures/providers/scientific-agent-skills-sample-catalog.json`
- Tests: `tests/test_scientific_agent_skills_provider_scaffold.py`

## Runtime Boundary

`ScientificAgentSkillsProviderConfig` defaults to:

- `enabled = False`
- `mode = "mock"`
- `package_name = "scientific_agent_skills"`
- `allow_external_calls = False`
- `allow_skill_execution = False`
- `require_explicit_consent = True`

The provider module imports only the Python standard library and Somatic-owned
dataclasses. It uses `importlib.util.find_spec` and a staged-source path check
for local availability reporting. This check does not import or execute the
staged source.

Mock mode returns deterministic local metadata for a small subset:

- `paper-lookup`
- `database-lookup`
- `medchem`
- `clinical-decision-support`
- `esm-responsible-biodesign-note`
- database connector placeholders for PubChem, ChEMBL, ClinicalTrials.gov,
  UniProt, and RCSB PDB

Real mode fails closed with `ScientificAgentSkillsRuntimeNotEnabledError`.

## Provider Surface

The scaffold exposes:

- `provider_id`
- `capabilities`
- `is_available()`
- `validate_config()`
- `lookup(SkillLookupRequest)`
- `describe(skill_id)`
- `list_skills()`
- `list_database_connectors()`
- `describe_skill(skill_id)`
- `describe_database_connector(connector_id)`
- `catalog_summary()`

There is intentionally no skill execution method in Phase 5C.

## Doctor Output

`python -m somatic doctor` reports:

- scientific-agent-skills provider: scaffolded, disabled by default
- scientific-agent-skills source: staged or not staged
- scientific-agent-skills optional dependency/source: available or unavailable
- scientific-agent-skills execution: disabled

This is a local scaffold status check only.

## Data And Consent

Future real adapters must require explicit user configuration and consent before
any external database/API connector is called. Health, patient, clinical,
genomic, biomolecular, or otherwise private data must remain local unless the
workflow explicitly configures an external connector, declares data locality,
and records consent and safety-review boundaries.

## Future Real Adapter Work

A future phase can add a static parser for staged `skills/*/SKILL.md`
frontmatter and `references/` metadata. That phase should still avoid executing
skills by default. A separate, later execution phase would need:

- explicit optional install notes
- allowlisted skills/connectors
- per-connector credentials and rate-limit handling
- clinical/health data consent gates
- safety and biosecurity review for relevant domains
- no default network execution
