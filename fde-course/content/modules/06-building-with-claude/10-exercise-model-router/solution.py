import anthropic

client = anthropic.Anthropic()

ROUTES = {
    "classify": {"model": "claude-sonnet-5-5", "effort": "low", "max_tokens": 1024},
    "chat": {"model": "claude-opus-5-5", "effort": "low", "max_tokens": 16000},
    "extract": {"model": "claude-opus-5-5", "effort": "medium", "max_tokens": 16000},
    "summarize": {"model": "claude-sonnet-5-5", "effort": None, "max_tokens": 16000},   # None: model default
}
FAST_MODEL = "claude-haiku-5-5"
CONTEXT_LIMITS = {"claude-opus-5-5": 1_000_000, "claude-sonnet-5-5": 1_000_000, "claude-haiku-5-5": 1_000_000}
FALLBACK = {"claude-opus-5-5": "claude-sonnet-5-5", "claude-sonnet-5-5": None, "claude-haiku-5-5": "claude-sonnet-5-5"}
PRICES = {  # dollars per million tokens
    "claude-opus-5-5": {"input": 4.00, "output": 20.00},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
    # Haiku 5.5 has two rate cards: a prompt over 100K tokens bills the whole request at the higher one.
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50,
                         "long_above": 100_000, "long_input": 0.50, "long_output": 2.50},
}



def choose(task, input_tokens, latency_budget_ms=None):
    if task not in ROUTES:
        raise ValueError(f"unknown task: {task}")
    route = dict(ROUTES[task])
    if task == "classify" and latency_budget_ms is not None and latency_budget_ms < 1000:
        route = {"model": FAST_MODEL, "effort": "low", "max_tokens": 2048}
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
    if "long_above" in p and input_tokens > p["long_above"]:
        in_price, out_price = p["long_input"], p["long_output"]
    else:
        in_price, out_price = p["input"], p["output"]
    return round((input_tokens * in_price + output_tokens * out_price) / 1_000_000, 6)


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
    ("classify", "<a 150K-token complaint thread>", 150_000, 500),
    ("chat", "What's the wire cutoff?", 2_000, None),
    ("extract", "<loan application text>", 250_000, None),
]
for task, text, tokens, budget in requests_today:
    route = choose(task, tokens, budget)
    if route:
        print(f"{task:<8} budget={str(budget):<5} -> {route['model']:<18} effort={str(route['effort']):<6} "
              f"est=${estimate_cost(route, tokens, 200)}")
        print("          ", run(client, task, "You help Harbor Bank staff.", text, tokens, budget))
