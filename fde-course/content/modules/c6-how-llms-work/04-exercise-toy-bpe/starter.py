TRAINING_TEXT = (
    "The support team answers customer questions about orders, refunds and delivery times. "
    "When a customer asks about a refund, the agent checks the order, confirms the payment "
    "and explains the refund policy. When a customer asks about a delivery, the agent checks "
    "the tracking number and gives the expected delivery date. The team wants answers that "
    "are short, clear and correct. The model reads the question, reads the order history and "
    "writes a reply. The reply should mention the order number, the next step and the date. "
    "If the question is about something the team does not handle, the reply should say so and "
    "point the customer to the right place. The team measures every reply for accuracy and tone. "
    "Most questions are about the status of an order, the cost of shipping, or how to return an "
    "item that does not fit. The best replies answer the question in the first sentence and then "
    "explain the reason. The worst replies repeat the question back to the customer and add nothing new."
)

SAMPLES = {
    "english": "The customer wants a refund for the order that arrived late.",
    "code": "def refund(order_id):\n    if order.status == \"late\":\n        return issue_refund(order_id)\n",
    "hindi": "ग्राहक देर से पहुँचे ऑर्डर के लिए रिफंड चाहता है।",
}


def learn_merges(text, num_merges):
    """Learn up to num_merges BPE merges over the UTF-8 bytes of text.

    Returns a list of ((a, b), new_id) in the order learned. new_id starts at 256.
    """
    # TODO
    pass


def encode(text, merges):
    """Return the list of token ids for text, replaying merges in order."""
    # TODO
    pass


def decode(ids, merges):
    """Turn token ids back into a string."""
    # TODO
    pass


def compare(samples, merges):
    """Return {name: {"chars", "tokens", "tokens_per_char"}} for each sample."""
    # TODO
    pass


# --- Try it out (not graded) ---
print("toy merges:", learn_merges("aaabdaaabac", 10))
merges = learn_merges(TRAINING_TEXT, 150)
report = compare(SAMPLES, merges)
if report:
    for name, row in report.items():
        print(f"{name:8} {row['chars']:3} chars -> {row['tokens']:3} tokens ({row['tokens_per_char']} per char)")
