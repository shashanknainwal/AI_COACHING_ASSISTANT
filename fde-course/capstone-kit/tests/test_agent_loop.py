import json
import unittest

from app.agent import run_agent
from app.costs import BudgetExceeded, CostMeter
from app.llm import call
from app.tools import LocalTools
from tests.fakes import FakeClient, response, text, thinking, tool_use


class AgentLoopTests(unittest.TestCase):
    def test_tool_round_trip_appends_content_unmodified(self):
        first = [thinking(), tool_use("tu_1", "get_order", {"order_id": "QF-1002"})]
        client = FakeClient([response(first, "tool_use"), response([text("It shipped.")], "end_turn")])
        res = run_agent("Where is QF-1002?", client=client, tools=LocalTools())
        self.assertEqual(res.status, "ok")
        self.assertEqual(res.text, "It shipped.")
        second = client.requests[1]["messages"]
        self.assertIs(second[1]["content"], first)          # same list, thinking block kept
        result = second[2]["content"][0]
        self.assertEqual(result["tool_use_id"], "tu_1")
        self.assertEqual(json.loads(result["content"])["status"], "shipped")
        self.assertEqual(client.requests[0]["output_config"], {"effort": "low"})
        self.assertIn("cache_control", client.requests[0]["system"][0])

    def test_refusal_runs_no_tools(self):
        client = FakeClient([response([tool_use("tu_1", "create_escalation", {"order_id": "x", "reason": "y"})], "refusal")])
        res = run_agent("hi", client=client)
        self.assertEqual(res.status, "refused")
        self.assertEqual(res.tool_calls, [])

    def test_max_tokens_with_tool_use_runs_nothing(self):
        client = FakeClient([response([tool_use("tu_1", "get_order", {"order_id": "QF-"})], "max_tokens")])
        res = run_agent("hi", client=client)
        self.assertEqual(res.status, "truncated")
        self.assertEqual(res.tool_calls, [])

    def test_pause_turn_resends_without_extra_user_message(self):
        paused = [text("working...")]
        client = FakeClient([response(paused, "pause_turn"), response([text("done")], "end_turn")])
        res = run_agent("hi", client=client)
        self.assertEqual(res.status, "ok")
        msgs = client.requests[1]["messages"]
        self.assertEqual(msgs[-1], {"role": "assistant", "content": paused})

    def test_escalation_denied_by_default(self):
        client = FakeClient([response([tool_use("tu_1", "create_escalation", {"order_id": "QF-1001", "reason": "dispute"})], "tool_use"),
                             response([text("A person will review it.")], "end_turn")])
        res = run_agent("person please", client=client)
        self.assertTrue(res.tool_calls[0]["is_error"])
        self.assertTrue(client.requests[1]["messages"][2]["content"][0]["is_error"])

    def test_max_turns(self):
        loop = [response([tool_use(f"tu_{i}", "get_order", {"order_id": "QF-1001"})], "tool_use") for i in range(3)]
        res = run_agent("hi", client=FakeClient(loop), max_turns=3)
        self.assertEqual(res.status, "max_turns")

    def test_budget_stops_the_loop(self):
        big = response([tool_use("tu_1", "get_order", {"order_id": "QF-1001"})], "tool_use",
                       input_tokens=2_000_000, output_tokens=0)
        with self.assertRaises(BudgetExceeded):
            run_agent("hi", client=FakeClient([big]), meter=CostMeter(budget_usd=0.05))

    def test_call_parses_json_only_on_clean_stop(self):
        ok = call(FakeClient([response([text('{"category": "billing"}')], "end_turn")]),
                  system="s", user="u", schema={"type": "object"})
        self.assertEqual(ok.parsed, {"category": "billing"})
        refused = call(FakeClient([response([text("{")], "refusal")]), system="s", user="u", schema={"type": "object"})
        self.assertTrue(refused.refused)
        self.assertIsNone(refused.parsed)


if __name__ == "__main__":
    unittest.main()
