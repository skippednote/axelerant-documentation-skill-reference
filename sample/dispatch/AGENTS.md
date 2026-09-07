# dispatch agent instructions

| Surface | Audience | Owns |
|---|---|---|
| README.md and docs/ | Engineers | Setup, architecture and operations |
| AGENTS.md | Coding agents | Guardrails and completion checks |

## Hard rules

- Do not replace accepted ADR history. Supersede it with a new record.
- Keep the sample local-only and dependency-free.
- Do not reset active claims during startup or read operations.
- Preserve claim-token checks so a stale worker cannot overwrite a newer outcome.
- Never stamp evidence for an unexecuted procedure.
- Keep CLAUDE.md as the one-line import of this file.

## Before claiming done

```bash
make verify
```

The owning repository runs rendered diagram validation separately. A static check is not a successful render.

## Where to look

| Need | Page |
|---|---|
| Runtime | `docs/how-to/run-locally.md` |
| Retry semantics | `docs/explanation/delivery-semantics.md` |
| API | `docs/reference/api.md` |
| Decisions | `docs/adr/README.md` |
| Alerts | `docs/runbooks/README.md` |
