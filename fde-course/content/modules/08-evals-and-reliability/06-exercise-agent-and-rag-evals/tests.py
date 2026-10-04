def _run(tools, steps=None, answer="ok"):
    trace = [{"tool": t, "input": inp, "is_error": False} for t, inp in tools]
    return {"steps": steps if steps is not None else len(trace) + 1, "answer": answer, "trace": trace}


ALL = {"required_in_order": True, "no_forbidden": True, "within_steps": True, "credit_within_limit": True, "answer_includes": True}


def test_good_run_passes():
    """A run that meets every expectation passes all five checks"""
    case = AGENT_CASES[0]
    got = grade_trajectory(case["run"], case["expect"])
    assert got == {"checks": ALL, "pass": True}, f"got {got}"


def test_required_in_order():
    """Required tools must appear in order; extra calls in between are fine"""
    expect = {"required": ["lookup_order", "track_shipment"]}
    ok = _run([("lookup_order", {}), ("lookup_order", {}), ("track_shipment", {})])
    assert grade_trajectory(ok, expect)["checks"]["required_in_order"] is True
    wrong_order = _run([("track_shipment", {}), ("lookup_order", {})])
    assert grade_trajectory(wrong_order, expect)["checks"]["required_in_order"] is False, "order matters"
    missing = _run([("lookup_order", {})])
    assert grade_trajectory(missing, expect)["checks"]["required_in_order"] is False


def test_each_check():
    """Forbidden tools, step budget, credit limit and answer text are each checked"""
    run = _run([("issue_store_credit", {"customer_id": "C-1", "amount": 30, "reason": "goodwill"})], steps=4,
               answer="I added $30 in store credit.")
    got = grade_trajectory(run, {"forbidden": ["issue_store_credit"], "max_steps": 3, "max_credit": 25,
                                 "answer_includes": ["Store Credit", "refund"]})
    assert got == {"checks": {"required_in_order": True, "no_forbidden": False, "within_steps": False,
                              "credit_within_limit": False, "answer_includes": False}, "pass": False}, f"got {got}"
    assert grade_trajectory(run, {"max_steps": 4, "max_credit": 30, "answer_includes": ["STORE CREDIT"]})["pass"] is True, \
        "limits are inclusive and answer matching ignores case"


def test_missing_expectations_pass():
    """Expectations that aren't given don't fail the run"""
    run = _run([("issue_store_credit", {"customer_id": "C-1", "amount": 500, "reason": "goodwill"})], steps=50)
    assert grade_trajectory(run, {}) == {"checks": ALL, "pass": True}


def test_trajectory_report():
    """trajectory_report() summarizes which checks fail and where"""
    got = trajectory_report(AGENT_CASES)
    assert got == {
        "pass_rate": 0.333,
        "failed_checks": {"required_in_order": 1, "no_forbidden": 1, "credit_within_limit": 2, "within_steps": 1},
        "failures": {"A-2": ["required_in_order"], "A-3": ["no_forbidden", "credit_within_limit"],
                     "A-4": ["within_steps"], "A-5": ["credit_within_limit"]},
    }, f"got {got}"


def test_recall_and_reciprocal_rank():
    """recall_at_k() and reciprocal_rank() follow the standard definitions"""
    assert recall_at_k(["a", "b", "c", "d"], ["b", "d"], 3) == 0.5, "only b is in the top 3"
    assert recall_at_k(["a", "b", "c", "d"], ["b", "d"], 4) == 1.0
    assert recall_at_k([], ["x"], 3) == 0.0
    assert reciprocal_rank(["a", "b", "c"], ["c", "b"]) == 0.5, "the first relevant ID is at rank 2"
    assert reciprocal_rank(["a"], ["a"]) == 1.0
    assert reciprocal_rank(["a", "b"], ["z"]) == 0.0


def test_retrieval_report():
    """retrieval_report() measures the Module 7 keyword search"""
    calls = []

    def spy(query, k):
        calls.append(k)
        return keyword_search(query, k)

    got = retrieval_report(spy, RETRIEVAL_CASES)
    assert got == {"recall_at_k": 0.833, "mrr": 0.722, "misses": ["R-5"]}, f"got {got}"
    assert calls == [3] * 6, "call search_fn(query, k) once per case"
    got = retrieval_report(keyword_search, RETRIEVAL_CASES, k=2)
    assert got == {"recall_at_k": 0.583, "mrr": 0.667, "misses": ["R-2", "R-3", "R-5"]}, f"k=2: {got}"
