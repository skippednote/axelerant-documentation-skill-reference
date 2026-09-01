# axelerant-documentation-skill-reference

A Claude Code skill that sets up repository documentation to a fixed contract, plus a worked example of what it produces.

## Status

`draft` — published for review. Not yet in a plugin marketplace.

## Requirements

- Claude Code
- Python 3.9 or newer, for the audit script. No third-party packages.

## Quick start

```bash
git clone https://github.com/skippednote/axelerant-documentation-skill-reference.git
cd axelerant-documentation-skill-reference

# install the skill for your user
cp -R skills/axelerant-engineering-documentation ~/.claude/skills/

# audit any repo against the contract
python3 skills/axelerant-engineering-documentation/scripts/docs_audit.py /path/to/repo
```

Then, inside a repo, `/docs-init` to scaffold or migrate, `/docs-check` to audit, `/docs-verify` to run the documented commands and stamp `last_verified`.

## Common commands

| Command | Does |
|---|---|
| `/docs-init` | Classifies the repo, confirms tier and owner, scaffolds or migrates |
| `/docs-check` | Audits against the contract and lists gaps, changing nothing |
| `/docs-verify` | Runs the commands in a doc, then stamps `last_verified` |
| `python3 skills/axelerant-engineering-documentation/scripts/docs_audit.py <repo>` | The audit on its own |
| `python3 ... docs_audit.py <repo> --strict` | Same, exits 1 on any blocking finding. Use in CI |
| `python3 ... docs_audit.py sample/dispatch --strict` | Audits the worked example. Passes clean |

## How it works

The skill classifies a repo into one of three tiers and applies the matching contract.

| Tier | What it covers | Required |
|---|---|---|
| 0 | One artefact consumed elsewhere: module, action, CLI, library, theme | README only, no `docs/` |
| 1 | One deployable application | README plus a flat `docs/` of five files |
| 2 | Multiple services, long-lived product, or on-call | README plus a Diátaxis tree, ADRs and runbooks |

It borrows rather than invents: [Diátaxis](https://diataxis.fr/) for the tree, [MADR](https://adr.github.io/madr/) for decisions, an [arc42](https://arc42.org/overview/) subset for the architecture page, [C4](https://c4model.com/) levels 1 and 2 for diagrams, the [Google SRE](https://sre.google/workbook/on-call/) shape for runbooks, and [standard-readme](https://github.com/RichardLitt/standard-readme) for README sections.

Two procedures, because the failure modes are opposite. Brownfield reads the CI config, manifests and entrypoint before it reads any existing documentation, and triages every file it finds into keep, fix, delete or ask. Greenfield has no code to ground claims in, so it writes less and defers sections until the fact exists.

## What is in here

```
skills/axelerant-engineering-documentation/
├── SKILL.md                    entry point and hard rules
├── references/
│   ├── contract.md             the normative spec
│   ├── brownfield.md           procedure for an existing repo
│   ├── greenfield.md           procedure for a new repo
│   ├── anti-fluff.md           what may be written, and the self-review
│   └── templates/              README, AGENTS, ADR, runbook, index, CI, Vale, markdownlint
└── scripts/docs_audit.py       contract checker, for local use and CI

commands/                       /docs-init, /docs-check, /docs-verify
sample/dispatch/                a worked Tier 2 example that passes the audit
```

`sample/dispatch` is a fictional notification service. Its documentation is the reference for what the contract produces: a README, an `AGENTS.md`, a full Diátaxis tree, two ADRs with real rejected options, and two runbooks named after the alerts that fire them.

## Enforcement

Every repo adopting the contract copies one file, `.github/workflows/docs.yml`, from
`skills/axelerant-engineering-documentation/references/templates/docs-workflow.yml`. It calls the
reusable workflows here, so the contract, the audit script, the Vale style and the markdownlint
config are pulled at a pinned ref instead of being vendored and left to drift.

| Workflow | What it does |
|---|---|
| `docs-check.yml` | Contract and frontmatter audit, markdownlint, Vale, link check. Four parallel jobs. |
| `docs-coupling.yml` | Comments on a PR that changes code and no documentation. Never fails the build. |

Both accept `strict: false` for a warn-only rollout period. This repository runs both against itself
and against `sample/dispatch` on every push.

## How we work here

The contract in `skills/axelerant-engineering-documentation/references/contract.md` is normative. Change it and the audit script in the same commit, or they drift. Branch as `<short-slug>`, one logical change per PR.

## Ownership

- Team: `@axelerant/engineering`
- Issues: this repository

## Distribution

Copy `skills/axelerant-engineering-documentation` into `~/.claude/skills/`, or add this repository as a Claude Code plugin marketplace source and install `axelerant-engineering-documentation`.

## Licence

MIT. See [LICENSE](LICENSE).
