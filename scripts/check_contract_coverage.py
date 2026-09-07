from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/axelerant-engineering-documentation/scripts'))
from docs_audit import RULES
contract=ROOT/'skills/axelerant-engineering-documentation/references/contract.md'
marked=set(re.findall(r'<!-- check: ([a-z_-]+) -->',contract.read_text()))
if marked!=RULES: raise SystemExit(f'Rule mismatch: unimplemented {marked-RULES}; undocumented {RULES-marked}')
tests=(ROOT/'tests/test_contract.py').read_text()
for rule in RULES:
    if f'def test_{rule}(' not in tests: raise SystemExit(f'Missing negative fixture for {rule}')
print(f'Coverage declarations: {len(RULES)} rule groups, matching negative fixtures. Behavior is established by tests, not this identifier check.')
