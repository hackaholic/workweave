"""Unit tests for WorkWeave parser."""

import tempfile
import unittest
from pathlib import Path

from workweave.parser import (
    SubTask,
    TaskContract,
    WorkflowState,
    parse_subtask_line,
    parse_task_contract,
    parse_work_directory,
    resolve_work_directory,
)


class TestParser(unittest.TestCase):
    def test_resolve_work_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Scenario 1: root with work/ subdir
            work_subdir = tmppath / "work"
            work_subdir.mkdir()
            resolved_work, resolved_root = resolve_work_directory(tmppath)
            self.assertEqual(resolved_work, work_subdir)
            self.assertEqual(resolved_root, tmppath)

            # Scenario 2: direct work/ folder
            resolved_work2, resolved_root2 = resolve_work_directory(work_subdir)
            self.assertEqual(resolved_work2, work_subdir)
            self.assertEqual(resolved_root2, tmppath)

    def test_parse_subtask_line(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            work_folder = root / "work" / "work-001"
            work_folder.mkdir(parents=True)

            # Completed task with owner comment
            line1 = "- [x] Gemini: 1.1 Initialize project"
            st1 = parse_subtask_line(line1, work_folder, root)
            self.assertIsNotNone(st1)
            self.assertTrue(st1.completed)
            self.assertIn("1.1 Initialize project", st1.title)
            self.assertEqual(st1.owner, "Gemini")

            # Incomplete task with contract link
            line2 = "- [ ] 1.2 Implement core API [contract](tasks/task-1.2.md)"
            st2 = parse_subtask_line(line2, work_folder, root)
            self.assertIsNotNone(st2)
            self.assertFalse(st2.completed)
            self.assertEqual(st2.contract_title, "contract")
            self.assertTrue(st2.contract_path.endswith("task-1.2.md"))

            # Invalid line
            self.assertIsNone(parse_subtask_line("Just some markdown text", work_folder, root))

    def test_parse_task_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            contract_file = root / "task-1.1.md"
            contract_file.write_text(
                """# Task Contract: Setup DB

**Owner:** Antigravity
**Status:** In Progress

## Objective
Configure PostgreSQL schema and migrations.

## Scope
- Setup tables
- Add seeds

## Out of Scope
- Production deployment

## Acceptance Criteria
- [x] Migrations pass
- [ ] Seeds run cleanly
""",
                encoding="utf-8",
            )

            contract = parse_task_contract(contract_file, root)
            self.assertEqual(contract.filename, "task-1.1.md")
            self.assertIn("Setup DB", contract.title)
            self.assertEqual(contract.owner, "Antigravity")
            self.assertEqual(contract.status, "In Progress")
            self.assertIn("Configure PostgreSQL schema", contract.objective)
            self.assertIn("Setup tables", contract.scope_in)

    def test_parse_mock_work_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            work_dir = root / "work"
            work_dir.mkdir()

            # INDEX.md
            (work_dir / "INDEX.md").write_text(
                """# Active Work Items
- **Work 001 — Foundation Setup** · Completed · [work folder](work-001-foundation/)
- **Work 002 — UI Layer** · In Progress · [work folder](work-002-ui/)
""",
                encoding="utf-8",
            )

            # work-001
            w1 = work_dir / "work-001-foundation"
            w1.mkdir()
            (w1 / "README.md").write_text("## Goal\nSetup foundational infrastructure.", encoding="utf-8")
            (w1 / "tasks.md").write_text("- [x] 1.1 Base setup\n- [x] 1.2 Config", encoding="utf-8")

            # work-002
            w2 = work_dir / "work-002-ui"
            w2.mkdir()
            (w2 / "README.md").write_text("## Goal\nImplement user dashboard.", encoding="utf-8")
            (w2 / "tasks.md").write_text("- [x] 2.1 Wireframes\n- [ ] 2.2 Views", encoding="utf-8")
            (w2 / "coordination.md").write_text(
                "**Current owner:** Gemini\n**Active cross-agent handoffs:** 2.2\n**Handoff state:** Active\n",
                encoding="utf-8",
            )

            state = parse_work_directory(root, project_title="Test Project")
            self.assertEqual(state.project_name, "Test Project")
            self.assertEqual(state.total_work_items, 2)
            self.assertEqual(state.completed_items, 1)
            self.assertEqual(state.in_progress_items, 1)
            self.assertEqual(state.total_subtasks, 4)
            self.assertEqual(state.completed_subtasks, 3)
            self.assertEqual(state.overall_progress_percent, 75)

    def test_comments_and_subtask_mutations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            work_dir = root / "work"
            work_dir.mkdir()
            (work_dir / "INDEX.md").write_text(
                "- **Work 001 — Core** · Pending · [work folder](work-001/)\n",
                encoding="utf-8",
            )
            w1 = work_dir / "work-001"
            w1.mkdir()
            (w1 / "README.md").write_text("# Work 001 — Core\n\n## Goal\nTest goal", encoding="utf-8")
            (w1 / "tasks.md").write_text("# Tasks\n\n- [ ] 1.1 First task\n", encoding="utf-8")

            # 1. Add comment
            from workweave.parser import (
                add_work_comment,
                create_subtask,
                create_work_item,
                scaffold_draft_work,
                update_subtask,
            )
            comment = add_work_comment(root, "work-001", "This is a test comment", author="Tester", subtask_id="1-1-first-task")
            self.assertEqual(comment.author, "Tester")
            self.assertIn("This is a test comment", (w1 / "comments.md").read_text(encoding="utf-8"))

            # 2. Update subtask
            updated = update_subtask(root, "work-001", "1-1-first-task", new_title="1.1 Renamed first task", completed=True)
            self.assertTrue(updated)
            tasks_content = (w1 / "tasks.md").read_text(encoding="utf-8")
            self.assertIn("- [x] 1.1 Renamed first task", tasks_content)

            # 3. Create subtask
            st = create_subtask(root, "work-001", "1.2 Second task", owner="Antigravity")
            self.assertIn("1.2 Second task", st.title)
            self.assertEqual(st.owner, "Antigravity")
            self.assertIn("1.2 Second task", (w1 / "tasks.md").read_text(encoding="utf-8"))

            # 4. Create new work draft
            folder = create_work_item(root, "New Feature", description="My user notes", is_draft=True)
            self.assertTrue(folder.startswith("work-002-"))
            self.assertTrue((work_dir / folder / "README.md").is_file())
            self.assertIn("New Feature", (work_dir / "INDEX.md").read_text(encoding="utf-8"))

            # Verify parsed state shows draft and comments
            state = parse_work_directory(root)
            self.assertEqual(state.total_work_items, 2)
            self.assertEqual(len(state.items[0].comments), 1)
            self.assertTrue(state.items[1].is_draft)

            # 5. Scaffold draft work
            scaffolded = scaffold_draft_work(root, "work-002")
            self.assertTrue(scaffolded)
            self.assertFalse((work_dir / folder / "tasks" / "task-2.1.md").exists())
            self.assertNotIn("In Progress", (work_dir / "INDEX.md").read_text(encoding="utf-8"))

    def test_parse_real_crochet_work_dir(self):
        crochet_dir = Path("/home/anu/git/crochet")
        if (crochet_dir / "work").is_dir():
            state = parse_work_directory(crochet_dir)
            self.assertTrue(state.total_work_items > 0)
            self.assertTrue(any(item.id == "work-009" for item in state.items))


if __name__ == "__main__":
    unittest.main()
