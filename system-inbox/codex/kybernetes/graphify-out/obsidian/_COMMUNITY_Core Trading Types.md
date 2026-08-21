---
type: community
cohesion: 0.13
members: 15
---

# Core Trading Types

**Cohesion:** 0.13 - loosely connected
**Members:** 15 nodes

## Members
- [[BacktestRun]] - code - packages/contract/index.ts
- [[DataSource]] - code - packages/contract/index.ts
- [[ExecutionMode]] - code - packages/contract/index.ts
- [[Fill]] - code - packages/contract/index.ts
- [[FynnRunMetadata]] - code - packages/contract/index.ts
- [[HealthCheck]] - code - packages/contract/index.ts
- [[Order]] - code - packages/contract/index.ts
- [[ProvenanceEvent]] - code - packages/contract/index.ts
- [[RiskPoint]] - code - packages/contract/index.ts
- [[RiskReport]] - code - packages/contract/index.ts
- [[Signal]] - code - packages/contract/index.ts
- [[Strategy]] - code - packages/contract/index.ts
- [[Tier]] - code - packages/contract/index.ts
- [[ToolStatus]] - code - packages/contract/index.ts
- [[index.ts]] - code - packages/contract/index.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Core_Trading_Types
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Fynn Risk Reporting]]
- 3 edges to [[_COMMUNITY_Tool Registry Sync]]
- 2 edges to [[_COMMUNITY_MCP JSON-RPC Transport]]
- 2 edges to [[_COMMUNITY_Remote Fynn Client]]
- 2 edges to [[_COMMUNITY_Launcher Module Dependencies]]
- 2 edges to [[_COMMUNITY_Risk Reporting Utilities]]
- 1 edge to [[_COMMUNITY_Fynn Bot Adapter]]
- 1 edge to [[_COMMUNITY_Performance Comparison UI]]

## Top bridge nodes
- [[index.ts]] - degree 29, connects to 8 communities
- [[Fill]] - degree 2, connects to 1 community
- [[FynnRunMetadata]] - degree 2, connects to 1 community
- [[Order]] - degree 2, connects to 1 community
- [[RiskPoint]] - degree 2, connects to 1 community