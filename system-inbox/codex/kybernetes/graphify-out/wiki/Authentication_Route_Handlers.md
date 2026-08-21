# Authentication Route Handlers

> 41 nodes · cohesion 0.12

## Key Concepts

- **index.ts** (29 connections) — `src/lib/auth/index.ts`
- **session.ts** (27 connections) — `src/lib/auth/session.ts`
- **isLoopbackRequest()** (11 connections) — `src/lib/auth/session.ts`
- **route.ts** (10 connections) — `src/app/auth/session/route.ts`
- **middleware.ts** (10 connections) — `src/middleware.ts`
- **POST()** (9 connections) — `src/app/auth/session/route.ts`
- **authenticateRequest()** (9 connections) — `src/lib/auth/session.ts`
- **authSecretFromEnv()** (9 connections) — `src/lib/auth/session.ts`
- **createSessionValue()** (8 connections) — `src/lib/auth/session.ts`
- **verifySessionValue()** (8 connections) — `src/lib/auth/session.ts`
- **verifySharedSecret()** (8 connections) — `src/lib/auth/session.ts`
- **middleware()** (8 connections) — `src/middleware.ts`
- **session.test.ts** (7 connections) — `src/lib/auth/session.test.ts`
- **route.test.ts** (5 connections) — `src/app/auth/session/route.test.ts`
- **hasMinimumSecretStrength()** (5 connections) — `src/lib/auth/session.ts`
- **isLoopbackHostname()** (5 connections) — `src/lib/auth/session.ts`
- **middleware.test.ts** (5 connections) — `src/middleware.test.ts`
- **AuthenticationError** (4 connections) — `src/lib/auth/index.ts`
- **hostnameFromHost()** (4 connections) — `src/lib/auth/session.ts`
- **importHmacKey()** (4 connections) — `src/lib/auth/session.ts`
- **sign()** (4 connections) — `src/lib/auth/session.ts`
- **AuthDecision** (3 connections) — `src/lib/auth/session.ts`
- **toArrayBuffer()** (3 connections) — `src/lib/auth/session.ts`
- **forwardedOverHttps()** (2 connections) — `src/app/auth/session/route.ts`
- **textResponse()** (2 connections) — `src/app/auth/session/route.ts`
- *... and 16 more nodes in this community*

## Relationships

- [Stack Tool Management](Stack_Tool_Management.md) (7 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (5 shared connections)
- [Risk Report Routes](Risk_Report_Routes.md) (3 shared connections)
- [Alert Notification System](Alert_Notification_System.md) (2 shared connections)
- [Strategy Backtesting UI](Strategy_Backtesting_UI.md) (2 shared connections)
- [Database Policy Management](Database_Policy_Management.md) (2 shared connections)
- [Launcher Security Boundaries](Launcher_Security_Boundaries.md) (1 shared connections)
- [Broker Latency Probing](Broker_Latency_Probing.md) (1 shared connections)
- [Performance Comparison UI](Performance_Comparison_UI.md) (1 shared connections)
- [Financial Anomaly Detection](Financial_Anomaly_Detection.md) (1 shared connections)
- [Terminal Layout Persistence](Terminal_Layout_Persistence.md) (1 shared connections)
- [Connector Management Actions](Connector_Management_Actions.md) (1 shared connections)

## Source Files

- `src/app/auth/session/route.test.ts`
- `src/app/auth/session/route.ts`
- `src/lib/auth/index.ts`
- `src/lib/auth/session.test.ts`
- `src/lib/auth/session.ts`
- `src/middleware.test.ts`
- `src/middleware.ts`

## Audit Trail

- EXTRACTED: 224 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*