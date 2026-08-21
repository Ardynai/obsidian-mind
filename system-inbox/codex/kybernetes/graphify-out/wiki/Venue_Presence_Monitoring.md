# Venue Presence Monitoring

> 9 nodes · cohesion 0.28

## Key Concepts

- **venue-presence.ts** (14 connections) — `src/lib/connectors/venue-presence.ts`
- **listVenuePresence()** (4 connections) — `src/lib/connectors/venue-presence.ts`
- **VenuePresenceRow** (4 connections) — `src/lib/connectors/venue-presence.ts`
- **ConnectorCenterSnapshot** (3 connections) — `src/app/terminal/connector-actions.ts`
- **EnvPresenceRow** (3 connections) — `src/lib/connectors/runtime-env.ts`
- **BROKER_ENV_NAMES** (3 connections) — `src/lib/safety/config.ts`
- **COINBASE_ENV_NAMES** (3 connections) — `src/lib/safety/config.ts`
- **venue-presence.test.ts** (2 connections) — `src/lib/connectors/venue-presence.test.ts`
- **VENUES** (1 connections) — `src/lib/connectors/venue-presence.ts`

## Relationships

- [Connector Management Actions](Connector_Management_Actions.md) (6 shared connections)
- [Binance Gateway Integration](Binance_Gateway_Integration.md) (5 shared connections)
- [Broker Environment Config](Broker_Environment_Config.md) (3 shared connections)
- [Runtime Environment Persistence](Runtime_Environment_Persistence.md) (2 shared connections)
- [Alpaca Gateway Integration](Alpaca_Gateway_Integration.md) (1 shared connections)

## Source Files

- `src/app/terminal/connector-actions.ts`
- `src/lib/connectors/runtime-env.ts`
- `src/lib/connectors/venue-presence.test.ts`
- `src/lib/connectors/venue-presence.ts`
- `src/lib/safety/config.ts`

## Audit Trail

- EXTRACTED: 37 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*