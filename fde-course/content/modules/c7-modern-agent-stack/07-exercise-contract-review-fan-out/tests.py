import json
import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _worker_calls():
    return [c for c in _sim.calls if c["params"]["model"] == WORKER_MODEL]


def _lead_calls():
    return [c for c in _sim.calls if c["params"]["model"] == LEAD_MODEL]


def test_worker_request_isolated():
    """Each worker request holds exactly one contract, on Haiku 5.5 at low effort"""
    p = worker_request("CC-104", CONTRACTS["CC-104"])
    assert isinstance(p, dict), "worker_request should return a dict of request parameters."
    assert p.get("model") == WORKER_MODEL and p.get("system") == WORKER_SYSTEM, "Use WORKER_MODEL and WORKER_SYSTEM."
    oc = p.get("output_config") or {}
    assert oc.get("effort") == "low", "Haiku 5.5 thinks at medium by default. Set effort to 'low' explicitly for this extraction."
    assert (oc.get("format") or {}).get("type") == "json_schema" and oc["format"].get("schema") == REPORT_SCHEMA, \
        "Ask for structured output: output_config.format with type json_schema and REPORT_SCHEMA."
    assert p.get("max_tokens", 0) >= 1000, "max_tokens covers thinking too. Leave room (at least 1000)."
    body = json.dumps(p["messages"])
    assert "CC-104" in body and "Liability" in body, "Put the full contract text in the user message."
    others = [c for c in CONTRACTS if c != "CC-104" and c in body]
    assert not others, f"Context isolation: the worker request mentions other contracts {others}."


def test_worker_success_and_usage():
    """A worker returns a validated report and its token usage"""
    _fresh()
    r = run_worker(client, "CC-102", CONTRACTS["CC-102"])
    assert isinstance(r, dict) and r.get("status") == "ok", f"CC-102 should succeed. Got {r}"
    assert r["report"] == TERMS["CC-102"] and r["error"] is None, "Parse the JSON text into the report."
    resp = _worker_calls()[-1]["response"]["usage"]
    assert r["usage"] == {"input_tokens": resp["input"], "output_tokens": resp["output"]}, "usage should come from response.usage."


def test_budget_gate():
    """A contract over the worker budget is skipped before any model call"""
    _fresh()
    r = run_worker(client, "CC-113", CONTRACTS["CC-113"])
    assert (r or {}).get("status") == "skipped" and r.get("error") == "over_budget", \
        f"CC-113 carries a huge rate-table appendix. Count tokens first and skip it when over budget. Got {r}"
    assert not _worker_calls(), "The budget check must happen before messages.create (use client.messages.count_tokens)."
    assert r["usage"] == {"input_tokens": 0, "output_tokens": 0}, "A skipped worker spent nothing."


def test_failure_isolated():
    """A worker whose API calls fail returns a failed result instead of raising"""
    _fresh()
    try:
        r = run_worker(client, "CC-117", CONTRACTS["CC-117"])
    except anthropic.APIError as e:
        raise AssertionError(f"run_worker raised {type(e).__name__}. Catch anthropic.APIError and return a failed result.")
    assert (r or {}).get("status") == "failed" and r.get("error") == "OverloadedError", f"Report the exception class name. Got {r}"
    assert len(_worker_calls()) == 3, "Let the SDK's own retries run (3 attempts) before giving up; don't add a second retry loop."


def test_bad_report_rejected():
    """A report about the wrong contract is rejected"""
    _fresh()
    _sim.queue(json.dumps(TERMS["CC-101"]))
    r = run_worker(client, "CC-104", CONTRACTS["CC-104"])
    assert (r or {}).get("status") == "failed" and r.get("error") == "bad_report", \
        "If the report's contract_id isn't the contract this worker was given, it's a bad_report."


def test_assess_rules():
    """The risk rules are applied in code"""
    base = {"liability_cap_eur": 100000, "termination_notice_days": 30, "auto_renew": False, "fuel_surcharge_cap_pct": 10}
    assert assess(base) == [], "A contract inside every rule has no flags."
    assert assess(dict(base, liability_cap_eur=40000)) == ["low_liability_cap"], "Liability cap under EUR 50,000: low_liability_cap."
    assert assess(dict(base, termination_notice_days=120)) == ["long_notice"], "Notice over 90 days: long_notice."
    assert assess(dict(base, auto_renew=True, termination_notice_days=75)) == ["auto_renew_trap"], "Auto-renew with notice over 60 days (75 isn't over 90)."
    assert assess(dict(base, fuel_surcharge_cap_pct=18.0)) == ["high_fuel_cap"], "Fuel cap over 15%: high_fuel_cap."
    assert assess(dict(base, liability_cap_eur=None)) == [], "A missing term (None) isn't a flag."


def test_review_merge_and_lead():
    """The review merges results, reports gaps, and the lead never sees contract text"""
    _fresh()
    review = run_review(client, CONTRACTS)
    assert isinstance(review, dict) and isinstance(review.get("merged"), dict), "run_review should return a dict with 'merged'."
    m = review["merged"]
    assert m.get("failed") == ["CC-117"] and m.get("skipped") == ["CC-113"], f"Failed and skipped contracts belong in their own lists. Got {m.get('failed')}, {m.get('skipped')}"
    expected = {c: assess(TERMS[c]) for c in TRUTH_RISKY if c not in ("CC-113", "CC-117")}
    assert m.get("flagged") == expected, "flagged should map each risky reviewed contract to its flags."
    assert m.get("coverage") == 0.9, "coverage = reviewed / total = 18 / 20."
    leads = _lead_calls()
    assert len(leads) == 1, f"Make exactly one lead call. Got {len(leads)}."
    lp = leads[0]["params"]
    assert (lp.get("output_config") or {}).get("effort"), "Set effort explicitly on the Opus 5.5 lead call."
    lead_text = json.dumps(lp["messages"])
    assert "Carrier shall perform" not in lead_text and "APPENDIX" not in lead_text, "The lead sees findings, never contract text."
    assert "CC-117" in lead_text and "CC-113" in lead_text, "Tell the lead which contracts weren't reviewed."
    assert review.get("summary"), "summary is the lead's text."


def test_tokens_and_cost():
    """Token totals and cost add up from the recorded usage"""
    _fresh()
    review = run_review(client, CONTRACTS)
    w_in = sum(c["response"]["usage"]["input"] for c in _worker_calls() if "response" in c)
    w_out = sum(c["response"]["usage"]["output"] for c in _worker_calls() if "response" in c)
    assert review["usage"]["workers"] == {"input_tokens": w_in, "output_tokens": w_out}, "Sum worker usage across every successful worker."
    lead = _lead_calls()[-1]["response"]["usage"]
    assert review["usage"]["lead"] == {"input_tokens": lead["input"], "output_tokens": lead["output"]}
    expect = (w_in * 0.10 + w_out * 0.50 + lead["input"] * 4.0 + lead["output"] * 20.0) / 1_000_000
    assert abs(review["cost_usd"] - expect) < 1e-9, f"Price each model at its own rate (PRICES). Expected {expect:.6f}, got {review['cost_usd']}"
    assert abs(cost_usd(LEAD_MODEL, {"input_tokens": 1_000_000, "output_tokens": 0}) - 4.0) < 1e-9, "Prices are per million tokens."


def test_compare_with_baseline():
    """The comparison reports cost, recall and what each approach failed to review"""
    _fresh()
    review = run_review(client, CONTRACTS)
    baseline = run_single_agent(client)
    c = compare(review, baseline, TRUTH_RISKY)
    assert isinstance(c, dict) and {"fanout", "baseline"} <= set(c), "Return {'fanout': {...}, 'baseline': {...}}."
    assert c["fanout"]["cost_usd"] < c["baseline"]["cost_usd"], "In this simulation the fan-out should cost less."
    assert abs(c["fanout"]["recall"] - 10 / 11) < 1e-9, "recall = risky contracts flagged / all risky contracts (TRUTH_RISKY)."
    assert abs(c["baseline"]["recall"] - 9 / 11) < 1e-9, "Apply assess() to the baseline's reports too."
    assert c["fanout"]["unreviewed_reported"] == ["CC-113", "CC-117"], "The fan-out knows exactly what it didn't review."
    assert c["baseline"].get("silently_missing") == ["CC-109", "CC-110", "CC-111"], \
        "Find the contracts the baseline never reported on: that's the failure it doesn't tell you about."
