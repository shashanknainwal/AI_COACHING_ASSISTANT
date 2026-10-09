---
title: "Exercise: Pick the Model"
type: exercise
minutes: 30
hints:
  - "Start with a helper that filters the table: keep a candidate only if `quality >= min_quality`, `p95_latency_ms <= max_latency_ms` and `cost_per_1k_requests <= budget_per_1k`. All three limits are inclusive."
  - "If the filtered list is empty, return `None`. Otherwise use `min()` with a sort key."
  - "The key `(c[\"cost_per_1k_requests\"], -c[\"quality\"], c[\"name\"])` sorts by cost ascending, then quality descending, then name."
  - "In `explain_choice`, format numbers with f-strings: `f\"{q:.2f}\"` gives `0.91`, and `f\"${cost:.2f}\"` gives `$6.00`. Count qualifying models with the same filter helper."
---

In a mock design round, your interview coach Nadia Okafor slides a table across the (virtual) desk. "Here are eval results for four models on the customer's ticket-routing task. Quality is the pass rate on 400 real tickets. The product needs 90% quality, a p95 latency under three seconds, and the customer won't pay more than $15 per thousand requests. Which model, and why?"

This is an original practice scenario, not a real interview question. It tests a habit any design-round interviewer will notice: do you apply the constraints first and optimise second, or just pick the "best" model? The models are labelled A to D on purpose. The point is the reasoning, not brand loyalty.

## The inputs

Each candidate is a dictionary:

```python
{
    "name": "Model D",
    "quality": 0.91,              # eval pass rate, 0 to 1
    "p95_latency_ms": 2600,       # 95th percentile end-to-end latency
    "cost_per_1k_requests": 6.00, # dollars per 1,000 requests at this workload's token counts
}
```

## Your task

**1. `choose_model(candidates, min_quality, max_latency_ms, budget_per_1k)`** returns the **name** of the model to use:

1. Keep only candidates with `quality >= min_quality`, `p95_latency_ms <= max_latency_ms` and `cost_per_1k_requests <= budget_per_1k`. All limits are inclusive.
2. Of those, return the **cheapest**. Break ties by **higher quality**, then by **name** alphabetically.
3. Return `None` if nothing qualifies (including an empty table).
4. Don't modify the input list.

**2. `explain_choice(candidates, min_quality, max_latency_ms, budget_per_1k)`** returns one line in exactly this format.

When a model is chosen:

```
{name}: quality {quality:.2f}, p95 {p95_latency_ms} ms, ${cost:.2f}/1k requests ({k} of {n} qualified)
```

where `k` is the number of candidates that met every constraint and `n` is the number of candidates.

When nothing qualifies:

```
No model qualifies: 0 of {n} meet quality >= {min_quality:.2f}, p95 <= {max_latency_ms} ms, cost <= ${budget_per_1k:.2f}/1k
```

## Example

```python
eval_table = [
    {"name": "Model A", "quality": 0.96, "p95_latency_ms": 4200, "cost_per_1k_requests": 22.00},
    {"name": "Model B", "quality": 0.93, "p95_latency_ms": 2100, "cost_per_1k_requests": 11.00},
    {"name": "Model C", "quality": 0.81, "p95_latency_ms": 900,  "cost_per_1k_requests": 0.55},
    {"name": "Model D", "quality": 0.91, "p95_latency_ms": 2600, "cost_per_1k_requests": 6.00},
]

choose_model(eval_table, 0.90, 3000, 15.00)    # -> "Model D"
explain_choice(eval_table, 0.90, 3000, 15.00)
# -> "Model D: quality 0.91, p95 2600 ms, $6.00/1k requests (2 of 4 qualified)"
```

Model A is the most accurate but too slow and over budget. Model C is fast and cheap but misses the quality bar. B and D both qualify, and D is cheaper.

Press **Run** to try the sample at the bottom of the file, then **Submit** to grade it.

> **Interview tip:** After you pick, say what would change your answer. "D clears the bar by one point. With 400 examples that's a thin margin, so I'd check its failures by category, and I'd also test the strongest model at a lower effort setting before committing, since one model also means one prompt cache." Constraints first, cheapest second, risks out loud.
