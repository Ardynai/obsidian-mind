---
title: Somatic — Fabric Consumer Boundary
reviewer: Fable 5
last_updated: 2026-07-02
tags: [somatic, fabric, multiverse, boundary]
---

# Somatic — Fabric Consumer Boundary

Back to [[README]]. **Verdict: COMPLIANT** — Somatic does not design or reimplement fabric transport.

## The standing rule
Content-addressed / chunked / integrity-verified / resumable / multi-source **transport is complete and security-reviewed in [[Multiverse]]** (`packages/fabric-core` + `fabric-transport-d` loopback sidecar). Somatic must not rebuild it, add new transport, DHT/swarm, or P2P deps.

## Evidence Somatic is compliant
- `somatic/fabric/` (canonical, catalog, conformance, crypto, digests, fixtures, interop, keyring, manifest, pathing, signing, spec) is **purely local** metadata / content-addressing / Ed25519 signing / conformance. **0 network imports** across all of `somatic/` (verified). CodeGraph: "transport" = only `manifest.py::_validate_transport` (validates an infohash/magnet *string*) + the 12T metadata funcs.
- README's "BitTorrent/WebSeed content fabric" line is aspirational + deferred everywhere; no transport code. (Cosmetic fix: annotate it "consumed externally; not implemented in Somatic".)
- **12L** marks interop/A2A/codecs/transport out-of-scope (`PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS`).
- **12T** = readiness/intake only: names external producer, sets `future-consumer-only`, retains point-to-point, fail-closed-blocks 37 actions (`PHASE12T_BLOCKED_ACTIONS`). Designated future path = `non-js-sidecar-consumer` (loopback + local contentId re-verify) — correct for a stdlib repo.

## Must wait for the Multiverse consumer prompt (all future-gated)
`repo_specific_consumer_prompt_received` must flip true first. Only then may Somatic build: `@multiverse/fabric-core` import / any JS dep · `fabric-transport-d` sidecar calls · loopback HTTP client · bearer-token handling · runtime contentId calc/verify + local re-verify · any payload fetch/write/move · any transport runtime · retiring point-to-point.

## Do NOT
Rebuild transport · add new transport · add public DHT/swarm · add P2P deps · wire fabric before the prompt.
