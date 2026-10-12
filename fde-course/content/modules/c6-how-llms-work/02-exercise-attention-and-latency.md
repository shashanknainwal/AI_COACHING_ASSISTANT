---
title: "Exercise: Attention by Hand and a Latency Estimator"
type: exercise
minutes: 30
hints:
  - "`softmax`: subtract `max(xs)` from every score before calling `math.exp`. It gives the same answer and avoids overflow on big scores."
  - "`attention`: the score for key i is `sum(q * k for q, k in zip(query, keys[i])) / math.sqrt(len(query))`. Softmax the scores, then the output's dimension j is `sum(w * v[j] for w, v in zip(weights, values))`."
  - "`estimate_latency`: only `prompt_tokens - cached_tokens` go through prefill. Thinking tokens are decoded before the visible answer, so they belong in TTFT."
  - "`kv_cache_bytes`: the 2 counts keys and values. Multiply 2 x tokens x layers x kv_heads x head_dim x bytes_per_value."
---

Mira Vasquez, the fictional interviewer who runs this module's fundamentals rounds, has one habit candidates dread. When you say "attention is a weighted lookup", she slides a sheet of paper across and says: "Show me. Three tokens, two dimensions." When you say "long prompts are slower", she asks: "How much slower, and which part of the request?"

So you'll build both answers in code. First, one attention step on toy vectors. Then a latency estimator that separates prefill from decode and counts thinking tokens, and a KV-cache sizer that shows why long contexts are expensive to serve. All speeds and model shapes here are illustrative, not any vendor's real numbers.

## Your task

**1. `softmax(xs)`** returns a list of probabilities that sum to 1. Subtract the maximum before exponentiating so large scores don't overflow.

**2. `attention(query, keys, values)`** runs scaled dot-product attention for one query and returns `(weights, output)`:

- score for key i = dot(query, keys[i]) / sqrt(d), where d = `len(query)`
- `weights = softmax(scores)`
- `output[j] = sum(weights[i] * values[i][j])`, a list as long as each value vector

**3. `estimate_latency(prompt_tokens, output_tokens, thinking_tokens, prefill_tps, decode_tps, cached_tokens=0, overhead_s=0.3)`** returns `{"ttft_s": ..., "total_s": ...}`, each rounded to 2 decimals:

```text
ttft_s  = overhead_s + (prompt_tokens - cached_tokens) / prefill_tps + thinking_tokens / decode_tps
total_s = ttft_s + output_tokens / decode_tps
```

`ttft_s` here is time to the first *visible* token. In this toy model, cached prefix tokens skip prefill entirely. Compute `total_s` from the unrounded TTFT.

**4. `kv_cache_bytes(tokens, layers, kv_heads, head_dim, bytes_per_value=2)`** returns `2 * tokens * layers * kv_heads * head_dim * bytes_per_value` as an int.

## Example

```python
weights, out = attention([1, 0], [[1, 0], [0, 1], [1, 1]], [[10, 0], [0, 10], [5, 5]])
# weights ≈ [0.401, 0.198, 0.401]   (keys 1 and 3 match the query equally)
# out     ≈ [6.02, 3.98]

estimate_latency(60_000, 400, 300, prefill_tps=8_000, decode_tps=80)
# {"ttft_s": 11.55, "total_s": 16.55}
estimate_latency(60_000, 400, 300, prefill_tps=8_000, decode_tps=80, cached_tokens=58_000)
# {"ttft_s": 4.3, "total_s": 9.3}

kv_cache_bytes(100_000, layers=60, kv_heads=8, head_dim=128)   # 24_576_000_000 bytes, about 24.6 GB
```

The second call is the prompt-caching story in numbers: same model, same output, about 7 seconds less waiting. The thinking line is there on purpose. On models that think by default, those tokens are spent before the first word appears.

> **Interview tip:** When you give a latency estimate, split it. "About 7.5 seconds of prefill for 60K tokens, nearly 4 seconds of thinking, 5 seconds of output. Caching the manual removes most of the prefill; lowering effort shrinks the thinking."
