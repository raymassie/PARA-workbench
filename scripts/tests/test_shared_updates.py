from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from vault_lock import vault_write_lock
spec=importlib.util.spec_from_file_location('project_tasks_shared_test',ROOT/'scripts/project-tasks.py')
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)

class SharedUpdates(unittest.TestCase):
    def test_shared_lock_serializes_another_writer(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();marker=root/'child-wrote'
            code='''import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from vault_lock import vault_write_lock
print('ready',flush=True)
with vault_write_lock(Path(sys.argv[2])):
    Path(sys.argv[3]).write_text('done')
'''
            with vault_write_lock(root):
                proc=subprocess.Popen([sys.executable,'-c',code,str(ROOT/'scripts'),str(root),str(marker)],stdout=subprocess.PIPE,text=True)
                self.assertEqual(proc.stdout.readline().strip(),'ready')
                self.assertFalse(marker.exists())
            proc.communicate(timeout=5)
            self.assertEqual(proc.returncode,0);self.assertEqual(marker.read_text(),'done')

    def test_report_and_task_activity_both_survive_overlapping_updates(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve()
            for rel in ('scripts/run-report.py','scripts/vault_lock.py','templates/project-note.md'):
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
            (root/'01-projects').mkdir();(root/'03-resources').mkdir()
            (root/'Home.md').write_text('# Home\n\n## Status\n- **Projects:** No active projects.\n\n## Topics\n')
            activity=root/'03-resources/vault-log.md';activity.write_text('# Activity\n')
            store=app.Store(root)
            p=store.apply({'name':'Concurrent work','goal':'A checked artifact','started':'undecided','due':'undecided','date_type':'undecided','tasks':['Check the artifact']},create=True)['project']
            ready,finish=root/'ready',root/'finish'
            helper=root/'assistant-fixture'
            helper.write_text('''#!/usr/bin/env python3
from pathlib import Path
import sys,time
sys.stdin.read()
Path('ready').touch()
end=time.monotonic()+5
while not Path('finish').exists():
    if time.monotonic()>end:sys.exit(9)
    time.sleep(.01)
print('---\\ncreated: 2026-11-10\\ntags: [test]\\nsources: []\\n---\\n# Report fixture\\nNo live model call.')
''')
            helper.chmod(0o755)
            proc=subprocess.Popen([sys.executable,str(root/'scripts/run-report.py'),'nightly-lint','--command',str(helper)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            end=time.monotonic()+5
            while not ready.exists():
                self.assertIsNone(proc.poll());self.assertLess(time.monotonic(),end);time.sleep(.01)
            original=store.publish
            def interleaved(changes,expected):
                finish.touch();time.sleep(.1)
                return original(changes,expected)
            with patch.object(store,'publish',side_effect=interleaved):
                store.apply({'path':p['path'],'version':p['version'],'states':{'t1':True}})
            stdout,stderr=proc.communicate(timeout=5)
            self.assertEqual(proc.returncode,0,stderr)
            saved=activity.read_text()
            self.assertIn('project tasks updated',saved);self.assertIn('nightly-lint report saved',saved)

if __name__=='__main__':unittest.main(verbosity=2)
