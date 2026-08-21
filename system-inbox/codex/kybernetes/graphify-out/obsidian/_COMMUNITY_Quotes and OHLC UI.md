---
type: community
cohesion: 1.00
members: 1
---

# Quotes and OHLC UI

**Cohesion:** 1.00 - tightly connected
**Members:** 1 nodes

## Members
- [[UI screenshot of the quotes and OHLC data panel after loading data]] - image - docs/assets/locus-after-quotes.png

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Quotes_and_OHLC_UI
SORT file.name ASC
```
