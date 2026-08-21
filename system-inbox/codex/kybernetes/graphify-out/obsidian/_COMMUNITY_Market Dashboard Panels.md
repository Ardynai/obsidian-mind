---
type: community
cohesion: 0.21
members: 23
---

# Market Dashboard Panels

**Cohesion:** 0.21 - loosely connected
**Members:** 23 nodes

## Members
- [[CalendarPanel()]] - code - src/components/terminal/calendar-panel.tsx
- [[ChartPanel()]] - code - src/components/terminal/chart-panel.tsx
- [[HeatmapPanel()]] - code - src/components/terminal/heatmap-panel.tsx
- [[NewsPanel()]] - code - src/components/terminal/news-panel.tsx
- [[NewsTicker()]] - code - src/components/terminal/news-ticker.tsx
- [[QuotesPanel()]] - code - src/components/terminal/quotes-panel.tsx
- [[SECTOR]] - code - src/components/terminal/heatmap-panel.tsx
- [[SignedNum()]] - code - src/components/terminal/signed-num.tsx
- [[TickNum()]] - code - src/components/terminal/signed-num.tsx
- [[WatchlistPanel()]] - code - src/components/terminal/watchlist-panel.tsx
- [[WatchlistTicker]] - code - src/lib/terminal/quotes.ts
- [[flashClass()]] - code - src/components/terminal/signed-num.tsx
- [[formatSigned()]] - code - src/lib/terminal/quotes.ts
- [[heatmap-panel.tsx]] - code - src/components/terminal/heatmap-panel.tsx
- [[lastChange()]] - code - src/lib/terminal/quotes.ts
- [[news-ticker.tsx]] - code - src/components/terminal/news-ticker.tsx
- [[quotes.test.ts]] - code - src/lib/terminal/quotes.test.ts
- [[quotes.ts]] - code - src/lib/terminal/quotes.ts
- [[signed-num.tsx]] - code - src/components/terminal/signed-num.tsx
- [[tickerFromChartSymbol()]] - code - src/lib/terminal/quotes.ts
- [[useMarketLive()]] - code - src/components/terminal/market-live-context.tsx
- [[useTerminalSymbol()]] - code - src/lib/terminal/symbol-context.tsx
- [[useTickFlash()]] - code - src/components/terminal/signed-num.tsx

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Market_Dashboard_Panels
SORT file.name ASC
```

## Connections to other communities
- 47 edges to [[_COMMUNITY_Trading Blotter Panels]]
- 14 edges to [[_COMMUNITY_Market Data Context]]
- 12 edges to [[_COMMUNITY_Chart Layout Configuration]]
- 7 edges to [[_COMMUNITY_Market Data Actions]]
- 6 edges to [[_COMMUNITY_Terminal Workspace UI]]
- 1 edge to [[_COMMUNITY_Terminal Layout Persistence]]
- 1 edge to [[_COMMUNITY_OHLC Tape Indicators]]
- 1 edge to [[_COMMUNITY_Module Resolution Utilities]]

## Top bridge nodes
- [[useMarketLive()]] - degree 21, connects to 4 communities
- [[useTerminalSymbol()]] - degree 19, connects to 4 communities
- [[quotes.ts]] - degree 16, connects to 4 communities
- [[ChartPanel()]] - degree 7, connects to 4 communities
- [[heatmap-panel.tsx]] - degree 20, connects to 3 communities