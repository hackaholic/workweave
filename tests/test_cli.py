import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workweave.cli import main


class TestCLI(unittest.TestCase):
    @patch.dict('os.environ', {}, clear=True)
    def test_startup_is_empty_and_loopback(self):
        with patch('workweave.cli.run_server') as run:
            self.assertEqual(main([]), 0)
        self.assertIsNone(run.call_args.kwargs['target_path'])
        self.assertEqual(run.call_args.kwargs['host'], '127.0.0.1')

    @patch.dict('os.environ', {}, clear=True)
    def test_exports_do_not_create_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'work').mkdir()
            args = ['--target', str(root), '--data-dir', str(root / 'data')]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(args + ['--json']), 0)
            self.assertEqual(json.loads(output.getvalue())['total_work_items'], 0)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args + ['--build', str(root / 'out.html')]), 0)
            self.assertIn('<!DOCTYPE html>', (root / 'out.html').read_text())
            self.assertNotIn('Project navigation', (root / 'out.html').read_text())
            self.assertFalse((root / 'data').exists())
