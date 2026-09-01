---
title: HTTP API
type: reference
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# HTTP API

Generated from `api/openapi.yaml` by `make openapi`. Do not edit by hand; the next generation will
overwrite it. Change the spec.

Base URL: `https://dispatch.internal`. All requests carry `Authorization: Bearer <service-token>`,
scoped to one sender key.

## POST /v1/messages

Accepts a message and queues it. Returns before delivery is attempted.

| Field | Type | Required | Notes |
|---|---|---|---|
| `sender_key` | string | yes | Must match a sender the token is scoped to |
| `channel` | enum | yes | `email`, `sms`, `push` |
| `to` | string | yes | Address or number, validated per channel |
| `subject` | string | email only | Rejected for `sms` |
| `body` | string | yes | Rendered by the producer, not by dispatch |
| `idempotency_key` | string | no | Deduplicates retries of this call, not deliveries |

| Status | Meaning |
|---|---|
| 202 | Queued. Body carries `id` and `status: queued` |
| 400 | Validation failed. Body names the field |
| 403 | Token is not scoped to `sender_key` |
| 422 | Recipient is on the suppression list |
| 503 | Suppression list unreachable; retry |

## GET /v1/messages/{id}

Returns the current row, including `status`, `attempts` and `last_error`.

| Status | Meaning |
|---|---|
| 200 | Found |
| 404 | Unknown id, or the body has passed its 30-day retention |

## POST /v1/senders

Creates a sender. Restricted to platform tokens.

| Field | Type | Required |
|---|---|---|
| `key` | string | yes |
| `from` | string | yes |
| `rate_per_minute` | int | yes |

## GET /healthz

No authentication. Returns `{"status","db","queue"}`. `queue: degraded` means the queue is
unreachable; the API keeps accepting and the backlog grows.
