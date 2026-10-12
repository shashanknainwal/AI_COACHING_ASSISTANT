import math


def _close(a, b, tol=1e-6):
    return abs(a - b) <= tol


def test_softmax_sums_to_one():
    """softmax() returns probabilities that sum to 1, in the same order"""
    p = softmax([2.0, 1.0, 0.1])
    assert isinstance(p, list) and len(p) == 3, f"return a list of 3 probabilities, got {p!r}"
    assert _close(sum(p), 1.0), f"probabilities must sum to 1, got {sum(p)}"
    assert p[0] > p[1] > p[2], f"a higher score must get a higher probability, got {p}"
    assert _close(p[0], 0.6590011388859679), f"softmax([2, 1, 0.1])[0] should be about 0.659, got {p[0]}"


def test_softmax_is_stable():
    """softmax() handles very large scores without overflowing"""
    p = softmax([1000.0, 1000.0])
    assert p and _close(p[0], 0.5) and _close(p[1], 0.5), f"subtract max(xs) before math.exp; got {p}"


def test_attention_weights():
    """attention() scales by sqrt(d) and softmaxes the scores"""
    out = attention([1, 0], [[1, 0], [0, 1], [1, 1]], [[10, 0], [0, 10], [5, 5]])
    assert isinstance(out, tuple) and len(out) == 2, f"return (weights, output), got {out!r}"
    w, _ = out
    s = 1 / math.sqrt(2)
    expected = softmax([s, 0.0, s])
    assert all(_close(a, b) for a, b in zip(w, expected)), f"weights should be softmax([1/sqrt(2), 0, 1/sqrt(2)]) = {expected}, got {w}"


def test_attention_output_is_weighted_sum():
    """attention() returns the weighted average of the value vectors"""
    w, o = attention([1, 0], [[1, 0], [0, 1], [1, 1]], [[10, 0], [0, 10], [5, 5]])
    assert len(o) == 2, f"output must have the same length as each value vector, got {o}"
    assert _close(o[0], 10 * w[0] + 5 * w[2]) and _close(o[1], 10 * w[1] + 5 * w[2]), f"output[j] = sum(w_i * v_i[j]); got {o}"
    w2, o2 = attention([0, 0, 0, 0], [[1, 2, 3, 4], [4, 3, 2, 1]], [[1.0], [3.0]])
    assert _close(w2[0], 0.5) and _close(o2[0], 2.0), f"a zero query attends equally: weights [0.5, 0.5], output [2.0]; got {w2}, {o2}"


def test_latency_cold_and_cached():
    """estimate_latency() splits prefill, thinking and decode, and skips cached prefill"""
    cold = estimate_latency(60_000, 400, 300, prefill_tps=8_000, decode_tps=80)
    assert cold == {"ttft_s": 11.55, "total_s": 16.55}, f"0.3 + 60000/8000 + 300/80 = 11.55 TTFT, + 400/80 = 16.55 total; got {cold}"
    warm = estimate_latency(60_000, 400, 300, prefill_tps=8_000, decode_tps=80, cached_tokens=58_000)
    assert warm == {"ttft_s": 4.3, "total_s": 9.3}, f"only 2,000 uncached tokens go through prefill; got {warm}"


def test_latency_thinking_counts_before_first_token():
    """Thinking tokens sit inside time to first visible token"""
    a = estimate_latency(1_000, 100, 0, prefill_tps=10_000, decode_tps=50, overhead_s=0.0)
    b = estimate_latency(1_000, 100, 500, prefill_tps=10_000, decode_tps=50, overhead_s=0.0)
    assert a == {"ttft_s": 0.1, "total_s": 2.1}, f"got {a}"
    assert b == {"ttft_s": 10.1, "total_s": 12.1}, f"500 thinking tokens at 50 tok/s add 10 s to TTFT; got {b}"


def test_kv_cache_bytes():
    """kv_cache_bytes() grows linearly with context length"""
    big = kv_cache_bytes(100_000, layers=60, kv_heads=8, head_dim=128)
    assert big == 24_576_000_000, f"2 x 100000 x 60 x 8 x 128 x 2 = 24,576,000,000; got {big!r}"
    small = kv_cache_bytes(10_000, layers=60, kv_heads=8, head_dim=128)
    assert small * 10 == big, "ten times the tokens should need ten times the memory"
    assert kv_cache_bytes(1, 1, 1, 1, bytes_per_value=4) == 8, "bytes_per_value must be used"
