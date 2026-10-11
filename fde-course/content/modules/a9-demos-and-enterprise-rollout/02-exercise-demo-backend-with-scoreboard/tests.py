import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()
    _install_responder()


def _case(cid):
    return next(c for c in CASES if c["id"] == cid)


def _good_fields(cid):
    text = _case(cid)["invoice_text"]
    lines = text.splitlines()
    inv = next(l for l in lines if l.startswith("Invoice no: "))
    ref = next(l for l in lines if l.startswith("Shipment ref: "))
    tot = next(l for l in lines if l.startswith("Total due: "))
    value = float(tot.split("EUR ")[1].replace(",", ""))
    return text, {
        "invoice_number": {"value": inv.split(": ")[1], "quote": inv},
        "shipment_ref": {"value": ref.split(": ")[1], "quote": ref},
        "total_eur": {"value": value, "quote": tot},
    }


def test_extract_request_shape():
    """extract() asks for structured output, sets effort, and leaves room for thinking"""
    _fresh()
    got = extract(client, _case("H01")["invoice_text"])
    assert got is not None, "extract() returned None"
    p = _sim.last_request()
    assert p is not None, "extract() never called client.messages.create"
    cfg = p.get("output_config") or {}
    assert (cfg.get("format") or {}).get("type") == "json_schema", \
        "use output_config.format with a JSON schema: prose answers can't be parsed or trusted in a demo"
    assert cfg.get("effort") in ("low", "medium", "high", "xhigh", "max"), \
        "set output_config.effort explicitly, so the demo's latency and cost are a choice, not a default"
    assert p["max_tokens"] >= 1024, "max_tokens covers thinking as well as the answer: give it at least 1024"
    assert _case("H01")["invoice_text"] in _user_text(p), "send the invoice text in the user message"


def test_extract_reads_text_blocks_by_type():
    """extract() returns the parsed fields even when a thinking block comes first"""
    _fresh()
    got = extract(client, _case("H01")["invoice_text"])
    assert got and got.get("status") == "ok", f"expected status 'ok', got {got!r}"
    assert got["fields"]["shipment_ref"]["value"] == "HFG-88213", \
        "read the JSON from the text block (find blocks by type; content[0] is a thinking block)"


def test_extract_handles_refusal():
    """extract() reports a refusal instead of crashing or inventing an answer"""
    _fresh()
    got = extract(client, _case("H13")["invoice_text"])
    assert got and got.get("status") == "refused", \
        f"check stop_reason == 'refusal' before reading content; got {got!r}"
    assert got.get("category") == "cyber", "keep the refusal category from stop_details for the log"


def test_ground_verdicts():
    """ground() compares the grounded total with the agreed rate, with tolerance"""
    text, f = _good_fields("H02")
    g = ground(f, text, SHIPMENTS)
    assert g and g["verdict"] == "overcharge" and g["difference_eur"] == 280.0, f"H02 is 280 EUR over: {g}"
    text, f = _good_fields("H09")
    g = ground(f, text, SHIPMENTS)
    assert g["verdict"] == "match" and g["difference_eur"] == 4.0, \
        f"4 EUR over on 900 is inside max(5, 1% of agreed): {g}"
    text, f = _good_fields("H19")
    g = ground(f, text, SHIPMENTS)
    assert g["verdict"] == "match", f"15 EUR over on 1,530 is inside the 15.30 tolerance: {g}"
    assert g["reason"] == "within tolerance", f"reason for a match is 'within tolerance': {g['reason']!r}"


def test_ground_abstains():
    """ground() abstains on missing, unsupported or unknown values instead of guessing"""
    text, f = _good_fields("H01")
    f["total_eur"] = {"value": None, "quote": None}
    g = ground(f, text, SHIPMENTS)
    assert g == {"verdict": "abstain", "reason": "missing total_eur", "difference_eur": None}, f"missing: {g}"
    text, f = _good_fields("H01")
    f["total_eur"] = {"value": 1500.0, "quote": "Total due: EUR 1,500.00"}
    g = ground(f, text, SHIPMENTS)
    assert g == {"verdict": "abstain", "reason": "unsupported total_eur", "difference_eur": None}, \
        f"a quote that isn't on the invoice means the value is unsupported: {g}"
    text, f = _good_fields("H12")
    g = ground(f, text, SHIPMENTS)
    assert g == {"verdict": "abstain", "reason": "unknown shipment HFG-99999", "difference_eur": None}, f"unknown: {g}"


def test_cite_lines():
    """cite() returns 1-based line numbers for every quoted field, in FIELDS order"""
    text, f = _good_fields("H01")
    got = cite(f, text)
    assert got == [
        {"field": "invoice_number", "line": 3, "quote": "Invoice no: VT-24-1187"},
        {"field": "shipment_ref", "line": 4, "quote": "Shipment ref: HFG-88213"},
        {"field": "total_eur", "line": 8, "quote": "Total due: EUR 1,322.00"},
    ], f"got {got}"
    f["total_eur"] = {"value": None, "quote": None}
    assert [c["field"] for c in cite(f, text)] == ["invoice_number", "shipment_ref"], "skip fields with no quote"


def test_run_case_errors_are_contained():
    """run_case() turns an API error into an 'error' verdict instead of crashing the demo"""
    _fresh()
    no_retry = anthropic.Anthropic(max_retries=0)
    _sim.queue(_sim.server_error())
    r = run_case(no_retry, _case("H01"), SHIPMENTS)
    assert r and r["verdict"] == "error" and r["id"] == "H01", f"got {r!r}"


def test_scoreboard_is_honest():
    """scoreboard() counts every case: refusals, abstains and wrong answers stay in the denominator"""
    _fresh()
    b = scoreboard(client, CASES, SHIPMENTS)
    assert b, "scoreboard() returned nothing"
    assert b["n"] == 20, f"n is every labelled case, got {b['n']}"
    assert b["correct"] == 17 and b["accuracy"] == 0.85, \
        f"17 of 20 match their label (a justified abstain counts as correct): got {b['correct']}, {b['accuracy']}"
    assert b["refused"] == 1 and b["errors"] == 0, f"one refusal (H13): got refused={b['refused']}"
    assert b["answered"] == 15 and b["answered_correct"] == 14 and b["precision_answered"] == 0.933, \
        f"15 answered, 14 right: got {b['answered']}, {b['answered_correct']}, {b['precision_answered']}"
    assert b["abstained"] == 4 and b["abstain_justified"] == 3, \
        f"4 abstains, 3 of them on cases labelled abstain: got {b['abstained']}, {b['abstain_justified']}"
    assert b["wrong"] == ["H13", "H14", "H15"], f"wrong cases in case order: got {b['wrong']}"


def test_scoreboard_headline():
    """The headline states the denominator and the failures, not just the best number"""
    _fresh()
    b = scoreboard(client, CASES, SHIPMENTS)
    assert b["headline"] == "17/20 correct (85%); answered 15, abstained 4, refused 1, errors 0", \
        f"got {b['headline']!r}"
    assert len(b["rows"]) == 20, "keep one row per case so you can show the failures on screen"
