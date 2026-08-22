# Manifests

Machine-readable workflow manifests will live here after workflows are proven.

A manifest should describe:

- workflow id
- target repo or tool
- required repo-intelligence precheck
- required gates
- allowed actions
- disallowed actions
- inputs
- outputs
- success criteria
- scoring metrics
- rollback notes
- audit requirements

## Rule

Do not create a manifest for an unproven workflow unless it is clearly marked as draft.

Human-readable workflow docs come first. Manifests come after the workflow has a clear target, gate model, and scoring model.
