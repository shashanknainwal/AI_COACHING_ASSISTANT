---
title: "The Executive Readout"
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Structure a readout that leads with the decision
> - Present results honestly, including what failed
> - End with a clear ask and answer the hard questions

Dana's CEO wants one answer: roll out, change, or stop? You get about five minutes of attention, and your numbers must survive an analyst.

## Structure: answer first

The readout is a **decision meeting**, not a demo.

1. **Recommendation**, one sentence: *"Roll out exception triage to all three Midwest hubs over the next six weeks."*
2. **Headline results** against baseline and agreed targets.
3. **Business meaning**: time, money, customers.
4. **What didn't work** and what you did.
5. **Risks** and mitigations.
6. **The ask**: decisions, people, budget, dates.
7. **Appendix** (not presented): method, evals, assumptions.

### The scoreboard you agreed

| Metric | Baseline | Target | Pilot |
|---|---|---|---|
| Median handling time | 25 min | 12.5 min | 8.6 min (average\*) ✓ |
| SLA breach rate | 20.7% | 10.3% | 8.2% ✓ |
| Automation rate | 0% | 40% | 45% ✓ |

\*Average vs median: footnote it or measure the same way.

### Business terms

- **Time:** "309 coordinator hours a month go back to the hard cases." Avoid "we saved 2.2 FTE": it sounds like a layoff plan, and Dana's team is in the room.
- **Customers:** "Platinum SLA breaches fell from 39% to 5%." The line Dana will repeat, because Halvorsen nearly left.
- **Money:** "About $14,800 a month net; the engagement pays back in under three months." Assumptions go in the appendix.

### What didn't work

Only good news sounds like hidden bad news.

- **Eval failures:** "Version one treated a platinum delay as routine. We added rules and tests; P1 recall is now 100% on the eval set, and the gate blocks regressions."
- **Guardrails:** "9 messages promising credits were blocked and rewritten."
- **Limits:** "Customs holds still need a broker."

**Check every number** against its source, and have someone else check too. The last exercise showed how a fluent draft invents one.

## The ask

> *"We're asking for three decisions today: (1) approve the rollout to Kansas City and Detroit in May and June; (2) assign one ops lead per hub to label 50 cases for the eval set; (3) move the Phase 2 items, proactive ETAs and claims automation, into next quarter's plan, with a scoping session in two weeks."*

Week-one out-of-scope asks become the next phase.

## Hard questions

| Question | Good answer includes |
|---|---|
| "What happens when it's wrong?" | Guardrails, approvals, audit log, fallback, eval gate |
| "What if the AI provider is down?" | Circuit breaker; exceptions go to coordinators as today |
| "Does our data leave our cloud?" | Deployed in their account; metadata-only logs |
| "Will this replace my team?" | Time goes to hard cases; coordinators oversee |
| "How do we know it keeps working?" | Monitoring, sampled review, an eval gate they own |
| "What does it cost at full scale?" | Cost per exception and monthly projection |

Afterwards: send a written summary the same day (decisions, owners, dates), hand off (Module 9), and measure again in 30 days.

> **Key takeaways**
> - Lead with the recommendation, then results against agreed targets, impact, failures, risks and the ask.
> - Frame time savings with care for the team in the room; check every number against its source.
> - End with specific decisions, including a next phase built from earlier out-of-scope asks.
