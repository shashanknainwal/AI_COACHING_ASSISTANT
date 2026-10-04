---
title: "Exercise: Prioritize a Customer Backlog"
type: exercise
minutes: 20
hints:
  - "For `score`, check `request[\"blocked\"]` first and return 0 before doing any math."
  - "Use `round(value, 2)` to round to two decimal places."
  - "`sorted(items, key=lambda r: (-score(r), r[\"effort\"], r[\"id\"]))` sorts by score descending, then effort ascending, then id."
  - "In `plan_sprint`, keep a `remaining` counter. Loop over the ranked requests; if `request[\"effort\"] <= remaining`, take it and subtract. Otherwise skip it and keep looping, because a smaller item further down may still fit."
  - "Requests with a score of 0 (blocked) should never be planned, even if there is capacity left."
---

It's week two at **Brightline Health**, a mid-size clinic network piloting your company's AI document-processing product. You've collected a backlog of requests from five different stakeholders. Everyone says theirs is urgent. You have **10 engineering days** before the next steering-committee meeting.

You need a defensible, explainable way to decide what to work on. A simple scoring model is a great FDE tool: it turns a political argument ("my request matters most") into a transparent conversation ("let's agree on the impact score").

## The scoring model

Each request is a dictionary:

```python
{
    "id": "BH-3",
    "title": "Auto-extract insurance member IDs",
    "impact": 5,     # 1-5: how much it moves the agreed success metric
    "urgency": 4,    # 1-5: cost of waiting
    "effort": 3,     # engineering days, 1 or more
    "blocked": False # True if we're waiting on the customer (data access, approvals, ...)
}
```

The priority score is:

```
score = impact × urgency ÷ effort
```

rounded to 2 decimal places. A **blocked** request scores `0`, because you can't make progress on it no matter how important it is. (Unblocking it is a separate action item for the customer.)

## Your task

Write two functions in the editor.

**1. `score(request)`** returns the priority score as a float, following the rules above.

**2. `plan_sprint(requests, capacity)`** returns a list of request **ids** to work on, in priority order:

1. Rank requests by score, highest first. Break ties by **lower effort first**, then by **id** alphabetically.
2. Walk down the ranked list. If a request's effort fits in the remaining capacity, include it and subtract its effort. If it doesn't fit, **skip it and keep going**, since a smaller request further down may still fit.
3. Never include a request with a score of `0`.
4. Don't modify the input list.

## Example

```python
backlog = [
    {"id": "A", "title": "...", "impact": 4, "urgency": 5, "effort": 4, "blocked": False},  # 5.0
    {"id": "B", "title": "...", "impact": 3, "urgency": 3, "effort": 1, "blocked": False},  # 9.0
    {"id": "C", "title": "...", "impact": 5, "urgency": 5, "effort": 8, "blocked": False},  # 3.12
]
plan_sprint(backlog, capacity=6)  # -> ["B", "A"]  (C needs 8 days; only 1 left)
```

Press **Run** to try your code with the sample backlog at the bottom of the file, then **Submit** to grade it.

> **FDE tip:** In a real engagement, share the scored table with the customer's sponsor *before* you start the work. Disagreements about scores are cheap to fix on Monday and expensive to fix after you've built the wrong thing.
