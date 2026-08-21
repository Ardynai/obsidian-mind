---
type: community
cohesion: 0.13
members: 16
---

# Registry Task Transport

**Cohesion:** 0.13 - loosely connected
**Members:** 16 nodes

## Members
- [[.connect()_1]] - code - src/lib/fabric/federation.ts
- [[.connect()]] - code - src/lib/fabric/federation.test.ts
- [[.constructor()_5]] - code - src/lib/fabric/federation.test.ts
- [[.discover()_1]] - code - src/lib/fabric/federation.ts
- [[.discover()]] - code - src/lib/fabric/federation.test.ts
- [[.emitTask()]] - code - src/lib/fabric/federation.test.ts
- [[.on()_1]] - code - src/lib/fabric/federation.ts
- [[.on()]] - code - src/lib/fabric/federation.test.ts
- [[.register()_1]] - code - src/lib/fabric/federation.ts
- [[.register()]] - code - src/lib/fabric/federation.test.ts
- [[.sendTaskResult()_1]] - code - src/lib/fabric/federation.ts
- [[.sendTaskResult()]] - code - src/lib/fabric/federation.test.ts
- [[.sendTaskToPeer()_1]] - code - src/lib/fabric/federation.ts
- [[.sendTaskToPeer()]] - code - src/lib/fabric/federation.test.ts
- [[FakeRegistry]] - code - src/lib/fabric/federation.test.ts
- [[RegistryTransport]] - code - src/lib/fabric/federation.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Registry_Task_Transport
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Fabric Audit Sinks]]
- 1 edge to [[_COMMUNITY_Fabric Identity Federation]]

## Top bridge nodes
- [[RegistryTransport]] - degree 10, connects to 2 communities
- [[FakeRegistry]] - degree 10, connects to 1 community