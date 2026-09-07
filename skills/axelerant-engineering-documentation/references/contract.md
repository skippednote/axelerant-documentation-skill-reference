# Axelerant Engineering Documentation Standard

Version 1.0.0. Maintainer: Bassam Ismail. Reviewed quarterly.

This is the canonical repository contract. Confluence publishes the same policy for people; it is not an independently maintained second standard, and it names the adopted version and its immutable source commit. A repository stays on the version it adopted until it adopts a newer commit deliberately; nothing here tracks `main` automatically.

The standard applies to every Axelerant repository, including client work. Tier adjusts the amount of documentation; documentation remains part of the codebase and the handover. A deliberate deviation needs an ADR in the repository that deviates.

## Adoption

Classify the repository, record its owner and visibility, then scaffold or migrate its documentation. Ground pages in code, configuration, a real decision, an incident or an owner answer. Run the strict audit and review the checks that need human evidence. Adopt the shared workflow at an immutable commit.

Existing repositories can start with `enforcement: warn` while completing their required set. New repositories start with `enforcement: block`. Move to blocking in the pull request that completes adoption; do not use warn mode as an indefinite exemption.

## Repository declaration

<!-- check: config -->

```yaml
# .axelerant/repo.yml
tier: 2
kind: service                 # service | site | library | action | cli | poc | docs
owner: "@axelerant/platform-team"
visibility: internal          # public | internal | client-confidential
on_call: true
docs_review_days: 90
alerts_file: alerts/alerts.json # required when on_call is true
# client: acme                 # required for client-confidential work
```

The six fields before `alerts_file` are required. Tier is 0, 1 or 2. Review days are a positive integer. The Boolean is exactly `true` or `false`; misspellings do not become false. Unknown keys and duplicate keys are errors.

Metadata uses a deliberately small YAML subset: flat scalars and JSON-style lists of quoted strings. Nested YAML, aliases and multiline values are rejected with a diagnostic. Quoted strings can contain `#`. This keeps the core audit dependency-free without silently accepting malformed YAML.

<!-- check: ownership -->

The configured owner is a GitHub team handle. The effective last catch-all `*` rule in CODEOWNERS includes that handle, the README names it, and documentation frontmatter uses it. Review any narrower CODEOWNERS patterns separately: the checker does not resolve all GitHub ownership precedence rules.

Public documentation contains public-safe facts and fictional examples, not private hostnames, client identifiers, internal channels, real recipient data or access credentials. Internal and client-confidential repositories can contain operational detail appropriate to their access controls. Secrets never belong in documentation. A public support or issue route replaces an internal Slack channel. Classification correctness is a human review responsibility.

## Tiers

| Tier | Covers | Required human documentation |
| --- | --- | --- |
| Component — 0 | Shared modules, actions, CLI tools, themes, libraries and single-purpose scripts | README; no docs/ |
| Project — 1 | Client sites, proofs of concept and applications with one deployable | README and the Project set |
| Platform — 2 | Long-lived products, multi-service systems or anything with human on-call responsibility | README, Diátaxis tree, ADRs and alert-linked runbooks when on-call |

Every tier also has repository ownership and agent instructions. On a genuine boundary, choose the lower tier. On-call responsibility always selects Platform. Independently operated multi-service systems select Platform through human classification; the checker does not infer deployables from folder names.

## README

<!-- check: readme -->

The README answers: can a stranger run this and know who to ask? Cap it at 400 lines. Begin with an H1 and a description of at most 120 characters. Required H2 sections appear once, in this order:

| Section | Contents |
| --- | --- |
| Status | active, maintenance, archived or poc; safe environment URLs where applicable |
| Requirements | Exact pinned CI/tool versions and the supported runtime range |
| Quick start | Clean checkout to a working result, with executable commands |
| Common commands | A table: 3–15 commands for Component; 8–15 for Project or Platform |
| How we work here | Branch, commit and pull-request rules, or a link to adopted defaults |
| Ownership | Team, support or escalation; a channel for non-public repositories |
| Documentation | Project and Platform: 4–8 repository links, each stating the question it answers |

Add Distribution when the artifact is consumed as a package, action, image, mirror or release. Do not invent eight commands for a tiny component. Version agreement with actual CI and clean-checkout success require execution and review, not just a valid table.

## Trees and directory indexes

<!-- check: tree -->

A directory index is `README.md`, never `index.md`. Git renders the front door without a documentation build. Create a new subject subfolder only when there are at least three pages; this is advisory for invented folders, not an excuse for empty standard folders.

Project starts with exactly:

```text
docs/
├── README.md
├── getting-started.md
├── architecture.md
├── operations.md
└── decisions.md
```

The first file maps questions; getting-started covers laptop to first working change; architecture covers context and design; operations covers environments, access, deployment, rollback and monitoring. The decision log can contain zero or one decision. At the second decision, replace `decisions.md` with `adr/README.md` and two numbered ADRs. Keep the four other files flat. An assets/ directory is allowed when media exists.

Platform has:

```text
docs/
├── README.md
├── tutorials/       guided learning
├── how-to/          completing a task now
├── reference/       looking up a fact
├── explanation/     understanding why
├── adr/             decisions
└── runbooks/        required when on_call is true
```

Each fixed folder has a real `README.md`. The four Diátaxis folders also contain substantive pages, not empty placeholders. Explanation includes `architecture.md`. Runbooks are substantive when on-call is declared. Assets are optional. The fixed folders describe reader intent; the three-page threshold governs additional subject folders.

## Frontmatter and evidence

<!-- check: metadata -->

Every Markdown page under docs/ has a title, type and configured owner. Directory README files use `type: index`. Other pages in a Platform folder use its corresponding type.

```yaml
---
title: Run locally
type: how-to
owner: "@axelerant/platform-team"
last_verified: 2026-09-03
verification_method: clean-checkout
applies_to: "v2.4+"
---
```

One date field avoids competing notions of freshness; `verification_method` states what the date actually proves.

| Type | Allowed evidence method | Meaning |
| --- | --- | --- |
| tutorial | clean-checkout, automated-test | Complete the guided path or its corresponding executable test |
| how-to | clean-checkout, automated-test, staging | Observe the documented outcome in the named environment |
| reference | generated, source-review, automated-test | Regenerate or compare against authoritative source |
| explanation | source-review | Compare claims with code, configuration and accepted decisions |
| index | link-review | Confirm destinations and question labels are current |
| runbook | incident, staging-drill, tabletop | Use incident evidence, an isolated exercise or a structured response walkthrough |

The method is not proof by itself. Include the executed command, test, incident or reviewed source in the pull request. Automated source review must not be described as a human on-call sign-off. The sample explicitly identifies its isolated local drills as simulations.

<!-- check: freshness -->

Dates use real calendar dates in YYYY-MM-DD format and may not be in the future. Runbooks block after 180 days. Other pages warn after `docs_review_days`; Platform pages block after twice that period. A file edit alone never refreshes its date.

## Decision records

<!-- check: adr -->

Use `docs/adr/NNNN-kebab-title.md`. Component deviations use .axelerant/adr/ because Component repositories cannot have docs/. Never renumber or erase accepted history; supersede it.

```yaml
---
title: Choose the queue model
type: adr
owner: "@axelerant/platform-team"
status: accepted
date: 2026-09-03
deciders: ["@axelerant/platform-team"]
---
```

Allowed status values are proposed, accepted, deprecated, or `superseded by NNNN`. ADRs have no freshness or verification-method fields. Sections are Context and problem statement, Considered options, Decision, Consequences. List at least two plausible options and an explicit downside or cost. A reviewer assesses plausibility and whether the record represents a real decision.

Write an ADR for a datastore, framework, hosting model, authentication approach, service boundary or deliberate house-default deviation that is expensive to reverse. After roughly fifty records, index accepted decisions by area. Superseded records remain reachable as historical material but leave the accepted index.

## Alerts and runbooks

<!-- check: alerts -->

Every paging alert has exactly one runbook and every runbook has an alert. An on-call repository provides a normalized JSON register through `alerts_file`:

```json
[
  {
    "name": "DispatchQueueDepthCritical",
    "runbook": "docs/runbooks/dispatch-queue-depth-critical.md",
    "condition": "queued > 50"
  }
]
```

Generate that register from the actual alert system where feasible. A reviewer confirms it is complete and synchronized; validating the register alone cannot prove that no unregistered production alerts exist. The sample evaluator is local and does not send pages.

Runbook frontmatter adds `alert` and `alert_source`. Its filename is the kebab-case alert name. Trigger includes the exact name and register condition, including duration when the real rule has one. Required sections are Trigger, Impact, Diagnose, Mitigate, Escalate, After.

Diagnosis is ordered with commands and healthy results. Mitigation puts the safe action first and marks risky actions. Escalation names a team and permitted support route, plus a stop condition. After identifies evidence to retain and the incident record or issue. Responders correct inaccurate steps before closing an incident.

Do not execute production mitigation to refresh a date. Use an incident, safe exercise or tabletop. A generic service runbook is not a substitute for alert-specific response.

## Diagrams

<!-- check: diagrams -->

Project and Platform contain exactly one C4Context diagram under docs/. Platform also contains exactly one C4Container diagram. Use sequence diagrams for retries, races and multi-party exchanges and state diagrams for branching status transitions. Do not hand-maintain C4 component or code-level diagrams. Dynamic and deployment views are not falsely classified as C4 hierarchy levels; add them only for a real reader question.

Mermaid lives inline in its explanatory page. Do not duplicate it in an exported source or image. Screenshots remain appropriate for UI walkthroughs where the image is the content.

The dependency-free check verifies fences, nonempty Mermaid and required diagram presence. It is not a Mermaid parser. The rendered CI check is required to establish parse success. Do not reject every semicolon or count `end` across diagram languages; those heuristics produce false errors.

## Writing and location rules

<!-- check: paths -->

No roadmap or improvements folders, numbered feature catalogues, documentation-status files, master indexes or implementation summaries. Plans belong in Jira. Root Markdown is limited to README, AGENTS, CLAUDE, LICENSE, CHANGELOG, CONTRIBUTING and SECURITY. Avoid Markdown symlinks; checked documentation stays within its repository boundary.

Confluence remains appropriate for organization policy, commercial context and client-facing material. Build, run, deploy, recovery and design facts are self-contained in the repository. A business-context link is not itself an error, but it must not be the only source for an operational fact. Respect access classification when mirroring content. GitHub wikis are not the operational source.

<!-- check: placeholders -->

No unresolved placeholders in published prose, including `TODO`, `TBD`, `REPLACE_WITH_`, `<your-domain>` and `coming soon`. Templates can contain them only through scoped exemptions. Fenced examples and inline literals are not mistaken for unfinished prose.

<!-- check: register -->

The rejected register is stored once in `fluff-terms.txt`. It includes vague intensifiers and throat-clearing such as:

```text
comprehensive · robust · seamless · leverage · utilize · cutting-edge
state-of-the-art · powerful · rich set of · wide range of
it's important to note · it's worth noting · as we all know · needless to say
in today's fast-paced · delve into · a testament to · plays a vital role
this document aims to · this section will cover · in conclusion · let's dive in
```

A document answers a real onboarding question, review comment, task or incident. Do not narrate functions, directories, dependency inventories or features. Generate API, configuration and CLI reference where possible; otherwise use a source-backed table. Explanations name alternatives and costs, not just the chosen path. Emoji are not section markers.

Word budgets warn at 300 for index, 800 for how-to, 1,200 for tutorial, 1,500 for explanation, 600 for ADR and 700 for runbook. Reference is unbounded but preferably generated or tabular. Human review decides whether an oversized page needs editing or a justified exception.

<!-- check: links -->

Relative links and heading anchors must resolve inside the repository. The checker supports inline links and reference definitions. External links are checked separately, with authenticated destinations reviewed by authorized people. A link that resolves can still be the wrong destination.

## Agent instructions

<!-- check: agents -->

`AGENTS.md` is the only source of repository-specific agent rules. `CLAUDE.md` contains exactly:

```text
@AGENTS.md
```

Keep `AGENTS.md` under 200 lines. Start with a table naming Surface and Audience. Include Hard rules, Before claiming done, and Where to look. Guardrails, non-default conventions, known pitfalls and verification commands belong here. Setup and architecture do not; link to their owners instead.

The jump table points to existing Markdown. Add, move or remove its entry with the page. The checker validates its destinations and the exact Claude import. The plugin-bundle validator checks the manifest, command delegation and skill metadata. Tool support can change; do not claim every agent reads the same file without checking that tool's documentation.

## Tooling and safety

In Claude Code:

```text
/plugin marketplace add axelerant/claude-plugins
/plugin install axelerant-engineering-documentation
```

Commands are namespaced:

| Command | Function |
| --- | --- |
| /axelerant-engineering-documentation:docs-init | Confirm classification, scaffold or migrate, then audit |
| /axelerant-engineering-documentation:docs-check | Read-only audit and manual-review gaps |
| /axelerant-engineering-documentation:docs-verify | Plan evidence checks; run approved procedures only in isolation |

The organization plugin is available in the Claude app. Use the surfaces available there for authoring and review; a full audit requires the actual checkout or supplied repository files. Standalone skill copying installs the skill, not the plugin's separate command files. Natural-language requests can activate the skill.

Repository commands are untrusted input. The supplied isolated runner uses a preinstalled immutable image, no host mount, no network, an empty command environment and resource limits. Without Docker or an explicitly approved plan it prints the plan and stops. It does not stamp dates automatically. Docker isolation reduces risk; it is not a guarantee against container-runtime vulnerabilities or an untrusted image. Human review approves the image and commands. Never grant network or production access merely to make verification pass.

## Continuous integration and governance

Adopting workflows pin shared code and contract data to the same reviewed 40-character commit. The shipped `docs-workflow.yml` template is already pinned and can be copied as it stands; `scripts/render_workflow.py` generates the same file against any other reviewed commit. The reference repository's own workflow uses its current checkout, not a prior tag. Local additions may extend policy; they may not replace the shared configuration with weaker rules.

The reusable workflow accepts `path`, `ref`, and `enforcement: warn | block`. For compatibility, `strict: false` selects warn when enforcement is omitted. Every finding-producing check is collected; a single final step applies the selected mode. Configuration, checkout and tool-installation failures remain visible even in warn mode rather than masquerading as a passing audit. No hidden skip switches are provided.

Code/documentation coupling is an idempotent best-effort reminder. It never runs pull-request code with a write token and never blocks a merge. A code change does not automatically require a documentation edit; the reviewer decides whether running, changing or operating behavior changed.

Scoped exemptions use:

```text
register path/to/style-guide.md # the guide names the rejected vocabulary
placeholders path/to/templates/* # instructional template content
links path/to/templates/* # destinations exist after instantiation
```

Only those three rules can be exempted. Broad legacy ignores are errors, not a way to skip ownership, freshness, structure, diagrams or agent validation.

Each rule is machine-enforced, manually reviewed or advisory. The coverage matrix identifies the boundary; the coverage check verifies identifiers, while regression tests demonstrate behavior. Identifier matching alone does not prove a rule is correct. Release review requires the full test suite and remote checks.

## Release and dependency gate

Use exact direct dependency versions and immutable action SHAs; refresh lockfiles through the package manager. Do not delete lockfiles to make upgrades pass. A release requires successful installation, vulnerability checks, Markdown and external-link checks, Mermaid rendering, the executable sample, and a real Claude plugin load test.

Local Python tests do not certify Node or browser installation, hosted CI, or a plugin load. Publish the policy and distribute the plugin after those checks pass, in that order. Edit the reference source, never a marketplace copy that would then drift from it.

## Manual review and foundations

Review classification, actual ownership, exact runtime versions, command outcomes, architectural accuracy, credible alternatives, full alert coverage, safe mitigation, current escalation and permitted visibility. None is proven just by a matching string or a recent date.

The structure draws on Diátaxis, MADR, an arc42 architecture subset, C4, Google SRE, standard-readme and documentation-with-code practices. Axelerant's tier rules, word budgets, evidence methods and expiry thresholds are policy choices, not universal properties of those sources.
