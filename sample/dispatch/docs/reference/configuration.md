---
title: Configuration keys
type: reference
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Configuration keys

Read once at startup into `internal/config.Config`. There is no `os.Getenv` elsewhere in the codebase.

| Key | Type | Default | Required | Notes |
|---|---|---|---|---|
| `DATABASE_URL` | string | — | yes | `timestamptz` columns; the driver must be in UTC |
| `REDIS_URL` | string | — | yes | Rate limiter state only. Losing it costs limits, not messages |
| `QUEUE_URL` | string | — | yes | `dispatch-outbound`. Visibility timeout 300s |
| `QUEUE_DLQ_URL` | string | — | yes | Redrive target after 5 receives |
| `HTTP_ADDR` | string | `:8080` | no | API listen address |
| `WORKER_CONCURRENCY` | int | `8` | no | Goroutines claiming from the queue |
| `WORKER_CLAIM_BATCH` | int | `10` | no | SQS max is 10; larger values are clamped |
| `RETRY_MAX_ATTEMPTS` | int | `5` | no | Must stay at or below the queue redrive count |
| `RETRY_BASE_DELAY` | duration | `2s` | no | Exponential, full jitter |
| `PROVIDER_TIMEOUT` | duration | `10s` | no | Per-attempt. Must stay under the visibility timeout |
| `SES_REGION` | string | `eu-west-1` | for email | |
| `SES_CONFIGURATION_SET` | string | — | no | Enables provider-side delivery events |
| `TWILIO_ACCOUNT_SID` | string | — | for SMS | From the `dispatch` secret |
| `TWILIO_AUTH_TOKEN` | secret | — | for SMS | From the `dispatch` secret |
| `SUPPRESSION_API_URL` | string | — | yes | CRM suppression list. Read-only |
| `LOG_LEVEL` | string | `info` | no | `debug` logs every provider request line |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | string | — | no | Traces are dropped when unset |

## Constraints between keys

- `PROVIDER_TIMEOUT` × `RETRY_MAX_ATTEMPTS` must stay below the queue visibility timeout, or a message is redelivered while it is still being processed. See [delivery semantics](../explanation/delivery-semantics.md).
- `RETRY_MAX_ATTEMPTS` above the queue redrive count means messages reach the DLQ before the application stops retrying.

## Vendor limits we depend on

| Provider | Limit | Effect when hit |
|---|---|---|
| SES | 14 sends/second per account | `Throttling`, classified retryable |
| Twilio | 100 messages/second per number | HTTP 429, classified retryable |
