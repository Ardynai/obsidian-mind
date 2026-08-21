# Durable State Store

> 21 nodes · cohesion 0.13

## Key Concepts

- **state.ts** (24 connections) — `src/lib/safety/state.ts`
- **state.test.ts** (8 connections) — `src/lib/safety/state.test.ts`
- **parseDate()** (3 connections) — `src/lib/safety/state.ts`
- **parseRevision()** (3 connections) — `src/lib/safety/state.ts`
- **parseSnapshot()** (3 connections) — `src/lib/safety/state.ts`
- **unavailableState()** (3 connections) — `src/lib/safety/state.ts`
- **checkedNow()** (2 connections) — `src/lib/safety/state.ts`
- **DURABLE_STATE_REASONS** (2 connections) — `src/lib/safety/state.ts`
- **fakeDatabase()** (2 connections) — `src/lib/safety/state.test.ts`
- **requiredString()** (2 connections) — `src/lib/safety/state.test.ts`
- **validatedRevision()** (2 connections) — `src/lib/safety/state.ts`
- **validatedState()** (2 connections) — `src/lib/safety/state.ts`
- **Database** (1 connections) — `src/lib/safety/state.ts`
- **DatabaseFactory** (1 connections) — `src/lib/safety/state.ts`
- **DurableKernelStateStoreOptions** (1 connections) — `src/lib/safety/state.ts`
- **parseTimestamp()** (1 connections) — `src/lib/safety/state.ts`
- **FakeStateRow** (1 connections) — `src/lib/safety/state.test.ts`
- **FIRST_BOOT** (1 connections) — `src/lib/safety/state.test.ts`
- **SECOND_BOOT** (1 connections) — `src/lib/safety/state.test.ts`
- **unavailableError()** (1 connections) — `src/lib/safety/state.ts`
- **withDatabase()** (1 connections) — `src/lib/safety/state.ts`

## Relationships

- [Broker Credential Controls](Broker_Credential_Controls.md) (4 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (4 shared connections)
- [Database Policy Management](Database_Policy_Management.md) (2 shared connections)
- [Broker Order Safety](Broker_Order_Safety.md) (1 shared connections)

## Source Files

- `src/lib/safety/state.test.ts`
- `src/lib/safety/state.ts`

## Audit Trail

- EXTRACTED: 65 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*