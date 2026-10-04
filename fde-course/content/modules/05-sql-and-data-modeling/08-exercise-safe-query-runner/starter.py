import re
from fde_datasets import pinecrest

con = pinecrest.connect()

FORBIDDEN = ["insert", "update", "delete", "drop", "alter", "create", "replace",
             "attach", "detach", "pragma", "vacuum", "truncate", "grant"]


def strip_sql_comments(sql):
    """Replace /* block */ and -- line comments with a space."""
    # TODO
    pass


def clean_sql(sql):
    """No comments, no surrounding whitespace, no single trailing semicolon."""
    # TODO
    pass


def is_read_only(sql):
    """True only for a single SELECT/WITH statement with no forbidden keywords."""
    # TODO
    pass


def limited(sql, max_rows):
    """Wrap the query so it returns at most max_rows rows."""
    # TODO
    pass


def mask_email(email):
    """'maya@example.com' -> 'm***@example.com'."""
    # TODO
    pass


def mask_phone(phone):
    """'503-555-1234' -> '***-***-1234'."""
    # TODO
    pass


PII_MASKERS = {"email": mask_email, "phone": mask_phone}


def safe_query(con, sql, params=(), max_rows=100):
    """Run a read-only, row-limited, parameterized query with PII masked."""
    # TODO
    pass


def find_member(con, email):
    """Members with exactly this email (parameterized)."""
    # TODO
    pass


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
