---
title: "Exercise: Temperature, Top-p and a Seeded Sampler"
type: exercise
minutes: 30
hints:
  - "`softmax_with_temperature`: handle `temperature <= 0` first with `logits.index(max(logits))`. Otherwise divide each logit by the temperature, subtract the max, exponentiate and normalize."
  - "Rank indices with `sorted(range(len(probs)), key=lambda i: (-probs[i], i))`. That gives most likely first, and lower index first on ties. Both filters use it."
  - "`top_p_filter`: walk the ranked indices, adding each to a kept set and its probability to a running total. Stop as soon as the total is at least p (allow a tiny tolerance such as `p - 1e-12`). Then divide each kept probability by the kept total."
  - "`sample`: draw `r = rng.random()` once, then walk the filtered probabilities in index order (0, 1, 2, ...) and return the first index where `r < cumulative`."
  - "`log_probs`: `log p_i = z_i - (m + log(sum(exp(z_j - m))))`, where m is the max logit."
---

Mira Vasquez, the fictional interviewer for this module, has a follow-up she uses on anyone who says "temperature controls randomness": "Write the sampler. Then tell me where the randomness actually comes from, and why setting temperature to zero doesn't make our API deterministic."

You'll implement the decoding step every LLM runs after the forward pass: temperature, top-k, top-p, a seeded draw, and log probabilities. The seeded random generator is passed in, which is how you make tests reproducible, and also why a vendor's seed parameter can only reproduce the *sampler*, not the floating-point arithmetic before it.

## Your task

**1. `softmax_with_temperature(logits, temperature)`** returns probabilities of `logit / temperature`. Subtract the max before `math.exp`. If `temperature <= 0`, return a one-hot list on the first highest logit (greedy decoding).

**2. `top_k_filter(probs, k)`** keeps the `k` most likely tokens, zeroes the rest and renormalizes. Ties go to the lower index.

**3. `top_p_filter(probs, p)`** keeps the smallest set of most likely tokens whose probabilities add up to at least `p`, zeroes the rest and renormalizes. Same tie rule.

**4. `sample(logits, temperature=1.0, top_k=None, top_p=None, rng=None)`**:

- compute probabilities with temperature, then apply `top_k`, then `top_p` (only those given);
- draw **exactly one** `r = rng.random()`;
- walk the probabilities in index order, keeping a running total, and return the first index where `r < total`.

If `rng` is `None`, use `random.Random()`.

**5. `log_probs(logits)`** returns natural-log probabilities at temperature 1, computed stably with the log-sum-exp trick.

## Example

```python
softmax_with_temperature([2.0, 1.0, 0.1], 1.0)   # [0.659, 0.242, 0.099]
softmax_with_temperature([2.0, 1.0, 0.1], 0.5)   # [0.862, 0.117, 0.019]
softmax_with_temperature([2.0, 1.0, 0.1], 0)     # [1.0, 0.0, 0.0]
top_p_filter([0.659, 0.242, 0.099], 0.9)          # [0.731, 0.269, 0.0]

rng = random.Random(42)
[sample([2.0, 1.0, 0.1, -1.0], top_p=0.9, rng=rng) for _ in range(5)]   # same 5 draws every time with seed 42
```

Press **Run**, then **Submit**.

## After you pass: answer Mira

In two or three sentences, say why your seeded sampler is reproducible but a provider's API at temperature 0 isn't. The key ideas: your logits are computed once, exactly, in plain Python; a provider's logits come from batched floating-point arithmetic whose summation order depends on what else is in the batch, so near-ties can flip and the outputs then diverge.

> **Interview tip:** When you explain top-p, use one confident step and one uncertain step as the example. "When the model is sure, top-p keeps one token. When it's unsure, it keeps twenty. Top-k keeps the same number either way."
