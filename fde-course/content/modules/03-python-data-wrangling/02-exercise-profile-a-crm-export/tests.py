def test_is_missing():
    """is_missing() catches None, blanks and disguised blanks"""
    for v in [None, "", "   ", "N/A", "n/a", "NULL", "-", " Unknown ", "none", "NA"]:
        assert is_missing(v) is True, f"{v!r} should count as missing"
    for v in ["0", "Acme", "no", "1900-01-01"]:
        assert is_missing(v) is False, f"{v!r} is a real value, not missing"


def test_infer_type_numbers():
    """infer_type() distinguishes int and float, ignoring missing values"""
    assert infer_type(["1", "-7", " 42 ", "N/A"]) == "int", "whole numbers (with a missing value) should be 'int'"
    assert infer_type(["1", "2.5"]) == "float", "a mix of 1 and 2.5 should be 'float'"
    assert infer_type(["1,200"]) == "text", "a number with a comma is still text until cleaned"


def test_infer_type_dates_text_empty():
    """infer_type() detects ISO dates, text and empty columns"""
    assert infer_type(["2024-02-29", "2019-04-02"]) == "date", "valid ISO dates should be 'date'"
    assert infer_type(["2023-02-29"]) == "text", "2023-02-29 isn't a real date, so it's text"
    assert infer_type(["2024-01-01", "03/15/2021"]) == "text", "mixed date formats should be 'text'"
    assert infer_type(["", "-", None]) == "empty", "only missing values should be 'empty'"


def test_profile_column_industry():
    """profile_column() matches the example for 'industry'"""
    got = profile_column(ROWS, "industry")
    want = {"column": "industry", "missing": 3, "missing_pct": 18.8, "distinct": 5, "top": "Manufacturing", "type": "text"}
    assert got == want, f"expected {want}, got {got}"


def test_profile_column_ties_and_strip():
    """Values are stripped; ties for top are broken alphabetically"""
    rows = [{"c": " b "}, {"c": "a"}, {"c": "b"}, {"c": "a"}, {"c": "N/A"}]
    got = profile_column(rows, "c")
    assert got["distinct"] == 2, f"' b ' and 'b' are the same value after strip; got distinct={got['distinct']}"
    assert got["top"] == "a", f"'a' and 'b' both appear twice; alphabetical first is 'a', got {got['top']!r}"
    assert got["missing"] == 1 and got["missing_pct"] == 20.0, f"1 of 5 missing should be 20.0%, got {got['missing_pct']}"


def test_profile_column_all_missing():
    """A fully missing column has top None and type 'empty'"""
    got = profile_column([{"c": ""}, {"c": "-"}], "c")
    assert got["top"] is None and got["type"] == "empty" and got["missing_pct"] == 100.0, f"got {got}"


def test_profile_all_columns():
    """profile() returns one entry per column, in order"""
    got = profile(ROWS)
    assert [p["column"] for p in got] == list(ROWS[0]), "columns should follow the order of the first row's keys"
    by = {p["column"]: p for p in got}
    assert by["employees"]["type"] == "int", "employees should infer as 'int' ('n/a' is missing)"
    assert by["annual_revenue"]["type"] == "text", "annual_revenue contains '1,200,000', so it's 'text'"
    assert profile([]) == [], "no rows should give []"


def test_duplicate_values():
    """duplicate_values() finds the repeated account ID"""
    assert duplicate_values(ROWS, "account_id") == ["A-1003"], f"got {duplicate_values(ROWS, 'account_id')!r}"
    rows = [{"k": "x "}, {"k": "x"}, {"k": ""}, {"k": ""}, {"k": "b"}, {"k": "b"}]
    assert duplicate_values(rows, "k") == ["b", "x"], "missing values never count as duplicates; results are sorted"
