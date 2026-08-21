---
type: community
cohesion: 0.11
members: 35
---

# Broker Environment Config

**Cohesion:** 0.11 - loosely connected
**Members:** 35 nodes

## Members
- [[ALPACA_ENDPOINTS]] - code - src/lib/safety/config.ts
- [[BrokerConfiguration]] - code - src/lib/safety/config.ts
- [[DEFAULT_SAFETY_LIMITS]] - code - src/lib/safety/config.ts
- [[KALSHI_ENDPOINTS]] - code - src/lib/safety/config.ts
- [[SAFETY_ENV_NAMES]] - code - src/lib/safety/config.ts
- [[VenueSelector]] - code - src/lib/safety/config.ts
- [[alpaca.smoke.test.ts]] - code - src/lib/safety/gateways/alpaca.smoke.test.ts
- [[alpacaConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[binanceConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[brokerConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[coinbaseConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[config.test.ts]] - code - src/lib/safety/config.test.ts
- [[config.ts_1]] - code - src/lib/safety/config.ts
- [[databaseHarness()]] - code - src/lib/safety/lock.test.ts
- [[ev1-gateways.test.ts]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[finiteNonNegative()]] - code - src/lib/safety/config.ts
- [[invalidEnvironment()]] - code - src/lib/safety/config.ts
- [[invalidVenue()]] - code - src/lib/safety/config.ts
- [[jsonBody()]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[kalshiConfig]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[kalshiConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[kalshiEnv]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[kalshiTruth()]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[krakenConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[lock.test.ts]] - code - src/lib/safety/lock.test.ts
- [[missingNames()]] - code - src/lib/safety/config.ts
- [[nonBlank()]] - code - src/lib/safety/config.ts
- [[oandaConfigurationFromEnv()]] - code - src/lib/safety/config.ts
- [[order_3]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[requestUrl()_5]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[response()_1]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[safePositiveInteger()]] - code - src/lib/safety/config.ts
- [[testPem]] - code - src/lib/safety/gateways/ev1-gateways.test.ts
- [[venueSelectorFromEnv()]] - code - src/lib/safety/config.ts
- [[{ privateKey }]] - code - src/lib/safety/gateways/ev1-gateways.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Broker_Environment_Config
SORT file.name ASC
```

## Connections to other communities
- 20 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 17 edges to [[_COMMUNITY_Binance Gateway Integration]]
- 12 edges to [[_COMMUNITY_Broker Order Safety]]
- 10 edges to [[_COMMUNITY_Alpaca Gateway Integration]]
- 9 edges to [[_COMMUNITY_Broker Credential Controls]]
- 7 edges to [[_COMMUNITY_Multi-Venue Gateway Factory]]
- 3 edges to [[_COMMUNITY_Performance Comparison UI]]
- 3 edges to [[_COMMUNITY_Venue Presence Monitoring]]

## Top bridge nodes
- [[config.ts_1]] - degree 62, connects to 8 communities
- [[ev1-gateways.test.ts]] - degree 19, connects to 5 communities
- [[BrokerConfiguration]] - degree 14, connects to 5 communities
- [[lock.test.ts]] - degree 19, connects to 4 communities
- [[brokerConfigurationFromEnv()]] - degree 12, connects to 1 community