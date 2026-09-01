---
title: DispatchProviderErrorRateHigh
type: runbook
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# DispatchProviderErrorRateHigh

## Trigger

`DispatchProviderErrorRateHigh` — `rate(dispatch_provider_errors_total[5m]) / rate(dispatch_provider_attempts_total[5m]) > 0.05` for a single provider over 10 minutes.

## Impact

Messages on that provider's channel are retrying or failing. Other channels are unaffected. Below 20% this is usually invisible to users because retries absorb it; above that, delivery latency becomes noticeable. Severity 3, rising to 2 if the error class is permanent rather than retryable.

## Diagnose

1. Which error class?
   `kubectl -n dispatch logs -l app=dispatch-worker --since=10m | grep 'dispatcher error' | awk '{print $NF}' | sort | uniq -c | sort -rn`
   Good: mostly `retryable`. A majority of `permanent` means messages are being dropped, not delayed, which is the more urgent case.

2. Which vendor error?
   `psql "$DATABASE_URL" -c "select last_error, count(*) from notifications where status='failed' and updated_at > now() - interval '15 minutes' group by 1 order by 2 desc limit 5;"`
   Good: a single recognisable vendor error rather than a spread. `Throttling` and `429` are expected under load; authentication errors are not.

3. Is it credentials?
   Check the age of the `dispatch` secret. A rotation that did not roll the pods leaves them holding the previous value.
   Good: pod start time later than the secret's last update.

4. Is the vendor up?
   Vendor status page, linked from the dispatch dashboard.

## Mitigate

1. **Safe: nothing, if the class is retryable and the vendor is recovering.** Retries handle it. Confirm the queue depth alert has not also fired.

2. **Safe: roll the pods after a credential rotation.**
   `kubectl -n dispatch rollout restart deployment/dispatch-worker`

3. **Safe: disable the channel** if the error class is permanent, so attempts stop being consumed.
   `kubectl -n dispatch set env deployment/dispatch-worker CHANNEL_SMS_ENABLED=false`

4. **Risky: redrive the DLQ** once the cause is fixed.
   `make dlq-redrive n=50`
   Redriving before the cause is fixed sends the same messages back into the same failure and consumes attempts. Redrive in batches and watch the error rate between batches.

## Escalate

- `@axelerant/platform-team` in `#platform-dispatch`.
- Escalate to the vendor when the error rate is above 50% for 30 minutes with no status page entry. Account contacts are in the vendor agreements folder.

## After

- Record the vendor error string and its classification in the incident ticket.
- If an error was misclassified, fix the classification in `internal/providers/<name>` and add the test case. That is the actual repair; this runbook only contains it.
