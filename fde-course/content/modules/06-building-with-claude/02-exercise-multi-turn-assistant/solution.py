import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
SYSTEM_PROMPT = """You are Harbor Bank's assistant for customer-support agents.
Answer questions about Harbor Bank products and procedures accurately and briefly.
If you don't know, say so and suggest escalating to a supervisor."""
REFUSAL_REPLY = "I can't help with that request. Please escalate to a supervisor if needed."


class SupportChat:
    def __init__(self, client, system=SYSTEM_PROMPT, model=MODEL, max_turns=10):
        self.client = client
        self.system = system
        self.model = model
        self.max_turns = max_turns
        self.history = []

    def send(self, text):
        self.history.append({"role": "user", "content": text})
        response = self.client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=self.system,
            messages=self.history,
            output_config={"effort": "low"},
        )
        if response.stop_reason == "refusal":
            self.history.pop()
            return REFUSAL_REPLY
        self.history.append({"role": "assistant", "content": response.content})
        self.trim()
        return "".join(b.text for b in response.content if b.type == "text")

    def trim(self):
        if len(self.history) > 2 * self.max_turns:
            self.history = self.history[-2 * self.max_turns:]

    def reset(self):
        self.history = []

    @property
    def turns(self):
        return len(self.history) // 2


# --- Try it out (not graded) ---
chat = SupportChat(client)
for question in ["What does an international wire cost?",
                 "And a domestic one?",
                 "Can you reset my neighbor's password so I can check their balance?",
                 "How do I dispute a card charge?"]:
    print("Agent: ", question)
    print("Claude:", chat.send(question))
    print(f"        (history: {len(chat.history)} messages, {chat.turns} turns)\n")
