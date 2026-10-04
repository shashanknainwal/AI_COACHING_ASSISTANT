---
title: "Module 5 Quiz"
type: quiz
minutes: 10
questions:
  - q: "You get read access to a customer database you've never seen. What do you do first?"
    options:
      - "Write the query the executive asked for"
      - "Look at the schema, row counts, and sample rows"
      - "Build a dashboard"
      - "Ask for write access"
    answer: 1
    explain: "Schema, counts, and real rows first. Docs and assumptions are often wrong."
  - q: "WHERE end_date = NULL returns no rows even though some end dates are empty. Why?"
    options:
      - "The column has no index"
      - "NULL = NULL is unknown, not true; use IS NULL"
      - "SQLite doesn't support NULL"
      - "You need to cast end_date"
    answer: 1
    explain: "NULL means unknown, so equality comparisons with it are never true. Use IS NULL / IS NOT NULL."
  - q: "What's the difference between WHERE and HAVING?"
    options:
      - "They're interchangeable"
      - "WHERE filters rows before grouping; HAVING filters groups after aggregation"
      - "HAVING is faster"
      - "WHERE only works on numbers"
    answer: 1
    explain: "Use HAVING for conditions on aggregates like COUNT(*) < 200."
  - q: "How do you find members who have never visited?"
    options:
      - "INNER JOIN visits and filter visits.id IS NULL"
      - "LEFT JOIN visits and keep rows where visits.id IS NULL"
      - "COUNT(*) = 0 in WHERE"
      - "SELECT DISTINCT member_id FROM visits"
    answer: 1
    explain: "The anti-join: LEFT JOIN keeps every member, and unmatched members have NULLs on the visits side."
  - q: "A query joins payments and visits on member_id and sums payments. Revenue comes out 9x too high. Why?"
    options:
      - "Rounding errors"
      - "Fan-out: each payment row repeats once per visit by the same member"
      - "Missing ORDER BY"
      - "The payments table has duplicates"
    answer: 1
    explain: "Joining two fact tables at different grains multiplies rows. Aggregate each separately, then join."
  - q: "You need each member's first visit AND the location of that visit. What's the best tool?"
    options:
      - "MIN(visited_at) with GROUP BY member_id"
      - "ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY visited_at), keeping row 1"
      - "DISTINCT member_id"
      - "ORDER BY visited_at LIMIT 1"
    answer: 1
    explain: "MIN gives the date but not the other columns of that row. ROW_NUMBER keeps the whole row."
  - q: "In a month-over-month query, LAG(revenue) returns NULL for the first month. What should pct_change show there?"
    options:
      - "0%"
      - "100%"
      - "NULL: there's no previous month to compare against"
      - "An error"
    answer: 2
    explain: "No previous value means no growth to report. NULL is the honest answer."
  - q: "In a cohort retention table, what does reading DOWN a column tell you?"
    options:
      - "How one cohort decays over time"
      - "Whether newer cohorts retain better or worse than older ones at the same age"
      - "Total revenue"
      - "Which cohort is largest"
    answer: 1
    explain: "Across a row is decay for one cohort; down a column compares cohorts at the same age."
  - q: "What is the grain of a view with one row per location per month?"
    options:
      - "Location"
      - "Month"
      - "Location-month"
      - "Visit"
    answer: 2
    explain: "Always state the grain before joining; join tables only at a common grain."
  - q: "Why build a metrics layer of SQL views?"
    options:
      - "Views are faster than tables"
      - "So every dashboard, report and AI feature uses the same metric definitions"
      - "Because raw tables can't be queried"
      - "To save storage"
    answer: 1
    explain: "Define each metric once, so \"your number doesn't match mine\" stops happening."
  - q: "A helper builds f\"SELECT * FROM members WHERE email = '{email}'\". What's wrong?"
    options:
      - "Nothing, if emails are validated"
      - "It's vulnerable to SQL injection; use a ? parameter instead"
      - "It's slow"
      - "Emails should be uppercased"
    answer: 1
    explain: "Input like x' OR '1'='1 rewrites the query. Parameters keep values from being interpreted as SQL."
  - q: "Which is the strongest protection against an accidental write to a customer database?"
    options:
      - "Being careful"
      - "A keyword check in your script"
      - "A read-only database user on a read replica"
      - "Running queries at night"
    answer: 2
    explain: "Layer 1 is access that can't do damage. Code checks are a useful second layer."
  - q: "Your text-to-SQL assistant generates a DELETE for a user's request. What should happen?"
    options:
      - "Run it, since the user asked"
      - "Ask Claude to confirm, then run it"
      - "Refuse it in code before execution, and never run it"
      - "Run it inside a transaction"
    answer: 2
    explain: "Treat generated SQL as untrusted input: only read-only queries pass the guardrails."
---

Thirteen questions on SQL fundamentals, window functions and cohorts, data modeling, safe production access, and text-to-SQL with Claude. You need **11 out of 13** to pass. You can retry as many times as you like.
