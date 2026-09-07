#!/usr/bin/env python3
"""Read-only Axelerant documentation audit. No third-party dependencies.

The supported metadata syntax is flat YAML scalars plus JSON-style lists.
Unsupported YAML, duplicate keys and malformed values are errors, not defaults.
"""
from __future__ import annotations
import argparse
import ast
import datetime as dt
import fnmatch
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

RULES = {
    'config', 'ownership', 'readme', 'tree', 'metadata', 'freshness',
    'adr', 'alerts', 'agents', 'paths', 'placeholders', 'register', 'links', 'diagrams',
}
OWNER = re.compile(r'@[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
ADR_NAME = re.compile(r'\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z')
KINDS = {'service','site','library','action','cli','poc','docs'}
METHODS = {
    'tutorial': {'clean-checkout','automated-test'},
    'how-to': {'clean-checkout','automated-test','staging'},
    'reference': {'generated','source-review','automated-test'},
    'explanation': {'source-review'}, 'index': {'link-review'},
    'runbook': {'incident','staging-drill','tabletop'},
}
BUDGETS = {'index':300,'how-to':800,'tutorial':1200,'explanation':1500,'adr':600,'runbook':700}
SKIP = {'.git','node_modules','.venv','__pycache__','.docs-standard','.runtime','.state','.deploy','dist'}
ROOT_MD = {'README.md','AGENTS.md','CLAUDE.md','LICENSE.md','CHANGELOG.md','CONTRIBUTING.md','SECURITY.md'}
SECTIONS = ['Status','Requirements','Quick start','Common commands','How we work here','Ownership']
PLATFORM = {'tutorials','how-to','reference','explanation','adr'}


def scalar_yaml(text: str) -> dict:
    """A strict, documented subset rather than an inaccurate general YAML parser."""
    data = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if line != line.lstrip():
            raise ValueError(f'line {number}: nested YAML is unsupported')
        match = re.fullmatch(r'([a-z_]+):\s*(.*)', line)
        if not match:
            raise ValueError(f'line {number}: expected key: scalar')
        key, value = match.groups()
        if key in data:
            raise ValueError(f'line {number}: duplicate key {key}')
        quote = None
        escape = False
        out = []
        for char in value:
            if escape:
                out.append(char); escape = False; continue
            if char == '\\' and quote == '"':
                out.append(char); escape = True; continue
            if char in "\"'":
                quote = None if quote == char else (char if quote is None else quote)
            if char == '#' and quote is None:
                break
            out.append(char)
        value = ''.join(out).strip()
        if quote:
            raise ValueError(f'line {number}: unclosed quote')
        if value.startswith(('"',"'",'[')):
            try:
                parsed = ast.literal_eval(value)
            except (SyntaxError, ValueError) as exc:
                raise ValueError(f'line {number}: invalid quoted scalar or list') from exc
            if not isinstance(parsed, (str, list)) or isinstance(parsed, list) and not all(isinstance(x, str) for x in parsed):
                raise ValueError(f'line {number}: expected a string or list of strings')
        elif value in ('true','false'):
            parsed = value == 'true'
        elif re.fullmatch(r'-?\d+', value):
            parsed = int(value)
        elif value.startswith(('{','&','*','!','|','>')) or ': ' in value:
            raise ValueError(f'line {number}: unsupported YAML construct; quote literal text')
        else:
            parsed = value
        data[key] = parsed
    return data


def frontmatter(text: str) -> tuple[dict, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != '---':
        raise ValueError('missing frontmatter')
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return scalar_yaml(''.join(lines[1:i])), ''.join(lines[i+1:])
    raise ValueError('unclosed frontmatter')


def fences(text: str):
    """Yield (language, body, first line) for backtick and tilde fences."""
    opening = None
    body = []
    for line_no, line in enumerate(text.splitlines(),1):
        if opening is None:
            m = re.match(r'^\s{0,3}(`{3,}|~{3,})\s*([^\s]*)[^\n]*$', line)
            if m:
                opening = (m.group(1),m.group(2),line_no)
                body = []
        elif re.fullmatch(r'\s{0,3}' + re.escape(opening[0][0]) + '{' + str(len(opening[0])) + r',}\s*',line):
            yield opening[1], '\n'.join(body), opening[2]
            opening = None
        else:
            body.append(line)
    if opening:
        raise ValueError(f'unclosed fence at line {opening[2]}')


def prose(text: str) -> str:
    result = []
    marker = None
    for line in text.splitlines():
        m = re.match(r'^\s{0,3}(`{3,}|~{3,})',line)
        if marker is None and m:
            marker = m.group(1); continue
        if marker is not None:
            if re.fullmatch(r'\s{0,3}' + re.escape(marker[0]) + '{' + str(len(marker)) + r',}\s*', line):
                marker = None
            continue
        result.append(line)
    return re.sub(r'`+[^`\n]*`+', '', '\n'.join(result))


def section(text: str, name: str) -> str:
    m = re.search(r'^## '+re.escape(name)+r'\s*\n(.*?)(?=^## |\Z)',text,re.M|re.S)
    return m.group(1) if m else ''


def local_links(text: str) -> list[str]:
    # Include inline and reference-definition links, not commands in fenced blocks.
    lines = []
    marker = None
    for line in text.splitlines():
        m = re.match(r'^\s{0,3}(`{3,}|~{3,})',line)
        if marker is None and m: marker=m.group(1); continue
        if marker is not None:
            if re.fullmatch(r'\s{0,3}'+re.escape(marker[0])+'{'+str(len(marker))+r',}\s*',line): marker=None
            continue
        lines.append(line)
    text='\n'.join(lines)
    return re.findall(r'\[[^\]]*\]\(([^\s)]+)',text)+re.findall(r'^\s*\[[^\]]+\]:\s*(\S+)',text,re.M)


class Audit:
    def __init__(self, root: Path, today: dt.date | None = None):
        self.root = root.resolve()
        self.today = today or dt.datetime.now(dt.timezone.utc).date()
        self.findings = []
        self.cfg = {}
        self.ignore = {'register':[],'placeholders':[],'links':[]}
        self.pages = {}

    def add(self, rule: str, path: Path | str, message: str, level: str = 'BLOCK'):
        assert rule in RULES
        self.findings.append({'rule':rule,'path':str(path),'message':message,'level':level})

    def files(self):
        # Explicit nested repositories have their own audit; do not count their diagrams twice.
        nested = [p.parent.parent.resolve() for p in self.root.rglob('.axelerant/repo.yml') if p.parent.parent.resolve()!=self.root]
        for p in sorted(self.root.rglob('*.md')):
            if any(x in SKIP for x in p.relative_to(self.root).parts): continue
            if any(p.is_relative_to(n) for n in nested): continue
            if p.is_symlink():
                self.add('paths',p.relative_to(self.root),'Markdown symlinks are unsupported; keep auditable files in this repository'); continue
            yield p

    def ignored(self, rule: str, path: str):
        return any(fnmatch.fnmatchcase(path,pattern) for pattern in self.ignore.get(rule,[]))

    def date(self, value, path, key):
        if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
            self.add('freshness',path,f'{key} must be YYYY-MM-DD'); return None
        try: parsed=dt.date.fromisoformat(value)
        except ValueError:
            self.add('freshness',path,f'{key} is not a calendar date'); return None
        if parsed>self.today: self.add('freshness',path,f'{key} is in the future')
        return parsed

    def config(self):
        p=self.root/'.axelerant/repo.yml'
        try: self.cfg=scalar_yaml(p.read_text())
        except (OSError,ValueError) as e:
            self.add('config','.axelerant/repo.yml',str(e)); return False
        required={'tier','kind','owner','visibility','on_call','docs_review_days'}
        missing=required-set(self.cfg)
        if missing: self.add('config',p.name,'missing '+', '.join(sorted(missing)))
        unknown=set(self.cfg)-required-{'client','alerts_file'}
        if unknown: self.add('config',p.name,'unknown keys '+', '.join(sorted(unknown)))
        # Validate a field only when it is present. A missing field is already
        # reported once above, and adding "invalid" to it doubles every
        # diagnostic an adopting repository sees on its first run.
        has=self.cfg.__contains__
        if has('tier') and (type(self.cfg['tier']) is not int or self.cfg['tier'] not in (0,1,2)): self.add('config',p.name,'tier must be 0, 1 or 2')
        if has('kind') and self.cfg['kind'] not in KINDS: self.add('config',p.name,'invalid kind')
        if has('owner') and not OWNER.fullmatch(str(self.cfg['owner'])): self.add('config',p.name,'owner must be @org/team')
        if has('on_call') and type(self.cfg['on_call']) is not bool: self.add('config',p.name,'on_call must be exactly true or false')
        if has('docs_review_days') and (type(self.cfg['docs_review_days']) is not int or self.cfg['docs_review_days']<1): self.add('config',p.name,'docs_review_days must be a positive integer')
        if has('visibility') and self.cfg['visibility'] not in ('public','internal','client-confidential'): self.add('config',p.name,'invalid visibility')
        if self.cfg.get('visibility')=='client-confidential' and not self.cfg.get('client'): self.add('config',p.name,'client is required')
        if self.cfg.get('on_call') is True and self.cfg.get('tier')!=2: self.add('config',p.name,'on_call: true requires tier: 2')
        if self.cfg.get('on_call') is True and not self.cfg.get('alerts_file'): self.add('alerts',p.name,'on_call: true requires alerts_file')
        for path in (self.root/'.github/CODEOWNERS',self.root/'CODEOWNERS',self.root/'docs/CODEOWNERS'):
            if path.is_file():
                rows=[l.split('#',1)[0].split() for l in path.read_text().splitlines()]
                defaults=[r for r in rows if r and r[0]=='*']
                if not defaults or self.cfg.get('owner') not in defaults[-1][1:]: self.add('ownership',path.relative_to(self.root),'last catch-all rule must include configured owner')
                break
        else: self.add('ownership','CODEOWNERS','missing ownership file')
        ig=self.root/'.axelerant/audit-ignore'
        if ig.exists():
            for n,line in enumerate(ig.read_text().splitlines(),1):
                if not line.strip() or line.lstrip().startswith('#'): continue
                rule,sep,rest=line.partition(' ')
                pattern,reason_sep,reason=rest.partition(' # ')
                if rule not in self.ignore or not sep or not pattern or not reason_sep or not reason.strip():
                    self.add('config','.axelerant/audit-ignore',f'line {n}: expected rule glob # reason'); continue
                self.ignore[rule].append(pattern.strip())
        return not any(f['rule']=='config' for f in self.findings)

    def readme(self):
        p=self.root/'README.md'
        if not p.is_file(): self.add('readme','README.md','missing'); return
        text=p.read_text(); lines=text.splitlines()
        if not lines or not lines[0].startswith('# '): self.add('readme','README.md','must begin with an H1')
        desc=next((l.strip() for l in lines[1:] if l.strip()),'')
        if not desc or desc.startswith('#') or len(desc)>120: self.add('readme','README.md','description must be 1–120 characters below title')
        headings=re.findall(r'^## (.+)$',prose(text),re.M)
        required=SECTIONS+(['Documentation'] if self.cfg['tier'] else [])
        if [h for h in headings if h in required]!=required: self.add('readme','README.md','required sections missing, duplicated or out of order')
        if not re.search(r'\b(active|maintenance|archived|poc)\b',section(text,'Status')): self.add('readme','README.md','invalid status')
        rows=[l for l in section(text,'Common commands').splitlines() if l.strip().startswith('|') and not re.fullmatch(r'[\s|:-]+',l)]
        count=max(0,len(rows)-1)
        if not (3 if self.cfg['tier']==0 else 8)<=count<=15: self.add('readme','README.md',f'invalid common-command count: {count}')
        own=section(text,'Ownership')
        if self.cfg['owner'] not in own: self.add('ownership','README.md','Ownership must include configured team')
        if not re.search(r'escalat|support|issues',own,re.I): self.add('ownership','README.md','support or escalation route missing')
        if self.cfg['visibility']!='public' and not re.search(r'#[a-z0-9_-]+',own): self.add('ownership','README.md','non-public repository needs a channel')
        if self.cfg['tier'] and not 4<=len([x for x in local_links(section(text,'Documentation')) if x.startswith('docs/')])<=8: self.add('readme','README.md','Documentation must have four to eight docs links')
        if len(lines)>400: self.add('readme','README.md','over 400 lines')

    def tree(self):
        docs=self.root/'docs'; tier=self.cfg['tier']
        if tier==0:
            if docs.exists(): self.add('tree','docs','Component must not have docs/')
            return
        if not docs.is_dir(): self.add('tree','docs','missing docs/'); return
        if tier==1:
            expected={'README.md','getting-started.md','architecture.md','operations.md'}
            if (docs/'adr').is_dir():
                records=list((docs/'adr').glob('[0-9][0-9][0-9][0-9]-*.md'))
                if len(records)<2 or not (docs/'adr/README.md').is_file(): self.add('tree','docs/adr','split requires two ADRs and README.md')
            else: expected.add('decisions.md')
            actual={p.name for p in docs.iterdir() if p.is_file()}
            if actual!=expected: self.add('tree','docs',f'Project file set differs: missing {sorted(expected-actual)}, extra {sorted(actual-expected)}')
            if any(p.is_dir() and p.name not in {'assets','adr'} for p in docs.iterdir()): self.add('tree','docs','Project folders may only be adr/ or assets/')
        else:
            required=PLATFORM|({'runbooks'} if self.cfg['on_call'] else set())
            for folder in sorted(required):
                d=docs/folder
                if not (d/'README.md').is_file(): self.add('tree',f'docs/{folder}/README.md','required index')
                if folder!='adr' and not any(p.name!='README.md' for p in d.glob('*.md')): self.add('tree',f'docs/{folder}','requires a substantive page')
            for name in ['README.md','explanation/architecture.md']:
                if not (docs/name).is_file(): self.add('tree',f'docs/{name}','required')
        for d in docs.rglob('*'):
            if d.is_dir() and d.name not in PLATFORM|{'assets','runbooks'} and len(list(d.glob('*.md')))<3:
                self.add('tree',d.relative_to(self.root),'invented folders normally start at three pages','WARN')

    def documents(self):
        terms=Path(__file__).resolve().parent.parent/'references/fluff-terms.txt'
        denied=[l.strip() for l in terms.read_text().splitlines() if l.strip() and not l.startswith('#')] if terms.is_file() else []
        fluff=re.compile(r'\b(?:'+'|'.join(denied)+r')\b',re.I) if denied else None
        for p in self.files():
            rel=p.relative_to(self.root).as_posix(); text=p.read_text(); body=text; meta={}
            if rel.startswith(('docs/','.axelerant/adr/')):
                try: meta,body=frontmatter(text)
                except ValueError as e: self.add('metadata',rel,str(e))
                if meta:
                    typ=meta.get('type'); self.pages[rel]=(meta,body)
                    if typ not in set(METHODS)|{'adr'}: self.add('metadata',rel,'invalid document type')
                    if not isinstance(meta.get('title'),str) or not meta['title']: self.add('metadata',rel,'missing title')
                    if meta.get('owner')!=self.cfg['owner']: self.add('ownership',rel,'document owner must match repository owner')
                    if p.name=='README.md' and typ!='index': self.add('metadata',rel,'directory README must have type: index')
                    folder_types={'tutorials':'tutorial','how-to':'how-to','reference':'reference','explanation':'explanation','runbooks':'runbook','adr':'adr'}
                    if p.name!='README.md' and p.parent.name in folder_types and typ!=folder_types[p.parent.name]: self.add('metadata',rel,'type does not match folder')
                    if typ=='adr': self.adr(rel,meta,body)
                    elif typ in METHODS:
                        when=self.date(meta.get('last_verified'),rel,'last_verified')
                        if meta.get('verification_method') not in METHODS[typ]: self.add('metadata',rel,'invalid or missing verification_method')
                        if when:
                            age=(self.today-when).days; threshold=self.cfg['docs_review_days']
                            if typ=='runbook' and age>180 or typ!='runbook' and self.cfg['tier']==2 and age>threshold*2: self.add('freshness',rel,f'evidence expired ({age} days)')
                            elif typ!='runbook' and age>threshold: self.add('freshness',rel,f'evidence needs review ({age} days)','WARN')
                    if typ in BUDGETS and len(re.findall(r'\b\w+\b',prose(body)))>BUDGETS[typ]: self.add('metadata',rel,'over word budget','WARN')
            if '/' not in rel and p.name not in ROOT_MD: self.add('paths',rel,'unapproved root Markdown')
            if p.name.lower()=='index.md' or p.name in {'DOCUMENTATION_STATUS.md','MASTER_INDEX.md','IMPLEMENTATION_SUMMARY.md','backlog-roadmap.md'} or any(x in {'improvements','roadmap','features'} for x in p.relative_to(self.root).parts): self.add('paths',rel,'prohibited path')
            visible=prose(body)
            if not self.ignored('placeholders',rel) and re.search(r'\b(?:TODO|TBD)\b|<your-|REPLACE_WITH_|coming soon',visible,re.I): self.add('placeholders',rel,'unresolved placeholder')
            if fluff and not self.ignored('register',rel) and fluff.search(visible): self.add('register',rel,'rejected prose register')
            if re.search(r'^#{1,6}\s+[\U0001F300-\U0001FAFF]',visible,re.M): self.add('register',rel,'emoji section marker')
            if not self.ignored('links',rel):
                for href in local_links(body): self.link(p,href)

    def link(self,p,href):
        parsed=urlsplit(href.strip('<>'))
        if parsed.scheme or href.startswith('//'): return
        target=(p.parent/unquote(parsed.path)).resolve() if parsed.path else p
        rel=p.relative_to(self.root)
        if not target.is_relative_to(self.root) or not target.exists(): self.add('links',rel,'missing or outside-repository link: '+href); return
        if parsed.fragment and target.is_file() and target.suffix=='.md':
            anchors=[]; counts={}
            for title in re.findall(r'^#{1,6}\s+(.+?)\s*#*$',prose(target.read_text()),re.M):
                slug=re.sub(r'[^\w\s-]','',title.lower()).replace(' ','-')
                n=counts.get(slug,0); counts[slug]=n+1; anchors.append(slug+(f'-{n}' if n else ''))
            if unquote(parsed.fragment) not in anchors and not re.search(r'(?:id|name)=["\']'+re.escape(parsed.fragment)+r'["\']',target.read_text()): self.add('links',rel,'missing heading anchor: '+href)

    def adr(self,rel,meta,body):
        if not ADR_NAME.fullmatch(Path(rel).name): self.add('adr',rel,'use NNNN-kebab-title.md')
        expected='.axelerant/adr/' if self.cfg['tier']==0 else 'docs/adr/'
        if not rel.startswith(expected): self.add('adr',rel,'incorrect ADR location')
        if not re.fullmatch(r'proposed|accepted|deprecated|superseded by \d{4}',str(meta.get('status',''))): self.add('adr',rel,'invalid status')
        self.date(meta.get('date'),rel,'date')
        if not isinstance(meta.get('deciders'),list) or not meta['deciders']: self.add('adr',rel,'deciders must be a nonempty list')
        if any(k in meta for k in ('last_verified','last_reviewed','verification_method')): self.add('adr',rel,'ADRs are superseded, not refreshed')
        self.ordered(rel,body,['Context and problem statement','Considered options','Decision','Consequences'],'adr')
        if len(re.findall(r'^[-*] ',section(body,'Considered options'),re.M))<2: self.add('adr',rel,'at least two options required')
        if not re.search(r'\b(bad|cost|downside|negative)\b',section(body,'Consequences'),re.I): self.add('adr',rel,'state a downside')

    def ordered(self,rel,body,required,rule):
        actual=re.findall(r'^## (.+)$',prose(body),re.M)
        if [x for x in actual if x in required]!=required: self.add(rule,rel,'missing or misordered sections')

    def alerts(self):
        records=[(p,m,b) for p,(m,b) in self.pages.items() if m.get('type')=='runbook']
        if not self.cfg['on_call'] and not records: return
        source=self.cfg.get('alerts_file','')
        target=(self.root/str(source)).resolve()
        if not source or not target.is_relative_to(self.root) or not target.is_file(): self.add('alerts',str(source),'missing repository alert register'); return
        try:
            alerts=json.loads(target.read_text())
            if not isinstance(alerts,list): raise ValueError('register must be an array')
            if any(not isinstance(a,dict) or not all(isinstance(a.get(k),str) and a[k] for k in ('name','runbook','condition')) for a in alerts): raise ValueError('each alert needs name, runbook, condition')
        except (ValueError,OSError) as e: self.add('alerts',str(source),str(e)); return
        if len({a['name'] for a in alerts})!=len(alerts) or len({a['runbook'] for a in alerts})!=len(alerts): self.add('alerts',str(source),'alert names and runbook destinations must be unique')
        if self.cfg['on_call'] and not alerts: self.add('alerts',str(source),'on-call repository needs at least one alert')
        if {a['runbook'] for a in alerts}!={p for p,_,_ in records}: self.add('alerts',str(source),'alert/runbook linkage is not one-to-one')
        by_path={a['runbook']:a for a in alerts}
        for p,m,b in records:
            a=by_path.get(p)
            self.ordered(p,b,['Trigger','Impact','Diagnose','Mitigate','Escalate','After'],'alerts')
            if a:
                slug=re.sub(r'([a-z0-9])([A-Z])',r'\1-\2',a['name']).lower().replace('_','-')
                if Path(p).stem!=slug or m.get('alert')!=a['name'] or m.get('alert_source')!=source: self.add('alerts',p,'alert identity, filename or source mismatch')
                if a['name'] not in section(b,'Trigger') or a['condition'] not in section(b,'Trigger'): self.add('alerts',p,'Trigger must include register name and condition')

    def agents(self):
        p=self.root/'AGENTS.md'
        if not p.is_file(): self.add('agents','AGENTS.md','missing')
        else:
            text=p.read_text()
            if len(text.splitlines())>200: self.add('agents','AGENTS.md','over 200 lines')
            if not re.search(r'\|\s*Surface\s*\|\s*Audience\s*\|',text): self.add('agents','AGENTS.md','surface/audience table missing')
            self.ordered('AGENTS.md',text,['Hard rules','Before claiming done','Where to look'],'agents')
            done=section(text,'Before claiming done')
            if not done.strip() or not re.search(r'docs_audit|docs-check|make verify',done): self.add('agents','AGENTS.md','documentation verification command missing')
            jump=section(text,'Where to look')
            refs=re.findall(r'`([^`\n]+\.md)`',jump)+local_links(jump)
            if self.cfg['tier'] and not any('docs/' in r for r in refs): self.add('agents','AGENTS.md','missing documentation jump table')
            for ref in refs: self.link(p,ref)
        c=self.root/'CLAUDE.md'
        if not c.is_file() or c.read_text().strip()!='@AGENTS.md': self.add('agents','CLAUDE.md','must contain exactly @AGENTS.md')

    def diagrams(self):
        counts={'C4Context':0,'C4Container':0}
        for p in self.files():
            try:
                for lang,body,line in fences(p.read_text()):
                    if lang!='mermaid': continue
                    substantive=[l.strip() for l in body.splitlines() if l.strip() and not l.strip().startswith('%%')]
                    if not substantive: self.add('diagrams',p.relative_to(self.root),'empty Mermaid block'); continue
                    kind=substantive[0].split()[0]
                    if p.is_relative_to(self.root/'docs') and kind in counts: counts[kind]+=1
                    if kind=='C4Component': self.add('diagrams',p.relative_to(self.root),'C4 level three is prohibited')
            except ValueError as e: self.add('diagrams',p.relative_to(self.root),str(e))
        if self.cfg['tier']>0 and counts['C4Context']!=1: self.add('diagrams','docs',f'exactly one C4Context required; found {counts["C4Context"]}')
        if self.cfg['tier']==2 and counts['C4Container']!=1: self.add('diagrams','docs',f'exactly one C4Container required; found {counts["C4Container"]}')
        # Do not pretend a heuristic is a parser. CI renders all Mermaid blocks.

    def run(self):
        if not self.config(): return self.findings
        self.readme(); self.tree(); self.documents(); self.alerts(); self.agents(); self.diagrams()
        decisions=[(path,meta,body) for path,(meta,body) in self.pages.items() if meta.get('type')=='adr']
        numbers=[Path(path).name[:4] for path,_,_ in decisions]
        if len(numbers)!=len(set(numbers)): self.add('adr','adr/','duplicate ADR numbers')
        for path,meta,body in decisions:
            match=re.fullmatch(r'superseded by (\d{4})',str(meta.get('status','')))
            if match:
                targets=[p for p,_,_ in decisions if Path(p).name.startswith(match[1]+'-')]
                if len(targets)!=1 or Path(targets[0]).name not in body:
                    self.add('adr',path,'superseded record must link to its unique replacement')
        return self.findings


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('root',nargs='?',default='.')
    parser.add_argument('--strict',action='store_true')
    parser.add_argument('--json',action='store_true')
    parser.add_argument('--today',type=dt.date.fromisoformat)
    args=parser.parse_args()
    audit=Audit(Path(args.root),args.today); results=audit.run()
    if args.json: print(json.dumps(results,indent=2))
    else:
        print(f'docs-audit: {len([x for x in results if x["level"]=="BLOCK"])} block, {len([x for x in results if x["level"]=="WARN"])} warn')
        for item in results: print('{level} [{rule}] {path}: {message}'.format(**item))
    return int(args.strict and any(x['level']=='BLOCK' for x in results))

if __name__=='__main__': raise SystemExit(main())
