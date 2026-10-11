# EXAMPLE_LIMITS holds MADE-UP placeholder numbers for practice. They are not
# Anthropic's, AWS's, Google's or Microsoft's published limits. Real numbers
# come from the customer's own console or quota page on the day you plan, and
# they change. Your functions must work for ANY table in this shape.
#
# One entry per platform/region/model combination you might deploy on.
# "cache_reads_count": True means cache reads count toward the input limit
# (the Claude API docs say they don't on most models; check per platform).
EXAMPLE_LIMITS = {
    "claude_api_global_sonnet": {"rpm": 4000, "itpm": 4_000_000, "otpm": 1_200_000},
    "bedrock_eu_sonnet": {"rpm": 2000, "itpm": 6_000_000, "otpm": 800_000, "cache_reads_count": False},
    "vertex_eu_sonnet": {"rpm": 1500, "itpm": 20_000_000, "otpm": 1_500_000, "cache_reads_count": True},
}

# Priority Tier burn-down rates, as documented on Anthropic's service tiers page
# (checked October 2026). Priority Tier is no longer sold to new customers;
# these rates apply to existing commitments, and they're passed in as a
# parameter so you can model any commitment measured this way.
PRIORITY_RATES = {
    "cache_read": 0.1,
    "cache_write_5m": 1.25,
    "cache_write_1h": 2.0,
    "us_only": 1.1,
}

# Brackenridge Bank's (fictional) customer-service assistant, per model call.
# input_tokens is the TOTAL input per call: cache reads + cache writes + uncached.
# output_tokens includes thinking at the effort level measured in the pilot.
BRACKENRIDGE_WORKLOAD = {
    "calls_per_minute": 400,
    "input_tokens": 14_000,
    "cache_read_tokens": 10_000,
    "cache_write_tokens": 500,
    "output_tokens": 700,
    "cache_ttl": "5m",
    "inference_geo": "global",
}
