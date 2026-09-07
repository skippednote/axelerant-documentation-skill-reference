---
name: axelerant-engineering-documentation
description: Scaffold, migrate or audit Axelerant repository documentation; write grounded ADRs and alert runbooks, check evidence and validate AGENTS.md and CLAUDE.md.
---

# Axelerant engineering documentation

Read `references/contract.md` and `references/validation.md` first. They define policy and the machine/manual boundary. Read `references/anti-fluff.md` before drafting prose.

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

Use the contract's method for the page type. Review indexes and explanations against source; do not pretend to execute prose. Reference pages need generation, source review or a named automated test. Runbooks use incident evidence or safe response exercises. ADRs receive no verification date.

For executable procedures, first print an approved plan using `scripts/verify_isolated.py`. It accepts explicit commands and a preinstalled immutable Docker image. Without Docker it stops; no host fallback. Do not mount host credentials or grant network access to make a failing procedure appear verified. The runner does not stamp dates: update metadata only after reviewing the successful result and recording its limits.

## Completion

Name files changed, executed checks, evidence dates, manual-review gaps and any blocked release steps. The organization plugin already exists; do not claim this revision has reached it without a successful distribution receipt.

## Publishing a book

Run `scripts/build_book.py <repo>`, adding `--pdf` when asked. The spine is `.axelerant/book.yml` and only reorders; never write pages to fill a book out, and never refresh an evidence date because a book was assembled.
