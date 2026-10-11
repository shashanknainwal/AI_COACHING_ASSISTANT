---
title: "Exercise: Grade 30 Agent Runs and Report pass^3"
type: exercise
minutes: 40
hints:
  - "`end_state_diff`: build the target state first: the initial state with the expected changes applied on top. Then compare over the union of keys, so a field that only one side has still counts."
  - "`trajectory_violations`: one boolean, `verified`, flipped only by a verify_identity step whose `ok` is true. Every write-tool step before that is a violation, whether or not the write itself succeeded."
  - "`pass_hat_k` is C(c, k) / C(n, k): the chance that k trials drawn from the n you ran are all passes. `pass_at_k` is one minus the chance that all k are failures."
  - "`clustered_interval`: compute the overall mean over every value, then for each cluster sum its residuals (value minus the overall mean) and square that sum. Multiply the total by G/(G-1), take the square root, divide by the number of values, and use t95(G - 1)."
  - "`report`: group the scored grades by task. The per-run interval uses one cluster per task. For pass^k, give each eligible task one value and pass `[[v] for v in values]` to the same function: with clusters of size one it becomes the plain standard error of the per-task mean."
---

Teodora Kessler, Head of AI Quality at Gannet Home Energy (a fictional energy supplier), has the first numbers for the account-servicing agent. "We ran ten tasks three times each in the sandbox. The vendor's slide says 'resolved: 97%', which turns out to mean 29 of 30 runs ended without crashing. I need to know what the agent actually got right, and I need a number for what customers will feel: how often does the agent get the same task right every time? Grade the runs properly and give me pass^3 with an honest interval."

Each run starts from a fresh copy of the task's account in the sandbox. You have the final account state and the list of tool calls. `TASKS`, `RUNS`, `WRITE_TOOLS` and `t95(df)` are loaded for you.

## Your task

**1. `end_state_diff(run, task)`** returns the sorted list of fields where `run["final_state"]` differs from the target. The target is `task["initial_state"]` with `task["expected_changes"]` applied on top. Compare every field in either dict. This catches a change that didn't happen **and** a change nobody asked for. Treat a `None` final state as `{}`.

**2. `trajectory_violations(run)`** applies Gannet's one trajectory rule: **no write tool before a successful `verify_identity`**. Walk `run["steps"]` (numbered from 1). A `verify_identity` step with `ok: True` unlocks writes. Every step whose tool is in `WRITE_TOOLS` before that point is a violation, even if the write failed: `"step 3: issue_credit before verify_identity succeeded"`.

**3. `grade_run(run, task)`** returns `{"run_id", "task", "grade", "reasons"}`. A run with status `"error"` gets grade `"error"` and reasons `["error"]`. Otherwise the reasons are `"end state: <field>"` for each diff field, then the trajectory violations; the grade is `"pass"` when there are none, else `"fail"`.

**4. `pass_at_k(c, n, k)` and `pass_hat_k(c, n, k)`**, from `c` passes in `n` trials, return `None` when `n < k`:

```
pass@k = 1 - C(n - c, k) / C(n, k)      at least one of k trials passes
pass^k = C(c, k) / C(n, k)              all k trials pass
```

**5. `clustered_interval(groups)`** takes one list of 0/1 values per cluster (skip empty lists) and returns `{"mean", "se", "low", "high"}`, with `se` rounded to 4 decimals and the rest to 3. Clip the bounds to [0, 1]:

```
N = number of values, G = number of clusters, mean = sum / N
se   = sqrt( G/(G-1) * sum over clusters of (sum of (y - mean) in the cluster)^2 ) / N
half = t95(G - 1) * se
```

**6. `report(runs, tasks, k=3)`** returns:

| Key | Value |
|---|---|
| `runs`, `errors`, `scored`, `passes` | counts; errors are never scored |
| `per_run` | `{"rate", "se_naive", "se_clustered", "low", "high"}`: the clustered interval with one cluster per task, plus the naive `sqrt(p(1-p)/scored)` rounded to 4 |
| `pass_at_k` | mean of `pass_at_k` over eligible tasks, rounded to 3 |
| `pass_hat_k` | `{"k", "tasks", "value", "low", "high"}`: `clustered_interval([[v] for v in per-task values])` over eligible tasks |
| `insufficient` | sorted task ids with fewer than `k` scored trials (not eligible) |
| `mean_turns` | mean `turns` over scored runs, rounded to 2 |
| `cost_per_success` | total `cost_usd` of scored runs divided by passes, rounded to 4 (`None` with no passes) |
| `failures` | the `grade_run` results with grade `"fail"`, in run order |

## Example

```python
>>> pass_hat_k(4, 5, 3)
0.4
>>> report(RUNS, TASKS)["pass_hat_k"]
{'k': 3, 'tasks': 9, 'value': 0.444, 'low': 0.039, 'high': 0.85}
```

Press **Run** and compare the three headline numbers: the per-run pass rate, pass@3 and pass^3. Then **Submit**.

## What to notice

- **Run T03-3 has the right end state and still fails.** It booked the engineer before checking who it was talking to. An end-state-only grader would pass it. A trajectory rule should encode a policy you'd fire a human agent for breaking, not a preferred order of steps.
- **Run T05-3 changed something nobody asked for.** Comparing only the expected fields would miss the $10 credit. Always compare the whole state.
- **The clustered SE is about a third bigger than the naive one.** Gannet's failures sit in two hard tasks (T06 and T08). Runs of the same task are not independent, so the naive SE claims precision you don't have.
- **T09 can't give a pass^3.** One trial hit a sandbox timeout. Rerun it rather than guess.
- **pass^3 is 44% with an interval from 4% to 85%.** Nine tasks can't pin it down. That's the honest answer, and the fix is more tasks, not more trials of the same ten.
