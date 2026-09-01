---
title: Run dispatch locally
type: how-to
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Run dispatch locally

## Before you start

- Go 1.23 (`go version`)
- Docker Compose 2.29 (`docker compose version`)
- `awslocal` for talking to LocalStack: `pipx install awscli-local`

No AWS credentials are needed. The compose stack runs LocalStack in place of SQS and SES.

## Steps

```bash
cp .env.example .env
make up            # postgres:16, redis:7, localstack:3
make migrate
make run
```

`make run` starts the API and the dispatcher in one process, which is the usual local setup. To reproduce a queue problem, run them apart:

```bash
make run-api       # :8080, accepts and enqueues only
make worker        # claims from SQS, delivers
```

## Check it works

```bash
curl -s localhost:8080/healthz
# {"status":"ok","db":"ok","queue":"ok"}
```

If `queue` is `degraded`, LocalStack has not finished creating `dispatch-outbound`. Wait five seconds and retry.

## Reset

```bash
make down          # removes volumes; next make up is a clean database
```

## When it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `dial tcp :5432: connect: connection refused` | Postgres has not finished starting | Wait, then `make migrate` |
| `make test-integration` passes instantly | Stack is down, so every test skipped | `make up`, then check the test count |
| Messages stay `queued` | Only the API is running | Start `make worker` |
| `NoSuchQueue` | LocalStack was reset without recreating the queue | `make down && make up` |

## Related

- [Configuration keys](../reference/configuration.md)
- [Deliver your first notification](../tutorials/first-notification.md)
