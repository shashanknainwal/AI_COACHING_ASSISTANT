import json
import tempfile
import unittest
from pathlib import Path

from evals.gate import evaluate_gate, main

POLICY = {"mode": "point", "max_drop": 0.05, "min_pass_rate": 0.7, "max_error_rate": 0.1,
          "max_cost_per_case_usd": 0.03, "max_p95_latency_s": 30, "critical_must_pass_every_run": True}


def result(rate, lo=None, hi=None, critical=(), err=0.0, cost=0.01, p95=5.0, trials=36):
    return {"pass_rate": rate, "summary": {"wilson_95": [lo if lo is not None else rate - 0.1,
                                                         hi if hi is not None else min(1.0, rate + 0.1)],
                                           "trials": trials},
            "critical_failures": list(critical), "error_rate": err,
            "cost": {"agent_per_case_usd": cost}, "latency_s": {"p95": p95}}


class GateTests(unittest.TestCase):
    def test_passes_when_equal_to_baseline(self):
        ok, failures, _ = evaluate_gate(result(0.85), {"pass_rate": 0.85}, POLICY)
        self.assertTrue(ok, failures)

    def test_point_mode_fails_on_big_drop(self):
        ok, failures, _ = evaluate_gate(result(0.76), {"pass_rate": 0.85}, POLICY)
        self.assertFalse(ok)
        self.assertTrue(any("regression" in f for f in failures))

    def test_point_mode_tolerates_small_drop(self):
        ok, _, _ = evaluate_gate(result(0.81), {"pass_rate": 0.85}, POLICY)
        self.assertTrue(ok)

    def test_interval_mode_only_fails_when_whole_interval_below(self):
        policy = {**POLICY, "mode": "interval"}
        ok, _, notes = evaluate_gate(result(0.76, 0.6, 0.88), {"pass_rate": 0.85}, policy)
        self.assertTrue(ok)
        self.assertTrue(any("within noise" in n for n in notes))
        ok, failures, _ = evaluate_gate(result(0.72, 0.6, 0.82), {"pass_rate": 0.85}, policy)
        self.assertFalse(ok, failures)

    def test_floor_critical_errors_cost_latency(self):
        self.assertFalse(evaluate_gate(result(0.6), {"pass_rate": None}, POLICY)[0])
        self.assertFalse(evaluate_gate(result(0.9, critical=["g07"]), {"pass_rate": 0.9}, POLICY)[0])
        self.assertFalse(evaluate_gate(result(0.9, err=0.2), {"pass_rate": 0.9}, POLICY)[0])
        self.assertFalse(evaluate_gate(result(0.9, cost=0.05), {"pass_rate": 0.9}, POLICY)[0])
        self.assertFalse(evaluate_gate(result(0.9, p95=45), {"pass_rate": 0.9}, POLICY)[0])

    def test_no_baseline_checks_absolute_only(self):
        ok, _, notes = evaluate_gate(result(0.8), {"pass_rate": None}, POLICY)
        self.assertTrue(ok)
        self.assertTrue(any("no baseline" in n for n in notes))

    def test_missing_pass_rate_fails(self):
        ok, failures, _ = evaluate_gate({"pass_rate": None}, {"pass_rate": 0.8}, POLICY)
        self.assertFalse(ok)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "policy.json").write_text(json.dumps(POLICY))
            (d / "base.json").write_text(json.dumps({"pass_rate": 0.9}))
            (d / "good.json").write_text(json.dumps(result(0.9)))
            (d / "bad.json").write_text(json.dumps(result(0.7)))
            args = ["--baseline", str(d / "base.json"), "--policy", str(d / "policy.json")]
            self.assertEqual(main(["--current", str(d / "good.json"), *args]), 0)
            self.assertEqual(main(["--current", str(d / "bad.json"), *args]), 1)


if __name__ == "__main__":
    unittest.main()
