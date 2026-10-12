import math
import random


def _close(a, b, tol=1e-6):
    return abs(a - b) <= tol


class _FixedRNG:
    """Returns the given numbers in order, so a test knows exactly what was drawn."""
    def __init__(self, *values):
        self.values = list(values)
        self.draws = 0

    def random(self):
        self.draws += 1
        return self.values.pop(0)


def test_temperature_sharpens_and_flattens():
    """softmax_with_temperature() divides logits by T before softmax"""
    p1 = softmax_with_temperature([2.0, 1.0, 0.1], 1.0)
    assert p1 and _close(sum(p1), 1.0), f"probabilities must sum to 1, got {p1!r}"
    assert [round(x, 2) for x in p1] == [0.66, 0.24, 0.1], f"T=1 gives [0.66, 0.24, 0.10], got {p1}"
    cold = softmax_with_temperature([2.0, 1.0, 0.1], 0.5)
    hot = softmax_with_temperature([2.0, 1.0, 0.1], 2.0)
    assert [round(x, 2) for x in cold] == [0.86, 0.12, 0.02], f"T=0.5 gives [0.86, 0.12, 0.02], got {cold}"
    assert [round(x, 2) for x in hot] == [0.5, 0.3, 0.19], f"T=2 gives [0.50, 0.30, 0.19], got {hot}"
    big = softmax_with_temperature([1000.0, 999.0], 1.0)
    assert big and _close(sum(big), 1.0), "subtract the max before math.exp so big logits don't overflow"


def test_temperature_zero_is_greedy():
    """Temperature 0 puts all probability on the first highest logit"""
    assert softmax_with_temperature([0.5, 3.0, 3.0, -1.0], 0) == [0.0, 1.0, 0.0, 0.0], "one-hot on the first max"


def test_top_k():
    """top_k_filter() keeps the k most likely tokens and renormalizes"""
    got = top_k_filter([0.5, 0.2, 0.2, 0.1], 2)
    assert got and all(_close(a, b) for a, b in zip(got, [0.5 / 0.7, 0.2 / 0.7, 0.0, 0.0])), \
        f"keep index 0 and the lower-index 0.2 (index 1), then renormalize; got {got}"


def test_top_p():
    """top_p_filter() keeps the smallest top set reaching p"""
    probs = softmax_with_temperature([2.0, 1.0, 0.1], 1.0)
    got = top_p_filter(probs, 0.9)
    assert got and got[2] == 0.0, f"the top two already sum to 0.901, so the third is dropped; got {got}"
    assert _close(got[0], 0.7310585786300049) and _close(sum(got), 1.0), f"renormalize the kept tokens; got {got}"
    one = top_p_filter([0.95, 0.03, 0.02], 0.9)
    assert one == [1.0, 0.0, 0.0], f"a confident step keeps just one token; got {one}"
    exact = top_p_filter([0.5, 0.3, 0.2], 0.8)
    assert exact[2] == 0.0 and _close(exact[0], 0.625), f"0.5 + 0.3 reaches 0.8 exactly, so stop there; got {exact}"


def test_sample_walks_the_distribution():
    """sample() draws one random number and walks the cumulative probabilities in index order"""
    logits = [math.log(0.5), math.log(0.3), math.log(0.2)]
    rng = _FixedRNG(0.49, 0.51, 0.79, 0.81)
    got = [sample(logits, rng=rng) for _ in range(4)]
    assert got == [0, 1, 1, 2], f"cumulative 0.5, 0.8, 1.0: r=0.49->0, 0.51->1, 0.79->1, 0.81->2; got {got}"
    assert rng.draws == 4, f"draw exactly one random number per sample() call, drew {rng.draws}"
    filtered = sample(logits, top_p=0.8, rng=_FixedRNG(0.99))
    assert filtered == 1, f"with top_p=0.8 only indices 0 and 1 survive, so r=0.99 lands on 1; got {filtered}"
    k1 = sample(logits, top_k=1, rng=_FixedRNG(0.99))
    assert k1 == 0, f"top_k=1 always returns the most likely token; got {k1}"


def test_seeded_sampling_is_reproducible():
    """The same seed gives the same draws, and the frequencies match the probabilities"""
    logits = [2.0, 1.0, 0.1]
    rng = random.Random(123)
    run2 = [sample(logits, rng=rng) for _ in range(50)]
    rng = random.Random(123)
    run3 = [sample(logits, rng=rng) for _ in range(50)]
    assert run2 == run3, "two runs with the same seed must produce the same sequence"
    rng = random.Random(2024)
    draws = [sample(logits, rng=rng) for _ in range(4000)]
    share = draws.count(0) / len(draws)
    assert abs(share - 0.659) < 0.03, f"index 0 has probability 0.659; it was drawn {share:.3f} of the time"
    assert sample(logits, temperature=0, rng=random.Random(1)) == 0, "temperature 0 always picks the top token"


def test_log_probs():
    """log_probs() returns stable log-softmax values"""
    lp = log_probs([2.0, 1.0, 0.1])
    assert lp and _close(lp[0], math.log(0.6590011388859679)), f"log_probs[0] should be log(0.659) = -0.417, got {lp}"
    big = log_probs([1000.0, 0.0])
    assert _close(big[0], 0.0, 1e-9) and big[1] < -999, f"compute it stably (log-sum-exp); got {big}"
