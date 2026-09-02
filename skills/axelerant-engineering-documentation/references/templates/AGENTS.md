# <name> — agent instructions

| Surface | Audience | Shape |
|---|---|---|
| `docs/` | Human engineers | Onboarding, reference, runbooks. Self-contained. |
| `AGENTS.md` (this file) | Coding agents | Rules and pitfalls. Slim. Links into `docs/`. |

Facts live in `docs/`. This file links, never duplicates.

At Component tier there is no `docs/`, so drop the table above and the jump table below, and keep
the rules, pitfalls and verification commands.

## Hard rules

- <What must never happen in this repository.>
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

Every path here must resolve, so build this table from the files that exist. At Project tier they
are flat under `docs/`; at Platform tier they sit under `how-to/`, `reference/` and `explanation/`.

| Need | Go to |
|---|---|
| Run it locally | <docs/getting-started.md at Project, docs/how-to/run-locally.md at Platform> |
| Deploy | <docs/operations.md at Project, docs/how-to/deploy.md at Platform> |
| Why it is shaped this way | <docs/architecture.md at Project, docs/explanation/architecture.md at Platform> |
| A past decision | <docs/decisions.md at Project, docs/adr/ at Platform> |
