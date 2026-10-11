---
title: "Module Quiz: FDE Drills and the War Room"
type: quiz
minutes: 10
questions:
  - q: "A webhook arrives with an event id you've seen before, but a different amount. What should an idempotent inbox do?"
    options:
      - "Apply the new amount, since the latest delivery wins"
      - "Treat it as a conflict, change nothing, and surface it"
      - "Treat it as a duplicate and quietly ignore it"
      - "Apply both amounts so no money is ever lost"
    answer: 1
    explain: "Same id and same payload is a retry. Same id and a different payload means one of the two is wrong, so a person needs to see it. Overwriting or summing hides the problem."
  - q: "An incremental sync uses `updated_at > watermark`. Which record does it miss?"
    options:
      - "A record whose updated_at is far in the future"
      - "A record deleted after the last successful sync"
      - "A record with the watermark's updated_at written later"
      - "A record whose data changed but whose id didn't"
    answer: 2
    explain: "With a strict comparison on time alone, a second record with the same updated_at arriving after the sync is skipped forever. A composite key (updated_at, id) fixes ties; a backfill catches writes that land before the watermark."
  - q: "Level 1 of a drill doesn't mention history. Why add an append-only change log anyway?"
    options:
      - "Later levels often ask what something was at a past time"
      - "Graders award extra marks for any defensive extra code"
      - "Dicts are slow in Python, so a list is faster to scan"
      - "It replaces the need for a catch-up helper at Level 3"
    answer: 0
    explain: "A dict answers 'what is it now'. A log written from the start answers 'what was it then' with a scan, so a Level 4 time-travel question costs minutes instead of a rewrite."
  - q: "A scheduled change was due at t=50 and is first noticed by a call at t=70. At what time is it recorded?"
    options:
      - "At t=70, when the code applied it"
      - "At t=60, halfway between the two"
      - "It isn't recorded, since it was late"
      - "At t=50, when it took effect"
    answer: 3
    explain: "Record the time a change took effect. Otherwise any question about state between 50 and 70 gets the wrong answer."
  - q: "In the war room, the dead-letter alert is firing and duplicates are piling up. What do you do first?"
    options:
      - "Find the root cause, then write and ship a full patch"
      - "Apply a small reversible change that stops the damage"
      - "Roll back the deploy, even though it takes 40 minutes"
      - "Write the status update before touching any settings"
    answer: 1
    explain: "Stabilise first with the smallest change you can undo, such as a settings override. Investigate once the bleeding has stopped. A slow rollback is a fallback, not the first move."
  - q: "Why did the 2.4.0 relay create duplicate invoices on retries?"
    options:
      - "The ERP ignored idempotency keys when it was busy"
      - "The relay retried too fast and overloaded the ERP"
      - "The key included the attempt number, so it changed"
      - "The dedupe cache was cleared on every new deploy"
    answer: 2
    explain: "An idempotency key must be the same for every attempt at the same operation. Adding the attempt number made each retry look like a new order. Fast retries caused the 429 storm, which is a separate problem."
  - q: "A write-the-tests exercise is graded by mutation testing. What makes a check valuable?"
    options:
      - "It passes on the correct code and fails on a realistic bug"
      - "It runs many random inputs without asserting on outputs"
      - "It checks the return type and the length of each result"
      - "It reproduces the implementation's logic inside the test"
    answer: 0
    explain: "A check earns its place when it goes red for a real mistake. Boundaries, duplicates, order and whole-result assertions kill the most mutants. Re-implementing the logic in the test tends to copy the same bug."
  - q: "A customer repo's README says rules belong in hooks. You need a new validation rule. What's the best change?"
    options:
      - "Edit the shared importer, since it's the shortest path"
      - "Copy the importer into a new file and change the copy"
      - "Monkeypatch the importer at start-up from your module"
      - "Add one hook module and register it in the settings"
    answer: 3
    explain: "Use the extension point the code already offers and keep the diff small. Editing or forking shared code works today and breaks other customers or the next upgrade."
  - q: "In an AI-allowed coding round, what are interviewers most likely judging?"
    options:
      - "How much code the assistant produced in the time"
      - "How you split the work and verify what comes back"
      - "Whether you can avoid reading the generated code"
      - "How quickly you paste the whole spec as one prompt"
    answer: 1
    explain: "When typing stops being the bottleneck, judgement is what's left to assess: modelling the problem, asking for small pieces, reading the output and testing the tricky edges. Always confirm with the recruiter whether AI is allowed at all."
  - q: "Mid-problem, the interviewer adds effective-dated prices. Which response shows the strongest adaptation?"
    options:
      - "Rewrite the whole function around a new pricing model"
      - "Add an if-statement for next month's price in the loop"
      - "Change only the price lookup and test the boundary"
      - "Say it's out of scope and finish the original task"
    answer: 2
    explain: "Name the part of the code the change touches, change only that, and pin a test to the exact effective-from instant. A rewrite costs time and a hard-coded branch breaks at the next price change."
---

Ten questions on the drills, the war room, mutation testing, customer repos and live coding. Explanations appear after you answer.
