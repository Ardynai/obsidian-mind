---
source_file: "src/lib/safety/receipts.ts"
type: "code"
community: "Order Audit Reconciliation"
location: "L753"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Order_Audit_Reconciliation
---

# validateReceipt()

## Connections
- [[assertIdentifier()]] - `calls` [EXTRACTED]
- [[assertPositiveFinite()]] - `calls` [EXTRACTED]
- [[groupReceipts()]] - `indirect_call` [INFERRED]
- [[loadExecutionReceipts()]] - `indirect_call` [INFERRED]
- [[persistExecutionReceipt()]] - `calls` [EXTRACTED]
- [[receipts.ts]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Order_Audit_Reconciliation