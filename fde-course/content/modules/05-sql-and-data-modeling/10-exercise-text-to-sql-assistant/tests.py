import json
import anthropic
from anthropic import _sim
from fde_datasets import pinecrest


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def test_schema_description():
    """schema_description() lists every table and view CREATE statement, ordered by name"""
    db = pinecrest.connect()
    db.execute("CREATE VIEW v_test AS SELECT 1 AS x")
    got = schema_description(db)
    assert isinstance(got, str), "return a string"
    parts = got.split("\n\n")
    names = ["locations", "members", "payments", "plans", "subscriptions", "v_test", "visits"]
    assert len(parts) == len(names), f"expected {len(names)} CREATE statements separated by blank lines, got {len(parts)}"
    for part, name in zip(parts, names):
        assert part.startswith("CREATE") and name in part.split("(")[0], f"expected {name} in order; got {part[:40]!r}"
    assert "sqlite_" not in got, "skip SQLite's internal objects"


def test_sql_schema():
    """SQL_SCHEMA describes {sql, explanation}"""
    assert SQL_SCHEMA.get("type") == "object" and SQL_SCHEMA.get("additionalProperties") is False
    assert SQL_SCHEMA.get("properties") == {"sql": {"type": "string"}, "explanation": {"type": "string"}}
    assert sorted(SQL_SCHEMA.get("required", [])) == ["explanation", "sql"]


def test_ask_request():
    """ask() sends the schema in the system prompt and uses structured outputs"""
    _fresh()
    db = pinecrest.connect()
    ask(anthropic.Anthropic(), db, "How many active Premium members do we have?")
    req = _sim.last_request()
    assert req["model"] == "claude-opus-5-5" and req["max_tokens"] >= 2048
    assert req.get("system") == SYSTEM_TEMPLATE.format(schema=schema_description(db)), "system = SYSTEM_TEMPLATE filled with the schema"
    assert req["messages"] == [{"role": "user", "content": "How many active Premium members do we have?"}]
    fmt = (req.get("output_config") or {}).get("format") or {}
    assert fmt.get("type") == "json_schema" and fmt.get("schema") == SQL_SCHEMA


def test_ask_answers():
    """ask() returns the SQL, explanation and rows"""
    _fresh()
    got = ask(anthropic.Anthropic(), pinecrest.connect(), "Which location had the most visits in March 2026?")
    assert got["rows"] == [{"location": "Downtown", "visits": 258}], f"rows: {got['rows']}"
    assert got["error"] is None and got["sql"].startswith("SELECT") and got["explanation"]
    assert got["question"] == "Which location had the most visits in March 2026?"


def test_ask_refuses_writes_without_running_them():
    """A generated DELETE raises PermissionError and is never executed"""
    _fresh()
    db = pinecrest.connect()
    try:
        ask(anthropic.Anthropic(), db, "Please delete all members who cancelled")
    except PermissionError as e:
        assert str(e) == "generated SQL is not read-only", f"message: {str(e)!r}"
    else:
        raise AssertionError("expected PermissionError for generated DELETE")
    assert db.execute("SELECT COUNT(*) FROM members").fetchone()[0] == 120, "no members may be deleted"


def test_ask_handles_broken_sql():
    """SQL that fails returns an error instead of crashing"""
    _fresh()
    got = ask(anthropic.Anthropic(), pinecrest.connect(), "Which trainer ran the most sessions?")
    assert got["rows"] == [] and "no such table" in (got["error"] or ""), f"got {got}"


def test_ask_respects_max_rows():
    """max_rows is applied to the generated query"""
    _fresh()
    _sim.queue(json.dumps({"sql": "SELECT id FROM visits ORDER BY id", "explanation": "all visits"}))
    got = ask(anthropic.Anthropic(), pinecrest.connect(), "list visits", max_rows=5)
    assert got["rows"] == [{"id": i} for i in range(1, 6)], f"got {got['rows']}"


def test_ask_stop_reasons():
    """Truncated and refused responses raise ValueError"""
    for reply, msg in [(_sim.message(_sim.text('{"sql": "SEL'), stop_reason="max_tokens"), "truncated"), (_sim.refusal(), "refused")]:
        _fresh()
        _sim.queue(reply)
        try:
            ask(anthropic.Anthropic(), pinecrest.connect(), "anything")
        except ValueError as e:
            assert str(e) == msg, f"expected ValueError({msg!r}), got {str(e)!r}"
        else:
            raise AssertionError(f"expected ValueError({msg!r})")
