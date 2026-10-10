---
title: "Exercise: The POC Scorecard"
type: exercise
minutes: 35
hints:
  - "Write a small `_is_number(x)` helper: `isinstance(x, (int, float)) and not isinstance(x, bool)`. Use it for thresholds and for measurements."
  - "In `validate_criteria`, keep a `seen` set. For each criterion, check in this order: missing name (or duplicate), direction, threshold, baseline. Add the \"no must-have criterion\" line once, after the loop."
  - "In `evaluate_criterion`, compute `band = criterion.get(\"margin\", margin) * abs(threshold)`. Check `band > 0 and abs(measured - threshold) <= band` first (borderline), then met or missed by direction."
  - "In `poc_readout`, the decision checks run in order on the must-have rows only: any missed means no-go; else any not_measured means incomplete; else any borderline means conditional; else go."
  - "`watch` is every borderline row (must-have or not) plus nice-to-have rows that are missed or not_measured, in criteria order. `unscored` is `sorted(m for m in results if m not in the criteria's metric names)`."
---

Grace Liu, the Principal architect who coaches this track (a fictional character), forwards you a spreadsheet and a calendar invite.

"Thornbury Mutual's claims-intake POC reads out on Thursday. Ruth Okafor, their VP of Claims Operations, is the decision owner. We agreed six success criteria with her at kickoff, with baselines, and three are must-haves. Week 6 numbers are in. Half the room thinks it's a clear win because the demo survey came back at 9.1 out of 10. I don't want anyone arguing from vibes on Thursday. Build me a scorecard that applies the rules we agreed: met, missed, borderline or not measured for each criterion, and go, conditional, no-go or incomplete overall. And it should refuse to score anything nobody agreed to up front."

Thornbury Mutual and Ruth Okafor are fictional. `CRITERIA` (the six agreed criteria) and `RESULTS` (the week 6 measurements) are loaded for you.

## The data

Each criterion is a dictionary:

```python
{"metric": "field_accuracy", "threshold": 0.95, "direction": "higher", "must_have": True,
 "baseline": 0.93, "how": "Share of 14 key fields correct on the 400-claim frozen test set, ..."}
```

`direction` is `"higher"` (the measurement must be at least the threshold) or `"lower"` (at most). A criterion may also carry its own `"margin"`. `RESULTS` maps metric names to measured numbers. A metric can be missing from `RESULTS`, or present with a value that isn't a number (`None`, `"TBD"`).

## Your task

**1. `validate_criteria(criteria)`** returns a list of problem strings, empty when the criteria are usable. For each criterion, in order, with `name` being its metric (or `f"criterion {i+1}"`, 1-based, when the metric is missing or empty):

- `"criterion 2: missing metric name"` when the metric is missing or empty, otherwise `"accuracy: duplicate metric"` when the name was already used.
- `"<name>: direction must be 'higher' or 'lower'"`
- `"<name>: threshold must be a number"` (an `int` or `float`; `True` and `False` don't count)
- `"<name>: no baseline agreed"` when `baseline` is missing or `None`

After the loop, add `"no must-have criterion"` if no criterion has a truthy `must_have`. A plan with no must-have can never produce a no-go, which means it can't produce a real decision either.

**2. `evaluate_criterion(criterion, results, margin=0.02)`** returns one row:

```python
{"metric": "field_accuracy", "status": "borderline", "measured": 0.948, "threshold": 0.95,
 "direction": "higher", "must_have": True, "vs_baseline": 0.018}
```

- If the measurement is missing or not a number, `status` is `"not_measured"` and `measured` and `vs_baseline` are `None`.
- Otherwise `vs_baseline` is `round(measured - baseline, 4)` (or `None` if the baseline isn't a number).
- The **borderline band** is `m * abs(threshold)`, where `m` is the criterion's own `"margin"` if it has one, else the `margin` argument. If the band is above zero and `abs(measured - threshold) <= band`, the status is `"borderline"`, on either side of the line. A result that just scrapes over is as uncertain as one that just misses.
- Otherwise `"met"` or `"missed"` by direction. A threshold of 0 has no band, so a zero-tolerance criterion is never borderline.
- `must_have` is a real `bool`.

**3. `poc_readout(criteria, results, margin=0.02)`** returns:

```python
{"decision": "conditional", "rows": [...], "blocking": [], "watch": [...], "unscored": ["demo_feedback_score"]}
```

- `rows`: one `evaluate_criterion` row per criterion, in order.
- `decision`, using must-have rows only, checked in this order: any `missed` means `"no-go"`; else any `not_measured` means `"incomplete"`; else any `borderline` means `"conditional"`; else `"go"`. Nice-to-haves never change the decision.
- `blocking`: must-have metrics that are `missed` or `not_measured`, in criteria order.
- `watch`: every `borderline` metric, plus nice-to-have metrics that are `missed` or `not_measured`, in criteria order.
- `unscored`: metrics in `results` that aren't in the criteria, sorted. They're reported so nobody can say they were hidden, but they're never scored.

## Example

```python
>>> c = {"metric": "acc", "threshold": 0.90, "direction": "higher", "must_have": True, "baseline": 0.85}
>>> evaluate_criterion(c, {"acc": 0.89})["status"]
'borderline'
>>> evaluate_criterion(c, {"acc": 0.87})["status"]
'missed'
>>> evaluate_criterion(c, {})["status"]
'not_measured'
```

The band around 0.90 is 0.02 × 0.90 = 0.018, so 0.89 is borderline and 0.87 is a miss.

Press **Run** to see Thornbury's scorecard, then **Submit**. Before you move on, write the one sentence you'd open Thursday's readout with. It should state the decision, the borderline must-have and what you'd do about it, and it shouldn't mention the 9.1.
