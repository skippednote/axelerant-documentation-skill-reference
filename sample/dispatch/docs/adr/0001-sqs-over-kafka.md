---
title: Use SQS for the outbound queue
type: adr
owner: "@axelerant/platform-team"
status: accepted
date: 2026-03-11
deciders: ["@axelerant/platform-team"]
---

## Context and problem statement

dispatch needs a queue between accepting a message and delivering it, so that a producer's request does not block on a vendor call. The queue must survive a worker crash, redeliver unacknowledged work, and hold a poison message aside after repeated failures.

At the time the platform already ran Kafka for the event bus, so reusing it was the path of least new infrastructure. The question was whether the event bus is the right shape for a work queue.

## Considered options

- **Kafka, a dedicated topic.** Already operated, already monitored, no new vendor surface. Redelivery would be built on consumer group offsets, and a poison message would need a manual offset skip or a side topic.
- **SQS with a redrive policy.** Per-message acknowledgement, visibility timeout and DLQ are primitives rather than things we implement. New infrastructure, but managed.
- **A database-backed queue,** claiming rows with `FOR UPDATE SKIP LOCKED`. No new infrastructure at all. Delivery work becomes contention on the same database that stores the messages.

## Decision

SQS, because per-message acknowledgement and a redrive policy are exactly the semantics a delivery queue needs, and Kafka gives us neither without building them.

The deciding factor was poison-message handling. A single undeliverable message on a Kafka partition blocks everything behind it until someone intervenes on the offset. On SQS it moves to the DLQ after five receives and the rest of the queue keeps moving. For a service whose job is delivering to unreliable third parties, that difference decides it.

## Consequences

**Good**
- Redelivery, visibility timeout and DLQ are configuration, not code.
- A stuck message affects one message.
- Depth is a first-class metric, so the alert and its runbook are straightforward.

**Bad**
- A second queue technology to operate and reason about.
- No ordering. Two messages to the same recipient can arrive out of order, and nothing in the design prevents it.
- LocalStack does not enforce visibility timeout faithfully, so timeout-related bugs do not reproduce locally.

**Forecloses**
- Replaying the outbound stream for analytics. If we want that later it needs a separate event emitted alongside the send, not a queue replay.
