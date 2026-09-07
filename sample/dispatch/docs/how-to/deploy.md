---
title: Package the local example
type: how-to
owner: "@axelerant/dispatch-admins"
last_verified: 2026-09-03
verification_method: automated-test
---

# Package the local example

This fixture has no staging or production deployment. The handover operation packages its source.

```bash
make package
```

The archive is `dist/dispatch.zip`. It includes the Makefile, source, tests and documentation. It excludes generated state and caches.

Extract it into a fresh directory to run `make test`. The documentation audit is not part of this example: it runs against the example from outside, so the checker is never duplicated inside it.

Keep the previous archive for rollback; extract it separately rather than overlaying different source versions.
