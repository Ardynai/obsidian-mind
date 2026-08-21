# System Health Metrics

> 32 nodes · cohesion 0.10

## Key Concepts

- **metrics.ts** (48 connections) — `src/lib/metrics.ts`
- **collectKybernetesMetrics()** (9 connections) — `src/lib/metrics.ts`
- **loadMetricsSnapshot()** (6 connections) — `src/lib/metrics.ts`
- **MetricsSnapshot** (6 connections) — `src/lib/metrics.ts`
- **collectConnectorMetrics()** (5 connections) — `src/lib/metrics.ts`
- **collectLedgerMetrics()** (5 connections) — `src/lib/metrics.ts`
- **getKybernetesMetrics()** (4 connections) — `src/lib/metrics.ts`
- **reportExportLabel()** (4 connections) — `src/lib/metrics.ts`
- **DatabaseStatus** (3 connections) — `src/db/client.ts`
- **lastRunDurationSeconds()** (3 connections) — `src/lib/metrics.ts`
- **LatencySnapshot** (3 connections) — `src/lib/ops/latency.ts`
- **collectDatabaseMetrics()** (2 connections) — `src/lib/metrics.ts`
- **collectLatencyMetrics()** (2 connections) — `src/lib/metrics.ts`
- **connectorStatus()** (2 connections) — `src/lib/metrics.ts`
- **emptyRunSummary()** (2 connections) — `src/lib/metrics.ts`
- **getKybernetesMetricsRegistry()** (2 connections) — `src/lib/metrics.ts`
- **isReportFormat()** (2 connections) — `src/lib/metrics.ts`
- **isReportScope()** (2 connections) — `src/lib/metrics.ts`
- **missingEnvVarCount()** (2 connections) — `src/lib/metrics.ts`
- **resetGauges()** (2 connections) — `src/lib/metrics.ts`
- **timestampMilliseconds()** (2 connections) — `src/lib/metrics.ts`
- **timestampSeconds()** (2 connections) — `src/lib/metrics.ts`
- **connectorStatuses** (1 connections) — `src/lib/metrics.ts`
- **ConnectorStatusLabel** (1 connections) — `src/lib/metrics.ts`
- **MetricsBundle** (1 connections) — `src/lib/metrics.ts`
- *... and 7 more nodes in this community*

## Relationships

- [Safety Control Actions](Safety_Control_Actions.md) (7 shared connections)
- [Database Policy Management](Database_Policy_Management.md) (4 shared connections)
- [Metrics API Routes](Metrics_API_Routes.md) (4 shared connections)
- [MCP JSON-RPC Transport](MCP_JSON-RPC_Transport.md) (3 shared connections)
- [Risk Report Routes](Risk_Report_Routes.md) (2 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (2 shared connections)
- [Broker Latency Probing](Broker_Latency_Probing.md) (2 shared connections)
- [Latency Probe Worker](Latency_Probe_Worker.md) (2 shared connections)
- [Connector Health Monitoring](Connector_Health_Monitoring.md) (1 shared connections)
- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (1 shared connections)

## Source Files

- `src/db/client.ts`
- `src/lib/metrics.ts`
- `src/lib/ops/latency.ts`

## Audit Trail

- EXTRACTED: 128 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*