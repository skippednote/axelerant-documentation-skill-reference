---
description: Run the commands in a doc, then stamp last_verified
---

Use the `axelerant-engineering-documentation` skill.

For the file I name (or every file under `docs/` if I name none):

1. Extract every shell command.
2. Run them on a clean checkout where possible. Report what failed.
3. Fix the document to match what actually happened.
4. Set `last_verified` to today only for files whose commands all succeeded. Leave it alone otherwise and tell me which.

$ARGUMENTS
