import tempfile
import unittest
from pathlib import Path
from workweave.parser import create_work_item, scaffold_draft_work
from workweave.services.lifecycle import state
from workweave.services.preparation import enroll, preview


class TestPreparation(unittest.TestCase):
    def test_new_draft_preserved_and_prepare_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'work').mkdir()
            name = create_work_item(root, 'My request', '  First line\nSecond line\n', is_draft=False, owner='Fake')
            folder = root / 'work' / name
            before = {p.name: p.read_bytes() for p in folder.iterdir() if p.is_file()}
            scaffold_draft_work(root, 'work-001')
            scaffold_draft_work(root, 'work-001')
            self.assertEqual(before, {p.name: p.read_bytes() for p in folder.iterdir() if p.is_file()})
            data = state(folder)
            self.assertEqual(data['request'], 'My request\n\n  First line\nSecond line\n')
            self.assertEqual(data['phase'], 'Draft')
            self.assertIsNone(data['executor'])
            self.assertEqual(list((folder / 'tasks').iterdir()), [])

    def test_legacy_enrollment_has_no_inferred_approval_or_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'notes.md').write_text('Original notes\n')
            (folder / 'tasks.md').write_text('- [x] Historical work\n')
            before = preview(folder)
            data = enroll(folder, 'User', 0)
            self.assertEqual(data['phase'], 'Draft')
            self.assertIsNone(data['approval'])
            self.assertEqual(before, preview(folder))
