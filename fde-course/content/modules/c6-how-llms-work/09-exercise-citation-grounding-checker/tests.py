def test_split_sentences():
    """split_sentences() splits after . ! ? and keeps decimals and citations intact"""
    got = split_sentences("Returns take 30 days [1]. Is 4.5 stars good? Yes!  ")
    assert got == ["Returns take 30 days [1].", "Is 4.5 stars good?", "Yes!"], f"got {got!r}"
    assert split_sentences("") == [], "empty text has no sentences"


def test_supported_claim():
    """A claim whose words and numbers appear in its cited span is supported"""
    c = check_claim("Refunds are issued within 5 business days after the item reaches the warehouse [2].", SPANS)
    assert isinstance(c, dict) and set(c) == {"sentence", "citations", "status", "overlap"}, f"got {c!r}"
    assert c["citations"] == [2] and c["status"] == "supported" and c["overlap"] == 1.0, f"got {c}"
    c = check_claim("You can return unworn items within 30 days of delivery for a full refund [1].", SPANS)
    assert c["status"] == "supported" and c["overlap"] == 0.88, f"7 of 8 content words match ('return' isn't 'returned'): got {c}"


def test_uncited_and_bad_citation():
    """Sentences with no citation, or citing a span that wasn't retrieved, are flagged"""
    c = check_claim("Exchanges are processed the same day.", SPANS)
    assert c["status"] == "uncited" and c["citations"] == [] and c["overlap"] == 0.0, f"got {c}"
    c = check_claim("Gift cards are refunded as store credit [4].", SPANS)
    assert c["status"] == "bad_citation" and c["citations"] == [4], f"span 4 doesn't exist: got {c}"
    c = check_claim("Unworn items can be returned within 30 days [1][4].", SPANS)
    assert c["status"] == "bad_citation", f"any missing citation makes it a bad citation: got {c}"


def test_wrong_number_is_unsupported():
    """A changed number makes a claim unsupported even when most words match"""
    c = check_claim("Refunds are issued within 7 business days after the item reaches the warehouse [2].", SPANS)
    assert c["overlap"] >= 0.6, f"the words mostly match (overlap {c['overlap']}), but..."
    assert c["status"] == "unsupported", f"...7 isn't in the cited span, so the claim is unsupported: got {c}"
    c = check_claim("Refunds for orders over $200 take 10 business days [2].", SPANS)
    assert c["status"] == "unsupported", f"got {c}"


def test_low_overlap_and_multiple_citations():
    """Overlap is measured against all cited spans together, after removing stopwords"""
    c = check_claim("Return shipping is free for loyalty members [2].", SPANS)
    assert c["status"] == "unsupported" and c["overlap"] == 0.0, f"got {c}"
    c = check_claim("Unworn items can be returned within 30 days, and refunds are issued within 5 business days [1][2].", SPANS)
    assert c["citations"] == [1, 2] and c["status"] == "supported", f"words come from spans 1 and 2 combined: got {c}"
    c = check_claim("Final sale items cannot be returned [3][3].", SPANS)
    assert c["citations"] == [3], f"list each citation once, in order: got {c['citations']}"
    strict = check_claim("You can return unworn items within 30 days of delivery for a full refund [1].", SPANS, threshold=0.9)
    assert strict["status"] == "unsupported", "the threshold argument must be used"


def test_grounding_report():
    """grounding_report() checks every sentence and lists the flagged ones"""
    r = grounding_report(ANSWER, SPANS)
    assert isinstance(r, dict) and set(r) == {"claims", "supported", "total", "grounded_ratio", "flagged"}, f"got {r!r}"
    assert r["total"] == 7 and r["supported"] == 3 and r["grounded_ratio"] == 0.43, f"3 of 7 sentences are supported: got {r['supported']}/{r['total']}"
    assert [c["status"] for c in r["claims"]] == ["supported", "supported", "supported", "unsupported", "unsupported", "uncited", "bad_citation"]
    assert r["flagged"][0] == "Return shipping is free for loyalty members [2]." and len(r["flagged"]) == 4, f"flagged: {r['flagged']}"
    empty = grounding_report("", SPANS)
    assert empty["total"] == 0 and empty["grounded_ratio"] == 0.0, f"an empty answer has ratio 0.0: got {empty}"
