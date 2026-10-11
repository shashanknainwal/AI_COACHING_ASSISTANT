---
title: "Drill: The Frozen-Test Protocol"
type: drill
minutes: 45
timeLimit: 45
levels:
  - "Split and fingerprint"
  - "Score without peeking"
  - "Hill-climb with a held-out check"
  - "One look at the test set"
hints:
  - "Level 1: `int(hashlib.sha256(cid.encode()).hexdigest(), 16) % 100` gives the bucket. Recompute the split from `self.case_ids` every time you need it, so Level 4's `add_cases` just works."
  - "Freeze the test fingerprint in `__init__`, before anything else can change the case list. Level 4 compares against it."
  - "Level 2: keep one private helper that computes a rate for any split, and make the public `score` refuse `\"test\"` before calling it. Level 4's `final_test` can then use the helper directly."
  - "Level 3: round both gains to 3 decimals before you compare them with the thresholds, and only move `self.best` on an accept."
  - "Level 4: check 'already used' before 'changed', and record which variant used the test split so the error message can name it."
---

This drill is an original problem in the progressive format from module C3 (Reported as a common screen shape): one class, four levels, a clock. The topic is the one interviewers probe when you say "we improved the prompt from 73% to 89%": how do you know you didn't tune to the test?

Teodora Kessler at Gannet Home Energy (fictional) has watched it happen. "Someone pasted every dev-set failure into the prompt as a few-shot example and the dev score jumped 27 points. I want a lab that makes that impossible to ship: a stable split, a validation check on every change, and a test split that gets read exactly once."

`CASE_IDS` (100 golden cases) and `RESULTS` (per-case pass or fail for three prompt variants) are loaded for you.

## The rules

- Implement the class `EvalLab` in the editor. Press **Submit** to run the checks for the levels you can see. When a level passes, the next one opens.
- The clock is a target, not a wall. Hints and the tutor are off while it runs.

## Level 1: Split and fingerprint

- `EvalLab(case_ids)` stores the ids.
- `split()` returns `{"dev": [...], "val": [...], "test": [...]}`. A case's bucket is `int(sha256(id).hexdigest(), 16) % 100` (UTF-8 bytes). Buckets below 60 go to dev, below 80 to val, the rest to test. Sort the ids in each split.
- `fingerprint(name)` returns the first 12 hex digits of the SHA-256 of that split's sorted ids joined with `"\n"`.

Why hash and not shuffle: a hash split never moves an existing case when you add new ones, and anyone can recompute it.

## Level 2: Score without peeking

- `record(variant, results)` stores a `{case_id: bool}` dict for a variant and returns how many results it stored. The first variant recorded becomes `best`.
- `score(variant, name)` returns the pass rate, rounded to 3 decimals, over the split's cases that have a result. It returns `None` for an unknown variant or a split with no results.
- `score(variant, "test")` raises `PermissionError`. Only Level 4 may read the test split.

## Level 3: Hill-climb with a held-out check

- `propose(variant, parent, min_gain=0.02)` computes `dev_gain` and `val_gain` (variant minus parent, each rounded to 3 decimals) and decides:

| Condition | Decision |
|---|---|
| `dev_gain >= min_gain` and `val_gain >= 0` | `"accept"`, and `best` becomes the variant |
| `dev_gain >= min_gain` and `val_gain < 0` | `"overfit"` |
| otherwise | `"reject"` |

  It returns `{"variant", "parent", "dev_gain", "val_gain", "decision"}` and appends that dict to the history.
- `history()` returns a copy of the list of proposals so far.

## Level 4: One look at the test set

- In `__init__`, freeze the test split's fingerprint.
- `add_cases(ids)` appends new case ids.
- `final_test(variant)` returns `{"variant", "test", "dev", "gap"}`, where `gap` is `dev - test` rounded to 3 decimals. Before that, it checks two things in order:
  - If the test split was already used, return `{"error": "test split already used for <variant>"}`.
  - If the test fingerprint no longer matches the frozen one, return `{"error": "test split changed since it was frozen"}`.
- `saturated(variant, ceiling=0.95)` is `True` when both the dev and val scores are at least the ceiling.

## After the clock

Press **Run**. The pasted-examples prompt gains 27 points on dev and loses 11 on validation, so the lab flags it as overfit. The read-back rule gains on both and gets the single test run. For the record, the pasted-examples prompt scores 59% on the test split against the baseline's 88%. You never needed to look, which is the point.

Three things to say in an interview:

- **The validation split is what you climb against; the test split is for the final report.** Every look at the test split leaks a little of it into your decisions.
- **The test split is small (17 cases here), so its number is noisy.** A negative gap is noise, not proof that the prompt generalizes better than it fits. Report the interval.
- **When dev and val are both above about 95%, the suite is saturated.** More climbing measures noise. Add harder cases from production failures and freeze a new version.
