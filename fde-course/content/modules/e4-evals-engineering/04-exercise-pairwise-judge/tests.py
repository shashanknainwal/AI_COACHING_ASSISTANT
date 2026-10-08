import json
import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _reply(winner):
    return json.dumps({"reasoning": "scripted", "winner": winner})


def test_schema():
    """PAIRWISE_SCHEMA asks for reasoning first, then a winner from a closed set"""
    s = PAIRWISE_SCHEMA
    props = s.get("properties", {})
    assert list(props) == ["reasoning", "winner"], f"reasoning must come before winner: {list(props)}"
    assert props["reasoning"].get("type") == "string"
    assert props["winner"].get("type") == "string" and props["winner"].get("enum") == ["first", "second", "tie"], \
        f"winner must be an enum of first/second/tie: {props['winner']}"
    assert s.get("type") == "object" and s.get("required") == ["reasoning", "winner"] and s.get("additionalProperties") is False


def test_build_prompt():
    """build_prompt() uses neutral position labels and no hint of which summary is new"""
    expected = (f"<rubric>\n{RUBRIC}\n</rubric>\n\n<clause>\nC.\n</clause>\n\n<response_1>\nX.\n</response_1>\n\n"
                "<response_2>\nY.\n</response_2>\n\n"
                'Compare the two summaries against the rubric. Explain your reasoning first, then answer "first", "second" or "tie".')
    got = build_prompt("C.", "X.", "Y.")
    assert got == expected, f"got:\n{got}"


def test_ask_judge_request():
    """ask_judge() sends one structured-output request to JUDGE_MODEL"""
    _fresh()
    _sim.queue(_reply("second"))
    got = ask_judge(anthropic.Anthropic(), "C.", "X.", "Y.")
    assert got == "second", f"expected 'second', got {got!r}"
    assert len(_sim.calls) == 1, f"one call expected, got {len(_sim.calls)}"
    p = _sim.last_request()
    assert p["model"] == JUDGE_MODEL and p["max_tokens"] >= 1024 and p.get("system") == JUDGE_SYSTEM, \
        "use JUDGE_MODEL, JUDGE_SYSTEM and max_tokens >= 1024"
    assert p["messages"] == [{"role": "user", "content": build_prompt("C.", "X.", "Y.")}]
    assert (p.get("output_config") or {}).get("format") == {"type": "json_schema", "schema": PAIRWISE_SCHEMA}, \
        "pass PAIRWISE_SCHEMA through output_config.format"
    assert "temperature" not in p, "sampling parameters are rejected on current models"


def test_ask_judge_errors():
    """A refusal or a truncated reply becomes "error" instead of a crash"""
    _fresh()
    _sim.queue(_sim.refusal())
    assert ask_judge(anthropic.Anthropic(), "C.", "X.", "Y.") == "error", "a refusal should return 'error'"
    _sim.queue(_sim.message(_sim.text('{"reasoning": "cut o'), stop_reason="max_tokens"))
    assert ask_judge(anthropic.Anthropic(), "C.", "X.", "Y.") == "error", "stop_reason max_tokens should return 'error'"


def test_judge_pair_runs_both_orders():
    """judge_pair() asks A-first, then B-first, and maps positions back to A/B"""
    _fresh()
    pair = {"id": "t", "clause": "C.", "a": "summary A", "b": "summary B", "human": "B"}
    _sim.queue(_reply("second"), _reply("first"))
    got = judge_pair(anthropic.Anthropic(), pair)
    assert got == {"verdict": "B", "consistent": True}, f"second-then-first both mean B: got {got}"
    reqs = _sim.requests()
    assert len(reqs) == 2, f"two calls per pair, got {len(reqs)}"
    assert reqs[0]["messages"][0]["content"] == build_prompt("C.", "summary A", "summary B"), "call 1 puts A first"
    assert reqs[1]["messages"][0]["content"] == build_prompt("C.", "summary B", "summary A"), "call 2 puts B first"


def test_judge_pair_inconsistent_and_error():
    """A flip between orders becomes a tie; any error makes the pair an error"""
    _fresh()
    pair = {"id": "t", "clause": "C.", "a": "A", "b": "B", "human": "A"}
    _sim.queue(_reply("first"), _reply("first"))
    got = judge_pair(anthropic.Anthropic(), pair)
    assert got == {"verdict": "tie", "consistent": False}, f"'first' both times is position bias: got {got}"
    _sim.queue(_reply("tie"), _reply("tie"))
    got = judge_pair(anthropic.Anthropic(), pair)
    assert got == {"verdict": "tie", "consistent": True}, f"tie in both orders is a consistent tie: got {got}"
    _sim.queue(_sim.refusal(), _reply("first"))
    got = judge_pair(anthropic.Anthropic(), pair)
    assert got == {"verdict": "error", "consistent": False}, f"got {got}"


def test_cohen_kappa():
    """cohen_kappa() handles three labels and the chance-agreement edge case"""
    r1 = ["A", "A", "B", "B", "tie", "A", "B", "B"]
    r2 = ["A", "B", "B", "B", "tie", "A", "B", "A"]
    # po = 6/8; pe = (3/8)(3/8) + (4/8)(4/8) + (1/8)(1/8) = 26/64; kappa = (0.75 - 0.40625) / 0.59375
    assert cohen_kappa(r1, r2) == 0.579, f"expected 0.579, got {cohen_kappa(r1, r2)}"
    assert cohen_kappa(["B", "B", "B"], ["B", "B", "B"]) == 1.0, "identical constant labels: pe is 1, so kappa is 1"
    assert cohen_kappa(["B", "B", "B", "B"], ["B", "B", "B", "A"]) == 0.0, "a judge that always says B has no skill"


def test_calibrate_saltmarsh():
    """calibrate() finds the judge agrees 80% of the time but flips order too often to trust"""
    _fresh()
    got = calibrate(anthropic.Anthropic(), PAIRS)
    assert got == {"n": 10, "errors": 0, "agreement": 0.8, "kappa": 0.688, "consistency": 0.7, "trusted": False,
                   "reasons": ["position consistency 0.700 below 0.8"], "disagreements": ["P-03", "P-07"]}, f"got {got}"
    assert len(_sim.calls) == 20, f"two calls per pair: expected 20, got {len(_sim.calls)}"


def test_calibrate_skips_errors():
    """Errors are counted but left out of every rate"""
    _fresh()
    pairs = [{"id": "x1", "clause": "C.", "a": "a", "b": "b", "human": "A"},
             {"id": "x2", "clause": "C.", "a": "a", "b": "b", "human": "B"}]
    _sim.queue(_reply("first"), _reply("second"), _sim.refusal(), _reply("first"))
    got = calibrate(anthropic.Anthropic(), pairs, min_kappa=0.6, min_consistency=0.8)
    assert got and got["n"] == 1 and got["errors"] == 1, f"got {got}"
    assert got["agreement"] == 1.0 and got["consistency"] == 1.0 and got["disagreements"] == [], f"got {got}"
