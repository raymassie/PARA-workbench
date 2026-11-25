import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'project-review.py'
spec = importlib.util.spec_from_file_location('project_review', SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ProjectReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '01-projects').mkdir()
        self.project = self.root / '01-projects/test.md'
        (self.root / 'source.txt').write_text('approved input')
        (self.root / 'output.txt').write_text('implemented output')
        self.tasks = [{'id': 'build', 'title': 'Build artifact', 'after': [], 'done': True},
                      {'id': 'test', 'title': 'Test artifact', 'after': ['build'], 'done': False},
                      {'id': 'other', 'title': 'Independent task', 'after': [], 'done': False}]
        self.meta = {'schema_version': 1, 'approval_reference': 'User approved local fixture work',
                     'authorized_tasks': [t['id'] for t in self.tasks],
                     'permission_scope': {t['id']: ['local fixture only; no publication'] for t in self.tasks},
                     'tasks': {'build': self.receipt(self.tasks[0])}}
        self.save()

    def receipt(self, task):
        binding = {'definition_sha256': review.fingerprint(task),
                   'inputs': {'source.txt': hashlib.sha256((self.root / 'source.txt').read_bytes()).hexdigest()},
                   'outputs': {'output.txt': hashlib.sha256((self.root / 'output.txt').read_bytes()).hexdigest()}}
        result = copy.deepcopy(binding)
        for role in review.ROLES:
            result[role] = dict(copy.deepcopy(binding), actor=role, verdict='PASS',
                                checks=['Inspected actual artifact against fixture request'],
                                evidence=['Fixture output.txt bytes and meaningful fixture check'], confirmed_output=True)
        return result

    def save(self, finish=False):
        text = '---\nstatus: active\n---\n# Test\n<!-- para-tasks:start -->\n'
        for t in self.tasks:
            deps = ' after:' + ','.join(t['after']) if t['after'] else ''
            text += '- [' + ('x' if t['done'] else ' ') + '] ' + t['title'] + ' <!-- task:' + t['id'] + deps + ' -->\n'
        text += '<!-- para-tasks:end -->\n<!-- para-project-state:start -->\n**Finish line confirmed:** '
        text += ('yes' if finish else 'no') + '\n<!-- para-project-state:end -->\n'
        if self.meta is not None:
            text += '<!-- para-review:start -->\n```json\n' + json.dumps(self.meta) + '\n```\n<!-- para-review:end -->\n'
        self.project.write_text(text)

    def result(self):
        return review.evaluate(self.root, '01-projects/test.md')

    def rows(self):
        return {r['id']: r for r in self.result()['tasks']}

    def test_acceptance_and_independent_continuation(self):
        rows = self.rows()
        self.assertTrue(rows['build']['accepted'])
        self.assertEqual(rows['test']['action'], 'execute')
        self.assertEqual(rows['other']['action'], 'execute')
        self.assertFalse(self.result()['stop_allowed'])

    def test_changed_input_invalidates_acceptance_and_dependent_not_neighbor(self):
        self.tasks[2]['done'] = True
        self.meta['tasks']['other'] = self.receipt(self.tasks[2])
        # Independent neighbor consumes a different unchanged input/output.
        (self.root / 'neighbor.txt').write_text('accepted neighbor')
        neighbor = self.meta['tasks']['other']
        for container in (neighbor, *(neighbor[r] for r in review.ROLES)):
            container['inputs'] = {}
            container['outputs'] = {'neighbor.txt': hashlib.sha256(b'accepted neighbor').hexdigest()}
        self.save()
        self.assertTrue(self.rows()['build']['accepted'])
        (self.root / 'source.txt').write_text('new input, same output')
        rows = self.rows()
        self.assertEqual(rows['build']['action'], 'repair')
        self.assertEqual(rows['test']['action'], 'wait_for_dependencies')
        self.assertTrue(rows['other']['accepted'])

    def test_changed_output_and_definition_invalidate(self):
        (self.root / 'output.txt').write_text('unreviewed edit')
        self.assertEqual(self.rows()['build']['action'], 'repair')
        (self.root / 'output.txt').write_text('implemented output')
        self.tasks[0]['title'] = 'Build different artifact'
        self.save()
        self.assertIn('changed task definition', self.rows()['build']['issues'])

    def test_all_three_gates_and_independence(self):
        receipt = self.meta['tasks']['build']
        for role in review.ROLES:
            original = receipt.pop(role)
            self.save()
            self.assertEqual(self.rows()['build']['action'], 'review_' + role)
            receipt[role] = original
        receipt['checker']['actor'] = ' WORKER '
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'review_checker')
        receipt['review_mode'] = 'sequential'
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'repair')
        receipt['sequential_opt_in'] = True
        self.save()
        self.assertTrue(self.rows()['build']['accepted'])
        self.assertFalse(self.rows()['build']['independent'])
        receipt['requires_independence'] = True
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'repair')

    def test_stale_review_bindings_and_actual_librarian_confirmation(self):
        self.meta['tasks']['build']['checker']['inputs'] = {}
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'review_checker')
        self.meta['tasks']['build'] = self.receipt(self.tasks[0])
        self.meta['tasks']['build']['librarian']['confirmed_output'] = False
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'review_librarian')

    def test_blocker_needs_evidence_and_independent_work_continues(self):
        worker = self.meta['tasks']['build']['worker']
        worker['verdict'] = 'BLOCKED'
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'review_worker')
        worker['blocker'] = {'reason': 'Fixture API unavailable', 'next_action': 'Owner restores API', 'evidence': ['Fixture failure transcript']}
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'blocked')
        # A genuinely blocked worker may have no output yet; never invent one.
        self.meta['tasks']['build']['outputs'] = {}
        worker['outputs'] = {}
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'blocked')
        self.assertEqual(self.rows()['test']['action'], 'wait_for_dependencies')
        self.assertEqual(self.rows()['other']['action'], 'execute')
        self.assertFalse(self.result()['stop_allowed'])

    def test_authority_scope_and_unknown_ids(self):
        self.meta['permission_scope']['build'] = []
        self.save()
        with self.assertRaises(ValueError):
            self.result()
        self.meta['permission_scope']['build'] = ['local only']
        self.meta['authorized_tasks'].remove('other')
        self.save()
        self.assertEqual(self.rows()['other']['action'], 'needs_authority')
        self.meta['tasks']['ghost'] = {}
        self.save()
        with self.assertRaises(ValueError):
            self.result()

    def test_checkboxes_are_reports_finish_line_separate_and_no_execution(self):
        for t in self.tasks:
            t['done'] = True
        self.save(True)
        self.assertEqual(self.rows()['other']['action'], 'review_reported_completion')
        self.assertFalse(self.result()['project_complete'])
        for t in self.tasks:
            self.meta['tasks'][t['id']] = self.receipt(t)
        self.save()
        self.assertTrue(self.result()['stop_allowed'])
        self.assertFalse(self.result()['project_complete'])
        self.save(True)
        self.assertTrue(self.result()['project_complete'])
        self.tasks[0]['done'] = False
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'reconcile_progress')
        self.assertEqual(self.rows()['test']['action'], 'wait_for_dependencies')

    def test_pending_followthrough_does_not_silently_stop(self):
        for t in self.tasks:
            t['done'] = True
            self.meta['tasks'][t['id']] = self.receipt(t)
        self.save(True)
        self.project.write_text(self.project.read_text() + '**Librarian review:** pending — UI update\n')
        self.assertFalse(self.result()['stop_allowed'])
        self.assertFalse(self.result()['project_complete'])
        self.assertEqual(self.result()['eligible'][-1]['action'], 'librarian_followthrough')

    def test_legacy_optional_and_boundary_checks(self):
        self.meta = None
        self.save()
        self.assertEqual(self.result()['mode'], 'legacy-untracked')
        self.assertFalse(self.result()['stop_allowed'])
        nested = self.root / '01-projects/nested'
        nested.mkdir()
        (nested / '.git').mkdir()
        (nested / 'README.md').write_text(self.project.read_text())
        with self.assertRaises(ValueError):
            review.evaluate(self.root, '01-projects/nested/README.md')
        with self.assertRaises(ValueError):
            review.evaluate(self.root, '../outside.md')

    def test_cli_assert_stop_and_no_state_writes(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--vault', str(self.root),
                                 '--project', '01-projects/test.md', '--assert-stop'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(json.loads(result.stdout)['eligible'])
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_outside_and_self_manifest_rejected(self):
        binding = self.meta['tasks']['build']
        binding['outputs'] = {'../outside': '0' * 64}
        self.save()
        self.assertEqual(self.rows()['build']['action'], 'repair')
        binding['outputs'] = {'01-projects/test.md': '0' * 64}
        self.save()
        self.assertIn('project note cannot hash itself: 01-projects/test.md', self.rows()['build']['issues'])


if __name__ == '__main__':
    unittest.main()
