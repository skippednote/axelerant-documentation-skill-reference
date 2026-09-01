---
title: DispatchQueueDepthCritical
type: runbook
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# DispatchQueueDepthCritical

## Trigger

`DispatchQueueDepthCritical` — `aws_sqs_approximate_number_of_messages_visible{queue="dispatch-outbound"} > 5000` for 10 minutes.

## Impact

Notifications are accepted but not delivered. At 5,000 the backlog is roughly 20 minutes of normal traffic. Password resets and one-time codes are in the same queue as everything else, so user-visible failures start before the backlog is obvious to producers. Severity 2; severity 1 if depth is still climbing after mitigation.

## Diagnose

1. Is the dispatcher running?
   `kubectl -n dispatch get pods -l app=dispatch-worker`
   Good: all pods `Running`, restart count stable. A crash loop points at configuration; check the pod events.

2. Is it processing anything?
   `kubectl -n dispatch logs -l app=dispatch-worker --since=5m | grep -c 'dispatcher sent'`
   Good: a non-zero count that grows between runs. Zero with healthy pods means it is claiming and failing.

3. Is one provider failing?
   Open the per-provider error rate panel on the dispatch dashboard.
   Good: error rate under 1% for each provider. A single provider at 100% is the common cause.

4. Is the DLQ filling?
   `make dlq-peek`
   Good: empty or near-empty. A filling DLQ means messages are being classified permanent and dropped, which is a different problem from a stall.

5. Is the suppression API up?
   `curl -s -o /dev/null -w '%{http_code}' "$SUPPRESSION_API_URL/healthz"`
   Good: 200. Non-200 fails every attempt, because an unavailable suppression list is treated as everything suppressed.

## Mitigate

1. **Safe: scale the dispatcher.**
   `kubectl -n dispatch scale deployment/dispatch-worker --replicas=8`
   Works when the cause is volume rather than failure. Watch depth for five minutes before doing anything else.

2. **Safe: disable the failing provider's channel.**
   `kubectl -n dispatch set env deployment/dispatch-worker CHANNEL_EMAIL_ENABLED=false`
   Messages for that channel stay queued rather than burning attempts. Re-enable when the provider recovers.

3. **Risky: raise `RETRY_MAX_ATTEMPTS`.**
   Only when a provider is recovering and messages are approaching the redrive count. Raising it above the queue's redrive count means messages hit the DLQ before the application stops retrying, so check the queue configuration first.

## Escalate

- `@axelerant/platform-team` in `#platform-dispatch`.
- Escalate when depth is still climbing 15 minutes after scaling, or when the cause is a vendor outage — then it needs the vendor's status page and an incident channel, not more workers.

## After

- Record peak depth, cause and time to recover in the incident ticket.
- If a diagnose step was missing or wrong, fix this file before closing the incident.
