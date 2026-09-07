#!/usr/bin/env python3
"""Print a verification plan; execute only with explicit approval and a local immutable image.

No host directory is mounted. Source and commands are piped into the container.
This tool does not stamp evidence dates or claim production validity.
"""
import argparse
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import uuid
from docs_audit import SKIP

BOOTSTRAP = r'''
import io,json,os,subprocess,sys,tarfile
payload=sys.stdin.buffer.read()
with tarfile.open(fileobj=io.BytesIO(payload)) as tar:
    tar.extractall('/work',filter='data')
plan=json.load(open('/work/.verification-plan.json'))
for command in plan:
    print('$ '+command,flush=True)
    result=subprocess.run(['/bin/sh','-eu','-c',command],cwd='/work',env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/tmp','PYTHONDONTWRITEBYTECODE':'1'},timeout=60)
    if result.returncode: sys.exit(result.returncode)
'''

def build_command(image):
    return ['docker','run','--rm','-i','--pull=never','--network=none','--read-only',
            '--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=64','--memory=512m','--cpus=1',
            '--user=65534:65534','--tmpfs=/work:rw,nosuid,nodev,mode=1777,size=256m',
            '--tmpfs=/tmp:rw,nosuid,nodev,noexec,mode=1777,size=128m',
            '--entrypoint=python3',image,'-c',BOOTSTRAP]

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    p.add_argument('--command',action='append',required=True)
    p.add_argument('--image',help='preinstalled sha256:image-id or registry@sha256:digest')
    p.add_argument('--execute',action='store_true',help='explicitly approve the displayed plan')
    args=p.parse_args();print(json.dumps({'root':str(args.root),'commands':args.command,'image':args.image},indent=2))
    if not args.execute: print('PLAN ONLY: no commands executed and no dates changed'); return 0
    if not args.image or not re.fullmatch(r'(?:[^\s]+@)?sha256:[0-9a-f]{64}',args.image): p.error('execution requires an immutable approved image')
    if not shutil.which('docker'): print('Docker unavailable; plan only. No host fallback.'); return 2
    # Do not auto-detect commands from untrusted Markdown. A human approves each literal command.
    root=args.root.resolve();buf=io.BytesIO();total=0
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for path in sorted(root.rglob('*')):
            rel=path.relative_to(root)
            if any(part in SKIP for part in rel.parts) or path.is_symlink() or not path.is_file(): continue
            if path.name=='.env' or path.name.startswith('.env.') or path.name=='.verification-plan.json': continue
            total+=path.stat().st_size
            if total>64*1024*1024: p.error('snapshot exceeds 64 MiB')
            tar.add(path,arcname=str(rel),recursive=False)
        data=json.dumps(args.command).encode();info=tarfile.TarInfo('.verification-plan.json');info.size=len(data);info.mode=0o644
        tar.addfile(info,io.BytesIO(data))
    name='ax-docs-verify-'+uuid.uuid4().hex
    command=build_command(args.image)
    command[2:2]=['--name',name]
    try: return subprocess.run(command,input=buf.getvalue(),timeout=120).returncode
    except subprocess.TimeoutExpired: print('verification timed out; dates unchanged'); return 1
    finally:
        subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)


if __name__=='__main__': raise SystemExit(main())
