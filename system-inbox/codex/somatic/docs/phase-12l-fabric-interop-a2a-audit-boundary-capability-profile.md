# Phase 12L Fabric Interop And A2A Audit-Boundary Capability Profile

Phase 12L is a non-executing metadata-only capability profile for future fabric
interop and A2A audit boundaries. It records possible future labels for shared
fabric pack awareness, connector scan compatibility, MessageCodec seam
consumption, plaintext JSON default expectations, decode-to-audit requirements,
A2A handshake awareness, agent-protocol/MCP interop awareness, Locus candidate
surfaces, and Secure Drop UI consumer candidates.

This phase is docs, contracts, fixtures, and tests only. It does not implement
runtime messaging, codecs, A2A transport, MCP server or client behavior, Secure
Drop send/receive, crypto, credential loading, vault/env/secret access, provider
or model execution, network calls, filesystem autoscan, connector or pack
installation, pack registration, cross-repo mutation, active grants, or
real-mode authorization.

Somatic remains standalone-first and independently usable. Future Locus or
content-fabric interop may consume shared contracts, but those integrations are
optional and cannot replace Somatic's own standalone path.

## Contract

- `profile_kind: phase-12l-fabric-interop-a2a-audit-boundary-capability-profile`
- `fabric_interop_a2a_audit_profile_contract_version: 1`
- `source_phase_range: 12A-12K,evidence-sensor-fabric-safety-boundaries`
- `capability_phase: fabric-interop-a2a-audit-boundary-profile-only`
- `authorization_status: not-authorized`
- `grant_status: no-grant`
- `runtime_stage: not-implemented`
- `fabric_interop_status: metadata-only`
- `message_codec_status: not-implemented`
- `a2a_transport_status: not-implemented`
- `mcp_interop_status: not-implemented`
- `secure_drop_status: consumer-boundary-only`
- `credential_policy: phase-h-vault-reference-only`
- `opaque_traffic_allowed: false`
- `untrusted_content_executable: false`
- `cross_repo_mutation_allowed: false`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`

## Future Fabric Capability Labels

The capability labels are metadata only:

- `fabric-pack-scan-aware`
- `connector-scan-compatible`
- `message-codec-seam-consumer`
- `plaintext-json-default`
- `decode-to-audit-required`
- `opaque-traffic-rejected`
- `a2a-handshake-aware`
- `capability-advertisement-aware`
- `codec-negotiation-aware`
- `keyring-did-identity-aware`
- `phase-h-gated`
- `agent-protocol-mcp-interop-aware`
- `locus-fusion-target-candidate`
- `locus-agent-expose-consumer-candidate`
- `secure-drop-ui-consumer-candidate`

These labels do not mean fabric, connector, pack, codec, A2A, MCP, Fusion, or
Secure Drop behavior is installed, enabled, configured, approved, authorized,
ready, or executable from Somatic.

## Forbidden Or Out-Of-Scope Labels

The forbidden labels are metadata-only denial markers:

- `no-bundled-agpl-codec`
- `no-glossopetrae-vendoring`
- `no-st3gg-vendoring`
- `no-covert-channel`
- `no-opaque-message-acting`
- `no-secret-in-pack`
- `no-secret-in-log`
- `no-secret-in-ipc`
- `no-secret-in-audit`
- `no-agent-invoked-secure-drop`
- `no-automation-invoked-secure-drop`
- `no-untrusted-content-execution`

## Required Future Gates

- shared-fabric-contract-review
- message-codec-contract-review
- decode-to-audit-policy-review
- a2a-handshake-contract-review
- phase-h-vault-boundary-review
- mcp-agent-protocol-interop-review
- secure-drop-user-initiation-review
- connector-pack-static-gate-review
- cross-repo-mutation-denial-review
- jules-security-fabric-safety-review

## Boundary Statements

Plaintext JSON default and decode-to-audit are future fabric requirements only.
Phase 12L implements no MessageCodec, transport, MCP runtime, or audit writer.

Secure Drop remains a user-initiated content-fabric boundary only; no agent or
automation invocation is allowed.

## Validation Stance

Validation fails closed on missing fields, unsupported versions, unknown fields,
unsafe/private values, URLs, tokenized URLs, API keys, env vars, vault access,
secret access, provider calls, model execution, network calls, crypto, transport,
runtime adapters, connector install, pack registration, MCP serving or client
use, filesystem autoscan, opaque traffic, covert channels, bundled AGPL codecs,
GLOSSOPETRAE vendoring, ST3GG vendoring, embedded secrets, active grants,
cross-repo mutation, real-mode authorization, and Secure Drop agent or
automation invocation claims.
