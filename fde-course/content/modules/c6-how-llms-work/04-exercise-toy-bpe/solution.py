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


def _merge(ids, pair, new_id):
    """Replace every non-overlapping occurrence of pair, scanning left to right."""
    out, i = [], 0
    while i < len(ids):
        if i + 1 < len(ids) and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def learn_merges(text, num_merges):
    """Learn up to num_merges BPE merges over the UTF-8 bytes of text.

    Returns a list of ((a, b), new_id) in the order learned. new_id starts at 256.
    """
    ids = list(text.encode("utf-8"))
    merges = []
    for i in range(num_merges):
        counts = {}
        for pair in zip(ids, ids[1:]):
            counts[pair] = counts.get(pair, 0) + 1   # dicts keep first-seen order
        if not counts:
            break
        best = max(counts, key=counts.get)          # ties: the pair seen first
        if counts[best] < 2:
            break
        new_id = 256 + i
        ids = _merge(ids, best, new_id)
        merges.append((best, new_id))
    return merges


def encode(text, merges):
    """Return the list of token ids for text, replaying merges in order."""
    ids = list(text.encode("utf-8"))
    for pair, new_id in merges:
        ids = _merge(ids, pair, new_id)
    return ids


def decode(ids, merges):
    """Turn token ids back into a string."""
    vocab = {i: bytes([i]) for i in range(256)}
    for (a, b), new_id in merges:
        vocab[new_id] = vocab[a] + vocab[b]
    return b"".join(vocab[i] for i in ids).decode("utf-8", errors="replace")


def compare(samples, merges):
    """Return {name: {"chars", "tokens", "tokens_per_char"}} for each sample."""
    out = {}
    for name, text in samples.items():
        tokens = len(encode(text, merges))
        out[name] = {"chars": len(text), "tokens": tokens, "tokens_per_char": round(tokens / len(text), 2)}
    return out


# --- Try it out (not graded) ---
print("toy merges:", learn_merges("aaabdaaabac", 10))
merges = learn_merges(TRAINING_TEXT, 150)
report = compare(SAMPLES, merges)
if report:
    for name, row in report.items():
        print(f"{name:8} {row['chars']:3} chars -> {row['tokens']:3} tokens ({row['tokens_per_char']} per char)")
