# Live Score Parsing

> 36 nodes · cohesion 0.12

## Key Concepts

- **paper-signal.ts** (45 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **parseLiveScore()** (13 connections) — `src/lib/bots/adapters/live-score.ts`
- **live-score.ts** (11 connections) — `src/lib/bots/adapters/live-score.ts`
- **pingHttp()** (11 connections) — `src/lib/stack-runtime/health.ts`
- **tryLiveCli()** (10 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **isLocalHttpUrl()** (9 connections) — `src/lib/stack-runtime/health.ts`
- **fetchLivePayload()** (8 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **tryLiveHttp()** (8 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **runPaperSignal()** (6 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **parseScoreText()** (5 connections) — `src/lib/bots/adapters/live-score.ts`
- **healthFromEnv()** (4 connections) — `src/lib/bots/adapters/mirofish.ts`
- **correlationToScore()** (4 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **healthFromSpec()** (4 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **joinUrl()** (4 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **runFromLiveScore()** (4 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **runWithOptionalLive()** (4 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **clampScore()** (3 connections) — `src/lib/bots/adapters/live-score.ts`
- **parseDecision()** (3 connections) — `src/lib/bots/adapters/live-score.ts`
- **live-score.test.ts** (3 connections) — `src/lib/bots/adapters/live-score.test.ts`
- **isNumberMatrix()** (3 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **isoDate()** (3 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **PaperSignalSpec** (3 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **parseMiroFishScore()** (2 connections) — `src/lib/bots/adapters/mirofish.ts`
- **CliCommandContext** (2 connections) — `src/lib/bots/adapters/paper-signal.ts`
- **getJson()** (2 connections) — `src/lib/bots/adapters/paper-signal.ts`
- *... and 11 more nodes in this community*

## Relationships

- [Trading Stack Paths](Trading_Stack_Paths.md) (16 shared connections)
- [Mirofish Simulation Execution](Mirofish_Simulation_Execution.md) (10 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (6 shared connections)
- [Fynn Adapter Conformance](Fynn_Adapter_Conformance.md) (4 shared connections)
- [Mirofish Integration Testing](Mirofish_Integration_Testing.md) (3 shared connections)
- [Research Signal Generation](Research_Signal_Generation.md) (2 shared connections)
- [Git Environment Configuration](Git_Environment_Configuration.md) (1 shared connections)

## Source Files

- `src/lib/bots/adapters/live-score.test.ts`
- `src/lib/bots/adapters/live-score.ts`
- `src/lib/bots/adapters/mirofish.ts`
- `src/lib/bots/adapters/paper-signal.ts`
- `src/lib/stack-runtime/health.ts`

## Audit Trail

- EXTRACTED: 188 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*