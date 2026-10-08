OPUS, SONNET, HAIKU = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"

# US dollars per million tokens. Haiku's cache rates are left out on purpose:
# add them from the pricing page before Ledgerline caches anything on Haiku.
PRICES = {
    OPUS: {"input": 4.00, "output": 20.00, "cache_write_5m": 5.00, "cache_write_1h": 8.00, "cache_read": 0.20},
    SONNET: {"input": 2.00, "output": 10.00, "cache_write_5m": 2.50, "cache_write_1h": 4.00, "cache_read": 0.10},
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
    if task not in ROUTES:
        raise ValueError(f"unknown task: {task}")
    r = dict(ROUTES[task])
    if complexity == "high":
        if r["model"] == OPUS:
            r["effort"] = "high"
        else:
            r["model"] = LADDER[LADDER.index(r["model"]) + 1]
    if r["model"] == HAIKU and input_tokens > HAIKU_MAX_INPUT:
        r["model"] = SONNET
    return r


_RATE_KEYS = [
    ("input_tokens", "input"),
    ("output_tokens", "output"),
    ("cache_read_input_tokens", "cache_read"),
]


def call_cost(model, usage, prices=PRICES, batch=False):
    """Dollar cost of one call from its usage dict, rounded to 6 decimals."""
    if model not in prices:
        raise ValueError(f"no prices for {model}")
    rates = prices[model]
    counts = [(usage.get(field, 0), key) for field, key in _RATE_KEYS]
    breakdown = usage.get("cache_creation")
    if breakdown:
        counts.append((breakdown.get("ephemeral_5m_input_tokens", 0), "cache_write_5m"))
        counts.append((breakdown.get("ephemeral_1h_input_tokens", 0), "cache_write_1h"))
    else:
        counts.append((usage.get("cache_creation_input_tokens", 0), "cache_write_5m"))
    total = 0.0
    for tokens, key in counts:
        if not tokens:
            continue
        if key not in rates:
            raise ValueError(f"no {key} price for {model}")
        total += tokens * rates[key]
    total /= 1_000_000
    if batch:
        total *= BATCH_DISCOUNT
    return round(total, 6)


def worst_case_cost(r, input_tokens, prices=PRICES):
    """Upper bound before the call: every input token uncached, output runs to max_tokens."""
    rates = prices[r["model"]]
    return round((input_tokens * rates["input"] + r["max_tokens"] * rates["output"]) / 1_000_000, 6)


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
        r = route(task, input_tokens, complexity)
        left = self.daily_budget_usd - self._day(day)["spent"]
        if worst_case_cost(r, input_tokens, self.prices) <= left:
            return dict(r, degraded=False)
        if task in DEGRADABLE:
            for model in reversed(LADDER[:LADDER.index(r["model"])]):
                if model == HAIKU and input_tokens > HAIKU_MAX_INPUT:
                    continue
                cheaper = dict(r, model=model)
                if worst_case_cost(cheaper, input_tokens, self.prices) <= left:
                    return dict(cheaper, degraded=True)
        raise BudgetExceeded(f"{task}: not enough budget left on {day}")

    def record(self, day, task, model, usage, completed, batch=False):
        """Add one call's actual cost to the day. Returns that cost."""
        cost = call_cost(model, usage, self.prices, batch)
        d = self._day(day)
        d["spent"] += cost
        d["by_model"][model] = d["by_model"].get(model, 0.0) + cost
        t = d["tasks"].setdefault(task, {"cost": 0.0, "completed": 0})
        t["cost"] += cost
        if completed:
            t["completed"] += 1
        return cost

    def report(self, day):
        """{"spent", "remaining", "by_model", "cost_per_completed"} for one day."""
        d = self._day(day)
        return {
            "spent": round(d["spent"], 6),
            "remaining": round(self.daily_budget_usd - d["spent"], 6),
            "by_model": {m: round(c, 6) for m, c in d["by_model"].items()},
            "cost_per_completed": {
                task: (round(t["cost"] / t["completed"], 6) if t["completed"] else None)
                for task, t in d["tasks"].items()
            },
        }


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
