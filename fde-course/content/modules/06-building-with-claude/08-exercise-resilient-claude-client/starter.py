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
    """Client with 3 retries and a 60 second timeout."""
    # TODO
    pass


def cached_system(text):
    """System prompt as one text block marked for caching."""
    # TODO
    pass


def call_claude(client, system, user_text, model=MODEL, max_tokens=4096):
    """Never raises. Returns {"status", "text", "request_id", "usage"}."""
    # TODO
    pass


def cost(usage, model=MODEL):
    """Dollar cost of a call, using all four token types, rounded to 6 decimals."""
    # TODO
    pass


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
