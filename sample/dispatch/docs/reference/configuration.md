---
title: Configuration
type: reference
owner: "@axelerant/platform-team"
last_verified: 2026-09-03
verification_method: source-review
---

# Configuration

| Setting | Default | Source |
| --- | --- | --- |
| DISPATCH_STATE | .state | Process environment |
| --state | Environment default | Global CLI argument |
| api --port | 8080 | CLI argument |
| Lease duration | 30 seconds | Store.claim default |
| Attempt limit | 3 | MAX_ATTEMPTS |
| Retry delay | 2 raised to attempt count, seconds | Store.finish |

`.env.example` is a reference, not an automatically loaded file. No credentials or remote-provider settings exist.
