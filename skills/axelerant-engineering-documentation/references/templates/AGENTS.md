# <name> — agent instructions

| Surface | Audience | Shape |
|---|---|---|
| `docs/` | Human engineers | Onboarding, reference, runbooks. Self-contained. |
| `AGENTS.md` (this file) | Coding agents | Rules and pitfalls. Slim. Links into `docs/`. |

Facts live in `docs/`. This file links, never duplicates.

## Hard rules

- <What must never happen in this repo.>
- <What requires a human decision.>

## Conventions that differ from the defaults

- <Where this project departs from what the ecosystem assumes.>

## Pitfalls

- <A trap that has already cost someone a day.>

## Before claiming done

```bash
<the exact commands that constitute "it works">
```

## Where to look

| Need | Go to |
|---|---|
| Run it locally | `docs/how-to/run-locally.md` |
| Deploy | `docs/how-to/deploy.md` |
| Why it is shaped this way | `docs/explanation/architecture.md` |
| A past decision | `docs/adr/` |
