# What validation establishes

| Rule group | Automated evidence | Human review still needed |
| --- | --- | --- |
| config | Required values, types, duplicate and unknown keys | Actual tier and access classification |
| ownership | Catch-all CODEOWNERS team, README and page ownership | Narrower patterns and real accountability |
| readme | Sections, order, length, status, command and link counts | Exact version agreement and clean execution |
| tree | Tier-specific file set, fixed indexes and substantive pages | Whether pages answer actual questions |
| metadata | Page type, method and required fields | Honesty and completeness of evidence |
| freshness | Calendar validity, future dates, expiry | Actual verification took place |
| adr | Naming, metadata, sections, options and downside | Historical immutability and credible decisions |
| alerts | Register/runbook bijection and identity | Register matches the complete live alert system |
| agents | Import, size, structure and live jump-table links | Instruction quality and no duplicated facts |
| paths | Prohibited roots and directories | No catalogues disguised by a different filename |
| placeholders | Unresolved markers outside literals | No future promises written without markers |
| register | Denied vocabulary outside literals | Clear prose and source-backed explanation |
| links | Local paths and heading anchors | External/authenticated destination correctness |
| diagrams | Nonempty fences and required C4 presence | Render success and architectural accuracy |

The rule-coverage check matches IDs with negative fixtures. It is not proof of semantic correctness. Run `make test` to exercise fixtures and `make verify` for the local merge check. The executable sample separately runs HTTP, retries, concurrency, recovery and isolated response exercises.

`make verify-release` requires the refreshed npm lockfile, actual dependency installation, vulnerability review, Mermaid rendering and the official Claude plugin validator. The hosted workflow also runs Markdown and external-link checks. A local static pass does not establish those unavailable checks.
