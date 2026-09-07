# Dispatch — a documented service

A small notification service, written to be read rather than run in anger. It
exists to show what a fully documented repository looks like under Axelerant's
engineering documentation standard, at the largest of the three tiers.

Everything here is fictional. There is no such service, the alert names are
invented, and the operational detail describes this local example and nothing
else.

## What to look at

| Path | Why it is interesting |
| --- | --- |
| `sample/dispatch/README.md` | The front door: status, requirements, quick start, commands, ownership |
| `sample/dispatch/docs/` | The full tree — tutorials, how-to, reference, explanation, decisions, runbooks |
| `sample/dispatch/docs/adr/` | Three decision records, including a superseded pair |
| `sample/dispatch/docs/runbooks/` | Runbooks named after the alerts in `alerts/alerts.json`, so neither side can drift |
| `sample/dispatch/docs/explanation/architecture.md` | C4 context and container diagrams, written inline |
| `sample/dispatch/.axelerant/repo.yml` | How a repository declares its tier, owner, visibility and on-call status |

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
