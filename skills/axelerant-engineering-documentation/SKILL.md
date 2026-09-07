---
name: axelerant-engineering-documentation
description: Scaffold, migrate or audit Axelerant repository documentation; write grounded ADRs and alert runbooks, check evidence and validate AGENTS.md and CLAUDE.md.
---

# Axelerant engineering documentation

Work from the procedure for the situation and let `scripts/docs_audit.py` be the authority. It
enforces the machine-checkable half of the policy, so there is no need to recite the rules before
starting: scaffold or migrate, run the audit, fix what it reports.

Read `references/anti-fluff.md` before drafting prose. It governs what you are allowed to write and
the audit cannot check most of it.

Open `references/contract.md` when you need one of three things: a rule the audit does not check, so
a human has to judge it; the wording to cite in an ADR that deviates from the policy; or the reason
behind a rule you are about to argue with. `references/validation.md` says which rules fall on which
side of that line.

## Decide the workflow

Read the checkout and `.axelerant/repo.yml`. Confirm an absent tier, owner, visibility and on-call status before scaffolding. Use `references/brownfield.md` for existing material and `references/greenfield.md` for a new repository. Never guess a command or publish a skeleton as completed documentation.

## Ground claims

Read code, configuration, real command output, the actual decision discussion or incident. Cite the source in the change summary. Distinguish a local example from production. Preserve ADR history; do not reuse its number or replace its original reasoning. A new decision supersedes the earlier one.

## Agent files

AGENTS.md is the single repository instruction source. CLAUDE.md contains only `@AGENTS.md`. Validate both after every migration. Keep setup and architecture in their human-facing pages. A moved page and its jump-table link change together.

## Run checks

Locate `scripts/docs_audit.py` relative to this SKILL.md; use an absolute script path when the current directory is the repository under audit. Run it with the checkout path and `--strict`. Run `scripts/mermaid_check.py` with `--render` when the approved renderer is installed. A static check is not a successful render.

In the reference implementation also run `make verify`. Report the actual command outputs; never convert an unavailable command into a passing check.

## Evidence verification

Use the evidence method the contract allows for the page type. Review indexes and explanations against source; do not pretend to execute prose. Reference pages need generation, source review or a named automated test. Runbooks use incident evidence or safe response exercises. ADRs receive no verification date.

For executable procedures, first print an approved plan using `scripts/verify_isolated.py`. It accepts explicit commands and a preinstalled immutable Docker image. Without Docker it stops; no host fallback. Do not mount host credentials or grant network access to make a failing procedure appear verified. The runner does not stamp dates: update metadata only after reviewing the successful result and recording its limits.

## Completion

Name files changed, executed checks, evidence dates, manual-review gaps and any blocked release steps. The organization plugin already exists; do not claim this revision has reached it without a successful distribution receipt.
