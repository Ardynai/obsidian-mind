---
type: community
cohesion: 0.28
members: 9
---

# Venue Presence Monitoring

**Cohesion:** 0.28 - loosely connected
**Members:** 9 nodes

## Members
- [[BROKER_ENV_NAMES]] - code - src/lib/safety/config.ts
- [[COINBASE_ENV_NAMES]] - code - src/lib/safety/config.ts
- [[ConnectorCenterSnapshot]] - code - src/app/terminal/connector-actions.ts
- [[EnvPresenceRow]] - code - src/lib/connectors/runtime-env.ts
- [[VENUES_1]] - code - src/lib/connectors/venue-presence.ts
- [[VenuePresenceRow]] - code - src/lib/connectors/venue-presence.ts
- [[listVenuePresence()]] - code - src/lib/connectors/venue-presence.ts
- [[venue-presence.test.ts]] - code - src/lib/connectors/venue-presence.test.ts
- [[venue-presence.ts]] - code - src/lib/connectors/venue-presence.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Venue_Presence_Monitoring
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Connector Management Actions]]
- 5 edges to [[_COMMUNITY_Binance Gateway Integration]]
- 3 edges to [[_COMMUNITY_Broker Environment Config]]
- 2 edges to [[_COMMUNITY_Runtime Environment Persistence]]
- 1 edge to [[_COMMUNITY_Alpaca Gateway Integration]]

## Top bridge nodes
- [[venue-presence.ts]] - degree 14, connects to 4 communities
- [[BROKER_ENV_NAMES]] - degree 3, connects to 2 communities
- [[COINBASE_ENV_NAMES]] - degree 3, connects to 2 communities
- [[listVenuePresence()]] - degree 4, connects to 1 community
- [[VenuePresenceRow]] - degree 4, connects to 1 community