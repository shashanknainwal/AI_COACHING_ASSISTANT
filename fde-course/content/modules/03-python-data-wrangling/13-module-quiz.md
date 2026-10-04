---
title: "Module 3 Quiz"
type: quiz
minutes: 10
questions:
  - q: "In the kickoff, the customer says \"the data is clean.\" What's the right response?"
    options:
      - "Trust it and start building the AI features"
      - "Thank them, then profile the data before relying on it"
      - "Tell them it's probably not clean"
      - "Ask them to clean it again before you start"
    answer: 1
    explain: "Treat it as a hypothesis you test. Messy data is the normal case, and profiling takes an hour."
  - q: "A \"status\" field meant \"won\" until 2023 and \"won or lost\" after. What kind of mess is this, and how do you find it?"
    options:
      - "Missing values; count blanks"
      - "Duplicates; run entity resolution"
      - "Semantic drift; ask the data owner whether the field's meaning ever changed"
      - "Wrong types; parse it as a number"
    answer: 2
    explain: "Semantic drift can't be detected from values alone. You find it by asking people."
  - q: "Why read a CSV with csv.DictReader (or pandas with dtype=str) at first?"
    options:
      - "It's faster"
      - "Everything stays text, so nothing gets silently converted before you've looked at it"
      - "It automatically fixes dates"
      - "It removes duplicates"
    answer: 1
    explain: "Automatic type guessing can hide problems, like turning \"NA\" into missing or dropping leading zeros."
  - q: "A date column contains 03/04/2026. What should your parser do?"
    options:
      - "Guess month-first, since that's most common"
      - "Use whichever format parses without an error"
      - "Confirm with the customer which systems use which format, and check whether any value has a first number above 12"
      - "Drop the column"
    answer: 2
    explain: "Ambiguous dates parse fine either way, so errors won't warn you. Confirm the convention."
  - q: "What does \"(1,204.50)\" mean in an accounting export?"
    options:
      - "1204.50"
      - "-1204.50"
      - "An estimate"
      - "A missing value"
    answer: 1
    explain: "Parentheses are accounting notation for negative numbers, such as refunds."
  - q: "Your cleaning code finds 40 rows with unreadable dates. What should it do with them?"
    options:
      - "Drop them silently so the output is clean"
      - "Replace the dates with today's date"
      - "Put them in a reject list with the reason, and report them to the customer"
      - "Crash the whole job"
    answer: 2
    explain: "Never silently drop data. Rejects with reasons are a deliverable and often reveal a systemic problem."
  - q: "You join orders to accounts and total revenue goes up by 8%. What's the most likely cause?"
    options:
      - "Revenue really increased"
      - "Duplicate keys on the accounts side caused a fan-out, counting some orders twice"
      - "Floating-point rounding"
      - "The inner join dropped rows"
    answer: 1
    explain: "Duplicate keys multiply rows silently. Check uniqueness before joining and fail loudly if it's violated."
  - q: "CRM says plan = Pro, billing says plan = Basic. How should you decide which is right?"
    options:
      - "The CRM always wins"
      - "Pick whichever looks more recent"
      - "Use the source of truth agreed with the customer for that field (often billing for plan and amount)"
      - "Average them"
    answer: 2
    explain: "Agree field-level ownership with the customer once, then apply it consistently."
  - q: "Two accounts both have contacts with @gmail.com addresses. Are they likely duplicates?"
    options:
      - "Yes, same domain"
      - "No, a free email domain isn't evidence of the same company"
      - "Only if their names are also identical"
      - "Yes, if they're in the same city"
    answer: 1
    explain: "Exclude free email providers from domain matching."
  - q: "For merging duplicate customer records, which mistake is usually worse?"
    options:
      - "Missing a real duplicate (false negative)"
      - "Merging two different companies (false positive)"
      - "They're equally bad"
      - "Neither matters if you have backups"
    answer: 1
    explain: "A false merge corrupts data and is hard to undo. Choose thresholds from labeled examples, with a review queue."
  - q: "Which task is the best fit for Claude rather than deterministic code?"
    options:
      - "Converting dates from MM/DD/YYYY to ISO"
      - "Summing invoice totals"
      - "Categorizing free-text support tickets"
      - "Joining two tables on account ID"
    answer: 2
    explain: "If you can write the rule, write the rule. Use Claude where language judgment is needed."
  - q: "You send 20 tickets per request to Claude. How should you match answers back to tickets?"
    options:
      - "By position: the first answer is the first ticket"
      - "By a stable index that you send with each ticket and Claude echoes back"
      - "By matching the ticket text"
      - "Send one ticket per request instead"
    answer: 1
    explain: "Models occasionally skip or reorder items; matching by position silently shifts every label after a skip."
  - q: "An email-format rule counts missing emails as invalid, and a separate rule counts them as missing. What's the problem?"
    options:
      - "Nothing, it's more thorough"
      - "Missing emails are double-counted, overstating the problem; validity rules should only check present values"
      - "The regex is too strict"
      - "Completeness can't be measured"
    answer: 1
    explain: "Keep completeness and validity separate so each problem is counted once."
---

Thirteen questions on profiling, normalization, reconciliation, entity resolution, LLM data jobs, and data-quality reporting. You need **11 out of 13** to pass. You can retry as many times as you like.
