# The contract

Normative. Deviations need an ADR.

## 1. Tiers

Declared once in `.axelerant/repo.yml`:

```yaml
tier: 2                  # 0 | 1 | 2
kind: service            # service | site | library | action | poc | docs
owner: "@org/team"       # GitHub team handle; must match CODEOWNERS
client: acme             # omit for internal
on_call: true            # true -> docs/runbooks/ required
docs_review_days: 90     # staleness warning threshold
```

| Tier | Definition | Required |
|---|---|---|
| 0 | One artefact consumed elsewhere. Module, action, CLI, library, theme. | README only. **No `docs/`.** |
| 1 | One deployable application. | README + flat `docs/` of exactly five files. |
| 2 | Multiple services, or long-lived product, or on-call. | README + Diátaxis tree + `adr/` + `runbooks/`. |

Subfolders appear when a folder would hold three or more files. Not before.

## 2. README — all tiers

Cap 400 lines. Answers one question: can a stranger run this and know who to ask.

| # | Section | Required | Contents |
|---|---|---|---|
| 1 | `# <name>` | yes | One sentence under 120 characters. What it is, who for. |
| 2 | `## Status` | yes | `active` / `maintenance` / `archived` / `poc`, plus environment URLs. |
| 3 | `## Requirements` | yes | Exact versions. Must match what CI pins. |
| 4 | `## Quick start` | yes | Clone to running instance. Copy-pasteable. Executed before commit. |
| 5 | `## Common commands` | yes | Table of the 8–15 commands people run. |
| 6 | `## How we work here` | yes | Branch, commit, PR rules, or a link if the repo uses defaults. |
| 7 | `## Ownership` | yes | Team, GitHub handle, Slack channel, escalation. |
| 8 | `## Documentation` | tier 1+ | 4–8 links into `docs/`, each with the question it answers. |
| 9 | `## Distribution` | if applies | How the artefact is consumed: package name, mirror, action reference. |

Order is fixed. Sections are not renamed.

## 3. docs/ — Tier 1

Exactly these five. No others, no subfolders except `adr/` once a second decision exists.

```
docs/index.md              what this is, who for, the map
docs/getting-started.md    laptop to first working change
docs/architecture.md       arc42 subset + one C4 container diagram
docs/operations.md         environments, deploy, rollback, access, monitoring
docs/decisions.md          running decision log
```

## 4. docs/ — Tier 2

```
docs/index.md
docs/tutorials/            learning by doing. 1-3 files.
docs/how-to/               task recipes. Largest folder.
docs/reference/            lookup. Generated where a generator exists.
docs/explanation/          architecture.md, data-model.md, security.md
docs/adr/                  MADR, one file per decision
docs/runbooks/             one per alert. Only when on_call: true
docs/assets/               images and standalone diagram sources
```

A diagram that explains one page lives in that page as a fenced Mermaid block, so GitHub renders it and a change arrives as a reviewable diff. `assets/` exists only for files that are not tied to a single page, or for screenshots. Do not keep a `.mmd` copy of a diagram that is already inline; two copies of a diagram is one diagram and one future lie.

Diátaxis assignment, when unsure which folder a page belongs in:

| The reader is | Folder |
|---|---|
| learning the system for the first time | `tutorials/` |
| trying to complete a task now | `how-to/` |
| looking up a fact | `reference/` |
| trying to understand why | `explanation/` |

## 5. Frontmatter — every file under docs/

```yaml
---
title: Deploy to production
type: how-to        # tutorial | how-to | reference | explanation | runbook | index
owner: "@org/team"
last_verified: 2026-09-01
applies_to: "v2.4+" # optional
---
```

`last_verified` means a human executed the steps and they worked. Not "edited on". Set it only after running the commands. Runbooks expire hard at 180 days.

**ADRs are the exception.** A decision is not re-verified, it is superseded. ADR frontmatter is `title`, `type: adr`, `owner`, `status`, `date`, `deciders` — no `last_verified`, and it never goes stale:

```yaml
---
title: Use SQS for the outbound queue
type: adr
owner: "@org/team"
status: accepted    # proposed | accepted | superseded by NNNN | deprecated
date: 2026-03-11
deciders: ["@org/team"]
---
```

## 6. ADRs

Path `docs/adr/NNNN-kebab-title.md`. Four digits, never renumbered, never deleted. Superseding writes a new ADR and flips the old status.

Frontmatter per section 5. Sections, in order: Context and problem statement, Considered options, Decision, Consequences.

Rules:
- Two or more real options. One option is not a decision; do not write the ADR.
- Consequences carries a bad list. An ADR with no downside was an announcement.
- Write one for anything expensive to reverse: datastore, framework, hosting, auth, a service boundary, a deliberate deviation from a house default.
- Past ~50 ADRs, add `docs/adr/README.md` indexing accepted ones by area. Superseded drop out.

## 7. Runbooks

Path `docs/runbooks/<alert-name>.md`, named after the alert, not the subsystem. One per alert that can page a human. The alert definition links to the file.

Sections, in order: Trigger, Impact, Diagnose, Mitigate, Escalate, After.

- Diagnose steps are ordered, carry real commands, and state what a good result looks like.
- Mitigate puts the safe action first and marks the risky one risky.
- Escalate names a team, a channel, and the point at which you stop trying.
- Whoever is paged updates the file before closing the incident.

A single generic `operations/runbook.md` does not satisfy this.

## 8. Diagrams

- C4 Level 1 (system context): required at Tier 1 and 2. One diagram.
- C4 Level 2 (containers): required at Tier 2.
- Sequence diagrams: optional, for flows prose keeps failing on.
- Levels 3 and 4: banned. Not maintainable by hand.
- Mermaid only, inline in the page it explains. `.mmd` files under `docs/assets/diagrams/` only for diagrams not tied to a single page. No exported PNGs except UI screenshots, where the image is the content.
- Sequence diagrams earn their place where prose is densest: a race, a retry path, a multi-party handshake. A state diagram is worth it when a status column moves in more than two ways.

## 9. Agent files

- `AGENTS.md` at the root is the source of truth. Cap 200 lines.
- `CLAUDE.md` is one line: `@AGENTS.md`.
- Holds: rules, guardrails, conventions that differ from tool defaults, pitfalls, verification commands, a jump table into `docs/`.
- Does not hold: architecture, directory layouts, setup steps, or anything duplicated from `docs/`.

## 10. Must not exist

- `docs/features/f001…` or any per-feature catalogue.
- `docs/improvements/`, `docs/roadmap/`, `backlog-roadmap.md`.
- `DOCUMENTATION_STATUS.md`, `MASTER_INDEX.md`, `IMPLEMENTATION_SUMMARY.md`.
- GitHub wiki content.
- Loose markdown at the repo root other than README, AGENTS, CLAUDE, LICENSE, CHANGELOG.
- Links out to Confluence or Drive for anything needed to run the code.

## 11. Enforcement

Copy `references/templates/docs-workflow.yml` to `.github/workflows/docs.yml`. It calls the shared reusable workflow, so the contract, the audit script, the Vale style and the markdownlint config are pulled at a pinned ref rather than vendored into each repo.

| Check | Level | Fails on |
|---|---|---|
| contract | block | Missing README section, missing tier-required file, Tier 0 with a `docs/` |
| frontmatter | block | A file under `docs/` missing the fields for its type |
| placeholders | block | `TODO`, `TBD`, `<your-`, `REPLACE_WITH_`, `coming soon` in prose |
| banned register | block | The deny-list from `anti-fluff.md`, in prose |
| markdownlint | block | Structure |
| Vale | block | The same deny-list, in prose |
| links | block | A dead link in any markdown file |
| staleness | warn | `last_verified` past `docs_review_days`; blocks at 2x on Tier 2; runbooks block at 180 days |
| coupling | comment | A PR that changes code and no documentation |

Prose means: after fenced blocks and inline code are stripped. A document may name the tokens it rejects.

`.axelerant/audit-ignore` holds globs that are skipped, one per line, for files that must carry rejected tokens in prose. Adding to it needs a reason in the PR.

Roll out as `strict: false` for a quarter, then flip. New repos start at `strict: true`.
