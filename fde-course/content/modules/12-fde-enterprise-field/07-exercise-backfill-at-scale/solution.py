import pandas as pd

CHUNK = 10_000
# Claude Haiku 5.5, prompts under 100K tokens, run with effort "low".
# output_tokens already includes thinking tokens, which bill as output.
PRICE_IN_PER_MTOK = 0.10
PRICE_OUT_PER_MTOK = 0.50
COLUMNS = ["tickets", "refusals", "input_tokens", "output_tokens", "cost_usd"]


def cost(input_tokens, output_tokens):
    """US dollars for a number of input and output tokens (given)."""
    return (input_tokens * PRICE_IN_PER_MTOK + output_tokens * PRICE_OUT_PER_MTOK) / 1_000_000


def latest_attempts(path, chunksize=CHUNK):
    """Pass 1: ticket_id -> highest attempt number, reading only two columns."""
    latest = {}
    for chunk in pd.read_csv(path, usecols=["ticket_id", "attempt"], chunksize=chunksize):
        for tid, attempt in chunk.groupby("ticket_id")["attempt"].max().items():
            if attempt > latest.get(tid, 0):
                latest[tid] = int(attempt)
    return latest


def aggregate(path, chunksize=CHUNK):
    """Pass 2: per (month, category) totals over each ticket's latest attempt only."""
    latest = latest_attempts(path, chunksize)
    parts = []
    reader = pd.read_csv(path, chunksize=chunksize, dtype={"category": str}, keep_default_na=False)
    for chunk in reader:
        chunk = chunk[chunk["attempt"] == chunk["ticket_id"].map(latest)]
        chunk = chunk.assign(
            category=chunk["category"].replace("", "(none)"),
            tickets=1,
            refusals=(chunk["stop_reason"] == "refusal").astype(int),
        )
        parts.append(chunk.groupby(["month", "category"])[["tickets", "refusals", "input_tokens", "output_tokens"]].sum())
    table = pd.concat(parts).groupby(level=["month", "category"]).sum().sort_index()
    table["cost_usd"] = cost(table["input_tokens"], table["output_tokens"])
    return table[COLUMNS]


def retry_overhead(path, chunksize=CHUNK):
    """Dollars spent on attempts that a later attempt replaced."""
    latest = latest_attempts(path, chunksize)
    total = 0.0
    cols = ["ticket_id", "attempt", "input_tokens", "output_tokens"]
    for chunk in pd.read_csv(path, usecols=cols, chunksize=chunksize):
        old = chunk[chunk["attempt"] < chunk["ticket_id"].map(latest)]
        total += cost(int(old["input_tokens"].sum()), int(old["output_tokens"].sum()))
    return total


def report(table):
    """Headline numbers for Sana's update."""
    tickets = int(table["tickets"].sum())
    by_month = table.groupby(level="month")["tickets"].sum()
    by_cat = table.groupby(level="category")["tickets"].sum().drop("(none)", errors="ignore")
    busiest = by_month[by_month == by_month.max()].index.min()
    top = by_cat[by_cat == by_cat.max()].index.min()
    return {
        "tickets": tickets,
        "refusal_rate": round(int(table["refusals"].sum()) / tickets, 4),
        "cost_usd": round(float(table["cost_usd"].sum()), 2),
        "busiest_month": busiest,
        "top_category": top,
    }


# --- Try it out (not graded) ---
table = aggregate(RESULTS_PATH)
if table is not None:
    print(table.head(8))
    print(report(table))
overhead = retry_overhead(RESULTS_PATH)
if overhead is not None:
    print(f"Retry overhead: ${overhead:.2f}")
