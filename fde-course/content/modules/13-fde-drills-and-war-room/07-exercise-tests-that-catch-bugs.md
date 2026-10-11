---
title: "Exercise: Write Tests That Catch Bugs"
type: exercise
minutes: 30
hints:
  - "Read plan_batches line by line and list every decision it makes: duplicates, oversized records, the record limit, the byte limit, the final batch, order. Each decision is a place a bug can hide, and each needs a check."
  - "Boundaries catch the most bugs. Use sizes that add up to exactly max_bytes, a batch of exactly max_records, and a record of exactly max_bytes."
  - "Assert the whole result, not just its type or length. `assert out == {...}` catches mistakes that `assert len(out['batches']) == 2` lets through."
  - "For duplicates, put the repeated id after a different id, then check both which copy was kept and where it sits in the batch."
---

Marram's bulk-upload code has broken three times this quarter, each time in a "small refactor" that passed every test. Petra Havel (fictional) asks you for tests that would actually have caught them. "I don't want more tests. I want tests that fail when the code is wrong."

This is how you'll be graded here too. Your checks run against the correct `plan_batches` (they must all pass) and against nine hidden versions, each with one realistic bug (each must be caught by at least one of your checks). This is **mutation testing**: a test suite is only as good as the bugs it kills.

## The function under test

`plan_batches(records, max_records, max_bytes)` is already loaded (its code is in the setup file; read it). It splits records for a bulk API:

- `records` is a list of `{"id": str, "size": int}` in the order they must be sent. The result keeps that order.
- If an id appears more than once, only its first occurrence counts. Later copies are ignored.
- A record with `size` greater than `max_bytes` is never sent. Its id goes in `"oversized"`, in order.
- Records fill a batch until adding the next one would make it hold more than `max_records` records or more than `max_bytes` bytes in total. Then a new batch starts. A batch whose sizes add up to exactly `max_bytes` is fine.
- It returns `{"batches": [[id, ...], ...], "oversized": [id, ...]}`. No records means no batches.

## Your task

Write at least three functions named `check_...`. Each takes the function under test as its only argument and uses `assert`:

```python
def check_record_limit(plan_batches):
    out = plan_batches([{"id": "a", "size": 1}, {"id": "b", "size": 1}, {"id": "c", "size": 1}], 2, 100)
    assert out["batches"] == [["a", "b"], ["c"]], out
```

- Press **Run** to try your checks against the real function.
- Press **Submit** to run them against the correct version and the nine hidden broken ones. Each failing line tells you what kind of bug got through, but not how to catch it.
- Name them `check_`, not `test_`. The grader collects `test_` functions itself.

## Why this matters in the job

At a customer site you'll often add a feature to code you didn't write, with tests you don't trust. The fastest way to earn trust in a suite is to break the code on purpose and see whether anything goes red. Interviewers who ask you to "write tests for this" are looking for the same thing: boundaries, duplicates, empty input, order, and whole-result assertions.
