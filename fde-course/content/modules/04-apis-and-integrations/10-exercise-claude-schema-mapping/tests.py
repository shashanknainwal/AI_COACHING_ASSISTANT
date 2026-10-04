import json
import anthropic
from anthropic import _sim


def _m(source, target, conf, transform="none"):
    return {"source": source, "target": target, "transform": transform, "confidence": conf}


def test_schema():
    """MAPPING_SCHEMA constrains targets and transforms with enums"""
    s = MAPPING_SCHEMA
    assert s.get("type") == "object" and s.get("additionalProperties") is False and s.get("required") == ["mappings"], \
        "top level: object, required ['mappings'], additionalProperties False"
    item = s["properties"]["mappings"]["items"]
    props = item["properties"]
    assert props["target"].get("enum") == TARGET_NAMES, "target should use enum TARGET_NAMES"
    assert props["transform"].get("enum") == TRANSFORMS, "transform should use enum TRANSFORMS"
    assert props["confidence"].get("type") == "number" and props["source"].get("type") == "string"
    assert sorted(item.get("required", [])) == ["confidence", "source", "target", "transform"] and item.get("additionalProperties") is False


def test_build_prompt():
    """build_prompt() includes the samples and every target field with its description"""
    p = build_prompt(POLAR_SAMPLES)
    assert isinstance(p, str), "return a string"
    assert '"trk_no": "PX-88213"' in p, "include the sample records as JSON (json.dumps)"
    for f in TARGET_FIELDS:
        assert f"- {f['name']}: {f['description']}" in p, f"missing target line for {f['name']}"


def test_suggest_mappings_request():
    """suggest_mappings() uses the model, system prompt and structured outputs"""
    _sim.calls.clear()
    out = suggest_mappings(anthropic.Anthropic(), POLAR_SAMPLES)
    assert isinstance(out, dict) and "mappings" in out, "return the parsed dict"
    req = _sim.last_request()
    assert req["model"] == "claude-opus-5-5" and req["max_tokens"] >= 4096 and req.get("system") == SYSTEM_PROMPT
    fmt = (req.get("output_config") or {}).get("format") or {}
    assert fmt.get("type") == "json_schema" and fmt.get("schema") == MAPPING_SCHEMA, "use output_config with MAPPING_SCHEMA"
    assert req["messages"][0]["content"] == build_prompt(POLAR_SAMPLES), "send build_prompt(samples) as the user message"


def test_suggest_mappings_stop_reasons():
    """Truncated and refused responses raise ValueError"""
    for reply, msg in [(_sim.message(_sim.text('{"mappings": ['), stop_reason="max_tokens"), "truncated"), (_sim.refusal(), "refused")]:
        _sim.queue(reply)
        try:
            suggest_mappings(anthropic.Anthropic(), POLAR_SAMPLES)
        except ValueError as e:
            assert str(e) == msg, f"expected ValueError({msg!r}), got {str(e)!r}"
        else:
            raise AssertionError(f"expected ValueError({msg!r})")


def test_review_polar():
    """review() sorts Claude's suggestions for Polar Express into the right buckets"""
    r = review(json.loads(json.dumps(_SUGGESTIONS)), POLAR_SAMPLES)
    assert [m["source"] for m in r["accepted"]] == ["trk_no", "wt_kg", "recipient", "state", "last_event_ts"], \
        f"accepted (highest confidence first): {[m['source'] for m in r['accepted']]}"
    assert [m["source"] for m in r["needs_review"]] == ["dest_city"], f"needs_review: {[m['source'] for m in r['needs_review']]}"
    assert [(m["source"], why) for m, why in r["rejected"]] == [("amount", "unknown source field"), ("svc_level", "duplicate target")], \
        f"rejected: {[(m['source'], why) for m, why in r['rejected']]}"
    assert r["missing_required"] == ["charge"], f"missing_required: {r['missing_required']}"


def test_most_confident_claim_wins():
    """When two sources claim one target, the more confident one wins regardless of input order"""
    r = review({"mappings": [_m("svc_level", "status", 0.4), _m("state", "status", 0.9)]}, POLAR_SAMPLES)
    assert [m["source"] for m in r["accepted"]] == ["state"]
    assert [(m["source"], why) for m, why in r["rejected"]] == [("svc_level", "duplicate target")]


def test_threshold_and_review_claims_target():
    """Confidence equal to the threshold is accepted; needs-review mappings also claim their target"""
    r = review({"mappings": [_m("dest_city", "city", 0.8), _m("recipient", "customer_name", 0.5),
                             _m("trk_no", "customer_name", 0.3)]}, POLAR_SAMPLES)
    assert [m["source"] for m in r["accepted"]] == ["dest_city"], "0.8 >= 0.8 is accepted"
    assert [m["source"] for m in r["needs_review"]] == ["recipient"]
    assert [why for _, why in r["rejected"]] == ["duplicate target"], "customer_name is already claimed by the needs-review mapping"


def test_missing_required_order():
    """missing_required lists required targets in TARGET_FIELDS order"""
    r = review({"mappings": [_m("trk_no", "external_id", 0.99)]}, POLAR_SAMPLES)
    assert r["missing_required"] == ["status", "weight_kg", "charge", "source_updated_at"], f"got {r['missing_required']}"
