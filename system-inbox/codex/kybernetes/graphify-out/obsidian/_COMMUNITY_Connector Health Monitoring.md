---
type: community
cohesion: 0.16
members: 23
---

# Connector Health Monitoring

**Cohesion:** 0.16 - loosely connected
**Members:** 23 nodes

## Members
- [[checkConnectorHealth()]] - code - src/lib/connectors/index.ts
- [[checkConnectorHealthAction()]] - code - src/app/page.tsx
- [[checkConnectorHealthById()]] - code - src/lib/connectors/index.ts
- [[connectorRuntimeAvailable()]] - code - src/lib/connectors/index.ts
- [[index.ts_8]] - code - src/lib/connectors/index.ts
- [[isRecord()_2]] - code - src/lib/connectors/index.ts
- [[isStatus()]] - code - src/lib/connectors/index.ts
- [[kinds]] - code - src/lib/connectors/index.ts
- [[liveProbeConnectorIds]] - code - src/lib/connectors/index.ts
- [[loadConnectorRowsFromDatabase()]] - code - src/lib/connectors/index.ts
- [[loadConnectorsWithFallback()]] - code - src/lib/connectors/index.ts
- [[loadSeedConnectors()]] - code - src/lib/connectors/index.ts
- [[missingRequiredEnvVars()]] - code - src/lib/connectors/index.ts
- [[redactEnvValues()]] - code - src/lib/connectors/index.ts
- [[safeErrorDetail()]] - code - src/lib/connectors/index.ts
- [[saveConnectorHealth()]] - code - src/lib/connectors/index.ts
- [[statuses]] - code - src/lib/connectors/index.ts
- [[toConnectorDefinition()]] - code - src/lib/connectors/index.ts
- [[toConnectorDefinitions()]] - code - src/lib/connectors/index.ts
- [[toConnectorHealth()]] - code - src/lib/connectors/index.ts
- [[toHealthJson()]] - code - src/lib/connectors/index.ts
- [[toNumberArray()]] - code - src/lib/connectors/index.ts
- [[toStringArray()]] - code - src/lib/connectors/index.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Connector_Health_Monitoring
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_MCP JSON-RPC Transport]]
- 6 edges to [[_COMMUNITY_Risk Report Routes]]
- 4 edges to [[_COMMUNITY_Stack Tool Management]]
- 4 edges to [[_COMMUNITY_Database Policy Management]]
- 3 edges to [[_COMMUNITY_Performance Comparison UI]]
- 3 edges to [[_COMMUNITY_Terminal Layout Persistence]]
- 3 edges to [[_COMMUNITY_Connector Management Actions]]
- 3 edges to [[_COMMUNITY_Trading Stack Paths]]
- 2 edges to [[_COMMUNITY_Runtime Environment Persistence]]
- 2 edges to [[_COMMUNITY_Financial Anomaly Detection]]
- 1 edge to [[_COMMUNITY_Module Resolution Utilities]]
- 1 edge to [[_COMMUNITY_OHLC Data Processing]]
- 1 edge to [[_COMMUNITY_System Health Metrics]]
- 1 edge to [[_COMMUNITY_Fabric Audit Sinks]]

## Top bridge nodes
- [[index.ts_8]] - degree 46, connects to 13 communities
- [[checkConnectorHealth()]] - degree 10, connects to 4 communities
- [[checkConnectorHealthById()]] - degree 8, connects to 3 communities
- [[loadSeedConnectors()]] - degree 5, connects to 2 communities
- [[checkConnectorHealthAction()]] - degree 3, connects to 2 communities