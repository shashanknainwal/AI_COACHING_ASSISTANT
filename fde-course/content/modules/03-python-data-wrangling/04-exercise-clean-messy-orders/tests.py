def test_parse_date_formats():
    """parse_date() reads all four formats and returns ISO strings"""
    cases = {"2026-03-04": "2026-03-04", " 03/05/2026 ": "2026-03-05", "Mar 6 2026": "2026-03-06", "06-Mar-2026": "2026-03-06"}
    for raw, want in cases.items():
        got = parse_date(raw)
        assert got == want, f"parse_date({raw!r}) should be {want!r}, got {got!r}"


def test_parse_date_rejects():
    """parse_date() returns None for missing, invalid, unknown-format and sentinel dates"""
    assert parse_date("2026-01-02") == "2026-01-02", "parse valid dates first (this test also checks rejects)"
    for raw in ["", "N/A", None, "2026-13-01", "2026/03/04", "1900-01-01", "2091-05-05", "March 6th"]:
        got = parse_date(raw)
        assert got is None, f"parse_date({raw!r}) should be None, got {got!r}"


def test_parse_money_formats():
    """parse_money() handles symbols, separators, codes and accounting negatives"""
    cases = {"$1,204.50": 1204.5, "USD 880": 880.0, "(45.00)": -45.0, "2200": 2200.0, "6,200": 6200.0,
             "$-3": -3.0, " 19.999 ": 20.0, "($1,000)": -1000.0}
    for raw, want in cases.items():
        got = parse_money(raw)
        assert got == want, f"parse_money({raw!r}) should be {want!r}, got {got!r}"


def test_parse_money_rejects():
    """parse_money() returns None for missing and non-numeric values"""
    assert parse_money("10") == 10.0, "parse valid amounts first (this test also checks rejects)"
    for raw in ["", "N/A", None, "12.3.4", "abc", "$", "1e5"]:
        got = parse_money(raw)
        assert got is None, f"parse_money({raw!r}) should be None, got {got!r}"


def test_normalize_phone():
    """normalize_phone() returns E.164 for valid US numbers"""
    cases = {"(555) 123-4567": "+15551234567", "555.987.6543 x12": "+15559876543", "1-555-222-3333": "+15552223333",
             "+1 (555) 010-0199": "+15550100199", "555-123-4567 EXT 9": "+15551234567"}
    for raw, want in cases.items():
        got = normalize_phone(raw)
        assert got == want, f"normalize_phone({raw!r}) should be {want!r}, got {got!r}"


def test_normalize_phone_rejects():
    """normalize_phone() returns None for missing, short and non-US numbers"""
    assert normalize_phone("5551234567") == "+15551234567", "normalize valid numbers first (this test also checks rejects)"
    for raw in ["", None, "123-4567", "2-555-222-3333", "+44 20 7946 0958"]:
        got = normalize_phone(raw)
        assert got is None, f"normalize_phone({raw!r}) should be None, got {got!r}"


def test_clean_orders_counts():
    """clean_orders() accepts 6 and rejects 4 rows from the sample"""
    result = clean_orders(ROWS)
    assert isinstance(result, tuple) and len(result) == 2, "return a tuple (clean, rejects)"
    clean, rejects = result
    assert [r["order_id"] for r in clean] == ["O-501", "O-502", "O-503", "O-504", "O-507", "O-509"], f"clean ids: got {[r['order_id'] for r in clean]}"
    assert len(rejects) == 4, f"expected 4 rejects, got {len(rejects)}"


def test_clean_row_shape():
    """Accepted rows are normalized: stripped/uppercased account, ISO date, float amount, E.164 or None phone"""
    clean, _ = clean_orders(ROWS)
    assert clean[0] == {"order_id": "O-501", "account_id": "A-1001", "order_date": "2026-03-04", "amount": 1204.5, "phone": "+15551234567"}, f"got {clean[0]}"
    assert clean[1]["account_id"] == "A-1003", "account_id should be stripped"
    assert clean[2]["phone"] is None, "a missing phone is allowed and stored as None"


def test_reject_reasons():
    """Rejects list every reason, in order, and catch duplicates of accepted rows"""
    _, rejects = clean_orders(ROWS)
    by_id = [(r["order_id"], r["reasons"]) for r in rejects]
    want = [("O-505", ["bad date"]), ("O-506", ["bad date", "bad amount", "bad phone"]),
            ("O-501", ["duplicate order_id"]), ("O-508", ["bad amount"])]
    assert by_id == want, f"expected {want}, got {by_id}"


def test_duplicate_only_counts_accepted_rows():
    """A rejected row doesn't block a later valid row with the same ID"""
    rows = [
        {"order_id": "X", "account_id": "a", "order_date": "bad", "amount": "1", "phone": ""},
        {"order_id": " X ", "account_id": "a", "order_date": "2026-01-01", "amount": "1", "phone": ""},
    ]
    clean, rejects = clean_orders(rows)
    assert [r["order_id"] for r in clean] == ["X"], "the second X is valid and the first was rejected, so it's not a duplicate"
    assert rejects == [{"order_id": "X", "reasons": ["bad date"]}], f"got {rejects}"
