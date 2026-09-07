---
title: Add a delivery channel
type: how-to
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: automated-test
---

# Add a delivery channel

## Change the supported channel set

The accepted values are declared by `CHANNELS` in `src/dispatch/app.py`. Add the new string there and add a store test that enqueues it and verifies a receipt. Invalid channels must remain rejected.

The local adapter uses the same receipt path for every channel. Integrating a real vendor changes the trust boundary and requires a new ADR; do not insert network calls into this fixture.

## Validate

```bash
make test
```

The validation commands are exercised in the local test suite. No new vendor integration is claimed to have been implemented by this recipe.
