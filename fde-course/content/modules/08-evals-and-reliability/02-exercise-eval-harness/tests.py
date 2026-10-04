import anthropic
from anthropic import _sim
from fde_datasets import brightway

CASE = {"id": "X-1", "text": "t", "category": "billing", "urgency": "high"}


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _rows():
    _fresh()
    return run_eval(anthropic.Anthropic(max_retries=1), brightway.EVAL_TICKETS)


def test_grade():
    """grade() checks each field and passes only when both match"""
    assert grade(CASE, {"category": "billing", "urgency": "high"}) == {"category": True, "urgency": True, "pass": True}
    assert grade(CASE, {"category": "billing", "urgency": "low"}) == {"category": True, "urgency": False, "pass": False}
    assert grade(CASE, {"category": "account", "urgency": "high"}) == {"category": False, "urgency": True, "pass": False}
    assert grade(CASE, None) == {"category": False, "urgency": False, "pass": False}, "a failed system call fails every check"


def test_run_eval_rows():
    """run_eval() returns one row per case with expected, actual and grades"""
    rows = _rows()
    assert isinstance(rows, list) and len(rows) == 20, "one row per case"
    assert [r["id"] for r in rows] == [c["id"] for c in brightway.EVAL_TICKETS], "keep the case order"
    first = rows[0]
    assert set(first) == {"id", "expected", "actual", "grades", "error"}, f"row keys: {set(first)}"
    assert first["expected"] == {"category": "order_status", "urgency": "normal"}
    assert first["actual"] == {"category": "order_status", "urgency": "normal"} and first["error"] is None
    t07 = next(r for r in rows if r["id"] == "T-07")
    assert t07["grades"] == {"category": True, "urgency": False, "pass": False}, f"T-07 grades: {t07['grades']}"


def test_errors_do_not_stop_the_eval():
    """An API error is recorded on its row, and the run continues"""
    rows = _rows()
    t12 = next(r for r in rows if r["id"] == "T-12")
    assert t12["actual"] is None and t12["grades"]["pass"] is False
    assert isinstance(t12["error"], str) and t12["error"].startswith("OverloadedError: "), f"error: {t12['error']!r}"
    assert rows[-1]["actual"] is not None, "cases after the error still run"


def test_summarize():
    """summarize() reports overall, per-field and per-category rates"""
    report = summarize(_rows())
    assert report == {
        "n": 20, "pass_rate": 0.7, "category_accuracy": 0.8, "urgency_accuracy": 0.85, "errors": 1,
        "by_category": {"order_status": 1.0, "returns": 1.0, "damaged_item": 0.5, "billing": 0.75, "account": 0.333, "other": 0.75},
    }, f"got {report}"


def test_summarize_small():
    """summarize() rounds to 3 decimals and slices by EXPECTED category"""
    rows = [
        {"id": "a", "expected": {"category": "returns", "urgency": "low"}, "actual": {"category": "billing", "urgency": "low"},
         "grades": {"category": False, "urgency": True, "pass": False}, "error": None},
        {"id": "b", "expected": {"category": "returns", "urgency": "low"}, "actual": {"category": "returns", "urgency": "low"},
         "grades": {"category": True, "urgency": True, "pass": True}, "error": None},
        {"id": "c", "expected": {"category": "billing", "urgency": "high"}, "actual": {"category": "billing", "urgency": "high"},
         "grades": {"category": True, "urgency": True, "pass": True}, "error": None},
    ]
    assert summarize(rows) == {"n": 3, "pass_rate": 0.667, "category_accuracy": 0.667, "urgency_accuracy": 1.0, "errors": 0,
                               "by_category": {"returns": 0.5, "billing": 1.0}}


def test_confusions():
    """confusions() counts expected -> actual category mix-ups, ignoring errors"""
    got = confusions(_rows())
    assert got == {"account -> billing": 1, "other -> damaged_item": 1, "damaged_item -> returns": 1}, f"got {got}"
