---
title: "Exercise: A Text-to-SQL Assistant with Guardrails"
type: exercise
minutes: 30
hints:
  - "`schema_description`: `SELECT sql FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name`, then join the `sql` values with blank lines (`\"\\n\\n\"`)."
  - "`SQL_SCHEMA`: an object with string properties `sql` and `explanation`, both required, `additionalProperties: False`."
  - "`ask`: system prompt is `SYSTEM_TEMPLATE.format(schema=schema_description(con))`; the user message is just the question."
  - "After the API call: `max_tokens` → `ValueError(\"truncated\")`, `refusal` → `ValueError(\"refused\")`. Then find the text block and `json.loads` it."
  - "Check `is_read_only(sql)` yourself and raise `PermissionError(\"generated SQL is not read-only\")` before calling `safe_query`."
  - "Wrap only the `safe_query` call in `try/except sqlite3.Error as e`, and return the result dict with `rows=[]` and `error=str(e)`."
---

Pinecrest's location managers keep asking the data team simple questions. You'll build an "ask the data" assistant: Claude writes the SQL; your code makes sure it's safe, runs it with guardrails, and returns the answer with the SQL and explanation so a human can check it.

The `is_read_only` and `safe_query` helpers from the last exercise are included in the starter code.

## Your task

**1. `schema_description(con)`** returns the `CREATE` statements of every table **and view** in the database (skip SQLite's internal `sqlite_%` objects), ordered by name, joined with a blank line between them.

**2. `SQL_SCHEMA`**: a JSON Schema for `{"sql": "...", "explanation": "..."}` (both strings, both required, no extra properties).

**3. `ask(client, con, question, max_rows=50)`** returns:

```python
{"question": "...", "sql": "...", "explanation": "...", "rows": [...], "error": None}
```

Steps:
1. Call Claude with `model=MODEL`, `max_tokens` ≥ 2048, `system=SYSTEM_TEMPLATE.format(schema=schema_description(con))`, a single user message containing the question, and structured outputs with `SQL_SCHEMA`.
2. Raise `ValueError("truncated")` or `ValueError("refused")` for those stop reasons. Otherwise parse the JSON from the text block.
3. If the generated SQL isn't read-only, raise `PermissionError("generated SQL is not read-only")`. Never execute it.
4. Run it with `safe_query(con, sql, max_rows=max_rows)`. If the database raises `sqlite3.Error`, return the dict with `rows=[]` and `error` set to the error message instead of crashing.

Press **Run** to ask four questions, including one that tries to delete data and one that produces broken SQL. Then **Submit**.
