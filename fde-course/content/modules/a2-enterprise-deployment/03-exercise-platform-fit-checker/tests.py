import copy

_NON_ZDR = ["batches", "files_api"]


def _p(procurement=("direct",), processor="anthropic", geos=("global", "us"), features=(), zdr="yes", net="no"):
    return {
        "label": "Test platform",
        "procurement": list(procurement),
        "processor": processor,
        "geos": list(geos),
        "features": list(features),
        "zdr": zdr,
        "private_network": net,
    }


def _check(platform, req, non_zdr=_NON_ZDR):
    r = check_platform("p", platform, req, non_zdr)
    assert isinstance(r, dict), f"check_platform should return a dict, got {r!r}"
    return r


def _prefixes(items):
    return [s.split(":", 1)[0] for s in items]


def test_result_shape():
    """check_platform() returns platform, eligible, reasons, gaps and open_items"""
    r = _check(_p(), {})
    for key in ("platform", "eligible", "reasons", "gaps", "open_items"):
        assert key in r, f"result is missing the key {key!r}: {r!r}"
    assert r["platform"] == "p", f"platform should echo the name passed in, got {r['platform']!r}"
    assert r["eligible"] is True and r["gaps"] == [] and r["open_items"] == [], \
        f"an empty requirements dict should make any platform eligible with no gaps, got {r!r}"


def test_procurement_gap_and_reason():
    """Procurement through the wrong cloud is a gap; the right one is a reason"""
    r = _check(_p(procurement=["aws"]), {"procurement": "azure"})
    assert r["eligible"] is False, "needing azure on an aws-only platform should block it"
    assert _prefixes(r["gaps"]) == ["procurement"], f"expected one 'procurement:' gap, got {r['gaps']!r}"
    assert "azure" in r["gaps"][0], f"the gap should name what's needed (azure): {r['gaps'][0]!r}"
    ok = _check(_p(procurement=["aws"]), {"procurement": "aws"})
    assert ok["eligible"] and "procurement" in _prefixes(ok["reasons"]), \
        f"a match should add a 'procurement:' reason, got {ok['reasons']!r}"


def test_processor_and_geo():
    """Processor and geo mismatches are gaps that name the requirement"""
    r = _check(_p(processor="anthropic", geos=["global", "us"]), {"processor": "cloud_provider", "geo": "eu"})
    assert _prefixes(r["gaps"]) == ["processor", "geo"], f"expected gaps in order processor, geo; got {r['gaps']!r}"
    assert "eu" in r["gaps"][1], f"the geo gap should name eu: {r['gaps'][1]!r}"
    ok = _check(_p(geos=["global", "eu"]), {"geo": "eu"})
    assert ok["eligible"] and "geo" in _prefixes(ok["reasons"]), f"eu offered should be a reason, got {ok!r}"


def test_missing_features_each_listed():
    """Each missing feature is its own gap, in requirement order"""
    r = _check(_p(features=["prompt_caching"]), {"features": ["batches", "prompt_caching", "code_execution"]})
    feature_gaps = [g for g in r["gaps"] if g.startswith("feature:")]
    assert len(feature_gaps) == 2, f"expected 2 feature gaps (batches, code_execution), got {r['gaps']!r}"
    assert "batches" in feature_gaps[0] and "code_execution" in feature_gaps[1], \
        f"feature gaps should follow the requirement order: {feature_gaps!r}"
    assert any(s.startswith("feature:") and "prompt_caching" in s for s in r["reasons"]), \
        f"an available feature should appear as a 'feature:' reason, got {r['reasons']!r}"


def test_zdr_yes_confirm_no():
    """ZDR: 'yes' is a reason, 'confirm' is an open item (still eligible), 'no' is a gap"""
    yes = _check(_p(zdr="yes"), {"zdr": True})
    assert yes["eligible"] and "zdr" in _prefixes(yes["reasons"]), f"zdr 'yes' should be a reason: {yes!r}"
    confirm = _check(_p(zdr="confirm"), {"zdr": True})
    assert confirm["eligible"] is True, "'confirm' is an open item, not a blocker"
    assert _prefixes(confirm["open_items"]) == ["zdr"], f"expected one 'zdr:' open item, got {confirm['open_items']!r}"
    no = _check(_p(zdr="no"), {"zdr": True})
    assert no["eligible"] is False and _prefixes(no["gaps"]) == ["zdr"], f"zdr 'no' should be a gap: {no!r}"
    skip = _check(_p(zdr="no"), {"zdr": False})
    assert skip["eligible"] is True, "when ZDR isn't required, the platform's ZDR status shouldn't matter"


def test_zdr_conflict_with_feature():
    """Requiring ZDR plus a non-ZDR feature is a 'conflict:' gap, even if the platform has the feature"""
    r = _check(_p(features=["batches", "prompt_caching"], zdr="yes"), {"zdr": True, "features": ["prompt_caching", "batches"]})
    assert r["eligible"] is False, "batches under ZDR should block the platform"
    conflicts = [g for g in r["gaps"] if g.startswith("conflict:")]
    assert len(conflicts) == 1 and "batches" in conflicts[0], f"expected one conflict naming batches, got {r['gaps']!r}"
    uses_arg = _check(_p(features=["batches"], zdr="yes"), {"zdr": True, "features": ["batches"]}, non_zdr=[])
    assert uses_arg["eligible"] is True, "use the non_zdr_features argument, not a hard-coded list"


def test_private_network():
    """Private networking follows the same yes/confirm/no rule with a 'network:' prefix"""
    assert _check(_p(net="yes"), {"private_network": True})["eligible"] is True
    c = _check(_p(net="confirm"), {"private_network": True})
    assert c["eligible"] is True and _prefixes(c["open_items"]) == ["network"], f"expected a 'network:' open item: {c!r}"
    n = _check(_p(net="no"), {"private_network": True})
    assert n["eligible"] is False and _prefixes(n["gaps"]) == ["network"], f"expected a 'network:' gap: {n!r}"


def test_gap_order():
    """Gaps come in the order procurement, processor, geo, feature, zdr, conflict, network"""
    plat = _p(procurement=["gcp"], processor="cloud_provider", geos=["global"], features=[], zdr="no", net="no")
    req = {"procurement": "aws", "processor": "anthropic", "geo": "us", "features": ["batches"],
           "zdr": True, "private_network": True}
    r = _check(plat, req)
    assert _prefixes(r["gaps"]) == ["procurement", "processor", "geo", "feature", "zdr", "conflict", "network"], \
        f"gap order is wrong: {_prefixes(r['gaps'])!r}"


def test_shortlist_ranks_and_blocks():
    """shortlist() puts platforms with fewer open items first and lists gaps for blocked ones"""
    platforms = {
        "zeta": _p(procurement=["aws"], zdr="yes", net="yes"),
        "alpha": _p(procurement=["aws"], zdr="confirm", net="yes"),
        "beta": _p(procurement=["aws"], zdr="yes", net="yes"),
        "gamma": _p(procurement=["gcp"], zdr="yes", net="yes"),
    }
    before = copy.deepcopy(platforms)
    req = {"procurement": "aws", "zdr": True, "private_network": True}
    s = shortlist(platforms, req, _NON_ZDR)
    assert isinstance(s, dict), f"shortlist should return a dict, got {s!r}"
    assert s.get("eligible") == ["beta", "zeta", "alpha"], \
        f"expected ['beta', 'zeta', 'alpha'] (0 open items alphabetically, then 1), got {s.get('eligible')!r}"
    assert list(s.get("blocked", {})) == ["gamma"], f"only gamma should be blocked, got {s.get('blocked')!r}"
    assert s["blocked"]["gamma"][0].startswith("procurement:"), f"gamma's gaps should explain why: {s['blocked']['gamma']!r}"
    assert platforms == before, "shortlist() must not modify the capability table"


def test_shortlist_on_course_table():
    """On the lesson's table, an AWS buyer needing Batches and private networking gets Claude Platform on AWS"""
    req = {"procurement": "aws", "geo": "us", "features": ["prompt_caching", "batches"], "private_network": True}
    s = shortlist(PLATFORMS, req, NON_ZDR_FEATURES)
    assert s["eligible"] == ["claude_platform_aws"], f"expected only claude_platform_aws, got {s['eligible']!r}"
    assert any("batches" in g for g in s["blocked"]["bedrock"]), \
        f"bedrock should be blocked for missing batches: {s['blocked'].get('bedrock')!r}"
