# Safety Gate Contract

The safety gate evaluates workflow intent, inputs, artifacts, evidence, provider permissions, and output language before a run advances or produces a report.

Phase 1A defines request and response contracts only. It does not implement policy logic.

## Request Object

A safety request should include:

- `id`
- `schema_version`
- `workflow_id`
- `run_id`
- `mode`
- `stage_id`
- `requested_action`
- `domain`: `general-research`, `health-research`, `lab-research`, `sensor-research`, `fabric-ingest`, or `mixed`.
- `inputs`: input ids, sensitivity, and declared consent or license state.
- `providers`: provider refs, classes, capabilities, and permissions.
- `evidence_refs`: evidence ids available to support claims.
- `artifacts`: artifacts under review.
- `claims`: draft claims or report statements to check.
- `pack_refs`: Fabric packs involved, if any.
- `requested_outputs`: report, catalog, lab plan, sensor dataset, or model output targets.

## Check Families

The `checks_requested` array should use explicit check ids:

- `medical-boundary`: verifies research and decision-support language only.
- `dangerous-protocol`: checks for unsafe lab, biological, chemical, physical, or operational instructions.
- `unsupported-claim`: checks whether claims exceed available evidence.
- `evidence-sufficiency`: checks minimum evidence and provenance requirements.
- `code-pack-risk`: checks executable pack quarantine, permissions, signatures, and enablement.
- `human-review-required`: determines whether a qualified human must review before use.
- `privacy-consent`: checks personal, patient, sensor, and baseline graph consent boundaries.
- `license-gate`: checks pack, dataset, document, and model license constraints.

## Response Object

A safety response should include:

- `id`
- `request_id`
- `schema_version`
- `decision`: `allow`, `warn`, `require-human-review`, or `block`.
- `checks`: one result per requested check.
- `required_actions`: actions that must happen before proceeding.
- `blocked_actions`: actions that must not proceed.
- `human_review`: review requirement, reviewer qualifications, and due-before state.
- `language_constraints`: terms or claims that must be removed or bounded.
- `evidence_requirements`: missing or insufficient evidence.
- `audit`: timestamps, policy version, and provider id.

## Medical Boundary

Health-related workflows must be bounded to research, decision support, safety-gated reports, and human review. Safety responses should block or require revision when draft outputs claim diagnosis, treatment, cure, emergency triage, or replacement of clinicians.

The safety gate may allow a report packet only when it preserves limitations, uncertainty, evidence links, and review state.

## Dangerous Protocol Boundary

Lab-facing workflows should distinguish:

- Literature or planning discussion.
- Manual protocol drafts for human review.
- Simulation outputs.
- Real-world lab actions.

Real-world lab actions require explicit operator approval and may require institutional, biosafety, chemical safety, procurement, or cloud-lab review.

## Code Pack Risk

Executable packs must stay quarantined until verified and explicitly enabled. The safety gate should consider:

- Manifest hash verification.
- Ed25519 signature state.
- Publisher trust state.
- License gate state.
- Requested permission scopes.
- Network, filesystem, lab, sensor, and export capabilities.

## Outcomes

- `allow`: proceed without additional gate action.
- `warn`: proceed only with warnings preserved in artifacts.
- `require-human-review`: stop publication, real-world action, or use until review is complete.
- `block`: do not proceed without changing the workflow, inputs, provider permissions, claims, or pack state.
