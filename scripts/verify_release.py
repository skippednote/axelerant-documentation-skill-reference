"""Fail closed when release evidence or runtime tools are absent."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
lock=ROOT/'package-lock.json'
if not lock.is_file():raise SystemExit('RELEASE BLOCKED: regenerate and review package-lock.json with npm install --package-lock-only --ignore-scripts')
package=json.loads((ROOT/'package.json').read_text());locked=json.loads(lock.read_text())
for name,version in package['devDependencies'].items():
    if locked.get('packages',{}).get('node_modules/'+name,{}).get('version')!=version:
        raise SystemExit(f'RELEASE BLOCKED: lockfile mismatch for {name}')
for binary in ('npm','claude'):
    if not shutil.which(binary):raise SystemExit('RELEASE BLOCKED: missing '+binary)
def run(command,**kw):subprocess.run(command,cwd=ROOT,check=True,**kw)
run(['npm','ci','--ignore-scripts','--no-fund'],env={**os.environ,'PUPPETEER_SKIP_DOWNLOAD':'true'})
run(['npm','audit','--audit-level=high'])
run([str(ROOT/'node_modules/.bin/puppeteer'),'browsers','install','chrome'])
for scope in ('.','sample/dispatch'):
    run([sys.executable,'skills/axelerant-engineering-documentation/scripts/mermaid_check.py',scope,'--render'],env={**os.environ,'MMDC_BIN':str(ROOT/'node_modules/.bin/mmdc')})
run(['claude','plugin','validate',str(ROOT)])
print('Local release prerequisites passed. Hosted Markdown/external-link checks and a real plugin load remain required.')
