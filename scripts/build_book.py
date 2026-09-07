#!/usr/bin/env python3
"""Assemble a repository's documentation into one book, and optionally a PDF.

The tree this standard already requires is the book: tiers fix the chapter set,
directory README files are section openers, and frontmatter supplies titles,
owners and evidence dates. Nothing has to be restated to publish.

Output is a single self-contained HTML file with print rules, so it reads in a
browser and prints to PDF without a hosted site. --pdf drives the same headless
browser the diagram check already pins, so publishing adds no new toolchain.

Usage:
  python3 scripts/build_book.py <repo> [--output DIR] [--pdf] [--title TEXT]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent /
                      'skills/axelerant-engineering-documentation/scripts'))
from docs_audit import frontmatter, scalar_yaml  # noqa: E402

# Reader order, not folder order. Someone meeting the system reads the
# overview, learns, does, looks up, understands, then operates it.
PLATFORM_ORDER = ['tutorials', 'how-to', 'reference', 'explanation', 'adr', 'runbooks']
PROJECT_ORDER = ['getting-started.md', 'architecture.md', 'operations.md', 'decisions.md']
SECTION_TITLES = {
    'tutorials': 'Tutorials', 'how-to': 'How-to guides', 'reference': 'Reference',
    'explanation': 'Explanation', 'adr': 'Decision records', 'runbooks': 'Runbooks',
}
BANNER = {
    'public': None,
    'internal': 'Internal — Axelerant staff only',
    'client-confidential': 'Client confidential — do not redistribute',
}


def die(message: str) -> None:
    raise SystemExit(f'build_book: {message}')


def load_markdown():
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        die('needs markdown-it-py; install requirements-ci.txt')
    return (MarkdownIt('commonmark', {'html': False})
            .enable('table').enable('strikethrough'))


def spine(root: Path, cfg: dict) -> list[tuple[str, list[Path]]]:
    """Chapters in reading order: (section title, pages)."""
    docs = root / 'docs'
    if cfg['tier'] == 0 or not docs.is_dir():
        return []
    declared = {}
    book = root / '.axelerant/book.yml'
    if book.is_file():
        try:
            declared = scalar_yaml(book.read_text())
        except ValueError as e:
            die(f'.axelerant/book.yml: {e}')

    def ordered(folder: Path, explicit) -> list[Path]:
        pages = sorted(p for p in folder.glob('*.md') if p.name != 'README.md')
        if explicit:
            if not isinstance(explicit, list):
                die(f'book.yml: {folder.name} must be a list of quoted filenames')
            wanted = [folder / str(n) for n in explicit]
            missing = [p for p in wanted if not p.is_file()]
            if missing:
                die(f'book.yml names a page that does not exist: '
                    f'{missing[0].relative_to(root)}')
            pages = wanted + [p for p in pages if p not in wanted]
        return ([folder / 'README.md'] if (folder / 'README.md').is_file() else []) + pages

    if cfg['tier'] == 1:
        flat = [docs / n for n in PROJECT_ORDER if (docs / n).is_file()]
        extra = sorted(p for p in docs.glob('*.md')
                       if p.name != 'README.md' and p not in flat)
        chapters = [('Documentation', [docs / 'README.md'] + flat + extra)]
        if (docs / 'adr').is_dir():
            chapters.append(('Decision records', ordered(docs / 'adr', declared.get('adr'))))
        return chapters

    chapters = [('Overview', [docs / 'README.md'])]
    for name in PLATFORM_ORDER:
        folder = docs / name
        if folder.is_dir():
            pages = ordered(folder, declared.get(name))
            if pages:
                chapters.append((SECTION_TITLES[name], pages))
    return chapters


def render_mermaid(code: str, binary: str, cache: dict) -> str | None:
    """Return inline SVG. A book is printed, so a live renderer is not there."""
    if code in cache:
        return cache[code]
    with tempfile.TemporaryDirectory() as td:
        src, out = Path(td) / 'd.mmd', Path(td) / 'd.svg'
        cfg = Path(td) / 'browser.json'
        cfg.write_text(json.dumps({'args': ['--no-sandbox', '--disable-setuid-sandbox']}))
        src.write_text(code)
        result = subprocess.run([binary, '-i', str(src), '-o', str(out), '-p', str(cfg)],
                                capture_output=True, text=True, timeout=120)
        if result.returncode or not out.exists():
            detail = ' '.join((result.stderr or 'no output').split())[:200]
            die(f'diagram did not render: {detail}')
        svg = out.read_text()
    svg = re.sub(r'<\?xml[^>]*\?>', '', svg).strip()
    cache[code] = svg
    return svg


def page_html(md, path: Path, root: Path, anchors: dict, binary: str | None,
              cache: dict) -> tuple[str, dict]:
    raw = path.read_text()
    try:
        meta, body = frontmatter(raw)
    except ValueError:
        meta, body = {}, raw
    slug = anchors[path]

    # Diagrams become pictures, because a printed book has no live renderer.
    # They are swapped in after the Markdown pass, through a placeholder: the
    # renderer keeps raw HTML disabled, so a page cannot inject markup of its
    # own into the book.
    diagrams: dict[str, str] = {}

    def reserve(match):
        if binary is None:
            return ''
        token = f'axdiagramtoken{len(diagrams)}'
        diagrams[token] = render_mermaid(match.group(1), binary, cache)
        return f'\n{token}\n'

    body = re.sub(r'```mermaid\n(.*?)```', reserve, body, flags=re.S)
    rendered = md.render(body)
    for token, svg in diagrams.items():
        rendered = rendered.replace(f'<p>{token}</p>',
                                    f'<div class="diagram">{svg}</div>')

    # A book has no filesystem, so cross-page links become internal anchors.
    def relink(match):
        quote, target = match.group(1), match.group(2)
        if re.match(r'[a-z]+:|#|//', target):
            return match.group(0)
        anchor, _, frag = target.partition('#')
        resolved = (path.parent / anchor).resolve() if anchor else path
        for page, ref in anchors.items():
            if page.resolve() == resolved:
                return f'href={quote}#{ref}{quote}'
        return f'href={quote}#{quote}'

    rendered = re.sub(r'href=(["\'])([^"\']+)\1', relink, rendered)
    # Headings inside a chapter drop one level so the page title is the top.
    for level in range(5, 0, -1):
        rendered = rendered.replace(f'<h{level}>', f'<h{level + 1}>')
        rendered = rendered.replace(f'</h{level}>', f'</h{level + 1}>')
    title = meta.get('title') or path.stem.replace('-', ' ').capitalize()
    return (f'<section class="page" id="{slug}">'
            f'<h2>{html.escape(str(title))}</h2>'
            f'{provenance(meta)}{rendered}</section>'), meta


def provenance(meta: dict) -> str:
    """What the page claims about itself, kept with the page in print."""
    bits = []
    for key, label in (('type', 'Type'), ('owner', 'Owner'),
                       ('last_verified', 'Verified'), ('verification_method', 'Method'),
                       ('status', 'Status'), ('date', 'Decided')):
        if meta.get(key):
            bits.append(f'<span><b>{label}</b> {html.escape(str(meta[key]))}</span>')
    return f'<p class="provenance">{"".join(bits)}</p>' if bits else ''


STYLE = """
:root{--ink:#141719;--muted:#5b6570;--line:#d8dde2;--accent:#8c2f24;--bg:#fff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.6 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif}
.sheet{max-width:44rem;margin:0 auto;padding:3rem 2rem 5rem}
h1,h2,h3,h4,h5{line-height:1.2;letter-spacing:-.01em;font-weight:600}
h1{font-size:2.4rem;margin:0 0 .4rem}
h2{font-size:1.7rem;margin:0 0 .75rem;padding-bottom:.4rem;border-bottom:2px solid var(--ink)}
h3{font-size:1.2rem;margin:2rem 0 .5rem}
h4,h5{font-size:1rem;margin:1.4rem 0 .4rem}
p,li{orphans:3;widows:3}
code,pre{font-family:"SF Mono",ui-monospace,Menlo,Consolas,monospace}
code{font-size:.86em;background:#f2f4f6;border:1px solid var(--line);border-radius:3px;padding:.05em .3em}
pre{background:#f7f8fa;border:1px solid var(--line);border-radius:5px;padding:.9rem 1rem;
  overflow-x:auto;font-size:.78rem;line-height:1.55;page-break-inside:avoid}
pre code{background:none;border:0;padding:0;font-size:inherit}
table{border-collapse:collapse;width:100%;font-size:.88rem;margin:1rem 0;page-break-inside:avoid}
th,td{border:1px solid var(--line);padding:.45rem .6rem;text-align:left;vertical-align:top}
th{background:#f2f4f6}
blockquote{margin:1rem 0;padding-left:1rem;border-left:3px solid var(--line);color:var(--muted)}
a{color:var(--accent)}
.diagram{margin:1.2rem 0;text-align:center;page-break-inside:avoid}
.diagram svg{max-width:100%;height:auto}
.provenance{margin:-.2rem 0 1.2rem;font-size:.74rem;color:var(--muted);
  font-family:system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:.2rem 1.1rem}
.provenance b{font-weight:600;color:var(--ink)}
.cover{min-height:88vh;display:flex;flex-direction:column;justify-content:center;
  page-break-after:always;border-bottom:0}
.cover .kicker{font-family:system-ui,sans-serif;font-size:.8rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--accent);margin-bottom:1.2rem}
.cover dl{font-family:system-ui,sans-serif;font-size:.85rem;color:var(--muted);
  display:grid;grid-template-columns:8rem 1fr;gap:.35rem 1rem;margin-top:2.5rem}
.cover dt{font-weight:600;color:var(--ink)}
.banner{font-family:system-ui,sans-serif;font-size:.78rem;font-weight:600;
  border:1px solid var(--accent);color:var(--accent);border-radius:4px;
  padding:.5rem .8rem;margin-bottom:2rem;display:inline-block}
.contents{page-break-after:always}
.contents ol{list-style:none;padding:0;font-family:system-ui,sans-serif;font-size:.92rem}
.contents > ol > li{margin:1rem 0 .3rem;font-weight:600}
.contents ol ol{margin:.2rem 0 0 1rem;font-weight:400}
.contents a{text-decoration:none;color:var(--ink)}
.chapter{page-break-before:always}
.chapter > h1{font-size:1.9rem;color:var(--accent);margin-bottom:2rem}
.page{page-break-before:always}
.chapter > .page:first-of-type{page-break-before:avoid}
@media print{
  @page{size:A4;margin:18mm 16mm 20mm}
  body{font-size:10.5pt}
  .sheet{max-width:none;padding:0}
  a{color:var(--ink);text-decoration:none}
  pre{font-size:8pt}
}
"""


def build(root: Path, out_dir: Path, title: str | None, want_pdf: bool,
          if_applicable: bool = False) -> Path | None:
    cfg_path = root / '.axelerant/repo.yml'
    if not cfg_path.is_file():
        die(f'{cfg_path} not found; a book is built from a declared repository')
    cfg = scalar_yaml(cfg_path.read_text())
    for key in ('tier', 'owner', 'visibility'):
        if key not in cfg:
            die(f'repo.yml is missing {key}')

    chapters = spine(root, cfg)
    if not chapters:
        message = 'no docs/ tree to publish; Component repositories have a README, not a book'
        if if_applicable:
            # A sweep across every repository should skip these, not fail on them.
            print(f'build_book: skipped, {message}')
            return None
        die(message)

    binary = os.getenv('MMDC_BIN') or shutil.which('mmdc')
    if binary is None:
        print('build_book: no mmdc found, diagrams will be omitted', file=sys.stderr)

    md = load_markdown()
    anchors, seen = {}, set()
    for _, pages in chapters:
        for page in pages:
            base = re.sub(r'[^a-z0-9]+', '-',
                          str(page.relative_to(root / 'docs')).lower()).strip('-')
            slug, n = base, 2
            while slug in seen:
                slug, n = f'{base}-{n}', n + 1
            seen.add(slug)
            anchors[page] = slug

    cache: dict[str, str] = {}
    body, contents = [], []
    for chapter, pages in chapters:
        cid = re.sub(r'[^a-z0-9]+', '-', chapter.lower()).strip('-')
        entries = []
        rendered_pages = []
        for page in pages:
            markup, meta = page_html(md, page, root, anchors, binary, cache)
            rendered_pages.append(markup)
            label = meta.get('title') or page.stem
            entries.append(f'<li><a href="#{anchors[page]}">{html.escape(str(label))}</a></li>')
        contents.append(f'<li><a href="#{cid}">{html.escape(chapter)}</a>'
                        f'<ol>{"".join(entries)}</ol></li>')
        body.append(f'<div class="chapter" id="{cid}"><h1>{html.escape(chapter)}</h1>'
                    f'{"".join(rendered_pages)}</div>')

    name = title or root.name
    banner = BANNER.get(cfg['visibility'])
    today = dt.date.today().isoformat()
    cover = (
        '<section class="cover">'
        + (f'<div class="banner">{html.escape(banner)}</div>' if banner else '')
        + '<p class="kicker">Axelerant engineering documentation</p>'
        + f'<h1>{html.escape(str(name))}</h1>'
        + '<dl>'
        + f'<dt>Tier</dt><dd>{cfg["tier"]}</dd>'
        + f'<dt>Owner</dt><dd>{html.escape(str(cfg["owner"]))}</dd>'
        + f'<dt>Visibility</dt><dd>{html.escape(str(cfg["visibility"]))}</dd>'
        + (f'<dt>Client</dt><dd>{html.escape(str(cfg["client"]))}</dd>' if cfg.get('client') else '')
        + f'<dt>Assembled</dt><dd>{today}</dd>'
        + '</dl>'
        + '<p class="provenance"><span>Assembled from the repository. Each page keeps the '
          'evidence date and method it was published with; the assembly date is not one.</span></p>'
        + '</section>')

    document = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{html.escape(str(name))} — documentation</title>'
                f'<style>{STYLE}</style></head><body><div class="sheet">'
                f'{cover}'
                f'<nav class="contents"><h1>Contents</h1><ol>{"".join(contents)}</ol></nav>'
                f'{"".join(body)}</div></body></html>')

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r'[^a-z0-9]+', '-', str(name).lower()).strip('-') or 'documentation'
    html_path = out_dir / f'{stem}-documentation.html'
    html_path.write_text(document)
    pages_total = sum(len(p) for _, p in chapters)
    print(f'{html_path}  ({len(chapters)} chapters, {pages_total} pages, '
          f'{len(cache)} diagrams)')

    if want_pdf:
        pdf_path = out_dir / f'{stem}-documentation.pdf'
        chrome = find_chrome()
        if not chrome:
            die('no headless browser found for --pdf; install one with '
                './node_modules/.bin/puppeteer browsers install chrome-headless-shell')
        subprocess.run([chrome, '--headless', '--disable-gpu', '--no-sandbox',
                        '--no-pdf-header-footer', f'--print-to-pdf={pdf_path}',
                        html_path.resolve().as_uri()],
                       check=True, capture_output=True, timeout=180)
        print(f'{pdf_path}  ({pdf_path.stat().st_size // 1024} KB)')
    return html_path


def find_chrome() -> str | None:
    """Reuse the browser the diagram check already pins."""
    explicit = os.getenv('CHROME_BIN')
    if explicit and Path(explicit).exists():
        return explicit
    cache = Path(os.getenv('PUPPETEER_CACHE_DIR') or Path.home() / '.cache/puppeteer')
    candidates = sorted(cache.glob('chrome-headless-shell/*/*/chrome-headless-shell'))
    candidates += sorted(cache.glob('chrome/*/*/Google Chrome for Testing'))
    candidates += sorted(cache.glob('chrome/*/*/chrome'))
    if candidates:
        return str(candidates[-1])
    return shutil.which('chrome-headless-shell') or shutil.which('google-chrome-stable')


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('root', nargs='?', default='.', type=Path)
    p.add_argument('--output', type=Path, default=None)
    p.add_argument('--title')
    p.add_argument('--pdf', action='store_true')
    p.add_argument('--if-applicable', action='store_true',
                   help='exit quietly when the tier has no book, for sweeps and CI')
    a = p.parse_args()
    root = a.root.resolve()
    build(root, (a.output or root / 'dist').resolve(), a.title, a.pdf, a.if_applicable)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
