# Broker Latency Probing

> 27 nodes · cohesion 0.14

## Key Concepts

- **latency.ts** (39 connections) — `src/lib/ops/latency.ts`
- **latency.test.ts** (11 connections) — `src/lib/ops/latency.test.ts`
- **probeAndRecord()** (10 connections) — `src/lib/ops/latency.ts`
- **actions.ts** (6 connections) — `src/app/ops/actions.ts`
- **orderRoundTripsFromEvents()** (5 connections) — `src/lib/ops/latency.ts`
- **persistProbeProvenance()** (5 connections) — `src/lib/ops/latency.ts`
- **probeBrokerEndpoints()** (5 connections) — `src/lib/ops/latency.ts`
- **snapshotFromSamples()** (5 connections) — `src/lib/ops/latency.ts`
- **probeBrokerLatencyAction()** (4 connections) — `src/app/ops/actions.ts`
- **loadLatencySamples()** (4 connections) — `src/lib/ops/latency.ts`
- **probeOne()** (4 connections) — `src/lib/ops/latency.ts`
- **percentile()** (3 connections) — `src/lib/ops/latency.ts`
- **storeLatencySamples()** (3 connections) — `src/lib/ops/latency.ts`
- **summarize()** (3 connections) — `src/lib/ops/latency.ts`
- **elapsedMs()** (2 connections) — `src/lib/ops/latency.ts`
- **EndpointLatencySummary** (2 connections) — `src/lib/ops/latency.ts`
- **isLatencySample()** (2 connections) — `src/lib/ops/latency.ts`
- **latencyAuditRun()** (2 connections) — `src/lib/ops/latency.ts`
- **LatencySample** (2 connections) — `src/lib/ops/latency.ts`
- **orderCorrelationKey()** (2 connections) — `src/lib/ops/latency.ts`
- **PercentileSummary** (2 connections) — `src/lib/ops/latency.ts`
- **BrokerEndpoint** (1 connections) — `src/lib/ops/latency.ts`
- **BrokerEndpointId** (1 connections) — `src/lib/ops/latency.ts`
- **DEFAULT_BROKER_ENDPOINTS** (1 connections) — `src/lib/ops/latency.ts`
- **DEFAULT_SAMPLE_PATH** (1 connections) — `src/lib/ops/latency.ts`
- *... and 2 more nodes in this community*

## Relationships

- [Latency Probe Worker](Latency_Probe_Worker.md) (13 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (10 shared connections)
- [Stack Tool Management](Stack_Tool_Management.md) (2 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (2 shared connections)
- [System Health Metrics](System_Health_Metrics.md) (2 shared connections)
- [Authentication Route Handlers](Authentication_Route_Handlers.md) (1 shared connections)
- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (1 shared connections)

## Source Files

- `src/app/ops/actions.ts`
- `src/lib/ops/latency.test.ts`
- `src/lib/ops/latency.ts`

## Audit Trail

- EXTRACTED: 124 (98%)
- INFERRED: 3 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*