# Fynn Bot Adapter

> 9 nodes · cohesion 0.31

## Key Concepts

- **FynnClient** (9 connections) — `packages/contract/index.ts`
- **FynnBotAdapter** (9 connections) — `src/lib/bots/adapters/fynn.ts`
- **.run()** (5 connections) — `src/lib/bots/adapters/fynn.ts`
- **.describe()** (3 connections) — `src/lib/bots/adapters/fynn.ts`
- **.health()** (3 connections) — `src/lib/bots/adapters/fynn.ts`
- **.localDescribe()** (3 connections) — `src/lib/bots/adapters/fynn.ts`
- **.run()** (2 connections) — `packages/contract/index.ts`
- **.constructor()** (2 connections) — `src/lib/bots/adapters/fynn.ts`
- **toBotRunResult()** (2 connections) — `src/lib/bots/adapters/fynn.ts`

## Relationships

- [Fynn Risk Reporting](Fynn_Risk_Reporting.md) (5 shared connections)
- [Mirofish Integration Testing](Mirofish_Integration_Testing.md) (5 shared connections)
- [Research Signal Generation](Research_Signal_Generation.md) (2 shared connections)
- [Core Trading Types](Core_Trading_Types.md) (1 shared connections)
- [Remote Fynn Client](Remote_Fynn_Client.md) (1 shared connections)
- [Remote Smoke Testing](Remote_Smoke_Testing.md) (1 shared connections)
- [Remote Parity Testing](Remote_Parity_Testing.md) (1 shared connections)

## Source Files

- `packages/contract/index.ts`
- `src/lib/bots/adapters/fynn.ts`

## Audit Trail

- EXTRACTED: 38 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*