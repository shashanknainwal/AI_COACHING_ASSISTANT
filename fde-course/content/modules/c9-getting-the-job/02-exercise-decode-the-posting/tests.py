import copy

POSTING = """
Forward Deployed Engineer (practice posting, fictional)

About the team:
- This line is not a requirement [ignored]

Must have:
- Python plus one more language [languages]
* Shipped LLM features to production [llm]
- Comfortable in front of customers

Nice to have:
- Built an MCP server [MCP]

Logistics:
- Travel 25-50% [travel]
"""


def _ev(claim, tags, kind, **extra):
    item = {"claim": claim, "tags": tags, "kind": kind}
    item.update(extra)
    return item


def test_parse_reads_sections_in_order():
    """parse_posting keeps bullets from the three known sections, in order"""
    reqs = parse_posting(POSTING)
    assert isinstance(reqs, list), f"parse_posting should return a list, got {type(reqs).__name__}"
    texts = [r["text"] for r in reqs]
    assert texts == [
        "Python plus one more language",
        "Shipped LLM features to production",
        "Comfortable in front of customers",
        "Built an MCP server",
        "Travel 25-50%",
    ], f"expected the five bullets under Must have / Nice to have / Logistics, got {texts}"
    prios = [r["priority"] for r in reqs]
    assert prios == ["must", "must", "must", "nice", "logistics"], f"wrong priorities: {prios}"


def test_parse_extracts_tags():
    """Tags come from a trailing [tag], lowercased; no brackets means tag None"""
    reqs = parse_posting(POSTING)
    tags = [r["tag"] for r in reqs]
    assert tags == ["languages", "llm", None, "mcp", "travel"], (
        f"expected tags ['languages', 'llm', None, 'mcp', 'travel'], got {tags}. "
        "Strip the [tag] from the text and lowercase it."
    )


def test_parse_ignores_unknown_sections_and_headers():
    """Bullets under other headings, and lines that aren't bullets, are ignored"""
    reqs = parse_posting("Intro text\nWhat you'll do:\n- Ignore me [x]\nMUST HAVE:\nNot a bullet\n- Evals experience [evals]\n")
    assert reqs == [{"text": "Evals experience", "tag": "evals", "priority": "must"}], (
        f"only the bullet under 'MUST HAVE:' should count (headings are case-insensitive), got {reqs}"
    )


def test_score_evidence_rules():
    """Work 2, project 1 (+1 with a link), course 1, +1 for a metric, capped at 3"""
    cases = [
        (_ev("a", [], "work"), 2),
        (_ev("a", [], "work", metric=True), 3),
        (_ev("a", [], "project"), 1),
        (_ev("a", [], "project", link="github.com/x"), 2),
        (_ev("a", [], "project", link="github.com/x", metric=True), 3),
        (_ev("a", [], "course"), 1),
        (_ev("a", [], "course", metric=True), 2),
        (_ev("a", [], "hobby", metric=True), 0),
    ]
    for item, want in cases:
        got = score_evidence(item)
        assert got == want, f"score_evidence({item}) should be {want}, got {got}"


def test_gap_report_statuses():
    """Green at 3, amber at 1-2, red with no matching evidence"""
    reqs = parse_posting(POSTING)
    evidence = [
        _ev("Led an LLM extraction launch, 30% fewer manual reviews", ["llm"], "work", metric=True),
        _ev("TypeScript side project", ["Languages"], "project"),
    ]
    report = gap_report(reqs, evidence)
    assert isinstance(report, list) and len(report) == 5, f"expected one row per requirement (5), got {report!r}"
    got = [(r["requirement"], r["status"]) for r in report]
    assert got[0] == ("Python plus one more language", "amber"), f"a plain project scores 1, so amber; got {got[0]} (tags match case-insensitively)"
    assert got[1] == ("Shipped LLM features to production", "green"), f"work with a metric scores 3, so green; got {got[1]}"
    assert got[3] == ("Built an MCP server", "red"), f"no evidence tagged 'mcp' means red; got {got[3]}"


def test_gap_report_special_rows():
    """Logistics rows are 'ask'; untagged requirements are 'review'"""
    report = gap_report(parse_posting(POSTING), [])
    statuses = [r["status"] for r in report]
    assert statuses == ["red", "red", "review", "red", "ask"], (
        f"with no evidence expected ['red', 'red', 'review', 'red', 'ask'], got {statuses}"
    )
    assert all(r["best"] is None for r in report), "with no evidence, best should be None in every row"
    assert report[4]["priority"] == "logistics", "rows should carry the requirement's priority"


def test_best_evidence_is_highest_score_first_on_ties():
    """best is the claim with the highest score; the earlier one wins a tie"""
    reqs = [{"text": "Evals", "tag": "evals", "priority": "must"}]
    evidence = [
        _ev("course on evals", ["evals"], "course"),
        _ev("eval repo", ["evals"], "project", link="github.com/x"),
        _ev("eval talk", ["evals"], "project", link="youtube.com/x"),
    ]
    row = gap_report(reqs, evidence)[0]
    assert row["best"] == "eval repo", f"'eval repo' and 'eval talk' both score 2; the first one should win, got {row['best']!r}"
    assert row["status"] == "amber", f"best score 2 is amber, got {row['status']!r}"


def test_gap_report_does_not_mutate_inputs():
    """gap_report leaves the requirements and evidence unchanged"""
    reqs = parse_posting(POSTING)
    evidence = [_ev("x", ["LLM"], "work")]
    before = (copy.deepcopy(reqs), copy.deepcopy(evidence))
    report = gap_report(reqs, evidence)
    assert isinstance(report, list), f"gap_report should return a list, got {type(report).__name__}"
    assert (reqs, evidence) == before, "don't modify the inputs (for example by lowercasing tags in place)"


def test_focus_list_order():
    """Must reds, then must ambers, then nice reds; posting order inside each group"""
    report = [
        {"requirement": "A", "priority": "must", "status": "amber", "best": "x"},
        {"requirement": "B", "priority": "nice", "status": "red", "best": None},
        {"requirement": "C", "priority": "must", "status": "red", "best": None},
        {"requirement": "D", "priority": "must", "status": "green", "best": "y"},
        {"requirement": "E", "priority": "logistics", "status": "ask", "best": None},
        {"requirement": "F", "priority": "must", "status": "red", "best": None},
        {"requirement": "G", "priority": "nice", "status": "amber", "best": "z"},
        {"requirement": "H", "priority": "must", "status": "review", "best": None},
    ]
    got = focus_list(report)
    assert got == ["C", "F", "A", "B"], (
        f"expected ['C', 'F', 'A', 'B'] (must reds, must ambers, nice reds), got {got}. "
        "Greens, nice ambers, 'ask' and 'review' rows are left out."
    )
