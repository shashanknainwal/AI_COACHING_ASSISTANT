import re as _re


def _norm(t):
    t = _re.sub(r"\d+", "#", t.lower())
    return " ".join(_re.sub(r"[^a-z# ]", " ", t).split())


def _sh(t):
    w = _norm(t).split()
    return {" ".join(w)} if len(w) < 3 else {" ".join(w[i:i + 3]) for i in range(len(w) - 2)}


def _jac(a, b):
    x, y = _sh(a), _sh(b)
    return len(x & y) / len(x | y)


def _case(cid, text, intent="close_account", tone="neutral"):
    return {"id": cid, "seed": "SD3", "text": text, "expected": {"intent": intent, "account": "GN-1", "amount": None},
            "axes": {"tone": tone, "channel": "chat", "typo": False}}


def test_generate_is_deterministic_and_complete():
    """generate() gives the same cases every time, per_seed for each seed"""
    a, b = generate(SEEDS, 6), generate(SEEDS, 6)
    assert a and len(a) == 48, f"8 seeds x 6 = 48 cases, got {a and len(a)}"
    assert a == b, "same seeds in, same cases out: use random.Random(f\"{seed_id}:{i}\") per case"
    assert [c["id"] for c in a[:7]] == ["SD1-s00", "SD1-s01", "SD1-s02", "SD1-s03", "SD1-s04", "SD1-s05", "SD2-s00"]
    assert generate(SEEDS[:1], 3) == a[:3], "a case doesn't depend on the other seeds or on per_seed"


def test_generated_cases_are_varied():
    """generate() spreads cases over tones, channels and typos"""
    cases = generate(SEEDS, 6)
    tones = {c["axes"]["tone"] for c in cases}
    channels = {c["axes"]["channel"] for c in cases}
    assert tones == set(TONES) and channels == set(CHANNELS), f"every tone and channel should appear: {tones}, {channels}"
    assert 5 <= sum(c["axes"]["typo"] for c in cases) <= 25, "about 30% of cases should get a typo"
    assert len({c["expected"]["account"] for c in cases}) == 48, "every case gets its own account number"
    assert len({_norm(c["text"]) for c in cases}) >= 30, "most cases should differ beyond their digits"


def test_labels_stay_true():
    """Every synthetic case keeps its seed's intent and contains its own slot values"""
    by_seed = {s["id"]: s for s in SEEDS}
    for c in generate(SEEDS, 6):
        seed = by_seed[c["seed"]]
        assert c["expected"]["intent"] == seed["intent"], f"{c['id']}: the intent comes from the seed"
        assert _re.fullmatch(r"GN-\d{6}", c["expected"]["account"]), f"{c['id']}: account must look like GN-123456"
        assert c["expected"]["account"].lower() in c["text"].lower(), f"{c['id']}: the account number must be in the text: {c['text']!r}"
        if seed["amounts"]:
            assert c["expected"]["amount"] in seed["amounts"] and f"${c['expected']['amount']}" in c["text"], \
                f"{c['id']}: the amount must be one of the seed's and appear in the text"
        else:
            assert c["expected"]["amount"] is None
        if c["axes"]["channel"] == "sms":
            assert c["text"] == c["text"].lower() and not _re.search(r"[.,!?;:]", c["text"]), f"{c['id']}: sms is lowercase, no punctuation"
        if c["axes"]["channel"] == "email":
            assert c["text"].startswith("Subject: Moving house\n\nHello,\n\n") and c["text"].endswith("\n\nRegards")


def test_similarity():
    """normalize(), shingles() and jaccard() ignore digits, case and punctuation"""
    assert normalize("Close GN-771203, please!") == "close gn # please", f"got {normalize('Close GN-771203, please!')!r}"
    assert shingles("a b") == {"a b"} and shingles("a b c d") == {"a b c", "b c d"}
    assert jaccard("Please close GN-1, now.", "please CLOSE gn-999 now") == 1.0
    assert abs(jaccard("a b c d", "a b c e") - 1 / 3) < 1e-9, "1 shared shingle out of 3 distinct ones"


def test_dedupe_and_decontaminate():
    """dedupe() keeps the first of each near-duplicate group; decontaminate() drops test-set lookalikes"""
    cases = [_case("x1", "Please close account GN-111111, I've sold the flat."),
             _case("x2", "please close account gn-222222 i've sold the flat"),
             _case("x3", "Can I take my EV Night tariff with me when I move?"),
             _case("x4", "Please close account GN-333333, I have sold the flat today.")]
    kept, dropped = dedupe(cases)
    assert [c["id"] for c in kept] == ["x1", "x3", "x4"] and dropped == [("x2", "x1")], f"got {[c['id'] for c in kept]}, {dropped}"
    kept, dropped = decontaminate(cases, ["Please close account GN-771203, I've sold the flat."])
    assert dropped == ["x1", "x2"] and [c["id"] for c in kept] == ["x3", "x4"], f"got {dropped}"


def test_build_suite():
    """build_suite() returns a clean, deduplicated suite with no test-set leaks"""
    s = build_suite(SEEDS, 6, HELD_OUT)
    assert s, "build_suite() returned nothing"
    cases = s["cases"]
    assert 25 <= len(cases) < 48, f"some near-duplicates must be dropped, got {len(cases)} kept"
    assert len(cases) + len(s["dropped_duplicates"]) + len(s["dropped_contaminated"]) == 48
    for i, a in enumerate(cases):
        for b in cases[i + 1:]:
            assert _jac(a["text"], b["text"]) < 0.8, f"{a['id']} and {b['id']} are near-duplicates"
        for h in HELD_OUT:
            assert _jac(a["text"], h) < 0.8, f"{a['id']} leaks a held-out test case"
    assert s["missing_coverage"] == coverage_gaps(cases)
    gaps = coverage_gaps([_case("a", "x", "close_account", "angry"), _case("b", "y", "open_new", "terse")])
    assert ("close_account", "neutral") in gaps and ("open_new", "terse") not in gaps and len(gaps) == 6, f"got {gaps}"
