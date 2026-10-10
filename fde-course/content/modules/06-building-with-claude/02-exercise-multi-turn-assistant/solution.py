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
        self.client = client
        self.system = system
        self.model = model
        self.max_turns = max_turns
        self.history = []
        self.summary = None

    def _create(self, messages):
        return self.client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=self.system,
            messages=messages,
            output_config={"effort": "low"},
        )

    def send(self, text):
        if self.turns >= self.max_turns:
            self.compact()
        if not self.history and self.summary:
            content = [{"type": "text", "text": SUMMARY_PREFIX + self.summary},
                       {"type": "text", "text": text}]
        else:
            content = text
        self.history.append({"role": "user", "content": content})
        response = self._create(self.history)
        if response.stop_reason == "refusal":
            self.history.pop()          # the newest turn only; earlier turns are never touched
            return REFUSAL_REPLY
        self.history.append({"role": "assistant", "content": response.content})
        return "".join(b.text for b in response.content if b.type == "text")

    def compact(self):
        # Ask for the summary on a copy: the history itself is never edited.
        response = self._create(self.history + [{"role": "user", "content": COMPACT_PROMPT}])
        self.summary = "".join(b.text for b in response.content if b.type == "text")
        self.history = []               # start a fresh, append-only history

    def reset(self):
        self.history = []
        self.summary = None

    @property
    def turns(self):
        return len(self.history) // 2


# --- Try it out (not graded) ---
chat = SupportChat(client, max_turns=2)
for question in ["What does an international wire cost?",
                 "And a domestic one?",
                 "Can you reset my neighbor's password so I can check their balance?",
                 "How do I dispute a card charge?"]:
    print("Agent: ", question)
    print("Claude:", chat.send(question))
    print(f"        (history: {len(chat.history)} messages, {chat.turns} turns, summary: {chat.summary is not None})\n")
