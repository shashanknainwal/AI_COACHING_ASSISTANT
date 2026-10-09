import json
import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _email(eid):
    return next(e for e in EMAILS if e["id"] == eid)


def _reply(**fields):
    base = {"serial_number": "HX-204611", "sku": "HR-ARM-2", "failure_mode": "no_power",
            "safety_issue": False, "requested_action": "replace", "evidence": "won't power on since Monday"}
    base.update(fields)
    return [_sim.thinking(), _sim.text(json.dumps(base))]


def test_system_prompt():
    """build_system_prompt() has context, catalog, failure modes and rules in tags"""
    expected = "\n".join(
        [CONTEXT, "", "<product_catalog>"]
        + [f"- {s}: {d}" for s, d in PRODUCTS]
        + ["</product_catalog>", "", "<failure_modes>"]
        + [f"- {n}: {d}" for n, d in FAILURE_MODES]
        + ["</failure_modes>", "", "<rules>", RULES, "</rules>"]
    )
    got = build_system_prompt()
    assert got == expected, f"got:\n{got}"
    assert build_system_prompt() == got, "the system prompt must be identical on every call so it can be cached"


def test_user_message():
    """build_user_message() wraps subject and body in tags and asks last"""
    got = build_user_message({"id": "x", "subject": "S", "body": "B line"})
    expected = "<email>\n<subject>S</subject>\n<body>\nB line\n</body>\n</email>\n\nExtract the warranty-claim fields from the email above."
    assert got == expected, f"got:\n{got}"


def test_schema():
    """RMA_SCHEMA uses enums, a nullable serial and forbids extra fields"""
    s = RMA_SCHEMA
    assert s.get("type") == "object" and s.get("additionalProperties") is False, "top level: type object, additionalProperties False"
    props = s.get("properties", {})
    want = ["serial_number", "sku", "failure_mode", "safety_issue", "requested_action", "evidence"]
    assert sorted(props) == sorted(want), f"properties should be exactly {want}, got {list(props)}"
    assert sorted(s.get("required", [])) == sorted(want), "every field is required (nullable is not the same as optional)"
    serial_types = sorted(x.get("type") for x in props["serial_number"].get("anyOf", []))
    assert serial_types == ["null", "string"], "serial_number: anyOf string or null"
    assert props["sku"].get("enum") == [p[0] for p in PRODUCTS] + ["unknown"], "sku: the catalog SKUs plus \"unknown\""
    assert props["failure_mode"].get("enum") == [f[0] for f in FAILURE_MODES], "failure_mode: the FAILURE_MODES names, in order"
    assert props["requested_action"].get("enum") == ACTIONS
    assert props["safety_issue"].get("type") == "boolean" and props["evidence"].get("type") == "string"


def test_validate_rma():
    """validate_rma() catches bad serials, invented serials and paraphrased evidence"""
    email = _email("M-101")
    good = json.loads(_reply()[1].text)
    assert validate_rma(good, email) == [], f"a correct extraction has no errors: {validate_rma(good, email)}"
    assert validate_rma(dict(good, serial_number=None), email) == [], "a null serial is allowed"
    got = validate_rma(dict(good, serial_number="204611"), email)
    assert got == ["serial_number '204611' is not a valid serial (expected HX- followed by 6 digits)"], f"got {got}"
    got = validate_rma(dict(good, serial_number="HX-999999"), email)
    assert got == ["serial_number 'HX-999999' does not appear in the email"], f"got {got}"
    got = validate_rma(dict(good, evidence="it is broken"), email)
    assert got == ["evidence is not an exact quote from the email body"], f"got {got}"
    got = validate_rma(dict(good, evidence="  "), email)
    assert got == ["evidence is not an exact quote from the email body"], f"blank evidence is not a quote: {got}"
    got = validate_rma(dict(good, serial_number="HX-1", evidence="nope"), email)
    assert len(got) == 2, f"report every problem, not just the first: {got}"


def test_request_shape():
    """extract_rma() sends one well-formed structured-output request"""
    _fresh()
    got = extract_rma(anthropic.Anthropic(), _email("M-101"))
    assert isinstance(got, dict) and got.get("status") == "ok", f"got {got}"
    assert got["attempts"] == 1 and got["errors"] == [] and got["id"] == "M-101"
    assert got["prompt_version"] == PROMPT_VERSION, "log which prompt version produced the output"
    assert got["data"]["serial_number"] == "HX-204611"
    assert len(_sim.calls) == 1, f"expected one call, got {len(_sim.calls)}"
    p = _sim.last_request()
    assert p["model"] == MODEL and p["max_tokens"] == MAX_TOKENS
    assert p.get("system") == build_system_prompt(), "send build_system_prompt() as the system prompt"
    assert p["messages"] == [{"role": "user", "content": build_user_message(_email("M-101"))}]
    assert (p.get("output_config") or {}).get("format") == {"type": "json_schema", "schema": RMA_SCHEMA}


def test_retry_with_feedback():
    """An invented serial gets one retry that shows Claude the validation errors"""
    _fresh()
    got = extract_rma(anthropic.Anthropic(), _email("M-104"))
    assert got.get("status") == "ok" and got["attempts"] == 2, f"got {got}"
    assert got["data"]["serial_number"] is None and got["data"]["failure_mode"] == "physical_damage"
    assert len(_sim.calls) == 2
    msgs = _sim.last_request()["messages"]
    assert len(msgs) == 3, "the retry continues the conversation: user email, Claude's answer, your correction"
    assert msgs[1]["role"] == "assistant" and isinstance(msgs[1]["content"], list), "append response.content (all blocks) as the assistant turn"
    assert any(b.get("type") == "text" for b in msgs[1]["content"])
    expected = ("Your previous answer failed validation:\n"
                "- serial_number 'HX-104000' does not appear in the email\n"
                "Return the corrected fields for the same email.")
    assert msgs[2] == {"role": "user", "content": expected}, f"got {msgs[2]}"


def test_gives_up_after_one_retry():
    """Output that is still invalid after one retry goes to human review"""
    _fresh()
    got = extract_rma(anthropic.Anthropic(), _email("M-105"))
    assert got.get("status") == "needs_review" and got["attempts"] == 2, f"got {got}"
    assert got["errors"] == ["evidence is not an exact quote from the email body"], f"got {got['errors']}"
    assert got["data"] is not None and got["data"]["sku"] == "unknown", "keep the last parsed answer for the reviewer"
    assert len(_sim.calls) == 2, "retry once, not more"


def test_refusal():
    """A refusal goes straight to review without a retry"""
    _fresh()
    _sim.queue(_sim.refusal())
    got = extract_rma(anthropic.Anthropic(), _email("M-101"))
    assert got.get("status") == "needs_review" and got["errors"] == ["refused"] and got["data"] is None, f"got {got}"
    assert got["attempts"] == 1 and len(_sim.calls) == 1, "don't retry a refusal with the same request"


def test_truncation():
    """Output cut off at max_tokens is retried once with double the budget"""
    _fresh()
    _sim.queue(_sim.message(_sim.thinking(), _sim.text('{"serial_number": "HX-2046'), stop_reason="max_tokens"))
    got = extract_rma(anthropic.Anthropic(), _email("M-101"))
    assert got.get("status") == "ok" and got["attempts"] == 2, f"got {got}"
    first, second = _sim.requests()
    assert second["max_tokens"] == 2 * MAX_TOKENS, f"retry with max_tokens={2 * MAX_TOKENS}, got {second['max_tokens']}"
    assert second["messages"] == first["messages"], "a truncated answer isn't worth showing back; resend the same messages"
    _fresh()
    _sim.queue(_sim.message(_sim.text('{"ser'), stop_reason="max_tokens"),
               _sim.message(_sim.text('{"ser'), stop_reason="max_tokens"))
    got = extract_rma(anthropic.Anthropic(), _email("M-101"))
    assert got.get("status") == "needs_review" and got["errors"] == ["output was cut off at max_tokens"], f"got {got}"
