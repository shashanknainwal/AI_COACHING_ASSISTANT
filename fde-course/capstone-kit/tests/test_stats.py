import unittest

from evals.stats import cohen_kappa, confusion, percentile, summarize_runs, wilson_interval


class WilsonTests(unittest.TestCase):
    def test_known_value(self):
        lo, hi = wilson_interval(27, 30)
        self.assertAlmostEqual(lo, 0.7438, places=3)
        self.assertAlmostEqual(hi, 0.9654, places=3)

    def test_zero_successes_has_nonzero_upper_bound(self):
        lo, hi = wilson_interval(0, 40)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.0876, places=3)

    def test_all_successes_and_bounds(self):
        lo, hi = wilson_interval(20, 20)
        self.assertLess(lo, 1.0)
        self.assertEqual(hi, 1.0)

    def test_empty_sample(self):
        self.assertEqual(wilson_interval(0, 0), (0.0, 1.0))

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            wilson_interval(5, 3)

    def test_narrows_with_more_data(self):
        small = wilson_interval(8, 10)
        big = wilson_interval(800, 1000)
        self.assertLess(big[1] - big[0], small[1] - small[0])


class KappaTests(unittest.TestCase):
    def test_hand_computed(self):
        a = ["pass", "pass", "fail", "fail"]
        b = ["pass", "fail", "fail", "fail"]
        self.assertAlmostEqual(cohen_kappa(a, b), 0.5)

    def test_perfect_and_chance(self):
        self.assertEqual(cohen_kappa(["p", "f", "p"], ["p", "f", "p"]), 1.0)
        # always-pass judge vs mixed human: agreement 55% but kappa 0
        human = ["pass"] * 11 + ["fail"] * 9
        judge = ["pass"] * 20
        self.assertAlmostEqual(cohen_kappa(human, judge), 0.0)

    def test_worse_than_chance_is_negative(self):
        self.assertLess(cohen_kappa(["p", "f", "p", "f"], ["f", "p", "f", "p"]), 0)

    def test_single_label_degenerate_case(self):
        self.assertEqual(cohen_kappa(["p", "p"], ["p", "p"]), 1.0)

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            cohen_kappa(["p"], ["p", "f"])

    def test_confusion(self):
        self.assertEqual(confusion(["p", "f"], ["p", "p"]), {("p", "p"): 1, ("f", "p"): 1})


class SummaryTests(unittest.TestCase):
    def test_percentile(self):
        self.assertEqual(percentile([1, 2, 3, 4, 5], 50), 3.0)
        self.assertAlmostEqual(percentile([1, 2, 3, 4], 95), 3.85)
        self.assertEqual(percentile([7], 95), 7.0)

    def test_summarize_runs_flaky_and_pass_all(self):
        runs = [{"a": True, "b": True, "c": False}, {"a": True, "b": False, "c": False}, {"a": True, "b": True}]
        s = summarize_runs(runs)
        self.assertEqual(s["trials"], 8)
        self.assertAlmostEqual(s["pass_rate"], 5 / 8)
        self.assertEqual(s["flaky_cases"], ["b"])
        self.assertEqual(s["pass_all_runs"], 1)
        self.assertAlmostEqual(s["min_run_rate"], 1 / 3)
        self.assertEqual(s["max_run_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
