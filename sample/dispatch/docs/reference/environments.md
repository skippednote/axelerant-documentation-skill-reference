---
title: Execution environments
type: reference
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: source-review
---

# Execution environments

| Environment | Persistence | Network |
| --- | --- | --- |
| Unit tests | Temporary directory | None |
| HTTP smoke test | Temporary directory | Loopback only |
| Interactive demo | .state until clean | Loopback only |
| Alert exercise | Temporary directory | None |

There is no cloud account, deployed environment or real paging target. Historical cloud-design ADRs are retained as superseded records, not statements about this executable.
