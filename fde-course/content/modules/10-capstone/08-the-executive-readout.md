---
title: "The Executive Readout"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Structure a readout that leads with the decision executives need to make
> - Present results honestly, including failures and limits, in a way that builds trust
> - Turn the engagement into a clear next step: expand, change course or stop
> - Handle the hard questions executives ask

## What a readout is for

The readout isn't a demo or a summary of your work. It's a **decision meeting**. Dana and the CEO need to decide: do we roll this out, change it, or stop? Everything in the readout should help them make that decision with confidence.

Executives have little time and many priorities. Assume you'll get the first five minutes of attention, and maybe not the rest.

## Structure: answer first

1. **The recommendation** (one sentence). *"Roll out exception triage to all three Midwest hubs over the next six weeks."*
2. **The headline results** (three to five numbers, against the baseline and the targets agreed at the start).
3. **What it means for the business** (time, money, customers).
4. **What didn't work, and what we did about it.**
5. **Risks and how they're managed.**
6. **The ask:** decisions, people, budget, dates.
7. **Appendix:** method, eval details, assumptions. Available, not presented.

### Results against the targets you agreed

Show the scoreboard from the brief. It's the strongest evidence that you did what you said you would:

| Metric | Baseline | Target | Pilot |
|---|---|---|---|
| Median handling time | 25 min | 12.5 min | 8.6 min (average\*) ✓ |
| SLA breach rate | 20.7% | 10.3% | 8.2% ✓ |
| Automation rate | 0% | 40% | 45% ✓ |

\*Be precise about comparisons: the pilot measured an average, the baseline a median. Say so in a footnote, or measure the same way. An executive's analyst will notice.

### Translate into business terms

- **Time:** "309 coordinator hours a month go back to the hard cases." (Not "we saved 2.2 FTE," unless the customer wants to frame it that way: it can sound like a layoff plan, and Dana's team is in the room.)
- **Customers:** "Platinum SLA breaches fell from 39% to 5%." This is the line Dana will repeat to the CEO, because Halvorsen nearly left.
- **Money:** "About $14,800 a month net, so the engagement pays for itself in under three months." Show the assumptions (loaded cost per hour, volume) in the appendix.

### Show what didn't work

Trust comes from honesty about limits. Include:

- **The eval failures** and their fixes: "Our first version treated a platinum delay as routine, and once forgot to notify a customer about damage. We added rules and tests; P1 recall is now 100% on the eval set, and the release gate blocks any version that regresses."
- **Guardrail activity:** "The guardrail blocked 9 messages that promised credits; in each case the agent rewrote the message. No message has promised compensation."
- **Limits:** "Customs holds still need a broker; the agent opens the ticket and informs the customer, but doesn't resolve them."

An executive who hears only good news assumes you're hiding the bad news.

### Check every number

You saw in the last exercise how a fluent draft can contain a number nobody gave it. Before the readout, check every number on every slide against its source: the eval report, the pilot data, the finance assumptions. Have someone else check them too.

## The ask

End with specific decisions:

> *"We're asking for three decisions today: (1) approve the rollout to Kansas City and Detroit in May and June; (2) assign one ops lead per hub to label 50 cases for the eval set; (3) move the Phase 2 items, proactive ETAs and claims automation, into next quarter's plan, with a scoping session in two weeks."*

Notice it includes the asks you said no to in week one. Out-of-scope items are not forgotten; they become the next phase. That's how engagements grow.

## Hard questions to prepare for

| Question | Good answer includes |
|---|---|
| "What happens when it's wrong?" | Guardrails, approvals, audit log, fallback to coordinators, eval gate on every change |
| "What if the AI provider has an outage?" | Circuit breaker and fallback: exceptions go to the coordinator queue as today |
| "Does our customer data leave our cloud?" | Data flow, deployment through their cloud account, what's logged |
| "Will this replace my team?" | Time goes to hard cases and customer relationships; coordinators approve and oversee |
| "How do we know it keeps working?" | Monitoring, sampled review, eval suite and release gate the customer's team owns |
| "What does it cost at full scale?" | API cost per exception and monthly projection with assumptions |

## After the readout

- **Send a written summary** the same day: decisions made, owners, dates.
- **Hand off** (Module 9): runbooks, eval suite, operations guide, and drills with their team.
- **Measure again** in 30 days, and share the results. The best references come from customers whose results held up after you left.

> **Key takeaways**
> - A readout is a decision meeting: lead with the recommendation, then results against the agreed targets, business impact, failures, risks and the ask.
> - Translate results into time, customers and money, with assumptions in the appendix; frame time savings with care for the team in the room.
> - Show what didn't work and what you did about it; check every number against its source.
> - End with specific decisions, including the next phase built from earlier out-of-scope asks.
