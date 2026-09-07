---
title: Delivery semantics
type: explanation
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: source-review
---

# Delivery semantics

A receipt can be appended immediately before a worker crashes. If success was not recorded, the lease eventually expires and another worker can append the same message identifier again.

```mermaid
sequenceDiagram
  participant W1 as First worker
  participant S as Receipt sink
  participant Q as SQLite
  participant W2 as Recovery worker
  W1->>Q: Claim
  W1->>S: Append receipt
  Note over W1: Process stops before recording success
  W2->>Q: Reclaim after expiry
  W2->>S: Append repeated receipt
  W2->>Q: Record sent
```

Recording success before the append would avoid this duplicate window but lose accepted work when the process stops between those operations. The fixture chooses retryable processing and exposes stable identifiers, not guaranteed eventual delivery: three failures are terminal.

An expired worker's old token cannot update the newer claim. This protects queue state, not external exactly-once effects. [ADR 0003](../adr/0003-executable-local-example.md) defines the executable boundary.
