---
type: community
cohesion: 0.13
members: 21
---

# Durable State Store

**Cohesion:** 0.13 - loosely connected
**Members:** 21 nodes

## Members
- [[DURABLE_STATE_REASONS]] - code - src/lib/safety/state.ts
- [[Database_3]] - code - src/lib/safety/state.ts
- [[DatabaseFactory_1]] - code - src/lib/safety/state.ts
- [[DurableKernelStateStoreOptions]] - code - src/lib/safety/state.ts
- [[FIRST_BOOT]] - code - src/lib/safety/state.test.ts
- [[FakeStateRow]] - code - src/lib/safety/state.test.ts
- [[SECOND_BOOT]] - code - src/lib/safety/state.test.ts
- [[checkedNow()_2]] - code - src/lib/safety/state.ts
- [[fakeDatabase()]] - code - src/lib/safety/state.test.ts
- [[parseDate()]] - code - src/lib/safety/state.ts
- [[parseRevision()]] - code - src/lib/safety/state.ts
- [[parseSnapshot()]] - code - src/lib/safety/state.ts
- [[parseTimestamp()]] - code - src/lib/safety/state.ts
- [[requiredString()]] - code - src/lib/safety/state.test.ts
- [[state.test.ts]] - code - src/lib/safety/state.test.ts
- [[state.ts]] - code - src/lib/safety/state.ts
- [[unavailableError()]] - code - src/lib/safety/state.ts
- [[unavailableState()]] - code - src/lib/safety/state.ts
- [[validatedRevision()]] - code - src/lib/safety/state.ts
- [[validatedState()]] - code - src/lib/safety/state.ts
- [[withDatabase()_1]] - code - src/lib/safety/state.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Durable_State_Store
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Broker Credential Controls]]
- 4 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 2 edges to [[_COMMUNITY_Database Policy Management]]
- 1 edge to [[_COMMUNITY_Broker Order Safety]]

## Top bridge nodes
- [[state.ts]] - degree 24, connects to 4 communities
- [[state.test.ts]] - degree 8, connects to 1 community
- [[unavailableState()]] - degree 3, connects to 1 community