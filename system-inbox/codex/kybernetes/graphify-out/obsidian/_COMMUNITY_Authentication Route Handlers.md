---
type: community
cohesion: 0.12
members: 41
---

# Authentication Route Handlers

**Cohesion:** 0.12 - loosely connected
**Members:** 41 nodes

## Members
- [[.constructor()]] - code - src/lib/auth/index.ts
- [[AuthDecision]] - code - src/lib/auth/session.ts
- [[AuthenticationError]] - code - src/lib/auth/index.ts
- [[POST()]] - code - src/app/auth/session/route.ts
- [[PUBLIC_PATHS]] - code - src/middleware.ts
- [[SessionPayload]] - code - src/lib/auth/session.ts
- [[authSecretFromEnv()]] - code - src/lib/auth/session.ts
- [[authenticateRequest()]] - code - src/lib/auth/session.ts
- [[config]] - code - src/middleware.ts
- [[createSessionValue()]] - code - src/lib/auth/session.ts
- [[decodeBase64Url()]] - code - src/lib/auth/session.ts
- [[encodeBase64Url()]] - code - src/lib/auth/session.ts
- [[forwardedOverHttps()]] - code - src/app/auth/session/route.ts
- [[hasMinimumSecretStrength()]] - code - src/lib/auth/session.ts
- [[hostnameFromHost()]] - code - src/lib/auth/session.ts
- [[importHmacKey()]] - code - src/lib/auth/session.ts
- [[index.ts_3]] - code - src/lib/auth/index.ts
- [[isLoopbackHostname()]] - code - src/lib/auth/session.ts
- [[isLoopbackRequest()]] - code - src/lib/auth/session.ts
- [[isNavigationalGet()]] - code - src/middleware.ts
- [[isProtectedMachineRoute()]] - code - src/middleware.ts
- [[isSessionPayload()]] - code - src/lib/auth/session.ts
- [[loginRequest()]] - code - src/app/auth/session/route.test.ts
- [[loopbackHeaders()]] - code - src/app/auth/session/route.test.ts
- [[loopbackHeaders()_1]] - code - src/middleware.test.ts
- [[middleware()]] - code - src/middleware.ts
- [[middleware.test.ts]] - code - src/middleware.test.ts
- [[middleware.ts]] - code - src/middleware.ts
- [[readCookie()]] - code - src/lib/auth/session.ts
- [[route.test.ts]] - code - src/app/auth/session/route.test.ts
- [[route.ts]] - code - src/app/auth/session/route.ts
- [[session.test.ts]] - code - src/lib/auth/session.test.ts
- [[session.ts]] - code - src/lib/auth/session.ts
- [[sign()]] - code - src/lib/auth/session.ts
- [[splitHeader()]] - code - src/lib/auth/session.ts
- [[textDecoder]] - code - src/lib/auth/session.ts
- [[textEncoder]] - code - src/lib/auth/session.ts
- [[textResponse()]] - code - src/app/auth/session/route.ts
- [[toArrayBuffer()]] - code - src/lib/auth/session.ts
- [[verifySessionValue()]] - code - src/lib/auth/session.ts
- [[verifySharedSecret()]] - code - src/lib/auth/session.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Authentication_Route_Handlers
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Stack Tool Management]]
- 5 edges to [[_COMMUNITY_Safety Control Actions]]
- 3 edges to [[_COMMUNITY_Risk Report Routes]]
- 2 edges to [[_COMMUNITY_Alert Notification System]]
- 2 edges to [[_COMMUNITY_Strategy Backtesting UI]]
- 2 edges to [[_COMMUNITY_Database Policy Management]]
- 1 edge to [[_COMMUNITY_Launcher Security Boundaries]]
- 1 edge to [[_COMMUNITY_Broker Latency Probing]]
- 1 edge to [[_COMMUNITY_Performance Comparison UI]]
- 1 edge to [[_COMMUNITY_Financial Anomaly Detection]]
- 1 edge to [[_COMMUNITY_Terminal Layout Persistence]]
- 1 edge to [[_COMMUNITY_Connector Management Actions]]
- 1 edge to [[_COMMUNITY_Market Data Actions]]

## Top bridge nodes
- [[index.ts_3]] - degree 29, connects to 13 communities
- [[isLoopbackRequest()]] - degree 11, connects to 1 community
- [[authenticateRequest()]] - degree 9, connects to 1 community
- [[authSecretFromEnv()]] - degree 9, connects to 1 community
- [[AuthenticationError]] - degree 4, connects to 1 community