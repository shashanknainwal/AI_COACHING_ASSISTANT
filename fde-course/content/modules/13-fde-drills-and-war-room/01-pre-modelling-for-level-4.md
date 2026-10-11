---
title: "How Strong Candidates Pre-Model for Level 4"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll have a five-minute routine for guessing what Levels 3 and 4 will ask before you can see them, a checklist for a data model that survives them, a way to find the feature interactions hidden checks love, and a minute-by-minute model run of the C3 feature-flag drill.

## Why Level 4 is decided in minute 5

Progressive screens reveal one level at a time (**Reported**, many candidate accounts; see module C3). That makes it tempting to write the simplest thing that passes Level 1. It works until Level 3 adds time and Level 4 adds history, and your Level 1 model has thrown away exactly what they need. Rewriting the core at minute 60 is how candidates run out of clock.

Module C3's lesson 03 gave you the patterns: records plus an append-only log, one catch-up helper, tuple sort keys. This lesson is about **when** you apply them: before you can see the levels that need them. The drills in this module are built to punish a Level 1 model that only answers Level 1, and their hidden checks test how features combine.

## The five-minute routine

Before writing any code, spend about five minutes on these questions. Write the answers as a comment at the top of the file.

1. **What are the nouns?** Each one becomes a record keyed by id: flags, events, accounts, tools, requests. Write the dict names.
2. **What changes over time?** Anything that changes will probably be asked about "as of time T" by Level 4. Give it an append-only list of `(time, change)` now. It costs one line per write.
3. **What could happen later than the call that notices it?** Expiry, schedules, timeouts, retries. If any are plausible, plan one `_catch_up(timestamp)` helper called first in every public method, even if Level 1 doesn't need it yet.
4. **What will need an id or an order?** Counters (`req1`, `sched2`) and sort keys (`(time, seq)`, `(-count, name)`) are cheap to add early and painful to retrofit.
5. **What gets undone?** Delete, revoke, void, rollback, cancel. Decide now whether "undo" removes a record or marks it (marking almost always survives Level 4 better).

You won't guess every level. You don't need to: a model with records, a log and a catch-up helper absorbs most of what the format reportedly asks for (time-based expiry, scheduled changes, history lookups).

## What Level 4 usually asks, and what to have ready

These are patterns in this course's drills and in public descriptions of the format (**Reported**). They're not a list of real questions.

| If Level 4 asks... | You need from Level 1 |
|---|---|
| "What was X at time T?" | An append-only log of `(time, change)` per record, written at the time the change **took effect** |
| "Undo or roll back to time T" | The same log; the undo is a new entry, not an edit of old ones |
| "Who did what, in order?" | An audit list appended on every public call, with the result |
| "Explain why this was allowed" | A function that returns the reasons, not just a yes/no |
| "Replay from position N" | Records that remember their position (seq, key) and their status |

## Find the interactions before the checks do

Hidden checks rarely test one feature alone at Level 4. They test two features meeting. A fast way to find those cells is a small **interaction grid**: write the features down both sides and ask "what happens when these two meet?"

For the webhook drill (lesson 02) the grid looks like this:

| | Duplicate delivery | Out-of-order hold | Gap timeout | Void |
|---|---|---|---|---|
| **Duplicate** | - | redelivering a held event | redelivering a late event | redelivering a voided event |
| **Hold** | | - | which held event starts the clock? | voiding a held event |
| **Timeout** | | | - | balance at a past time across a skip |

Each cell is a test you can write in one minute. You'll find at least one spec question in the grid that you would otherwise have discovered as a failed check at minute 65.

## A model run: the C3 feature-flag drill in 90 minutes

Here's how a strong run of `c3-progressive-coding/02` could go. It's a model written for this course, not a recording of a real candidate. Do that drill first if you haven't: the rest of this section is a spoiler.

**Minutes 0-6: read and model.** Read Level 1 twice. Nouns: flags, users. Changes over time: a flag's state. Write the header comment:

```python
# flags:   name -> {"enabled": bool, "overrides": {user: bool}}
# history: name -> [(time, state)]   state None = deleted   (for "as of" questions)
# pending: [(at, seq, id, name, enabled)]  (in case anything is scheduled)
# every public method starts with self._apply_due(timestamp)
```

Level 1 doesn't mention history or schedules. The candidate adds both anyway, because "flag" plus "timestamp on every call" strongly suggests time travel later.

**Minutes 6-18: Level 1.** Four methods, each starting with `_apply_due` (which does nothing yet) and each writing to `history`. Before submitting, two quick checks by hand: create, delete, create again; and `is_enabled` on a missing flag. Submit. Pass.

**Minutes 18-35: Level 2.** Overrides go in the record that already exists. `list_flags` and `top_overridden` are sort-key questions: `sorted(..., key=lambda f: (-count, name))`. The trap is in the last bullet: deleting a flag deletes its overrides. Because overrides live inside the flag record, `del self.flags[name]` already does it. Two minutes saved by the model.

**Minutes 35-58: Level 3.** Schedules. `_apply_due` gets a body: pop the due entries, sort by `(at, seq)`, apply each, and record each change **at `at`**, not at the current timestamp. Cancel marks an entry as cancelled rather than searching for it later. Before submitting, the candidate fills two cells of the grid: "delete a flag with a pending schedule" and "two schedules due at the same time". Pass on the first submit.

**Minutes 58-80: Level 4.** `state_at` is a scan of `history[name]` for the last entry with `time <= at`. `rollback` reads `state_at(to)` and writes a new change at `timestamp`. About fifteen lines, because the log has existed since minute 6. The interaction cells: rollback while a schedule is pending, and `state_at` across a delete and re-create. Both pass.

**Minutes 80-90: buffer.** Re-read the spec for edge words ("exactly", "already", "or later"), and add a test for each. Done with ten minutes spare.

The run has no clever code. It's fast because nothing written in minutes 0-18 had to be rewritten later. Compare your own last attempt: where did you spend the time you didn't have?

## Pacing for the drills in this module

| Drill | Clock | Target for Level 1 | If you're behind |
|---|---|---|---|
| Webhook ingest | 70 min | 15 min | Skip `balance_at` polish; get `void` right |
| Rate-limited sync | 70 min | 12 min | Make one request helper before Level 2's paging |
| Tool and permission engine | 70 min | 12 min | Build the log replay before roles, not after |
| SSE stream client (AI-allowed) | 45 min | 8 min | Write the split-CRLF check before accepting a parser |
| War room | 30 min | 6 min to stabilise | Ship the override first, investigate second |

Record the minute you clear each level. Your times are the measure of progress, not whether you finished.

> **Key takeaways**
> - Spend the first five minutes on nouns, changes over time, late events, ids and undo. Write the model as a comment.
> - Add the append-only log and the catch-up helper in Level 1, even when Level 1 doesn't need them.
> - Record changes at the time they took effect. Undo is a new entry, never an edit.
> - Draw a small interaction grid and write one test per cell before you submit Levels 3 and 4.
> - A strong run is fast because nothing gets rewritten, not because the code is clever.
