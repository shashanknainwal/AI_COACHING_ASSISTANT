---
title: Why Discovery Decides the Engagement
type: reading
minutes: 12
---

> **By the end of this lesson you will be able to:**
> - Explain why most failed deployments fail *before* any code is written
> - Tell the difference between what a customer *asks for* and what they *need*
> - Recognize the four outputs every discovery phase must produce

## A story you will live through

A logistics company signs a contract for "an AI assistant for our dispatchers." The FDE arrives, meets the IT lead, and gets a list of features: a chat window, integration with the dispatch system, and answers about shipment status. Six weeks later the assistant works. It's accurate and fast. Nobody uses it.

In the post-mortem the real story comes out. Dispatchers didn't need *answers*. They already knew where shipments were. Their pain was the 40 minutes a day they spent **writing exception emails** to customers when trucks were late. The VP who bought the product cared about one number: late-delivery complaints, which had doubled in a year. Nobody asked the dispatchers. Nobody asked the VP what number they'd be judged on.

The engineering was excellent. The discovery was missing. That's the most common way FDE engagements fail.

## Asks vs. needs

Customers describe **solutions** they've imagined, not the problems underneath. This isn't a flaw; it's how people talk. Your job is to translate.

| What the customer says (the ask) | What might be underneath (the need) |
|---|---|
| "We need a chatbot for our support team." | Agents spend too long searching for answers; new hires take 3 months to ramp. |
| "Can you build a dashboard of all our shipments?" | The COO is blindsided by late shipments and wants early warning. |
| "We want AI to read our contracts." | Legal misses auto-renewal dates, costing ~$400k a year in unwanted renewals. |
| "Integrate with Salesforce." | Sales reps won't use any tool that makes them leave Salesforce. |

The ask often *is* part of the answer. The point isn't to ignore it. The point is to understand the need well enough to know whether the ask will actually solve it, and to be able to measure whether it did.

> **A useful reflex:** whenever you hear a solution ("we need X"), ask *"What would X let you do that you can't do today?"* and then *"What does that cost you right now?"*

## Why FDEs, specifically, must own discovery

In many companies, sales has already "done discovery" before the contract. Treat that as a starting hypothesis, not a fact:

- **Sales discovery optimizes for winning the deal.** It finds enough pain to justify a purchase. It rarely captures workflow detail, data realities, or who will block you.
- **The buyer is rarely the user.** The VP who signed has different pains from the people whose workflow will change.
- **Things changed.** Between the first sales call and your kickoff, there may be a reorg, a new priority, or a failed internal project that makes people wary.

You are the person who will be accountable for the outcome, so you need your own understanding.

## The cost curve of a wrong assumption

A misunderstanding is cheap to fix early and very expensive late:

| When you discover you built the wrong thing | Typical cost |
|---|---|
| During discovery (a question corrects you) | One conversation |
| During prototyping (a demo surprises the user) | A few days of rework |
| During pilot (users don't adopt it) | Weeks, plus lost trust |
| After launch (the sponsor sees no business impact) | The renewal, and your reputation at the account |

This is why great FDEs seem "slow" for the first week and very fast afterward. They're buying down risk while it's still cheap.

## The four outputs of discovery

Discovery isn't a vibe; it has deliverables. By the end of it you should have written down:

1. **A problem statement with numbers.** Who has the problem, what it costs, the current baseline, the target, and the deadline.
2. **A stakeholder map.** The sponsor, champion, users, and gatekeepers, and what each one needs.
3. **Success metrics and acceptance criteria.** How everyone will agree, objectively, that it worked.
4. **A scope.** What you will build first, and just as importantly, what you won't.

The rest of this module teaches each one, with an exercise for each:

| Output | Lesson | Exercise |
|---|---|---|
| Problem statement | Running a discovery call | Analyze a call transcript |
| Stakeholder map | Stakeholder mapping | Build an engagement plan |
| Success metrics | Metrics and acceptance criteria | Measure a baseline from raw data |
| Requirements | Structured outputs with Claude | Extract requirements with Claude |
| Scope | Scope, change requests, saying no | Change-request impact calculator |

## How long should discovery take?

Shorter than you think, and it never fully ends.

- **Timebox the first pass to about one week** for a typical engagement. You should be looking at real data and showing something rough by the end of week one or early week two.
- **Keep discovering throughout.** Every demo is a discovery session in disguise. Users react to working software far more honestly than to questions.

> **Key takeaways**
> - Most failed engagements fail at discovery, not engineering.
> - Customers describe solutions; your job is to uncover and quantify the need beneath them.
> - Sales discovery is a hypothesis. Do your own.
> - Discovery produces four written outputs: problem statement, stakeholder map, success metrics, and scope.
