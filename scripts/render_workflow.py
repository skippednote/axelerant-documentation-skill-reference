"""Render an adopting repository's workflow against one immutable source commit.

The shipped template already pins the current release. Use this when adopting a
different reviewed commit, or when generating the file from automation.
"""
import argparse
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('commit', help='full 40-character reviewed commit SHA')
p.add_argument('--output', type=Path)
p.add_argument('--mode', choices=['warn', 'block'], default='block')
p.add_argument('--no-coupling', action='store_true',
               help='omit the documentation reminder job')
a = p.parse_args()
if not re.fullmatch('[0-9a-f]{40}', a.commit):
    p.error('expected a full reviewed commit SHA, not a tag or short SHA')

SOURCE = 'skippednote/axelerant-documentation-skill-reference'
text = f'''name: docs
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  docs:
    uses: {SOURCE}/.github/workflows/docs-check.yml@{a.commit}
    with:
      ref: {a.commit}
      path: .
      enforcement: {a.mode}
'''
if not a.no_coupling:
    text += f'''  coupling:
    if: github.event_name == 'pull_request'
    # A called workflow cannot hold more permission than its caller grants.
    permissions:
      contents: read
      pull-requests: write
    uses: {SOURCE}/.github/workflows/docs-coupling.yml@{a.commit}
    with:
      ref: {a.commit}
'''

if a.output:
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(text)
    print(a.output)
else:
    print(text, end='')
