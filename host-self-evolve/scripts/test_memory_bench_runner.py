import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("memory_bench_runner.py")
spec = importlib.util.spec_from_file_location("memory_bench_runner", MODULE_PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class MemoryBenchReportCardTests(unittest.TestCase):
    def _card(self, raw):
        return runner.build_report_card("run", "time", 50, 40, 12, 10, raw,
                                        "judge")

    def test_exact_row_count_and_order(self):
        rows = [line for line in self._card(1.2).splitlines()
                if line.startswith("|") and line.split("|")[1].strip().isdigit()]
        self.assertEqual(11, len(rows))
        expected = ["run_id", "timestamp", "host", "skill_version", "model", "judge",
                    "recall_total", "consistency_total", "compliance_total",
                    "weighted_score", "target_met"]
        self.assertEqual(expected, [row.split("|")[2].strip() for row in rows])

    def test_threshold_boundary_and_normalization(self):
        self.assertEqual(60.0, runner.normalize_weighted(1.2))
        self.assertIn("✅ ≥ 60", self._card(1.2))
        self.assertIn("❌ < 60", self._card(1.199))
        self.assertIn("raw=1.200", self._card(1.2))
        self.assertIn("normalized=60.0", self._card(1.2))

    def test_weighted_score_uses_zero_to_two_scale(self):
        weights = {"recall": 0.35, "consistency": 0.25,
                   "compliance": 0.30, "token_economy": 0.10}
        perfect = runner.compute_weighted_score(weights, 50, 50, 15, 15, 12, 12, 100)
        self.assertAlmostEqual(2.0, perfect)
        expected = 2 * (0.35 * 0.8 + 0.25 * 1 + 0.30 * 1 + 0.10 * 1)
        actual = runner.compute_weighted_score(weights, 40, 50, 15, 15, 12, 12, 100)
        self.assertAlmostEqual(expected, actual)
        self.assertGreaterEqual(runner.normalize_weighted(actual), 60)

    def test_report_discloses_actual_runtime(self):
        card = self._card(1.2)
        self.assertIn("MiniMax via mmx text chat", card)
        self.assertIn("MiniMax via mmx dual-order judge", card)

    def test_dynamic_version(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "SKILL.md"
            path.write_text('---\nmetadata:\n  version: "9.8.7"\n---\n')
            self.assertEqual("v9.8.7", runner.read_skill_version(path))


if __name__ == "__main__":
    unittest.main()
