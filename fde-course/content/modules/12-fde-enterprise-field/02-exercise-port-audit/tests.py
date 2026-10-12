import copy

_MATRIX = {
    "alpha": {"messages": "yes", "batches": "yes", "skills": "beta", "geo": "x", "inference_geo": "yes"},
    "beta_cloud": {"messages": "yes", "batches": "no", "skills": "no", "inference_geo": "no"},
    "gamma": {"messages": "yes", "batches": "partial", "skills": "yes", "inference_geo": "no"},
}
_SITES = [
    {"file": "b.py", "feature": "batches"},
    {"file": "a.py", "feature": "messages"},
    {"file": "c.py", "feature": "skills"},
    {"file": "a.py", "feature": "batches"},
    {"file": "a.py", "feature": "messages"},
]
_WORK = {"batches": "use a worker pool", "skills": "inline the instructions"}


def test_features_used():
    """features_used() returns distinct features, sorted"""
    got = features_used(_SITES)
    assert got == ["batches", "messages", "skills"], f"expected ['batches', 'messages', 'skills'], got {got!r}"


def test_files_using():
    """files_using() returns distinct files for one feature, sorted"""
    got = files_using(_SITES, "batches")
    assert got == ["a.py", "b.py"], f"expected ['a.py', 'b.py'], got {got!r}"
    assert files_using(_SITES, "nothing") == [], "a feature nobody uses has no files"


def test_ready_platform():
    """A platform with every feature at 'yes' is ready"""
    sites = [s for s in _SITES if s["feature"] != "skills"]
    got = audit_platform("alpha", _MATRIX, sites, {}, _WORK)
    assert got is not None, "audit_platform returned None"
    assert got["verdict"] == "ready", f"expected verdict 'ready', got {got['verdict']!r}"
    assert got["blockers"] == [] and got["beta"] == [] and got["open_items"] == [], f"nothing should be flagged, got {got!r}"
    assert got["platform"] == "alpha" and got["residency"] is None and got["rework_files"] == [], f"unexpected fields: {got!r}"


def test_beta_depends_on_allow_beta():
    """A beta feature is a blocker unless allow_beta is true"""
    strict = audit_platform("alpha", _MATRIX, _SITES, {"allow_beta": False}, _WORK)
    assert strict["verdict"] == "rework", f"beta without allow_beta should need rework, got {strict['verdict']!r}"
    assert strict["blockers"] == [{"feature": "skills", "files": ["c.py"], "workaround": "inline the instructions"}], f"got {strict['blockers']!r}"
    loose = audit_platform("alpha", _MATRIX, _SITES, {"allow_beta": True}, _WORK)
    assert loose["verdict"] == "ready_with_beta", f"expected 'ready_with_beta', got {loose['verdict']!r}"
    assert loose["beta"] == ["skills"] and loose["blockers"] == [], f"got beta={loose['beta']!r} blockers={loose['blockers']!r}"


def test_blockers_list_files_and_workarounds():
    """Unsupported features become blockers with their files and workaround"""
    got = audit_platform("beta_cloud", _MATRIX, _SITES, {}, _WORK)
    assert got["verdict"] == "rework", f"expected 'rework', got {got['verdict']!r}"
    assert got["blockers"] == [
        {"feature": "batches", "files": ["a.py", "b.py"], "workaround": "use a worker pool"},
        {"feature": "skills", "files": ["c.py"], "workaround": "inline the instructions"},
    ], f"blockers should be in feature order with sorted files, got {got['blockers']!r}"
    assert got["rework_files"] == ["a.py", "b.py", "c.py"], f"got {got['rework_files']!r}"


def test_blocked_without_workaround():
    """A blocker with no known workaround makes the verdict 'blocked'"""
    got = audit_platform("beta_cloud", _MATRIX, _SITES, {}, {"batches": "use a worker pool"})
    assert got["verdict"] == "blocked", f"expected 'blocked', got {got['verdict']!r}"
    skills = [b for b in got["blockers"] if b["feature"] == "skills"]
    assert skills and skills[0]["workaround"] is None, f"missing workaround should be None, got {got['blockers']!r}"


def test_partial_and_unknown_are_open_items():
    """'partial' and features missing from the matrix become open items, not blockers"""
    sites = _SITES + [{"file": "d.py", "feature": "teleport"}]
    got = audit_platform("gamma", _MATRIX, sites, {}, _WORK)
    assert got["blockers"] == [], f"partial and unknown are not blockers, got {got['blockers']!r}"
    assert got["verdict"] == "confirm", f"expected 'confirm', got {got['verdict']!r}"
    assert len(got["open_items"]) == 2, f"expected two open items, got {got['open_items']!r}"
    assert got["open_items"][0].startswith("batches:") and got["open_items"][1].startswith("teleport:"), f"open items start with the feature name, in feature order: {got['open_items']!r}"


def test_residency():
    """Residency uses inference_geo where it exists, otherwise adds an open item"""
    sites = [{"file": "a.py", "feature": "messages"}]
    a = audit_platform("alpha", _MATRIX, sites, {"residency": "us"}, _WORK)
    assert a["residency"] == "inference_geo" and a["verdict"] == "ready", f"alpha has inference_geo, got {a!r}"
    b = audit_platform("beta_cloud", _MATRIX, sites, {"residency": "us"}, _WORK)
    assert b["residency"] == "confirm", f"expected residency 'confirm', got {b['residency']!r}"
    assert b["verdict"] == "confirm", f"a residency open item should make the verdict 'confirm', got {b['verdict']!r}"
    assert any(i.startswith("residency:") and "us" in i for i in b["open_items"]), f"expected a 'residency: ...us...' open item, got {b['open_items']!r}"


def test_port_report_order():
    """port_report() sorts by verdict, then number of rework files, then name"""
    matrix = copy.deepcopy(_MATRIX)
    matrix["delta"] = {"messages": "yes", "batches": "no", "skills": "yes", "inference_geo": "no"}
    before = copy.deepcopy(matrix)
    got = port_report(matrix, _SITES, {"allow_beta": True}, _WORK)
    assert got is not None, "port_report returned None"
    names = [a["platform"] for a in got]
    assert names == ["alpha", "gamma", "delta", "beta_cloud"], f"expected ['alpha', 'gamma', 'delta', 'beta_cloud'], got {names!r}"
    assert matrix == before, "don't modify the matrix"


def test_real_matrix_bedrock():
    """On the snapshot, the Quarrybank prototype needs five files reworked for Bedrock"""
    got = audit_platform("bedrock", PLATFORM_FEATURES, QUARRYBANK_PROTOTYPE, {"residency": "us"}, WORKAROUNDS)
    assert got["verdict"] == "rework", f"expected 'rework', got {got['verdict']!r}"
    feats = [b["feature"] for b in got["blockers"]]
    assert feats == ["batches", "code_execution", "mcp_connector", "server_fallbacks"], f"got {feats!r}"
    assert len(got["rework_files"]) == 5, f"expected 5 files, got {got['rework_files']!r}"
