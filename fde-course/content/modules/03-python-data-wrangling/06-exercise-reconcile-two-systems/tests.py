def test_normalize_key():
    """normalize_key() handles case, whitespace, hyphens and leading zeros"""
    cases = {"A-1001": "A1001", "a1001": "A1001", "A-01003": "A1003", " A-1006 ": "A1006", "a - 0042": "A42",
             "A-000": "A0", "XY-0010": "XY10", "1234": "1234", "INV-2026-01": "INV202601"}
    for raw, want in cases.items():
        got = normalize_key(raw)
        assert got == want, f"normalize_key({raw!r}) should be {want!r}, got {got!r}"


def test_index_by_key():
    """index_by_key() maps normalized keys to rows"""
    idx = index_by_key(CRM, "account_id")
    assert isinstance(idx, dict) and len(idx) == 12, "expected 12 CRM accounts in the index"
    assert idx["A1004"]["name"] == "acme corporation", "keys should be normalized (A-1004 -> A1004)"


def test_index_by_key_duplicates_raise():
    """index_by_key() raises ValueError on keys that normalize to the same value"""
    rows = [{"k": "A-1003"}, {"k": "a01003"}]
    try:
        index_by_key(rows, "k")
    except ValueError as e:
        assert str(e) == "duplicate key: A1003", f"message should be 'duplicate key: A1003', got {str(e)!r}"
    else:
        raise AssertionError("expected ValueError for duplicate keys (the fan-out guard)")


def test_reconcile_groups():
    """reconcile() splits keys into matched, only_crm and only_billing (sorted)"""
    r = reconcile(CRM, BILLING)
    assert r["matched"] == ["A1001", "A1003", "A1004", "A1006", "A1007", "A1011", "A1012", "A1014", "A1015", "A1016"], f"matched: {r['matched']}"
    assert r["only_crm"] == ["A1009", "A1013"], f"only_crm: {r['only_crm']}"
    assert r["only_billing"] == ["A1020"], f"only_billing: {r['only_billing']}"


def test_reconcile_mismatches():
    """reconcile() reports real mismatches only, with original values"""
    r = reconcile(CRM, BILLING)
    want = [
        {"key": "A1004", "field": "plan", "crm": "Pro", "billing": "basic"},
        {"key": "A1006", "field": "mrr", "crm": "2450.50", "billing": "2405.50"},
        {"key": "A1015", "field": "mrr", "crm": "6200.00", "billing": "6000"},
    ]
    assert r["mismatches"] == want, f"expected {want}, got {r['mismatches']}"


def test_tolerance_and_plan_normalization():
    """'starter ' vs 'Starter' and 275.749 vs 275.75 are not mismatches; tolerance is respected"""
    crm = [{"account_id": "B-1", "name": "x", "plan": "Starter", "mrr": "100.00"}]
    billing = [{"customer_ref": "b1", "customer_name": "x", "plan": " starter ", "monthly_amount": "100.009"}]
    assert reconcile(crm, billing)["mismatches"] == [], "within one cent and same plan ignoring case/spaces"
    got = reconcile(crm, billing, tolerance=0.001)["mismatches"]
    assert [m["field"] for m in got] == ["mrr"], f"with tolerance 0.001 the amount differs; got {got}"


def test_mismatch_order_key_then_field():
    """Mismatches are ordered by key, then by FIELD_MAP order"""
    crm = [{"account_id": "Z-2", "name": "", "plan": "a", "mrr": "1"}, {"account_id": "Z-1", "name": "", "plan": "a", "mrr": "1"}]
    billing = [{"customer_ref": "Z2", "customer_name": "", "plan": "b", "monthly_amount": "2"},
               {"customer_ref": "Z1", "customer_name": "", "plan": "b", "monthly_amount": "2"}]
    got = [(m["key"], m["field"]) for m in reconcile(crm, billing)["mismatches"]]
    assert got == [("Z1", "plan"), ("Z1", "mrr"), ("Z2", "plan"), ("Z2", "mrr")], f"got {got}"


def test_summary():
    """summary() writes the one-line result"""
    got = summary(reconcile(CRM, BILLING))
    assert got == "10 matched, 2 only in CRM, 1 only in billing, 3 field mismatches", f"got {got!r}"
