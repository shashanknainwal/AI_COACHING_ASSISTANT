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
        self.tokens = float(capacity)
        self.updated = now

    def _refill(self, now):
        elapsed = max(0.0, now - self.updated)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
        self.updated = max(self.updated, now)

    def available(self, now):
        self._refill(now)
        return self.tokens

    def try_take(self, amount, now):
        self._refill(now)
        if amount <= self.tokens:
            self.tokens -= amount
            return True
        return False

    def adjust(self, delta, now):
        """Give back (delta > 0) or charge extra (delta < 0). May go negative, never above capacity."""
        self._refill(now)
        self.tokens = min(self.capacity, self.tokens + delta)


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
        tenant, model = req.get("tenant"), req.get("model")
        if tenant not in self.tenant_tokens:
            raise ValueError(f"unknown tenant: {tenant}")
        if req.get("priority") not in PRIORITY:
            raise ValueError(f"unknown priority: {req.get('priority')}")
        if model not in self.pools or model not in self.prices:
            raise ValueError(f"unknown model: {model}")
        reserve = req["input_tokens"] + req["max_tokens"]
        if reserve > self.tenant_tokens[tenant].capacity or reserve > self.pools[model].capacity:
            raise ValueError(f"request {req['id']} can never fit: reserves {reserve} tokens")
        self._seq += 1
        self.queue.append({**req, "_seq": self._seq, "_arrived": now})

    def effective_priority(self, queued, now):
        waited = max(0.0, now - queued["_arrived"])
        return max(0, PRIORITY[queued["priority"]] - int(waited // AGING_SECONDS))

    def drain(self, now):
        """Admit every waiting request that fits, best priority first. Returns admitted ids in order."""
        order = sorted(self.queue, key=lambda q: (self.effective_priority(q, now), q["_seq"]))
        blocked_tenants, blocked_pools, admitted = set(), set(), []
        for q in order:
            tenant, model = q["tenant"], q["model"]
            if tenant in blocked_tenants or model in blocked_pools:
                continue
            reserve = q["input_tokens"] + q["max_tokens"]
            tok, reqs, pool = self.tenant_tokens[tenant], self.tenant_requests[tenant], self.pools[model]
            if tok.available(now) < reserve or reqs.available(now) < 1:
                blocked_tenants.add(tenant)   # keep this tenant's order: nothing of theirs jumps ahead
                continue
            if pool.available(now) < reserve:
                blocked_pools.add(model)      # nothing lower-priority jumps ahead on the shared pool
                continue
            tok.try_take(reserve, now)
            reqs.try_take(1, now)
            pool.try_take(reserve, now)
            self.in_flight[q["id"]] = (q, reserve)
            admitted.append(q["id"])
        self.queue = [q for q in self.queue if q["id"] not in self.in_flight]
        return admitted

    def complete(self, req_id, usage, now):
        """Settle a finished request: refund unused tokens, attribute cost. Returns the cost."""
        if req_id not in self.in_flight:
            raise ValueError(f"unknown request: {req_id}")
        q, reserved = self.in_flight.pop(req_id)
        # Cache reads don't count toward the limit (as upstream on most models); cache writes do.
        used = (usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
                + usage.get("output_tokens", 0))
        self.tenant_tokens[q["tenant"]].adjust(reserved - used, now)
        self.pools[q["model"]].adjust(reserved - used, now)
        p = self.prices[q["model"]]
        cost = (usage.get("input_tokens", 0) * p["input"]
                + usage.get("output_tokens", 0) * p["output"]
                + usage.get("cache_creation_input_tokens", 0) * p["cache_write_5m"]
                + usage.get("cache_read_input_tokens", 0) * p["cache_read"]) / 1_000_000
        cost = round(cost, 6)
        self.spend[q["tenant"]] += cost
        return cost

    def costs(self):
        return {t: round(v, 6) for t, v in self.spend.items()}


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
