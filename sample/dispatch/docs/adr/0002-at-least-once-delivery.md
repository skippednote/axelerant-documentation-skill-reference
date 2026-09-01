---
title: Deliver at least once
type: adr
owner: "@axelerant/platform-team"
status: accepted
date: 2026-03-18
deciders: ["@axelerant/platform-team"]
---

## Context and problem statement

A message can be sent by the provider and then fail to be recorded as sent, or be redelivered while an attempt is still in flight. Either way the recipient can receive two copies. We had to decide whether to attempt suppression of the second copy, and to state the guarantee producers can rely on.

The trigger was a billing producer asking whether they needed their own idempotency handling. The honest answer required deciding this first.

## Considered options

- **At least once, stated openly.** Producers must tolerate duplicates. No dedupe machinery.
- **Best-effort dedupe on a fingerprint** of sender, recipient, channel and body hash, within a five-minute window in Redis. Suppresses most duplicates.
- **Exactly-once.** Would require an idempotency key honoured end to end by the provider.

## Decision

At least once, stated in the API documentation and in this repository, with no dedupe layer.

Exactly-once is not available: neither SES nor Twilio exposes an idempotency key covering the whole send path, so any guarantee we made would be a guess dressed as a contract. Between the remaining two, the fingerprint window fails in the more expensive direction. A legitimate second send — the same password reset requested twice in four minutes — looks identical to a duplicate and would be suppressed. A missing password reset generates a support ticket and an angry user; a duplicate generates a shrug.

## Consequences

**Good**
- The guarantee is true, so producers can design against it.
- No dedupe state to operate, size or debug.
- A failure mode we cannot prevent is documented rather than hidden behind machinery that mostly works.

**Bad**
- Every producer carries the tolerance requirement, and new producers have to learn it.
- Duplicate rate is a number we watch rather than a number we control.

**Forecloses**
- Marketing-style bulk sends where a duplicate is a brand problem. Those need a different service, or a dedupe layer added deliberately with this ADR superseded.
