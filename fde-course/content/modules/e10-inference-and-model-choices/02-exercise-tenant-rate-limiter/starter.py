"""Admission control for Lumenfold's LLM gateway: token buckets, a priority queue, cost per tenant."""

# US dollars per million tokens. Cache reads are 0.05x input on Opus 5.5 and Sonnet 5.5, 0.1x on Haiku 5.5.
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_write_5m": 5.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_write_5m": 2.50, "cache_read": 0.10},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_write_5m": 0.125, "cache_read": 0.01},
}

PRIORITY = {"interactive": 0, "standard": 1, "batch": 2}
AGING_SECONDS = 30  # every 30 seconds of waiting promotes a request one priority level


class TokenBucket:
    """A bucket that holds up to `capacity` tokens and refills continuously."""

    def __init__(self, capacity, refill_per_sec, now=0.0):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.tokens = float(capacity)   # starts full
        self.updated = now

    def available(self, now):
        """Refill for the time since the last update (never above capacity), then return the tokens."""
        # TODO
        pass

    def try_take(self, amount, now):
        """Take `amount` if it's there and return True; otherwise take nothing and return False."""
        # TODO
        pass

    def adjust(self, delta, now):
        """Give back (delta > 0) or charge extra (delta < 0). May go negative, never above capacity."""
        # TODO
        pass


class Gateway:
    def __init__(self, tenants, pools, prices=PRICES, now=0.0):
        # tenants: {name: {"tokens_per_min": int, "requests_per_min": int}}
        # pools:   {model: tokens_per_min}  (the organisation's upstream limit, shared by every tenant)
        self.prices = prices
        self.tenant_tokens = {t: TokenBucket(c["tokens_per_min"], c["tokens_per_min"] / 60, now) for t, c in tenants.items()}
        self.tenant_requests = {t: TokenBucket(c["requests_per_min"], c["requests_per_min"] / 60, now) for t, c in tenants.items()}
        self.pools = {m: TokenBucket(tpm, tpm / 60, now) for m, tpm in pools.items()}
        self.queue = []          # waiting requests, each with "_seq" and "_arrived"
        self.in_flight = {}      # id -> (request, reserved tokens)
        self.spend = {t: 0.0 for t in tenants}
        self._seq = 0

    def submit(self, req, now):
        """Validate and enqueue one request. Admission happens in drain()."""
        # TODO
        pass

    def effective_priority(self, queued, now):
        """PRIORITY of the request, promoted one level per AGING_SECONDS waited, never below 0."""
        # TODO
        pass

    def drain(self, now):
        """Admit every waiting request that fits, best priority first. Returns admitted ids in order."""
        # TODO
        pass

    def complete(self, req_id, usage, now):
        """Settle a finished request: refund unused tokens, attribute cost. Returns the cost."""
        # TODO
        pass

    def costs(self):
        """{tenant: total cost rounded to 6 decimals}."""
        # TODO
        pass


# --- Try it out (not graded) ---
gw = Gateway(
    tenants={"northwind-news": {"tokens_per_min": 60_000, "requests_per_min": 60},
             "harbor-weekly": {"tokens_per_min": 30_000, "requests_per_min": 30}},
    pools={"claude-sonnet-5-5": 50_000, "claude-haiku-5-5": 200_000},
)
gw.submit({"id": "b1", "tenant": "northwind-news", "priority": "batch", "model": "claude-sonnet-5-5",
           "input_tokens": 20_000, "max_tokens": 8_000}, now=0)
gw.submit({"id": "i1", "tenant": "harbor-weekly", "priority": "interactive", "model": "claude-sonnet-5-5",
           "input_tokens": 6_000, "max_tokens": 2_000}, now=0)
gw.submit({"id": "b2", "tenant": "northwind-news", "priority": "batch", "model": "claude-sonnet-5-5",
           "input_tokens": 20_000, "max_tokens": 8_000}, now=0)
print("t=0 admitted:", gw.drain(now=0))
admitted_i1 = "i1" in gw.in_flight
if admitted_i1:
    cost = gw.complete("i1", {"input_tokens": 1_000, "cache_read_input_tokens": 5_000, "output_tokens": 400}, now=2)
    print("i1 cost:", cost)
print("t=2 admitted:", gw.drain(now=2))
print("t=40 admitted:", gw.drain(now=40))
print("costs:", gw.costs())
