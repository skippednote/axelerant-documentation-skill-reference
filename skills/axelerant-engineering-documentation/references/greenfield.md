# Greenfield: a new repo

The risk here is the opposite of brownfield. There is no code to ground claims in, so everything is easy to invent. Write less.

## Step 1 — Establish facts

Ask, do not assume:

- What it is, in one sentence, and who uses it.
- Tier and kind.
- Owning team and Slack channel.
- Stack and pinned versions.
- Environments and how it deploys.
- Will it have on-call?

If the user cannot answer a question yet, the corresponding section does not get written. An empty `docs/` is honest for a repo with no code.

## Step 2 — Write `.axelerant/repo.yml` first

Everything downstream reads it. Set `on_call: false` until an alert exists.

## Step 3 — README before code

At greenfield the README is a specification. Sections 1, 2, 3, 6 and 7 of the contract can be written on day one. Quick start and common commands are written when the commands exist and you have run them — not before.

## Step 4 — Scaffold only what is real

- **Tier 0**: README, `.axelerant/repo.yml`, `AGENTS.md`, `CLAUDE.md`. Nothing else. Do not create `docs/`.

  `AGENTS.md` on day one holds only what you actually know: the two-surface table, the verification
  commands, and any rule the team has already agreed. Pitfalls arrive later, when something has cost
  someone a day. Do not pre-populate it with guesses.
- **Tier 1**: add `docs/README.md` and `docs/architecture.md` (context diagram plus the intended approach). The other three files are written when there is something true to put in them.
- **Tier 2**: add `docs/README.md`, `docs/explanation/architecture.md`, and `docs/adr/0001-*.md` for the founding stack decision. Folders are created when their first real file is.

Do not pre-create empty folders or placeholder pages. The tree grows as facts arrive.

## Step 5 — First ADR

A new repo has at least one decision worth recording: why this stack, this hosting, this boundary. Write `0001` while the alternatives are still remembered. This is the highest-value document in a greenfield repo and the one nobody writes later.

## Step 6 — Wire the gate on day one

Add the docs CI workflow immediately, with `strict: false`. A repository that deliberately defers
sections cannot pass the blocking checks yet, and a gate that fails on day one gets deleted on day
two. Flip `strict: true` in the same pull request that completes the tier's required set.

## Step 7 — Report

What was written, what was deferred, and the specific fact needed to write each deferred section.
