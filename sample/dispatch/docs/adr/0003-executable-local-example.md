---
title: Make the worked example executable locally
type: adr
owner: "@axelerant/dispatch-admins"
status: accepted
date: 2026-09-03
deciders: ["@axelerant/dispatch-admins"]
---

## Context and problem statement

The existing cloud-service specimen contained commands with no executable implementation. The maintainer requested a runnable example without turning the documentation standard into a cloud deployment project.

## Considered options

- **Implement the whole cloud design.** Preserves vendor details but requires credentials, emulators and more dependencies.
- **Use a local SQLite queue and receipt adapter.** Keeps the acceptance, claim, retry and duplicate-delivery lessons executable offline.
- **Keep a documentation-only specimen.** Smallest effort, but cannot substantiate execution dates.

## Decision

Use a local SQLite implementation and a file receipt adapter. Preserve the previous records as history: [0001](0001-sqs-over-kafka.md) and [0002](0002-at-least-once-delivery.md) are superseded for this sample. Their provider-specific statements are historical, not claims about the current implementation.

## Consequences

**Good:** unit tests and HTTP smoke tests run without services or credentials. Queue leases and duplicate effects are visible.

**Bad:** there is no distributed broker, real provider, production alert system or deployment. Three attempts are a terminal bound, not a guarantee of eventual delivery.

**Forecloses:** presenting this local fixture as production-ready or claiming its tests validate the earlier cloud design.
