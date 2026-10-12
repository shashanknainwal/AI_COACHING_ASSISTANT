"""Turn `response.usage` into dollars, and stop a run before it overspends.

Pure functions only: no SDK import, so the unit tests run without a key.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app import config


def usage_to_dict(usage) -> dict:
    """Normalise an SDK `Usage` object (or a dict) into plain ints.

    `output_tokens` already includes thinking tokens. Where the response
    reports them separately, `thinking_tokens` holds that part.
    """
    if usage is None:
        return {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0, "thinking_tokens": 0}

    def get(obj, name):
        if isinstance(obj, dict):
            return obj.get(name)
        return getattr(obj, name, None)

    details = get(usage, "output_tokens_details")
    thinking = get(details, "thinking_tokens") if details is not None else None
    return {
        "input_tokens": int(get(usage, "input_tokens") or 0),
        "output_tokens": int(get(usage, "output_tokens") or 0),
        "cache_creation_input_tokens": int(get(usage, "cache_creation_input_tokens") or 0),
        "cache_read_input_tokens": int(get(usage, "cache_read_input_tokens") or 0),
        "thinking_tokens": int(thinking or 0),
    }


def prompt_tokens(u: dict) -> int:
    """All input-side tokens of one request: uncached + cache writes + cache reads."""
    return u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]


def cost_usd(model: str, usage) -> float:
    """Dollar cost of one request from its usage block.

    Raises KeyError for a model missing from config.PRICES, on purpose: a
    silent zero would make a cost table look better than it is.
    """
    u = usage if isinstance(usage, dict) and "thinking_tokens" in usage else usage_to_dict(usage)
    prices = config.PRICES[model]
    if model == config.HAIKU and prompt_tokens(u) > config.HAIKU_LONG_PROMPT_THRESHOLD:
        prices = config.HAIKU_LONG_PROMPT_PRICES
    per = 1_000_000
    return (
        u["input_tokens"] * prices["input"] / per
        + u["cache_creation_input_tokens"] * prices["cache_write"] / per
        + u["cache_read_input_tokens"] * prices["cache_read"] / per
        + u["output_tokens"] * prices["output"] / per
    )


class BudgetExceeded(RuntimeError):
    """Raised when a run has spent more than its budget."""


@dataclass
class CostMeter:
    """Accumulates usage across calls and enforces a budget.

    Create one per script run. Call `add()` after every response. It raises
    BudgetExceeded once the total passes the budget, so a bug in a loop costs
    you at most the budget plus one call.
    """

    budget_usd: float = config.BUDGET_USD
    calls: int = 0
    total_usd: float = 0.0
    totals: dict = field(default_factory=lambda: {
        "input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0, "thinking_tokens": 0})

    def add(self, model: str, usage) -> float:
        u = usage_to_dict(usage) if not (isinstance(usage, dict) and "thinking_tokens" in usage) else usage
        c = cost_usd(model, u)
        self.calls += 1
        self.total_usd += c
        for k in self.totals:
            self.totals[k] += u.get(k, 0)
        if self.total_usd > self.budget_usd:
            raise BudgetExceeded(
                f"spent ${self.total_usd:.4f}, over the ${self.budget_usd:.2f} budget "
                f"(set CAPSTONE_BUDGET_USD to raise it on purpose)")
        return c

    def summary(self) -> dict:
        return {"calls": self.calls, "total_usd": round(self.total_usd, 6), **self.totals}
