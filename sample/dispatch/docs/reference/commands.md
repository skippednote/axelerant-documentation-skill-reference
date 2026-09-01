---
title: Command reference
type: reference
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Command reference

Everything the Makefile exposes. `make help` prints the same list.

## Stack

| Command | Does |
|---|---|
| `make up` | Starts postgres, redis, localstack |
| `make down` | Stops the stack and removes volumes |
| `make logs` | Tails all compose services |

## Run

| Command | Does |
|---|---|
| `make run` | API and dispatcher in one process |
| `make run-api` | API only |
| `make worker` | Dispatcher only |

## Database

| Command | Does |
|---|---|
| `make migrate` | Applies pending migrations |
| `make migrate-down` | Reverts the last migration; local only |
| `make migrate-new name=x` | Creates an up/down pair |
| `make psql` | Opens psql against the local database |
| `make psql-prod` | Port-forwards through the bastion, read-only role |

## Quality

| Command | Does |
|---|---|
| `make test` | Unit tests |
| `make test-integration` | Integration tests; requires `make up` |
| `make lint` | golangci-lint and gofumpt |
| `make openapi` | Regenerates `reference/api.md` from `api/openapi.yaml` |

## Operational

| Command | Does |
|---|---|
| `make dlq-peek` | Prints the first 10 messages on the DLQ without consuming |
| `make dlq-redrive n=50` | Moves up to 50 messages from the DLQ back to the main queue |
| `make queue-depth` | Prints approximate depth for both queues |
