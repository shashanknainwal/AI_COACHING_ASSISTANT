import json
import anthropic
from anthropic import _sim


def test_rule_category():
    """rule_category() uses the first matching keyword, case-insensitively"""
    assert rule_category("Please resend INVOICE 12") == "billing"
    assert rule_category("Refund for the tracking number mixup") == "billing", "'refund' comes before 'tracking number' in RULES"
    assert rule_category("Valve hisses") is None, "no keyword -> None"


def test_chunks():
    """chunks() splits into consecutive lists"""
    assert chunks([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]], f"got {chunks([1, 2, 3, 4, 5], 2)}"
    assert chunks([], 3) == [], "empty input gives []"


def test_build_prompt():
    """build_prompt() is the header plus numbered lines"""
    got = build_prompt([(3, "Valve hisses"), (7, "Call me")])
    assert got == PROMPT_HEADER + "\n3. Valve hisses\n7. Call me", f"got {got!r}"


def test_schema():
    """BATCH_SCHEMA describes results with an integer index and enum category"""
    s = BATCH_SCHEMA
    assert s.get("type") == "object" and s.get("additionalProperties") is False and s.get("required") == ["results"], \
        "top level: object, required ['results'], additionalProperties False"
    item = s["properties"]["results"]["items"]
    assert item["properties"]["index"] == {"type": "integer"}, "index should be {'type': 'integer'}"
    assert item["properties"]["category"].get("enum") == CATEGORIES, "category should use enum CATEGORIES"
    assert sorted(item.get("required", [])) == ["category", "index"] and item.get("additionalProperties") is False


def _fresh():
    # Clear recorded calls and queued replies but keep the exercise's responder.
    _sim.calls.clear()
    _sim._queue.clear()


def test_categorize_sample_and_call_count():
    """Rules label 4 tickets; the other 8 go to Claude in 2 batches of 4"""
    _fresh()
    got = categorize(anthropic.Anthropic(), TICKETS, batch_size=4)
    want = ["billing", "product defect", "shipping", "billing", "product defect", "account access",
            "other", "shipping", "billing", "account access", "product defect", "other"]
    assert got == want, f"expected {want}, got {got}"
    assert len(_sim.calls) == 2, f"expected exactly 2 API calls (8 unlabeled tickets / batch 4), got {len(_sim.calls)}"


def test_request_parameters():
    """Each request uses the model, system prompt, structured outputs and only unlabeled tickets"""
    _sim.calls.clear()
    categorize(anthropic.Anthropic(), TICKETS, batch_size=10)
    assert len(_sim.calls) == 1, f"8 unlabeled tickets with batch_size=10 is 1 call, got {len(_sim.calls)}"
    req = _sim.last_request()
    assert req["model"] == "claude-opus-5-5" and req["max_tokens"] >= 2048 and req.get("system") == SYSTEM_PROMPT
    fmt = (req.get("output_config") or {}).get("format") or {}
    assert fmt.get("type") == "json_schema" and fmt.get("schema") == BATCH_SCHEMA, "use output_config with BATCH_SCHEMA"
    prompt = req["messages"][0]["content"]
    assert "1. The relief valve" in prompt, "tickets should keep their original index in the prompt"
    assert "invoice 4471" not in prompt, "tickets labeled by rules must not be sent to Claude"


def test_matches_by_index_and_validates():
    """Results are matched by index; unknown indexes/categories are ignored; missing ones become 'other'"""
    _fresh()
    _sim.queue(json.dumps({"results": [
        {"index": 2, "category": "shipping"},
        {"index": 99, "category": "billing"},
        {"index": 0, "category": "made-up"},
    ]}))
    got = categorize(anthropic.Anthropic(), ["valve hisses", "need help", "late pallet"], batch_size=10)
    assert got == ["other", "other", "shipping"], f"expected ['other', 'other', 'shipping'], got {got}"


def test_failed_batch_falls_back():
    """A truncated or refused batch labels its tickets 'other' without crashing"""
    _fresh()
    _sim.queue(_sim.message(_sim.text('{"results": [{"index": 0'), stop_reason="max_tokens"))
    _sim.queue(json.dumps({"results": [{"index": 1, "category": "shipping"}]}))
    got = categorize(anthropic.Anthropic(), ["a", "b"], batch_size=1)
    assert got == ["other", "shipping"], f"batch 1 failed -> 'other'; batch 2 ok; got {got}"


def test_no_calls_when_rules_cover_everything():
    """Claude isn't called when rules label every ticket"""
    _fresh()
    got = categorize(anthropic.Anthropic(), ["invoice copy please", "password reset"], batch_size=5)
    assert got == ["billing", "account access"], f"got {got}"
    assert len(_sim.calls) == 0, f"expected no API calls, got {len(_sim.calls)}"


def test_estimate_cost():
    """estimate_cost() matches the lesson's table"""
    assert estimate_cost(50_000, 1) == 107.0, f"got {estimate_cost(50_000, 1)}"
    assert estimate_cost(50_000, 25) == 30.2, f"got {estimate_cost(50_000, 25)}"
    assert estimate_cost(10, 3, tokens_per_ticket=50, overhead=100, output_per_ticket=10) == 0.0056, \
        f"4 calls: input 900, output 100 -> 0.0056; got {estimate_cost(10, 3, tokens_per_ticket=50, overhead=100, output_per_ticket=10)}"
    assert estimate_cost(0, 10) == 0.0
