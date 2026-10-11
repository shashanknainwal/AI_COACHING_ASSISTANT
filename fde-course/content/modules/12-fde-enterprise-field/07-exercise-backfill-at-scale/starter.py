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
    # TODO
    pass


def aggregate(path, chunksize=CHUNK):
    """Pass 2: per (month, category) totals over each ticket's latest attempt only."""
    # TODO
    pass


def retry_overhead(path, chunksize=CHUNK):
    """Dollars spent on attempts that a later attempt replaced."""
    # TODO
    pass


def report(table):
    """Headline numbers for Sana's update."""
    # TODO
    pass


# --- Try it out (not graded) ---
table = aggregate(RESULTS_PATH)
if table is not None:
    print(table.head(8))
    print(report(table))
overhead = retry_overhead(RESULTS_PATH)
if overhead is not None:
    print(f"Retry overhead: ${overhead:.2f}")
