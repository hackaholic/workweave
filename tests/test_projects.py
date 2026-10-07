"""Registry persistence, validation, and failure behavior."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workweave.projects import ProjectError, ProjectRegistry


class TestProjects(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'alpha'
        (self.project / 'work').mkdir(parents=True)
        self.data = self.root / 'data'
        self.registry = ProjectRegistry(self.data)

    def test_empty_add_and_restart(self):
        self.assertEqual(self.registry.list(), [])
        self.assertFalse(self.data.exists())
        first = self.registry.add(str(self.project))
        second_dir = self.root / 'beta' / 'work'
        second_dir.mkdir(parents=True)
        second = self.registry.add(str(second_dir), 'Second project')
        self.assertEqual(first['name'], 'Alpha')
        self.assertNotEqual(first['id'], second['id'])
        self.assertEqual(ProjectRegistry(self.data).list(), [first, second])
        self.assertEqual(list((self.project / 'work').iterdir()), [])

    def test_duplicates_canonicalized(self):
        self.registry.add(str(self.project))
        alias = self.root / 'alias'
        alias.symlink_to(self.project, target_is_directory=True)
        for path in [self.project / 'work', alias]:
            with self.assertRaises(ProjectError) as ctx:
                self.registry.add(str(path))
            self.assertEqual(ctx.exception.status, 409)
        self.assertEqual(len(self.registry.list()), 1)

    def test_invalid_inputs_do_not_write(self):
        file = self.root / 'file'
        file.write_text('text')
        for path in ['', 'relative', str(file), str(self.root / 'missing'), str(self.root), None, 42, '\x00']:
            with self.subTest(path=path), self.assertRaises(ProjectError):
                self.registry.add(path)
        for name in [42, 'x' * 121, None]:
            with self.assertRaises(ProjectError):
                self.registry.add(str(self.project), name)
        self.assertFalse(self.data.exists())

    def test_root_boundary_and_symlink(self):
        restricted = ProjectRegistry(self.data, self.project)
        outside = self.root / 'outside' / 'work'
        outside.mkdir(parents=True)
        alias = self.project / 'escape'
        alias.symlink_to(outside, target_is_directory=True)
        for path in [outside, alias, self.project / '..' / 'outside']:
            with self.assertRaises(ProjectError) as ctx:
                restricted.add(str(path))
            self.assertEqual(ctx.exception.code, 'outside_projects_root')
        self.assertFalse(self.data.exists())

    def test_corruption_preserved(self):
        self.data.mkdir()
        for content in ['broken', '{"version":2,"projects":[]}', '{"version":1,"projects":[{}]}']:
            self.registry.path.write_text(content)
            with self.assertRaises(ProjectError):
                self.registry.add(str(self.project))
            self.assertEqual(self.registry.path.read_text(), content)

    def test_failed_replace_preserves_registry(self):
        self.registry.add(str(self.project))
        before = self.registry.path.read_bytes()
        second = self.root / 'beta' / 'work'
        second.mkdir(parents=True)
        with patch('workweave.projects.os.replace', side_effect=OSError('disk error')):
            with self.assertRaises(ProjectError):
                self.registry.add(str(second))
        self.assertEqual(self.registry.path.read_bytes(), before)
        self.assertEqual(list(self.data.iterdir()), [self.registry.path])
