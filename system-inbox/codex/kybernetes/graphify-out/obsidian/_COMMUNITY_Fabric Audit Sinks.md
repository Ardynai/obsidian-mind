---
type: community
cohesion: 0.16
members: 19
---

# Fabric Audit Sinks

**Cohesion:** 0.16 - loosely connected
**Members:** 19 nodes

## Members
- [[.record()]] - code - src/lib/fabric/federation.ts
- [[.record()_1]] - code - src/lib/fabric/federation.ts
- [[FabricAuditSink]] - code - src/lib/fabric/federation.ts
- [[FabricDeliveredContent]] - code - src/lib/fabric/federation.ts
- [[FabricFederationPeerOptions]] - code - src/lib/fabric/federation.ts
- [[MemoryFabricFederationAuditSink]] - code - src/lib/fabric/federation.ts
- [[PeerFixture]] - code - src/lib/fabric/federation.test.ts
- [[createFabricIdentityFromSeed()]] - code - src/lib/fabric/federation.ts
- [[createFixture()]] - code - src/lib/fabric/federation.test.ts
- [[createLocalTrustKeyring()]] - code - src/lib/fabric/federation.ts
- [[createPeerFixture()]] - code - src/lib/fabric/federation.test.ts
- [[federation.test.ts]] - code - src/lib/fabric/federation.test.ts
- [[isRecord()_6]] - code - src/lib/fabric/federation.test.ts
- [[mergePublishers()]] - code - src/lib/fabric/federation.ts
- [[publisherFor()]] - code - src/lib/fabric/federation.test.ts
- [[readTaskKind()]] - code - src/lib/fabric/federation.test.ts
- [[seed()]] - code - src/lib/fabric/federation.test.ts
- [[systemFor()]] - code - src/lib/fabric/federation.test.ts
- [[tempDirs]] - code - src/lib/fabric/federation.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Fabric_Audit_Sinks
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Fabric Identity Federation]]
- 2 edges to [[_COMMUNITY_Fabric Federation Protocol]]
- 2 edges to [[_COMMUNITY_Registry Task Transport]]
- 1 edge to [[_COMMUNITY_Connector Health Monitoring]]
- 1 edge to [[_COMMUNITY_Ledger Memory Reservations]]

## Top bridge nodes
- [[federation.test.ts]] - degree 18, connects to 3 communities
- [[seed()]] - degree 4, connects to 2 communities
- [[createFabricIdentityFromSeed()]] - degree 5, connects to 1 community
- [[createLocalTrustKeyring()]] - degree 5, connects to 1 community
- [[MemoryFabricFederationAuditSink]] - degree 5, connects to 1 community