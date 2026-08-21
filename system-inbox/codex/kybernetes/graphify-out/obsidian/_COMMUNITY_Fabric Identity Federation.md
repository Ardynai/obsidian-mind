---
type: community
cohesion: 0.12
members: 25
---

# Fabric Identity Federation

**Cohesion:** 0.12 - loosely connected
**Members:** 25 nodes

## Members
- [[AuthenticatedFabricPeer]] - code - src/lib/fabric/federation.ts
- [[CLOSED_FEDERATION_NAMESPACES]] - code - src/lib/fabric/federation.ts
- [[FabricAuditEvent]] - code - src/lib/fabric/federation.ts
- [[FabricCaEnvelope]] - code - src/lib/fabric/federation.ts
- [[FabricDefaultEnvelope]] - code - src/lib/fabric/federation.ts
- [[FabricEnvelopeBase]] - code - src/lib/fabric/federation.ts
- [[FabricEnvelopeKind]] - code - src/lib/fabric/federation.ts
- [[FabricIdentity]] - code - src/lib/fabric/federation.ts
- [[FabricPayloadEnvelope]] - code - src/lib/fabric/federation.ts
- [[FabricRoute]] - code - src/lib/fabric/federation.ts
- [[FabricSecureDropEnvelope]] - code - src/lib/fabric/federation.ts
- [[FabricSendOptions]] - code - src/lib/fabric/federation.ts
- [[FabricSendResult]] - code - src/lib/fabric/federation.ts
- [[createFabricFederationPeerFromEnv()]] - code - src/lib/fabric/federation.ts
- [[createPeerPublisher()]] - code - src/lib/fabric/federation.ts
- [[didArrayFromUnknown()]] - code - src/lib/fabric/federation.ts
- [[ed25519SeedPkcs8Prefix]] - code - src/lib/fabric/federation.ts
- [[federation.ts]] - code - src/lib/fabric/federation.ts
- [[loadAllowlistFromRegistryOrEnv()]] - code - src/lib/fabric/federation.ts
- [[loadFabricIdentityFromEnv()]] - code - src/lib/fabric/federation.ts
- [[parseFabricKeyring()]] - code - src/lib/fabric/federation.ts
- [[parsePeerKeysJson()]] - code - src/lib/fabric/federation.ts
- [[parsePeerPublishersFromEnv()]] - code - src/lib/fabric/federation.ts
- [[peerEntriesToPublishers()]] - code - src/lib/fabric/federation.ts
- [[peerKeyFromUnknown()]] - code - src/lib/fabric/federation.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Fabric_Identity_Federation
SORT file.name ASC
```

## Connections to other communities
- 17 edges to [[_COMMUNITY_Fabric Envelope Validation]]
- 12 edges to [[_COMMUNITY_Fabric Federation Protocol]]
- 10 edges to [[_COMMUNITY_Fabric Audit Sinks]]
- 6 edges to [[_COMMUNITY_Secure Drop Encryption]]
- 1 edge to [[_COMMUNITY_Registry Task Transport]]

## Top bridge nodes
- [[federation.ts]] - degree 61, connects to 5 communities
- [[loadFabricIdentityFromEnv()]] - degree 4, connects to 2 communities
- [[peerKeyFromUnknown()]] - degree 4, connects to 2 communities
- [[createFabricFederationPeerFromEnv()]] - degree 6, connects to 1 community
- [[parsePeerPublishersFromEnv()]] - degree 5, connects to 1 community