from fde_datasets import pinecrest


def test_strip_comments():
    """strip_sql_comments() removes block and line comments"""
    got = strip_sql_comments("SELECT 1 /* a\nb */ FROM t -- note\nWHERE x = 2")
    assert "/*" not in got and "--" not in got and "note" not in got, f"got {got!r}"
    assert "SELECT 1" in got and "FROM t" in got and "WHERE x = 2" in got, "keep the actual SQL"


def test_clean_sql():
    """clean_sql() strips comments, whitespace and one trailing semicolon"""
    assert clean_sql("  SELECT 1;  ") == "SELECT 1"
    assert clean_sql("-- hi\nSELECT 2 ;") == "SELECT 2"


def test_read_only_accepts():
    """is_read_only() accepts single SELECT and WITH queries"""
    for sql in ["SELECT * FROM members", "select id from plans;", "  WITH x AS (SELECT 1) SELECT * FROM x",
                "SELECT * FROM members -- just reading\n", "SELECT created_at FROM t"]:
        assert is_read_only(sql) is True, f"should be allowed: {sql!r}"


def test_read_only_rejects():
    """is_read_only() rejects writes, multiple statements, hidden statements and empty input"""
    for sql in ["DELETE FROM visits", "SELECT 1; DROP TABLE members", "UPDATE members SET email = NULL",
                "/* sneaky */ DROP TABLE plans", "PRAGMA table_info(members)",
                "WITH x AS (DELETE FROM visits RETURNING *) SELECT * FROM x", "", "   ", "-- only a comment",
                "INSERT INTO plans VALUES (9, 'x', 1)", "select * from members where id = 1 or 1=1;; "]:
        assert is_read_only(sql) is False, f"should be rejected: {sql!r}"


def test_limited():
    """limited() wraps the cleaned query with a LIMIT"""
    assert limited("SELECT * FROM members;", 5) == "SELECT * FROM (SELECT * FROM members) AS q LIMIT 5"
    db = pinecrest.connect()
    assert len(db.execute(limited("SELECT * FROM visits", 7)).fetchall()) == 7


def test_masks():
    """mask_email() and mask_phone() hide PII"""
    assert mask_email("maya.okafor@example.com") == "m***@example.com"
    assert mask_email("weird@sub@corp.com") == "w***@corp.com", "split on the last @"
    assert mask_email("no-at-sign") == "***" and mask_email(None) is None
    assert mask_phone("503-555-1234") == "***-***-1234"
    assert mask_phone("(503) 555 9876") == "***-***-9876" and mask_phone(None) is None


def test_safe_query_masks_and_limits():
    """safe_query() returns dicts, applies max_rows and masks PII columns"""
    db = pinecrest.connect()
    rows = safe_query(db, "SELECT id, first_name, email, phone FROM members ORDER BY id", max_rows=2)
    assert rows == [{"id": 1, "first_name": "Ben", "email": "b***@example.com", "phone": "***-***-2697"},
                    {"id": 2, "first_name": "Hiro", "email": "h***@example.com", "phone": "***-***-7227"}], f"got {rows}"


def test_safe_query_params_and_blocking():
    """safe_query() passes params and blocks writes with PermissionError"""
    db = pinecrest.connect()
    rows = safe_query(db, "SELECT name FROM plans WHERE monthly_price > ? ORDER BY monthly_price", (40,))
    assert rows == [{"name": "Plus"}, {"name": "Premium"}], f"got {rows}"
    try:
        safe_query(db, "DELETE FROM visits")
    except PermissionError as e:
        assert str(e) == "only read-only SELECT queries are allowed", f"message: {str(e)!r}"
    else:
        raise AssertionError("expected PermissionError for a DELETE")
    assert db.execute("SELECT COUNT(*) FROM visits").fetchone()[0] == 2538, "the DELETE must never run"


def test_find_member_and_injection():
    """find_member() finds by exact email and is immune to injection"""
    db = pinecrest.connect()
    assert find_member(db, "ben.smith1@example.com") == [{"id": 1, "first_name": "Ben", "last_name": "Smith", "email": "b***@example.com"}]
    assert find_member(db, "x' OR '1'='1") == [], "an injection attempt must return no rows (use a ? parameter)"
