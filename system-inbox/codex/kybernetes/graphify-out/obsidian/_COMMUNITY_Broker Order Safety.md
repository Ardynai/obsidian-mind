---
type: community
cohesion: 0.06
members: 80
---

# Broker Order Safety

**Cohesion:** 0.06 - loosely connected
**Members:** 80 nodes

## Members
- [[.cancelOpenOrders()]] - code - src/lib/safety/types.ts
- [[.listPositions()]] - code - src/lib/safety/types.ts
- [[.snapshot()]] - code - src/lib/safety/gateways/paper.ts
- [[.submit()]] - code - src/lib/safety/types.ts
- [[ARMED_1]] - code - src/lib/safety/controls.test.ts
- [[ARMED_2]] - code - src/lib/safety/kernel.test.ts
- [[BrokerAck]] - code - src/lib/safety/types.ts
- [[BrokerGateway]] - code - src/lib/safety/types.ts
- [[BrokerOrder]] - code - src/lib/safety/types.ts
- [[BrokerPosition]] - code - src/lib/safety/types.ts
- [[ClientOrderIdentity]] - code - src/lib/safety/client-order-id.ts
- [[ControllableBrokerGateway]] - code - src/lib/safety/types.ts
- [[EMPTY_CONTEXT]] - code - src/lib/safety/kernel.test.ts
- [[ExecuteFlattenRequest]] - code - src/lib/safety/kernel.ts
- [[ExecuteOrderIntentRequest]] - code - src/lib/safety/kernel.ts
- [[ExecuteOrderIntentsRequest]] - code - src/lib/safety/kernel.ts
- [[ExecutionReceiptSink]] - code - src/lib/safety/kernel.ts
- [[FlattenExecutionResult]] - code - src/lib/safety/kernel.ts
- [[INTENT_1]] - code - src/lib/safety/kernel.test.ts
- [[KernelExecutionResult]] - code - src/lib/safety/kernel.ts
- [[LIMITS]] - code - src/lib/safety/kernel.test.ts
- [[NOW]] - code - src/lib/safety/gateways/paper.test.ts
- [[ORDER_4]] - code - src/lib/safety/gateways/paper.test.ts
- [[OrderIntent]] - code - src/lib/safety/types.ts
- [[OrderRateLimit]] - code - src/lib/safety/types.ts
- [[PaperGateway]] - code - src/lib/safety/gateways/paper.ts
- [[PaperGatewayOptions]] - code - src/lib/safety/gateways/paper.ts
- [[PaperGatewaySnapshot]] - code - src/lib/safety/gateways/paper.ts
- [[RiskDecision]] - code - src/lib/safety/types.ts
- [[START_2]] - code - src/lib/safety/controls.test.ts
- [[SafetyConfiguration]] - code - src/lib/safety/config.ts
- [[SafetyLimits]] - code - src/lib/safety/types.ts
- [[SafetyRiskContext]] - code - src/lib/safety/kernel.ts
- [[applyOrder()]] - code - src/lib/safety/gateways/paper.ts
- [[auditEvent()]] - code - src/lib/safety/kernel.ts
- [[brokerOrderAuditRef()]] - code - src/lib/safety/order-audit.ts
- [[cancelOpenOrders()]] - code - src/lib/safety/controls.test.ts
- [[client-order-id.test.ts]] - code - src/lib/safety/client-order-id.test.ts
- [[client-order-id.ts]] - code - src/lib/safety/client-order-id.ts
- [[cloneOrder()]] - code - src/lib/safety/gateways/paper.ts
- [[clonePositions()]] - code - src/lib/safety/gateways/paper.ts
- [[cloneRiskContext()]] - code - src/lib/safety/kernel.ts
- [[compact()_1]] - code - src/lib/safety/client-order-id.ts
- [[compactClientOrderId()]] - code - src/lib/safety/client-order-id.ts
- [[compactFlattenClientOrderId()]] - code - src/lib/safety/client-order-id.ts
- [[controls.test.ts]] - code - src/lib/safety/controls.test.ts
- [[createPaperGateway()]] - code - src/lib/safety/gateways/paper.ts
- [[decisionReason()]] - code - src/lib/safety/kernel.ts
- [[evaluate()]] - code - src/lib/safety/kernel.ts
- [[execute()]] - code - src/lib/safety/kernel.ts
- [[executeBatch()]] - code - src/lib/safety/kernel.ts
- [[executeFlatten()]] - code - src/lib/safety/kernel.ts
- [[flattenAuditRef()]] - code - src/lib/safety/kernel.ts
- [[flattenOrder()]] - code - src/lib/safety/kernel.ts
- [[ids()]] - code - src/lib/safety/controls.test.ts
- [[isNonNegativeFinite()]] - code - src/lib/safety/kernel.ts
- [[isPositiveFinite()]] - code - src/lib/safety/kernel.ts
- [[isRemoteBrokerGatewayName()]] - code - src/lib/safety/config.ts
- [[kernel.test.ts]] - code - src/lib/safety/kernel.test.ts
- [[kernel.ts]] - code - src/lib/safety/kernel.ts
- [[listPositions()]] - code - src/lib/safety/controls.test.ts
- [[maximumPermittedNotional()]] - code - src/lib/safety/kernel.ts
- [[noOpFlatten()]] - code - src/lib/safety/controls.test.ts
- [[normalizeSymbol()]] - code - src/lib/safety/kernel.ts
- [[normalizedSymbols()]] - code - src/lib/safety/kernel.ts
- [[order-audit.ts]] - code - src/lib/safety/order-audit.ts
- [[paper.test.ts]] - code - src/lib/safety/gateways/paper.test.ts
- [[paper.ts]] - code - src/lib/safety/gateways/paper.ts
- [[parseBrokerOrderAuditRef()]] - code - src/lib/safety/order-audit.ts
- [[projectRiskContext()]] - code - src/lib/safety/kernel.ts
- [[readBrokerPositions()]] - code - src/lib/safety/kernel.ts
- [[submit()]] - code - src/lib/safety/controls.test.ts
- [[toBrokerOrder()]] - code - src/lib/safety/kernel.ts
- [[types.ts_9]] - code - src/lib/safety/types.ts
- [[validOpenOrderCount()]] - code - src/lib/safety/gateways/paper.ts
- [[validateInput()]] - code - src/lib/safety/kernel.ts
- [[validateOrder()_6]] - code - src/lib/safety/gateways/paper.ts
- [[validatedPositions()]] - code - src/lib/safety/kernel.ts
- [[write()_1]] - code - src/lib/safety/controls.test.ts
- [[writeIfUnchanged()]] - code - src/lib/safety/controls.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Broker_Order_Safety
SORT file.name ASC
```

## Connections to other communities
- 34 edges to [[_COMMUNITY_Binance Gateway Integration]]
- 31 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 30 edges to [[_COMMUNITY_Broker Credential Controls]]
- 12 edges to [[_COMMUNITY_Broker Environment Config]]
- 11 edges to [[_COMMUNITY_Safety Control Actions]]
- 11 edges to [[_COMMUNITY_Alpaca Gateway Integration]]
- 9 edges to [[_COMMUNITY_Multi-Venue Gateway Factory]]
- 3 edges to [[_COMMUNITY_Venue Gateway Interface]]
- 3 edges to [[_COMMUNITY_Order Audit Reconciliation]]
- 1 edge to [[_COMMUNITY_Alert Notification System]]
- 1 edge to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 1 edge to [[_COMMUNITY_Durable State Store]]

## Top bridge nodes
- [[types.ts_9]] - degree 38, connects to 9 communities
- [[BrokerOrder]] - degree 27, connects to 8 communities
- [[order-audit.ts]] - degree 15, connects to 6 communities
- [[kernel.ts]] - degree 57, connects to 5 communities
- [[BrokerAck]] - degree 19, connects to 5 communities