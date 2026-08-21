# Database Policy Management

> 86 nodes · cohesion 0.07

## Key Concepts

- **index.ts** (51 connections) — `src/lib/governance/index.ts`
- **gate.ts** (42 connections) — `src/lib/governance/gate.ts`
- **openDatabase()** (30 connections) — `src/db/client.ts`
- **trust-gate.ts** (26 connections) — `src/lib/governance/trust-gate.ts`
- **types.ts** (24 connections) — `src/lib/governance/types.ts`
- **supervision-log.ts** (20 connections) — `src/lib/governance/supervision-log.ts`
- **assertActionAllowed()** (17 connections) — `src/lib/governance/gate.ts`
- **gate.test.ts** (17 connections) — `src/lib/governance/gate.test.ts`
- **policy.ts** (15 connections) — `src/lib/governance/policy.ts`
- **trust-gate.test.ts** (15 connections) — `src/lib/governance/trust-gate.test.ts`
- **client.ts** (14 connections) — `src/db/client.ts`
- **resetGovernanceForTests()** (12 connections) — `src/lib/governance/gate.ts`
- **defaultPolicy()** (12 connections) — `src/lib/governance/types.ts`
- **ActionClass** (11 connections) — `src/lib/governance/types.ts`
- **PolicyDeniedError** (11 connections) — `src/lib/governance/types.ts`
- **listSupervisionLog()** (10 connections) — `src/lib/governance/supervision-log.ts`
- **actions.ts** (8 connections) — `src/app/policy/actions.ts`
- **loadGovernanceView()** (8 connections) — `src/lib/governance/gate.ts`
- **loadPolicy()** (8 connections) — `src/lib/governance/policy.ts`
- **appendSupervisionEntry()** (8 connections) — `src/lib/governance/supervision-log.ts`
- **TrustGateStore** (8 connections) — `src/lib/governance/trust-gate.ts`
- **isActionClass()** (8 connections) — `src/lib/governance/types.ts`
- **page.tsx** (7 connections) — `src/app/policy/page.tsx`
- **parsePolicyDocument()** (7 connections) — `src/lib/governance/policy.ts`
- **policy.test.ts** (7 connections) — `src/lib/governance/policy.test.ts`
- *... and 61 more nodes in this community*

## Relationships

- [Safety Control Actions](Safety_Control_Actions.md) (13 shared connections)
- [Strategy Backtesting UI](Strategy_Backtesting_UI.md) (9 shared connections)
- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (8 shared connections)
- [Risk Report Routes](Risk_Report_Routes.md) (8 shared connections)
- [Fynn Adapter Conformance](Fynn_Adapter_Conformance.md) (7 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (5 shared connections)
- [Order Simulation Testing](Order_Simulation_Testing.md) (5 shared connections)
- [Stack Tool Management](Stack_Tool_Management.md) (4 shared connections)
- [System Health Metrics](System_Health_Metrics.md) (4 shared connections)
- [Connector Health Monitoring](Connector_Health_Monitoring.md) (4 shared connections)
- [Order Audit Reconciliation](Order_Audit_Reconciliation.md) (4 shared connections)
- [Terminal Layout Persistence](Terminal_Layout_Persistence.md) (4 shared connections)

## Source Files

- `src/app/policy/actions.test.ts`
- `src/app/policy/actions.ts`
- `src/app/policy/page.tsx`
- `src/db/client.ts`
- `src/lib/bots/adapters/research.test.ts`
- `src/lib/governance/gate.test.ts`
- `src/lib/governance/gate.ts`
- `src/lib/governance/index.ts`
- `src/lib/governance/policy.test.ts`
- `src/lib/governance/policy.ts`
- `src/lib/governance/supervision-log.test.ts`
- `src/lib/governance/supervision-log.ts`
- `src/lib/governance/trust-gate.test.ts`
- `src/lib/governance/trust-gate.ts`
- `src/lib/governance/types.ts`

## Audit Trail

- EXTRACTED: 584 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*