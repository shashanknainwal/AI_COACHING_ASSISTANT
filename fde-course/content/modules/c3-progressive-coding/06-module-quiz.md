---
title: "Module Quiz: Progressive Coding"
type: quiz
minutes: 8
questions:
  - q: "How do candidates describe the shape of Anthropic's online coding assessment? (Reported)"
    options:
      - "Several unrelated algorithm puzzles, 45 minutes"
      - "One problem in about four levels, roughly 90 minutes, where each level extends the last"
      - "A take-home project with a week to finish"
      - "A whiteboard system design with no code"
    answer: 1
    explain: "Many candidate accounts agree on one progressive problem, about four levels, roughly 90 minutes. It's a candidate report, not an official description; recruiters confirm the format per role."
  - q: "Level 4 asks for a record's value at a past time. Which Level 1 data model makes that a one-method change?"
    options:
      - "A single dict that you overwrite on every change"
      - "A list of current records that you re-sort on every call"
      - "A dict of current records plus an append-only log of (time, id, value) changes"
      - "A database connection string"
    answer: 2
    explain: "The dict answers 'what is it now?'. The append-only log answers 'what was it then?' with a scan. Overwriting throws the past away."
  - q: "A spec has records that expire and changes scheduled for later. Where should the time-based logic live?"
    options:
      - "In one private helper called at the start of every public method"
      - "In a background thread that wakes up every second"
      - "Only in the read methods, since writes don't care about time"
      - "In each method separately, written slightly differently as needed"
    answer: 0
    explain: "One 'bring state up to date' helper, called first everywhere, means time rules are applied consistently and the boundary comparison lives in one place."
  - q: "A scheduled change for t=50 is noticed by a call at t=70. When should the change be recorded in the history?"
    options:
      - "At t=70, when your code noticed it"
      - "At t=50, when it was scheduled to take effect"
      - "It shouldn't be recorded at all"
      - "At the time the schedule was created"
    answer: 1
    explain: "Log the time a change took effect, not the time your code happened to apply it. Otherwise 'state at t=60' gives the wrong answer."
  - q: "Rank users by total descending, then by name ascending. Which sort key does that in one call?"
    options:
      - "key=lambda u: (total[u], u), reverse=True"
      - "key=lambda u: (u, -total[u])"
      - "key=lambda u: total[u]"
      - "key=lambda u: (-total[u], u)"
    answer: 3
    explain: "Negating the number makes it descending while the name stays ascending. reverse=True would flip the name order too."
  - q: "The spec says to count events 'with start inclusive, end exclusive'. Which comparison is right?"
    options:
      - "start < t <= end"
      - "start <= t < end"
      - "start <= t <= end"
      - "start < t < end"
    answer: 1
    explain: "Inclusive means the bound itself counts (<=); exclusive means it doesn't (<)."
  - q: "A rate limit allows max_requests uses in the window (ts - window, ts]. With window=10, a use at t=10 and a new call at ts=20: does the old use count?"
    options:
      - "Yes, because 10 is within 10 units of 20"
      - "Only if the old use was rejected"
      - "No, because the lower bound is exclusive and 10 is not greater than 20 - 10"
      - "It depends on the quota"
    answer: 2
    explain: "The window is ts - window < t <= ts, so 10 < t. A use at exactly ts - window has aged out."
  - q: "A spec says 'return None if the key doesn't exist' and the check uses `is None`. What does returning False do?"
    options:
      - "Passes, because both are falsy"
      - "Passes only in Python 3"
      - "Raises an exception in the test"
      - "Fails the check, because False is not None"
    answer: 3
    explain: "None and False are different values. Checks often use `is`, so read the return type in the spec exactly."
---

Eight questions on the format and the patterns from this module. You need 7 of 8 to pass.
