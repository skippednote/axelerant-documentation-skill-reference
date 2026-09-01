---
title: <AlertName>
type: runbook
owner: "@org/team"
last_verified: <YYYY-MM-DD>
---

# <AlertName>

## Trigger

<Exact alert name, and the query or threshold that fires it.>

## Impact

<Who notices, how fast, what breaks. Severity.>

## Diagnose

1. <Check> — `<command>`
   Good result looks like: <what you expect to see>
2. <Check> — <dashboard link>
   Good result looks like: <what you expect to see>

## Mitigate

1. **Safe:** <action> — `<command>`
2. **Risky:** <action> — `<command>` — <what it costs if wrong>

## Escalate

- <@team> in <#channel>.
- Stop trying and escalate when: <condition>.

## After

- Record <what> in <where>.
- Update this runbook before closing the incident.
