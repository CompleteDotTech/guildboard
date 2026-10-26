"""Research invariants and negative cases; these do not test Guildboard."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("t11_baseline", ROOT / "scripts/research/t11-baseline.py")
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


class BaselineTests(unittest.TestCase):
    def test_underload_has_no_loss_and_service_time_latency(self):
        result = baseline.queue_model(100, 60, 4, 128)
        self.assertEqual(result["offered"], 6000)
        self.assertEqual(result["rejected"], 0)
        self.assertEqual(result["accepted_virtual_latency_ms"]["p99"], 4)

    def test_overload_preserves_accounting_and_bound(self):
        result = baseline.queue_model(1000, 10, 4, 128)
        self.assertGreater(result["rejected"], 0)
        self.assertLessEqual(result["peak_outstanding"], 128)
        self.assertEqual(result["offered"], result["rejected"] + result["accepted_and_eventually_completed"])

    def test_invalid_and_unbounded_configs_fail(self):
        for args in [(0, 1, 4, 128), (100, 1, -1, 128), (100, 1, 4, 0),
                     (100, 1, 4, True), (float("nan"), 1, 4, 128), (1000, 1000, 4, 128)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                baseline.queue_model(*args)

    def test_wrong_sequence_fails_even_with_matching_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong-sequence"
            path.write_bytes(baseline.record(1) + baseline.record(0))
            with self.assertRaisesRegex(ValueError, "sequence"):
                baseline.verify(path, baseline.digest(path), 2)

    def test_local_copy_corruption_and_owned_child_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            result = baseline.file_experiment(Path(directory))
        self.assertEqual(result["restored_records"], 300)
        self.assertTrue(result["truncated_copy_rejected"])
        self.assertEqual(result["abrupt_owned_child_exit_code"], 23)
        self.assertEqual(result["abrupt_child_prefix_verified_records"], 32)


if __name__ == "__main__":
    unittest.main()
