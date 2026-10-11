import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def test_exact_match_normalizes():
    """exact_match() ignores case, extra whitespace and a trailing period"""
    assert exact_match("order_status", "Order_Status ") is True, "case and trailing spaces shouldn't matter"
    assert exact_match("shipping", "shipping.") is True, "a trailing period shouldn't matter"
    assert exact_match("refund", "  REFUND\n") is True
    assert exact_match("refund", "complaint") is False, "different labels must not match"
    assert exact_match("refund", None) is False, "None never matches"
    assert exact_match("order status", "order   status") is True, "collapse repeated whitespace"


def test_judge_request_shape():
    """judge() uses structured outputs, an explicit effort and no sampling parameters"""
    _fresh()
    v = judge(anthropic.Anthropic(), "Must mention replacement.", "Torn jacket?", "We'll send a replacement.")
    assert v == {"pass": True, "reason": "The answer mentions replacement."}, f"got {v!r}"
    p = _sim.last_request()
    assert p["model"] == JUDGE_MODEL and p["max_tokens"] == JUDGE_MAX_TOKENS, "use JUDGE_MODEL and JUDGE_MAX_TOKENS"
    oc = p.get("output_config", {})
    assert oc.get("format") == {"type": "json_schema", "schema": JUDGE_SCHEMA}, f"use output_config.format with JUDGE_SCHEMA, got {oc}"
    assert oc.get("effort") == "low", "set effort explicitly (low) for a narrow rubric judge"
    assert "temperature" not in p, "don't send temperature"
    content = p["messages"][-1]["content"]
    assert content == "Rubric:\nMust mention replacement.\n\nQuestion:\nTorn jacket?\n\nAnswer:\nWe'll send a replacement.\n\nGrade the answer against the rubric.", \
        f"use the prompt format from the brief, got {content!r}"


def test_judge_fails_closed():
    """judge() treats unparseable or truncated replies as a fail with reason judge_error"""
    _fresh()
    _sim.queue("not json at all")
    v = judge(anthropic.Anthropic(), "Must mention x.", "q", "x")
    assert v == {"pass": False, "reason": "judge_error"}, f"bad JSON must not count as a pass: got {v!r}"
    _sim.queue(_sim.message(_sim.text('{"pass": tr'), stop_reason="max_tokens"))
    v = judge(anthropic.Anthropic(), "Must mention x.", "q", "x")
    assert v == {"pass": False, "reason": "judge_error"}, f"a truncated verdict is a judge error: got {v!r}"


def test_wilson_interval():
    """wilson_interval() matches the worked examples and handles the edges"""
    assert wilson_interval(46, 50) == (0.812, 0.968), f"46/50 -> (0.812, 0.968), got {wilson_interval(46, 50)!r}"
    assert wilson_interval(184, 200) == (0.874, 0.95), f"got {wilson_interval(184, 200)!r}"
    assert wilson_interval(10, 10) == (0.722, 1.0), f"10/10 is not 100%: got {wilson_interval(10, 10)!r}"
    lo, hi = wilson_interval(0, 10)
    assert lo == 0.0 and hi == 0.278, f"0/10 -> (0.0, 0.278), clamped at 0; got {(lo, hi)}"
    assert wilson_interval(0, 0) == (0.0, 1.0), "no trials means we know nothing: (0.0, 1.0)"


def test_run_eval_report():
    """run_eval() runs each case n times and reports pass rate, flaky cases and an interval"""
    _fresh()
    r = run_eval(CASES, system_under_test, 3, anthropic.Anthropic())
    assert isinstance(r, dict) and set(r) == {"trials", "passes", "pass_rate", "per_case", "flaky", "interval"}, f"got {r!r}"
    assert r["trials"] == 15 and r["passes"] == 13 and r["pass_rate"] == 0.867, f"13 of 15 trials pass, got {r['passes']}/{r['trials']}"
    assert r["per_case"] == {"intent-1": 3, "intent-2": 2, "intent-3": 3, "reply-1": 3, "reply-2": 2}, f"per_case: {r['per_case']}"
    assert r["flaky"] == ["intent-2", "reply-2"], f"flaky cases pass sometimes and fail sometimes, in case order: {r['flaky']}"
    assert r["interval"] == wilson_interval(13, 15), "interval is the Wilson interval over all trials"
    judge_calls = [c for c in _sim.calls if c["params"]["model"] == JUDGE_MODEL]
    assert len(judge_calls) == 6, f"only judge-graded cases call the judge: 2 cases x 3 runs = 6, got {len(judge_calls)}"


def test_run_eval_passes_run_index():
    """run_eval() passes the run number (0, 1, 2, ...) to generate"""
    seen = []

    def gen(text, run):
        seen.append(run)
        return "refund"

    r = run_eval([{"id": "a", "input": "x", "grader": "exact", "expected": "refund"}], gen, 4, anthropic.Anthropic())
    assert seen == [0, 1, 2, 3] and r["pass_rate"] == 1.0 and r["flaky"] == [], f"runs seen: {seen}, report {r}"
