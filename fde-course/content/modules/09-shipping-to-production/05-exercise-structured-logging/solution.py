import json
import re
import time
import anthropic

client = anthropic.Anthropic(max_retries=0)
PRICES = {  # dollars per million tokens (given)
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_write": 5.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.20},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00, "cache_write": 1.25, "cache_read": 0.10},
}


def call_cost(model, usage):
    """Dollar cost of one response (given, from Module 8)."""
    p = PRICES[model]
    return round((usage.input_tokens * p["input"] + usage.cache_creation_input_tokens * p["cache_write"]
                  + usage.cache_read_input_tokens * p["cache_read"] + usage.output_tokens * p["output"]) / 1e6, 6)


# Patterns from Brightway's security team (given).
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
CARD = re.compile(r"\b(?:\d[ -]?){12,15}\d\b")
PHONE = re.compile(r"(?:\(\d{3}\)\s?|\b\d{3}[-. ])\d{3}[-. ]\d{4}\b")


def redact(text):
    text = EMAIL.sub("[email]", text)
    text = CARD.sub("[card]", text)
    return PHONE.sub("[phone]", text)


class JsonLogger:
    def __init__(self, service, clock=time.time):
        self.service = service
        self.clock = clock
        self.lines = []

    def log(self, level, event, **fields):
        record = {"ts": round(self.clock(), 3), "level": level, "service": self.service, "event": event}
        for key, value in fields.items():
            record[key] = redact(value) if isinstance(value, str) else value
        line = json.dumps(record, sort_keys=True)
        self.lines.append(line)
        return line


def logged_create(client, logger, request_id, clock=time.monotonic, **params):
    start = clock()
    try:
        response = client.messages.create(**params)
    except anthropic.APIError as e:
        logger.log("error", "llm_error", request_id=request_id, model=params.get("model"),
                   error_type=type(e).__name__, latency_ms=round((clock() - start) * 1000))
        raise
    latency_ms = round((clock() - start) * 1000)
    usage = response.usage
    level = "warning" if response.stop_reason in ("max_tokens", "refusal") else "info"
    logger.log(level, "llm_call", request_id=request_id, model=response.model, stop_reason=response.stop_reason,
               input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
               cache_read_tokens=usage.cache_read_input_tokens, cache_write_tokens=usage.cache_creation_input_tokens,
               latency_ms=latency_ms, cost_usd=call_cost(response.model, usage))
    return response


# --- Try it out (not graded) ---
logger = JsonLogger("brightway-triage")
logger.log("info", "ticket_received", request_id="req-7f3a", channel="email",
           customer_note="Reach me at maya@example.com or (415) 555-0134. Card 4111 1111 1111 1111 was charged twice.")
ticket = "I'm maya@example.com and my order B-1001 is late."
response = logged_create(client, logger, "req-7f3a", model="claude-sonnet-5-5", max_tokens=1024,
                         messages=[{"role": "user", "content": f"<ticket>\n{ticket}\n</ticket>"}])
for line in logger.lines:
    print(line)
