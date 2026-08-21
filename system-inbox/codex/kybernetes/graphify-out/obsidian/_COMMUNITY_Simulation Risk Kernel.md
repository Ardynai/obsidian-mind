---
type: community
cohesion: 0.07
members: 71
---

# Simulation Risk Kernel

**Cohesion:** 0.07 - loosely connected
**Members:** 71 nodes

## Members
- [[.assertOwned()]] - code - src/lib/safety/lock.ts
- [[.constructor()_13]] - code - src/lib/safety/index.ts
- [[.constructor()_14]] - code - src/lib/safety/lock.ts
- [[.getDailyLoss()_1]] - code - src/lib/safety/gateways/venue.ts
- [[ArmBrokerOptions]] - code - src/lib/safety/index.ts
- [[Database_2]] - code - src/lib/safety/lock.ts
- [[DatabaseFactory]] - code - src/lib/safety/lock.ts
- [[DurableSafetyFence]] - code - src/lib/safety/lock.ts
- [[DurableSafetyFenceError]] - code - src/lib/safety/lock.ts
- [[DurableSafetyLockOptions]] - code - src/lib/safety/lock.ts
- [[DurableSafetyPoisonOptions]] - code - src/lib/safety/lock.ts
- [[ForceClearFlattenUnknownOptions]] - code - src/lib/safety/index.ts
- [[KernelBatchExecutionResult]] - code - src/lib/safety/kernel.ts
- [[KillSwitchOptions]] - code - src/lib/safety/index.ts
- [[ReceiptPersistenceError]] - code - src/lib/safety/index.ts
- [[ReconcileBrokerOptions]] - code - src/lib/safety/index.ts
- [[SafetyActionOptions]] - code - src/lib/safety/index.ts
- [[SafetyAuditSink]] - code - src/lib/safety/kernel.ts
- [[UNFENCED_OPERATION]] - code - src/lib/safety/lock.ts
- [[acknowledgementReceiptId()]] - code - src/lib/safety/index.ts
- [[armBroker()]] - code - src/lib/safety/index.ts
- [[assertFlattenMutationAllowed()]] - code - src/lib/safety/index.ts
- [[assertOrdinaryMutationAllowed()]] - code - src/lib/safety/index.ts
- [[brokerConnectivity()]] - code - src/lib/safety/index.ts
- [[brokerOrder()]] - code - src/lib/safety/receipts.test.ts
- [[brokerRequestTimeoutFromEnv()]] - code - src/lib/safety/config.ts
- [[checkedNow()_1]] - code - src/lib/safety/index.ts
- [[checkedToken()]] - code - src/lib/safety/lock.ts
- [[claimFence()]] - code - src/lib/safety/lock.ts
- [[collectAuditedBrokerOrders()]] - code - src/lib/safety/index.ts
- [[controlsFor()]] - code - src/lib/safety/index.ts
- [[createDurableKernelStateStore()]] - code - src/lib/safety/state.ts
- [[disarmBroker()]] - code - src/lib/safety/index.ts
- [[flattenBroker()]] - code - src/lib/safety/index.ts
- [[forceClearFlattenUnknown()]] - code - src/lib/safety/index.ts
- [[getRuntime()]] - code - src/lib/safety/index.ts
- [[getSafetySnapshot()]] - code - src/lib/safety/index.ts
- [[guardBrokerMutations()]] - code - src/lib/safety/kernel.ts
- [[haltRuntime()]] - code - src/lib/safety/index.ts
- [[index.ts_15]] - code - src/lib/safety/index.ts
- [[isUnknownAck()]] - code - src/lib/safety/types.ts
- [[isVenueGateway()]] - code - src/lib/safety/gateways/venue.ts
- [[loadRiskContext()]] - code - src/lib/safety/index.ts
- [[lock.ts]] - code - src/lib/safety/lock.ts
- [[outstandingOrderRanges()]] - code - src/lib/safety/index.ts
- [[ownerFromRow()]] - code - src/lib/safety/lock.ts
- [[ownsFence()]] - code - src/lib/safety/lock.ts
- [[poisonDurableSafetyFence()]] - code - src/lib/safety/lock.ts
- [[processBacktestOrderIntents()]] - code - src/lib/backtest/simulation-kernel.ts
- [[processOrderIntent()]] - code - src/lib/safety/index.ts
- [[processOrderIntents()]] - code - src/lib/safety/index.ts
- [[receiptSinkFor()]] - code - src/lib/safety/index.ts
- [[receiptSummary()]] - code - src/lib/safety/index.ts
- [[reconcileBrokerTruth()]] - code - src/lib/safety/index.ts
- [[reconcileRuntime()]] - code - src/lib/safety/index.ts
- [[reconciliationGateway()]] - code - src/lib/safety/index.ts
- [[reconciliationTruth()]] - code - src/lib/safety/index.ts
- [[recordSafetyHeartbeat()]] - code - src/lib/safety/index.ts
- [[releaseFence()]] - code - src/lib/safety/lock.ts
- [[safetyConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[safetyGlobal]] - code - src/lib/safety/index.ts
- [[serialize()]] - code - src/lib/safety/index.ts
- [[serializeMutation()]] - code - src/lib/safety/index.ts
- [[simulation-kernel.ts]] - code - src/lib/backtest/simulation-kernel.ts
- [[simulationRiskContext()]] - code - src/lib/backtest/simulation-kernel.ts
- [[symbolList()]] - code - src/lib/safety/config.ts
- [[unresolvedFlattenForRuntime()]] - code - src/lib/safety/index.ts
- [[unresolvedUnknownClientOrderIds()]] - code - src/lib/safety/receipts.ts
- [[venueOrderMatchesAudit()]] - code - src/lib/safety/index.ts
- [[withDatabase()]] - code - src/lib/safety/lock.ts
- [[withDurableSafetyLock()]] - code - src/lib/safety/lock.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Simulation_Risk_Kernel
SORT file.name ASC
```

## Connections to other communities
- 31 edges to [[_COMMUNITY_Broker Order Safety]]
- 23 edges to [[_COMMUNITY_Broker Credential Controls]]
- 20 edges to [[_COMMUNITY_Broker Environment Config]]
- 19 edges to [[_COMMUNITY_Order Audit Reconciliation]]
- 16 edges to [[_COMMUNITY_Safety Control Actions]]
- 11 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 8 edges to [[_COMMUNITY_Binance Gateway Integration]]
- 8 edges to [[_COMMUNITY_Multi-Venue Gateway Factory]]
- 6 edges to [[_COMMUNITY_Cockpit Navigation Layout]]
- 5 edges to [[_COMMUNITY_Performance Comparison UI]]
- 5 edges to [[_COMMUNITY_Database Policy Management]]
- 5 edges to [[_COMMUNITY_Order Simulation Testing]]
- 5 edges to [[_COMMUNITY_Venue Gateway Interface]]
- 4 edges to [[_COMMUNITY_Strategy Backtesting UI]]
- 4 edges to [[_COMMUNITY_Durable State Store]]
- 3 edges to [[_COMMUNITY_Terminal Layout Persistence]]
- 3 edges to [[_COMMUNITY_Connector Management Actions]]
- 3 edges to [[_COMMUNITY_Alpaca Gateway Integration]]
- 2 edges to [[_COMMUNITY_Ledger Memory Reservations]]
- 1 edge to [[_COMMUNITY_Design System Dashboard]]

## Top bridge nodes
- [[index.ts_15]] - degree 134, connects to 19 communities
- [[getSafetySnapshot()]] - degree 17, connects to 7 communities
- [[simulation-kernel.ts]] - degree 14, connects to 5 communities
- [[controlsFor()]] - degree 19, connects to 4 communities
- [[forceClearFlattenUnknown()]] - degree 16, connects to 4 communities