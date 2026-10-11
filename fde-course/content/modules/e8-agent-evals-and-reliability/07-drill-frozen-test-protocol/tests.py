_IDS = ["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10", "a11", "a12"]
_SPLIT = {"dev": ["a10", "a11", "a2", "a5", "a9"], "val": ["a1", "a12", "a7", "a8"], "test": ["a3", "a4", "a6"]}


def _lab():
    lab = EvalLab(list(_IDS))
    # base passes dev 3/5, val 2/4. "dev_only" aces dev, loses val. "general" gains on both.
    lab.record("base", {"a10": True, "a11": True, "a2": True, "a5": False, "a9": False,
                        "a1": True, "a12": True, "a7": False, "a8": False, "a3": True, "a4": False, "a6": False})
    lab.record("dev_only", {"a10": True, "a11": True, "a2": True, "a5": True, "a9": True,
                            "a1": True, "a12": False, "a7": False, "a8": False, "a3": False, "a4": False, "a6": False})
    lab.record("general", {"a10": True, "a11": True, "a2": True, "a5": True, "a9": False,
                           "a1": True, "a12": True, "a7": True, "a8": False, "a3": True, "a4": True, "a6": False})
    return lab


# Level 1 ----------------------------------------------------------------
def test_l1_split_is_hash_based_and_sorted():
    """split() buckets each id by its SHA-256 hash and sorts each split"""
    got = EvalLab(list(_IDS)).split()
    assert got == _SPLIT, f"bucket = int(sha256(id).hexdigest(), 16) % 100; <60 dev, <80 val, else test. got {got}"
    assert EvalLab(list(reversed(_IDS))).split() == _SPLIT, "input order must not matter"


def test_l1_split_is_stable_when_cases_are_added():
    """Adding cases never moves an existing case to another split"""
    bigger = EvalLab(_IDS + ["N-1", "N-2", "N-0"]).split()
    for name, ids in _SPLIT.items():
        assert set(ids) <= set(bigger[name]), f"{name}: existing cases moved after adding new ones"
    assert "N-0" in bigger["test"] and "N-1" in bigger["dev"]


def test_l1_fingerprint():
    """fingerprint() is the first 12 hex digits of sha256 over the sorted ids joined by newlines"""
    lab = EvalLab(list(_IDS))
    assert lab.fingerprint("test") == "82884ee2e8ec", f"got {lab.fingerprint('test')}"
    assert lab.fingerprint("dev") == "e8a53ae1b3ea"
    assert EvalLab(CASE_IDS).fingerprint("test") == "c53581a60c01"


# Level 2 ----------------------------------------------------------------
def test_l2_record_and_score():
    """score() is the pass rate over the split's cases that have results"""
    lab = _lab()
    assert lab.record("partial", {"a10": True, "a2": False, "zzz": True}) == 3, "record returns how many results it stored"
    assert lab.score("base", "dev") == 0.6 and lab.score("base", "val") == 0.5
    assert lab.score("partial", "dev") == 0.5, "only cases in the split that have a result count"
    assert lab.score("partial", "val") is None, "no results in the split: None"
    assert lab.score("nobody", "dev") is None, "unknown variant: None"


def test_l2_test_split_is_locked():
    """score() refuses to read the test split"""
    lab = _lab()
    try:
        lab.score("base", "test")
    except PermissionError:
        return
    assert False, "score(variant, 'test') must raise PermissionError: only final_test() may read it"


# Level 3 ----------------------------------------------------------------
def test_l3_overfit_is_detected():
    """propose() flags a dev win that loses on validation as overfit"""
    lab = _lab()
    got = lab.propose("dev_only", "base")
    assert got == {"variant": "dev_only", "parent": "base", "dev_gain": 0.4, "val_gain": -0.25, "decision": "overfit"}, f"got {got}"
    assert lab.best == "base", "an overfit variant must not become the best"


def test_l3_accept_and_reject():
    """propose() accepts a general gain and rejects a tiny one"""
    lab = _lab()
    got = lab.propose("general", "base")
    assert got and got["decision"] == "accept" and got["dev_gain"] == 0.2 and got["val_gain"] == 0.25, f"got {got}"
    assert lab.best == "general"
    got = lab.propose("base", "general")
    assert got["decision"] == "reject", f"a dev loss is a reject: got {got}"
    assert [h["decision"] for h in lab.history()] == ["accept", "reject"]


def test_l3_gannet_variants():
    """On Gannet's data, the pasted-examples prompt is overfit and the read-back rule is accepted"""
    lab = EvalLab(CASE_IDS)
    for name, res in RESULTS.items():
        lab.record(name, res)
    v1 = lab.propose("v1-pasted-examples", "v0-baseline")
    v2 = lab.propose("v2-read-back-rule", "v0-baseline")
    assert v1 and v1["decision"] == "overfit" and v1["dev_gain"] == 0.268 and v1["val_gain"] == -0.111, f"got {v1}"
    assert v2["decision"] == "accept" and lab.best == "v2-read-back-rule", f"got {v2}"


# Level 4 ----------------------------------------------------------------
def test_l4_one_look():
    """final_test() reads the test split once and reports the generalization gap"""
    lab = _lab()
    lab.propose("general", "base")
    got = lab.final_test(lab.best)
    assert got == {"variant": "general", "test": 0.667, "dev": 0.8, "gap": 0.133}, f"got {got}"
    again = lab.final_test("dev_only")
    assert again == {"error": "test split already used for general"}, f"a second look is refused: got {again}"


def test_l4_tampered_test_split():
    """final_test() refuses if the test split changed after the lab was created"""
    lab = _lab()
    lab.add_cases(["N-1", "N-2"])
    assert lab.final_test("base").get("error") is None, "new cases that land in dev don't touch the frozen test split"
    lab2 = _lab()
    lab2.add_cases(["N-0"])
    assert lab2.final_test("base") == {"error": "test split changed since it was frozen"}


def test_l4_saturation_and_gannet_result():
    """saturated() needs both dev and val at the ceiling; the accepted variant gets one test score"""
    lab = _lab()
    assert lab.saturated("dev_only") is False and lab.saturated("dev_only", ceiling=0.25) is True
    lab = EvalLab(CASE_IDS)
    for name, res in RESULTS.items():
        lab.record(name, res)
    lab.propose("v2-read-back-rule", "v0-baseline")
    got = lab.final_test("v2-read-back-rule")
    assert got == {"variant": "v2-read-back-rule", "test": 0.941, "dev": 0.893, "gap": -0.048}, f"got {got}"
