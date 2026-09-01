# Anti-fluff rules

These govern what you may write. They apply to your own output first.

## The five rules

1. **A document answers a question someone actually asked.** Point to the thread, the PR comment, the onboarding question, the incident. Without one, do not write the page. "Document the service" produces a catalogue; "why does the settlement job run twice?" produces something useful.
2. **Nothing that restates the code.** No per-function prose, feature catalogues, directory listings, dependency inventories. API surface, config keys and CLI flags are generated from OpenAPI, schema or `--help`, or they are a table, or they are omitted.
3. **Explanation contains a "why not".** State what was rejected and what the choice costs. A page that only describes what exists is reference material in costume. This is the reliable tell for generated text: confident description of the chosen path, no credible account of what it forecloses.
4. **Every command is executable, and you executed it.** If you could not run it, do not stamp `last_verified`, and say so.
5. **Word budgets.** index 300 · how-to 800 · reference unbounded but tabular · explanation 1,500 · ADR 600 · runbook 700. A budget forces you to cut the throat-clearing paragraph instead of the specific detail.

## Banned register

Do not write these. They mark a sentence carrying no information.

```
comprehensive · robust · seamless · seamlessly · leverage (as a verb) · utilize
cutting-edge · state-of-the-art · powerful · rich set of · wide range of
it's important to note · it's worth noting · as we all know · needless to say
in today's fast-paced · delve into · a testament to · plays a vital role
this document aims to · this section will cover · in conclusion · let's dive in
```

Also banned: emoji as section markers, "🎯 Overview"-style headings, and a first paragraph that restates the page title.

## Structural checks

- No document whose headings are its folder names. GitHub renders a directory listing already.
- No forward-declared content. Never describe a file that does not exist. Never write a status page about documentation you intend to write.
- No unresolved placeholders: `TODO`, `TBD`, `@todo`, `<your-domain>`, `REPLACE_WITH_`, `coming soon`, `lorem`.
- No section that exists only because the template has it. Delete the heading.

## Self-review before finishing

For each file you wrote, answer:

1. Which question does this answer, and who asked it?
2. Which sentence here could be replaced by reading the code? Delete it.
3. If this is explanation — where is the "why not"?
4. Which commands did I run? Which did I not?
5. What is the word count against the budget?

If a file fails 1, delete the file. Do not soften it.
