import math
import random


def softmax_with_temperature(logits, temperature):
    """Probabilities from logits / temperature. temperature <= 0 means greedy (one-hot on the first max)."""
    if temperature <= 0:
        best = logits.index(max(logits))
        return [1.0 if i == best else 0.0 for i in range(len(logits))]
    scaled = [z / temperature for z in logits]
    m = max(scaled)
    exps = [math.exp(z - m) for z in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def _ranked(probs):
    """Indices from most to least likely; ties keep the lower index first."""
    return sorted(range(len(probs)), key=lambda i: (-probs[i], i))


def _keep(probs, kept):
    total = sum(probs[i] for i in kept)
    return [probs[i] / total if i in kept else 0.0 for i in range(len(probs))]


def top_k_filter(probs, k):
    """Keep the k most likely tokens (ties: lower index first), zero the rest, renormalize."""
    return _keep(probs, set(_ranked(probs)[:k]))


def top_p_filter(probs, p):
    """Keep the smallest set of most likely tokens whose total is at least p, zero the rest, renormalize."""
    kept, cumulative = set(), 0.0
    for i in _ranked(probs):
        kept.add(i)
        cumulative += probs[i]
        if cumulative >= p - 1e-12:
            break
    return _keep(probs, kept)


def sample(logits, temperature=1.0, top_k=None, top_p=None, rng=None):
    """Return the index of one sampled token. Draw exactly one rng.random() per call."""
    rng = rng or random.Random()
    probs = softmax_with_temperature(logits, temperature)
    if top_k is not None:
        probs = top_k_filter(probs, top_k)
    if top_p is not None:
        probs = top_p_filter(probs, top_p)
    r = rng.random()
    cumulative = 0.0
    last = 0
    for i, pr in enumerate(probs):
        if pr == 0.0:
            continue
        last = i
        cumulative += pr
        if r < cumulative:
            return i
    return last


def log_probs(logits):
    """Natural-log probabilities at temperature 1, computed stably."""
    m = max(logits)
    log_total = m + math.log(sum(math.exp(z - m) for z in logits))
    return [z - log_total for z in logits]


# --- Try it out (not graded) ---
LOGITS = [2.0, 1.0, 0.1, -1.0]
for t in (0.5, 1.0, 2.0):
    print(f"T={t}:", softmax_with_temperature(LOGITS, t))
print("top-p 0.9:", top_p_filter(softmax_with_temperature(LOGITS, 1.0) or [0.25] * 4, 0.9))
rng = random.Random(42)
draws = [sample(LOGITS, temperature=1.0, top_p=0.9, rng=rng) for _ in range(20)]
print("20 draws with seed 42:", draws)
print("logprobs:", log_probs(LOGITS))
