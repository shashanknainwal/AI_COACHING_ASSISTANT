def test_normalize_company():
    """normalize_company() removes case, punctuation, & and trailing suffixes"""
    cases = {"ACME Corporation, Inc.": "acme", "Acme Corp": "acme", "Birch & Co": "birch and",
             "Birch and Company LLC": "birch and", "Co-op Grocers": "co op grocers",
             "  Cobalt   Rigging LLC ": "cobalt rigging", "Corp Inc": "", "Delta Ltd. Company": "delta"}
    for raw, want in cases.items():
        got = normalize_company(raw)
        assert got == want, f"normalize_company({raw!r}) should be {want!r}, got {got!r}"


def test_domain():
    """domain() extracts a clean domain from URLs and emails"""
    cases = {"https://www.acme.com/about": "acme.com", "buyer@acme.com": "acme.com", "www.birchco.com": "birchco.com",
             "http://cobaltrigging.com": "cobaltrigging.com", " SALES@Ironclad-Safety.com ": "ironclad-safety.com",
             "acme.com": "acme.com"}
    for raw, want in cases.items():
        got = domain(raw)
        assert got == want, f"domain({raw!r}) should be {want!r}, got {got!r}"
    for raw in ["", "N/A", None, "  "]:
        assert domain(raw) is None, f"domain({raw!r}) should be None"


def test_similarity():
    """similarity() compares normalized names"""
    assert similarity("Meridian Valves", "Meridan Valves") == 0.97, f"got {similarity('Meridian Valves', 'Meridan Valves')}"
    assert similarity("Acme Corp", "ACME, Inc.") == 1.0, "names that normalize identically score 1.0"
    assert similarity("Acme Corp", "Acme Pumps") == 0.57, f"got {similarity('Acme Corp', 'Acme Pumps')}"


def test_find_duplicates_cobalt():
    """find_duplicates() returns Cobalt's five candidate pairs, best first"""
    got = [(p["ids"], p["score"], p["reason"]) for p in find_duplicates(ACCOUNTS)]
    want = [
        (("A-1001", "A-1004"), 1.0, "same name"),
        (("A-1002", "A-1018"), 1.0, "same name"),
        (("A-1003", "A-1010"), 1.0, "same name"),
        (("A-1015", "A-1017"), 0.97, "similar name"),
        (("A-1021", "A-1022"), 0.81, "same domain"),
    ]
    assert got == want, f"expected {want}, got {got}"


def test_free_domains_are_ignored():
    """Two different companies on gmail.com are not duplicates"""
    recs = [{"id": "X", "name": "Falcon Hydraulics", "website": "a@gmail.com"},
            {"id": "Y", "name": "Granite Works", "website": "b@gmail.com"}]
    assert find_duplicates(recs) == [], "a shared free email domain isn't evidence of the same company"


def test_reason_priority_and_threshold():
    """Same name beats same domain; the threshold is respected"""
    recs = [{"id": "P", "name": "Acme", "website": "acme.com"}, {"id": "Q", "name": "ACME Inc", "website": "acme.com"}]
    assert find_duplicates(recs)[0]["reason"] == "same name", "when several reasons apply, use the first one"
    recs = [{"id": "M1", "name": "Meridian Valves", "website": ""}, {"id": "M2", "name": "Meridan Valves", "website": ""}]
    assert find_duplicates(recs, threshold=0.98) == [], "0.97 is below a 0.98 threshold"
    assert len(find_duplicates(recs, threshold=0.97)) == 1, "a score equal to the threshold counts"


def test_sorting_ties_by_ids():
    """Pairs with equal scores are sorted by ids"""
    recs = [{"id": "Z", "name": "Beta", "website": ""}, {"id": "B", "name": "Alpha", "website": ""},
            {"id": "A", "name": "Alpha LLC", "website": ""}, {"id": "Y", "name": "Beta Co", "website": ""}]
    got = [p["ids"] for p in find_duplicates(recs)]
    assert got == [("B", "A"), ("Z", "Y")], f"ids keep input order inside a pair; pairs sort by ids; got {got}"
