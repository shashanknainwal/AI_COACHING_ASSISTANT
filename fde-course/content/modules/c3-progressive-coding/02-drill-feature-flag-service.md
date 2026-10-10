---
title: "Drill: A Feature-Flag Service"
type: drill
minutes: 90
timeLimit: 90
levels:
  - "Flags"
  - "Overrides and listing"
  - "Scheduled changes"
  - "History and rollback"
hints:
  - "Before Level 1, decide where a flag's state lives and where its history will live. Level 4 asks what the flag was at any past time, so a list of (time, state) changes per flag is cheap to keep from the start."
  - "Scheduled changes (Level 3) are easiest if every public method begins with the same helper call that applies everything due at the current timestamp."
  - "Sort due schedules by (time, creation order). A tuple like (at, seq, id, name, enabled) sorts correctly on its own."
  - "Record a scheduled change in the history at its scheduled time, not at the timestamp of the call that noticed it."
---

This drill is an original problem in the same format as the coding screens candidates describe: one class, four levels, a clock. Each level adds requirements that you can't see yet, so **the data model you pick in Level 1 decides how painful Level 4 is.**

## The rules

- Implement a class called `FlagService` in the editor. Every method takes `timestamp` (an integer) as its first argument, and timestamps only ever increase from one call to the next.
- Press **Submit** to run the checks for the levels you can see. When every check for a level passes, the next level opens below.
- The clock is a target, not a wall. If time runs out, keep going: finishing late is still practice.
- Hints and the AI tutor are off while the clock runs, the same as a real assessment.

## Level 1: Flags

A flag is a named on/off switch.

- `create_flag(timestamp, name, default)`: create a flag whose state is `default` (`True` or `False`). Return `True`, or `False` if a flag with that name already exists (leave it unchanged).
- `set_flag(timestamp, name, enabled)`: set the flag's state. Return `True`, or `False` if the flag doesn't exist.
- `is_enabled(timestamp, name, user_id)`: return the flag's state for this user, or `None` if the flag doesn't exist. (Until Level 2, every user sees the same state.)
- `delete_flag(timestamp, name)`: delete the flag. Return `True`, or `False` if it doesn't exist. A deleted name can be created again.

## Level 2: Overrides and listing

Support teams want to turn a flag on for one customer without touching anyone else.

- `set_override(timestamp, name, user_id, enabled)`: from now on, `is_enabled` returns `enabled` for this user, whatever the flag's own state. A later override for the same user replaces the earlier one. Return `True`, or `False` if the flag doesn't exist.
- `list_flags(timestamp, prefix)`: return the flags whose names start with `prefix`, sorted by name, each formatted as `"name(on)"` or `"name(off)"` using the flag's own state. An empty prefix lists every flag.
- `top_overridden(timestamp, n)`: return up to `n` flags ranked by how many distinct users have an override, highest first, ties broken by name. Format each as `"name(count)"`. Leave out flags with no overrides.
- Deleting a flag deletes its overrides too. A flag created again with the same name starts with none.

## Level 3: Scheduled changes

Launches happen at 9am whether or not anyone is awake.

- `schedule(timestamp, name, at, enabled)`: at time `at`, set the flag's state to `enabled`. Return an id: `"sched1"`, `"sched2"`, and so on, counting across all flags. Return `None` if the flag doesn't exist.
- A scheduled change takes effect at its time: any call with `timestamp >= at` must see it. When several are due, apply them in order of `at`, then in the order they were scheduled.
- `cancel_schedule(timestamp, schedule_id)`: cancel a pending change. Return `True`, or `False` if the id is unknown, already cancelled, or already applied.
- Deleting a flag drops its pending schedules.

## Level 4: History and rollback

An incident review asks: "what was this flag at 2:14am, and can we put it back?"

- `state_at(timestamp, name, at)`: return the flag's own state (ignoring overrides) as of time `at`, or `None` if the flag didn't exist then. A change made at exactly `at` counts. A scheduled change happened at its scheduled time. `at` may be later than `timestamp`: then answer with what has happened up to `timestamp`. A change that is still pending doesn't count until it has been applied.
- `rollback(timestamp, name, to)`: set the flag to the state it had at time `to`. The rollback is a new change recorded at `timestamp`; earlier history stays as it was. Return `True`, or `False` if the flag doesn't exist now or didn't exist at `to`.
