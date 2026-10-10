---
title: Data Models That Survive Level 4
type: reading
minutes: 15
---

> **By the end of this lesson** you'll have six small patterns that make progressive problems easier to extend: records plus a change log, one "bring state up to date" helper, tuple sort keys, formatting helpers, dataclasses used where they help, and a habit of reading the spec for its edge words.

## Why the model matters more than the code

In a progressive screen, Level 1 is rarely hard. What costs time is Level 3 or 4 asking a question your Level 1 structure can't answer: "what was the balance at time 40?", "expire this record after 30 seconds", "rank by total, then by who got there first". If the answer lives nowhere in your state, you rewrite. If it is already there, you add one method.

Candidates describe the best-known variants of Anthropic's online assessment as an in-memory database and a banking system (Reported). This lesson doesn't reconstruct either. The patterns below are general: they apply to any problem with entities, a clock and rankings, which covers most of what these screens look like.

## Pattern 1: a dict of records plus an append-only change log

Keep the **current state** in a dict keyed by id, and keep **every change** in a list you only append to.

```python
class Store:
    def __init__(self):
        self.records = {}   # id -> current record (a dict or a dataclass)
        self.log = []       # (timestamp, id, field, new_value), append only

    def set(self, ts, rid, field, value):
        self.records.setdefault(rid, {})[field] = value
        self.log.append((ts, rid, field, value))
```

The dict answers "what is it now?" in one lookup. The log answers "what was it then?" and "what happened between t1 and t2?" with a scan. You almost never need anything cleverer in a 90-minute screen. A scan over a few thousand entries is instant, and the checks are about correctness, not speed.

Two rules keep the log useful:

- **Never edit or delete log entries.** Deletes and rollbacks are new entries. A deleted record can be logged with a value of `None`.
- **Log the time a change took effect**, not the time your code noticed it. This matters for scheduled events (Pattern 2).

To answer "value as of time `at`", walk the log for that id and keep the last entry with `t <= at`:

```python
def value_at(self, rid, field, at):
    result = None
    for t, r, f, v in self.log:
        if t > at:
            break           # safe only if the log is in time order (see below)
        if r == rid and f == field:
            result = v
    return result
```

That `break` assumes the log is sorted by time. "Timestamps only increase" doesn't guarantee it on its own, because scheduled changes are logged at their scheduled time, which is earlier than the call that applies them. The log stays sorted only if `_advance` (Pattern 2) runs at the **top of every public method**, including read-only ones, so every due change is logged before anything at the current timestamp. Skip it in one method and a later call can append an entry dated 10 after one dated 50; `value_at` then stops early and returns a silently wrong answer. The same problem appears if the spec allows scheduling at a time already in the past. If you're unsure, drop the `break` and scan the whole list, or sort before scanning: at screen sizes it costs nothing.

## Pattern 2: one helper that brings state up to date

Time-based rules show up in almost every progressive problem: records that expire, changes scheduled for later, limits that reset. The trap is checking time in some methods and forgetting it in others.

The fix is one private helper, called as the **first line of every public method**:

```python
def _advance(self, ts):
    # 1. apply scheduled events that are due, in order
    due = sorted(e for e in self.pending if e[0] <= ts)
    self.pending = [e for e in self.pending if e[0] > ts]
    for at, seq, rid, value in due:
        self._apply(at, rid, value)   # logged at `at`, not at `ts`

    # 2. drop expired records
    for rid in [r for r, rec in self.records.items() if rec.get("expires") is not None and rec["expires"] <= ts]:
        del self.records[rid]
```

This is **lazy expiry**: nothing runs on a timer. State catches up whenever someone looks at it. It works because the checks can only observe state through your public methods.

Two details decide whether this passes:

- **Order of due events.** Sort by scheduled time, then by creation order. A counter (`seq`) you increment for each new event gives you the tie-break for free.
- **The boundary.** If something "expires after 30 seconds" and was set at `t=10`, is it still there at `t=40`? The spec will say. Write the comparison once, in the helper, so you only get it right or wrong in one place.

An alternative to deleting expired records is to keep them and filter on read (`if rec["expires"] > ts`). Keeping them is better when a later level asks about the past.

## Pattern 3: sort keys as tuples

Rankings in these problems almost always have two or three levels: "by total descending, then by name". Python sorts tuples element by element, so you write the rule once as a key function.

```python
ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
```

- **Descending numbers:** negate them (`-total`).
- **Descending strings:** you can't negate a string. Either sort twice (Python's sort is stable, so sort by the secondary key first, then by the primary key), or restructure so the string part is ascending, which it usually is.
- **"Earliest wins" tie-breaks:** keep the timestamp in the tuple as-is, since smaller is earlier.

```python
# total desc, then the time they reached that total (earliest first), then name
key = lambda u: (-u.total, u.reached_at, u.name)
```

Write the key as one named function if it's used in two places. A ranking rule that drifts between two methods is a classic lost check.

## Pattern 4: formatting helpers

Many checks compare exact strings like `"alice(120)"` or `"key_a(off)"`. A missing parenthesis or an extra space fails the whole check, and the failure message often only shows the first difference.

```python
def fmt(name, value):
    return f"{name}({value})"

def top(items, n):
    return [fmt(name, total) for name, total in items[:n]]
```

Put every output format in a tiny helper the first time you see it. When Level 2 asks for `"name(count)"` and Level 3 asks for the same shape with a different number, you reuse it. Slicing with `[:n]` also handles the "n is larger than the list" case for free; check the spec for what `n <= 0` should return.

## Pattern 5: when a dataclass helps

A plain dict is fine for records with two or three fields. Once a record has five or more fields, or you keep mistyping a key, a dataclass is clearer and catches typos as errors instead of silent new keys.

```python
from dataclasses import dataclass, field

@dataclass
class Account:
    owner: str
    balance: int = 0
    history: list = field(default_factory=list)   # never use a bare [] default
```

Use a dataclass when:

- the record has many fields, or you'll add fields at later levels;
- you want attribute access (`acct.balance`) to read cleanly in sort keys.

Stick with a dict when the record is tiny or the spec hands you dicts already. Don't spend more than a minute deciding; both work.

## Pattern 6: read the spec for its edge words

Most failed checks are a misread sentence, not a bug in logic. Before you code a method, underline the words that change a comparison or a count:

| Spec says | What it means in code |
|---|---|
| "at exactly time `t`", "as of `t`" | include `t`: `<= t` |
| "before `t`" | exclude `t`: `< t` |
| "between `start` and `end`, start inclusive, end exclusive" | `start <= t < end` |
| "in the last `w` seconds", window `(ts - w, ts]` | `ts - w < t <= ts` |
| "distinct users" | count a `set`, not a list |
| "up to `n`" | `[:n]`, and return fewer if there are fewer |
| "return `None`" vs "return `False`" | they are different; checks often use `is` |
| "rejected ... is not recorded" | return early before you mutate anything |

A useful habit: after reading a level, write each method's return cases as a comment before you write its body.

```python
# record(ts, id, amount):
#   unknown id      -> None
#   would overdraw  -> -1, nothing recorded
#   otherwise       -> new balance
```

That comment block is your checklist when a check fails.

## Putting it together

A model that survives Level 4 usually looks like this:

```python
class Service:
    def __init__(self):
        self.items = {}     # id -> record: current state
        self.log = []       # append-only: (ts, id, what, value)
        self.pending = []   # (at, seq, id, ...) scheduled work
        self.seq = 0        # creation-order tie-break and id counter

    def _advance(self, ts):
        ...                 # apply due events, drop or mark expired records
```

Four fields, one helper. Everything else is a method that calls `_advance`, reads or writes `items`, appends to `log`, and formats the result with one helper.

The next lesson is a short warm-up on the details that cost points: ranking ties and window bounds. After that comes a full four-level drill.

> **Key takeaways**
>
> - Keep current state in a dict and every change in an append-only log; history questions then cost one method.
> - Call one "bring state up to date" helper at the top of every public method, and log scheduled changes at their scheduled time.
> - Write rankings as tuple sort keys and outputs through one formatting helper.
> - Use a dataclass when a record grows past a few fields; otherwise a dict is fine.
> - Underline the edge words ("at exactly", "inclusive", "distinct", `None` vs `False`) before you write a method.
