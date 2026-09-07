---
title: HTTP API
type: reference
owner: "@axelerant/platform-team"
last_verified: 2026-09-03
verification_method: source-review
---

# HTTP API

Source: `src/dispatch/app.py`.

| Method | Route | Result |
| --- | --- | --- |
| GET | /healthz | 200 after a database read; 503 on a database error |
| GET | /metrics | JSON counts for queued, processing, sent and failed |
| POST | /v1/messages | 202 with id and queued status |
| GET | /v1/messages/{id} | Message record, or 404 |

A create request is a JSON object with string fields `channel`, `recipient`, and `body`. Channel is email, sms or push; recipient and body are nonempty. Bodies are capped at 65,536 bytes. Invalid input returns 400.

No authentication is implemented; loopback binding is mandatory. A 202 response confirms persistence, not delivery.
