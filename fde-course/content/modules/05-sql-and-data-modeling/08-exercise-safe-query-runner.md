---
title: "Exercise: Build a Safe Query Runner"
type: exercise
minutes: 30
hints:
  - "`strip_sql_comments`: `re.sub(r\"/\\*.*?\\*/\", \" \", sql, flags=re.S)` removes block comments; then `re.sub(r\"--[^\\n]*\", \" \", ...)` removes line comments."
  - "`clean_sql`: strip comments, `.strip()`, then remove one trailing `;` and strip again."
  - "`is_read_only`: empty → False; any remaining `;` → False; the first word (lowercased) must be `select` or `with`; then `re.search(rf\"\\b{word}\\b\", lowered)` for each word in FORBIDDEN."
  - "`limited`: `f\"SELECT * FROM ({clean_sql(sql)}) AS q LIMIT {int(max_rows)}\"`."
  - "`mask_email`: split on the last `@` with `email.rsplit(\"@\", 1)`."
  - "In `safe_query`, build dicts with `dict(zip(columns, row))`, then replace any column found in `PII_MASKERS` with the masked value."
---

The Pinecrest data team wants a small helper that analysts and (later) the AI assistant can use to run ad-hoc SQL against the reporting replica. Security agreed, on four conditions: **read-only queries only, row limits, query parameters, and masked personal data by default.** Build it.

## Your task

**1. `strip_sql_comments(sql)`** removes `/* block */` comments and `-- line` comments (replace each with a space).

**2. `clean_sql(sql)`** strips comments and surrounding whitespace, and removes **one** trailing semicolon.

**3. `is_read_only(sql)`** returns `True` only if, after `clean_sql`:
- the SQL isn't empty,
- it contains **no** semicolon (so only one statement),
- its first word is `select` or `with` (any case), and
- none of the words in `FORBIDDEN` appear as whole words (any case).

**4. `limited(sql, max_rows)`** returns `"SELECT * FROM (<clean sql>) AS q LIMIT <max_rows>"`.

**5. `mask_email(email)`** → `"m***@example.com"` (first character, `***`, then `@domain`). `None` → `None`; a value with no `@` → `"***"`.
**`mask_phone(phone)`** → `"***-***-1234"` (last 4 digits). `None` → `None`.

**6. `safe_query(con, sql, params=(), max_rows=100)`**:
- If `is_read_only(sql)` is false, raise `PermissionError("only read-only SELECT queries are allowed")`.
- Execute `limited(sql, max_rows)` **with** `params`.
- Return a list of dicts (column → value), with every column named in `PII_MASKERS` masked.

**7. `find_member(con, email)`** returns `safe_query` results for `id, first_name, last_name, email` of members with that exact email, using a **parameter**. A malicious input like `x' OR '1'='1` must return `[]`.

Press **Run** to try safe and unsafe queries, then **Submit**.
