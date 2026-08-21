# Next.js Listener Process

> 10 nodes · cohesion 0.31

## Key Concepts

- **run-next.mjs** (7 connections) — `scripts/run-next.mjs`
- **next-listener-args.mjs** (4 connections) — `scripts/next-listener-args.mjs`
- **resolveHostname()** (3 connections) — `scripts/next-listener-args.mjs`
- **start-alert-drain.mjs** (3 connections) — `scripts/start-alert-drain.mjs`
- **startSelfDrain()** (3 connections) — `scripts/start-alert-drain.mjs`
- **resolvePort()** (2 connections) — `scripts/next-listener-args.mjs`
- **alertDrainUrl()** (2 connections) — `scripts/start-alert-drain.mjs`
- **next-listener-args.test.ts** (2 connections) — `src/lib/auth/next-listener-args.test.ts`
- **allowedCommands** (1 connections) — `scripts/run-next.mjs`
- **[command, ...args]** (1 connections) — `scripts/run-next.mjs`

## Relationships

- No strong cross-community connections detected

## Source Files

- `scripts/next-listener-args.mjs`
- `scripts/run-next.mjs`
- `scripts/start-alert-drain.mjs`
- `src/lib/auth/next-listener-args.test.ts`

## Audit Trail

- EXTRACTED: 28 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*