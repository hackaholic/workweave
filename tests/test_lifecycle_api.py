"""End-to-end HTTP approval gates using disposable projects."""
import unittest
import test_project_api
from test_lifecycle import example_plan


class TestLifecycleAPI(unittest.TestCase):
    setUp = test_project_api.TestProjectAPI.setUp
    stop = test_project_api.TestProjectAPI.stop
    request = test_project_api.TestProjectAPI.request
    add = test_project_api.TestProjectAPI.add
    def test_planning_review_execution_and_isolation(self):
        first, other = self.add('Alpha'), self.add('Beta')
        pid = first['id']
        def act(action, version, **extra):
            return self.request('POST', '/api/lifecycle', dict(project_id=pid, work_id='work-001',
                action=action, expected_version=version, actor='Codex', **extra))
        status, before = self.request('GET', f'/api/lifecycle?project={pid}&work=work-001')
        self.assertEqual(status, 200)
        self.assertFalse(before['lifecycle']['managed'])
        self.assertFalse(before['handoff']['direct_invocation_available'])
        self.assertNotIn('Beta objective', before['handoff']['prompt'])
        self.assertEqual(act('start', 0)[0], 409)
        self.assertEqual(act('enroll', 0)[0], 200)
        self.assertEqual(act('enroll', 0)[0], 409)
        _, result = act('accept_planning', 1)
        run = result['lifecycle']['run']['id']
        self.assertEqual(act('submit_plan', 2, run_id='old', plan=example_plan())[0], 409)
        wrong = dict(project_id=other['id'], work_id='work-001', action='submit_plan',
                     expected_version=2, actor='Codex', run_id=run, plan=example_plan())
        self.assertEqual(self.request('POST', '/api/lifecycle', wrong)[0], 409)
        plan = example_plan(); plan['objective'] = '<script>throw new Error("unsafe")</script>'
        self.assertEqual(act('submit_plan', 2, run_id=run, plan=plan)[0], 200)
        self.assertEqual(act('start', 3)[0], 409)
        toggle = dict(project_id=pid, work_id='work-001', subtask_id='planned-1', completed=True, expected_version=3)
        self.assertEqual(self.request('POST', '/api/subtasks/toggle', toggle)[0], 409)
        self.assertEqual(act('approve', 3)[0], 200)
        self.assertEqual(act('approve', 3)[0], 409)
        self.assertEqual(act('start', 4)[0], 200)
        self.assertEqual(act('complete', 5, feedback='Tests passed')[0], 409)
        toggle['expected_version'] = 5
        self.assertEqual(self.request('POST', '/api/subtasks/toggle', toggle)[0], 200)
        self.assertEqual(self.request('POST', '/api/subtasks/toggle', toggle)[0], 409)
        self.assertEqual(act('complete', 6, feedback='Tests passed')[0], 200)
        _, state = self.request('GET', f'/api/workflow?project={pid}')
        self.assertEqual(state['items'][0]['status'], 'Completed')
        self.assertTrue(state['items'][0]['subtasks'][0]['completed'])
        self.assertEqual(act('request_changes', 7, feedback='Adjust scope')[0], 200)
        _, context = self.request('GET', f'/api/lifecycle?project={pid}&work=work-001')
        self.assertIn('Adjust scope', context['handoff']['prompt'])
        self.assertEqual(context['lifecycle']['request'], '## Goal\nAlpha objective')
        status, page = self.request('GET', f'/projects/{pid}/work/work-001/review')
        self.assertEqual(status, 200)
        self.assertIn('textContent', page)
        self.assertNotIn(plan['objective'], page)

    def test_lifecycle_invalid_requests_and_changed_context(self):
        project = self.add('Alpha'); pid = project['id']
        base = dict(project_id=pid, work_id='work-001', action='enroll', expected_version=0, actor='User')
        self.assertEqual(self.request('POST', '/api/lifecycle', dict(base, actor=None))[0], 400)
        self.assertEqual(self.request('POST', '/api/lifecycle', dict(base, work_id='../work-001'))[0], 400)
        self.assertEqual(self.request('POST', '/api/lifecycle', base, headers={'Origin':'https://untrusted.test'})[0], 403)
        self.assertEqual(self.request('POST', '/api/lifecycle', base)[0], 200)
        base.update(action='accept_planning', expected_version=1)
        _, result = self.request('POST', '/api/lifecycle', base)
        (self.root / 'Alpha/work/work-001/README.md').write_text('Changed during planning')
        base.update(action='submit_plan', expected_version=2, run_id=result['lifecycle']['run']['id'], plan=example_plan())
        self.assertEqual(self.request('POST', '/api/lifecycle', base)[0], 409)
        _, current = self.request('GET', f'/api/lifecycle?project={pid}&work=work-001')
        self.assertEqual(current['lifecycle']['phase'], 'Planning')
        self.assertEqual(current['lifecycle']['plans'], [])

    def test_legacy_definition_edits_cannot_bypass_completion_gate(self):
        project = self.add('Legacy')
        payload = dict(project_id=project['id'], work_id='work-001', title='Planning input')
        code, result = self.request('POST', '/api/subtasks/new', payload)
        self.assertEqual(code, 201)
        task_id = result['subtask']['id']
        payload.update(subtask_id=task_id, title='Refined planning input')
        self.assertEqual(self.request('POST', '/api/subtasks/toggle', payload)[0], 200)
        tasks = self.root / 'Legacy/work/work-001/tasks.md'
        before = tasks.read_bytes()
        self.assertEqual(self.request('POST', '/api/subtasks/toggle', dict(payload, completed=True))[0], 409)
        self.assertEqual(tasks.read_bytes(), before)
