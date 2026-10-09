import anthropic
from anthropic import _sim

# Month-end at Ledgerline: the API is busy. The demo run sees an overload,
# then a rate limit with a retry-after header, then an answer.
_sim.queue(
    anthropic.OverloadedError("Error code: 529 - overloaded_error", request_id="req_demo_0001"),
    anthropic.RateLimitError("Error code: 429 - rate_limit_error", headers={"retry-after": "3"}, request_id="req_demo_0002"),
    '{"vendor": "Brightfield Paper Co.", "total": "1,284.50", "currency": "USD"}',
)
