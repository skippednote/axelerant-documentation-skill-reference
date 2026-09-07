---
title: Package the local example
type: how-to
owner: "@axelerant/platform-team"
last_verified: 2026-09-03
verification_method: automated-test
---

# Package the local example

This fixture has no staging or production deployment. The handover operation packages its source.

```bash
make package
```

The archive is `dist/dispatch.zip`. It includes the Makefile, source, tests and documentation. It excludes generated state and caches.

Extract it into a fresh directory to run `make test`. `make docs-check` is run from the parent reference checkout because the checker is deliberately not duplicated inside this example.

Keep the previous archive for rollback; extract it separately rather than overlaying different source versions.
