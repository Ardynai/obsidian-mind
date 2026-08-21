---
source_file: "src/lib/safety/kernel.ts"
type: "code"
community: "Broker Order Safety"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Broker_Order_Safety
---

# kernel.ts

## Connections
- [[BrokerAck]] - `imports` [EXTRACTED]
- [[BrokerGateway]] - `imports` [EXTRACTED]
- [[BrokerGatewayName]] - `imports` [EXTRACTED]
- [[BrokerOrder]] - `imports` [EXTRACTED]
- [[BrokerPosition]] - `imports` [EXTRACTED]
- [[ControllableBrokerGateway]] - `imports` [EXTRACTED]
- [[ExecuteFlattenRequest]] - `contains` [EXTRACTED]
- [[ExecuteOrderIntentRequest]] - `contains` [EXTRACTED]
- [[ExecuteOrderIntentsRequest]] - `contains` [EXTRACTED]
- [[ExecutionReceiptSink]] - `contains` [EXTRACTED]
- [[FlattenAuditSink]] - `contains` [EXTRACTED]
- [[FlattenExecutionResult]] - `contains` [EXTRACTED]
- [[KernelBatchExecutionResult]] - `contains` [EXTRACTED]
- [[KernelExecutionResult]] - `contains` [EXTRACTED]
- [[KernelState]] - `imports` [EXTRACTED]
- [[OrderIntent]] - `imports` [EXTRACTED]
- [[ProvenanceEvent_1]] - `imports` [EXTRACTED]
- [[RiskDecision]] - `imports` [EXTRACTED]
- [[SafetyAuditSink]] - `contains` [EXTRACTED]
- [[SafetyLimits]] - `imports` [EXTRACTED]
- [[SafetyRiskContext]] - `contains` [EXTRACTED]
- [[auditEvent()]] - `contains` [EXTRACTED]
- [[brokerOrderAuditRef()]] - `imports` [EXTRACTED]
- [[client-order-id.ts]] - `imports_from` [EXTRACTED]
- [[clientOrderIdLimit()]] - `imports` [EXTRACTED]
- [[cloneRiskContext()]] - `contains` [EXTRACTED]
- [[compactClientOrderId()]] - `imports` [EXTRACTED]
- [[compactFlattenClientOrderId()]] - `imports` [EXTRACTED]
- [[config.ts_1]] - `imports_from` [EXTRACTED]
- [[controls.test.ts]] - `imports_from` [EXTRACTED]
- [[controls.ts]] - `imports_from` [EXTRACTED]
- [[decisionReason()]] - `contains` [EXTRACTED]
- [[evaluate()]] - `contains` [EXTRACTED]
- [[execute()]] - `contains` [EXTRACTED]
- [[executeBatch()]] - `contains` [EXTRACTED]
- [[executeFlatten()]] - `contains` [EXTRACTED]
- [[flattenAuditRef()]] - `contains` [EXTRACTED]
- [[flattenOrder()]] - `contains` [EXTRACTED]
- [[guardBrokerMutations()]] - `contains` [EXTRACTED]
- [[index.ts_15]] - `re_exports` [EXTRACTED]
- [[isNonNegativeFinite()]] - `contains` [EXTRACTED]
- [[isPositiveFinite()]] - `contains` [EXTRACTED]
- [[isRemoteBrokerGatewayName()]] - `imports` [EXTRACTED]
- [[kernel.test.ts]] - `imports_from` [EXTRACTED]
- [[lock.test.ts]] - `imports_from` [EXTRACTED]
- [[maximumPermittedNotional()]] - `contains` [EXTRACTED]
- [[normalizeSymbol()]] - `contains` [EXTRACTED]
- [[normalizedSymbols()]] - `contains` [EXTRACTED]
- [[order-audit.ts]] - `imports_from` [EXTRACTED]
- [[projectRiskContext()]] - `contains` [EXTRACTED]
- [[readBrokerPositions()]] - `contains` [EXTRACTED]
- [[simulation-kernel.ts]] - `imports_from` [EXTRACTED]
- [[toBrokerOrder()]] - `contains` [EXTRACTED]
- [[types.ts_2]] - `imports_from` [EXTRACTED]
- [[types.ts_9]] - `imports_from` [EXTRACTED]
- [[validateInput()]] - `contains` [EXTRACTED]
- [[validatedPositions()]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Broker_Order_Safety