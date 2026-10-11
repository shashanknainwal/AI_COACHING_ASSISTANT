import csv as _csv
import pandas as _pd

_REF = None


def _reference():
    """Plain-Python answer, computed once from the same file."""
    global _REF
    if _REF is None:
        with open(RESULTS_PATH, newline="") as f:
            rows = list(_csv.DictReader(f))
        latest = {}
        for r in rows:
            latest[r["ticket_id"]] = max(latest.get(r["ticket_id"], 0), int(r["attempt"]))
        groups, overhead_in, overhead_out = {}, 0, 0
        for r in rows:
            if int(r["attempt"]) < latest[r["ticket_id"]]:
                overhead_in += int(r["input_tokens"])
                overhead_out += int(r["output_tokens"])
                continue
            key = (r["month"], r["category"] or "(none)")
            g = groups.setdefault(key, [0, 0, 0, 0])
            g[0] += 1
            g[1] += r["stop_reason"] == "refusal"
            g[2] += int(r["input_tokens"])
            g[3] += int(r["output_tokens"])
        _REF = {"latest": latest, "groups": groups, "overhead": (overhead_in * 0.10 + overhead_out * 0.50) / 1e6}
    return _REF


class _Spy:
    """Wraps pd.read_csv to record how it was called."""

    def __init__(self):
        self.calls = []
        self.real = _pd.read_csv

    def __enter__(self):
        def spy(*args, **kwargs):
            self.calls.append(kwargs)
            return self.real(*args, **kwargs)
        _pd.read_csv = spy
        return self

    def __exit__(self, *exc):
        _pd.read_csv = self.real


def test_latest_attempts():
    """latest_attempts() maps every ticket to its highest attempt"""
    got = latest_attempts(RESULTS_PATH, 7_000)
    assert isinstance(got, dict), f"expected a dict, got {type(got).__name__}"
    ref = _reference()["latest"]
    assert len(got) == 50_000, f"expected 50,000 tickets, got {len(got)}"
    wrong = [t for t in ref if got.get(t) != ref[t]]
    assert not wrong, f"{len(wrong)} tickets have the wrong latest attempt, for example {wrong[0]}: expected {ref[wrong[0]]}, got {got.get(wrong[0])!r}"


def test_reads_in_chunks():
    """Every read_csv call uses the chunksize you were given"""
    with _Spy() as spy:
        aggregate(RESULTS_PATH, 9_000)
    assert spy.calls, "aggregate() never called pd.read_csv"
    sizes = [c.get("chunksize") for c in spy.calls]
    assert all(s == 9_000 for s in sizes), f"every pd.read_csv call should pass chunksize=9000, got {sizes!r}"


def test_pass_one_reads_two_columns():
    """latest_attempts() reads only ticket_id and attempt"""
    with _Spy() as spy:
        latest_attempts(RESULTS_PATH, 10_000)
    assert spy.calls, "latest_attempts() never called pd.read_csv"
    cols = spy.calls[0].get("usecols")
    assert cols is not None and sorted(cols) == ["attempt", "ticket_id"], f"pass 1 should use usecols=['ticket_id', 'attempt'], got {cols!r}"


def test_aggregate_shape():
    """aggregate() returns a (month, category) index and the five columns, sorted"""
    t = aggregate(RESULTS_PATH, 10_000)
    assert t is not None, "aggregate returned None"
    assert list(t.index.names) == ["month", "category"], f"index names should be ['month', 'category'], got {list(t.index.names)!r}"
    assert list(t.columns) == COLUMNS, f"columns should be {COLUMNS}, got {list(t.columns)!r}"
    assert t.index.is_monotonic_increasing, "sort the index"
    assert ("2024-01", "(none)") in t.index, "an empty category should become '(none)'"


def test_aggregate_values():
    """aggregate() counts each ticket once, at its latest attempt, even across chunk boundaries"""
    t = aggregate(RESULTS_PATH, 6_000)
    ref = _reference()["groups"]
    assert len(t) == len(ref), f"expected {len(ref)} (month, category) rows, got {len(t)}"
    assert int(t["tickets"].sum()) == 50_000, f"expected 50,000 tickets in total, got {int(t['tickets'].sum())}: did you drop the superseded attempts?"
    for key, (n, refusals, tin, tout) in ref.items():
        row = t.loc[key]
        got = (int(row["tickets"]), int(row["refusals"]), int(row["input_tokens"]), int(row["output_tokens"]))
        assert got == (n, refusals, tin, tout), f"{key}: expected tickets, refusals, input, output = {(n, refusals, tin, tout)}, got {got}"
        want_cost = (tin * 0.10 + tout * 0.50) / 1e6
        assert abs(float(row["cost_usd"]) - want_cost) < 1e-9, f"{key}: cost_usd should be {want_cost:.6f}, got {float(row['cost_usd']):.6f}"


def test_chunk_size_does_not_change_answer():
    """aggregate() gives the same table for different chunk sizes"""
    a = aggregate(RESULTS_PATH, 4_999)
    b = aggregate(RESULTS_PATH, 50_000)
    assert a is not None and b is not None, "aggregate returned None"
    assert a[["tickets", "refusals"]].equals(b[["tickets", "refusals"]]), "the result depends on chunk size: combine partial results by summing them"


def test_retry_overhead():
    """retry_overhead() prices only the attempts that were replaced"""
    got = retry_overhead(RESULTS_PATH, 8_000)
    want = _reference()["overhead"]
    assert got is not None and abs(got - want) < 1e-9, f"expected about ${want:.4f}, got {got!r}"


def test_report():
    """report() returns the headline numbers"""
    t = aggregate(RESULTS_PATH, 10_000)
    got = report(t)
    assert got is not None, "report returned None"
    ref = _reference()["groups"]
    refusals = sum(v[1] for v in ref.values())
    cost_total = sum((v[2] * 0.10 + v[3] * 0.50) / 1e6 for v in ref.values())
    assert got["tickets"] == 50_000, f"got {got['tickets']!r}"
    assert got["refusal_rate"] == round(refusals / 50_000, 4), f"expected {round(refusals / 50_000, 4)}, got {got['refusal_rate']!r}"
    assert got["cost_usd"] == round(cost_total, 2), f"expected {round(cost_total, 2)}, got {got['cost_usd']!r}"
    months, cats = {}, {}
    for (m, c), v in ref.items():
        months[m] = months.get(m, 0) + v[0]
        if c != "(none)":
            cats[c] = cats.get(c, 0) + v[0]
    assert got["busiest_month"] == max(sorted(months), key=lambda m: months[m]), f"got {got['busiest_month']!r}"
    assert got["top_category"] == max(sorted(cats), key=lambda c: cats[c]), f"top_category ignores '(none)', got {got['top_category']!r}"


def test_report_ties():
    """report() breaks ties by the earliest month and the first category name"""
    idx = _pd.MultiIndex.from_tuples([("2025-02", "card"), ("2025-01", "billing"), ("2025-01", "(none)"), ("2025-02", "billing")], names=["month", "category"])
    t = _pd.DataFrame({"tickets": [5, 3, 2, 0], "refusals": [0, 0, 2, 0], "input_tokens": [1, 1, 1, 1],
                       "output_tokens": [1, 1, 1, 1], "cost_usd": [0.5, 0.25, 0.25, 0.0]}, index=idx)
    got = report(t)
    assert got["busiest_month"] == "2025-01", f"2025-01 and 2025-02 both have 5 tickets; expected the earlier one, got {got['busiest_month']!r}"
    assert got["top_category"] == "card", f"got {got['top_category']!r}"
    assert got["refusal_rate"] == 0.2 and got["cost_usd"] == 1.0, f"got {got!r}"
