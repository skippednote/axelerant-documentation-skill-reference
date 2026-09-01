---
name: axelerant-engineering-documentation
description: Set up or repair repository documentation to the Axelerant Engineering Documentation Standard — tiered README + docs/ contract, MADR ADRs, alert-named runbooks, C4/Mermaid diagrams, frontmatter with last_verified, and the anti-fluff rules. Use when asked to document a repo, add or restructure docs/, write an ADR or runbook, audit or fix documentation, or set up docs for a new project. Handles both brownfield (existing code, existing or absent docs) and greenfield (new repo).
---

# Axelerant Engineering Documentation

Produce documentation that a stranger can act on, and that a linter can check. The contract is normative: do not invent alternative layouts, extra folders, or extra files.

## Before anything

1. Read `references/contract.md`. It is the full spec. Everything below assumes it.
2. Read `references/anti-fluff.md`. It governs what you are allowed to write. Violating it is worse than writing nothing.
3. Determine the tier. If `.axelerant/repo.yml` exists, use it. If not, classify:
   - **Tier 0** — one deployable artefact consumed elsewhere: shared module, action, CLI, theme, library.
   - **Tier 1** — one deployable application: client site, POC, internal app.
   - **Tier 2** — multiple services, or long-lived product, or on-call exists.
   When the repo sits on a boundary, pick the lower tier. Ceremony nobody maintains is worse than a gap.
4. Confirm the tier and the owner with the user before writing files. Those two choices drive everything and you cannot infer the owner.

## Which workflow

| Situation | Follow |
|---|---|
| Repo has code already, docs absent, partial, or in a different layout | `references/brownfield.md` |
| New or empty repo | `references/greenfield.md` |
| One ADR or one runbook needed | `references/contract.md`, sections 6 and 7, plus the templates |
| "Is this repo compliant?" | Run `scripts/docs_audit.py` |
| A diagram was written or changed | Run `scripts/mermaid_check.py`, then `--render` if `npx` is available |

## Hard rules

- **Never write a file you cannot ground.** Every statement comes from code you read, a command you ran, or an answer the user gave. If you cannot ground it, ask or leave the section out. A missing section is a visible gap; an invented one is a lie that outlives you.
- **Run the commands you document.** A quick start you have not executed is a guess. If you cannot run it, mark `last_verified` absent and say so in your summary.
- **No placeholder files.** Never create a file whose content is a heading and a `TODO`. Create it when you have the content.
- **No forward declarations.** Never write an index entry for a file that does not exist, and never write a status document about documentation you plan to write.
- **Delete rather than migrate filler.** Per-feature catalogues, roadmap folders and docs-about-docs are removed, not relocated. Say what you deleted.
- **Validate every diagram you write.** Run `scripts/mermaid_check.py <repo>` after writing any Mermaid block, and `--render` when `npx` is available. A diagram that fails to parse renders as a red error box on GitHub, which is worse than no diagram. The commonest cause is a semicolon inside note or label text: it separates statements and truncates the block.
- **Stop at the contract.** Do not add `CONTRIBUTING.md`, `SECURITY.md`, badges, tables of contents or extra folders unless the user asks.

## Output

End every run with:

1. Files created, modified, deleted — as paths.
2. Sections left empty and the question that would fill each.
3. `scripts/docs_audit.py` result, and `scripts/mermaid_check.py` if you wrote or changed a diagram.

Do not claim the docs are complete. State what is grounded and what is not.
