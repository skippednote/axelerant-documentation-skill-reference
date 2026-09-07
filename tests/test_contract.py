"""Regression fixtures for every declared machine rule, plus parser edge cases."""
import datetime as dt
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/axelerant-engineering-documentation/scripts'
sys.path.insert(0,str(SCRIPTS))
from docs_audit import Audit, RULES, scalar_yaml, fences
from verify_isolated import build_command
TODAY=dt.date(2026,9,3)


def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)


class RuleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'fixture'
        shutil.copytree(ROOT/'sample/dispatch',self.root,ignore=shutil.ignore_patterns('__pycache__','.state','dist'))
    def audit(self): return Audit(self.root,TODAY).run()
    def assert_rule(self,rule):
        results=self.audit()
        self.assertTrue(any(r['rule']==rule and r['level']=='BLOCK' for r in results),results)
    def replace(self,path,old,new):
        file=self.root/path; text=file.read_text();self.assertIn(old,text);file.write_text(text.replace(old,new))
    def test_valid_platform(self): self.assertEqual(self.audit(),[])
    def test_config(self):
        self.replace('.axelerant/repo.yml','on_call: true','on_call: tru');self.assert_rule('config')
    def test_ownership(self):
        write(self.root/'.github/CODEOWNERS','* @wrong/owner\n');self.assert_rule('ownership')
    def test_readme(self):
        self.replace('README.md','## Quick start','## Renamed');self.assert_rule('readme')
    def test_tree(self):
        (self.root/'docs/tutorials/README.md').unlink();self.assert_rule('tree')
    def test_metadata(self):
        self.replace('docs/how-to/run-locally.md','verification_method: automated-test','verification_method: edited');self.assert_rule('metadata')
    def test_freshness(self):
        self.replace('docs/how-to/run-locally.md','2026-09-03','2026-09-04');self.assert_rule('freshness')
    def test_adr(self):
        self.replace('docs/adr/0003-executable-local-example.md','## Decision','## Selected');self.assert_rule('adr')
    def test_alerts(self):
        p=self.root/'alerts/alerts.json';data=json.loads(p.read_text());data.pop();p.write_text(json.dumps(data));self.assert_rule('alerts')
    def test_agents(self):
        write(self.root/'CLAUDE.md','Duplicated instructions\n');self.assert_rule('agents')
    def test_paths(self):
        write(self.root/'MASTER_INDEX.md','# Not allowed\n');self.assert_rule('paths')
    def test_placeholders(self):
        p=self.root/'docs/reference/api.md';p.write_text(p.read_text()+'\nTODO\n');self.assert_rule('placeholders')
    def test_register(self):
        p=self.root/'docs/reference/api.md';p.write_text(p.read_text()+'\nThis is robust.\n');self.assert_rule('register')
    def test_links(self):
        p=self.root/'docs/README.md';p.write_text(p.read_text()+'\n[Missing](missing.md)\n');self.assert_rule('links')
    def test_diagrams(self):
        self.replace('docs/explanation/architecture.md','C4Context','flowchart LR');self.assert_rule('diagrams')
    def test_duplicate_adr_number(self):
        src=self.root/'docs/adr/0003-executable-local-example.md'
        shutil.copyfile(src,self.root/'docs/adr/0003-duplicate.md')
        self.assert_rule('adr')
    def test_supersession_target_must_exist(self):
        self.replace('docs/adr/0001-sqs-over-kafka.md','superseded by 0003','superseded by 0099')
        self.assert_rule('adr')
    def test_invalid_calendar_date_does_not_crash(self):
        self.replace('docs/reference/api.md','2026-09-03','2026-13-40');self.assert_rule('freshness')
    def test_stale_runbook(self):
        self.replace('docs/runbooks/provider-error-rate-high.md','2026-09-03','2026-01-01');self.assert_rule('freshness')
    def test_placeholder_ignore_cannot_skip_metadata(self):
        write(self.root/'.axelerant/audit-ignore','placeholders docs/reference/* # template specimen\n')
        self.replace('docs/reference/api.md','verification_method: source-review','verification_method: invalid');self.assert_rule('metadata')
    def test_unscoped_ignore_rejected(self):
        write(self.root/'.axelerant/audit-ignore','docs/**\n');self.assert_rule('config')
    def test_missing_heading_anchor(self):
        p=self.root/'docs/README.md';p.write_text(p.read_text()+'\n[Wrong](reference/api.md#missing-heading)\n');self.assert_rule('links')
    def test_fenced_placeholder_is_not_prose(self):
        p=self.root/'docs/reference/api.md';p.write_text(p.read_text()+'\n~~~text\nTODO <your-domain> robust\n~~~\n');self.assertEqual(self.audit(),[])
    def test_no_diagram_false_positive_from_flowchart_end(self):
        p=self.root/'docs/explanation/architecture.md';p.write_text(p.read_text()+'\n```mermaid\nflowchart LR\n  subgraph worker\n    a-->b\n  end\n```\n');self.assertEqual(self.audit(),[])
    def test_readme_heading_in_code_is_not_section(self):
        self.replace('README.md','## Quick start','```markdown\n## Quick start\n```');self.assert_rule('readme')


class ParserTests(unittest.TestCase):
    def test_literal_types(self):
        self.assertEqual(scalar_yaml('tier: 2\non_call: false\nowner: "@org/team"'),{'tier':2,'on_call':False,'owner':'@org/team'})
    def test_hash_in_quoted_string(self):
        self.assertEqual(scalar_yaml('title: "Run #1" # comment')['title'],'Run #1')
    def test_duplicates(self):
        with self.assertRaises(ValueError): scalar_yaml('tier: 1\ntier: 2')
    def test_nested_yaml_rejected(self):
        with self.assertRaises(ValueError): scalar_yaml('settings:\n  unsafe: true')
    def test_malformed_quote(self):
        with self.assertRaises(ValueError): scalar_yaml('owner: "@org/team')
    def test_arrays(self):
        self.assertEqual(scalar_yaml('deciders: ["@org/team", "@person"]')['deciders'],['@org/team','@person'])
    def test_fences(self):
        self.assertEqual(list(fences('~~~mermaid\nflowchart LR\n a-->b\n~~~'))[0][0],'mermaid')
    def test_unclosed_fence(self):
        with self.assertRaises(ValueError): list(fences('```mermaid\nflowchart LR'))
    def test_isolation_arguments(self):
        args=build_command('sha256:'+'0'*64)
        for flag in ('--network=none','--read-only','--cap-drop=ALL','--pull=never','--user=65534:65534'):
            self.assertIn(flag,args)
        self.assertFalse(any('volume' in x or x=='-v' or '--mount' in x for x in args))
    def test_without_execute_only_plans(self):
        r=subprocess.run([sys.executable,str(SCRIPTS/'verify_isolated.py'),'.','--command','echo hello'],capture_output=True,text=True)
        self.assertEqual(r.returncode,0);self.assertIn('PLAN ONLY',r.stdout)
    def test_rules_have_negative_fixtures(self):
        for rule in RULES:self.assertTrue(hasattr(RuleTests,'test_'+rule),rule)


class TierTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        # The actual root is the positive Component fixture.
        for name in ('README.md','AGENTS.md','CLAUDE.md','.axelerant/repo.yml','.github/CODEOWNERS'):
            source=ROOT/name;dest=self.root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    def test_component_rejects_docs(self):
        (self.root/'docs').mkdir();self.assertTrue(any(f['rule']=='tree' for f in Audit(self.root,TODAY).run()))
    def test_boolean_tier_is_invalid(self):
        p=self.root/'.axelerant/repo.yml';p.write_text(p.read_text().replace('tier: 0','tier: true'))
        self.assertTrue(any(f['rule']=='config' for f in Audit(self.root,TODAY).run()))
    def test_quoted_false_is_invalid(self):
        p=self.root/'.axelerant/repo.yml';p.write_text(p.read_text().replace('on_call: false','on_call: "false"'))
        self.assertTrue(any(f['rule']=='config' for f in Audit(self.root,TODAY).run()))
    def test_project_extra_file(self):
        p=self.root/'.axelerant/repo.yml';p.write_text(p.read_text().replace('tier: 0','tier: 1'))
        for name in ('README','getting-started','architecture','operations','decisions','extra'):
            write(self.root/f'docs/{name}.md','# Temporary fixture\n')
        self.assertTrue(any(f['rule']=='tree' and 'extra' in f['message'] for f in Audit(self.root,TODAY).run()))

if __name__=='__main__': unittest.main()
