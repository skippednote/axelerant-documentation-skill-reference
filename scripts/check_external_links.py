"""Run a preinstalled Lychee against explicit files, respecting scoped link exemptions."""
import json
from pathlib import Path
import subprocess
import sys
files=json.loads(Path(sys.argv[1]).read_text())
if not files: print('No external link inputs');raise SystemExit(0)
# .test and loopback addresses are intentional executable-example destinations.
cmd=['lychee','--no-progress','--exclude',r'^https?://(?:localhost|127\.0\.0\.1|[^/]+\.test)(?:[:/]|$)','--exclude-all-private',*files]
raise SystemExit(subprocess.run(cmd,check=False).returncode)
