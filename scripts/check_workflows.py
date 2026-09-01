#!/usr/bin/env python3
"""Parse every workflow file. A syntax error here silently disables the gate."""
import glob
import sys

import yaml

bad = 0
files = sorted(set(glob.glob(".github/workflows/*.y*ml")
                   + glob.glob("**/.github/workflows/*.y*ml", recursive=True)))
for f in files:
    try:
        yaml.safe_load(open(f))
        print(f"ok    {f}")
    except Exception as e:
        print(f"FAIL  {f}: {e}")
        bad = 1
sys.exit(bad)
