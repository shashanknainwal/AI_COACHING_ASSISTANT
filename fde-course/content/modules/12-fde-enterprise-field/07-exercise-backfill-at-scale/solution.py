import csv
from collections import defaultdict
from itertools import islice

CHUNK = 10_000
# Claude Haiku 5.5, prompts under 100K tokens, run with effort "low".
# output_tokens already includes thinking tokens, which bill as output.
PRICE_IN_PER_MTOK = 0.10
PRICE_OUT_PER_MTOK = 0.50
INT_COLUMNS = ("attempt", "input_tokens", "output_tokens")


def cost(input_tokens, output_tokens):
    """US dollars for a number of input and output tokens (given)."""
    return (input_tokens * PRICE_IN_PER_MTOK + output_tokens * PRICE_OUT_PER_MTOK) / 1_000_000


def iter_chunks(path, chunksize=CHUNK):
    """Yield lists of at most `chunksize` rows (dicts, int columns converted)."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        while True:
            chunk = list(islice(reader, chunksize))
            if not chunk:
                return
            for row in chunk:
                for col in INT_COLUMNS:
                    row[col] = int(row[col])
            yield chunk


def latest_attempts(path, chunksize=CHUNK):
    """Pass 1: ticket_id -> highest attempt number."""
    latest = {}
    for chunk in iter_chunks(path, chunksize):
        for row in chunk:
            if row["attempt"] > latest.get(row["ticket_id"], 0):
                latest[row["ticket_id"]] = row["attempt"]
    return latest


def aggregate(path, chunksize=CHUNK):
    """Pass 2: per (month, category) totals over each ticket's latest attempt only."""
    latest = latest_attempts(path, chunksize)
    totals = defaultdict(lambda: {"tickets": 0, "refusals": 0, "input_tokens": 0, "output_tokens": 0})
    for chunk in iter_chunks(path, chunksize):
        for row in chunk:
            if row["attempt"] != latest[row["ticket_id"]]:
                continue
            t = totals[(row["month"], row["category"] or "(none)")]
            t["tickets"] += 1
            t["refusals"] += row["stop_reason"] == "refusal"
            t["input_tokens"] += row["input_tokens"]
            t["output_tokens"] += row["output_tokens"]
    table = {}
    for key in sorted(totals):
        t = dict(totals[key])
        t["cost_usd"] = cost(t["input_tokens"], t["output_tokens"])
        table[key] = t
    return table


def retry_overhead(path, chunksize=CHUNK):
    """Dollars spent on attempts that a later attempt replaced."""
    latest = latest_attempts(path, chunksize)
    tin = tout = 0
    for chunk in iter_chunks(path, chunksize):
        for row in chunk:
            if row["attempt"] < latest[row["ticket_id"]]:
                tin += row["input_tokens"]
                tout += row["output_tokens"]
    return cost(tin, tout)


def report(table):
    """Headline numbers for Sana's update."""
    tickets = sum(t["tickets"] for t in table.values())
    refusals = sum(t["refusals"] for t in table.values())
    by_month, by_cat = defaultdict(int), defaultdict(int)
    for (month, cat), t in table.items():
        by_month[month] += t["tickets"]
        if cat != "(none)":
            by_cat[cat] += t["tickets"]
    return {
        "tickets": tickets,
        "refusal_rate": round(refusals / tickets, 4),
        "cost_usd": round(sum(t["cost_usd"] for t in table.values()), 2),
        "busiest_month": min(by_month, key=lambda m: (-by_month[m], m)),
        "top_category": min(by_cat, key=lambda c: (-by_cat[c], c)),
    }


# --- Try it out (not graded) ---
table = aggregate(RESULTS_PATH)
if table:
    for key in list(table)[:8]:
        print(key, table[key])
    print(report(table))
overhead = retry_overhead(RESULTS_PATH)
if overhead is not None:
    print(f"Retry overhead: ${overhead:.2f}")
