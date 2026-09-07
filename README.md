# Axelerant engineering documentation

Repository documentation contract, Claude plugin and executable example for Axelerant engineering teams.

## Status

`active` — implementation candidate for contract 1.0.0. The organization plugin already exists; this revision is not yet deployed.

## Requirements

Core checks need Python 3.12 or newer. CI targets Python 3.14.7; local preparation ran on Python 3.13.5.
Workflow validation uses PyYAML 6.0.3. Rendering targets Node 24.20.0 LTS, Mermaid CLI 11.17.0, Mermaid 11.17.2 and Puppeteer 25.9.0.
Full browser installation and hosted CI must pass before this candidate is released.

## Quick start

```bash
python3 -m pip install -r requirements-ci.txt
make verify
```

For the already available organization plugin in Claude Code:

```text
/plugin marketplace add axelerant/claude-plugins
/plugin install axelerant-engineering-documentation
/axelerant-engineering-documentation:docs-init
/axelerant-engineering-documentation:docs-check
/axelerant-engineering-documentation:docs-verify
```

In the Claude app, use the organization-provided plugin. Copying only the skill directory does not install the plugin's three command files.

## Common commands

| Command | Does |
| --- | --- |
| `make audit` | Checks the reference and nested example separately |
| `make test` | Runs positive and negative checker tests |
| `make sample` | Runs the executable sample and its documentation checks |
| `make plugin-check` | Validates the manifest, skill and Claude import |
| `make workflow-check` | Validates YAML, action pins and reusable inputs |
| `make coverage` | Compares declared rule IDs with implemented rules |
| `make verify` | Runs all locally available checks |
| `make verify-release` | Requires lockfile, browser render and official plugin validation |
| `npm install --package-lock-only --ignore-scripts` | Refreshes the lockfile for reviewed package versions |
| `python3 scripts/render_workflow.py --help` | Shows immutable workflow adoption options |

## How we work here

Change the contract, checker, fixtures, templates and published policy together. Keep historical ADRs. Run tests against the proposed source, not an older release. Promote the candidate only after dependency installation, rendering and plugin-load checks pass.

## Ownership

Team: `@axelerant/engineering`. Maintainer: Bassam Ismail. Support and escalation: repository issues assigned to the owning team.

## Distribution

The organization marketplace is `axelerant/claude-plugins`. The reference repository owns the source contract. A reviewed release is copied to the marketplace; the marketplace update has not been performed by this candidate.

The canonical rules are in [contract.md](skills/axelerant-engineering-documentation/references/contract.md). The [coverage boundary](skills/axelerant-engineering-documentation/references/validation.md) distinguishes automation from review. The worked service is under [sample/dispatch](sample/dispatch/README.md).
