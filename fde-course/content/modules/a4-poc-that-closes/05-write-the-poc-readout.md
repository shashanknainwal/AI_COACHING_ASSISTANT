---
title: "Write It: The POC Readout"
type: written
minutes: 40
sections:
  - key: summary
    label: 1. Summary and recommendation
    prompt: "The decision you recommend, in the first sentence, and the two or three facts it rests on."
    words: [60, 200]
  - key: results
    label: 2. Results against the agreed criteria
    prompt: "Each agreed criterion: target, baseline, result, met or not. Include the uncertainty where it matters."
    words: [120, 350]
  - key: misses
    label: 3. What didn't work
    prompt: "The misses and the problems, with causes. No excuses, no euphemisms."
    words: [80, 250]
  - key: risks
    label: 4. Risks
    prompt: "What could go wrong in the next phase or in production, and what you'd do about each."
    words: [80, 250]
  - key: next
    label: 5. Next phase and cost
    prompt: "Scope, success criteria, timeline, cost and the decision you need from the customer, with a date."
    words: [80, 250]
rubric:
  - name: Recommendation up front
    points: 20
    lookFor: "The first sentence states a clear decision that follows from the signed decision rules: handling time is a clearly missed must-have, so not a rollout. For example, a fixed extension with live order lookups to re-measure handling time, or a no-go with a stated path back. The summary names the facts it rests on, including the misses."
  - name: Honest results against criteria
    points: 25
    lookFor: "Reports every agreed criterion against its target and baseline. Calls the handling-time result a miss. Reports policy accuracy as 97.7% against a 98% target, below the line, and notes that its interval overlaps the human baseline. Doesn't promote the agent survey to a success criterion."
  - name: What didn't work, owned
    points: 20
    lookFor: "Names the misses (handling time, Spanish emails, the week 2 logging incident, two agents dropping out) with plausible causes (for example the late order data and the read-only snapshot), without blaming the customer or burying the problems in qualifiers."
  - name: Risks with mitigations
    points: 15
    lookFor: "Covers the risks that matter at scale: wrong policy statements reaching customers, non-English traffic, data handling, adoption. Each one comes with a concrete mitigation or monitoring signal."
  - name: Concrete next phase and cost
    points: 20
    lookFor: "A scoped next step (extension or next phase) with its own success criteria, a timeline, a cost estimate built from the numbers given (for example about $1,400 a month in model cost at 45,000 emails, plus the integration work), and a named decision with a date."
passScore: 70
graderNotes: "Reward honesty about the misses above everything else. Mark down heavily if the readout calls handling time 'met' or 'on track', rounds 97.7% up to 98%, leads with the 8.4 agent survey or the acceptance-rate win while hiding the misses, leaves out the week 2 logging incident, or recommends a full rollout to all agents and languages now. Under the signed rules, handling time (6.1 vs at most 5.5 minutes, about 11% over) is clearly missed, and policy accuracy (97.7% vs 98%) is within the 2% borderline band. Good answers recognise both. Acceptable recommendations: a fixed extension (with a date) that adds live order lookups and the holiday policy, then re-measures handling time and policy accuracy; or a no-go on rollout with a stated path back. An argument that the handling-time measurement wasn't fair because of the nightly snapshot is reasonable if it invokes the extension clause rather than declaring the criterion met. A plain 'go' or 'conditional go' that ignores the handling-time miss should not pass. Mark down vague next steps without criteria, dates or cost. Don't reward length; a tight readout that a COO can read in two minutes is the goal."
---

The readout is where a POC closes or stalls. Grace Liu, the Principal architect who coaches this track (a fictional character), has one rule for it: *"Write the readout you'd want if it were your budget. Lead with the decision, show every agreed number, and put the misses where the reader can't miss them."*

In interviews, a case round may ask you to present results like these, and "tell me about a project that didn't go to plan" is a staple of behavioural rounds. Public accounts of architect loops are thin, so treat the exact format as **Anecdotal**. Either way, the skill being tested is the same: honest, decision-ready communication of mixed results.

## The situation

Marlow & Finch, a department-store chain (fictional), ran a six-week POC of an assistant that drafts replies to customer-service emails. Agents review every draft and send it, edit it or discard it. The decision owner is Helen Castellano, Chief Operating Officer (fictional). She'll read your readout before a 30-minute decision meeting.

The signed POC plan had these decision rules: **go** if every must-have is met; **conditional go** if must-haves are met or within 2% of the target, with a fix plan; **no-go** if any must-have is clearly missed; and the option of a fixed extension if a must-have couldn't be measured fairly.

### Results

Quality metrics come from a frozen test set of 300 real English emails from last quarter, graded blind by two senior agents. Handling time comes from a two-week shadow pilot with 12 agents.

| Criterion | Type | Baseline (today) | Target | Result |
|---|---|---|---|---|
| Draft acceptance (sent with no or minor edits) | Must-have | 31% of macro templates sent as-is | at least 60% | 68% (204/300; 95% interval 63%–73%) |
| Policy accuracy (no wrong return, refund or warranty statement) | Must-have | 97.0% for human agents (291/300 in a QA audit) | at least 98% | 97.7% (293/300; 95% interval 95.3%–98.9%) |
| Average handling time per email | Must-have | 7.8 minutes | at most 5.5 minutes | 6.1 minutes (shadow pilot, 12 agents) |
| Customer data written outside approved stores | Must-have | n/a | zero incidents | Zero during the measured weeks 4–6. One incident in week 2 (see notes) |
| Spanish-language emails (12% of volume) acceptance | Nice-to-have | n/a | at least 60% | 42% (15/36; 95% interval 27%–58%) |
| p95 time to draft | Nice-to-have | n/a | at most 8 seconds | 5.2 seconds |
| Model cost per email | Nice-to-have | Agent labour is about $2.10 per email | at most $0.05 | $0.031 |

### Notes from the project log

- Real order data arrived in **week 3**, not week 1, and only as a **read-only nightly snapshot**. In the shadow pilot, agents often checked live order status in the old system before sending a draft. Their logs suggest this took about a minute per email.
- In **week 2**, a debug setting wrote the bodies of 40 customer emails to a development storage bucket outside the approved stores. The team found it the next day, deleted the data, removed the setting, and reported it to Marlow & Finch's security team, who closed it as a minor incident.
- Of the 7 policy errors, 5 involved the **holiday returns extension**, which was announced mid-POC and wasn't in the policy documents the assistant used.
- **2 of the 12** pilot agents stopped using the assistant after week 1. Both said the drafts were too long.
- An end-of-pilot survey gave the assistant **8.4 out of 10** among agents. It was not one of the agreed criteria.
- Marlow & Finch handles about **45,000 customer emails a month**. Building live order lookups is estimated at **3 engineer-weeks**.

## The task

Write the executive readout for Helen Castellano in the five sections on the right. Aim for something she can read in two minutes.

## What a strong readout does

1. **The decision first.** The first sentence is the recommendation. The reasons come after it.
2. **Every agreed number, the same way it was agreed.** Show target, baseline and result side by side. A miss is a miss even if it improved on the baseline. Don't round toward the target, and don't swap in a metric nobody agreed to.
3. **Uncertainty where it changes the story.** Policy accuracy at 97.7% against a 98% target, with an interval that overlaps the human baseline, is a different story from 97.7% on its own.
4. **Causes, not excuses.** "Handling time missed because agents re-checked order status against a nightly snapshot" is useful. "Handling time was impacted by various factors" is not.
5. **A next phase someone can approve.** Scope, criteria, timeline, cost and the decision you need, with a date.

Submit when you're done. You'll get a score for each rubric line, the strongest part of your readout, and the one change to make first.
