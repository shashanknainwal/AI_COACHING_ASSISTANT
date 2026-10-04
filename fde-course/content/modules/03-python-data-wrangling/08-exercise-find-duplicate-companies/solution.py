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
    s = name.casefold().replace("&", " and ")
    words = re.sub(r"[^a-z0-9]+", " ", s).split()
    while words and words[-1] in SUFFIXES:
        words.pop()
    return " ".join(words)


def domain(value):
    if value is None or value.strip().lower() in MISSING_TOKENS:
        return None
    s = re.sub(r"^https?://", "", value.strip().lower())
    if "@" in s:
        s = s.split("@", 1)[1]
    s = s.split("/", 1)[0]
    if s.startswith("www."):
        s = s[4:]
    return s or None


def similarity(a, b):
    return round(SequenceMatcher(None, normalize_company(a), normalize_company(b)).ratio(), 2)


def _reason(a, b, threshold):
    if normalize_company(a["name"]) == normalize_company(b["name"]):
        return "same name"
    da, db = domain(a["website"]), domain(b["website"])
    if da and da == db and da not in FREE_DOMAINS:
        return "same domain"
    if similarity(a["name"], b["name"]) >= threshold:
        return "similar name"
    return None


def find_duplicates(records, threshold=0.85):
    pairs = []
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            a, b = records[i], records[j]
            reason = _reason(a, b, threshold)
            if reason:
                pairs.append({"ids": (a["id"], b["id"]), "score": similarity(a["name"], b["name"]), "reason": reason})
    return sorted(pairs, key=lambda p: (-p["score"], p["ids"]))


# --- Try it out (not graded) ---
for pair in find_duplicates(ACCOUNTS) or []:
    a, b = pair["ids"]
    print(f"{a} <-> {b}   score={pair['score']:<5} {pair['reason']}")
