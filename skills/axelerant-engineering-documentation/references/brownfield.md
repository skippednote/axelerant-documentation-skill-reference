# Brownfield: an existing repo

The code is the source of truth. Existing documentation is a claim to be verified, not a starting point to be reformatted.

## Step 1 — Survey before writing

Gather, and keep the notes; they become the docs.

```bash
ls -a                                   # root files, stray markdown, agent files
cat .axelerant/repo.yml 2>/dev/null     # tier already declared?
find docs doc documentation -type f 2>/dev/null | head -50
ls .github/workflows/ 2>/dev/null       # what CI actually does
cat CODEOWNERS .github/CODEOWNERS 2>/dev/null
git log -1 --format=%cd                 # is this repo alive?
git log -1 --format=%cd -- README.md    # how far behind the README is
```

Read, in this order: the CI workflows, the build/dependency manifest, the entrypoint, the config loader, the migration directory, the deployment manifest. These tell you the truth about requirements, commands, environments and integrations. The old README tells you what someone believed in the past.

## Step 2 — Classify and confirm

Set the tier from the contract. Draft `.axelerant/repo.yml`. Confirm tier and owner with the user before writing anything else.

## Step 3 — Triage what exists

For every existing doc file, one of four verdicts. Record it; report it at the end.

| Verdict | When | Action |
|---|---|---|
| **Keep** | Accurate and belongs in the new layout | Move to its contract path, add frontmatter |
| **Fix** | Right subject, wrong or stale content | Rewrite from the code, then verify |
| **Delete** | Per-feature catalogue, roadmap, docs-about-docs, vendor scaffold text, forward declarations | Delete. Do not migrate. |
| **Ask** | Cannot tell whether it is still true | Leave in place, list it for the user |

Vendor scaffold READMEs — text describing a generator's template rather than this project — are always Delete.

## Step 4 — Map an existing tree onto the contract

| Found | Goes to |
|---|---|
| `architecture/`, `quality/`, `design/` | `explanation/` |
| `features/`, `integrations/`, `api/` | `reference/` (as tables, not prose) |
| `flows/` | `explanation/`, or a Mermaid sequence diagram |
| `operations/runbook.md` | Split into `runbooks/<alert>.md`, one per real alert |
| `improvements/`, `roadmap/` | Jira. Delete the files. |
| `local_setup.md`, `tools.md` | Tier 1 `getting-started.md`; Tier 2 `how-to/run-locally.md` |
| `how_to_work.md` | README `## How we work here` |
| `faqs.md` | Split: each real question becomes a `how-to/` page. Delete the rest. |
| `links.md` | `index.md` jump table |
| `content_types.md`, `custom_modules.md` | `reference/` |

If a target folder would hold fewer than three files, keep those files flat at the tier below.

## Step 5 — Verify, then write

For each command you are about to document, run it. Record what actually happened.

- The quick start runs on a clean checkout.
- Environment variables come from the config loader and the deploy manifest, not from an old `.env.example` alone.
- Version numbers come from CI and the lockfile.
- Only set `last_verified` on files whose commands you executed.

Write in this order, so later files can link to earlier ones: `.axelerant/repo.yml`, README, `docs/index.md`, the rest of `docs/`, `AGENTS.md` and `CLAUDE.md` last.

## Step 6 — Runbooks, only from real alerts

List the alerts that can page a human — from the monitoring config, the alerting rules, or by asking. One file per alert. If there are no alerts, write no runbooks and set `on_call: false`.

Never invent an alert to fill the folder.

## Step 7 — ADRs from what already happened

Do not backfill a decision log. Write ADRs only for decisions you can source from a PR discussion, a design document, or the user's own account, and only where two options were genuinely on the table. Three well-sourced ADRs beat thirty reconstructed ones.

## Step 8 — The agent file

Most repos already have one, and most of them hold the wrong things. An agent file that carries an
architecture overview is a second copy of a fact that lives in `docs/`, and two copies is one fact
and one future lie.

Read the existing `CLAUDE.md`, `AGENTS.md` or `GEMINI.md` and move each section:

| Found in the agent file | Goes to |
|---|---|
| Architecture, system overview, how it fits together | `docs/explanation/architecture.md` |
| Directory or file layout | Delete. The tree is the tree. |
| Setup, install, prerequisites | README `## Quick start` |
| Deploy steps | `docs/how-to/deploy.md` |
| Dependency or feature inventories | Delete |
| Rules, guardrails, "never do X" | Stays |
| Conventions that differ from the ecosystem default | Stays |
| Pitfalls that have cost someone a day | Stays |
| The commands that mean "it works" | Stays |

Then:

1. Rename to `AGENTS.md` if it is not already. It is the cross-tool name; Codex, Cursor and Copilot
   read it.
2. Replace `CLAUDE.md` with a single line: `@AGENTS.md`. Delete `GEMINI.md`.
3. Open the file with the two-surface table from the template, so neither reader has to guess which
   surface owns a fact.
4. End it with a jump table into `docs/`, one line per destination. Every path must resolve — the
   audit checks them, because a jump table with a dead entry sends an agent to invent the answer.
5. Cap it at 200 lines. Instruction-following degrades past roughly 150 to 200 instructions, and a
   context file that grows unchecked silently stops being obeyed.

Preserve `.claude/` and `.cursor/` as they are. Hooks, skills and permissions are tool machinery,
not documentation.

## Step 9 — Clean up

- Delete the files marked Delete.
- Move stray root markdown into `docs/` under a real name, or delete it.
- Add the docs CI workflow.
- Disable the GitHub wiki if it is empty.

## Step 10 — Report

Files created, modified, deleted. Sections left empty and the question that fills each. Files marked Ask. The audit result.
