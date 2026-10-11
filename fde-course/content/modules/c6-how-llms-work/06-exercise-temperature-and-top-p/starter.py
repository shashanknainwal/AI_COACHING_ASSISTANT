import math
import random


def softmax_with_temperature(logits, temperature):
    """Probabilities from logits / temperature. temperature <= 0 means greedy (one-hot on the first max)."""
    # TODO
    pass


def top_k_filter(probs, k):
    """Keep the k most likely tokens (ties: lower index first), zero the rest, renormalize."""
    # TODO
    pass


def top_p_filter(probs, p):
    """Keep the smallest set of most likely tokens whose total is at least p, zero the rest, renormalize."""
    # TODO
    pass


def sample(logits, temperature=1.0, top_k=None, top_p=None, rng=None):
    """Return the index of one sampled token. Draw exactly one rng.random() per call."""
    # TODO
    pass


def log_probs(logits):
    """Natural-log probabilities at temperature 1, computed stably."""
    # TODO
    pass


# --- Try it out (not graded) ---
LOGITS = [2.0, 1.0, 0.1, -1.0]
for t in (0.5, 1.0, 2.0):
    print(f"T={t}:", softmax_with_temperature(LOGITS, t))
print("top-p 0.9:", top_p_filter(softmax_with_temperature(LOGITS, 1.0) or [0.25] * 4, 0.9))
rng = random.Random(42)
draws = [sample(LOGITS, temperature=1.0, top_p=0.9, rng=rng) for _ in range(20)]
print("20 draws with seed 42:", draws)
print("logprobs:", log_probs(LOGITS))
