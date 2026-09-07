# dispatch

Local notification-service example for engineers adopting the Axelerant documentation standard.

## Status

`poc` — local simulation only. No real notifications, customers, paging service or production deployment.

## Requirements

Python 3.14.7 is the target CI runtime. Python 3.12 or newer is supported; the preparation tests ran on 3.13.5.
GNU Make is a command convenience; there are no third-party runtime packages. The API binds only to loopback.

## Quick start

From `sample/dispatch` in this repository:

```bash
make up
make send
make worker-once
make status
make smoke
```

The status includes one `sent` message. A receipt is written to `.state/outbox.jsonl`.
For interactive HTTP, run `make run` and start `make worker` in another terminal.

## Common commands

| Command | Does |
| --- | --- |
| `make up` | Creates the SQLite schema without changing existing claims |
| `make run` | Runs the API at http://127.0.0.1:8080 |
| `make worker` | Polls the queue until interrupted |
| `make worker-once` | Processes at most one ready message |
| `make send` | Enqueues a local example email |
| `make status` | Reports counts by delivery state |
| `make test` | Runs behavior and concurrency tests |
| `make smoke` | Tests the complete HTTP-to-receipt flow |
| `make docs-check` | Runs the documentation audit |
| `make verify` | Runs syntax, behavior and documentation checks |
| `make package` | Writes a source archive under dist/ |
| `make clean` | Deletes only generated state and archives |

## How we work here

Change behavior, tests and documentation together. Preserve historical ADRs. New queue or provider guarantees need a new decision record.

## Ownership

Team: `@axelerant/platform-team`. Support and escalation: repository issues, assigned to the owning team.
All example operational information is fictional and public-safe.

## Documentation

- [Documentation map](docs/README.md) — where do I begin?
- [First notification](docs/tutorials/first-notification.md) — what happens after acceptance?
- [Run locally](docs/how-to/run-locally.md) — how do I start the API and worker?
- [Architecture](docs/explanation/architecture.md) — why separate delivery?
- [API reference](docs/reference/api.md) — which routes exist?
- [Alert response](docs/runbooks/README.md) — how do the local response exercises work?

## Distribution

Included in the reference repository. `make package` creates a local source ZIP, not a production deployment.
