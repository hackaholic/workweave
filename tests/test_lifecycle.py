import copy
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from workweave.repositories import lifecycle as store
from workweave.schemas.lifecycle import LifecycleError
from workweave.services import lifecycle as life


def example_plan():
    return {'objective': 'Add a folder picker', 'scope': ['Browse mounted folders'], 'non_goals': ['Upload files'],
            'architecture': 'Reuse the registry boundary.', 'assumptions': ['Local use'], 'questions': [],
            'tasks': [{'id': '1', 'title': 'List folders', 'objective': 'Return contained directories',
                       'acceptance': ['Reject symlink escapes'], 'dependencies': []}]}


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        (self.folder / 'README.md').write_text('Original goal\n')
        (self.folder / 'tasks.md').write_text('- [ ] Original task\n')
        self.state = life.initialize(self.folder, 'Original user request\nKeep every line.\n')

    def act(self, action, actor='User', **kwargs):
        self.state = life.transition(self.folder, action, self.state['version'], actor, **kwargs)
        return self.state

    def submit(self, plan=None):
        self.act('accept_planning', 'Codex')
        self.act('submit_plan', 'Codex', run_id=self.state['run']['id'], plan=plan or example_plan())

    def test_complete_sequence_and_restart(self):
        self.submit()
        self.assertEqual(self.state['phase'], 'Ready for review')
        self.act('approve')
        self.assertIsNone(self.state['executor'])
        self.act('start', 'Codex')
        self.state = life.toggle_task(self.folder, '1', True, self.state['version'])
        self.act('complete', 'Codex', feedback='Acceptance tests passed')
        self.assertEqual(life.state(self.folder)['phase'], 'Completed')
        self.assertEqual(self.state['request'], 'Original user request\nKeep every line.\n')

    def test_no_skip_and_stale_updates(self):
        before = (self.folder / 'workflow.json').read_bytes()
        with self.assertRaises(LifecycleError):
            self.act('start')
        self.assertEqual((self.folder / 'workflow.json').read_bytes(), before)
        self.submit()
        version = self.state['version']
        def approve():
            try:
                life.transition(self.folder, 'approve', version, 'User')
                return True
            except LifecycleError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(lambda _: approve(), range(2))), [False, True])

    def test_scope_changes_invalidate_but_progress_does_not(self):
        self.submit()
        self.act('approve')
        (self.folder / 'notes.md').write_text('Execution observations')
        (self.folder / 'tasks.md').write_text('- [x] Original task\n')
        self.assertTrue(life.state(self.folder)['approval_valid'])
        (self.folder / 'README.md').write_text('Changed scope')
        self.assertFalse(life.state(self.folder)['approval_valid'])
        with self.assertRaises(LifecycleError):
            self.act('start')

    def test_questions_revisions_and_stale_returns(self):
        plan = example_plan()
        plan['questions'] = ['Which folder?']
        self.submit(plan)
        old = copy.deepcopy(self.state['plans'])
        with self.assertRaises(LifecycleError):
            self.act('approve')
        self.act('request_changes', feedback='Use the mounted root')
        self.act('accept_planning', 'Codex')
        run = self.state['run']['id']
        with self.assertRaises(LifecycleError):
            self.act('submit_plan', 'Codex', run_id='old-run', plan=example_plan())
        self.act('submit_plan', 'Codex', run_id=run, plan=example_plan())
        self.assertEqual(self.state['plans'][:1], old)
        self.act('approve')
        self.assertEqual(self.state['approval']['revision'], 2)

    def test_cancel_and_failed_atomic_save(self):
        self.act('accept_planning', 'Codex')
        run = self.state['run']['id']
        self.act('cancel_planning', run_id=run)
        self.assertEqual(self.state['phase'], 'Draft')
        before = (self.folder / 'workflow.json').read_bytes()
        with patch('workweave.repositories.lifecycle.os.replace', side_effect=OSError('disk')):
            with self.assertRaises(LifecycleError):
                self.act('accept_planning', 'Codex')
        self.assertEqual((self.folder / 'workflow.json').read_bytes(), before)

    def test_corrupt_record_and_path_escape_fail_closed(self):
        (self.folder / 'workflow.json').write_text('{broken')
        with self.assertRaises(LifecycleError):
            life.state(self.folder)
        with self.assertRaises(LifecycleError):
            store.safe_file(self.folder, '../escape')

    def test_invalid_plan_dependencies(self):
        self.act('accept_planning', 'Codex')
        plan = example_plan()
        plan['tasks'][0]['dependencies'] = ['1']
        with self.assertRaises(LifecycleError):
            self.act('submit_plan', 'Codex', run_id=self.state['run']['id'], plan=plan)

    def test_dependencies_and_corrupt_metadata(self):
        plan = example_plan()
        second = copy.deepcopy(plan['tasks'][0]); second.update(id='2', dependencies=['1'])
        plan['tasks'].append(second)
        self.submit(plan); self.act('approve'); self.act('start')
        with self.assertRaises(LifecycleError):
            life.toggle_task(self.folder, '2', True, self.state['version'])
        self.state = life.toggle_task(self.folder, '1', True, self.state['version'])
        self.state = life.toggle_task(self.folder, '2', True, self.state['version'])
        with self.assertRaises(LifecycleError):
            life.toggle_task(self.folder, '1', False, self.state['version'])
        raw = store.read(self.folder); del raw['progress']
        store.write(self.folder, raw)
        with self.assertRaises(LifecycleError):
            life.state(self.folder)
