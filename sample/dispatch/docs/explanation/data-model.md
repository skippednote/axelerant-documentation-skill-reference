---
title: Data model
type: explanation
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Data model

Four tables. The message row is the source of truth for content and state; the queue only carries identifiers, so a redelivery re-reads the current row rather than replaying a stale copy.

```mermaid
erDiagram
    SENDERS ||--o{ NOTIFICATIONS : "sends as"
    NOTIFICATIONS ||--o{ ATTEMPTS : "has"
    ATTEMPTS }o--|| PROVIDERS : "used"

    SENDERS {
        uuid id PK
        text key UK "stable, referenced by producers"
        text from_address
        int rate_per_minute
        timestamptz created_at
    }
    NOTIFICATIONS {
        uuid id PK
        uuid sender_id FK
        channel channel "enum: email, sms, push"
        text to_address
        text subject "null for sms"
        text body "nulled after 30 days"
        status status "enum: queued, sent, failed"
        int attempts
        text last_error
        timestamptz created_at
        timestamptz updated_at
    }
    ATTEMPTS {
        uuid id PK
        uuid notification_id FK
        text provider_name FK
        int attempt_no
        text outcome "accepted, retryable, permanent"
        text vendor_receipt
        int latency_ms
        timestamptz created_at
    }
    PROVIDERS {
        text name PK
        channel channel
        bool enabled
    }
```

## Why attempts are a separate table

A counter on the message would answer "how many tries", which is all the retry logic needs. It would not answer "which provider failed, with what error, how slowly" — the question every incident asks. Keeping attempts as rows costs one insert per try and makes the provider error-rate metric a query rather than a log scrape.

The cost is table growth: attempts outnumber notifications, and nothing prunes them yet. That is a known gap.

## Message lifecycle

`status` moves in one direction only. There is no path back from `failed`; a message that must go out again is a new message, so the audit trail stays intact.

```mermaid
stateDiagram-v2
    [*] --> queued: API accepts and persists
    queued --> queued: retryable error, attempts + 1
    queued --> sent: provider accepts
    queued --> failed: permanent error
    queued --> dlq: 5 receives, SQS redrives
    dlq --> queued: operator redrives after the cause is fixed
    sent --> [*]
    failed --> [*]
```

`dlq` is not a column. It is a queue location, shown here because operationally it is a state someone has to reason about, and the queue depth runbook treats it as one.

## Constraints worth knowing

- `senders.key` is the stable identifier producers reference. `senders.id` is internal and may change on a restore.
- `channel` is a Postgres enum. Values can be added and never removed, which makes adding a channel a one-way migration.
- Every timestamp is `timestamptz`, compared in UTC. A driver in local time produces retry storms at the DST boundary.
- `notifications.body` is nulled by a scheduled job at 30 days. The row survives for reporting.
