from pathlib import Path
import json
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/axelerant-engineering-documentation/scripts'))
from docs_audit import frontmatter
name='axelerant-engineering-documentation'
manifest=json.loads((ROOT/'.claude-plugin/plugin.json').read_text())
errors=[]
if manifest.get('name')!=name or not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?',manifest.get('version','')):errors.append('invalid plugin identity/version')
for key in ('commands','skills'):
    value=manifest.get(key)
    if not isinstance(value,str) or not value.startswith('./') or not (ROOT/value).is_dir(): errors.append(f'invalid {key} path')
expected={'docs-init.md','docs-check.md','docs-verify.md','docs-book.md'}
files=list((ROOT/'commands').glob('*.md'))
if {f.name for f in files}!=expected:errors.append('unexpected command set')
for path in files:
    metadata,body=frontmatter(path.read_text())
    if not metadata.get('description') or f'Use the `{name}` skill.' not in body or '$ARGUMENTS' not in body: errors.append(f'invalid command {path.name}')
skill=ROOT/f'skills/{name}/SKILL.md';metadata,body=frontmatter(skill.read_text())
if metadata.get('name')!=name or not metadata.get('description'):errors.append('invalid skill metadata')
for relative in re.findall(r'`((?:references|scripts)/[A-Za-z0-9_./-]+)`',body):
    if not (skill.parent/relative).is_file():errors.append(f'missing skill dependency {relative}')
for path in ROOT.rglob('CLAUDE.md'):
    if any(p in {'node_modules','.git','.venv'} for p in path.parts):continue
    if path.read_text().strip()!='@AGENTS.md' or not (path.parent/'AGENTS.md').is_file():errors.append(f'invalid Claude import {path}')
if errors:raise SystemExit('\n'.join(errors))
print('Plugin structure, skill dependencies, four command delegates and all Claude imports: OK. Official plugin execution is a separate release check.')
