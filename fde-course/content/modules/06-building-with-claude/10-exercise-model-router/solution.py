import anthropic

client = anthropic.Anthropic()

ROUTES = {
    "classify": {"model": "claude-sonnet-5-5", "effort": "low", "max_tokens": 1024},
    "chat": {"model": "claude-opus-5-5", "effort": "low", "max_tokens": 16000},
    "extract": {"model": "claude-opus-5-5", "effort": "medium", "max_tokens": 16000},
}
FAST_MODEL = "claude-haiku-4-5"
CONTEXT_LIMITS = {"claude-opus-5-5": 1_000_000, "claude-sonnet-5-5": 1_000_000, "claude-haiku-4-5": 200_000}
FALLBACK = {"claude-opus-5-5": "claude-sonnet-5-5", "claude-sonnet-5-5": None, "claude-haiku-4-5": "claude-sonnet-5-5"}
PRICES = {  # dollars per million tokens
    "claude-opus-5-5": {"input": 4.00, "output": 20.00},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
}


def choose(task, input_tokens, latency_budget_ms=None):
    if task not in ROUTES:
        raise ValueError(f"unknown task: {task}")
    route = dict(ROUTES[task])
    if task == "classify" and latency_budget_ms is not None and latency_budget_ms < 1000:
        route = {"model": FAST_MODEL, "effort": None, "max_tokens": 1024}
    if input_tokens > CONTEXT_LIMITS[route["model"]] and route["model"] == FAST_MODEL:
        route = {"model": "claude-sonnet-5-5", "effort": "low", "max_tokens": route["max_tokens"]}
    if input_tokens > CONTEXT_LIMITS[route["model"]]:
        raise ValueError("input too large")
    return route


def build_params(route, system, user_text):
    params = {
        "model": route["model"],
        "max_tokens": route["max_tokens"],
        "system": system,
        "messages": [{"role": "user", "content": user_text}],
    }
    if route["effort"] is not None:
        params["output_config"] = {"effort": route["effort"]}
    return params


def estimate_cost(route, input_tokens, output_tokens):
    p = PRICES[route["model"]]
    return round((input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000, 6)


def _text(response):
    return "".join(b.text for b in response.content if b.type == "text")


def run(client, task, system, user_text, input_tokens, latency_budget_ms=None):
    route = choose(task, input_tokens, latency_budget_ms)
    try:
        response = client.messages.create(**build_params(route, system, user_text))
        return {"text": _text(response), "model": route["model"], "fallback_used": False}
    except (anthropic.OverloadedError, anthropic.InternalServerError):
        fallback = FALLBACK.get(route["model"])
        if fallback is None:
            raise
        backup = dict(route, model=fallback)
        response = client.messages.create(**build_params(backup, system, user_text))
        return {"text": _text(response), "model": fallback, "fallback_used": True}


# --- Try it out (not graded) ---
requests_today = [
    ("classify", "Card was charged twice", 300, 500),
    ("classify", "Card was charged twice", 300, None),
    ("chat", "What's the wire cutoff?", 2_000, None),
    ("extract", "<loan application text>", 250_000, None),
]
for task, text, tokens, budget in requests_today:
    route = choose(task, tokens, budget)
    if route:
        print(f"{task:<8} budget={str(budget):<5} -> {route['model']:<18} effort={str(route['effort']):<6} "
              f"est=${estimate_cost(route, tokens, 200)}")
        print("          ", run(client, task, "You help Harbor Bank staff.", text, tokens, budget))
