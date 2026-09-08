---
title: Operations
type: how-to
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: clean-checkout
---

# Operations

How this example runs, how it is deployed, and what to do when it stops
behaving. Dispatch is a local example, so every environment below is one you
create on your own machine.

## Environments

| Environment | What it is | How you get one |
| --- | --- | --- |
| local | The only environment. SQLite on disk, HTTP on loopback | `make up` |
| none | There is no staging or production. Nothing here is deployed anywhere | |

A real service would list its environments and their URLs here, along with who
can reach each one.

## Access

No authentication is implemented, and the listener binds to loopback only. That
is the whole access model, and it is why this example is safe to run and unsafe
to expose.

## Deploy

`make package` builds `dist/dispatch.zip`, which you can extract elsewhere. See
[Deploy](how-to/deploy.md) for what it contains and what it does not.

## Rollback

Stop the worker, restore the previous checkout, and start it again. Messages
already accepted survive in `.state/dispatch.db`, because the queue is on disk
rather than in memory.

```bash
make worker-once   # leases and delivers one message, prints True
```

`worker-once` handles a single message per call. Repeat it until it prints
`False`, which means nothing was waiting, before swapping versions.

## Monitoring

The queue depth is the number that matters. Anything else follows from it.

```bash
make status        # queued, leased and failed counts
```

`alerts/alerts.json` lists the alerts this repo would fire and the runbook for
each. See [Alerts and runbooks](runbooks/README.md).
