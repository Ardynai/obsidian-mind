---
type: community
cohesion: 0.11
members: 35
---

# OHLC Data Processing

**Cohesion:** 0.11 - loosely connected
**Members:** 35 nodes

## Members
- [[GapAssessment]] - code - src/lib/data/ohlc.ts
- [[OhlcDataQualityIssue]] - code - src/lib/data/ohlc.ts
- [[OhlcDataQualityIssueCode]] - code - src/lib/data/ohlc.ts
- [[OhlcDataQualitySeverity]] - code - src/lib/data/ohlc.ts
- [[OhlcValidationOptions]] - code - src/lib/data/ohlc.ts
- [[OhlcValidationResult]] - code - src/lib/data/ohlc.ts
- [[ParsedTimeframe]] - code - src/lib/data/ohlc.ts
- [[alignToInterval()]] - code - src/lib/data/ohlc.ts
- [[alpacaBars]] - code - src/lib/data/ohlc.test.ts
- [[assessMissingBusinessSessions()]] - code - src/lib/data/ohlc.ts
- [[assessMissingIntervals()]] - code - src/lib/data/ohlc.ts
- [[assessMissingMarketIntervals()]] - code - src/lib/data/ohlc.ts
- [[exchangeLocalMinuteToUtc()]] - code - src/lib/data/ohlc.ts
- [[extractOhlcBars()]] - code - src/lib/data/ohlc.ts
- [[fetchAlpacaOhlcViaMcp()]] - code - src/lib/data/ohlc.ts
- [[fetchYfinanceOhlc()]] - code - src/lib/data/ohlc.ts
- [[findBarArrays()]] - code - src/lib/data/ohlc.ts
- [[isOhlcBar()]] - code - src/lib/data/ohlc.ts
- [[isRecord()_3]] - code - src/lib/data/ohlc.ts
- [[loadFixtureBars()]] - code - src/lib/data/ohlc.ts
- [[loadOhlcWindow()]] - code - src/lib/data/ohlc.ts
- [[marketOffsetFormatter]] - code - src/lib/data/ohlc.ts
- [[marketSession()]] - code - src/lib/data/ohlc.ts
- [[minuteBars()]] - code - src/lib/data/ohlc.test.ts
- [[ohlc.test.ts]] - code - src/lib/data/ohlc.test.ts
- [[ohlc.ts]] - code - src/lib/data/ohlc.ts
- [[parseTimeframe()]] - code - src/lib/data/ohlc.ts
- [[qualityBar()]] - code - src/lib/data/ohlc.test.ts
- [[startOfUtcDay()]] - code - src/lib/data/ohlc.ts
- [[toBar()]] - code - src/lib/data/ohlc.ts
- [[toNumber()]] - code - src/lib/data/ohlc.ts
- [[toRequiredNumber()]] - code - src/lib/data/ohlc.ts
- [[unwrapMcpJson()]] - code - src/lib/data/ohlc.ts
- [[utcDay()]] - code - src/lib/data/ohlc.ts
- [[validateOhlcWindow()]] - code - src/lib/data/ohlc.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/OHLC_Data_Processing
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Market Data Actions]]
- 6 edges to [[_COMMUNITY_Trading Stack Paths]]
- 6 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 5 edges to [[_COMMUNITY_Strategy Backtesting UI]]
- 5 edges to [[_COMMUNITY_Order Simulation Testing]]
- 4 edges to [[_COMMUNITY_MCP JSON-RPC Transport]]
- 3 edges to [[_COMMUNITY_Financial Anomaly Detection]]
- 2 edges to [[_COMMUNITY_Fynn Adapter Conformance]]
- 2 edges to [[_COMMUNITY_Safety Control Actions]]
- 2 edges to [[_COMMUNITY_Risk Report Routes]]
- 1 edge to [[_COMMUNITY_Connector Health Monitoring]]

## Top bridge nodes
- [[ohlc.ts]] - degree 54, connects to 11 communities
- [[loadOhlcWindow()]] - degree 14, connects to 4 communities
- [[ohlc.test.ts]] - degree 10, connects to 2 communities
- [[validateOhlcWindow()]] - degree 10, connects to 2 communities
- [[extractOhlcBars()]] - degree 7, connects to 1 community