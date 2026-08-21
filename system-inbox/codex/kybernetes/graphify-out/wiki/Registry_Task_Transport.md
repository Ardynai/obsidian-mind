# Registry Task Transport

> 16 nodes · cohesion 0.13

## Key Concepts

- **RegistryTransport** (10 connections) — `src/lib/fabric/federation.ts`
- **FakeRegistry** (10 connections) — `src/lib/fabric/federation.test.ts`
- **.register()** (2 connections) — `src/lib/fabric/federation.test.ts`
- **.connect()** (1 connections) — `src/lib/fabric/federation.ts`
- **.discover()** (1 connections) — `src/lib/fabric/federation.ts`
- **.on()** (1 connections) — `src/lib/fabric/federation.ts`
- **.register()** (1 connections) — `src/lib/fabric/federation.ts`
- **.sendTaskResult()** (1 connections) — `src/lib/fabric/federation.ts`
- **.sendTaskToPeer()** (1 connections) — `src/lib/fabric/federation.ts`
- **.connect()** (1 connections) — `src/lib/fabric/federation.test.ts`
- **.constructor()** (1 connections) — `src/lib/fabric/federation.test.ts`
- **.discover()** (1 connections) — `src/lib/fabric/federation.test.ts`
- **.emitTask()** (1 connections) — `src/lib/fabric/federation.test.ts`
- **.on()** (1 connections) — `src/lib/fabric/federation.test.ts`
- **.sendTaskResult()** (1 connections) — `src/lib/fabric/federation.test.ts`
- **.sendTaskToPeer()** (1 connections) — `src/lib/fabric/federation.test.ts`

## Relationships

- [Fabric Audit Sinks](Fabric_Audit_Sinks.md) (2 shared connections)
- [Fabric Identity Federation](Fabric_Identity_Federation.md) (1 shared connections)

## Source Files

- `src/lib/fabric/federation.test.ts`
- `src/lib/fabric/federation.ts`

## Audit Trail

- EXTRACTED: 35 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*