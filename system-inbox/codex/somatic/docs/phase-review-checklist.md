# Phase Review Checklist

Use this checklist before closing any implementation phase.

## Scope

- [ ] The phase matches the roadmap and does not add unapproved runtime scope.
- [ ] No private harness dependency was introduced.
- [ ] Public interfaces are documented before implementation details.
- [ ] Examples can run without private services unless clearly labeled otherwise.
- [ ] Sensor-evidence release summaries align with the provider manifest and docs when provider metadata changes.

## Safety

- [ ] Clinical language stays within research, decision support, safety-gated reports, and human review.
- [ ] No diagnosis, treatment, cure, emergency triage, or clinician replacement claims were added.
- [ ] Lab workflows require human approval before real-world actions.
- [ ] Sensor workflows document consent, privacy, and retention assumptions.
- [ ] Public CSI examples run without private services, package downloads, hardware access, live capture, or network capture.
- [ ] CSI evidence-pack examples export sanitized metadata only.
- [ ] Parser CLI examples are labeled as local parser-contract reports, not portable public exports.
- [ ] Tournament CSI readiness metadata is not a ranking, Elo, bracket, score-field, winner-selection, or candidate-scoring input.
- [ ] Reports include evidence, assumptions, uncertainty, and review state.

## Security

- [ ] No secrets or credentials were committed.
- [ ] Local state and generated artifacts are ignored.
- [ ] Code packs remain quarantined until explicitly enabled.
- [ ] Hash and signature verification paths have tests when implemented.
- [ ] Data and code pack boundaries remain separate.
- [ ] CSI portable public artifacts do not export fixture refs, unsafe refs, absolute paths, source IDs, raw CSI arrays, signal values, secrets, or clinical claims.
- [ ] Sensor-evidence summary artifacts do not expose fixture filenames, private paths, source IDs, provider/parser internals, secret-like fields, raw measurement terms, or care-related claims.

## Quality

- [ ] Schemas and manifests have validation tests when implemented.
- [ ] Mock providers cover adapter contracts.
- [ ] Documentation matches the source tree.
- [ ] The repository can be verified without package downloads unless the phase explicitly adds dependencies.

## Release Evidence

- [ ] `git status` is clean except for intentional changes before commit.
- [ ] Sanity checks passed.
- [ ] Commit hash is recorded.
- [ ] Any known issues are documented.
