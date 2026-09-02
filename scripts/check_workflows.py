#!/usr/bin/env python3
"""Parse every workflow file. A syntax error here silently disables the gate.

Globs are bounded on purpose. A recursive `**` from the working directory walks
whatever happens to be above it, which is fast in CI and pathological anywhere
else.
"""
import glob
import sys

import yaml

PATTERNS = [
    ".github/workflows/*.y*ml",
    "*/.github/workflows/*.y*ml",
    "*/*/.github/workflows/*.y*ml",
]

files = sorted({f for p in PATTERNS for f in glob.glob(p)})
if not files:
    print("no workflow files found; run this from the repository root")
    sys.exit(1)

bad = 0
for f in files:
    try:
        yaml.safe_load(open(f))
        print(f"ok    {f}")
    except Exception as e:
        print(f"FAIL  {f}: {e}")
        bad = 1
sys.exit(bad)
