---
type: community
cohesion: 0.20
members: 16
---

# Fabric Envelope Validation

**Cohesion:** 0.20 - loosely connected
**Members:** 16 nodes

## Members
- [[.authenticatedPeerForTask()]] - code - src/lib/fabric/federation.ts
- [[.handleRegistryTask()]] - code - src/lib/fabric/federation.ts
- [[.receiveEnvelope()]] - code - src/lib/fabric/federation.ts
- [[hasBaseEnvelope()]] - code - src/lib/fabric/federation.ts
- [[isCaEnvelope()]] - code - src/lib/fabric/federation.ts
- [[isCaPayloadEnvelope()]] - code - src/lib/fabric/federation.ts
- [[isDefaultEnvelope()]] - code - src/lib/fabric/federation.ts
- [[isEncodedPayloadEnvelope()]] - code - src/lib/fabric/federation.ts
- [[isFabricKey()]] - code - src/lib/fabric/federation.ts
- [[isFabricPublisherKeys()]] - code - src/lib/fabric/federation.ts
- [[isRecord()_7]] - code - src/lib/fabric/federation.ts
- [[isSecureDropContentAddressedContent()]] - code - src/lib/fabric/federation.ts
- [[isSecureDropDefaultContent()]] - code - src/lib/fabric/federation.ts
- [[isSecureDropFabricEnvelope()]] - code - src/lib/fabric/federation.ts
- [[parseFabricEnvelope()]] - code - src/lib/fabric/federation.ts
- [[safeErrorMessage()]] - code - src/lib/fabric/federation.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Fabric_Envelope_Validation
SORT file.name ASC
```

## Connections to other communities
- 17 edges to [[_COMMUNITY_Fabric Identity Federation]]
- 6 edges to [[_COMMUNITY_Fabric Federation Protocol]]
- 3 edges to [[_COMMUNITY_Secure Drop Encryption]]

## Top bridge nodes
- [[.receiveEnvelope()]] - degree 9, connects to 2 communities
- [[isRecord()_7]] - degree 11, connects to 1 community
- [[parseFabricEnvelope()]] - degree 7, connects to 1 community
- [[.handleRegistryTask()]] - degree 6, connects to 1 community
- [[isSecureDropFabricEnvelope()]] - degree 6, connects to 1 community