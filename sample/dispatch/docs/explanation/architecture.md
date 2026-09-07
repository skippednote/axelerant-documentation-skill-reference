---
title: Architecture
type: explanation
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: source-review
---

# Architecture

## Context and scope

A caller submits notifications; the local fixture persists requests and writes delivery receipts instead of contacting external vendors.

```mermaid
C4Context
  Person(caller, "Caller", "Submits a notification")
  System(dispatch, "dispatch", "Accepts and processes local notifications")
  System_Ext(sink, "Local receipt sink", "Represents a provider")
  Rel(caller, dispatch, "Submit and query", "HTTP")
  Rel(dispatch, sink, "Write receipt", "File append")
```

## Solution strategy

Acceptance and delivery are separate. Returning 202 after a database commit avoids blocking the caller on provider behavior. The cost is a state machine and delayed completion.

SQLite replaces the earlier fictional cloud queue for this executable example. It eliminates service installation and credentials, but does not demonstrate a distributed broker. [ADR 0003](../adr/0003-executable-local-example.md) records this change without erasing earlier decisions.

## Building blocks

```mermaid
C4Container
  System_Boundary(local, "dispatch") {
    Container(api, "API", "Python", "Validates and stores requests")
    Container(worker, "Worker", "Python", "Claims and processes ready work")
    ContainerDb(db, "Queue and messages", "SQLite", "State, leases and attempts")
    Container(sink, "Receipt sink", "JSON Lines", "Local provider substitute")
  }
  Rel(api, db, "Insert and read", "SQL")
  Rel(worker, db, "Claim and finish", "SQL")
  Rel(worker, sink, "Append", "File")
```

## Runtime view

```mermaid
sequenceDiagram
  participant C as Caller
  participant A as API
  participant Q as SQLite
  participant W as Worker
  participant S as Receipt sink
  C->>A: Submit
  A->>Q: Commit queued record
  A-->>C: 202 with identifier
  W->>Q: Claim with token and lease
  W->>S: Append receipt
  W->>Q: Finish only if token still owns claim
```

## Crosscutting concepts

Claims use an immediate SQLite transaction. A lease expires after 30 seconds; a stale worker cannot overwrite a newer claim token. The receipt side effect can still repeat, so this is not exactly-once delivery. The public sample contains no real recipient data.
