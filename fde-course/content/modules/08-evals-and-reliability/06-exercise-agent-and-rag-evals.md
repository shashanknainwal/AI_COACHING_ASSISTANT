---
title: "Exercise: Evaluate an Agent and a Retriever"
type: exercise
minutes: 35
hints:
  - "Required tools in order: keep a position `i` in the required list; walk the tool names and advance `i` whenever the tool equals `required[i]`. Pass if `i` reaches the end."
  - "Use `expect.get(\"forbidden\", [])`, `expect.get(\"max_steps\")` and so on, so that missing expectations pass. For `max_credit`, check every `issue_store_credit` call's `input[\"amount\"]`."
  - "Build the checks dict in this order: `required_in_order`, `no_forbidden`, `within_steps`, `credit_within_limit`, `answer_includes`. `pass` is `all(checks.values())`."
  - "`recall_at_k`: `len(set(retrieved[:k]) & set(relevant)) / len(relevant)`. `reciprocal_rank`: `for rank, cid in enumerate(retrieved, 1)`."
  - "`retrieval_report`: call `search_fn(case[\"query\"], k)` once per case, average the two metrics, round to 3 decimals, and list cases with recall below 1 as misses."
---

A support agent can give the right answer the wrong way, for example by issuing credit without checking that the shipment was actually late. And a RAG system can fail before Claude sees anything, if retrieval misses the right chunk. Both need evals that look **inside** the system, not just at the final answer.

You're given six recorded runs of the Module 7 agent (`AGENT_CASES`, each with an `expect` dict) and the Module 7 keyword search (`keyword_search(query, k)`) with six labeled queries (`RETRIEVAL_CASES`).

## Part 1: trajectory evals

**1. `grade_trajectory(run, expect)`** returns `{"checks": {...}, "pass": bool}` with these five checks:

| Check | Passes when | Expectation key |
|---|---|---|
| `required_in_order` | The `required` tools all appear in the trace, in that order (other calls may come in between) | `required` |
| `no_forbidden` | No `forbidden` tool was called | `forbidden` |
| `within_steps` | `run["steps"] <= max_steps` | `max_steps` |
| `credit_within_limit` | Every `issue_store_credit` call has `amount <= max_credit` | `max_credit` |
| `answer_includes` | Every string appears in the answer (case-insensitive) | `answer_includes` |

If an expectation key is missing, its check passes. `pass` is true only if all five pass.

**2. `trajectory_report(cases)`** returns:

```python
{"pass_rate": 0.333,
 "failed_checks": {"required_in_order": 1, ...},    # how many cases failed each check
 "failures": {"A-2": ["required_in_order"], ...}}   # failed check names per failing case, in check order
```

## Part 2: retrieval evals

**3. `recall_at_k(retrieved, relevant, k)`**: the share of `relevant` IDs that appear in `retrieved[:k]`.

**4. `reciprocal_rank(retrieved, relevant)`**: `1 / rank` of the first relevant ID (rank 1 is the first result), or `0.0` if none was retrieved.

**5. `retrieval_report(search_fn, cases, k=3)`** calls `search_fn(query, k)` once per case and returns `{"recall_at_k": mean recall, "mrr": mean reciprocal rank, "misses": [ids with recall < 1]}`, with means rounded to 3 decimals.

Press **Run**. Notice that A-2's final answer looks fine but its process doesn't, and that "Refund my couch" fails at retrieval. Then **Submit**.
