---
title: Data model
type: explanation
owner: "@axelerant/platform-team"
last_verified: 2026-09-03
verification_method: source-review
---

# Data model

The messages table also acts as a single-host queue. UUIDs identify requests. Rows contain channel, recipient, body, status, attempts, earliest available time, lease expiry, claim token and last error.

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> processing: claim and increment attempts
  processing --> sent: receipt and matching token
  processing --> queued: failure with attempts remaining
  processing --> failed: attempts exhausted
  processing --> queued: expired lease with attempts remaining
  processing --> failed: expired lease at attempt limit
```

Separating queue and messages into two stores would resemble a production service but require cross-store reconciliation. One database is sufficient for a runnable teaching fixture, at the cost of single-host write contention.
