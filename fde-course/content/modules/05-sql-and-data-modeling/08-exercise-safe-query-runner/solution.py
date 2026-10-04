import re
from fde_datasets import pinecrest

con = pinecrest.connect()

FORBIDDEN = ["insert", "update", "delete", "drop", "alter", "create", "replace",
             "attach", "detach", "pragma", "vacuum", "truncate", "grant"]


def strip_sql_comments(sql):
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def clean_sql(sql):
    s = strip_sql_comments(sql).strip()
    if s.endswith(";"):
        s = s[:-1].strip()
    return s


def is_read_only(sql):
    s = clean_sql(sql)
    if not s or ";" in s:
        return False
    lowered = s.lower()
    if lowered.split()[0] not in ("select", "with"):
        return False
    return not any(re.search(rf"\b{word}\b", lowered) for word in FORBIDDEN)


def limited(sql, max_rows):
    return f"SELECT * FROM ({clean_sql(sql)}) AS q LIMIT {int(max_rows)}"


def mask_email(email):
    if email is None:
        return None
    if "@" not in email:
        return "***"
    local, domain = email.rsplit("@", 1)
    return f"{local[:1]}***@{domain}"


def mask_phone(phone):
    if phone is None:
        return None
    digits = re.sub(r"\D", "", phone)
    return f"***-***-{digits[-4:]}"


PII_MASKERS = {"email": mask_email, "phone": mask_phone}


def safe_query(con, sql, params=(), max_rows=100):
    if not is_read_only(sql):
        raise PermissionError("only read-only SELECT queries are allowed")
    cur = con.execute(limited(sql, max_rows), params)
    columns = [d[0] for d in cur.description]
    rows = []
    for values in cur.fetchall():
        row = dict(zip(columns, values))
        for col, masker in PII_MASKERS.items():
            if col in row:
                row[col] = masker(row[col])
        rows.append(row)
    return rows


def find_member(con, email):
    return safe_query(con, "SELECT id, first_name, last_name, email FROM members WHERE email = ?", (email,))


# --- Try it out (not graded) ---
tries = [
    "SELECT id, first_name, email, phone FROM members ORDER BY id",
    "SELECT * FROM members; DROP TABLE members",
    "DELETE FROM visits",
    "/* harmless? */ UPDATE members SET email = NULL",
]
for sql in tries:
    print(f"{sql[:55]:<57} read_only={is_read_only(sql)}")

print()
try:
    for row in safe_query(con, tries[0], max_rows=3) or []:
        print(row)
    safe_query(con, tries[2])
except PermissionError as e:
    print("Blocked:", e)

print("\nfind_member (normal):   ", find_member(con, "ben.smith1@example.com"))
print("find_member (injection):", find_member(con, "x' OR '1'='1"))
