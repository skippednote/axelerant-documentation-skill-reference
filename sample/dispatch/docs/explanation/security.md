---
title: Security posture
type: explanation
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: source-review
---

# Security posture

The listener binds only to 127.0.0.1. The sample makes no provider network requests and reads no credentials. Message data is plaintext on disk; use fictional content only.

Request bodies are size-limited, fields are type-checked, and SQL uses bound parameters. There is no authentication, tenant isolation, TLS, quota enforcement or production hardening.

Those controls were excluded rather than simulated. Adding an exposed listener or a real provider is a different product boundary requiring threat review and new ADRs, not a configuration tweak to this demo.
