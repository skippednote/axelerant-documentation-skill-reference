---
title: Run dispatch locally
type: how-to
owner: "@axelerant/platform-team"
last_verified: 2026-09-03
verification_method: automated-test
---

# Run dispatch locally

## Start

```bash
make up
make run
```

The API binds to http://127.0.0.1:8080. Run `make worker` in another terminal for continuous delivery. Use Ctrl-C to stop either process.

## Exercise a request

```bash
make send
make worker-once
make status
```

The sent count rises by one. `make smoke` runs an isolated version with an ephemeral HTTP port and no shared state.

## Reset

Stop the API and worker first, then run:

```bash
make clean
make up
```

Reset discards example messages and receipts. It is never a production recovery step.
The variable `DISPATCH_STATE` is read from the process environment; copying `.env.example` does not load it automatically.
