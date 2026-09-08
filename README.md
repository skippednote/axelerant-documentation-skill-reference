# Dispatch — a documented service

A small notification service, written to be read rather than run in anger. It
exists to show what a fully documented repository looks like under Axelerant's
engineering documentation standard.

Everything here is fictional. There is no such service, the alert names are
invented, and the operational detail describes this local example and nothing
else.

## What to look at

| Path | Why it is interesting |
| --- | --- |
| `sample/dispatch/README.md` | The front door: status, requirements, quick start, commands, ownership |
| `sample/dispatch/docs/` | The four core files, then the folders this repository turned out to need |
| `sample/dispatch/docs/architecture.md` | C4 context and container diagrams, written inline |
| `sample/dispatch/docs/operations.md` | What breaks, what it looks like, and what to do about it |
| `sample/dispatch/docs/adr/` | Three decision records, including a superseded pair |
| `sample/dispatch/docs/runbooks/` | Runbooks named after the alerts in `alerts/alerts.json`, so neither side can drift |
| `sample/dispatch/.docs/repo.yml` | How a repository declares its kind, owner, visibility and on-call status |

Every repository gets the same shape: `docs/` with the core files its kind owes,
plus whatever folders it has enough pages to justify. The shape does not change
from repository to repository.

Every page under `docs/` carries an owner, a date, and the method that date
proves, which is the part most documentation leaves out.

## It runs

The service is real code with tests, so the documented commands are commands
that work rather than commands that look plausible.

```
cd sample/dispatch
make test
```

## Scope

This repository is the example only. The standard itself, the skill that
scaffolds and audits a repository against it, and the shared checks are internal
to Axelerant and are not published here.
