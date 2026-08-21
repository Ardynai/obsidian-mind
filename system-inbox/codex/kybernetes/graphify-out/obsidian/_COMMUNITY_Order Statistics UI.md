---
type: community
cohesion: 1.00
members: 1
---

# Order Statistics UI

**Cohesion:** 1.00 - tightly connected
**Members:** 1 nodes

## Members
- [[UI Screenshot Operations Cockpit with Order Round-trip Stats]] - image - docs/assets/dt1-ops-cockpit.png

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Order_Statistics_UI
SORT file.name ASC
```
