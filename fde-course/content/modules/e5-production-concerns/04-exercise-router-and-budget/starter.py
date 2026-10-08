OPUS, SONNET, HAIKU = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"

# US dollars per million tokens. Haiku's cache rates are left out on purpose:
# add them from the pricing page before Ledgerline caches anything on Haiku.
PRICES = {
    OPUS: {"input": 4.00, "output": 20.00, "cache_write_5m": 5.00, "cache_write_1h": 8.00, "cache_read": 0.20},
    SONNET: {"input": 2.00, "output": 10.00, "cache_write_5m": 2.50, "cache_write_1h": 4.00, "cache_read": 0.20},
    HAIKU: {"input": 0.10, "output": 0.50},
}
BATCH_DISCOUNT = 0.5          # the Batch API bills every token type at half price
HAIKU_MAX_INPUT = 100_000     # Haiku 5.5's listed price applies to prompts up to 100K tokens
LADDER = [HAIKU, SONNET, OPUS]  # cheapest to most capable

ROUTES = {
    "classify_email":  {"model": HAIKU,  "effort": "low",    "max_tokens": 512},
    "extract_invoice": {"model": HAIKU,  "effort": "low",    "max_tokens": 2048},
    "draft_reply":     {"model": SONNET, "effort": "medium", "max_tokens": 4096},
    "audit_anomaly":   {"model": OPUS,   "effort": "medium", "max_tokens": 16000},
}
# Tasks where a cheaper model is acceptable when the day's budget is tight.
DEGRADABLE = {"classify_email", "extract_invoice", "draft_reply"}


class BudgetExceeded(Exception):
    pass


def route(task, input_tokens, complexity="normal"):
    """{"model", "effort", "max_tokens"} for a task, adjusted for complexity and prompt size."""
    # TODO
    pass


def call_cost(model, usage, prices=PRICES, batch=False):
    """Dollar cost of one call from its usage dict, rounded to 6 decimals."""
    # TODO
    pass


def worst_case_cost(r, input_tokens, prices=PRICES):
    """Upper bound before the call: every input token uncached, output runs to max_tokens."""
    # TODO
    pass


class BudgetGuard:
    def __init__(self, daily_budget_usd, prices=PRICES):
        self.daily_budget_usd = daily_budget_usd
        self.prices = prices
        self._days = {}

    def _day(self, day):
        return self._days.setdefault(day, {"spent": 0.0, "by_model": {}, "tasks": {}})

    def spent(self, day):
        return round(self._day(day)["spent"], 6)

    def admit(self, task, input_tokens, day, complexity="normal"):
        """Pick a route that fits the day's remaining budget, stepping down the ladder if allowed."""
        # TODO
        pass

    def record(self, day, task, model, usage, completed, batch=False):
        """Add one call's actual cost to the day. Returns that cost."""
        # TODO
        pass

    def report(self, day):
        """{"spent", "remaining", "by_model", "cost_per_completed"} for one day."""
        # TODO
        pass


# --- Try it out (not graded) ---
guard = BudgetGuard(daily_budget_usd=0.30)
day = "2026-10-30"
traffic = [
    # task, input tokens, complexity, usage the call reported, did the task complete?
    ("extract_invoice", 3_200, "normal", {"input_tokens": 3_200, "output_tokens": 420}, True),
    ("extract_invoice", 2_900, "normal", {"input_tokens": 2_900, "output_tokens": 2_048}, False),  # hit max_tokens
    ("extract_invoice", 2_900, "high", {"input_tokens": 1_100, "output_tokens": 380,
                                        "cache_read_input_tokens": 1_800}, True),
    ("draft_reply", 6_000, "normal", {"input_tokens": 2_000, "output_tokens": 900,
                                      "cache_creation_input_tokens": 4_000}, True),
    ("audit_anomaly", 40_000, "high", {"input_tokens": 40_000, "output_tokens": 6_500}, True),
    ("draft_reply", 60_000, "high", {"input_tokens": 60_000, "output_tokens": 1_200}, True),
]
for task, tokens, complexity, usage, completed in traffic:
    try:
        r = guard.admit(task, tokens, day, complexity)
    except BudgetExceeded as exc:
        print("REJECTED", exc)
        continue
    if r is None:
        continue
    cost = guard.record(day, task, r["model"], usage, completed)
    print(f"{task:16} -> {r['model']:18} effort={r['effort']:6} degraded={r['degraded']}  ${cost}")
print(guard.report(day))
