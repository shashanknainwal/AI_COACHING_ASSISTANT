---
title: "Exercise: A Pairwise Judge You Can Trust"
type: exercise
minutes: 40
hints:
  - "`PAIRWISE_SCHEMA`: an object whose `properties` are `reasoning` (string) then `winner` (string, enum `[\"first\", \"second\", \"tie\"]`), with both in `required` in that order and `additionalProperties: False`."
  - "`ask_judge`: check `response.stop_reason in (\"refusal\", \"max_tokens\")` before parsing. Then `json.loads` the first block whose `type` is `\"text\"` and return its `winner`."
  - "`judge_pair`: call 1 is `(pair[\"a\"], pair[\"b\"])`, call 2 is `(pair[\"b\"], pair[\"a\"])`. Map call 1 with `{\"first\": \"A\", \"second\": \"B\", \"tie\": \"tie\"}` and call 2 with `{\"first\": \"B\", \"second\": \"A\", \"tie\": \"tie\"}`, then compare."
  - "`cohen_kappa`: `po` is the share of positions where the two lists match. `pe = sum((r1.count(l) / n) * (r2.count(l) / n) for l in labels)`. Handle `pe == 1` before dividing."
  - "`calibrate`: judge every pair once, drop the ones whose verdict is `\"error\"`, then compute agreement, kappa and consistency on the rest. Build the reason strings with `f\"kappa {kappa:.3f} below {min_kappa}\"` and `f\"position consistency {consistency:.3f} below {min_consistency}\"`."
---

Leo forwards you a thread from Saltmarsh Legal, a fictional law firm that uses Claude to summarize contract clauses for its associates. "They want to move to a new summarization prompt. Someone ran a model judge that compared old and new summaries and says the new one wins. Before I let a judge decide a migration, I want proof it's trustworthy. A senior associate has already compared ten pairs by hand. Build a pairwise judge that runs both orders, measure it against her labels, and tell me whether we can trust it."

`PAIRS` holds ten clauses. In each, `a` is the current prompt's summary, `b` is the new prompt's summary, and `human` is the associate's verdict: `"A"`, `"B"` or `"tie"`. `JUDGE_MODEL`, `JUDGE_SYSTEM` and `RUBRIC` are given. The judge model is deliberately not the model that writes the summaries.

## Your task

**1. `PAIRWISE_SCHEMA`**: an object with `reasoning` (string) **first**, then `winner` (string, enum `["first", "second", "tie"]`). Both required, no extra properties. The judge sees positions, not version names, so the schema talks about positions too.

**2. `build_prompt(clause, first, second)`** returns these lines joined with `"\n"`:

```
<rubric>
...RUBRIC...
</rubric>

<clause>
...clause...
</clause>

<response_1>
...first...
</response_1>

<response_2>
...second...
</response_2>

Compare the two summaries against the rubric. Explain your reasoning first, then answer "first", "second" or "tie".
```

Nothing in it says which summary is old or new. Judges defer to labels like "baseline".

**3. `ask_judge(client, clause, first, second)`** makes **one** call: `JUDGE_MODEL`, `max_tokens` of at least 1024, `system=JUDGE_SYSTEM`, one user message with the prompt, and `output_config={"format": {"type": "json_schema", "schema": PAIRWISE_SCHEMA}}`. It returns the `winner` string. If `stop_reason` is `"refusal"` or `"max_tokens"`, it returns `"error"` without parsing.

**4. `judge_pair(client, pair)`** runs the judge **twice**: first with A in position 1, then with B in position 1. It translates each answer back to `"A"`, `"B"` or `"tie"` and returns:

| Both orders say | Result |
|---|---|
| The same label | `{"verdict": <that label>, "consistent": True}` |
| Different labels | `{"verdict": "tie", "consistent": False}` (position bias: no real preference) |
| Either call returned `"error"` | `{"verdict": "error", "consistent": False}` |

**5. `cohen_kappa(rater1, rater2, labels=("A", "B", "tie"))`** returns kappa for two equal-length label lists, rounded to 3 decimals:

```
po = share of positions where the lists agree
pe = sum over labels L of (share of rater1 = L) × (share of rater2 = L)
kappa = (po − pe) / (1 − pe)
```

If `pe == 1`, return `1.0` when `po == 1`, else `0.0`. For empty lists, return `0.0`.

**6. `calibrate(client, pairs, min_kappa=0.6, min_consistency=0.8)`** judges every pair once (two calls each) and returns:

```python
{"n": 10, "errors": 0, "agreement": 0.8, "kappa": 0.688, "consistency": 0.7,
 "trusted": False, "reasons": ["position consistency 0.700 below 0.8"],
 "disagreements": ["P-03", "P-07"]}
```

- Pairs with verdict `"error"` are counted in `errors` and left out of everything else. `n` is the number left.
- `agreement` is the share of those pairs where the verdict equals `human`. `consistency` is the share that were consistent. Both are rounded to 3 decimals (`0.0` when `n` is 0).
- `kappa` is `cohen_kappa(judge_verdicts, human_verdicts)` over the same pairs.
- `reasons`, in this order: `f"kappa {kappa:.3f} below {min_kappa}"` if kappa is below the bar, and `f"position consistency {consistency:.3f} below {min_consistency}"` if consistency is below its bar. If `n` is 0, the only reason is `"no pairs could be judged"`.
- `trusted` is true only when there are no reasons. `disagreements` lists the IDs where the verdict differs from `human`, in input order.

Press **Run**. The judge agrees with the associate 80% of the time and its kappa clears the bar, yet it isn't trusted. Look at which pairs flipped when the order changed and what those pairs have in common. What would you change in the rubric or the setup before re-running? Then **Submit**.
