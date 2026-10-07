"""Folder listing behavior and filesystem boundaries."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workweave.projects import ProjectError, ProjectRegistry


class TestFolders(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'repos'
        self.root.mkdir()
        self.registry = ProjectRegistry(self.base / 'data', self.root)

    def test_navigation_and_selection(self):
        project = self.root / 'Alpha'
        (project / 'work').mkdir(parents=True)
        (self.root / 'beta').mkdir()
        (self.root / 'file.txt').write_text('not listed')
        data = self.registry.browse()
        self.assertEqual(data['path'], str(self.root))
        self.assertIsNone(data['parent'])
        self.assertFalse(data['selectable'])
        self.assertEqual([p['name'] for p in data['directories']], ['Alpha', 'beta'])
        data = self.registry.browse(str(project))
        self.assertTrue(data['selectable'])
        self.assertEqual(data['parent'], str(self.root))
        data = self.registry.browse(str(project / 'work'))
        self.assertEqual(data['directories'], [])
        self.assertTrue(data['selectable'])
        self.assertFalse(self.registry.path.exists())

    def test_escape_and_invalid_paths(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (self.root / 'escape').symlink_to(outside, target_is_directory=True)
        (self.root / 'broken').symlink_to(self.base / 'missing')
        (self.root / 'file').write_text('secret')
        for path in [str(self.root / '..'), str(self.root / 'escape'), str(self.root / 'missing'), str(self.root / 'file'), '', 'relative', '\x00', 12]:
            with self.subTest(path=path), self.assertRaises(ProjectError):
                self.registry.browse(path)
        self.assertEqual(self.registry.browse()['directories'], [])
        self.assertFalse(self.registry.path.exists())

    def test_native_home_and_root(self):
        registry = ProjectRegistry(self.base / 'data')
        with patch('workweave.projects.Path.home', return_value=self.root):
            self.assertEqual(registry.browse()['path'], str(self.root))
        self.assertIsNone(registry.browse(self.root.anchor)['parent'])

    def test_unreadable_folder(self):
        with patch('workweave.projects.Path.iterdir', side_effect=PermissionError):
            with self.assertRaises(ProjectError) as ctx:
                self.registry.browse()
        self.assertEqual(ctx.exception.code, 'folder_unreadable')
        self.assertFalse(self.registry.path.exists())

    def test_listing_limit_and_special_names(self):
        for i in range(1001):
            (self.root / f'folder-{i:04d}').mkdir()
        data = self.registry.browse()
        self.assertEqual(len(data['directories']), 1000)
        self.assertTrue(data['truncated'])
        self.assertEqual(data['directories'][0]['name'], 'folder-0000')
        name = '<img onerror=alert(1)> & quotes\''
        (self.root / name).mkdir()
        data = self.registry.browse()
        self.assertEqual(data['directories'][0]['name'], name)
