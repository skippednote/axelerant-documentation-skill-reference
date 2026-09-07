"""Create Markdown-only lint input copies; caller configs cannot weaken house lint.

The real checkout is used for contract/local-link checks. Lint copies omit each
check's individually exempted files. Never execute scripts from the caller.
"""
from pathlib import Path
import argparse
import json
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/axelerant-engineering-documentation/scripts'))
from docs_audit import Audit
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path)
a=p.parse_args();audit=Audit(a.root);audit.config()
a.output.mkdir(parents=True,exist_ok=True)
for name in ('markdown','prose'):(a.output/name).mkdir(exist_ok=True)
files=list(audit.files())
for source in files:
    rel=source.relative_to(audit.root)
    for name in ('markdown','prose'):
        if name=='prose' and audit.ignored('register',rel.as_posix()):continue
        target=a.output/name/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
# Actual source paths for external link checks; relative links are checked by the audit.
(a.output/'external-files.json').write_text(json.dumps([str(f) for f in files if not audit.ignored('links',f.relative_to(audit.root).as_posix())]))
print(f'{len(files)} Markdown files selected from {audit.root}')
