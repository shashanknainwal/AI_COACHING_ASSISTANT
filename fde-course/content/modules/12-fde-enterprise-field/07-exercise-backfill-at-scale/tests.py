import csv as _csv
import inspect as _inspect

_REF = None


def _reference():
    """Plain answer computed once from the same file, independently."""
    global _REF
    if _REF is None:
        with open(RESULTS_PATH, newline="") as f:
            rows = list(_csv.DictReader(f))
        latest = {}
        for r in rows:
            latest[r["ticket_id"]] = max(latest.get(r["ticket_id"], 0), int(r["attempt"]))
        groups, oin, oout = {}, 0, 0
        for r in rows:
            if int(r["attempt"]) < latest[r["ticket_id"]]:
                oin += int(r["input_tokens"])
                oout += int(r["output_tokens"])
                continue
            g = groups.setdefault((r["month"], r["category"] or "(none)"), [0, 0, 0, 0])
            g[0] += 1
            g[1] += r["stop_reason"] == "refusal"
            g[2] += int(r["input_tokens"])
            g[3] += int(r["output_tokens"])
        _REF = {"latest": latest, "groups": groups, "overhead": (oin * 0.10 + oout * 0.50) / 1e6}
    return _REF


class _Spy:
    """Temporarily wraps the learner's iter_chunks to record chunk sizes."""

    def __init__(self, fn):
        self.g = fn.__globals__
        self.calls, self.max_rows = [], 0

    def __enter__(self):
        self.real = self.g["iter_chunks"]
        def spy(path, chunksize=10_000):
            self.calls.append(chunksize)
            for chunk in self.real(path, chunksize):
                self.max_rows = max(self.max_rows, len(chunk))
                yield chunk
        self.g["iter_chunks"] = spy
        return self

    def __exit__(self, *exc):
        self.g["iter_chunks"] = self.real


def test_iter_chunks():
    """iter_chunks() is a generator yielding lists of at most chunksize rows, ints converted"""
    gen = iter_chunks(RESULTS_PATH, 7_000)
    assert _inspect.isgenerator(gen), "iter_chunks should be a generator (use yield), so memory stays flat"
    sizes, first = [], None
    for chunk in gen:
        sizes.append(len(chunk))
        if first is None:
            first = chunk[0]
    assert max(sizes) == 7_000 and sum(sizes) == sum(1 for _ in open(RESULTS_PATH)) - 1, f"chunks should hold at most 7000 rows and cover every row, got sizes {sizes!r}"
    assert isinstance(first["attempt"], int) and isinstance(first["input_tokens"], int) and isinstance(first["output_tokens"], int), f"convert attempt and token columns to int, got {first!r}"


def test_latest_attempts():
    """latest_attempts() maps every ticket to its highest attempt"""
    got = latest_attempts(RESULTS_PATH, 7_000)
    assert isinstance(got, dict), f"expected a dict, got {type(got).__name__}"
    ref = _reference()["latest"]
    assert len(got) == 50_000, f"expected 50,000 tickets, got {len(got)}"
    wrong = [t for t in ref if got.get(t) != ref[t]]
    assert not wrong, f"{len(wrong)} tickets wrong, e.g. {wrong[0]}: expected {ref[wrong[0]]}, got {got.get(wrong[0])!r}"


def test_reads_through_chunks():
    """aggregate() reads the file only through iter_chunks, with your chunksize"""
    with _Spy(aggregate) as spy:
        aggregate(RESULTS_PATH, 9_000)
    assert len(spy.calls) >= 2, f"two passes means at least two calls to iter_chunks, got {len(spy.calls)}"
    assert all(c == 9_000 for c in spy.calls), f"pass chunksize through, got {spy.calls!r}"
    assert spy.max_rows <= 9_000, "no chunk may exceed chunksize"


def test_aggregate_values():
    """aggregate() counts each ticket once, at its latest attempt, even across chunk boundaries"""
    t = aggregate(RESULTS_PATH, 6_000)
    assert t is not None, "aggregate returned None"
    ref = _reference()["groups"]
    assert list(t) == sorted(ref), "keys should be every (month, category) pair, sorted; an empty category is '(none)'"
    assert sum(v["tickets"] for v in t.values()) == 50_000, "expected 50,000 tickets in total: did you drop superseded attempts?"
    for key, (n, refusals, tin, tout) in ref.items():
        row = t[key]
        got = (row["tickets"], row["refusals"], row["input_tokens"], row["output_tokens"])
        assert got == (n, refusals, tin, tout), f"{key}: expected {(n, refusals, tin, tout)}, got {got}"
        want = (tin * 0.10 + tout * 0.50) / 1e6
        assert abs(row["cost_usd"] - want) < 1e-9, f"{key}: cost_usd should be {want:.6f}, got {row['cost_usd']!r}"


def test_chunk_size_does_not_change_answer():
    """aggregate() gives the same table for different chunk sizes"""
    a = aggregate(RESULTS_PATH, 4_999)
    b = aggregate(RESULTS_PATH, 60_000)
    assert a is not None and a == b, "the result depends on chunk size: dedupe needs the first pass"


def test_retry_overhead():
    """retry_overhead() prices only the attempts that were replaced"""
    got = retry_overhead(RESULTS_PATH, 8_000)
    want = _reference()["overhead"]
    assert got is not None and abs(got - want) < 1e-9, f"expected about ${want:.4f}, got {got!r}"


def test_report():
    """report() returns the headline numbers"""
    got = report(aggregate(RESULTS_PATH, 10_000))
    assert got is not None, "report returned None"
    ref = _reference()["groups"]
    refusals = sum(v[1] for v in ref.values())
    total = sum((v[2] * 0.10 + v[3] * 0.50) / 1e6 for v in ref.values())
    assert got["tickets"] == 50_000, f"got {got['tickets']!r}"
    assert got["refusal_rate"] == round(refusals / 50_000, 4), f"got {got['refusal_rate']!r}"
    assert got["cost_usd"] == round(total, 2), f"expected {round(total, 2)}, got {got['cost_usd']!r}"


def test_report_ties():
    """report() breaks ties by the earliest month and the first category name, ignoring '(none)'"""
    def row(n, r=0):
        return {"tickets": n, "refusals": r, "input_tokens": 1, "output_tokens": 1, "cost_usd": 0.25}
    t = {("2025-01", "(none)"): row(9, 9), ("2025-01", "billing"): row(1), ("2025-02", "card"): row(5),
         ("2025-02", "billing"): row(4), ("2025-03", "login"): row(2)}
    got = report(t)
    assert got["busiest_month"] == "2025-01", f"2025-01 and 2025-02 both have 10; expected the earlier, got {got['busiest_month']!r}"
    assert got["top_category"] == "billing", f"billing and card both have 5; expected billing, got {got['top_category']!r}"
    assert got["refusal_rate"] == 0.4286 and got["cost_usd"] == 1.25, f"got {got!r}"
