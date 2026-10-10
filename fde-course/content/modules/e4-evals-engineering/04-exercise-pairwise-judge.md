---
title: "Exercise: A Pairwise Judge You Can Trust"
type: exercise
minutes: 40
hints:
  - "`PAIRWISE_SCHEMA`: a closed set for the verdict, a free string for the short rationale, and the two settings every structured-output object needs."
  - "`ask_judge`: some replies can't be parsed at all. Decide from `stop_reason` before you touch the text, and find the text block by type."
  - "`judge_pair`: the second call swaps the positions, so 'first' means a different summary in each call. Translate both answers into A/B/tie before you compare them."
  - "`cohen_kappa`: compute observed agreement and chance agreement separately, as in the lesson's worked example. Think about what happens to the formula when both raters always use the same single label."
  - "`calibrate`: errors are neither agreements nor disagreements. Remove them first, then compute every rate on what's left. The reasons are checked against the thresholds in a fixed order."
---

Leo forwards you a thread from Saltmarsh Legal, a fictional law firm that uses Claude to summarize contract clauses for its associates. "They want to move to a new summarization prompt. Someone ran a model judge that compared old and new summaries and says the new one wins. Before I let a judge decide a migration, I want proof it's trustworthy. A senior associate has already compared ten pairs by hand. Build a pairwise judge that runs both orders, measure it against her labels, and tell me whether we can trust it."

`PAIRS` holds ten clauses. In each, `a` is the current prompt's summary, `b` is the new prompt's summary, and `human` is the associate's verdict: `"A"`, `"B"` or `"tie"`. `JUDGE_MODEL`, `JUDGE_SYSTEM` and `RUBRIC` are given. The judge model is deliberately not the model that writes the summaries.

## Your task

**1. `PAIRWISE_SCHEMA`**: an object with `winner` (string, enum `["first", "second", "tie"]`) and `rationale` (string). Both required, no extra properties. The judge sees positions, not version names, so the schema talks about positions too. The rationale is one or two sentences for the human reading disagreements; you don't need a long reasoning field, because the judge's adaptive thinking already deliberates before it answers.

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

Compare the two summaries against the rubric. Answer "first", "second" or "tie", with a one- or two-sentence rationale naming the deciding fact.
```

Nothing in it says which summary is old or new. Judges defer to labels like "baseline".

**3. `ask_judge(client, clause, first, second)`** makes **one** call: `JUDGE_MODEL`, `max_tokens` of at least 1024, `system=JUDGE_SYSTEM`, one user message with the prompt, and `output_config` with an explicit `effort` (use `"low"`) plus `"format": {"type": "json_schema", "schema": PAIRWISE_SCHEMA}`. `max_tokens` covers thinking too, so leave room (4096 is sensible). It returns the `winner` string. If `stop_reason` is `"refusal"` or `"max_tokens"`, it returns `"error"` without parsing.

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

## A caveat on ten pairs

Ten pairs keep the exercise fast. They are far too few for a real trust decision. A kappa computed on 10 items has a very wide interval: a single relabelled pair can move it by 0.1 to 0.2, so "0.688 clears 0.6" is not evidence of anything on its own. The calibration lesson recommends 50 to 200 cases, stratified and with plenty of borderline ones, plus a held-out split. In an interview, if you're shown a judge validated on ten examples, say so before you say anything else.
