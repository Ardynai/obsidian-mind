# Latency Probe Worker

> 19 nodes · cohesion 0.20

## Key Concepts

- **worker.ts** (18 connections) — `src/lib/ops/worker.ts`
- **page.tsx** (11 connections) — `src/app/ops/page.tsx`
- **startHeadlessWorker()** (9 connections) — `src/lib/ops/worker.ts`
- **loadLatencySnapshot()** (8 connections) — `src/lib/ops/latency.ts`
- **OperationsPage()** (5 connections) — `src/app/ops/page.tsx`
- **ProbeOptions** (5 connections) — `src/lib/ops/latency.ts`
- **HeadlessWorkerOptions** (5 connections) — `src/lib/ops/worker.ts`
- **workerIntervalMs()** (5 connections) — `src/lib/ops/worker.ts`
- **workerRunEnabled()** (5 connections) — `src/lib/ops/worker.ts`
- **probeTimeoutMs()** (4 connections) — `src/lib/ops/latency.ts`
- **worker.test.ts** (4 connections) — `src/lib/ops/worker.test.ts`
- **run-worker.ts** (3 connections) — `src/lib/ops/run-worker.ts`
- **HeadlessWorkerHandle** (3 connections) — `src/lib/ops/worker.ts`
- **formatMs()** (2 connections) — `src/app/ops/page.tsx`
- **.tick()** (2 connections) — `src/lib/ops/worker.ts`
- **stop()** (1 connections) — `src/lib/ops/run-worker.ts`
- **.stop()** (1 connections) — `src/lib/ops/worker.ts`
- **IntervalHandle** (1 connections) — `src/lib/ops/worker.ts`
- **WorkerEnv** (1 connections) — `src/lib/ops/worker.ts`

## Relationships

- [Broker Latency Probing](Broker_Latency_Probing.md) (13 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (4 shared connections)
- [Alert Notification System](Alert_Notification_System.md) (4 shared connections)
- [Trading Blotter Panels](Trading_Blotter_Panels.md) (2 shared connections)
- [System Health Metrics](System_Health_Metrics.md) (2 shared connections)

## Source Files

- `src/app/ops/page.tsx`
- `src/lib/ops/latency.ts`
- `src/lib/ops/run-worker.ts`
- `src/lib/ops/worker.test.ts`
- `src/lib/ops/worker.ts`

## Audit Trail

- EXTRACTED: 91 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*