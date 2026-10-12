import math


def softmax(xs):
    """Return probabilities that sum to 1. Subtract max(xs) first for stability."""
    # TODO
    pass


def attention(query, keys, values):
    """Scaled dot-product attention for one query. Returns (weights, output)."""
    # TODO
    pass


def estimate_latency(prompt_tokens, output_tokens, thinking_tokens, prefill_tps, decode_tps,
                     cached_tokens=0, overhead_s=0.3):
    """Return {"ttft_s": ..., "total_s": ...}, each rounded to 2 decimals."""
    # TODO
    pass


def kv_cache_bytes(tokens, layers, kv_heads, head_dim, bytes_per_value=2):
    """Bytes of KV cache for one sequence: 2 x tokens x layers x kv_heads x head_dim x bytes."""
    # TODO
    pass


# --- Try it out (not graded) ---
print("softmax:", softmax([2.0, 1.0, 0.1]))
print("attention:", attention([1, 0], [[1, 0], [0, 1], [1, 1]], [[10, 0], [0, 10], [5, 5]]))
print("cold:  ", estimate_latency(60_000, 400, 300, prefill_tps=8_000, decode_tps=80))
print("cached:", estimate_latency(60_000, 400, 300, prefill_tps=8_000, decode_tps=80, cached_tokens=58_000))
size = kv_cache_bytes(100_000, layers=60, kv_heads=8, head_dim=128)
if size:
    print(f"KV cache for one 100K-token sequence: {size / 1e9:.1f} GB")
