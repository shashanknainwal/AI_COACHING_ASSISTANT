def _rec(i, correct=True, tin=1000, tout=100, lat=1000, error=None):
    return {"id": i, "correct": correct, "input_tokens": tin, "output_tokens": tout, "latency_ms": lat, "error": error}


_PRICE = {"input_per_mtok": 2.0, "output_per_mtok": 10.0}


def test_check_same_cases():
    """check_same_cases() reports missing, unknown and duplicate ids, and leaves clean candidates out"""
    ids = ["a", "b", "c"]
    results = {
        "clean": [_rec("a"), _rec("b"), _rec("c")],
        "messy": [_rec("c"), _rec("z"), _rec("c"), _rec("y")],
    }
    got = check_same_cases(ids, results)
    assert got == {"messy": {"missing": ["a", "b"], "unknown": ["y", "z"], "duplicates": ["c"]}}, \
        f"missing keeps the eval-set order; unknown and duplicates are sorted. Got {got}"


def test_percentile_nearest_rank():
    """percentile() uses the nearest-rank method"""
    vals = list(range(1, 21))  # 1..20
    assert percentile(vals, 95) == 19, f"ceil(0.95 * 20) = 19th smallest is 19, got {percentile(vals, 95)}"
    assert percentile([5, 1, 3], 50) == 3, "values must be sorted first; the median of 1, 3, 5 is 3"
    assert percentile([7], 95) == 7, "a single value is every percentile"
    assert percentile(list(range(1, 41)), 95) == 38, "with 40 values, p95 is the 38th smallest: the two slowest don't count"
    assert percentile([], 95) is None, "no values: None"


def test_wilson_interval():
    """wilson_interval() matches the Wilson formula, rounded to 3 decimals"""
    assert wilson_interval(34, 40) == (0.709, 0.929), f"got {wilson_interval(34, 40)}"
    assert wilson_interval(9, 10) == (0.596, 0.982), f"got {wilson_interval(9, 10)}"
    assert wilson_interval(0, 0) == (0.0, 1.0), "no scored cases: (0.0, 1.0)"


def test_score_candidate_basic():
    """score_candidate() computes accuracy, cost per task and p95 from the records"""
    ids = ["a", "b", "c", "d"]
    recs = [_rec("a"), _rec("b", correct=False), _rec("c", tin=3000, lat=2000), _rec("d", lat=500)]
    s = score_candidate(recs, _PRICE, ids)
    assert s, "score_candidate returned nothing"
    # cost: 3 x (1000*2 + 100*10)/1e6 = 0.003 each, plus (3000*2 + 100*10)/1e6 = 0.007 -> 0.016 / 4 = 0.004
    assert s == {"n": 4, "passes": 3, "accuracy": 0.75, "ci": (0.301, 0.954), "errors": 0, "error_rate": 0.0,
                 "cost_per_task": 0.004, "p95_ms": 2000}, f"got {s}"


def test_score_candidate_errors_and_missing():
    """Errors and missing cases are not scored but count toward the error rate; extras and duplicates are ignored"""
    ids = ["a", "b", "c", "d"]
    recs = [
        _rec("a"),
        _rec("b", correct=False, tin=0, tout=0, lat=30000, error="TimeoutError: slow"),
        _rec("a", correct=False),            # duplicate: only the first record for an id counts
        _rec("zz", tin=999999),              # not in the eval set: ignored
        _rec("c"),
    ]                                        # "d" is missing
    s = score_candidate(recs, _PRICE, ids)
    assert s and (s["n"], s["passes"], s["accuracy"]) == (2, 2, 1.0), \
        f"only a and c are scored (b errored, d is missing): got n={s and s['n']}, passes={s and s['passes']}"
    assert s["errors"] == 2 and s["error_rate"] == 0.5, f"b (error) and d (missing) are 2 of 4 cases: got {s}"
    assert s["cost_per_task"] == 0.002, f"cost of the 3 kept records (a, b, c) = 0.006, over 3 records = 0.002: got {s['cost_per_task']}"
    assert s["p95_ms"] == 30000, f"the timed-out call's latency counts; users waited for it: got {s['p95_ms']}"


def test_pick_winner_rules():
    """pick_winner() filters on constraints, then picks the cheapest candidate tied with the quality leader"""
    scores = {
        "big":   {"accuracy": 0.95, "ci": (0.85, 0.99), "cost_per_task": 0.02, "p95_ms": 2000, "error_rate": 0.0},
        "mid":   {"accuracy": 0.90, "ci": (0.80, 0.96), "cost_per_task": 0.008, "p95_ms": 1500, "error_rate": 0.0},
        "small": {"accuracy": 0.86, "ci": (0.75, 0.93), "cost_per_task": 0.001, "p95_ms": 900, "error_rate": 0.0},
        "weak":  {"accuracy": 0.70, "ci": (0.55, 0.81), "cost_per_task": 0.0005, "p95_ms": 800, "error_rate": 0.0},
    }
    cons = {"min_accuracy": 0.75, "max_cost_per_task": 0.01, "max_p95_ms": 3000, "max_error_rate": 0.05}
    got = pick_winner(scores, cons)
    assert got and got["disqualified"] == {"big": ["cost $0.0200 per task above $0.0100"],
                                           "weak": ["accuracy 70.0% below 75.0%"]}, f"got {got and got['disqualified']}"
    assert got["leader"] == "mid", f"big is out on cost, so mid leads among eligible candidates: got {got['leader']}"
    assert got["tied"] == ["mid", "small"] and got["winner"] == "small", \
        f"small's upper bound 0.93 reaches mid's lower bound 0.80, and small is cheaper: got {got}"


def test_pick_winner_tie_and_cheapest():
    """Tied candidates are those whose upper bound reaches the leader's lower bound; the cheapest tied one wins"""
    scores = {
        "mid":   {"accuracy": 0.90, "ci": (0.80, 0.96), "cost_per_task": 0.008, "p95_ms": 1500, "error_rate": 0.0},
        "small": {"accuracy": 0.86, "ci": (0.75, 0.93), "cost_per_task": 0.001, "p95_ms": 900, "error_rate": 0.0},
        "weak":  {"accuracy": 0.70, "ci": (0.55, 0.79), "cost_per_task": 0.0005, "p95_ms": 800, "error_rate": 0.0},
    }
    got = pick_winner(scores, {"min_accuracy": 0.6})
    assert got and got["tied"] == ["mid", "small"], f"weak's upper bound 0.79 is below mid's lower bound 0.80: got {got and got['tied']}"
    assert got["winner"] == "small", f"within noise, the cheaper candidate wins: got {got['winner']}"
    assert got["disqualified"] == {}, "constraints that aren't given aren't checked"


def test_pick_winner_reasons_and_none():
    """Every failed constraint is listed, in order, and no eligible candidate means no winner"""
    scores = {"x": {"accuracy": 0.5, "ci": (0.3, 0.7), "cost_per_task": 0.05, "p95_ms": 9000, "error_rate": 0.2}}
    cons = {"min_accuracy": 0.85, "max_cost_per_task": 0.01, "max_p95_ms": 3000, "max_error_rate": 0.05}
    got = pick_winner(scores, cons)
    assert got == {"winner": None, "leader": None, "tied": [], "disqualified": {"x": [
        "accuracy 50.0% below 85.0%", "cost $0.0500 per task above $0.0100",
        "p95 latency 9000 ms above 3000 ms", "error rate 20.0% above 5.0%"]}}, f"got {got}"


def test_ellery_scores():
    """Ellery bake-off: the scores for each candidate"""
    s = {n: score_candidate(r, PRICING[n], EVAL_CASE_IDS) for n, r in RESULTS.items()}
    assert all(s.values()), "score_candidate returned nothing"
    got = {n: (v["passes"], v["n"], v["accuracy"], v["ci"], v["errors"], v["cost_per_task"], v["p95_ms"]) for n, v in s.items()}
    expected = {
        "opus-rubric":    (37, 40, 0.925, (0.801, 0.974), 0, 0.017309, 4701),
        "sonnet-rubric":  (34, 39, 0.872, (0.733, 0.944), 1, 0.007689, 2755),
        "haiku-fewshot":  (34, 40, 0.85, (0.709, 0.929), 0, 0.000478, 1247),
        "haiku-zeroshot": (31, 40, 0.775, (0.625, 0.877), 0, 0.000348, 1043),
        "quillon-v4":     (34, 36, 0.944, (0.819, 0.985), 4, 0.01113, 2722),
    }
    for name in expected:
        assert got[name] == expected[name], f"{name}: expected (passes, n, accuracy, ci, errors, cost, p95) = {expected[name]}, got {got[name]}"


def test_ellery_decision():
    """Ellery bake-off: haiku-fewshot wins under the constraints; the incumbent's 94% is on 36 of 40 cases"""
    assert check_same_cases(EVAL_CASE_IDS, RESULTS) == {
        "quillon-v4": {"missing": ["D-07", "D-19", "D-28", "D-33"], "unknown": [], "duplicates": []}}, \
        "the incumbent skipped four cases"
    s = {n: score_candidate(r, PRICING[n], EVAL_CASE_IDS) for n, r in RESULTS.items()}
    d = pick_winner(s, CONSTRAINTS)
    assert d and d["leader"] == "sonnet-rubric" and d["tied"] == ["haiku-fewshot", "sonnet-rubric"] and d["winner"] == "haiku-fewshot", \
        f"got leader={d and d['leader']}, tied={d and d['tied']}, winner={d and d['winner']}"
    assert d["disqualified"] == {
        "haiku-zeroshot": ["accuracy 77.5% below 85.0%"],
        "opus-rubric": ["cost $0.0173 per task above $0.0100", "p95 latency 4701 ms above 3000 ms"],
        "quillon-v4": ["cost $0.0111 per task above $0.0100", "error rate 10.0% above 5.0%"],
    }, f"got {d['disqualified']}"
