---
type: community
cohesion: 0.07
members: 88
---

# Financial Anomaly Detection

**Cohesion:** 0.07 - loosely connected
**Members:** 88 nodes

## Members
- [[AnomalyCode]] - code - src/lib/data/anomaly.ts
- [[AnomalyFlag]] - code - src/lib/data/anomaly.ts
- [[AnomalyOptions]] - code - src/lib/data/anomaly.ts
- [[DEFAULT_ROBINHOOD_FIXTURE_PATH]] - code - src/lib/data/robinhood.ts
- [[DataEnvironment]] - code - src/lib/data/types.ts
- [[DataFetch]] - code - src/lib/data/types.ts
- [[DataKind]] - code - src/lib/data/types.ts
- [[DataPoint]] - code - src/lib/data/types.ts
- [[DataQualityIssue]] - code - src/lib/data/types.ts
- [[DataQualityIssueCode]] - code - src/lib/data/types.ts
- [[DataQualitySeverity]] - code - src/lib/data/types.ts
- [[DataValidationResult]] - code - src/lib/data/types.ts
- [[DataWindowRequest]] - code - src/lib/data/types.ts
- [[DataWindowResult]] - code - src/lib/data/types.ts
- [[RobinhoodHistoryItem]] - code - src/lib/data/robinhood.ts
- [[RobinhoodPage()]] - code - src/app/robinhood/page.tsx
- [[RobinhoodPosition]] - code - src/lib/data/robinhood.ts
- [[RobinhoodSnapshot]] - code - src/lib/data/robinhood.ts
- [[anomaly.test.ts]] - code - src/lib/data/anomaly.test.ts
- [[anomaly.ts]] - code - src/lib/data/anomaly.ts
- [[callMcpToolOverStdio()]] - code - src/lib/connectors/mcp.ts
- [[completeWindow()]] - code - src/lib/data/window-validation.ts
- [[extractFinancialDatasetPoints()]] - code - src/lib/data/financial-datasets.ts
- [[extractFredObservations()]] - code - src/lib/data/fred.ts
- [[extractMassivePoints()]] - code - src/lib/data/massive.ts
- [[extractWeatherPoints()]] - code - src/lib/data/weather.ts
- [[fetchFinancialDatasetsViaMcp()]] - code - src/lib/data/financial-datasets.ts
- [[fetchFredObservations()]] - code - src/lib/data/fred.ts
- [[fetchMassiveViaMcp()]] - code - src/lib/data/massive.ts
- [[fetchOpenMeteo()]] - code - src/lib/data/weather.ts
- [[filterPointsToWindow()]] - code - src/lib/data/parse.ts
- [[financial-datasets.test.ts]] - code - src/lib/data/financial-datasets.test.ts
- [[financial-datasets.ts]] - code - src/lib/data/financial-datasets.ts
- [[findArrays()]] - code - src/lib/data/parse.ts
- [[fixture]] - code - src/lib/data/financial-datasets.ts
- [[fixture_1]] - code - src/lib/data/massive.ts
- [[flagAnomalies()]] - code - src/lib/data/anomaly.ts
- [[fred.test.ts]] - code - src/lib/data/fred.test.ts
- [[fred.ts]] - code - src/lib/data/fred.ts
- [[fredObservationsUrl()]] - code - src/lib/data/fred.ts
- [[isRecord()_4]] - code - src/lib/data/parse.ts
- [[joinPortfolioUrl()]] - code - src/lib/data/robinhood.ts
- [[jsonResponse()]] - code - src/lib/data/fred.test.ts
- [[jsonResponse()_1]] - code - src/lib/data/weather.test.ts
- [[loadFinancialDatasetsWindow()]] - code - src/lib/data/financial-datasets.ts
- [[loadFredFixture()]] - code - src/lib/data/fred.ts
- [[loadFredWindow()]] - code - src/lib/data/fred.ts
- [[loadMassiveWindow()]] - code - src/lib/data/massive.ts
- [[loadNewsFixture()]] - code - src/lib/data/news.ts
- [[loadNewsWindow()]] - code - src/lib/data/news.ts
- [[loadRobinhoodFixture()]] - code - src/lib/data/robinhood.ts
- [[loadRobinhoodSnapshot()]] - code - src/lib/data/robinhood.ts
- [[loadWeatherFixture()]] - code - src/lib/data/weather.ts
- [[loadWeatherWindow()]] - code - src/lib/data/weather.ts
- [[looksLikePoint()]] - code - src/lib/data/parse.ts
- [[massive.test.ts]] - code - src/lib/data/massive.test.ts
- [[massive.ts]] - code - src/lib/data/massive.ts
- [[news.test.ts]] - code - src/lib/data/news.test.ts
- [[news.ts]] - code - src/lib/data/news.ts
- [[page.tsx_7]] - code - src/app/robinhood/page.tsx
- [[parse.ts]] - code - src/lib/data/parse.ts
- [[parseHistory()]] - code - src/lib/data/robinhood.ts
- [[parseLatLon()]] - code - src/lib/data/weather.ts
- [[parsePosition()_1]] - code - src/lib/data/robinhood.ts
- [[parseRobinhoodBody()]] - code - src/lib/data/robinhood.ts
- [[point()]] - code - src/lib/data/anomaly.test.ts
- [[request]] - code - src/lib/data/financial-datasets.test.ts
- [[request_1]] - code - src/lib/data/fred.test.ts
- [[request_2]] - code - src/lib/data/massive.test.ts
- [[request_3]] - code - src/lib/data/news.test.ts
- [[request_5]] - code - src/lib/data/weather.test.ts
- [[request_6]] - code - src/lib/data/window-validation.test.ts
- [[robinhood.test.ts]] - code - src/lib/data/robinhood.test.ts
- [[robinhood.ts]] - code - src/lib/data/robinhood.ts
- [[sample()]] - code - src/lib/data/window-validation.test.ts
- [[sources.ts]] - code - src/lib/data/sources.ts
- [[toFredPoint()]] - code - src/lib/data/fred.ts
- [[toIsoUtc()]] - code - src/lib/data/weather.ts
- [[toMarketPoint()]] - code - src/lib/data/parse.ts
- [[toNumber()_1]] - code - src/lib/data/parse.ts
- [[toTimestamp()]] - code - src/lib/data/parse.ts
- [[types.ts_4]] - code - src/lib/data/types.ts
- [[unwrapMcpJson()_1]] - code - src/lib/data/parse.ts
- [[validateDataWindow()]] - code - src/lib/data/window-validation.ts
- [[weather.test.ts]] - code - src/lib/data/weather.test.ts
- [[weather.ts]] - code - src/lib/data/weather.ts
- [[window-validation.test.ts]] - code - src/lib/data/window-validation.test.ts
- [[window-validation.ts]] - code - src/lib/data/window-validation.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Financial_Anomaly_Detection
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_MCP JSON-RPC Transport]]
- 7 edges to [[_COMMUNITY_Market Data Actions]]
- 4 edges to [[_COMMUNITY_Risk Report Routes]]
- 3 edges to [[_COMMUNITY_Module Resolution Utilities]]
- 3 edges to [[_COMMUNITY_OHLC Data Processing]]
- 2 edges to [[_COMMUNITY_Stack Tool Management]]
- 2 edges to [[_COMMUNITY_Connector Health Monitoring]]
- 1 edge to [[_COMMUNITY_Authentication Route Handlers]]
- 1 edge to [[_COMMUNITY_Mirofish Integration Testing]]
- 1 edge to [[_COMMUNITY_Alert Notification System]]

## Top bridge nodes
- [[callMcpToolOverStdio()]] - degree 15, connects to 4 communities
- [[financial-datasets.ts]] - degree 24, connects to 3 communities
- [[massive.ts]] - degree 24, connects to 3 communities
- [[loadFinancialDatasetsWindow()]] - degree 8, connects to 2 communities
- [[loadMassiveWindow()]] - degree 8, connects to 2 communities