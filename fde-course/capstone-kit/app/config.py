"""Model ids, effort defaults and prices in one place.

Change models here, not in the code that calls them. Every cost figure in this
kit is computed from `PRICES` and the `usage` block of each real response.

Prices are USD per million tokens, checked against the Anthropic pricing page
on 2026-10-10. Prices change: check https://platform.claude.com/docs/en/about-claude/pricing
before you quote a number in your README, and write the date you checked.
"""

from __future__ import annotations

import os

HAIKU = "claude-haiku-5-5"
SONNET = "claude-sonnet-5-5"
OPUS = "claude-opus-5-5"

# The cheap tier is the default so a mistake costs cents, not dollars.
DEFAULT_MODEL = os.environ.get("CAPSTONE_MODEL", HAIKU)
JUDGE_MODEL = os.environ.get("CAPSTONE_JUDGE_MODEL", SONNET)

# Always send effort explicitly. Defaults differ by model (Haiku 5.5 and
# Opus 5.5 default to "medium", Sonnet 5.5 to "high"), and all three think by
# default. Thinking tokens are billed as output and count against max_tokens.
DEFAULT_EFFORT = os.environ.get("CAPSTONE_EFFORT", "low")
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")

# A hard stop for one process. LLM code in a loop can spend money fast.
BUDGET_USD = float(os.environ.get("CAPSTONE_BUDGET_USD", "1.00"))

# USD per million tokens. cache_write is the default 5-minute TTL.
PRICES: dict[str, dict[str, float]] = {
    HAIKU: {
        "input": 0.10,
        "output": 0.50,
        "cache_write": 0.125,
        "cache_read": 0.01,
    },
    SONNET: {
        "input": 2.00,
        "output": 10.00,
        "cache_write": 2.50,
        "cache_read": 0.10,
    },
    OPUS: {
        "input": 4.00,
        "output": 20.00,
        "cache_write": 5.00,
        "cache_read": 0.20,
    },
}

# Haiku 5.5 charges more when a prompt is over 100K tokens ($0.50 input,
# $2.50 output, $0.05 cache reads). The cache-write figure below is derived
# from the 1.25x rule, not read from the pricing page: check it if you go there.
HAIKU_LONG_PROMPT_THRESHOLD = 100_000
HAIKU_LONG_PROMPT_PRICES = {
    "input": 0.50,
    "output": 2.50,
    "cache_write": 0.625,
    "cache_read": 0.05,
}

# Minimum cacheable prefix on the current models above. Shorter prefixes are
# processed normally and never show up in cache_read_input_tokens.
MIN_CACHEABLE_TOKENS = 512
