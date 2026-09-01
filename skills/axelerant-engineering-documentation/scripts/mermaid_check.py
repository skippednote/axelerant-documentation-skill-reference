#!/usr/bin/env python3
"""Check the Mermaid blocks in a tree.

Two layers, because they catch different things:

  Static (default, no dependencies) — the footguns that produce a rendered
  parse error on GitHub. Cheap enough to run on every save.

  Render (--render, needs npx) — hands each block to mermaid-cli, which is the
  only authoritative answer to "does this render". Used in CI.

Usage:  python3 mermaid_check.py [ROOT] [--render] [--keep DIR]
Exit 1 on any finding.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BLOCK = re.compile(r"```mermaid[^\n]*\n(.*?)```", re.S)

KNOWN = {
    "graph", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "journey", "gantt", "pie", "quadrantChart",
    "requirementDiagram", "gitGraph", "mindmap", "timeline", "sankey-beta",
    "xychart-beta", "block-beta", "C4Context", "C4Container", "C4Component",
    "C4Dynamic", "C4Deployment", "architecture-beta",
}
# The contract keeps C4 to levels 1 and 2. Component and code level cannot be
# maintained by hand and go stale before the sprint ends.
BANNED_TYPES = {"C4Component", "C4Dynamic", "C4Deployment"}

findings = []


def add(path, block, line, msg):
    findings.append((f"{path}#{block}", line, msg))


def blocks(text):
    for i, m in enumerate(BLOCK.finditer(text), 1):
        yield i, m.group(1), text[: m.start()].count("\n") + 1


def static_check(path, index, body):
    lines = body.splitlines()
    stripped = [ln for ln in lines if ln.strip() and not ln.strip().startswith("%%")]
    if not stripped:
        add(path, index, 0, "empty mermaid block")
        return
    head = stripped[0].strip().split()[0].rstrip(";")
    if head not in KNOWN:
        add(path, index, 1, f"unknown diagram type {head!r}")
    if head in BANNED_TYPES:
        add(path, index, 1,
            f"{head} is C4 level 3 or 4; the contract keeps diagrams to levels 1 and 2")
    for n, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s or s.startswith("%%"):
            continue
        # A semicolon separates statements. Inside note or label text it
        # silently truncates the statement and breaks the block.
        if ";" in s and not s.endswith(";"):
            add(path, index, n,
                "semicolon inside a line separates statements; use a comma")
        if s.startswith(("Note ", "note ")) and ":" not in s:
            add(path, index, n, "note without a colon")
    opens = sum(1 for ln in lines if ln.strip().startswith(("alt ", "opt ", "loop ", "par ", "critical ", "rect ")))
    ends = sum(1 for ln in lines if ln.strip() == "end")
    if opens != ends:
        add(path, index, 0, f"{opens} block opener(s) and {ends} end(s)")


def render_check(path, index, body):
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "d.mmd"
        src.write_text(body)
        out = Path(d) / "d.svg"
        # CI runners have no sandbox available to the browser puppeteer starts.
        cfg = Path(d) / "puppeteer.json"
        cfg.write_text(json.dumps({"args": ["--no-sandbox", "--disable-setuid-sandbox"]}))
        try:
            r = subprocess.run(
                ["npx", "-y", "@mermaid-js/mermaid-cli@11",
                 "-i", str(src), "-o", str(out), "-p", str(cfg)],
                capture_output=True, text=True, timeout=180)
        except FileNotFoundError:
            print("npx not found; skipping the render pass", file=sys.stderr)
            return False
        except subprocess.TimeoutExpired:
            add(path, index, 0, "mermaid-cli timed out")
            return True
        if not out.exists():
            msg = next((ln for ln in (r.stderr + r.stdout).splitlines()
                        if "error" in ln.lower() or "Expecting" in ln), "render failed")
            add(path, index, 0, msg.strip()[:200])
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--render", action="store_true",
                    help="also render each block with mermaid-cli")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    total = 0
    skip = {".git", "node_modules", "vendor", ".docs-standard"}
    for f in sorted(root.rglob("*.md")):
        if any(p in skip for p in f.parts):
            continue
        text = f.read_text(errors="ignore")
        rel = f.relative_to(root)
        for index, body, _ in blocks(text):
            total += 1
            static_check(rel, index, body)
            if args.render:
                render_check(rel, index, body)

    mode = "static + render" if args.render else "static"
    print(f"mermaid-check ({mode}): {total} block(s), {len(findings)} finding(s)")
    for where, line, msg in findings:
        loc = f"{where} line {line}" if line else where
        print(f"  {loc}: {msg}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
