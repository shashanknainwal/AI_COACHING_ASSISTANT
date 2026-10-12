---
title: "Exercise: A Small Eval Harness with an LLM Judge"
type: exercise
minutes: 35
hints:
  - "`exact_match`: normalize both sides with `\" \".join(text.lower().split()).rstrip(\".!\")`. Return False straight away if `got` is None."
  - "`judge`: build the prompt exactly as shown, then call `client.messages.create(model=JUDGE_MODEL, max_tokens=JUDGE_MAX_TOKENS, output_config={\"effort\": \"low\", \"format\": {\"type\": \"json_schema\", \"schema\": JUDGE_SCHEMA}}, messages=[...])`."
  - "Fail closed: if `stop_reason` isn't `end_turn`, or `json.loads` raises, or a key is missing, return `{\"pass\": False, \"reason\": \"judge_error\"}`. A broken judge must never count as a pass."
  - "`wilson_interval`: p = k/n, denom = 1 + z²/n, centre = (p + z²/(2n)) / denom, half = z·sqrt(p(1−p)/n + z²/(4n²)) / denom. Clamp to [0, 1], then round to 3."
  - "`run_eval`: loop cases, then `for run in range(n_runs)`, call `generate(case[\"input\"], run)`, grade by `case[\"grader\"]`, and count passes per case id. A case is flaky when 0 < passes < n_runs."
---

Mira Vasquez, this module's fictional interviewer, asks every candidate the same design follow-up: "You changed the prompt. How do you know it's better?" Candidates who say "I'd test it" get a second question: "Show me the harness, and tell me how sure you are."

You'll build that harness for a fictional retailer's support bot. It grades short labels with exact match and free-text replies with a rubric-graded LLM judge, runs every case several times, finds the flaky cases and reports a Wilson confidence interval. The judge call uses the simulated `anthropic` SDK; its replies are scripted for this exercise, but the code is what you'd run against the real API.

## Your task

**1. `exact_match(expected, got)`**: True if both match after normalizing: lowercase, collapse whitespace, strip, and remove a trailing `.` or `!`. `got=None` is False.

**2. `judge(client, rubric, question, answer)`** returns `{"pass": bool, "reason": str}`:

- One request with `model=JUDGE_MODEL`, `max_tokens=JUDGE_MAX_TOKENS` and `output_config={"effort": "low", "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}}`. No `temperature`.
- One user message, exactly:

```text
Rubric:
{rubric}

Question:
{question}

Answer:
{answer}

Grade the answer against the rubric.
```

- Parse the text block with `json.loads`. If `stop_reason` isn't `"end_turn"` or the JSON is unusable, return `{"pass": False, "reason": "judge_error"}`.

Effort is set explicitly because the judge model, Claude Haiku 5.5, thinks by default at `medium` effort. A narrow pass or fail rubric rarely needs it, and thinking tokens are billed as output and count toward `max_tokens`.

**3. `wilson_interval(k, n, z=1.96)`** returns `(low, high)` rounded to 3 decimals, clamped to [0, 1]. With `n == 0`, return `(0.0, 1.0)`.

**4. `run_eval(cases, generate, n_runs, client)`** calls `generate(case["input"], run)` for `run` in `0..n_runs-1`, grades with `exact_match` (grader `"exact"`, against `case["expected"]`) or `judge` (grader `"judge"`, with `case["rubric"]`), and returns:

```python
{"trials": 15, "passes": 13, "pass_rate": 0.867,            # pass_rate rounded to 3
 "per_case": {"intent-1": 3, "intent-2": 2, ...},           # passes per case id
 "flaky": ["intent-2", "reply-2"],                          # 0 < passes < n_runs, in case order
 "interval": (0.621, 0.963)}                                 # wilson_interval(passes, trials)
```

## Example

```text
pass rate 0.867 over 15 trials, 95% CI (0.621, 0.963)
per case: {'intent-1': 3, 'intent-2': 2, 'intent-3': 3, 'reply-1': 3, 'reply-2': 2}
flaky: ['intent-2', 'reply-2']
```

Press **Run**, then **Submit**.

## After you pass: read your own report

Look at the interval: 62% to 96%. With five cases you can't tell this bot from one that's 70% accurate. Say what you'd do next: add real cases (especially refunds and final-sale questions, the flaky ones), calibrate the judge against hand grades, and only then compare prompts.

> **Interview tip:** Always say the interval with the number. "87%, but on 15 trials the 95% interval is 62 to 96, so I'd want about 200 cases before calling a winner."
