class Gateway:
    """An LLM gateway that tracks API keys, token quotas and rate limits.
    Timestamps only ever increase between calls.

    Read Level 1 on the left, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self):
        pass

    def create_key(self, timestamp, key_id, owner, quota):
        pass

    def record_usage(self, timestamp, key_id, tokens):
        pass

    def get_remaining(self, timestamp, key_id):
        pass


# --- Try it out (not graded) ---
g = Gateway()
print(g.create_key(1, "k1", "acme", 1000))
print(g.record_usage(2, "k1", 300))
print(g.get_remaining(3, "k1"))
