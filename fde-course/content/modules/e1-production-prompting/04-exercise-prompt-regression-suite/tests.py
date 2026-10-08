import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _row(cid, **wrong):
    scores = {f: True for f in FIELDS}
    scores.update(wrong)
    return {"id": cid, "actual": {}, "scores": scores, "error": None}


def test_normalize():
    """normalize() makes equivalent values compare equal"""
    assert normalize("vendor", "  Sorrel   &  Pike ") == normalize("vendor", "sorrel & pike"), "collapse whitespace and ignore case"
    assert normalize("total", "1,200.00") == normalize("total", 1200) == 1200.0, "totals compare as numbers, rounded to cents"
    assert normalize("total", 86.499) == 86.5
    assert normalize("currency", " gbp") == "GBP"
    assert normalize("due_date", None) is None and normalize("vendor", None) is None, "None stays None"
    assert normalize("invoice_number", "BT-5521") != normalize("invoice_number", "BT-5512")


def test_score_case():
    """score_case() scores every field, and a missing answer scores nothing"""
    exp = GOLDEN[0]["expected"]
    got = score_case(exp, {"vendor": "BRANNOCK TOOLS", "invoice_number": "BT-5521", "total": "1,200.00", "currency": "gbp", "due_date": None})
    assert got == {"vendor": True, "invoice_number": True, "total": True, "currency": True, "due_date": False}, f"got {got}"
    got = score_case(GOLDEN[4]["expected"], dict(GOLDEN[4]["expected"]))
    assert got["due_date"] is True, "expected null and got null is correct"
    got = score_case(GOLDEN[4]["expected"], dict(GOLDEN[4]["expected"], due_date="2026-11-02"))
    assert got["due_date"] is False, "expected null but got a date: a made-up value"
    assert score_case(exp, None) == {f: False for f in FIELDS}


def test_run_suite_requests():
    """run_suite() sends each case with the given prompt and the schema"""
    _fresh()
    rows = run_suite(anthropic.Anthropic(), PROMPT_V1, GOLDEN[:3])
    assert isinstance(rows, list) and len(rows) == 3, f"one row per case, got {rows!r}"
    assert [r["id"] for r in rows] == ["G-01", "G-02", "G-03"]
    assert rows[0]["error"] is None and rows[0]["actual"]["invoice_number"] == "BT-5521"
    assert rows[1]["scores"]["vendor"] is False and rows[1]["scores"]["total"] is True, f"got {rows[1]['scores']}"
    assert len(_sim.calls) == 3
    p = _sim.requests()[1]
    assert p["model"] == MODEL and p["system"] == PROMPT_V1
    assert p["messages"] == [{"role": "user", "content": invoice_message(GOLDEN[1]["text"])}]
    assert (p.get("output_config") or {}).get("format") == {"type": "json_schema", "schema": INVOICE_SCHEMA}
    assert invoice_message("X") == "<invoice>\nX\n</invoice>\n\nExtract the invoice fields."


def test_run_suite_failures():
    """A refusal or an API error fails that case and the suite keeps going"""
    _fresh()
    _sim.queue(_sim.refusal(), _sim.overloaded())
    rows = run_suite(anthropic.Anthropic(max_retries=0), PROMPT_V1, GOLDEN[:3])
    assert isinstance(rows, list) and len(rows) == 3, "one failure must not stop the suite"
    assert rows[0]["error"] == "refused" and rows[0]["actual"] is None
    assert rows[1]["error"] == "OverloadedError" and rows[1]["actual"] is None, f"got {rows[1]}"
    assert rows[0]["scores"] == {f: False for f in FIELDS}
    assert rows[2]["error"] is None and all(rows[2]["scores"].values())


def test_field_accuracy():
    """field_accuracy() reports each field and the all-fields rate"""
    rows = [_row("a"), _row("b", currency=False), _row("c", currency=False, vendor=False)]
    got = field_accuracy(rows)
    assert got == {"vendor": 0.667, "invoice_number": 1.0, "total": 1.0, "currency": 0.333, "due_date": 1.0, "all_fields": 0.333}, f"got {got}"
    assert field_accuracy([])["all_fields"] == 0.0


def test_compare_small():
    """compare() lists regressions and fixes and applies the gate rules"""
    old = [_row("a"), _row("b", vendor=False), _row("c")]
    new = [_row("a", due_date=False), _row("b"), _row("c")]
    got = compare(old, new)
    assert got["regressions"] == ["a:due_date"] and got["fixes"] == ["b:vendor"], f"got {got}"
    assert got["deltas"]["vendor"] == 0.333 and got["deltas"]["due_date"] == -0.333 and got["deltas"]["all_fields"] == 0.0
    assert got["verdict"] == "block" and got["reasons"] == ["due_date accuracy dropped from 1.000 to 0.667"], f"got {got['reasons']}"
    got = compare([_row("a")], [_row("a", total=False)], tolerance=1.0)
    assert got["reasons"] == ["critical field total regressed on a"] and got["verdict"] == "block", \
        f"a critical-field regression blocks even within tolerance: {got['reasons']}"
    got = compare([_row("a"), _row("b")], [_row("b"), _row("z", vendor=False)])
    assert got["regressions"] == [] and got["fixes"] == [], f"cases missing from the old run aren't regressions or fixes: {got}"
    got = compare([_row("a")], [_row("a")])
    assert got["verdict"] == "ship" and got["reasons"] == [] and got["regressions"] == []


def test_compare_v1_v2():
    """The v2 prompt scores higher overall but is blocked on currency"""
    _fresh()
    c = anthropic.Anthropic()
    v1, v2 = run_suite(c, PROMPT_V1, GOLDEN), run_suite(c, PROMPT_V2, GOLDEN)
    assert field_accuracy(v1)["all_fields"] == 0.5 and field_accuracy(v2)["all_fields"] == 0.7
    got = compare(v1, v2)
    assert got["regressions"] == ["G-05:due_date", "G-06:currency", "G-08:currency"], f"got {got['regressions']}"
    assert got["fixes"] == ["G-02:vendor", "G-04:vendor", "G-06:due_date", "G-07:total", "G-09:vendor"], f"got {got['fixes']}"
    assert got["deltas"]["due_date"] == 0.0, "a fix and a regression cancel out in the average; that's why you diff cases"
    assert got["verdict"] == "block"
    assert got["reasons"] == ["currency accuracy dropped from 1.000 to 0.800",
                              "critical field currency regressed on G-06",
                              "critical field currency regressed on G-08"], f"got {got['reasons']}"
