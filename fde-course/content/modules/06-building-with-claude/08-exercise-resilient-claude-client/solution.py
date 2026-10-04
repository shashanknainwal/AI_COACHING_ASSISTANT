import anthropic

MODEL = "claude-opus-5-5"

# Dollars per million tokens. Keep prices in one place: they change over time.
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "cache_write": 5.00, "cache_read": 0.20, "output": 20.00},
    "claude-sonnet-5-5": {"input": 2.00, "cache_write": 2.50, "cache_read": 0.20, "output": 10.00},
}

POLICY_MANUAL = "Harbor Bank support policy. " + " ".join(
    f"Section {i}: procedures for wires, disputes, fees, holds and account access, with escalation rules." for i in range(1, 400)
)


def make_client():
    return anthropic.Anthropic(max_retries=3, timeout=60.0)


def cached_system(text):
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def _error(status, e):
    return {"status": status, "text": None, "request_id": getattr(e, "request_id", None), "usage": None}


def call_claude(client, system, user_text, model=MODEL, max_tokens=4096):
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=cached_system(system),
            messages=[{"role": "user", "content": user_text}],
        )
    except anthropic.RateLimitError as e:
        return _error("rate_limited", e)
    except anthropic.BadRequestError as e:
        return _error("bad_request", e)
    except anthropic.AuthenticationError as e:
        return _error("auth_error", e)
    except anthropic.APIStatusError as e:
        return _error("server_error" if e.status_code >= 500 else "api_error", e)
    except anthropic.APIConnectionError as e:
        return _error("connection_error", e)

    text = "".join(b.text for b in response.content if b.type == "text")
    if response.stop_reason == "refusal":
        status, text = "refused", None
    elif response.stop_reason == "max_tokens":
        status = "truncated"
    else:
        status = "ok"
    return {"status": status, "text": text, "request_id": response._request_id, "usage": response.usage}


def cost(usage, model=MODEL):
    p = PRICES[model]
    total = (
        usage.input_tokens * p["input"]
        + usage.cache_creation_input_tokens * p["cache_write"]
        + usage.cache_read_input_tokens * p["cache_read"]
        + usage.output_tokens * p["output"]
    )
    return round(total / 1_000_000, 6)


# --- Try it out (not graded) ---
client = make_client()
if client:
    for question in ["What's the wire cutoff time?", "Is the cutoff different on Fridays?"]:
        result = call_claude(client, POLICY_MANUAL, question)
        if result and result["usage"]:
            u = result["usage"]
            print(f"{result['status']:<4} {question}")
            print(f"     input={u.input_tokens} cache_write={u.cache_creation_input_tokens} "
                  f"cache_read={u.cache_read_input_tokens} output={u.output_tokens}  cost=${cost(u)}")
