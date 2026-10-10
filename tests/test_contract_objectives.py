import tempfile
import unittest
from pathlib import Path

from workweave.parser import parse_task_contract


class TestContractObjectives(unittest.TestCase):
    def parse(self, text):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'task.md'
            path.write_text(text)
            before = path.read_bytes()
            result = parse_task_contract(path, root)
            self.assertEqual(path.read_bytes(), before)
            return result

    def test_canonical_and_observed_headings(self):
        for heading in ('Objective', 'Objective and context', 'Objective and scope',
                        'Objective and contract', 'Objective/context',
                        'Objective/context and scope'):
            with self.subTest(heading=heading):
                task = self.parse(f'# Task 18.5 — Account\n## {heading}\nEdit profile.\n\nKeep <script> text literal.\n## Scope\nOther text\n')
                self.assertEqual(task.objective, 'Edit profile. Keep <script> text literal.')
                self.assertFalse(task.warnings)

    def test_missing_empty_and_unrecognized_objective_warn(self):
        for text in ('## Scope\nDo something\n', '## Objective\n\n## Scope\nOther\n',
                     '## Objective evidence\nHistorical result\n'):
            with self.subTest(text=text):
                task = self.parse('# Task 1.1 — Example\n' + text)
                self.assertEqual(task.objective, '')
                self.assertTrue(any('## Objective' in warning for warning in task.warnings))
