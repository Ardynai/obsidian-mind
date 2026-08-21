# Remote Fynn Client

> 9 nodes · cohesion 0.33

## Key Concepts

- **RemoteFynn** (8 connections) — `src/lib/bots/adapters/fynn.ts`
- **FynnRunRequest** (6 connections) — `packages/contract/index.ts`
- **FynnRunResult** (6 connections) — `packages/contract/index.ts`
- **.requestJson()** (6 connections) — `src/lib/bots/adapters/fynn.ts`
- **.run()** (6 connections) — `src/lib/bots/adapters/fynn.ts`
- **.probeHealth()** (5 connections) — `src/lib/bots/adapters/fynn.ts`
- **readBoundedJson()** (4 connections) — `src/lib/bots/adapters/fynn.ts`
- **.probeDescribe()** (4 connections) — `src/lib/bots/adapters/fynn.ts`
- **cancelResponseBody()** (3 connections) — `src/lib/bots/adapters/fynn.ts`

## Relationships

- [Fynn Risk Reporting](Fynn_Risk_Reporting.md) (11 shared connections)
- [Remote Response Parsing](Remote_Response_Parsing.md) (6 shared connections)
- [Core Trading Types](Core_Trading_Types.md) (2 shared connections)
- [Remote Parity Testing](Remote_Parity_Testing.md) (2 shared connections)
- [Remote Smoke Testing](Remote_Smoke_Testing.md) (1 shared connections)
- [Fynn Bot Adapter](Fynn_Bot_Adapter.md) (1 shared connections)
- [Mirofish Integration Testing](Mirofish_Integration_Testing.md) (1 shared connections)

## Source Files

- `packages/contract/index.ts`
- `src/lib/bots/adapters/fynn.ts`

## Audit Trail

- EXTRACTED: 48 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*