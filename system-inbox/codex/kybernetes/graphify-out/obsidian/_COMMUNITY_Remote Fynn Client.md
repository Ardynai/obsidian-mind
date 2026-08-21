---
type: community
cohesion: 0.33
members: 9
---

# Remote Fynn Client

**Cohesion:** 0.33 - loosely connected
**Members:** 9 nodes

## Members
- [[.probeDescribe()]] - code - src/lib/bots/adapters/fynn.ts
- [[.probeHealth()]] - code - src/lib/bots/adapters/fynn.ts
- [[.requestJson()]] - code - src/lib/bots/adapters/fynn.ts
- [[.run()_3]] - code - src/lib/bots/adapters/fynn.ts
- [[FynnRunRequest]] - code - packages/contract/index.ts
- [[FynnRunResult]] - code - packages/contract/index.ts
- [[RemoteFynn]] - code - src/lib/bots/adapters/fynn.ts
- [[cancelResponseBody()]] - code - src/lib/bots/adapters/fynn.ts
- [[readBoundedJson()]] - code - src/lib/bots/adapters/fynn.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Remote_Fynn_Client
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Fynn Risk Reporting]]
- 6 edges to [[_COMMUNITY_Remote Response Parsing]]
- 2 edges to [[_COMMUNITY_Core Trading Types]]
- 2 edges to [[_COMMUNITY_Remote Parity Testing]]
- 1 edge to [[_COMMUNITY_Remote Smoke Testing]]
- 1 edge to [[_COMMUNITY_Fynn Bot Adapter]]
- 1 edge to [[_COMMUNITY_Mirofish Integration Testing]]

## Top bridge nodes
- [[FynnRunRequest]] - degree 6, connects to 4 communities
- [[FynnRunResult]] - degree 6, connects to 3 communities
- [[RemoteFynn]] - degree 8, connects to 2 communities
- [[.run()_3]] - degree 6, connects to 2 communities
- [[readBoundedJson()]] - degree 4, connects to 2 communities