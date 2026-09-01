---
title: Deploy dispatch and roll back
type: how-to
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Deploy dispatch and roll back

## Before you start

- Merge rights on `main`, or an approved PR
- `kubectl` context `platform-prod` (`kubectl config get-contexts`)
- Membership of `@axelerant/platform-team`

## Deploy

Merging to `main` builds an image tagged with the commit SHA and deploys it to staging. Production is a manual promotion.

```bash
gh workflow run promote.yml -f sha=<commit-sha> -f env=production
gh run watch
```

The workflow does a rolling restart of the `dispatch-api` and `dispatch-worker` deployments. Migrations run as a pre-deploy job and must be backwards compatible for one release; the old pods keep serving while the new ones start.

## Confirm

```bash
kubectl -n dispatch get pods -w                 # all Running, none restarting
curl -s https://dispatch.internal/healthz
kubectl -n dispatch logs -l app=dispatch-worker --since=2m | grep -c 'dispatcher sent'
```

The last command should be non-zero within two minutes on any weekday. Zero at low traffic is not conclusive; check the queue depth dashboard instead.

## Roll back

```bash
kubectl -n dispatch rollout undo deployment/dispatch-api
kubectl -n dispatch rollout undo deployment/dispatch-worker
```

Rolling back does not revert migrations. A migration that is not backwards compatible cannot be rolled back this way — write a forward fix instead. This is why the compatibility rule exists.

## Related

- [Environments](../reference/environments.md)
- [Queue depth runbook](../runbooks/dispatch-queue-depth-critical.md)
