"""Validate YAML, remote action pinning, and reusable workflow inputs.

This is a local structural check, not a substitute for GitHub Actions execution.
"""
from pathlib import Path
import re
import sys
import yaml
ROOT=Path(__file__).resolve().parents[1]
errors=[]; docs={}
for path in sorted(set((ROOT/'.github/workflows').glob('*.yml')) | set((ROOT/'sample/dispatch/.github/workflows').glob('*.yml'))):
    try:
        doc=yaml.load(path.read_text(),Loader=yaml.BaseLoader)
        if not isinstance(doc,dict) or not all(k in doc for k in ('on','jobs')): raise ValueError('workflow must have on and jobs mappings')
        docs[path]=doc
        refs=re.findall(r'^\s*-?\s*uses:\s*(\S+)',path.read_text(),re.M)
        for ref in refs:
            if ref.startswith('./'):continue
            if not re.fullmatch(r'[^\s@]+@[0-9a-f]{40}',ref):errors.append(f'{path.name}: non-immutable action: {ref}')
    except Exception as e: errors.append(f'{path.name}: {e}')
for path,doc in docs.items():
    for name,job in doc['jobs'].items():
        if not isinstance(job,dict):errors.append(f'{path.name}: invalid job');continue
        ref=job.get('uses','')
        if ref.startswith('./'):
            target=ROOT/ref
            if target not in docs:errors.append(f'{path.name}/{name}: missing reusable target');continue
            expected=docs[target]['on']['workflow_call'].get('inputs',{})
            supplied=job.get('with',{})
            extra=set(supplied)-set(expected)
            required={k for k,v in expected.items() if v.get('required')=='true'}
            if extra or required-set(supplied):errors.append(f'{path.name}/{name}: invalid inputs, extra {extra}, missing {required-set(supplied)}')
check=docs.get(ROOT/'.github/workflows/docs-check.yml',{})
steps=check.get('jobs',{}).get('checks',{}).get('steps',[])
ids={s.get('id'):s for s in steps if 'id' in s}
for key in ('contract','markdown','vale','install','dependencies','browser','diagrams','links'):
    if ids.get(key,{}).get('continue-on-error')!='true':errors.append(f'{key}: results must reach the central enforcement gate')
if not steps or steps[-1].get('if')!='always()':errors.append('missing always-run enforcement gate')
if errors:raise SystemExit('\n'.join(errors))
print(f'Workflow validation: {len(docs)} files, immutable actions, valid reusable inputs and centralized enforcement.')
