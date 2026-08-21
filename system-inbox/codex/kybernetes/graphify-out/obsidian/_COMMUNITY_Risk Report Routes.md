---
type: community
cohesion: 0.27
members: 19
---

# Risk Report Routes

**Cohesion:** 0.27 - loosely connected
**Members:** 19 nodes

## Members
- [[GET()_1]] - code - src/app/reports/compare/route.ts
- [[GET()_2]] - code - src/app/reports/run/[runId]/route.ts
- [[ReportFormat]] - code - src/lib/reports/index.ts
- [[authenticationErrorResponse()]] - code - src/lib/auth/index.ts
- [[loadConnectors()]] - code - src/lib/connectors/index.ts
- [[parseReportFormat()]] - code - src/lib/reports/index.ts
- [[reportContentType()]] - code - src/lib/reports/index.ts
- [[reportExtension()]] - code - src/lib/reports/index.ts
- [[reportResponse()]] - code - src/app/reports/compare/route.ts
- [[reportResponse()_1]] - code - src/app/reports/run/[runId]/route.ts
- [[riskThresholdsFromEnv()]] - code - src/lib/ledger/compare.ts
- [[route.ts_2]] - code - src/app/reports/compare/route.ts
- [[route.ts_3]] - code - src/app/reports/run/[runId]/route.ts
- [[safeName()]] - code - src/app/reports/compare/route.ts
- [[safeName()_1]] - code - src/app/reports/run/[runId]/route.ts
- [[selectedRunIds()]] - code - src/app/reports/compare/route.ts
- [[serializeReport()]] - code - src/lib/reports/index.ts
- [[textResponse()_1]] - code - src/app/reports/compare/route.ts
- [[textResponse()_2]] - code - src/app/reports/run/[runId]/route.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Risk_Report_Routes
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_Risk Reporting Utilities]]
- 8 edges to [[_COMMUNITY_Database Policy Management]]
- 6 edges to [[_COMMUNITY_Safety Control Actions]]
- 6 edges to [[_COMMUNITY_Stack Tool Management]]
- 6 edges to [[_COMMUNITY_Connector Health Monitoring]]
- 6 edges to [[_COMMUNITY_Launcher Module Dependencies]]
- 5 edges to [[_COMMUNITY_Risk Threshold Comparison]]
- 4 edges to [[_COMMUNITY_Performance Comparison UI]]
- 4 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 4 edges to [[_COMMUNITY_Financial Anomaly Detection]]
- 3 edges to [[_COMMUNITY_Authentication Route Handlers]]
- 3 edges to [[_COMMUNITY_Connector Management Actions]]
- 2 edges to [[_COMMUNITY_Ledger Memory Reservations]]
- 2 edges to [[_COMMUNITY_OHLC Data Processing]]
- 2 edges to [[_COMMUNITY_System Health Metrics]]
- 1 edge to [[_COMMUNITY_MCP JSON-RPC Transport]]

## Top bridge nodes
- [[route.ts_2]] - degree 29, connects to 10 communities
- [[route.ts_3]] - degree 26, connects to 10 communities
- [[loadConnectors()]] - degree 24, connects to 8 communities
- [[GET()_1]] - degree 17, connects to 6 communities
- [[GET()_2]] - degree 16, connects to 6 communities