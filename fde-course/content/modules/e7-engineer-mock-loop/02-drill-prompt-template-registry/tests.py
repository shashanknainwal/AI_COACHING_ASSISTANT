def _reg():
    return TemplateRegistry()


# Level 1 ----------------------------------------------------------------
def test_l1_versions_and_render():
    """add_version numbers versions from 1, and render fills the newest one"""
    r = _reg()
    assert r.add_version(1, "greet", "Hello {{name}}!") == 1, "the first version of a template is 1"
    assert r.render(2, "greet", {"name": "Ada"}) == "Hello Ada!"
    assert r.add_version(3, "greet", "Hi {{name}}, welcome to {{product}}.") == 2
    assert r.render(4, "greet", {"name": "Ada", "product": "Atlas"}) == "Hi Ada, welcome to Atlas."
    assert r.add_version(5, "other", "x") == 1, "version numbers count per template"


def test_l1_render_details():
    """Repeated placeholders, non-string values, extra variables and old versions"""
    r = _reg()
    r.add_version(1, "t", "{{n}} items, {{n}} left")
    r.add_version(2, "t", "v2 {{n}}")
    assert r.render(3, "t", {"n": 3, "unused": "x"}, 1) == "3 items, 3 left", "fill every occurrence; ignore extra variables; use str()"
    assert r.render(4, "t", {"n": 3}) == "v2 3", "without a version, render the newest one"
    assert r.render(5, "t", {"n": 3}, 7) is None, "a version that doesn't exist renders as None"
    assert r.render(6, "missing", {}) is None, "a template that doesn't exist renders as None"


def test_l1_missing_variables():
    """Missing variables give 'error: missing a,b' (sorted, no duplicates)"""
    r = _reg()
    r.add_version(1, "t", "{{zeta}} {{alpha}} {{zeta}} {{mid}}")
    assert r.render(2, "t", {"mid": 1}) == "error: missing alpha,zeta"
    assert r.render(3, "t", {}) == "error: missing alpha,mid,zeta"


def test_l1_get_variables():
    """get_variables lists the placeholders of a version, sorted and unique"""
    r = _reg()
    r.add_version(1, "t", "{{b}} and {{a}} and {{b}}, not { c } or {{ d }}")
    r.add_version(2, "t", "no variables")
    assert r.get_variables(3, "t", 1) == ["a", "b"], "only {{name}} with no spaces counts"
    assert r.get_variables(4, "t") == [], "the newest version has none"
    assert r.get_variables(5, "t", 3) is None
    assert r.get_variables(6, "nope") is None


# Level 2 ----------------------------------------------------------------
def test_l2_tag_and_search_by_tag():
    """search filters by tag and returns names sorted"""
    r = _reg()
    r.add_version(1, "summarize", "Summarize: {{doc}}")
    r.add_version(2, "classify", "Classify the ticket: {{ticket}}")
    r.add_version(3, "extract", "Extract fields from {{doc}}")
    assert r.tag(4, "summarize", ["support", "docs"]) is True
    assert r.tag(5, "classify", ["support"]) is True
    assert r.tag(6, "classify", ["support"]) is True, "tagging twice is fine"
    assert r.tag(7, "missing", ["x"]) is False
    assert r.search(8, "support", "") == ["classify", "summarize"]
    assert r.search(9, "", "") == ["classify", "extract", "summarize"], "an empty tag and text match everything"
    assert r.search(10, "billing", "") == []


def test_l2_search_text_uses_newest_version():
    """Text search is case-insensitive and looks at the newest version only"""
    r = _reg()
    r.add_version(1, "a", "Answer the QUESTION: {{q}}")
    r.add_version(2, "b", "Old wording about questions")
    r.add_version(3, "b", "New wording")
    r.tag(4, "a", ["qa"])
    assert r.search(5, "", "question") == ["a"], "b's newest version no longer mentions questions"
    assert r.search(6, "qa", "answer") == ["a"]
    assert r.search(7, "qa", "wording") == [], "tag and text must both match"


def test_l2_top_used():
    """top_used counts successful renders only, ties broken by name"""
    r = _reg()
    for t, name in enumerate(["a", "b", "c", "d"], start=1):
        r.add_version(t, name, "{{x}}")
    r.render(10, "b", {"x": 1})
    r.render(11, "b", {"x": 1}, 1)
    r.render(12, "c", {"x": 1})
    r.render(13, "a", {"x": 1})
    r.render(14, "d", {})
    r.render(15, "d", {"x": 1}, 9)
    r.render(16, "zzz", {})
    assert r.top_used(17, 2) == ["b(2)", "a(1)"], "rank by uses, then by name"
    assert r.top_used(18, 10) == ["b(2)", "a(1)", "c(1)"], "errors and None renders don't count; unused templates are left out"


# Level 3 ----------------------------------------------------------------
def test_l3_bucket_assignment():
    """Users fall into versions by sum(ord(c)) % 100, lowest version first"""
    r = _reg()
    r.add_version(1, "t", "v1")
    r.add_version(2, "t", "v2")
    assert r.set_split(3, "t", {2: 80, 1: 20}) is True
    # alice -> 10, bob -> 7, carol -> 29, zed -> 23
    assert r.assign(4, "t", "alice") == 1, "bucket 10 is inside version 1's range [0, 20)"
    assert r.assign(5, "t", "bob") == 1
    assert r.assign(6, "t", "carol") == 2, "bucket 29 is inside version 2's range [20, 100)"
    assert r.assign(7, "t", "zed") == 2
    assert r.assign(8, "missing", "alice") is None


def test_l3_invalid_splits_are_refused():
    """Splits must name existing versions and add up to exactly 100"""
    r = _reg()
    r.add_version(1, "t", "v1")
    r.add_version(2, "t", "v2")
    assert r.set_split(3, "t", {1: 50, 2: 40}) is False, "percentages must sum to 100"
    assert r.set_split(4, "t", {1: 50, 3: 50}) is False, "version 3 doesn't exist"
    assert r.set_split(5, "t", {}) is False
    assert r.set_split(6, "missing", {1: 100}) is False
    assert r.assign(7, "t", "alice") == 2, "with no valid split, everyone gets the newest version"
    assert r.set_split(8, "t", {1: 0, 2: 100}) is True, "a version may get 0%"
    assert r.assign(9, "t", "bob") == 2


def test_l3_render_for_and_split_lifecycle():
    """render_for renders the assigned version; clear_split goes back to the newest"""
    r = _reg()
    r.add_version(1, "t", "A {{x}}")
    r.add_version(2, "t", "B {{x}}")
    r.set_split(3, "t", {1: 30, 2: 70})
    assert r.render_for(4, "t", "carol", {"x": 1}) == "A 1", "carol's bucket is 29"
    assert r.render_for(5, "t", "erin", {"x": 1}) == "B 1", "erin's bucket is 30"
    assert r.render_for(6, "t", "erin", {}) == "error: missing x"
    assert r.render(7, "t", {"x": 1}) == "B 1", "plain render ignores the split"
    assert r.top_used(8, 5) == ["t(3)"], "render_for counts as a use"
    r.add_version(9, "t", "C {{x}}")
    assert r.assign(10, "t", "carol") == 1, "a new version doesn't change a running split"
    assert r.clear_split(11, "t") is True
    assert r.clear_split(12, "t") is False, "there's no split left to clear"
    assert r.assign(13, "t", "carol") == 3


# Level 4 ----------------------------------------------------------------
def test_l4_rollback():
    """rollback makes an old version the one everyone gets"""
    r = _reg()
    r.add_version(1, "t", "A {{x}}")
    r.add_version(2, "t", "B {{x}}")
    r.set_split(3, "t", {1: 50, 2: 50})
    assert r.rollback(4, "t", 1) is True
    assert r.assign(5, "t", "u1") == 1, "rollback clears the split (u1's bucket is 66)"
    assert r.render(6, "t", {"x": 2}) == "A 2"
    assert r.rollback(7, "t", 5) is False
    assert r.rollback(8, "missing", 1) is False
    assert r.add_version(9, "t", "C {{x}}") == 3, "versions are never deleted; numbering continues"


def test_l4_version_at_follows_history():
    """version_at answers which version a user got at a past time"""
    r = _reg()
    r.add_version(10, "t", "v1")
    r.add_version(20, "t", "v2")
    r.set_split(30, "t", {1: 20, 2: 80})
    r.rollback(40, "t", 1)
    assert r.version_at(50, "t", "carol", 5) is None, "the template didn't exist yet"
    assert r.version_at(51, "t", "carol", 15) == 1
    assert r.version_at(52, "t", "carol", 20) == 2, "a change made exactly at t counts"
    assert r.version_at(53, "t", "alice", 35) == 1, "during the split alice (bucket 10) got version 1"
    assert r.version_at(54, "t", "carol", 35) == 2
    assert r.version_at(55, "t", "carol", 45) == 1, "after the rollback everyone got version 1"


def test_l4_version_at_with_new_versions_during_split():
    """History keeps both the split and the newest version"""
    r = _reg()
    r.add_version(1, "t", "v1")
    r.add_version(2, "t", "v2")
    r.set_split(3, "t", {1: 50, 2: 50})
    r.add_version(4, "t", "v3")
    r.clear_split(6, "t")
    assert r.version_at(10, "t", "u1", 5) == 2, "at 5 the split still applied (u1's bucket is 66)"
    assert r.version_at(11, "t", "alice", 5) == 1
    assert r.version_at(12, "t", "alice", 6) == 3, "after clear_split everyone got the newest version"
    assert r.version_at(13, "nope", "alice", 6) is None


def test_l4_rollback_is_recorded_not_rewritten():
    """A rollback is a new change; earlier history stays as it was"""
    r = _reg()
    r.add_version(1, "t", "v1")
    r.add_version(5, "t", "v2")
    r.rollback(10, "t", 1)
    r.rollback(20, "t", 2)
    assert r.version_at(30, "t", "bob", 7) == 2
    assert r.version_at(31, "t", "bob", 12) == 1
    assert r.version_at(32, "t", "bob", 20) == 2
