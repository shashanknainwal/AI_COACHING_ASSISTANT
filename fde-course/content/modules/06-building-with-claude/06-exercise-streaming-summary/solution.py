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
    chunks = []

    def on_text(piece):
        chunks.append(piece)

    return on_text, chunks


def stream_summary(client, transcript, on_text):
    with client.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"<transcript>\n{transcript}\n</transcript>"}],
    ) as stream:
        for piece in stream.text_stream:
            on_text(piece)
        message = stream.get_final_message()
    return {
        "text": "".join(b.text for b in message.content if b.type == "text"),
        "stop_reason": message.stop_reason,
        "output_tokens": message.usage.output_tokens,
        "truncated": message.stop_reason == "max_tokens",
    }


# --- Try it out (not graded) ---
def show(piece):
    print(piece, end="|")          # "|" marks each streamed piece

result = stream_summary(client, TRANSCRIPT, show)
print("\n")
if result:
    print("stop_reason:", result["stop_reason"], "| output tokens:", result["output_tokens"], "| truncated:", result["truncated"])
