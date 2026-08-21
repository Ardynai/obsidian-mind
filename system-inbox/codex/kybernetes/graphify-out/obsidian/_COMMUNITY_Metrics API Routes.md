---
type: community
cohesion: 0.83
members: 4
---

# Metrics API Routes

**Cohesion:** 0.83 - tightly connected
**Members:** 4 nodes

## Members
- [[GET()]] - code - src/app/metrics/route.ts
- [[renderKybernetesMetrics()]] - code - src/lib/metrics.ts
- [[route.test.ts_1]] - code - src/app/metrics/route.test.ts
- [[route.ts_1]] - code - src/app/metrics/route.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Metrics_API_Routes
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_System Health Metrics]]
- 1 edge to [[_COMMUNITY_Safety Control Actions]]

## Top bridge nodes
- [[renderKybernetesMetrics()]] - degree 6, connects to 2 communities
- [[route.ts_1]] - degree 4, connects to 1 community