---
type: community
cohesion: 0.67
members: 3
---

# Market Data UI

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[UI Quotes and News Panels with OHLC Data]] - image - docs/assets/flash-after-quotes.png
- [[UI Terminal Overview with Watchlist, Chart, and Quotes]] - image - docs/assets/flash-after-overview.png
- [[UI Watchlist and Heatmap with AAPL Session Data]] - image - docs/assets/flash-after-watchlist.png

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Market_Data_UI
SORT file.name ASC
```
