---
type: community
cohesion: 1.00
members: 1
---

# Latency Telemetry UI

**Cohesion:** 1.00 - tightly connected
**Members:** 1 nodes

## Members
- [[UI Screenshot Operations Dashboard with Latency Telemetry]] - image - docs/assets/b7-after-ops.png

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Latency_Telemetry_UI
SORT file.name ASC
```
