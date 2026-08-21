---
type: community
cohesion: 0.14
members: 27
---

# Broker Latency Probing

**Cohesion:** 0.14 - loosely connected
**Members:** 27 nodes

## Members
- [[BrokerEndpoint]] - code - src/lib/ops/latency.ts
- [[BrokerEndpointId]] - code - src/lib/ops/latency.ts
- [[DEFAULT_BROKER_ENDPOINTS]] - code - src/lib/ops/latency.ts
- [[DEFAULT_SAMPLE_PATH]] - code - src/lib/ops/latency.ts
- [[EndpointLatencySummary]] - code - src/lib/ops/latency.ts
- [[LatencySample]] - code - src/lib/ops/latency.ts
- [[OrderRoundTrip]] - code - src/lib/ops/latency.ts
- [[PercentileSummary]] - code - src/lib/ops/latency.ts
- [[actions.ts_2]] - code - src/app/ops/actions.ts
- [[elapsedMs()]] - code - src/lib/ops/latency.ts
- [[isLatencySample()]] - code - src/lib/ops/latency.ts
- [[latency.test.ts]] - code - src/lib/ops/latency.test.ts
- [[latency.ts]] - code - src/lib/ops/latency.ts
- [[latencyAuditRun()]] - code - src/lib/ops/latency.ts
- [[loadLatencySamples()]] - code - src/lib/ops/latency.ts
- [[orderCorrelationKey()]] - code - src/lib/ops/latency.ts
- [[orderRoundTripsFromEvents()]] - code - src/lib/ops/latency.ts
- [[percentile()]] - code - src/lib/ops/latency.ts
- [[persistProbeProvenance()]] - code - src/lib/ops/latency.ts
- [[probeAndRecord()]] - code - src/lib/ops/latency.ts
- [[probeBrokerEndpoints()]] - code - src/lib/ops/latency.ts
- [[probeBrokerLatencyAction()]] - code - src/app/ops/actions.ts
- [[probeOne()]] - code - src/lib/ops/latency.ts
- [[snapshotFromSamples()]] - code - src/lib/ops/latency.ts
- [[storeLatencySamples()]] - code - src/lib/ops/latency.ts
- [[summarize()_1]] - code - src/lib/ops/latency.ts
- [[tempDirs_1]] - code - src/lib/ops/latency.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Broker_Latency_Probing
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Latency Probe Worker]]
- 10 edges to [[_COMMUNITY_Safety Control Actions]]
- 2 edges to [[_COMMUNITY_Stack Tool Management]]
- 2 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 2 edges to [[_COMMUNITY_System Health Metrics]]
- 1 edge to [[_COMMUNITY_Authentication Route Handlers]]
- 1 edge to [[_COMMUNITY_Ledger Memory Reservations]]

## Top bridge nodes
- [[latency.ts]] - degree 39, connects to 5 communities
- [[actions.ts_2]] - degree 6, connects to 3 communities
- [[probeBrokerLatencyAction()]] - degree 4, connects to 2 communities
- [[latency.test.ts]] - degree 11, connects to 1 community
- [[probeAndRecord()]] - degree 10, connects to 1 community