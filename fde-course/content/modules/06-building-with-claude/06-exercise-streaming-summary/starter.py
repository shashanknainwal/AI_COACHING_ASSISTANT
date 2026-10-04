import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
SYSTEM_PROMPT = """You summarize Harbor Bank operations stand-ups for team leads.
Cover: progress, risks, decisions, and action items with owners. Plain language, under 150 words."""

TRANSCRIPT = """Maya: Dispute backlog is down to 290 from 410 since the classifier went live.
Leo: Lakeview branch had two ATM outages; vendor is coming Thursday.
Maya: Overdraft fee complaints are up 12% week over week. I'll pull examples for compliance.
Priya: We agreed to expand the pilot to the mortgage team on Monday. I'll write the onboarding plan."""


def make_collector():
    """Return (on_text, chunks): a callback and the list it appends to."""
    # TODO
    pass


def stream_summary(client, transcript, on_text):
    """Stream a summary, calling on_text for each piece. Return the result dict."""
    # TODO
    pass


# --- Try it out (not graded) ---
def show(piece):
    print(piece, end="|")          # "|" marks each streamed piece

result = stream_summary(client, TRANSCRIPT, show)
print("\n")
if result:
    print("stop_reason:", result["stop_reason"], "| output tokens:", result["output_tokens"], "| truncated:", result["truncated"])
