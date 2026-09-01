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

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import mermaid_check
except ImportError:                                   # standalone copy
    mermaid_check = None

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


def prose_only(text):
    """Strip fenced blocks and inline code before scanning prose.

    A style guide names the tokens it rejects, and a template shows the
    placeholders it expects to be replaced. Scanning those as prose makes the
    audit unable to describe its own rules.
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


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
        if any(part in (".git", "node_modules", "vendor", ".docs-standard") for part in rel.parts):
            continue
        if ignored(rel):
            continue
        text = p.read_text(errors="ignore")
        for pat, why in BANNED_PATHS:
            if pat.search(s):
                add("BLOCK", s, f"must not exist — {why}")
        if len(rel.parts) == 1 and rel.name not in ROOT_MD_ALLOWED:
            add("WARN", s, "stray markdown at the repo root")
        prose = prose_only(text)
        m = PLACEHOLDERS.search(prose)
        if m:
            add("BLOCK", s, f"unresolved placeholder: {m.group(0)!r}")
        m = FLUFF.search(prose)
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


def check_mermaid(root):
    """Static Mermaid checks. The render pass is a separate CI job."""
    if mermaid_check is None:
        add("WARN", "-", "mermaid_check.py not alongside; diagram checks skipped")
        return
    mermaid_check.findings = []
    for f in sorted(root.rglob("*.md")):
        rel = f.relative_to(root)
        if any(p in (".git", "node_modules", "vendor", ".docs-standard") for p in rel.parts):
            continue
        if ignored(rel):
            continue
        text = f.read_text(errors="ignore")
        for index, body, _ in mermaid_check.blocks(text):
            mermaid_check.static_check(rel, index, body)
    for where, line, msg in mermaid_check.findings:
        add("BLOCK", f"{where}" + (f" line {line}" if line else ""), msg)


# Sections that belong in docs/ or the README, not in the agent file.
MISPLACED = [
    (re.compile(r"^#{1,6}\s*(architecture|system (overview|design)|how it (works|fits))",
                re.I), "docs/explanation/architecture.md"),
    (re.compile(r"^#{1,6}\s*(directory|repo(sitory)?|file|project) (structure|layout|map)",
                re.I), "nowhere — the tree is the tree"),
    (re.compile(r"^#{1,6}\s*(setup|install(ation)?|prerequisites|getting started|quick ?start)",
                re.I), "README, Quick start"),
    (re.compile(r"^#{1,6}\s*(deploy(ment)?|release process)", re.I),
     "docs/how-to/deploy.md, or docs/operations.md at Tier 1"),
    (re.compile(r"^#{1,6}\s*(dependencies|tech stack|features?)\b", re.I),
     "docs/reference/, or delete it"),
]
# Backticked repo-relative paths in the jump table.
PATHREF = re.compile(r"`([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+)`")


def check_agents(root, tier):
    a, c, g = root / "AGENTS.md", root / "CLAUDE.md", root / "GEMINI.md"

    if g.exists():
        add("BLOCK", "GEMINI.md", "one agent file: AGENTS.md, with CLAUDE.md importing it")

    if not a.exists():
        if c.exists():
            add("BLOCK", "CLAUDE.md",
                "agent file is not AGENTS.md; rename it and leave CLAUDE.md as '@AGENTS.md'")
        else:
            add("WARN", "AGENTS.md", "missing")
        return

    text = a.read_text()
    lines = text.splitlines()
    if len(lines) > 200:
        add("BLOCK", "AGENTS.md", f"{len(lines)} lines, cap is 200")

    for line in lines:
        for pat, dest in MISPLACED:
            if pat.match(line.strip()):
                add("BLOCK", "AGENTS.md",
                    f"{line.strip()[:48]!r} belongs in {dest}")

    # Only documentation targets. Source paths and symbols are not jump-table
    # entries and are none of this check's business.
    for m in PATHREF.finditer(text):
        ref = m.group(1)
        if "..." in ref or ref.startswith(("http", "@")):
            continue
        if not (ref.endswith(".md") or ref.endswith("/")):
            continue
        if not (root / ref).exists():
            add("BLOCK", "AGENTS.md", f"points at {ref}, which does not exist")

    if tier and tier > 0 and "docs/" not in text:
        add("WARN", "AGENTS.md", "no jump table into docs/")

    if c.exists():
        if c.read_text().strip() != "@AGENTS.md":
            add("BLOCK", "CLAUDE.md", "must contain only '@AGENTS.md'")
    else:
        add("WARN", "CLAUDE.md", "missing; Claude Code will not read AGENTS.md without it")


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
    check_mermaid(root)
    check_agents(root, tier)

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
