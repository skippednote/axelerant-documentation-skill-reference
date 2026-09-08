---
title: Deliver a first notification
type: tutorial
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: automated-test
---

# Deliver a first notification

The automated HTTP walkthrough is self-contained:

```bash
make smoke
```

It starts the API on an ephemeral loopback port, submits a notification, runs one worker cycle, reads the stored status and checks the receipt. It removes temporary state afterward.

For the CLI path:

```bash
make up
make send
make worker-once
make status
```

Acceptance is not delivery. `send` records `queued`; the worker appends a receipt and then records `sent`.
The interactive path is covered by store and worker tests; the HTTP path is covered by `test_http_roundtrip`.
