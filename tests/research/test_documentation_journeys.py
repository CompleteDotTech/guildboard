import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('journeys', ROOT / 'scripts/research/audit_documentation_journeys.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class JourneyAuditTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'docs/research/documentation-journeys.json').read_text())

    def check_error(self, fragment):
        errors, _ = module.audit(ROOT, self.manifest)
        self.assertTrue(any(fragment in x for x in errors), errors)

    def test_real_snapshot(self):
        errors, counts = module.audit(ROOT, self.manifest)
        self.assertEqual(errors, [])
        self.assertEqual(sum(counts.values()), 12)
        self.assertGreater(counts['blocked'], 0)  # valid research does not mean usable journeys

    def test_missing_persona(self):
        self.manifest['journeys'].pop()
        self.check_error('all four')

    def test_duplicate_persona(self):
        self.manifest['journeys'].append(copy.deepcopy(self.manifest['journeys'][0]))
        self.check_error('duplicate')

    def test_evidence_drift(self):
        self.manifest['journeys'][0]['steps'][0]['evidence'][0]['sha256'] = '0' * 64
        self.check_error('evidence changed')

    def test_evidence_missing(self):
        self.manifest['journeys'][0]['steps'][0]['evidence'][0]['path'] = 'nonexistent.md'
        self.check_error('missing evidence')

    def test_traversal_and_absolute_paths(self):
        for path in ('../README.md', '/etc/passwd'):
            with self.subTest(path=path):
                self.manifest['journeys'][0]['steps'][0]['evidence'][0]['path'] = path
                self.check_error('escapes repository')

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'escape').symlink_to(ROOT / 'README.md')
            self.manifest['journeys'][0]['steps'][0]['evidence'][0]['path'] = 'escape'
            errors, _ = module.audit(root, self.manifest)
            self.assertIn('evidence path escapes repository', errors)

    def test_no_evidence_or_validation(self):
        step = self.manifest['journeys'][0]['steps'][0]
        step['evidence'] = []
        step['next_validation'] = ''
        self.check_error('requires evidence')
        self.check_error('missing next_validation')

    def test_malformed_shapes_fail_closed(self):
        for manifest in (None, [], {}, {'schema_version': 2}, {'schema_version': 1, 'journeys': None},
                         {'schema_version': 1, 'journeys': [None, {'persona': [], 'steps': [None]}]}):
            with self.subTest(manifest=manifest):
                errors, _ = module.audit(ROOT, manifest)
                self.assertTrue(errors)

    def test_unknown_state(self):
        self.manifest['journeys'][0]['steps'][0]['state'] = 'verified'
        self.check_error('unknown step state')


if __name__ == '__main__':
    unittest.main()
