import json
import time
import anthropic

client = anthropic.Anthropic(max_retries=0, timeout=10)
MODEL = "claude-sonnet-5-5"
FEATURE_FLAGS = {"claude_triage": True}   # the kill switch: flip to False to stop calling Claude
TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {"category": {"type": "string"}, "urgency": {"type": "string", "enum": ["low", "normal", "high"]}},
    "required": ["category", "urgency"],
    "additionalProperties": False,
}


def rules_triage(text):
    """The pre-Claude keyword rules (given): worse, but always available."""
    low = text.lower()
    for category, words in [("damaged_item", ("broken", "damaged", "cracked")), ("returns", ("return", "send back")),
                            ("billing", ("charged", "refund", "fee")), ("order_status", ("where", "late", "tracking"))]:
        if any(w in low for w in words):
            return {"category": category, "urgency": "normal"}
    return {"category": "other", "urgency": "normal"}


def claude_triage(client, text):
    """One Claude triage call (given)."""
    response = client.messages.create(
        model=MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": f"<ticket>\n{text}\n</ticket>"}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": TRIAGE_SCHEMA}},
    )
    return json.loads(next(b.text for b in response.content if b.type == "text"))


class CircuitBreaker:
    def __init__(self, failure_threshold=3, cooldown_s=30.0, clock=time.monotonic):
        self.failure_threshold = failure_threshold
        self.cooldown_s = cooldown_s
        self.clock = clock
        self.state = "closed"
        self.failures = 0
        self.opened_at = None

    def allow(self):
        """May a request go to Claude now? Moves open -> half_open once the cooldown has passed."""
        # TODO
        pass

    def record_success(self):
        # TODO
        pass

    def record_failure(self):
        # TODO
        pass


def triage(client, breaker, text, flags=FEATURE_FLAGS):
    """Claude triage with a kill switch, a circuit breaker and a rules fallback. Adds a "source" key."""
    # TODO
    pass


# --- Try it out (not graded) ---
now = [0.0]                                    # a controllable clock for the demo
breaker = CircuitBreaker(failure_threshold=3, cooldown_s=30, clock=lambda: now[0])
# The first three tickets hit a (simulated) API outage.
for t, ticket in [(0, "Where is my order?"), (5, "My lamp arrived broken"), (10, "Where is B-1004?"),
                  (15, "I was charged twice"), (20, "Where is my rug?"), (45, "The mirror arrived broken"),
                  (50, "Where is my sofa?")]:
    now[0] = t
    result = triage(client, breaker, ticket)
    if result:
        print(f"t={t:>2}s  {result['source']:<12} {result['category']:<13} breaker={breaker.state}")
FEATURE_FLAGS["claude_triage"] = False
print("kill switch off ->", triage(client, breaker, "Where is my sofa?"))
FEATURE_FLAGS["claude_triage"] = True
