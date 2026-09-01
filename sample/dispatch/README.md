# dispatch

Outbound notification service: takes a message from any internal service and delivers it by email, SMS or push.

## Status

`active` · production `https://dispatch.internal` · staging `https://dispatch.stg.internal`

## Requirements

- Go 1.23
- PostgreSQL 16
- Redis 7
- Docker Compose 2.29 (local only)
- AWS credentials with `sqs:ReceiveMessage` on `dispatch-outbound` (local development uses LocalStack instead)

## Quick start

```bash
git clone git@github.com:axelerant/dispatch.git
cd dispatch
cp .env.example .env          # defaults point at the compose stack
make up                       # postgres, redis, localstack
make migrate
make run                      # serves on :8080
curl -s localhost:8080/healthz
```

`make up` takes about 40 seconds on first run while it pulls images.

## Common commands

| Command | Does |
|---|---|
| `make up` | Starts postgres, redis and localstack via Docker Compose |
| `make down` | Stops the stack and removes volumes |
| `make run` | Runs the API and the dispatcher in one process |
| `make worker` | Runs only the dispatcher, against the same database |
| `make migrate` | Applies pending migrations |
| `make migrate-new name=add_channel` | Creates an empty migration pair |
| `make test` | Unit tests |
| `make test-integration` | Integration tests; needs `make up` first |
| `make lint` | golangci-lint and gofumpt |
| `make openapi` | Regenerates `docs/reference/api.md` from `api/openapi.yaml` |

## How we work here

Branch from `main` as `<ticket>-<short-slug>`. Commits are prefixed with the ticket key. Every PR needs one review and a green `docs-check`. Squash on merge.

## Ownership

- Team: `@axelerant/platform-team`
- Slack: `#platform-dispatch`
- Escalation: platform on-call rota, then the engineering manager for platform

## Documentation

- [Documentation index](docs/index.md) — where everything is
- [Run it locally](docs/how-to/run-locally.md) — how do I get a working copy?
- [Deploy and roll back](docs/how-to/deploy.md) — how does a change reach production?
- [Architecture](docs/explanation/architecture.md) — why is it split into API and dispatcher?
- [Delivery semantics](docs/explanation/delivery-semantics.md) — why can a recipient get two copies?
- [Runbooks](docs/runbooks/) — an alert fired, what now?
