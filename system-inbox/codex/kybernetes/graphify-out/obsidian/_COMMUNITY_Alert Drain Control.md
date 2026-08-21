---
type: community
cohesion: 1.00
members: 2
---

# Alert Drain Control

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[start-alert-drain.d.mts]] - code - scripts/start-alert-drain.d.mts
- [[stop()]] - code - scripts/start-alert-drain.d.mts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Alert_Drain_Control
SORT file.name ASC
```
