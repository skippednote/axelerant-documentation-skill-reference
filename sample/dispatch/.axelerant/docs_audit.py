#!/usr/bin/env python3
"""Audit a repo against the Axelerant Engineering Documentation Standard.

Usage:  python3 docs_audit.py [REPO_ROOT] [--strict]
Exit 1 with --strict when any BLOCK finding is present.
No third-party dependencies.
"""
import re
import sys
import datetime
from pathlib import Path

README_SECTIONS = [
    ("Status", True), ("Requirements", True), ("Quick start", True),
    ("Common commands", True), ("How we work here", True), ("Ownership", True),
    ("Documentation", "tier1+"),
]
TIER1_FILES = ["index.md", "getting-started.md", "architecture.md",
               "operations.md", "decisions.md"]
TIER2_DIRS = ["how-to", "reference", "explanation", "adr"]
BUDGETS = {"index": 300, "how-to": 800, "tutorial": 1200,
           "explanation": 1500, "adr": 600, "runbook": 700}
PLACEHOLDERS = re.compile(
    r"\bTODO\b|\bTBD\b|@todo|<your-|REPLACE_WITH_|coming soon|lorem ipsum", re.I)
FLUFF = re.compile(
    r"\b(comprehensive|robust|seamless(ly)?|leverages?|utilizes?|powerful|"
    r"cutting.edge|state.of.the.art|rich set of|wide range of|delve into|"
    r"a testament to|plays a vital role)\b|it'?s (important|worth) (to note|noting)|"
    r"this (document aims to|section will cover)|in conclusion|in today'?s fast.paced",
    re.I)
BANNED_PATHS = [
    (re.compile(r"docs/features/f\d{3}"), "per-feature catalogue"),
    (re.compile(r"docs/(improvements|roadmap)/"), "plans belong in the tracker"),
    (re.compile(r"(DOCUMENTATION_STATUS|MASTER_INDEX|IMPLEMENTATION_SUMMARY)\.md$"),
     "documentation about the documentation"),
]
ROOT_MD_ALLOWED = {"README.md", "AGENTS.md", "CLAUDE.md", "LICENSE.md",
                   "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md"}
FM_REQUIRED = ["title", "type", "owner", "last_verified"]
FM_REQUIRED_ADR = ["title", "type", "owner", "status", "date"]
ADR_STATUS = re.compile(r"^(proposed|accepted|deprecated|superseded by \d{4})$")

findings = []
ignore_globs = []


def add(level, path, msg):
    findings.append((level, str(path), msg))


def load_ignores(root):
    """Globs in .axelerant/audit-ignore are skipped.

    Style guides and file templates legitimately contain the banned register
    and placeholder tokens they exist to describe.
    """
    f = root / ".axelerant" / "audit-ignore"
    if not f.exists():
        return []
    return [ln.strip() for ln in f.read_text().splitlines()
            if ln.strip() and not ln.startswith("#")]


def ignored(rel):
    from fnmatch import fnmatch
    s = str(rel)
    return any(fnmatch(s, g) for g in ignore_globs)


def read_repo_yml(root):
    cfg = {"tier": None, "owner": None, "on_call": False, "docs_review_days": 90}
    f = root / ".axelerant" / "repo.yml"
    if not f.exists():
        add("BLOCK", ".axelerant/repo.yml", "missing — tier cannot be determined")
        return cfg
    for line in f.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        cfg[k.strip()] = v.strip().strip('"\'')
    if cfg.get("tier") is None:
        add("BLOCK", ".axelerant/repo.yml", "no tier declared")
    else:
        cfg["tier"] = int(cfg["tier"])
    cfg["on_call"] = str(cfg.get("on_call", "false")).lower() == "true"
    cfg["docs_review_days"] = int(cfg.get("docs_review_days", 90) or 90)
    return cfg


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.split("#", 1)[0].strip().strip('"\'')
    return fm


def body_words(text):
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            body = text[end + 4:]
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    return len(body.split())


def check_readme(root, tier):
    p = root / "README.md"
    if not p.exists():
        add("BLOCK", "README.md", "missing")
        return
    text = p.read_text()
    heads = [h.strip().lower() for h in re.findall(r"^#{1,3}\s+(.+)$", text, re.M)]
    if not re.match(r"^#\s+\S", text.strip()):
        add("BLOCK", "README.md", "no H1 title on the first line")
    for name, req in README_SECTIONS:
        if req == "tier1+" and tier == 0:
            continue
        if name.lower() not in heads:
            add("BLOCK", "README.md", f"missing required section: {name}")
    if len(text.splitlines()) > 400:
        add("WARN", "README.md", f"{len(text.splitlines())} lines, cap is 400")


def check_tree(root, tier, on_call):
    docs = root / "docs"
    if tier == 0:
        if docs.exists():
            add("BLOCK", "docs/", "Tier 0 must not have a docs/ directory")
        return
    if not docs.exists():
        add("BLOCK", "docs/", f"Tier {tier} requires a docs/ directory")
        return
    if tier == 1:
        for f in TIER1_FILES:
            if not (docs / f).exists():
                add("BLOCK", f"docs/{f}", "required at Tier 1")
        extra = [p.name for p in docs.iterdir()
                 if p.is_dir() and p.name not in ("adr", "assets")]
        for e in extra:
            add("BLOCK", f"docs/{e}/", "Tier 1 docs/ is flat; only adr/ and assets/ allowed")
    if tier == 2:
        if not (docs / "index.md").exists():
            add("BLOCK", "docs/index.md", "required at Tier 2")
        for d in TIER2_DIRS:
            if not (docs / d).is_dir():
                add("BLOCK", f"docs/{d}/", "required at Tier 2")
        if on_call and not (docs / "runbooks").is_dir():
            add("BLOCK", "docs/runbooks/", "on_call is true, so runbooks are required")
        for d in docs.iterdir():
            if d.is_dir():
                n = len([f for f in d.rglob("*.md")])
                if 0 < n < 3 and d.name not in ("adr", "runbooks", "tutorials", "assets"):
                    add("WARN", f"docs/{d.name}/", f"{n} file(s); subfolders start at 3")


def check_docs_files(root, cfg):
    today = datetime.date.today()
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        s = str(rel)
        if any(part in (".git", "node_modules", "vendor") for part in rel.parts):
            continue
        if ignored(rel):
            continue
        text = p.read_text(errors="ignore")
        for pat, why in BANNED_PATHS:
            if pat.search(s):
                add("BLOCK", s, f"must not exist — {why}")
        if len(rel.parts) == 1 and rel.name not in ROOT_MD_ALLOWED:
            add("WARN", s, "stray markdown at the repo root")
        m = PLACEHOLDERS.search(text)
        if m:
            add("BLOCK", s, f"unresolved placeholder: {m.group(0)!r}")
        m = FLUFF.search(text)
        if m:
            add("BLOCK", s, f"banned register: {m.group(0)!r}")
        if re.search(r"^#{1,6}\s+[\U0001F300-\U0001FAFF☀-➿]", text, re.M):
            add("BLOCK", s, "emoji used as a section marker")
        if not s.startswith("docs/"):
            continue
        fm = parse_frontmatter(text)
        if fm is None:
            add("BLOCK", s, "no frontmatter")
            continue
        t = fm.get("type", "")
        required = FM_REQUIRED_ADR if t == "adr" else FM_REQUIRED
        for k in required:
            if k not in fm or not fm[k]:
                add("BLOCK", s, f"frontmatter missing {k}")
        if t == "adr":
            if "last_verified" in fm:
                add("WARN", s, "ADRs are superseded, not re-verified; drop last_verified")
            if not ADR_STATUS.match(fm.get("status", "")):
                add("BLOCK", s, f"invalid ADR status: {fm.get('status','')!r}")
        if t and t not in BUDGETS and t not in ("reference",):
            add("WARN", s, f"unknown type: {t}")
        if t in BUDGETS:
            w = body_words(text)
            if w > BUDGETS[t]:
                add("WARN", s, f"{w} words, budget for {t} is {BUDGETS[t]}")
        lv = fm.get("last_verified", "")
        if re.match(r"\d{4}-\d{2}-\d{2}$", lv):
            age = (today - datetime.date.fromisoformat(lv)).days
            limit = 180 if t == "runbook" else cfg["docs_review_days"]
            if t == "runbook" and age > 180:
                add("BLOCK", s, f"runbook unverified for {age} days, ceiling is 180")
            elif age > limit * 2 and cfg["tier"] == 2:
                add("BLOCK", s, f"unverified for {age} days, over 2x {limit}")
            elif age > limit:
                add("WARN", s, f"unverified for {age} days, threshold is {limit}")
        elif lv:
            add("WARN", s, f"last_verified is not a date: {lv!r}")


def check_agents(root):
    a, c = root / "AGENTS.md", root / "CLAUDE.md"
    if not a.exists():
        add("WARN", "AGENTS.md", "missing")
    elif len(a.read_text().splitlines()) > 200:
        add("WARN", "AGENTS.md", "over the 200-line cap")
    if c.exists() and c.read_text().strip() not in ("@AGENTS.md",):
        add("WARN", "CLAUDE.md", "should contain only '@AGENTS.md'")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    root = Path(args[0] if args else ".").resolve()
    global ignore_globs
    ignore_globs = load_ignores(root)
    cfg = read_repo_yml(root)
    tier = cfg["tier"] if isinstance(cfg["tier"], int) else 1
    check_readme(root, tier)
    check_tree(root, tier, cfg["on_call"])
    check_docs_files(root, cfg)
    check_agents(root)

    blocks = [f for f in findings if f[0] == "BLOCK"]
    warns = [f for f in findings if f[0] == "WARN"]
    print(f"docs-audit: {root.name}  tier={cfg['tier']}  "
          f"{len(blocks)} block, {len(warns)} warn")
    for level, path, msg in blocks + warns:
        print(f"  {level:<5} {path:<44} {msg}")
    if not findings:
        print("  clean")
    return 1 if (strict and blocks) else 0


if __name__ == "__main__":
    sys.exit(main())
