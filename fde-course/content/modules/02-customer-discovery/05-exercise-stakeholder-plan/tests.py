def _s(name, influence, interest, stance="neutral", role=None):
    return {"name": name, "title": "t", "influence": influence, "interest": interest, "stance": stance, "role": role}


def test_quadrants():
    """quadrant() maps influence/interest to the four quadrants"""
    cases = [((5, 5), "manage closely"), ((3, 3), "manage closely"), ((4, 1), "keep satisfied"),
             ((2, 4), "keep informed"), ((1, 1), "monitor"), ((2, 2), "monitor"), ((3, 2), "keep satisfied")]
    for (inf, intr), want in cases:
        got = quadrant(_s("x", inf, intr))
        assert got == want, f"influence={inf}, interest={intr}: expected {want!r}, got {got!r}"


def test_plan_shape():
    """engagement_plan() returns name, quadrant and cadence for everyone"""
    plan = engagement_plan(LUMEN)
    assert isinstance(plan, list) and len(plan) == len(LUMEN), "plan should have one entry per stakeholder"
    for row in plan:
        assert set(row) == {"name", "quadrant", "cadence"}, f"each entry needs exactly name, quadrant, cadence; got {sorted(row)}"
        assert row["cadence"] == CADENCE[row["quadrant"]], f"wrong cadence for {row['name']}"


def test_plan_order_lumen():
    """Plan is sorted by quadrant, then influence (high first), then name"""
    got = [r["name"] for r in engagement_plan(LUMEN)]
    want = ["Joan Pierce", "Tom Bray", "Marcus Lee", "Ravi Shah", "Adjuster team", "Dee Ortiz"]
    assert got == want, f"expected {want}, got {got}"


def test_plan_name_tiebreak():
    """Ties on quadrant and influence are broken by name"""
    got = [r["name"] for r in engagement_plan([_s("Zed", 4, 4), _s("Amy", 4, 5), _s("Bo", 5, 3)])]
    assert got == ["Bo", "Amy", "Zed"], f"expected ['Bo', 'Amy', 'Zed'], got {got}"


def test_plan_does_not_mutate():
    """engagement_plan() doesn't reorder or modify the input"""
    data = [_s("B", 1, 1), _s("A", 5, 5)]
    result = engagement_plan(data)
    assert isinstance(result, list), "implement engagement_plan first: it should return a list"
    assert [d["name"] for d in data] == ["B", "A"], "the input list was reordered; use sorted() instead of .sort()"


def test_risks_healthy():
    """risks() returns [] for a healthy engagement"""
    team = [_s("S", 5, 5, "supporter", "sponsor"), _s("C", 3, 5, "supporter", "champion"), _s("K", 3, 1, "skeptic")]
    got = risks(team)
    assert got == [], f"a skeptic with influence 3 is not flagged; expected [], got {got!r}"


def test_risks_lumen():
    """risks() flags the CISO for Lumen"""
    got = risks(LUMEN)
    assert got == ["high-influence skeptic: Ravi Shah"], f"got {got!r}"


def test_risks_missing_roles_and_order():
    """Missing sponsor/champion come first, then skeptics in input order"""
    team = [_s("X", 4, 2, "skeptic"), _s("U", 1, 5, "neutral", "user"), _s("Y", 5, 5, "skeptic")]
    got = risks(team)
    want = ["no sponsor", "no champion", "high-influence skeptic: X", "high-influence skeptic: Y"]
    assert got == want, f"expected {want}, got {got!r}"


def test_risks_unsupportive_sponsor():
    """A sponsor who isn't a supporter is flagged once, after the missing-role checks"""
    team = [_s("S", 5, 5, "skeptic", "sponsor"), _s("C", 3, 4, "supporter", "champion")]
    got = risks(team)
    want = ["sponsor is not a supporter", "high-influence skeptic: S"]
    assert got == want, f"expected {want}, got {got!r}"
