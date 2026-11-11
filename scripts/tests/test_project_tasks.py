import importlib.util
import sys
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[2]
STAGE=BASE
sys.path.insert(0,str(BASE/"scripts"))
spec=importlib.util.spec_from_file_location('project_tasks',STAGE/'scripts/project-tasks.py')
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)

class Tasks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='para-task-tests-')
        self.root=Path(self.temp.name).resolve()
        for rel in ('templates/project-note.md','templates/project-readme.md'):
            p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(STAGE/rel,p)
        (self.root/'01-projects').mkdir()
        (self.root/'Home.md').write_text('# Home\n\n## Status\n\n- **Projects:** No active projects.\n- **Areas:** KEEP THIS\n<!-- generated boundary -->\n\n## Topics\n\nKeep these links.\n')
        (self.root/'03-resources').mkdir()
        (self.root/'03-resources/vault-log.md').write_text('# Activity\n')
        self.store=app.Store(self.root)
    def tearDown(self):
        self.temp.cleanup()
    def create(self):
        return self.store.apply({'name':'Task test','goal':'A tested form works','started':'2026-11-10','due':'2026-12-01','date_type':'target','tasks':['Implement form error handling','Verify the invalid-input error appears']},create=True)['project']
    def update(self, p, states, **kw):
        return self.store.apply({'path':p['path'],'version':p['version'],'states':states,**kw})['project']
    def test_create_uses_template_and_actual_actions(self):
        p=self.create();self.assertEqual(p['status'],'active');self.assertEqual(len(p['tasks']),2)
        text=(self.root/p['path']).read_text();self.assertNotIn('<date>',text);self.assertIn('goal: "A tested form works"',text)
        self.assertIn('**Librarian review:** pending',text);self.assertIn('## Next steps',text)
        self.assertEqual(p['goal'],'A tested form works')
    def test_checked_task_updates_records_preserving_home(self):
        p=self.create();p=self.update(p,{'t1':True,'t2':False})
        self.assertIn('1/2',p['summary']);home=(self.root/'Home.md').read_text()
        self.assertIn('KEEP THIS',home);self.assertIn('generated boundary',home);self.assertIn('Keep these links.',home)
        self.assertIn('Task test',home);self.assertIn('project tasks updated',(self.root/'03-resources/vault-log.md').read_text())
    def test_all_done_requires_finish_line_confirmation_and_reopens(self):
        p=self.create();p=self.update(p,{'t1':True,'t2':True});self.assertEqual(p['status'],'ready-for-review')
        p=self.update(p,{'t1':True,'t2':True},confirmed=True);self.assertEqual(p['status'],'done')
        p=self.update(p,{'t1':True,'t2':False},confirmed=True);self.assertEqual(p['status'],'active');self.assertFalse(p['confirmed'])
    def test_same_update_does_not_duplicate_activity(self):
        p=self.create();log=(self.root/'03-resources/vault-log.md').read_text()
        self.update(p,{'t1':False,'t2':False});self.assertEqual((self.root/'03-resources/vault-log.md').read_text(),log)
    def test_stale_project_conflict_preserves_new_edit(self):
        p=self.create();path=self.root/p['path'];path.write_text(path.read_text()+'\nManual change\n')
        with self.assertRaises(app.Conflict):self.update(p,{'t1':True,'t2':False})
        self.assertTrue(path.read_text().endswith('Manual change\n'))
    def test_dependencies_validation_and_next_actions(self):
        p=self.create();path=self.root/p['path'];path.write_text(path.read_text().replace('task:t2 -->','task:t2 after:t1 -->'))
        p=self.store.view(path)
        with self.assertRaises(ValueError):self.update(p,{'t1':False,'t2':True})
        p=self.update(p,{'t1':True,'t2':False});self.assertIn('Verify the invalid-input',p['summary'])
    def test_cycle_and_missing_dependency_rejected(self):
        text='\n'.join([app.TASK_START,'- [ ] A <!-- task:a after:b -->','- [ ] B <!-- task:b after:a -->',app.TASK_END])
        with self.assertRaisesRegex(ValueError,'cycle'):app.read_tasks(text)
        with self.assertRaisesRegex(ValueError,'does not exist'):app.read_tasks(text.replace('task:b after:a','task:b after:missing'))
    def test_200_task_dag_is_linear_and_accepted(self):
        rows=[]
        for i in range(200):
            deps=' after:'+','.join('t'+str(d) for d in (i-1,i-2) if d>=0) if i else ''
            rows.append(f'- [ ] Task {i} <!-- task:t{i}{deps} -->')
        start=time.monotonic();parsed=app.read_tasks(app.TASK_START+'\n'+'\n'.join(rows)+'\n'+app.TASK_END)
        self.assertEqual(len(parsed),200);self.assertLess(time.monotonic()-start,1)
    def test_add_action_reopens_completed_project(self):
        p=self.create();p=self.update(p,{'t1':True,'t2':True},confirmed=True)
        p=self.update(p,{'t1':True,'t2':True},confirmed=True,new_tasks=['Test keyboard submission'])
        self.assertEqual(p['status'],'active');self.assertEqual(len(p['tasks']),3);self.assertFalse(p['confirmed'])
    def test_markdown_edits_refresh_stale_summary(self):
        p=self.create();path=self.root/p['path'];path.write_text(path.read_text().replace('- [ ] Implement','- [x] Implement'))
        p=self.store.view(path);p=self.update(p,{'t1':True,'t2':False});self.assertIn('1/2 tasks',p['summary'])
    def test_promoted_readme_preserves_user_content(self):
        folder=self.root/'01-projects/promoted';folder.mkdir();path=folder/'README.md'
        text=(STAGE/'templates/project-readme.md').read_text().replace('<Project Name>','Promoted').replace('<what "done" looks like>','A verified deliverable').replace('<start date>','2026-11-10').replace('<end date>','2026-11-10').replace('<end date type>','target').replace('<Skills selected from the actual project brief, with reasons and invocation stages>','Librarian only for now.').replace('<Verb + specific deliverable + observable completion check>','Verify a concrete artifact')+'\n## Manual notes\nKEEP\n'
        path.write_text(text);p=self.store.view(path);p=self.update(p,{'t1':True})
        saved=path.read_text();self.assertIn('**Due:** 2026-11-10',saved);self.assertIn('## Next steps\t',saved);self.assertIn('KEEP',saved)
        self.assertIn('**Status:** ready-for-review',saved)
    def test_nested_repo_and_archive_are_not_writable(self):
        p=self.create();folder=self.root/'01-projects/implementation';folder.mkdir();(folder/'.git').mkdir();(folder/'README.md').write_text((self.root/p['path']).read_text())
        self.assertNotIn(folder/'README.md',self.store.candidates())
        with self.assertRaises(ValueError):self.store.apply({'path':'04-archive/anything.md'})
        with self.assertRaises(ValueError):self.store.apply({'path':'../../elsewhere.md'})
    def test_mid_write_failure_rolls_back_all_notes(self):
        p=self.create();paths=[self.root/p['path'],self.root/'Home.md',self.root/'03-resources/vault-log.md'];before={f:f.read_text() for f in paths}
        actual=self.store.atomic;calls=[]
        def fail_third(path,text,create=False):
            calls.append(path)
            if len(calls)==3:raise OSError('fixture failure')
            return actual(path,text,create)
        with patch.object(self.store,'atomic',side_effect=fail_third):
            with self.assertRaises(OSError):self.update(p,{'t1':True,'t2':False})
        self.assertEqual(before,{f:f.read_text() for f in paths})
        self.assertFalse(list((self.root/'logs/project-tasks').glob('*.pending.json')))
    def test_prepared_home_conflict_cannot_overwrite_external_edit(self):
        p=self.create();actual=self.store.publish
        def concurrent(changes,expected):
            home=self.root/'Home.md';home.write_text(home.read_text()+'\nExternal note\n')
            return actual(changes,expected)
        with patch.object(self.store,'publish',side_effect=concurrent):
            with self.assertRaises(app.Conflict):self.update(p,{'t1':True,'t2':False})
        self.assertIn('External note',(self.root/'Home.md').read_text())
        self.assertFalse(self.store.view(self.root/p['path'])['tasks'][0]['done'])
    def test_pending_crash_journal_blocks_writes(self):
        p=self.create();folder=self.root/'logs/project-tasks';(folder/'crash.pending.json').write_text('[]')
        with self.assertRaises(app.Conflict):self.update(p,{'t1':True,'t2':False})
    def test_duplicate_project_create_preserves_existing(self):
        p=self.create();before=(self.root/p['path']).read_text()
        with self.assertRaises(app.Conflict):self.create()
        self.assertEqual(before,(self.root/p['path']).read_text())
    def test_unmanaged_project_is_read_only(self):
        path=self.root/'01-projects/old.md';path.write_text('---\nstatus: active\n---\n# Old\nManual task list\n')
        self.assertIsNotNone(self.store.view(path)['error'])
        self.assertEqual(self.store.view(path)['status'],'active')
        self.create();self.assertIn('[Old](01-projects/old.md) — active',(self.root/'Home.md').read_text())
    def test_custom_template_sections_survive_creation(self):
        path=self.root/'templates/project-note.md';path.write_text(path.read_text()+'\n## Custom context\nKEEP THIS TOO\n')
        p=self.create();self.assertIn('KEEP THIS TOO',(self.root/p['path']).read_text())
    def test_nested_blocks_rejected_without_touching_task_text(self):
        p=self.create();path=self.root/p['path'];text=path.read_text()
        state=app.block(text,app.STATE_START,app.STATE_END)
        text=text.replace(app.STATE_START+state+app.STATE_END,'')
        text=text.replace(app.TASK_START,app.STATE_START+'\n'+app.TASK_START).replace(app.TASK_END,app.TASK_END+'\n'+app.STATE_END)
        path.write_text(text);p=self.store.view(path);self.assertIn('separate',p['error'])
        with self.assertRaises(ValueError):self.update(p,{'t1':True,'t2':False})
        self.assertEqual(path.read_text(),text)
    def test_reconciled_review_survives_unchanged_save(self):
        p=self.create();path=self.root/p['path'];path.write_text(path.read_text().replace('**Librarian review:** pending — reconcile changed task outcomes and any linked-project or specialist follow-up.','**Librarian review:** reconciled — 2026-11-10; checked.'))
        p=self.store.view(path);before=path.read_text();log=(self.root/'03-resources/vault-log.md').read_text()
        self.update(p,{'t1':False,'t2':False});self.assertEqual(before,path.read_text());self.assertEqual(log,(self.root/'03-resources/vault-log.md').read_text())
    def test_journal_symlink_cannot_write_outside_vault(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root/'logs').symlink_to(outside,target_is_directory=True)
            with self.assertRaises(ValueError):self.create()
            self.assertFalse(list(Path(outside).iterdir()))
    def test_literal_angles_in_user_text_are_preserved(self):
        p=self.store.apply({'name':'Check <date> rendering','goal':'Confirm x < y and z > w','started':'2026-11-10','due':'undecided','date_type':'undecided','tasks':['Test the <button> keyboard interaction']},create=True)['project']
        self.assertEqual(p['name'],'Check <date> rendering');self.assertEqual(p['goal'],'Confirm x < y and z > w');self.assertIn('<button>',p['tasks'][0]['title'])
    def test_lock_leaf_symlink_cannot_create_outside_file(self):
        with tempfile.TemporaryDirectory() as outside:
            folder=self.root/'logs';folder.mkdir(parents=True)
            target=Path(outside)/'must-not-exist'
            (folder/'vault-write.lock').symlink_to(target)
            with self.assertRaises(ValueError):self.create()
            self.assertFalse(target.exists())
    def test_existing_special_filename_has_valid_home_link(self):
        path=self.root/'01-projects/plan #1?.md';path.write_text('---\nstatus: active\n---\n# Existing plan\n')
        self.create();self.assertIn('01-projects/plan%20%231%3F.md',(self.root/'Home.md').read_text())

    def test_home_keeps_mixed_roots_and_folders_without_readme(self):
        missing=self.root/'01-projects/no-summary';missing.mkdir()
        mixed=self.root/'01-projects/mixed-root';mixed.mkdir();(mixed/'.git').mkdir()
        (mixed/'README.md').write_text('# Independent project\n\n**Status:** active\n')
        self.create();home=(self.root/'Home.md').read_text()
        self.assertIn('[no-summary](01-projects/no-summary/) — unknown',home)
        self.assertIn('[Independent project](01-projects/mixed-root/README.md) — active',home)
        self.assertNotIn(mixed/'README.md',self.store.candidates())
    def test_dates_are_required_and_not_inferred(self):
        payload={'name':'Missing dates','goal':'A tested artifact','tasks':['Verify the artifact']}
        with self.assertRaisesRegex(ValueError,'start date'):self.store.apply(payload,create=True)
        self.assertEqual(self.store.listing(),[])
    def test_explicit_unknown_dates_are_saved(self):
        p=self.store.apply({'name':'Undecided schedule','goal':'A verified artifact','started':'undecided','due':'undecided','date_type':'undecided','tasks':['Verify the artifact']},create=True)['project']
        self.assertEqual(p['started'],'undecided');self.assertEqual(p['due'],'undecided');self.assertEqual(p['date_type'],'undecided')
    def test_start_and_target_dates_persist_through_update(self):
        p=self.create();p=self.update(p,{'t1':True,'t2':False})
        self.assertEqual(p['started'],'2026-11-10');self.assertEqual(p['due'],'2026-12-01');self.assertEqual(p['date_type'],'target')
    def test_invalid_timeline_is_rejected(self):
        for fields in ({'started':'2026-11-20','due':'2026-11-01','date_type':'deadline'}, {'started':'2026-02-30','due':'undecided','date_type':'undecided'}, {'started':'2026-11-10','due':'undecided','date_type':'target'}):
            with self.assertRaises(ValueError):app.intake_dates(fields)
    def test_skill_recommendations_use_relevant_roles(self):
        rows=app.recommend_skills({'goal':'Fix a software authentication bug','tasks':['Test the API response']})
        self.assertEqual([r['id'] for r in rows],['dev'])
        rows=app.recommend_skills({'goal':'Write a weekly newsletter','tasks':['Draft the first issue']})
        self.assertEqual({r['id'] for r in rows},{'content-strategist','copywriter','editor'})
    def test_no_specialist_is_a_valid_intake(self):
        self.assertEqual(app.recommend_skills({'goal':'Organize the garage','tasks':['Sort the spare parts']}),[])
    def test_saved_skill_plan_has_reasons_and_survives_tasks(self):
        p=self.create();note=(self.root/p['path']).read_text()
        self.assertIn('[[skills/dev/SKILL|Dev]]',note);self.assertIn('Invoke:',note)
        plan=app.block(note,app.SKILL_START,app.SKILL_END)
        p=self.update(p,{'t1':True,'t2':False})
        self.assertEqual(app.block((self.root/p['path']).read_text(),app.SKILL_START,app.SKILL_END),plan)
        self.assertIn('Dev',[r['name'] for r in p['skills']])

if __name__=='__main__':
    unittest.main(verbosity=2)
