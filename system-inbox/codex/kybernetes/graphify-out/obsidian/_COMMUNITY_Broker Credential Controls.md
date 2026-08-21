---
type: community
cohesion: 0.05
members: 66
---

# Broker Credential Controls

**Cohesion:** 0.05 - loosely connected
**Members:** 66 nodes

## Members
- [[.arm()]] - code - src/lib/safety/controls.ts
- [[.checkDeadMan()]] - code - src/lib/safety/controls.ts
- [[.constructor()_10]] - code - src/lib/safety/controls.ts
- [[.constructor()_11]] - code - src/lib/safety/controls.ts
- [[.constructor()_12]] - code - src/lib/safety/index.ts
- [[.disarm()]] - code - src/lib/safety/controls.ts
- [[.flatten()]] - code - src/lib/safety/controls.ts
- [[.getState()]] - code - src/lib/safety/controls.ts
- [[.heartbeat()]] - code - src/lib/safety/controls.ts
- [[.isHealthy()]] - code - src/lib/safety/controls.ts
- [[.killSwitch()]] - code - src/lib/safety/controls.ts
- [[.read()_2]] - code - src/lib/safety/controls.ts
- [[.readHeartbeatAt()]] - code - src/lib/safety/controls.ts
- [[.readSnapshot()]] - code - src/lib/safety/controls.ts
- [[.write()_1]] - code - src/lib/safety/controls.ts
- [[.writeHeartbeatAt()]] - code - src/lib/safety/controls.ts
- [[.writeIfUnchanged()]] - code - src/lib/safety/controls.ts
- [[ALPACA_CLIENT_ORDER_ID]] - code - src/lib/safety/index.test.ts
- [[ArmPreconditionCode]] - code - src/lib/safety/controls.ts
- [[ArmPreconditionError]] - code - src/lib/safety/controls.ts
- [[ArmRequest]] - code - src/lib/safety/controls.ts
- [[ArmResult]] - code - src/lib/safety/controls.ts
- [[AuditedBrokerOrder]] - code - src/lib/safety/order-audit.ts
- [[BrokerCredentialState]] - code - src/lib/safety/config.ts
- [[BrokerGatewayName]] - code - src/lib/safety/config.ts
- [[ControlAuditSink]] - code - src/lib/safety/controls.ts
- [[EVALUATED_AT]] - code - src/lib/safety/index.test.ts
- [[FlattenAuditSink]] - code - src/lib/safety/kernel.ts
- [[FlattenReconciliationRequiredError]] - code - src/lib/safety/index.ts
- [[FlattenResult]] - code - src/lib/safety/controls.ts
- [[HaltPersistenceError]] - code - src/lib/safety/controls.ts
- [[INTENT]] - code - src/lib/safety/index.test.ts
- [[KernelState]] - code - src/lib/safety/types.ts
- [[KernelStateSnapshot]] - code - src/lib/safety/controls.ts
- [[KernelStateStore]] - code - src/lib/safety/controls.ts
- [[KillSwitchResult]] - code - src/lib/safety/controls.ts
- [[SafetyControls]] - code - src/lib/safety/controls.ts
- [[SafetyControlsDependencies]] - code - src/lib/safety/controls.ts
- [[SafetyRuntime]] - code - src/lib/safety/index.ts
- [[SafetySnapshot]] - code - src/lib/safety/index.ts
- [[StoreValue]] - code - src/lib/safety/controls.ts
- [[alpacaAuditRef()]] - code - src/lib/safety/index.test.ts
- [[alpacaTruth()]] - code - src/lib/safety/index.test.ts
- [[armedStateStore()]] - code - src/lib/safety/index.test.ts
- [[auditControl()]] - code - src/lib/safety/controls.ts
- [[checkedNow()]] - code - src/lib/safety/controls.ts
- [[checkedTimestamp()]] - code - src/lib/safety/controls.ts
- [[cloneState()]] - code - src/lib/safety/controls.ts
- [[controls.ts]] - code - src/lib/safety/controls.ts
- [[createKernelStateStore()]] - code - src/lib/safety/controls.ts
- [[createSafetyControls()]] - code - src/lib/safety/controls.ts
- [[haltedStateStore()]] - code - src/lib/safety/index.test.ts
- [[index.test.ts]] - code - src/lib/safety/index.test.ts
- [[isLiveBrokerGatewayName()]] - code - src/lib/safety/config.ts
- [[jsonResponse()_2]] - code - src/lib/safety/index.test.ts
- [[ledgerRecord()]] - code - src/lib/safety/index.test.ts
- [[mocks_10]] - code - src/lib/safety/index.test.ts
- [[normalizedReason()]] - code - src/lib/safety/controls.ts
- [[persistHaltedState()]] - code - src/lib/safety/controls.ts
- [[poisonMutationPath()]] - code - src/lib/safety/controls.ts
- [[provenance()]] - code - src/lib/safety/index.test.ts
- [[read()_1]] - code - src/lib/safety/index.test.ts
- [[requestBody()_4]] - code - src/lib/safety/index.test.ts
- [[requestUrl()_7]] - code - src/lib/safety/index.test.ts
- [[sameKernelState()]] - code - src/lib/safety/controls.ts
- [[validateHeartbeatTimeout()]] - code - src/lib/safety/controls.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Broker_Credential_Controls
SORT file.name ASC
```

## Connections to other communities
- 30 edges to [[_COMMUNITY_Broker Order Safety]]
- 23 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 9 edges to [[_COMMUNITY_Broker Environment Config]]
- 7 edges to [[_COMMUNITY_Safety Control Actions]]
- 6 edges to [[_COMMUNITY_Alert Notification System]]
- 6 edges to [[_COMMUNITY_Order Simulation Testing]]
- 4 edges to [[_COMMUNITY_Durable State Store]]
- 4 edges to [[_COMMUNITY_Order Audit Reconciliation]]
- 3 edges to [[_COMMUNITY_Cockpit Navigation Layout]]
- 2 edges to [[_COMMUNITY_Performance Comparison UI]]
- 2 edges to [[_COMMUNITY_Strategy Backtesting UI]]
- 1 edge to [[_COMMUNITY_Design System Dashboard]]
- 1 edge to [[_COMMUNITY_Binance Gateway Integration]]
- 1 edge to [[_COMMUNITY_Venue Gateway Interface]]
- 1 edge to [[_COMMUNITY_Module Resolution Utilities]]

## Top bridge nodes
- [[controls.ts]] - degree 46, connects to 10 communities
- [[index.test.ts]] - degree 40, connects to 6 communities
- [[BrokerGatewayName]] - degree 15, connects to 5 communities
- [[createKernelStateStore()]] - degree 13, connects to 5 communities
- [[KernelState]] - degree 20, connects to 4 communities