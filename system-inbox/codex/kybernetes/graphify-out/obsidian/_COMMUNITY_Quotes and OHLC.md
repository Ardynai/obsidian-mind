---
type: community
cohesion: 1.00
members: 1
---

# Quotes and OHLC

**Cohesion:** 1.00 - tightly connected
**Members:** 1 nodes

## Members
- [[UI Screenshot Quotes and OHLC Panel]] - image - docs/assets/live-after-quotes.png

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Quotes_and_OHLC
SORT file.name ASC
```
