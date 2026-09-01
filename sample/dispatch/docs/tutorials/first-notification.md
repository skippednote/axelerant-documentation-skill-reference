---
title: Deliver your first notification
type: tutorial
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Deliver your first notification

By the end you will have sent one email through a local dispatch and seen it land in the LocalStack mailbox. Takes about ten minutes. You need the stack from [run-locally](../how-to/run-locally.md) already up.

## 1. Create a sender

Every message belongs to a sender, which carries the from-address and the rate limit.

```bash
curl -s -X POST localhost:8080/v1/senders \
  -H 'content-type: application/json' \
  -d '{"key":"tutorial","from":"noreply@example.test","rate_per_minute":60}'
```

You get back a sender with an `id`. Keep it.

## 2. Queue a message

```bash
curl -s -X POST localhost:8080/v1/messages \
  -H 'content-type: application/json' \
  -d '{
        "sender_key":"tutorial",
        "channel":"email",
        "to":"someone@example.test",
        "subject":"Hello",
        "body":"First one."
      }'
```

The response has `"status":"queued"`. Nothing has been sent yet — the API only persists and enqueues.

## 3. Watch the dispatcher pick it up

If `make run` is in the foreground you will see two lines: one claiming the message, one recording the provider response. If you are running `make worker` separately, watch that terminal instead.

```
dispatcher claim  id=01J... channel=email attempt=1
dispatcher sent   id=01J... provider=localstack-ses latency=41ms
```

## 4. Confirm it arrived

```bash
awslocal ses list-identities
awslocal ses get-send-statistics
```

`SentLast24Hours` increments by one. LocalStack does not store message bodies, so this counter is the confirmation.

## 5. Look at what was written

```bash
psql "$DATABASE_URL" -c \
  "select id, channel, status, attempts, last_error from notifications order by created_at desc limit 1;"
```

`status` is `sent` and `attempts` is 1. If `status` is `failed`, `last_error` carries the provider's message, and [runbooks/provider-error-rate-high.md](../runbooks/provider-error-rate-high.md) explains what to do with it.

## What you learned

The API and the dispatcher are separate: one accepts and persists, the other delivers. That separation is the reason a message can be accepted while every provider is down, and it is explained in [architecture](../explanation/architecture.md).

Next: [add a channel](../how-to/add-a-channel.md).
