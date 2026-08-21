# OHLC Data Processing

> 35 nodes · cohesion 0.11

## Key Concepts

- **ohlc.ts** (54 connections) — `src/lib/data/ohlc.ts`
- **loadOhlcWindow()** (14 connections) — `src/lib/data/ohlc.ts`
- **ohlc.test.ts** (10 connections) — `src/lib/data/ohlc.test.ts`
- **validateOhlcWindow()** (10 connections) — `src/lib/data/ohlc.ts`
- **extractOhlcBars()** (7 connections) — `src/lib/data/ohlc.ts`
- **assessMissingMarketIntervals()** (6 connections) — `src/lib/data/ohlc.ts`
- **toBar()** (5 connections) — `src/lib/data/ohlc.ts`
- **assessMissingBusinessSessions()** (4 connections) — `src/lib/data/ohlc.ts`
- **fetchYfinanceOhlc()** (4 connections) — `src/lib/data/ohlc.ts`
- **isRecord()** (4 connections) — `src/lib/data/ohlc.ts`
- **assessMissingIntervals()** (3 connections) — `src/lib/data/ohlc.ts`
- **fetchAlpacaOhlcViaMcp()** (3 connections) — `src/lib/data/ohlc.ts`
- **findBarArrays()** (3 connections) — `src/lib/data/ohlc.ts`
- **loadFixtureBars()** (3 connections) — `src/lib/data/ohlc.ts`
- **marketSession()** (3 connections) — `src/lib/data/ohlc.ts`
- **OhlcValidationOptions** (3 connections) — `src/lib/data/ohlc.ts`
- **startOfUtcDay()** (3 connections) — `src/lib/data/ohlc.ts`
- **toNumber()** (3 connections) — `src/lib/data/ohlc.ts`
- **toRequiredNumber()** (3 connections) — `src/lib/data/ohlc.ts`
- **unwrapMcpJson()** (3 connections) — `src/lib/data/ohlc.ts`
- **alignToInterval()** (2 connections) — `src/lib/data/ohlc.ts`
- **exchangeLocalMinuteToUtc()** (2 connections) — `src/lib/data/ohlc.ts`
- **isOhlcBar()** (2 connections) — `src/lib/data/ohlc.ts`
- **OhlcDataQualityIssue** (2 connections) — `src/lib/data/ohlc.ts`
- **OhlcDataQualityIssueCode** (2 connections) — `src/lib/data/ohlc.ts`
- *... and 10 more nodes in this community*

## Relationships

- [Market Data Actions](Market_Data_Actions.md) (9 shared connections)
- [Trading Stack Paths](Trading_Stack_Paths.md) (6 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (6 shared connections)
- [Strategy Backtesting UI](Strategy_Backtesting_UI.md) (5 shared connections)
- [Order Simulation Testing](Order_Simulation_Testing.md) (5 shared connections)
- [MCP JSON-RPC Transport](MCP_JSON-RPC_Transport.md) (4 shared connections)
- [Financial Anomaly Detection](Financial_Anomaly_Detection.md) (3 shared connections)
- [Fynn Adapter Conformance](Fynn_Adapter_Conformance.md) (2 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (2 shared connections)
- [Risk Report Routes](Risk_Report_Routes.md) (2 shared connections)
- [Connector Health Monitoring](Connector_Health_Monitoring.md) (1 shared connections)

## Source Files

- `src/lib/data/ohlc.test.ts`
- `src/lib/data/ohlc.ts`

## Audit Trail

- EXTRACTED: 169 (98%)
- INFERRED: 4 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*