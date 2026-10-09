def _gw():
    return Gateway()


# Level 1 ----------------------------------------------------------------
def test_l1_create_and_use():
    """create_key stores a quota, and record_usage returns what's left"""
    g = _gw()
    assert g.create_key(1, "k1", "acme", 1000) is True, "create_key should return True for a new key"
    got = g.record_usage(2, "k1", 300)
    assert got == 700, f"after using 300 of 1000, record_usage should return 700, got {got!r}"
    got = g.record_usage(3, "k1", 200)
    assert got == 500, f"a second use of 200 should leave 500, got {got!r}"
    assert g.get_remaining(4, "k1") == 500, "get_remaining should match the last record_usage result"


def test_l1_duplicates_and_missing():
    """Duplicate keys are refused and missing keys read as None"""
    g = _gw()
    g.create_key(1, "k1", "acme", 100)
    assert g.create_key(2, "k1", "other", 999) is False, "creating an existing key should return False"
    assert g.get_remaining(3, "k1") == 100, "a refused create must not change the key"
    assert g.record_usage(4, "nope", 10) is None, "record_usage on a missing key should return None"
    assert g.get_remaining(5, "nope") is None, "get_remaining on a missing key should return None"


def test_l1_over_quota_is_rejected_and_not_recorded():
    """A use that would exceed the quota returns -1 and records nothing"""
    g = _gw()
    g.create_key(1, "k1", "acme", 100)
    g.record_usage(2, "k1", 60)
    got = g.record_usage(3, "k1", 50)
    assert got == -1, f"60 + 50 > 100, so record_usage should return -1, got {got!r}"
    assert g.get_remaining(4, "k1") == 40, "a rejected use must not change the remaining quota"
    got = g.record_usage(5, "k1", 40)
    assert got == 0, f"using exactly the remaining 40 is allowed and leaves 0, got {got!r}"
    assert g.record_usage(6, "k1", 1) == -1, "with 0 left, any further use should return -1"


# Level 2 ----------------------------------------------------------------
def test_l2_top_owners_sums_across_keys():
    """top_owners sums tokens across an owner's keys, highest first"""
    g = _gw()
    g.create_key(1, "a1", "acme", 1000)
    g.create_key(2, "a2", "acme", 1000)
    g.create_key(3, "b1", "beta", 1000)
    g.record_usage(4, "a1", 100)
    g.record_usage(5, "a2", 250)
    g.record_usage(6, "b1", 300)
    got = g.top_owners(7, 2)
    assert got == ["acme(350)", "beta(300)"], f"expected ['acme(350)', 'beta(300)'], got {got!r}"


def test_l2_top_owners_ties_and_limits():
    """Ties break by owner name; n caps the list; owners with no usage show 0"""
    g = _gw()
    g.create_key(1, "z", "zeta", 500)
    g.create_key(2, "a", "alpha", 500)
    g.create_key(3, "m", "mid", 500)
    g.record_usage(4, "z", 200)
    g.record_usage(5, "a", 200)
    assert g.top_owners(6, 2) == ["alpha(200)", "zeta(200)"], "equal totals should sort by owner name"
    got = g.top_owners(7, 10)
    assert got == ["alpha(200)", "zeta(200)", "mid(0)"], f"n larger than owners returns all of them, got {got!r}"
    assert g.top_owners(8, 0) == [], "n of 0 should return []"


def test_l2_rejected_usage_does_not_count():
    """Rejected uses don't add to an owner's total"""
    g = _gw()
    g.create_key(1, "k", "acme", 100)
    g.record_usage(2, "k", 80)
    g.record_usage(3, "k", 50)
    assert g.top_owners(4, 1) == ["acme(80)"], "the rejected 50 must not be counted"


def test_l2_keys_for_sorted_with_remaining():
    """keys_for lists an owner's keys sorted by id as key(remaining)"""
    g = _gw()
    g.create_key(1, "prod", "acme", 1000)
    g.create_key(2, "dev", "acme", 200)
    g.create_key(3, "x", "beta", 50)
    g.record_usage(4, "prod", 400)
    got = g.keys_for(5, "acme")
    assert got == ["dev(200)", "prod(600)"], f"expected ['dev(200)', 'prod(600)'], got {got!r}"
    assert g.keys_for(6, "nobody") == [], "an owner with no keys should get []"


# Level 3 ----------------------------------------------------------------
def test_l3_rate_limit_blocks_with_minus_two():
    """Once max_requests uses fall inside the window, record_usage returns -2"""
    g = _gw()
    g.create_key(1, "k", "acme", 10000)
    assert g.set_rate_limit(2, "k", 2, 10) is True
    assert g.record_usage(3, "k", 10) == 9990
    assert g.record_usage(4, "k", 10) == 9980
    got = g.record_usage(5, "k", 10)
    assert got == -2, f"a third use within 10 time units of two others should return -2, got {got!r}"
    assert g.get_remaining(6, "k") == 9980, "a rate-limited use must not be recorded"
    assert g.set_rate_limit(7, "nope", 1, 1) is False, "set_rate_limit on a missing key should return False"


def test_l3_window_lower_bound_is_exclusive():
    """The window is (ts - window, ts]: a use at exactly ts - window has aged out"""
    g = _gw()
    g.create_key(1, "k", "acme", 1000)
    g.set_rate_limit(2, "k", 1, 10)
    g.record_usage(10, "k", 5)
    assert g.record_usage(19, "k", 5) == -2, "at ts=19, the use at t=10 is inside (9, 19]"
    got = g.record_usage(20, "k", 5)
    assert got == 990, f"at ts=20, the use at t=10 is outside (10, 20], so it should be accepted; got {got!r}"


def test_l3_rejected_uses_do_not_count_toward_limit():
    """Uses rejected for quota or rate limit don't count in the window"""
    g = _gw()
    g.create_key(1, "k", "acme", 100)
    g.set_rate_limit(2, "k", 2, 100)
    g.record_usage(3, "k", 90)
    assert g.record_usage(4, "k", 50) == -1, "50 more would exceed the quota"
    got = g.record_usage(5, "k", 10)
    assert got == 0, f"the quota-rejected use doesn't count, so this is the 2nd use in the window; got {got!r}"
    assert g.record_usage(6, "k", 1) == -2, "two recorded uses are in the window now"


def test_l3_limit_counts_earlier_uses_and_can_be_replaced():
    """A new limit counts uses made before it was set; a later limit replaces it"""
    g = _gw()
    g.create_key(1, "k", "acme", 1000)
    g.record_usage(2, "k", 1)
    g.record_usage(3, "k", 1)
    g.set_rate_limit(4, "k", 2, 50)
    assert g.record_usage(5, "k", 1) == -2, "the two uses at t=2 and t=3 count toward the new limit"
    g.set_rate_limit(6, "k", 5, 50)
    got = g.record_usage(7, "k", 1)
    assert got == 997, f"the new limit of 5 replaces the old one; got {got!r}"


# Level 4 ----------------------------------------------------------------
def test_l4_revoke_blocks_usage():
    """A revoked key rejects usage with None and can't be revoked or recreated"""
    g = _gw()
    g.create_key(1, "k", "acme", 1000)
    g.record_usage(2, "k", 100)
    assert g.revoke_key(3, "k") is True
    assert g.record_usage(4, "k", 10) is None, "record_usage on a revoked key should return None"
    assert g.get_remaining(5, "k") is None, "get_remaining on a revoked key should return None"
    assert g.revoke_key(6, "k") is False, "revoking twice should return False"
    assert g.revoke_key(7, "nope") is False, "revoking a missing key should return False"
    assert g.create_key(8, "k", "acme", 5) is False, "a revoked key id can't be created again"
    assert g.set_rate_limit(9, "k", 1, 1) is False, "set_rate_limit on a revoked key should return False"


def test_l4_revoked_keys_leave_rankings():
    """Revoked keys disappear from top_owners and keys_for"""
    g = _gw()
    g.create_key(1, "a1", "acme", 1000)
    g.create_key(2, "a2", "acme", 1000)
    g.create_key(3, "b1", "beta", 1000)
    g.record_usage(4, "a1", 500)
    g.record_usage(5, "a2", 10)
    g.record_usage(6, "b1", 100)
    g.revoke_key(7, "a1")
    got = g.top_owners(8, 5)
    assert got == ["beta(100)", "acme(10)"], f"a1's 500 tokens should no longer count, got {got!r}"
    assert g.keys_for(9, "acme") == ["a2(990)"], "keys_for should leave out revoked keys"
    g.revoke_key(10, "b1")
    assert g.top_owners(11, 5) == ["acme(10)"], "an owner with no active keys drops out"


def test_l4_usage_between_bounds():
    """usage_between counts accepted uses with start <= t < end"""
    g = _gw()
    g.create_key(1, "k", "acme", 1000)
    g.record_usage(10, "k", 1)
    g.record_usage(20, "k", 2)
    g.record_usage(30, "k", 4)
    g.record_usage(40, "k", 2000)
    got = g.usage_between(41, "k", 10, 30)
    assert got == 3, f"start=10 is included and end=30 is excluded, so expected 3, got {got!r}"
    assert g.usage_between(42, "k", 0, 100) == 7, "the rejected 2000 must not be counted"
    assert g.usage_between(43, "k", 50, 60) == 0, "no uses in the range should return 0"


def test_l4_usage_between_after_revoke():
    """usage_between still works for revoked keys; None only for keys that never existed"""
    g = _gw()
    g.create_key(1, "k", "acme", 1000)
    g.record_usage(2, "k", 300)
    g.revoke_key(3, "k")
    assert g.usage_between(4, "k", 0, 10) == 300, "history survives a revoke"
    assert g.usage_between(5, "ghost", 0, 10) is None, "a key that never existed should return None"
