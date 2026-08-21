---
type: community
cohesion: 0.10
members: 32
---

# System Health Metrics

**Cohesion:** 0.10 - loosely connected
**Members:** 32 nodes

## Members
- [[ConnectorStatusLabel]] - code - src/lib/metrics.ts
- [[DatabaseStatus]] - code - src/db/client.ts
- [[LatencySnapshot]] - code - src/lib/ops/latency.ts
- [[MetricsBundle]] - code - src/lib/metrics.ts
- [[MetricsSnapshot]] - code - src/lib/metrics.ts
- [[ReportFormatLabel]] - code - src/lib/metrics.ts
- [[ReportScope]] - code - src/lib/metrics.ts
- [[collectConnectorMetrics()]] - code - src/lib/metrics.ts
- [[collectDatabaseMetrics()]] - code - src/lib/metrics.ts
- [[collectKybernetesMetrics()]] - code - src/lib/metrics.ts
- [[collectLatencyMetrics()]] - code - src/lib/metrics.ts
- [[collectLedgerMetrics()]] - code - src/lib/metrics.ts
- [[connectorStatus()]] - code - src/lib/metrics.ts
- [[connectorStatuses]] - code - src/lib/metrics.ts
- [[emptyRunSummary()]] - code - src/lib/metrics.ts
- [[getKybernetesMetrics()]] - code - src/lib/metrics.ts
- [[getKybernetesMetricsRegistry()]] - code - src/lib/metrics.ts
- [[isReportFormat()]] - code - src/lib/metrics.ts
- [[isReportScope()]] - code - src/lib/metrics.ts
- [[lastRunDurationSeconds()]] - code - src/lib/metrics.ts
- [[loadMetricsSnapshot()]] - code - src/lib/metrics.ts
- [[metrics.ts]] - code - src/lib/metrics.ts
- [[metricsGlobal]] - code - src/lib/metrics.ts
- [[missingEnvVarCount()]] - code - src/lib/metrics.ts
- [[reportExportLabel()]] - code - src/lib/metrics.ts
- [[reportFormats]] - code - src/lib/metrics.ts
- [[reportScopes]] - code - src/lib/metrics.ts
- [[resetGauges()]] - code - src/lib/metrics.ts
- [[round()]] - code - src/lib/metrics.ts
- [[runModes]] - code - src/lib/metrics.ts
- [[timestampMilliseconds()]] - code - src/lib/metrics.ts
- [[timestampSeconds()]] - code - src/lib/metrics.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/System_Health_Metrics
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Safety Control Actions]]
- 4 edges to [[_COMMUNITY_Metrics API Routes]]
- 4 edges to [[_COMMUNITY_Database Policy Management]]
- 3 edges to [[_COMMUNITY_MCP JSON-RPC Transport]]
- 2 edges to [[_COMMUNITY_Risk Report Routes]]
- 2 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 2 edges to [[_COMMUNITY_Broker Latency Probing]]
- 2 edges to [[_COMMUNITY_Latency Probe Worker]]
- 1 edge to [[_COMMUNITY_Connector Health Monitoring]]
- 1 edge to [[_COMMUNITY_Ledger Memory Reservations]]

## Top bridge nodes
- [[metrics.ts]] - degree 48, connects to 10 communities
- [[loadMetricsSnapshot()]] - degree 6, connects to 4 communities
- [[MetricsSnapshot]] - degree 6, connects to 2 communities
- [[collectKybernetesMetrics()]] - degree 9, connects to 1 community
- [[getKybernetesMetrics()]] - degree 4, connects to 1 community