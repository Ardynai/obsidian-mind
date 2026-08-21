# Broker Environment Config

> 35 nodes · cohesion 0.11

## Key Concepts

- **config.ts** (62 connections) — `src/lib/safety/config.ts`
- **ev1-gateways.test.ts** (19 connections) — `src/lib/safety/gateways/ev1-gateways.test.ts`
- **lock.test.ts** (19 connections) — `src/lib/safety/lock.test.ts`
- **BrokerConfiguration** (14 connections) — `src/lib/safety/config.ts`
- **brokerConfigurationFromEnv()** (12 connections) — `src/lib/safety/config.ts`
- **missingNames()** (7 connections) — `src/lib/safety/config.ts`
- **ALPACA_ENDPOINTS** (6 connections) — `src/lib/safety/config.ts`
- **invalidVenue()** (6 connections) — `src/lib/safety/config.ts`
- **config.test.ts** (5 connections) — `src/lib/safety/config.test.ts`
- **alpaca.smoke.test.ts** (5 connections) — `src/lib/safety/gateways/alpaca.smoke.test.ts`
- **binanceConfigurationFromEnv()** (4 connections) — `src/lib/safety/config.ts`
- **coinbaseConfigurationFromEnv()** (4 connections) — `src/lib/safety/config.ts`
- **kalshiConfigurationFromEnv()** (4 connections) — `src/lib/safety/config.ts`
- **krakenConfigurationFromEnv()** (4 connections) — `src/lib/safety/config.ts`
- **oandaConfigurationFromEnv()** (4 connections) — `src/lib/safety/config.ts`
- **safePositiveInteger()** (4 connections) — `src/lib/safety/config.ts`
- **alpacaConfigurationFromEnv()** (3 connections) — `src/lib/safety/config.ts`
- **finiteNonNegative()** (3 connections) — `src/lib/safety/config.ts`
- **invalidEnvironment()** (3 connections) — `src/lib/safety/config.ts`
- **KALSHI_ENDPOINTS** (3 connections) — `src/lib/safety/config.ts`
- **nonBlank()** (3 connections) — `src/lib/safety/config.ts`
- **DEFAULT_SAFETY_LIMITS** (2 connections) — `src/lib/safety/config.ts`
- **SAFETY_ENV_NAMES** (2 connections) — `src/lib/safety/config.ts`
- **venueSelectorFromEnv()** (2 connections) — `src/lib/safety/config.ts`
- **VenueSelector** (1 connections) — `src/lib/safety/config.ts`
- *... and 10 more nodes in this community*

## Relationships

- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (20 shared connections)
- [Binance Gateway Integration](Binance_Gateway_Integration.md) (17 shared connections)
- [Broker Order Safety](Broker_Order_Safety.md) (12 shared connections)
- [Alpaca Gateway Integration](Alpaca_Gateway_Integration.md) (10 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (9 shared connections)
- [Multi-Venue Gateway Factory](Multi-Venue_Gateway_Factory.md) (7 shared connections)
- [Performance Comparison UI](Performance_Comparison_UI.md) (3 shared connections)
- [Venue Presence Monitoring](Venue_Presence_Monitoring.md) (3 shared connections)

## Source Files

- `src/lib/safety/config.test.ts`
- `src/lib/safety/config.ts`
- `src/lib/safety/gateways/alpaca.smoke.test.ts`
- `src/lib/safety/gateways/ev1-gateways.test.ts`
- `src/lib/safety/lock.test.ts`

## Audit Trail

- EXTRACTED: 211 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*