---
title: "Exercise: Ranking and Formatting Warm-Up"
type: exercise
minutes: 20
hints:
  - "Build two dicts in one pass over the events: `totals[user]` and `reached[user]`. Use `dict.get(user, 0)` so the first event for a user doesn't need a special case."
  - "A user reaches their final total at their latest event. Events can arrive in any order, so keep the `max` of the timestamps rather than the last one you saw."
  - "`sorted(totals, key=lambda u: (-totals[u], reached[u], u))` ranks by total descending, then earliest reach time, then name."
  - "Handle `n <= 0` by returning `[]` before you do any work. For `n` larger than the number of users, slicing with `[:n]` already does the right thing."
  - "For the window, the whole rule is one comparison: `start <= e[\"t\"] < end`. Only users with at least one event inside the window appear in the result."
---

Your coach, Nadia Okafor, has watched a lot of people take progressive coding screens. Her observation: most lost points aren't hard logic. They're a tie-break done in the wrong order, a bound that should have been inclusive, or `None` where an empty list was expected. Before you sit a full four-level drill, she wants you to do a 20-minute warm-up that pins those details one at a time.

Each check below tests exactly one detail. When one fails, read its message, then reread the matching sentence of the spec. That's the habit you want on the day.

## The data

Each event is a dict. Points are always positive integers, and timestamps are integers. The list is **not** guaranteed to be in time order.

```python
{"user": "maya", "points": 30, "t": 4}
```

## Your task

Write two functions in the editor. Don't modify the input list or its dicts.

**1. `leaderboard(events, n)`** returns up to `n` entries formatted as `"name(total)"`, where `total` is the sum of that user's points.

Rank users by:

1. **total**, highest first;
2. then by the **time they reached that total**, earliest first. Because points are positive, a user reaches their final total at their **latest** event;
3. then by **name**, alphabetically.

If `n` is larger than the number of users, return them all. If `n` is `0` or less, return `[]`. With no events, return `[]`.

**2. `window_totals(events, start, end)`** returns a dict `{user: total}` that only counts events with `start <= t < end`: **start inclusive, end exclusive.** Leave out users with no events in the window. With no matching events, return `{}`.

## Example

```python
events = [
    {"user": "maya", "points": 30, "t": 1},
    {"user": "leo",  "points": 50, "t": 2},
    {"user": "maya", "points": 20, "t": 4},
    {"user": "ana",  "points": 50, "t": 5},
    {"user": "leo",  "points": 10, "t": 9},
]

leaderboard(events, 3)
# -> ["leo(60)", "maya(50)", "ana(50)"]
#    maya and ana both have 50; maya reached it at t=4, ana at t=5

window_totals(events, 2, 5)
# -> {"leo": 50, "maya": 20}   (t=5 is the end, so ana's event is excluded)
```

Press **Run** to try the sample at the bottom of the file, then **Submit** to grade it.

> **Coach's note:** The formatting helper and the sort key you write here are the same two lines you'll need in the drill that follows. Write them as small named pieces now, so you can reuse them under the clock.
