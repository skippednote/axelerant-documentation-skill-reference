---
title: Security posture
type: explanation
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Security posture

## What dispatch holds

Recipient addresses and message bodies, both of which are personal data. Bodies are rendered by the producer, so dispatch cannot know in advance whether a body contains anything sensitive. It is treated as though it always does.

- Message bodies are retained for 30 days, then nulled by a scheduled job. The row survives for reporting; the content does not.
- Bodies are never written to logs. `LOG_LEVEL=debug` logs provider request metadata, not payloads. This is enforced by a test, because it is the mistake most likely to be made again.
- Database encryption at rest is on by default in RDS; there is no field-level encryption.

## Trust boundaries

Producers are inside the platform and authenticate with a service token scoped to a sender key. A producer cannot send as another producer's sender. Vendors are outside; every call to them leaves the VPC through the NAT gateway and carries no data beyond the message itself.

The CRM suppression list is read on every send. If it is unavailable, dispatch fails the attempt rather than sending — a suppression list that cannot be consulted is treated as though everything is suppressed.

**Why this way.** The alternative, caching suppression locally and sending on a cache hit, keeps delivery working during a CRM outage but risks sending to someone who has withdrawn consent. A delayed notification is recoverable; a message to a suppressed recipient is a regulatory problem. We chose the recoverable failure.

## Secrets

Provider credentials live in the `dispatch` Kubernetes secret, sourced from Secrets Manager. They are not in the config struct defaults, not in `.env.example`, and not in any test fixture. Local development uses LocalStack, which needs no real credentials.

## Known gaps

- No per-recipient rate limit. A misbehaving producer can send one recipient many messages; only the per-sender limit constrains it.
- The 30-day body retention is enforced by a job, not by a database policy. If the job stops, bodies persist. There is no alert on that job.
