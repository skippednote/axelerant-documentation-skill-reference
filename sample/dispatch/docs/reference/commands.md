---
title: Command reference
type: reference
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: source-review
---

# Command reference

| Command | Behavior |
| --- | --- |
| python3 -m dispatch init | Create schema without resetting active work |
| python3 -m dispatch api | Start local HTTP API |
| python3 -m dispatch worker | Poll ready work continuously |
| python3 -m dispatch worker-once | Attempt one ready item |
| python3 -m dispatch send | Enqueue an example email |
| python3 -m dispatch status | Count rows by state |
| python3 -m dispatch get ID | Read one message |

The Makefile sets `PYTHONPATH=src`. Direct CLI calls need that environment setting. A recipient beginning with `fail:` triggers deterministic provider rejection for exercises.
