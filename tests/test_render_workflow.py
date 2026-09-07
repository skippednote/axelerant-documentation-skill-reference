"""The template adopters copy must be exactly what the renderer produces."""
from pathlib import Path
import re
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/'skills/axelerant-engineering-documentation/references/templates/docs-workflow.yml'

class TemplateMatchesRenderer(unittest.TestCase):
    def test_committed_template_is_renderer_output(self):
        # Adopters copy the template; automation runs the renderer. Drift means
        # half the repositories get a file nobody reviewed.
        template=TEMPLATE.read_text()
        pins=set(re.findall(r'@([0-9a-f]{40})',template))
        self.assertEqual(len(pins),1,f'template should pin one commit, pins {sorted(pins)}')
        rendered=subprocess.check_output(
            [sys.executable,str(ROOT/'scripts/render_workflow.py'),pins.pop()],text=True)
        self.assertEqual(rendered,template)

    def test_pinned_commit_is_on_a_branch(self):
        # A squash merge leaves the commit a template was generated against
        # reachable from nothing. Actions still resolves it for a while, so the
        # breakage surfaces long after the merge that caused it.
        pin=re.search(r'@([0-9a-f]{40})',TEMPLATE.read_text()).group(1)
        branches=subprocess.run(['git','-C',str(ROOT),'branch','--contains',pin,'--format=%(refname:short)'],
                                capture_output=True,text=True)
        if branches.returncode:
            self.skipTest('commit not present in this checkout')
        self.assertTrue(branches.stdout.split(),f'{pin[:12]} is on no branch')

if __name__=='__main__': unittest.main()
