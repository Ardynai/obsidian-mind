---
type: community
cohesion: 0.07
members: 86
---

# Database Policy Management

**Cohesion:** 0.07 - loosely connected
**Members:** 86 nodes

## Members
- [[.constructor()_7]] - code - src/lib/governance/types.ts
- [[.constructor()_9]] - code - src/lib/governance/types.ts
- [[.constructor()_8]] - code - src/lib/governance/types.ts
- [[.consume()]] - code - src/lib/governance/trust-gate.ts
- [[.read()_1]] - code - src/lib/governance/trust-gate.ts
- [[.write()]] - code - src/lib/governance/trust-gate.ts
- [[ACTION_CLASSES]] - code - src/lib/governance/types.ts
- [[ActionClass]] - code - src/lib/governance/types.ts
- [[DEFAULT_POLICY_PATH]] - code - src/lib/governance/policy.ts
- [[Database]] - code - src/lib/governance/supervision-log.ts
- [[Database_1]] - code - src/lib/governance/trust-gate.ts
- [[GateContext]] - code - src/lib/governance/types.ts
- [[GovernanceClassView]] - code - src/lib/governance/gate.ts
- [[GovernanceView]] - code - src/lib/governance/gate.ts
- [[POLICY_DECISIONS]] - code - src/lib/governance/types.ts
- [[PolicyDecision]] - code - src/lib/governance/types.ts
- [[PolicyDeniedError]] - code - src/lib/governance/types.ts
- [[PolicyDocument]] - code - src/lib/governance/types.ts
- [[PolicyPage()]] - code - src/app/policy/page.tsx
- [[SupervisionEntry]] - code - src/lib/governance/types.ts
- [[SupervisionLogUnavailableError]] - code - src/lib/governance/types.ts
- [[TrustGateRecord]] - code - src/lib/governance/trust-gate.ts
- [[TrustGateStore]] - code - src/lib/governance/trust-gate.ts
- [[TrustGateUnavailableError]] - code - src/lib/governance/types.ts
- [[actions.test.ts]] - code - src/app/policy/actions.test.ts
- [[actions.ts_3]] - code - src/app/policy/actions.ts
- [[allowWebSearchPolicy()]] - code - src/lib/bots/adapters/research.test.ts
- [[appendGovernanceProvenance()]] - code - src/lib/governance/gate.ts
- [[appendSupervisionEntry()]] - code - src/lib/governance/supervision-log.ts
- [[approvePolicyAction()]] - code - src/app/policy/actions.ts
- [[assertActionAllowed()]] - code - src/lib/governance/gate.ts
- [[bars_1]] - code - src/lib/governance/gate.test.ts
- [[canonicalSupervisionPayload()]] - code - src/lib/governance/supervision-log.ts
- [[client.ts]] - code - src/db/client.ts
- [[consume()]] - code - src/lib/governance/trust-gate.test.ts
- [[consumeToken()]] - code - src/lib/governance/trust-gate.ts
- [[consumeTrustGate()]] - code - src/lib/governance/trust-gate.ts
- [[currentTrustGateBootId()]] - code - src/lib/governance/trust-gate.ts
- [[decisionFor()]] - code - src/lib/governance/policy.ts
- [[defaultPolicy()]] - code - src/lib/governance/types.ts
- [[digestSupervisionPayload()]] - code - src/lib/governance/supervision-log.ts
- [[entryFromRow()]] - code - src/lib/governance/supervision-log.ts
- [[flipHexByte()]] - code - src/lib/governance/supervision-log.test.ts
- [[gate.test.ts]] - code - src/lib/governance/gate.test.ts
- [[gate.ts]] - code - src/lib/governance/gate.ts
- [[governanceAuditRun()]] - code - src/lib/governance/gate.ts
- [[hasUnusedTrustToken()]] - code - src/lib/governance/trust-gate.ts
- [[index.ts_10]] - code - src/lib/governance/index.ts
- [[isActionClass()]] - code - src/lib/governance/types.ts
- [[isPolicyDecision()]] - code - src/lib/governance/types.ts
- [[latchTrustGate()]] - code - src/lib/governance/trust-gate.ts
- [[listSupervisionLog()]] - code - src/lib/governance/supervision-log.ts
- [[loadGovernanceView()]] - code - src/lib/governance/gate.ts
- [[loadPolicy()]] - code - src/lib/governance/policy.ts
- [[memoryEntries]] - code - src/lib/governance/supervision-log.ts
- [[memoryTokens]] - code - src/lib/governance/trust-gate.ts
- [[mocks]] - code - src/app/policy/actions.test.ts
- [[openDatabase()]] - code - src/db/client.ts
- [[page.tsx_6]] - code - src/app/policy/page.tsx
- [[parsePolicyDocument()]] - code - src/lib/governance/policy.ts
- [[persistToken()]] - code - src/lib/governance/trust-gate.ts
- [[policy.test.ts]] - code - src/lib/governance/policy.test.ts
- [[policy.ts]] - code - src/lib/governance/policy.ts
- [[postgresTrustGateStore()]] - code - src/lib/governance/trust-gate.ts
- [[probeDatabaseStatus()]] - code - src/db/client.ts
- [[processBootId]] - code - src/lib/governance/trust-gate.ts
- [[processLatch]] - code - src/lib/governance/trust-gate.ts
- [[read()]] - code - src/lib/governance/trust-gate.test.ts
- [[readToken()]] - code - src/lib/governance/trust-gate.ts
- [[recordDecision()]] - code - src/lib/governance/gate.ts
- [[recordFromRow()]] - code - src/lib/governance/trust-gate.ts
- [[request()_2]] - code - src/lib/governance/gate.test.ts
- [[requireDatabaseUrl()]] - code - src/db/client.ts
- [[resetGovernanceForTests()]] - code - src/lib/governance/gate.ts
- [[resetSupervisionLogForTests()]] - code - src/lib/governance/supervision-log.ts
- [[resetTrustGateForTests()]] - code - src/lib/governance/trust-gate.ts
- [[setPolicyOverrideForTests()]] - code - src/lib/governance/policy.ts
- [[storeFor()]] - code - src/lib/governance/trust-gate.ts
- [[supervision-log.test.ts]] - code - src/lib/governance/supervision-log.test.ts
- [[supervision-log.ts]] - code - src/lib/governance/supervision-log.ts
- [[supervisionLogTail()]] - code - src/lib/governance/supervision-log.ts
- [[trust-gate.test.ts]] - code - src/lib/governance/trust-gate.test.ts
- [[trust-gate.ts]] - code - src/lib/governance/trust-gate.ts
- [[types.ts_6]] - code - src/lib/governance/types.ts
- [[verifySupervisionChain()]] - code - src/lib/governance/supervision-log.ts
- [[write()]] - code - src/lib/governance/trust-gate.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Database_Policy_Management
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Safety Control Actions]]
- 9 edges to [[_COMMUNITY_Strategy Backtesting UI]]
- 8 edges to [[_COMMUNITY_Risk Report Routes]]
- 8 edges to [[_COMMUNITY_Ledger Memory Reservations]]
- 7 edges to [[_COMMUNITY_Fynn Adapter Conformance]]
- 5 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 5 edges to [[_COMMUNITY_Order Simulation Testing]]
- 4 edges to [[_COMMUNITY_Performance Comparison UI]]
- 4 edges to [[_COMMUNITY_Stack Tool Management]]
- 4 edges to [[_COMMUNITY_System Health Metrics]]
- 4 edges to [[_COMMUNITY_Connector Health Monitoring]]
- 4 edges to [[_COMMUNITY_Order Audit Reconciliation]]
- 4 edges to [[_COMMUNITY_Terminal Layout Persistence]]
- 4 edges to [[_COMMUNITY_Research Signal Generation]]
- 3 edges to [[_COMMUNITY_Launcher Module Dependencies]]
- 3 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 2 edges to [[_COMMUNITY_Design System Dashboard]]
- 2 edges to [[_COMMUNITY_Authentication Route Handlers]]
- 2 edges to [[_COMMUNITY_Durable State Store]]
- 1 edge to [[_COMMUNITY_Mirofish Integration Testing]]

## Top bridge nodes
- [[index.ts_10]] - degree 51, connects to 9 communities
- [[client.ts]] - degree 14, connects to 8 communities
- [[openDatabase()]] - degree 30, connects to 7 communities
- [[gate.test.ts]] - degree 17, connects to 5 communities
- [[assertActionAllowed()]] - degree 17, connects to 4 communities