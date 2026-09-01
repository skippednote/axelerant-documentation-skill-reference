# axelerant-documentation-skill-reference — agent instructions

| Surface | Audience | Shape |
|---|---|---|
| `README.md` and `skills/*/references/` | Human engineers | What the contract is and how to apply it. |
| `AGENTS.md` (this file) | Coding agents | Rules for changing this repo. Slim. |

## Hard rules

- `references/contract.md` and `scripts/docs_audit.py` change in the same commit. A contract the script does not enforce is a suggestion.
- Never relax a check to make this repo pass. Fix the repo, or change the contract deliberately and say so in the PR.
- `sample/dispatch` must keep passing `--strict`. It is the executable proof that the contract is satisfiable.
- Do not add a rule the script cannot check unless you say in the PR why it is unenforceable.

## Conventions that differ from the defaults

- The audit strips fenced and inline code before scanning prose, so a document may name the tokens it rejects.
- `.axelerant/audit-ignore` is for files that must contain rejected tokens in prose. Adding to it needs a reason in the PR.

## Pitfalls

- Editing `sample/dispatch/.axelerant/docs_audit.py` instead of the source copy under `skills/`. The sample's copy is a snapshot; regenerate it with `make sync-sample`.
- The Vale style and the `FLUFF` regex in the script hold the same list twice. Change both.

## Before claiming done

```bash
python3 skills/axelerant-engineering-documentation/scripts/docs_audit.py . --strict
python3 skills/axelerant-engineering-documentation/scripts/docs_audit.py sample/dispatch --strict
```

## Where to look

| Need | Go to |
|---|---|
| The rules themselves | `skills/axelerant-engineering-documentation/references/contract.md` |
| How an existing repo is migrated | `.../references/brownfield.md` |
| How a new repo is set up | `.../references/greenfield.md` |
| What the output looks like | `sample/dispatch/` |
