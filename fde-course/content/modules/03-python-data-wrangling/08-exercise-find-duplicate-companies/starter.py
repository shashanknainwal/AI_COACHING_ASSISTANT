import re
from difflib import SequenceMatcher

SUFFIXES = {"inc", "incorporated", "llc", "ltd", "limited", "corp", "corporation", "co", "company"}
FREE_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
MISSING_TOKENS = {"", "n/a", "na", "null", "none", "-"}

ACCOUNTS = [
    {"id": "A-1001", "name": "Acme Corp", "website": "https://www.acme.com/about"},
    {"id": "A-1002", "name": "Birch & Co", "website": "birchco.com"},
    {"id": "A-1003", "name": "Cobalt Rigging", "website": "http://cobaltrigging.com"},
    {"id": "A-1004", "name": "ACME Corporation, Inc.", "website": "buyer@acme.com"},
    {"id": "A-1007", "name": "Falcon Hydraulics", "website": "jim.falcon@gmail.com"},
    {"id": "A-1010", "name": "Cobalt Rigging LLC", "website": ""},
    {"id": "A-1015", "name": "Meridian Valves", "website": "meridianvalves.com"},
    {"id": "A-1017", "name": "Meridan Valves", "website": "N/A"},
    {"id": "A-1018", "name": "Birch and Company LLC", "website": "www.birchco.com"},
    {"id": "A-1019", "name": "Acme Pumps", "website": "acmepumps.com"},
    {"id": "A-1021", "name": "Ironclad Safety", "website": "sales@ironclad-safety.com"},
    {"id": "A-1022", "name": "Ironclad Safety Supply", "website": "https://ironclad-safety.com/contact"},
    {"id": "A-1023", "name": "Granite Works", "website": "orders@gmail.com"},
]


def normalize_company(name):
    """Lowercase, & -> and, no punctuation, no trailing legal suffixes."""
    # TODO
    pass


def domain(value):
    """Normalized domain from a URL or email address, or None."""
    # TODO
    pass


def similarity(a, b):
    """SequenceMatcher ratio of the normalized names, rounded to 2 decimals."""
    # TODO
    pass


def find_duplicates(records, threshold=0.85):
    """Candidate duplicate pairs with score and reason, best first."""
    # TODO
    pass


# --- Try it out (not graded) ---
for pair in find_duplicates(ACCOUNTS) or []:
    a, b = pair["ids"]
    print(f"{a} <-> {b}   score={pair['score']:<5} {pair['reason']}")
