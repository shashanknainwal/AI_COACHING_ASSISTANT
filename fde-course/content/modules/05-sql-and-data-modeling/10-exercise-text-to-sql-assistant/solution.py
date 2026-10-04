import json
import re
import sqlite3
import anthropic
from fde_datasets import pinecrest

client = anthropic.Anthropic()
con = pinecrest.connect()
MODEL = "claude-opus-5-5"

SYSTEM_TEMPLATE = """You write SQLite queries for Pinecrest Fitness's reporting database.

Schema:
{schema}

Rules:
- Write a single read-only SELECT query in the SQLite dialect.
- "Active member" means a subscription with status = 'active'. subscriptions.status is 'active' or 'cancelled'.
- A member's home location is members.home_location_id; a visit's location is visits.location_id.
- If the question can't be answered from this schema, return SELECT NULL and say why in the explanation."""

# --- Helpers from the previous exercise (given) ---------------------------------
FORBIDDEN = ["insert", "update", "delete", "drop", "alter", "create", "replace",
             "attach", "detach", "pragma", "vacuum", "truncate", "grant"]


def clean_sql(sql):
    s = re.sub(r"--[^\n]*", " ", re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)).strip()
    return s[:-1].strip() if s.endswith(";") else s


def is_read_only(sql):
    s = clean_sql(sql)
    if not s or ";" in s or s.lower().split()[0] not in ("select", "with"):
        return False
    return not any(re.search(rf"\b{w}\b", s.lower()) for w in FORBIDDEN)


def safe_query(con, sql, params=(), max_rows=100):
    if not is_read_only(sql):
        raise PermissionError("only read-only SELECT queries are allowed")
    cur = con.execute(f"SELECT * FROM ({clean_sql(sql)}) AS q LIMIT {int(max_rows)}", params)
    columns = [d[0] for d in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]
# ---------------------------------------------------------------------------------


def schema_description(con):
    rows = con.execute(
        "SELECT sql FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return "\n\n".join(r[0] for r in rows)


SQL_SCHEMA = {
    "type": "object",
    "properties": {"sql": {"type": "string"}, "explanation": {"type": "string"}},
    "required": ["sql", "explanation"],
    "additionalProperties": False,
}


def ask(client, con, question, max_rows=50):
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_TEMPLATE.format(schema=schema_description(con)),
        messages=[{"role": "user", "content": question}],
        output_config={"format": {"type": "json_schema", "schema": SQL_SCHEMA}},
    )
    if response.stop_reason == "max_tokens":
        raise ValueError("truncated")
    if response.stop_reason == "refusal":
        raise ValueError("refused")
    answer = json.loads(next(b.text for b in response.content if b.type == "text"))
    sql = answer["sql"]
    if not is_read_only(sql):
        raise PermissionError("generated SQL is not read-only")
    result = {"question": question, "sql": sql, "explanation": answer["explanation"], "rows": [], "error": None}
    try:
        result["rows"] = safe_query(con, sql, max_rows=max_rows)
    except sqlite3.Error as e:
        result["error"] = str(e)
    return result


# --- Try it out (not graded) ---
questions = [
    "Which location had the most visits in March 2026?",
    "How many active Premium members do we have?",
    "Please delete all members who cancelled",
    "Which trainer ran the most sessions?",
]
for q in questions:
    print("Q:", q)
    try:
        answer = ask(client, con, q)
        if answer:
            print("   SQL:  ", answer["sql"][:90] + ("..." if len(answer["sql"]) > 90 else ""))
            print("   Why:  ", answer["explanation"])
            print("   Rows: ", answer["rows"], "| error:", answer["error"])
    except PermissionError as e:
        print("   Refused:", e)
    print()
