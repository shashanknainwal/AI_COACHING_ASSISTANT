import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from app.mcp_server import Server
from evals.calibrate_judge import calibration_report, majority
from evals.run_evals import deterministic_checks
from labs.common import accuracy_report

ROOT = Path(__file__).resolve().parent.parent


class MCPServerTests(unittest.TestCase):
    def setUp(self):
        self.s = Server(allow_writes=False)

    def test_initialize_and_list(self):
        r = self.s.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", r["result"]["capabilities"])
        tools = self.s.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["get_order", "search_knowledge_base", "create_escalation"])
        self.assertIn("inputSchema", tools[0])

    def test_notification_gets_no_reply(self):
        self.assertIsNone(self.s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_call_and_errors(self):
        r = self.s.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                           "params": {"name": "get_order", "arguments": {"order_id": "QF-1003"}}})
        self.assertFalse(r["result"]["isError"])
        self.assertEqual(json.loads(r["result"]["content"][0]["text"])["status"], "processing")
        w = self.s.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                           "params": {"name": "create_escalation", "arguments": {"order_id": "QF-1", "reason": "x"}}})
        self.assertTrue(w["result"]["isError"])  # writes refused by default
        self.assertEqual(self.s.handle({"jsonrpc": "2.0", "id": 5, "method": "nope"})["error"]["code"], -32601)
        self.assertEqual(json.loads(self.s.handle_line("{not json"))["error"]["code"], -32700)

    def test_stdio_round_trip(self):
        lines = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                 {"jsonrpc": "2.0", "method": "notifications/initialized"},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
        out = subprocess.run([sys.executable, "-m", "app.mcp_server"], cwd=ROOT, text=True, capture_output=True,
                             input="\n".join(json.dumps(l) for l in lines) + "\n", timeout=30,
                             env={**os.environ, "PYTHONPATH": str(ROOT)})
        replies = [json.loads(l) for l in out.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2])

    def test_mcp_client_backend(self):
        from app.mcp_client import MCPTools
        with MCPTools(env={**os.environ, "PYTHONPATH": str(ROOT)}) as tools:
            self.assertEqual(len(tools.definitions), 3)
            text, is_error = tools.call("get_order", {"order_id": "QF-9999"})
            self.assertTrue(is_error)


class CheckTests(unittest.TestCase):
    def test_deterministic_checks(self):
        case = {"checks": {"must_call": ["get_order"], "must_include_any": [["final sale", "cannot be returned"]],
                           "must_not_include": ["refund confirmed"]}}
        self.assertEqual(deterministic_checks(case, "It is FINAL SALE.", ["get_order"]), [])
        failed = deterministic_checks(case, "Refund confirmed.", [])
        self.assertEqual(len(failed), 3)

    def test_calibration_report(self):
        human = {"a": "pass", "b": "fail", "c": "pass", "d": "fail"}
        runs = [{"a": "pass", "b": "fail", "c": "fail", "d": "fail"},
                {"a": "pass", "b": "fail", "c": "pass", "d": "fail"},
                {"a": "pass", "b": "fail", "c": "fail", "d": "fail"}]
        rep = calibration_report(list(human), human, runs)
        self.assertEqual(rep["disagreements"], ["c"])
        self.assertEqual(rep["unstable_items"], ["c"])
        self.assertAlmostEqual(rep["judge_self_agreement"], 0.75)
        self.assertEqual(majority(["pass", "fail"]), "fail")

    def test_accuracy_report(self):
        labels = {"t1": "a", "t2": "b", "t3": "c"}
        rep = accuracy_report(labels, [{"t1": "a", "t2": "b", "t3": None}, {"t1": "a", "t2": "c", "t3": "a"}])
        self.assertEqual(rep["per_run"][0]["correct"], 2)
        self.assertEqual(rep["per_run"][0]["missing"], 1)
        self.assertEqual(rep["flipped_tickets"], ["t2"])
        self.assertEqual(rep["always_wrong"], [])


if __name__ == "__main__":
    unittest.main()
