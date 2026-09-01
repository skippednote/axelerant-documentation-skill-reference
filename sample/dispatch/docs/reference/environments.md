---
title: Environments
type: reference
owner: "@axelerant/platform-team"
last_verified: 2026-09-01
---

# Environments

| | local | staging | production |
|---|---|---|---|
| URL | `localhost:8080` | `dispatch.stg.internal` | `dispatch.internal` |
| Cluster | Docker Compose | `platform-stg` | `platform-prod` |
| Namespace | — | `dispatch` | `dispatch` |
| Database | compose postgres | `dispatch-stg` (RDS) | `dispatch-prod` (RDS, multi-AZ) |
| Queue | LocalStack | `dispatch-outbound-stg` | `dispatch-outbound` |
| Email provider | LocalStack SES | SES sandbox | SES production |
| SMS provider | logged, not sent | Twilio test credentials | Twilio |
| Deploys on | — | merge to `main` | manual promotion |
| Data | synthetic | synthetic | real recipients |

## Access

| Need | How |
|---|---|
| Cluster | `aws sso login`, then `kubectl config use-context platform-prod` |
| Database (read) | `make psql-prod`, which opens a port-forward through the bastion |
| Database (write) | Break-glass role, approved in `#platform-dispatch`, expires in one hour |
| Provider consoles | Vendor SSO; ask the platform team |

## Rules

- Staging sends to real Twilio test numbers. It cannot reach a real handset, but it does bill.
- Production is never the place to test a new provider. Add it in staging behind a sender-level flag first.
