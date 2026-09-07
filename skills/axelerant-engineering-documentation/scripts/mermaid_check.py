#!/usr/bin/env python3
"""Static fence checks; --render additionally uses an already installed mmdc."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from docs_audit import Audit, fences


def main():
    p=argparse.ArgumentParser();p.add_argument('root',nargs='?',default='.')
    p.add_argument('--render',action='store_true');args=p.parse_args()
    binary=os.getenv('MMDC_BIN') or shutil.which('mmdc')
    if args.render and not binary: p.error('--render requires preinstalled mmdc or MMDC_BIN; nothing is downloaded automatically')
    root=Path(args.root).resolve();errors=[];count=0
    for file in Audit(root).files():
        try:
            for lang,body,line in fences(file.read_text()):
                if lang!='mermaid': continue
                count+=1
                if not body.strip(): errors.append(f'{file}:{line}: empty block')
                elif args.render:
                    with tempfile.TemporaryDirectory() as td:
                        src=Path(td)/'source.mmd';dst=Path(td)/'out.svg';src.write_text(body)
                        config=Path(td)/'browser.json'
                        # CI runner is an ephemeral trusted environment; never render in a privileged host session.
                        config.write_text(json.dumps({'args':['--no-sandbox','--disable-setuid-sandbox']}))
                        r=subprocess.run([binary,'-i',str(src),'-o',str(dst),'-p',str(config)],capture_output=True,text=True,timeout=60)
                        if r.returncode or not dst.exists():
                            # Keep the head: the message is first, the tail is stack frames.
                            detail=' '.join((r.stderr or r.stdout or 'no output').split())[:400]
                            errors.append(f'{file}:{line}: {detail}')
        except (ValueError,OSError,subprocess.TimeoutExpired) as e: errors.append(f'{file}: {e}')
    print(f'Mermaid: {count} blocks; {len(errors)} errors; '+('rendered' if args.render else 'static only, parsing not established'))
    for error in errors: print(error)
    return bool(errors)

if __name__=='__main__': raise SystemExit(main())
