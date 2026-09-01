---
title: dispatch documentation
type: index
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# dispatch

Outbound notification service. Internal services POST a message; dispatch persists it, picks a channel and a provider, and delivers it. Delivery is at-least-once, so consumers must tolerate duplicates.

## Start here

| You want to | Read |
|---|---|
| deliver your first notification | [tutorials/first-notification.md](tutorials/first-notification.md) |
| get a working local copy | [how-to/run-locally.md](how-to/run-locally.md) |
| ship a change | [how-to/deploy.md](how-to/deploy.md) |
| add a channel or provider | [how-to/add-a-channel.md](how-to/add-a-channel.md) |
| look up a config key | [reference/configuration.md](reference/configuration.md) |
| know which environment is which | [reference/environments.md](reference/environments.md) |
| understand the split between API and dispatcher | [explanation/architecture.md](explanation/architecture.md) |
| understand duplicate deliveries | [explanation/delivery-semantics.md](explanation/delivery-semantics.md) |
| read the schema | [explanation/data-model.md](explanation/data-model.md) |
| know why something is the way it is | [adr/](adr/) |
| respond to an alert | [runbooks/](runbooks/) |

## Owned elsewhere

- Provider contracts, pricing and rate limits: the vendor agreements in Legal's Drive folder. Only the numbers we depend on are mirrored into [reference/configuration.md](reference/configuration.md).
- Recipient consent and suppression lists: owned by the CRM. dispatch reads them and never writes them.
