---
type: community
cohesion: 1.00
members: 2
---

# Alert Status Dashboard

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[Alerts Documentation]] - document - docs/how-it-works/alerts.md
- [[UI screenshot of the Alert Status dashboard]] - image - docs/assets/m1-alert-status.png

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Alert_Status_Dashboard
SORT file.name ASC
```
