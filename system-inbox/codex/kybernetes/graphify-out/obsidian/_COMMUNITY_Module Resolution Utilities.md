---
type: community
cohesion: 0.15
members: 21
---

# Module Resolution Utilities

**Cohesion:** 0.15 - loosely connected
**Members:** 21 nodes

## Members
- [[.close()]] - code - src/lib/connectors/mcp.ts
- [[.handleLine()]] - code - src/lib/connectors/mcp.ts
- [[.read()]] - code - src/lib/connectors/mcp.ts
- [[.rejectPending()]] - code - src/lib/connectors/mcp.ts
- [[.request()]] - code - src/lib/connectors/mcp.ts
- [[.start()]] - code - src/lib/connectors/mcp.ts
- [[SOURCE_EXTENSIONS]] - code - scripts/ts-resolve.mjs
- [[StdioJsonRpcClient]] - code - src/lib/connectors/mcp.ts
- [[contractEntry]] - code - scripts/ts-resolve.mjs
- [[defaultHaltRetryDelay()]] - code - src/lib/safety/controls.ts
- [[getToolCount()]] - code - src/lib/connectors/mcp.ts
- [[isDirectory()]] - code - scripts/ts-resolve.mjs
- [[isFile()]] - code - scripts/ts-resolve.mjs
- [[load()]] - code - scripts/ts-resolve.mjs
- [[mapSpecifier()]] - code - scripts/ts-resolve.mjs
- [[probeMcpOverStdio()]] - code - src/lib/connectors/mcp.ts
- [[repoRoot]] - code - scripts/ts-resolve.mjs
- [[resolve()]] - code - scripts/ts-resolve.mjs
- [[resolveFile()]] - code - scripts/ts-resolve.mjs
- [[srcRoot]] - code - scripts/ts-resolve.mjs
- [[ts-resolve.mjs]] - code - scripts/ts-resolve.mjs

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Module_Resolution_Utilities
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_MCP JSON-RPC Transport]]
- 3 edges to [[_COMMUNITY_Financial Anomaly Detection]]
- 2 edges to [[_COMMUNITY_Alert Notification System]]
- 1 edge to [[_COMMUNITY_Trading Stack Paths]]
- 1 edge to [[_COMMUNITY_Market Dashboard Panels]]
- 1 edge to [[_COMMUNITY_Connector Health Monitoring]]
- 1 edge to [[_COMMUNITY_Tool Launcher Containment]]
- 1 edge to [[_COMMUNITY_Market Data Context]]
- 1 edge to [[_COMMUNITY_Broker Credential Controls]]

## Top bridge nodes
- [[probeMcpOverStdio()]] - degree 7, connects to 3 communities
- [[.close()]] - degree 6, connects to 3 communities
- [[StdioJsonRpcClient]] - degree 9, connects to 2 communities
- [[.start()]] - degree 7, connects to 2 communities
- [[resolve()]] - degree 8, connects to 1 community