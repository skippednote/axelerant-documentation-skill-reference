---
title: ProviderErrorRateHigh
type: runbook
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: staging-drill
alert: ProviderErrorRateHigh
alert_source: alerts/alerts.json
---

# ProviderErrorRateHigh

## Trigger

`ProviderErrorRateHigh`: `failed / (sent + failed) > 0.05 and sent + failed >= 20`. Evaluated by the local exercise script; no real pager is configured.

## Impact

The local failure ratio is high. Failed notifications exhausted their attempt limit. This is a simulation, not a production severity assignment.

## Diagnose

1. Run `make status`. Healthy: queued and failed counts are zero after a normal completed example.
2. Run `make worker-once`. Healthy: ready work advances; `False` means no item is ready yet.
3. Check recipients for the deliberately failing `fail:` prefix. Healthy examples do not use it.
4. Run `make test`. Healthy: lease, retry and delivery tests pass independently of local state.

## Mitigate

**Safe:** start `make worker` for queued work. Wait for retry availability rather than repeatedly resetting state.

**Safe:** after a deliberate failure exercise, submit a new normal message and confirm a receipt.

**Risky:** `make clean` discards messages and evidence. Stop running processes and use it only for disposable local data.

## Escalate

Stop changing state if normal messages cannot be delivered or tests fail. Open a repository issue for `@axelerant/dispatch-admins`, removing recipient and body values. This public example uses no internal contact details.

## After

Record the failing test or command, count values and corrective change in the issue. Correct this runbook before closing the issue. Its verification date refers to an isolated local response exercise, not a production incident.
