EXPECTED_REPORT = """# Cobalt CRM data quality
16 rows checked against 6 rules.

| Rule | Checked | Failed | Pass rate | Severity |
|---|---|---|---|---|
| email format | 13 | 3 | 76.9% | critical |
| email present | 16 | 3 | 81.2% | critical |
| account id unique | 16 | 2 | 87.5% | critical |
| revenue numeric | 13 | 1 | 92.3% | warning |
| owner present | 16 | 1 | 93.8% | warning |
| industry allowed | 15 | 0 | 100.0% | ok |

Critical: 3, warnings: 2, ok: 1"""


def _rows(values, col="c"):
    return [{col: v} for v in values]


def test_required():
    """'required' checks every row; missing values fail"""
    got = evaluate_rule(_rows(["a", "", "N/A", "b"]), {"name": "r", "column": "c", "check": "required"})
    assert got == {"name": "r", "checked": 4, "failed": 2, "pass_rate": 50.0}, f"got {got}"


def test_unique():
    """'unique' fails every occurrence of a repeated value; missing values don't fail"""
    got = evaluate_rule(_rows(["A", "A ", "B", "", ""]), {"name": "u", "column": "c", "check": "unique"})
    assert got == {"name": "u", "checked": 5, "failed": 2, "pass_rate": 60.0}, f"got {got}"


def test_regex_only_checks_present_values():
    """'regex' only checks rows with a value"""
    rule = {"name": "e", "column": "c", "check": "regex", "pattern": r"[^@\s]+@[^@\s]+\.[a-z]{2,}"}
    got = evaluate_rule(_rows(["a@b.com", "jim@acme", "", " x@y.io "]), rule)
    assert got == {"name": "e", "checked": 3, "failed": 1, "pass_rate": 66.7}, f"missing values are skipped, values stripped; got {got}"


def test_numeric_and_allowed():
    """'numeric' and 'allowed' check stripped present values"""
    got = evaluate_rule(_rows(["12", "-3.5", "1,200", "N/A"]), {"name": "n", "column": "c", "check": "numeric"})
    assert got == {"name": "n", "checked": 3, "failed": 1, "pass_rate": 66.7}, f"got {got}"
    got = evaluate_rule(_rows(["Retail ", "Mining", "-"]), {"name": "a", "column": "c", "check": "allowed", "values": ["Retail"]})
    assert got == {"name": "a", "checked": 2, "failed": 1, "pass_rate": 50.0}, f"got {got}"


def test_nothing_checked():
    """A rule with nothing to check passes at 100.0"""
    got = evaluate_rule(_rows(["", "-"]), {"name": "x", "column": "c", "check": "numeric"})
    assert got == {"name": "x", "checked": 0, "failed": 0, "pass_rate": 100.0}, f"got {got}"


def test_cobalt_rules():
    """evaluate_rule() matches the Cobalt numbers for every rule"""
    got = {r["name"]: (r["checked"], r["failed"], r["pass_rate"]) for r in (evaluate_rule(ROWS, rule) for rule in RULES)}
    want = {"email present": (16, 3, 81.2), "email format": (13, 3, 76.9), "account id unique": (16, 2, 87.5),
            "revenue numeric": (13, 1, 92.3), "industry allowed": (15, 0, 100.0), "owner present": (16, 1, 93.8)}
    for name, w in want.items():
        assert got.get(name) == w, f"{name}: expected (checked, failed, pass_rate) = {w}, got {got.get(name)}"


def test_severity():
    """severity() uses the 90 / 98 thresholds"""
    cases = {89.9: "critical", 90.0: "warning", 97.9: "warning", 98.0: "ok", 100.0: "ok", 0.0: "critical"}
    for rate, want in cases.items():
        assert severity(rate) == want, f"severity({rate}) should be {want!r}, got {severity(rate)!r}"


def test_report_exact():
    """dq_report() produces the exact Markdown report"""
    got = dq_report(ROWS, RULES, "Cobalt CRM data quality")
    if got != EXPECTED_REPORT:
        g, w = (got or "").splitlines(), EXPECTED_REPORT.splitlines()
        for i, (a, b) in enumerate(zip(g, w), 1):
            assert a == b, f"line {i} differs:\n  expected: {b!r}\n  got:      {a!r}"
        assert len(g) == len(w), f"expected {len(w)} lines, got {len(g)}"


def test_report_tie_break_by_name():
    """Rules with the same pass rate are ordered by name"""
    rules = [{"name": "zeta", "column": "c", "check": "required"}, {"name": "alpha", "column": "c", "check": "required"}]
    got = dq_report(_rows(["x"]), rules, "T").splitlines()
    assert got[5].startswith("| alpha") and got[6].startswith("| zeta"), f"got {got[5:7]}"
