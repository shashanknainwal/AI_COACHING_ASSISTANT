---
title: "Module Quiz: Progressive Coding"
type: quiz
minutes: 10
questions:
  - q: "How do candidates describe the shape of Anthropic's online coding assessment? (Reported)"
    options:
      - "Several unrelated algorithm puzzles in about 45 minutes"
      - "One problem in about four levels, each extending the last"
      - "A take-home project with a full week to finish it"
      - "A whiteboard system design session with no code at all"
    answer: 1
    explain: "Many candidate accounts agree on one progressive problem, about four levels, roughly 90 minutes. It's a candidate report, not an official description; recruiters confirm the format per role."
  - q: "Level 4 asks for a record's value at a past time. Which Level 1 data model makes that a one-method change?"
    options:
      - "A single dict of records that you overwrite on every change"
      - "A list of current records that you re-sort on every call"
      - "A dict of current records plus an append-only change log"
      - "A JSON file on disk that you rewrite after every method call"
    answer: 2
    explain: "The dict answers 'what is it now?'. The append-only log answers 'what was it then?' with a scan. Overwriting throws the past away."
  - q: "A spec has records that expire and changes scheduled for later. Where should the time-based logic live?"
    options:
      - "In one helper called first in every public method"
      - "In a background thread that wakes up once every second"
      - "Only in the read methods, since writes don't care about time"
      - "In each method separately, adapted to what that method needs"
    answer: 0
    explain: "One 'bring state up to date' helper, called first everywhere, means time rules are applied consistently and the boundary comparison lives in one place."
  - q: "A scheduled change for t=50 is noticed by a call at t=70. When should the change be recorded in the history?"
    options:
      - "At t=70, the moment your code noticed and applied it"
      - "At t=50"
      - "Nowhere, because scheduled changes aren't real changes"
      - "At the earlier time when the schedule itself was created"
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
      - "Only if that earlier use was itself rejected by the limit"
      - "No, because 10 is not greater than 20 - 10"
      - "It depends on the max_requests quota that was configured"
    answer: 2
    explain: "The window is ts - window < t <= ts, so 10 < t. A use at exactly ts - window has aged out."
  - q: "A spec says 'return None if the key doesn't exist' and the check uses `is None`. What does returning False do?"
    options:
      - "Passes, because both values are falsy in Python"
      - "Passes only when the tests run under Python 3"
      - "Raises an exception inside the test runner"
      - "Fails the check"
    answer: 3
    explain: "None and False are different values. Checks often use `is`, so read the return type in the spec exactly."
  - q: "Your value_at method breaks out of its scan at the first log entry later than `at`. When is that safe?"
    options:
      - "Only if every public method runs the catch-up helper first, so the log stays in time order"
      - "Always, because the timestamps passed to your methods only ever increase"
      - "Never, because a Python list can't be kept in sorted order"
      - "Only when no record has ever been deleted from the store"
    answer: 0
    explain: "Scheduled changes are logged at their scheduled time, which is earlier than the call that applies them. If one method skips the catch-up helper, an older entry can land after a newer one and the early break returns a wrong answer."
  - q: "Which statement about Anthropic's coding environment is Official, from the company's own careers page?"
    options:
      - "Technical interviews use live coding tools such as Colab and CodeSignal"
      - "The online assessment runs Python 3.8 with partial credit per check"
      - "Every candidate sits exactly four levels in exactly 90 minutes"
      - "Candidates may use an AI assistant if they disclose it afterwards"
    answer: 0
    explain: "The careers page names Colab and CodeSignal and says you can look things up. The four-level, 90-minute shape is Reported, the Python version and scoring details aren't public, and AI help is off unless you're told otherwise."
---

Ten questions on the format, the environment and the patterns from this module. You need 8 of 10 to pass.
