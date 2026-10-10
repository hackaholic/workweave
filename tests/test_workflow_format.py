import tempfile
import unittest
from pathlib import Path
from workweave.parser import parse_work_directory, update_subtask, add_work_comment
from workweave.workflow_format import dependencies, fields
FIXTURES = Path(__file__).parent / 'fixtures/shared-workflow'

class TestWorkflowFormat(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.work = self.root / 'work'
        self.folder = self.work / 'work-001-setup'
        (self.folder / 'tasks').mkdir(parents=True)
        (self.work / 'INDEX.md').write_text((FIXTURES / 'INDEX.md').read_text().replace('<Initial Project Setup / Feature>', 'Fixture'))
        (self.folder / 'coordination.md').write_text((FIXTURES / 'coordination.md').read_text().replace('<agent/person/unassigned>', 'Research Agent').replace('<Active / Blocked / Returned / Ready for Review>', 'Active').replace('<None / Link to tasks/task-XXX.md>', '[1.2](tasks/ui.md)').replace('<None / concrete next action and responsible agent/person>', 'Return API evidence'))

    def contract(self, filename, task_id, status='Pending', depends='None'):
        content = (FIXTURES / 'TASK_TEMPLATE.md').read_text().replace('<work-id>.<task-id>', task_id).replace('<short title>', 'Example').replace('<agent/person>', 'Research Agent').replace('**Status:** Pending', '**Status:** ' + status).replace('- Depends on: None', '- Depends on: ' + depends)
        (self.folder / 'tasks' / filename).write_text(content)

    def test_scaffold_fields_and_read_only(self):
        self.contract('api.md', '1.1'); self.contract('ui.md', '1.2', 'Blocked', '1.1')
        (self.folder / 'tasks.md').write_text('## Pending\n- [ ] 1.1 Research Agent: [API](tasks/api.md)\n## Blocked\n- [ ] 1.2 [UI](tasks/ui.md)\n')
        before = {p:p.read_bytes() for p in self.work.rglob('*.md')}
        item = parse_work_directory(self.root).items[0]
        self.assertEqual(item.current_owner, 'Research Agent'); self.assertEqual(item.handoff_state, 'Active')
        self.assertEqual(item.active_task, '[1.2](tasks/ui.md)'); self.assertEqual(item.next_action, 'Return API evidence')
        task = item.subtasks[1]
        self.assertEqual((task.task_id,task.owner,task.status), ('1.2','Research Agent','Blocked'))
        self.assertEqual(task.dependencies, ['1.1']); self.assertFalse(task.resolved_dependencies[0]['completed'])
        self.assertEqual(before, {p:p.read_bytes() for p in self.work.rglob('*.md')})

    def test_conflicts_unknown_duplicate_and_cycle(self):
        self.contract('api.md', '1.1', 'Blocked', '1.2'); self.contract('ui.md', '1.2', depends='1.1, 9.9')
        (self.folder / 'tasks.md').write_text('## Pending\n- [ ] 1.1 Other Agent: [API](tasks/api.md)\n- [ ] 1.2 [UI](tasks/ui.md)\n')
        tasks = parse_work_directory(self.root).items[0].subtasks
        self.assertEqual(tasks[0].status, 'Pending')
        self.assertIn('owners disagree', ' '.join(tasks[0].warnings)); self.assertIn('cycle', ' '.join(tasks[0].warnings))
        self.assertIn('9.9', ' '.join(tasks[1].warnings))
        with (self.folder / 'tasks.md').open('a') as f: f.write('- [ ] 1.1 Duplicate\n')
        self.assertIn('Duplicate task ID', ' '.join(parse_work_directory(self.root).items[0].subtasks[0].warnings))
        self.assertEqual(dependencies('Requires returned Gemini 1.1 API'), [])
        meta,warnings=fields('**Current owner:** Alice\n- Current Owner: Bob\n')
        self.assertEqual(meta['current owner'],'Alice'); self.assertTrue(warnings)
        self.assertEqual(fields('Completed: previous work\nCompleted: later work\n'), ({}, []))

    def test_rename_preserves_identity_comments_and_unrelated_bytes(self):
        self.contract('api.md', '1.1')
        tasks=self.folder/'tasks.md'; tasks.write_text('# Tasks\n\n## Pending\n* [ ] 1.1 Research Agent: [API](tasks/api.md)\n\nUntouched footer\n')
        old=parse_work_directory(self.root).items[0].subtasks[0]
        add_work_comment(self.root,'work-001','Keep this comment',subtask_id=old.id)
        update_subtask(self.root,'work-001',old.id,new_title='Renamed API')
        new=parse_work_directory(self.root).items[0].subtasks[0]
        self.assertEqual(new.id,old.id); self.assertEqual(new.task_id,'1.1')
        self.assertEqual(new.comments[0].text,'Keep this comment'); self.assertEqual(new.contract_path,old.contract_path)
        self.assertTrue(tasks.read_text().endswith('\n\nUntouched footer\n'))
        before=tasks.read_bytes()
        with self.assertRaises(ValueError): update_subtask(self.root,'work-001',old.id,new_title='9.9 Wrong ID')
        self.assertEqual(before,tasks.read_bytes())

    def test_legacy_bold_and_contract_fallback(self):
        (self.folder/'coordination.md').write_text('**Current owner:** New Agent\n**Handoff state:** Returned\n')
        self.contract('api.md','1.1','Blocked')
        (self.folder/'tasks.md').write_text('- [ ] 1.1 [API](tasks/api.md)\n')
        item=parse_work_directory(self.root).items[0]
        self.assertEqual(item.handoff_state,'Returned'); self.assertEqual(item.subtasks[0].status,'Blocked')

    def test_cross_work_links_and_unsafe_unknown_targets(self):
        other=self.work/'work-002-other'; (other/'tasks').mkdir(parents=True)
        (other/'tasks.md').write_text('## Completed\n- [x] 2.1 [Ready](tasks/api.md)\n')
        (other/'tasks/api.md').write_text('# Task 2.1 — Ready\n**Status:** Completed\n')
        self.contract('ui.md','1.2', depends='[2.1](../../work-002-other/tasks/api.md), [outside](../../../../outside.md)')
        (self.folder/'tasks.md').write_text('## Blocked\n- [ ] 1.2 [UI](tasks/ui.md)\n')
        task=parse_work_directory(self.root).items[0].subtasks[0]
        self.assertEqual(len(task.resolved_dependencies),1)
        self.assertEqual(task.resolved_dependencies[0]['work_id'],'work-002')
        self.assertTrue(task.resolved_dependencies[0]['completed']); self.assertEqual(task.status,'Blocked')
        self.assertIn('outside', ' '.join(task.warnings))

    def test_rename_preserves_crlf_and_duplicate_denial(self):
        tasks=self.folder/'tasks.md'; tasks.write_bytes(b'# Tasks\r\n- [ ] 1.1 Title\r\n\r\nFooter\r\n')
        task=parse_work_directory(self.root).items[0].subtasks[0]
        update_subtask(self.root,'work-001',task.id,new_title='New title')
        self.assertTrue(tasks.read_bytes().endswith(b'\r\n\r\nFooter\r\n'))
        self.assertNotIn(b'\n',tasks.read_bytes().replace(b'\r\n',b''))
        tasks.write_text('- [ ] Duplicate\n- [ ] Duplicate\n')
        before=tasks.read_bytes()
        with self.assertRaises(ValueError): update_subtask(self.root,'work-001','Duplicate',new_title='Change')
        self.assertEqual(before,tasks.read_bytes())

    def test_dependency_actionable_warnings(self):
        self.contract('api.md', '1.1')
        self.contract('ui.md', '1.2', depends='1.1 coordinate final classes')
        (self.folder / 'tasks.md').write_text('## Pending\n- [ ] 1.1 [API](tasks/api.md)\n- [ ] 1.2 [UI](tasks/ui.md)\n')
        tasks = parse_work_directory(self.root).items[0].subtasks
        self.assertEqual(tasks[1].dependencies, [])
        self.assertTrue(any('Put narrative under Dependency context' in w for w in tasks[1].warnings))
        self.contract('clean.md', '1.3', depends='1.1, 1.2')
        with (self.folder / 'tasks.md').open('a') as f: f.write('- [ ] 1.3 [Clean](tasks/clean.md)\n')
        clean_task = parse_work_directory(self.root).items[0].subtasks[2]
        self.assertEqual(clean_task.dependencies, ['1.1', '1.2'])
        self.assertFalse(any('Dependency prose' in w for w in clean_task.warnings))

