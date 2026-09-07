---
description: Assemble the documentation in this repository into one book, and a PDF on request
---

Use the `axelerant-engineering-documentation` skill.

Build the book from the tree that already exists. Do not write new pages to fill it out, and do not
reorder anything by editing files: the spine is `.axelerant/book.yml`, and it only reorders.

1. Run `scripts/build_book.py <repo>`, adding `--pdf` if I asked for one.
2. If it reports a missing page named by `book.yml`, or a diagram that will not render, fix that and
   say what was wrong. Those are documentation defects, not build problems.
3. Tell me where the files are, how many chapters and pages, and how many diagrams were rendered.
4. If the repository is `internal` or `client-confidential`, say so and say that the cover banner is
   a label rather than a control. Where the book goes is my decision.

Do not stamp or refresh any `last_verified` date. Assembling a book proves nothing about whether the
pages are still true.

$ARGUMENTS
