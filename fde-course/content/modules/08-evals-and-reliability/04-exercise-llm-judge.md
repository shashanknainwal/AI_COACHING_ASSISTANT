---
title: "Exercise: Calibrate an LLM-as-Judge"
type: exercise
minutes: 35
hints:
  - "`JUDGE_SCHEMA`: Python dicts keep insertion order, so write `reasoning` before `verdict` in `properties`, and list them in that order in `required`."
  - "`build_judge_prompt`: build a list of lines (`\"<rubric>\", RUBRIC, \"</rubric>\", \"\", ...`) and join with `\"\\n\"`."
  - "`judge`: check `response.stop_reason == \"refusal\"` before parsing the text block with `json.loads`."
  - "Cohen's kappa: `po` is the share of matching pairs; `pe = jp*hp + (1-jp)*(1-hp)` where `jp` and `hp` are each side's pass rate; `kappa = (po - pe) / (1 - pe)`. If `pe == 1`, use 1.0 when `po == 1`, else 0.0."
  - "`calibrate`: collect `judge(client, case)[\"verdict\"]` for every case, then call `agreement` with the human labels. A disagreement is a case where the verdict isn't \"error\" and differs from `case[\"human\"]`."
---

Brightway's help-center assistant writes free-text answers, so exact-match grading won't work. You'll build an **LLM-as-judge** grader. Before anyone trusts its scores, you'll **calibrate** it against 12 answers a Brightway support lead has already labeled (`JUDGE_CASES`).

`RUBRIC`, `JUDGE_SYSTEM` and `JUDGE_MODEL` are given.

## Your task

**1. `JUDGE_SCHEMA`**: `reasoning` (string) **first**, then `verdict` (string, enum `["pass", "fail"]`). Both required, no extra properties. The order matters: the judge reasons before it decides.

**2. `build_judge_prompt(case)`** returns (lines joined with `"\n"`):

```
<rubric>
...RUBRIC...
</rubric>

<question>
Can I return a sofa?
</question>

<reference_answer>
Yes, within 14 days of delivery, with a $49 pickup fee.
</reference_answer>

<candidate_answer>
Yes, sofas can be returned within 30 days for free.
</candidate_answer>

Grade the candidate answer against the rubric. Explain your reasoning first, then give the verdict.
```

**3. `judge(client, case)`** calls `JUDGE_MODEL` with `max_tokens` ≥ 1024, `system=JUDGE_SYSTEM`, one user message with the prompt, and `output_config={"format": {"type": "json_schema", "schema": JUDGE_SCHEMA}}`. It returns `{"verdict", "reasoning"}`. On a refusal, it returns `{"verdict": "error", "reasoning": "refused"}`.

**4. `agreement(judge_verdicts, human_verdicts)`** compares two lists of `"pass"`/`"fail"` labels and returns:

```python
{"n": 12, "accuracy": 0.833, "kappa": 0.667, "false_pass": 1, "false_fail": 1, "errors": 0}
```

- Skip pairs where the judge said `"error"`, and count them in `errors`. `n` is the number of pairs left.
- `false_pass`: the judge passed an answer the human failed (the dangerous kind). `false_fail` is the reverse.
- `kappa` is Cohen's kappa (agreement corrected for chance; see the lesson). Round `accuracy` and `kappa` to 3 decimals.

**5. `calibrate(client, cases)`** judges every case and returns `{"report": agreement(...), "disagreements": [ids]}`.

Press **Run** and read the two disagreements. Can you tell what each one reveals about the judge? Then **Submit**.
