import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
SYSTEM_PROMPT = """You are Harbor Bank's assistant for customer-support agents.
Answer questions about Harbor Bank products and procedures accurately and briefly.
If you don't know, say so and suggest escalating to a supervisor."""
REFUSAL_REPLY = "I can't help with that request. Please escalate to a supervisor if needed."
COMPACT_PROMPT = ("Summarize this conversation for your own future reference: the customer's issue, "
                  "facts and amounts already given, and anything still open. Plain text, under 150 words.")
SUMMARY_PREFIX = "Summary of the earlier conversation:\n"


class SupportChat:
    def __init__(self, client, system=SYSTEM_PROMPT, model=MODEL, max_turns=10):
        # TODO
        self.history = []
        self.summary = None

    def send(self, text):
        """Send one user message, keep history append-only, return the reply text."""
        # TODO
        pass

    def compact(self):
        """Replace the whole history with a summary. Never edit earlier turns."""
        # TODO
        pass

    def reset(self):
        # TODO
        pass

    @property
    def turns(self):
        # TODO
        return 0


# --- Try it out (not graded) ---
chat = SupportChat(client, max_turns=2)
for question in ["What does an international wire cost?",
                 "And a domestic one?",
                 "Can you reset my neighbor's password so I can check their balance?",
                 "How do I dispute a card charge?"]:
    print("Agent: ", question)
    print("Claude:", chat.send(question))
    print(f"        (history: {len(chat.history)} messages, {chat.turns} turns, summary: {chat.summary is not None})\n")
