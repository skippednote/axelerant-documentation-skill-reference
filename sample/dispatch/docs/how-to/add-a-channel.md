---
title: Add a delivery channel
type: how-to
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Add a delivery channel

A channel is a delivery medium — email, SMS, push. A provider is a vendor that implements one. This describes adding a channel; adding a second provider to an existing channel is the same work minus steps 1 and 2.

## Before you start

Decide whether the channel needs its own rate limit and its own suppression rules. If it shares both with an existing channel, you probably want a provider, not a channel.

## Steps

1. **Add the enum value.** `internal/domain/channel.go`, then a migration adding the value to the `channel` type. Postgres enum values cannot be removed, so this is one-way.

2. **Extend the request schema.** `api/openapi.yaml`, then `make openapi` to regenerate `docs/reference/api.md`. Do not edit that file directly.

3. **Implement the provider.** A new package under `internal/providers/`, satisfying:

   ```go
   type Provider interface {
       Name() string
       Send(ctx context.Context, m domain.Message) (domain.Receipt, error)
       Supports(c domain.Channel) bool
   }
   ```

   `Send` returns a `Receipt` on success and a wrapped error otherwise. Classify vendor errors into `errs.Retryable` or `errs.Permanent` — the dispatcher retries the first and gives up on the second. Getting this wrong is the most common cause of a stuck queue.

4. **Register it.** `internal/providers/registry.go`. Registration is explicit; there is no reflection-based discovery.

5. **Add config.** Keys go in `internal/config/config.go` and are documented in [reference/configuration.md](../reference/configuration.md). Secrets go in the `dispatch` Kubernetes secret, never in the config struct defaults.

6. **Test the classification.** `internal/providers/<name>/provider_test.go` must cover one retryable and one permanent vendor error. The integration suite will not catch a misclassification.

## Confirm

```bash
make test
make test-integration
make run
curl -s -X POST localhost:8080/v1/messages \
  -H 'content-type: application/json' \
  -d '{"sender_key":"tutorial","channel":"<new-channel>","to":"...","body":"probe"}'
```

## Related

- [Delivery semantics](../explanation/delivery-semantics.md) — why classification matters
- [Architecture](../explanation/architecture.md)
