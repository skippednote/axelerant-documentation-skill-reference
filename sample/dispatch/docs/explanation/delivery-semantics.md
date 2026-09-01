---
title: Delivery semantics
type: explanation
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Delivery semantics

dispatch delivers at least once. A recipient can receive the same notification twice. This page explains when, why we chose it, and what it costs.

## When a duplicate happens

Three paths produce one.

**The visibility timeout expires mid-send.** The dispatcher claims a message, calls the provider, and the provider takes longer than the remaining visibility window. SQS redelivers to another worker while the first attempt is still in flight. Both succeed. The recipient gets two.

This is why `PROVIDER_TIMEOUT` × `RETRY_MAX_ATTEMPTS` must stay under the queue's 300-second visibility timeout. That constraint is not decoration; violating it turns a rare duplicate into a routine one.

**The provider succeeds and the status write fails.** The vendor accepted the message, then the database write recording `sent` failed. The row still says `queued`, so the next claim sends again.

**A worker is killed between send and acknowledge.** Same shape as the previous case, caused by a pod eviction rather than a database error.

## Why not exactly-once

Exactly-once across a network boundary we do not control is not available. SES and Twilio expose no idempotency key that covers the whole send path, so the best we could do is a local dedupe window that guesses. A guess that suppresses a real second send is worse than a duplicate: a password reset that never arrives generates a support ticket, while a duplicate generates a shrug.

The full reasoning is in [ADR 0002](../adr/0002-at-least-once-delivery.md).

## What this costs consumers

Producers must make their notifications tolerable to receive twice. In practice that means:

- No side effects in the notification itself. A link in the body must be idempotent when followed twice.
- One-time codes carry their own expiry and single-use enforcement on the producer's side, not on delivery uniqueness.
- Anything that must not be duplicated is not a notification. It is a job with its own transactional guarantees.

## What we do to keep duplicates rare

- The visibility timeout is set well above the worst observed provider latency, and the constraint between it and the retry keys is checked at startup — dispatch refuses to boot on a violating configuration.
- Status writes happen immediately after the provider call, before any other work.
- The dispatcher handles `SIGTERM` by finishing the in-flight send before exiting, within the pod's termination grace period.

None of these make duplicates impossible. They make them rare enough that the tradeoff holds.
