---
title: What an Applied AI Architect Does
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to describe the applied AI architect's job from first call to production, explain the trusted-advisor posture in concrete behaviours, tell the role apart from Applied AI Engineer and Forward Deployed Engineer, and say what the interview loop is likely to test (and how little is publicly known about it).

## The job in one sentence

An applied AI architect helps a large customer decide **whether, where and how** to use a model like Claude, designs the solution, proves it works on the customer's own data, and hands it to the people who will build and run it. You write some code, mostly prototypes and evals. Most of your output is **decisions, designs, numbers and conversations**.

Your coach for this track is **Grace Liu**, a fictional principal architect. She'll hand you customer situations at fictional companies throughout the track. None of them are real customers.

## What the posting says

Anthropic has hired for this work under the title **Solutions Architect, Applied AI**. The posting describes the role in roughly these terms (**Official**, from the posting as mirrored on job boards in 2026):

- A **pre-sales** architect for **large enterprises**.
- A **trusted technical advisor** who helps customers understand what Claude can do and how it fits into their **technology stack**.
- Builds **evals** and designs **scalable architectures**.
- Works with **Sales, Product and Engineering** to take customers **from discovery to deployment**.

When this lesson was checked on 2026-10-08, Anthropic's careers page listed these jobs under the **Applied AI** heading with the title **Applied AI Architect**, split by segment and region: Industries, Commercial, Enterprise Tech, Startups, Digital Natives Business, Partnerships, Public Sector and Cyber, plus regional roles in Asia-Pacific and Europe and manager roles for verticals such as Financial Services and Healthcare & Life Sciences (**Official**, [anthropic.com/jobs](https://www.anthropic.com/jobs)). The full job descriptions sit on a separate hiring site this course couldn't load, so this lesson doesn't quote years of experience, travel or pay. **Read the current posting for your segment yourself** before you apply; segment matters, because a Startups architect and a Public Sector architect spend their weeks very differently.

## From first call to production

The work follows the customer through a lifecycle. Your role changes at each stage, but one thing doesn't: you are the person who makes sure what gets sold can actually be built and will actually work.

| Stage | What you do | What you leave behind | Who else is in the room |
|---|---|---|---|
| 1. Discovery | Find the business problem, the workflow, the data, the constraints and the decision process | A discovery summary with metrics and open questions | Account executive, customer business owner |
| 2. Qualification | Decide with Sales whether this is a good fit and worth a proof of concept | A go/no-go and a scoped use case | Account executive, sales leadership |
| 3. Solution design | Pick the approach, design the architecture, estimate cost and latency | A solution design doc (lesson 04) | Customer architects and engineers |
| 4. Proof of concept | Agree success criteria up front, build evals on real data, run the bake-off honestly | Eval results and a recommendation | Customer engineers, sometimes Applied AI engineers |
| 5. Security and procurement | Answer the security review, explain data handling, support legal | Completed questionnaires, an architecture diagram for the CISO | CISO's team, legal, procurement |
| 6. Deployment handoff | Hand the design and evals to whoever builds production: the customer, a partner, or a forward deployed team | A handoff pack: design, evals, risks, open items | Customer engineering, partners, FDEs |
| 7. Expansion | Check the metrics landed, find the next use case, feed field lessons back to Product | A results review and the next opportunity | Account team, Product |

Two things in that table are easy to miss. First, **qualification is part of your job**: telling Sales that a use case is a poor fit early saves everyone months. Second, **the security review can easily become the longest stage** of an enterprise deal, so you start it during discovery, not after the proof of concept. Module A2 covers enterprise deployment and security reviews in depth; A4 covers proofs of concept.

## The trusted-advisor posture

"Trusted advisor" is easy to put in a posting and hard to do. It means the customer believes you'll tell them the truth even when the truth costs your company a deal. In practice it looks like this:

| A vendor says | An advisor says |
|---|---|
| "Claude can do that." | "Claude can do the classification well. The final payout decision should stay with a person, and here's why." |
| "Let's start a pilot." | "Before a pilot, we need a baseline. How long does this take today, and how often is it wrong?" |
| "Accuracy will be very high." | "On your 300 test cases we got 91% right. Here are the 27 we got wrong and what they have in common." |
| "We support every requirement." | "Two of your requirements conflict. Here are the options and what each one costs." |
| "Fine-tuning will fix it." | "Let's try better prompts and retrieval first. They're cheaper to change, and we can measure whether they're enough." |

Three habits sit behind the right-hand column:

1. **Quantify.** Every claim you make has a number and a source: an eval result, a cost estimate with its arithmetic, a baseline the customer measured.
2. **Say what you don't know.** "I'll confirm that with our security team by Thursday" builds more trust than a confident guess that turns out wrong in the security review.
3. **Recommend against yourself when it's right.** If a rules engine solves 80% of the problem for a tenth of the cost, say so. Customers remember the architect who saved them money.

## Working with Sales, Product and Engineering

**Sales.** The account executive owns the relationship, the deal and the forecast. You own the **technical win**: the customer's technical team believes the solution will work and is willing to say so. Agree early who leads which meeting. Tell your account executive bad news (a blocked data source, a skeptical CISO) the day you learn it.

**Product.** You see dozens of customers. Product sees aggregates. Your field feedback is valuable only when it's specific: "Four financial-services customers this quarter blocked on X; here's the workaround each used and the revenue at stake" gets read. "Customers want more features" doesn't.

**Engineering, Applied AI engineers and FDEs.** When the build is hard, you bring in specialists. Write the handoff so they don't have to repeat discovery: goals, constraints, evals, decisions made and why, and what's still open.

## How it differs from the neighbouring roles

The three applied roles in this course overlap. This comparison is the course's framing, built from the three postings summarised in module C1; it isn't an official org chart.

| | Applied AI Architect | Applied AI Engineer | Forward Deployed Engineer |
|---|---|---|---|
| Main question | Should we, and how, at what cost? | How do we build it so it works? | How do we ship it inside this customer's systems? |
| Typical stage | Pre-sales through handoff | Discovery through deployment, deeper on the build | Deployment and production |
| Main outputs | Designs, recommendations, eval plans, cost models | Eval frameworks, prototypes, reference implementations | Production code, integrations, MCP servers, agents |
| Code | Prototypes, evals, scripts | A lot | Most of the week |
| Accounts at once | Many | Several | One or a few |
| Who you persuade | Executives, CISOs, customer architects | Customer engineers | Customer engineers and operators |

If you're deciding between tracks: choose this one if you enjoy whiteboards, tradeoffs and rooms with executives more than long stretches of implementation. The FDE track (modules 01–10) and the Engineer track (E1–E7) cover building in depth; this track assumes you could build it and focuses on deciding and persuading.

## How this shows up in interviews

Public data on applied architect loops is **sparse**. Treat everything below as a starting hypothesis and ask your recruiter for the actual format.

| What you might face | Label |
|---|---|
| Write your own application answers; no AI in take-homes or live interviews unless told otherwise; preparing with Claude is encouraged | **Official** ([candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance)) |
| A culture or values interview, as for every role at Anthropic | Reported (module C5) |
| A recruiter screen, then a technical screen on LLM application architecture and AI concepts | Anecdotal (commercial prep guides, few independent accounts) |
| A customer scenario: either a presentation of a solution to a case you're given, or a live role-play with an interviewer playing the customer | Anecdotal |
| At other labs, solutions roles reported as a case discussion plus a presentation | Anecdotal (module C1) |

The common thread is that you'll have to **think like an architect out loud**: ask discovery questions before designing, make tradeoffs with numbers, and stay honest under pressure. This module trains the first two; module A5 trains executive pressure; the A7 mock loop puts it all together.

**Practice prompts** (original, in the style of the rounds above):

- "Walk me through how you'd take a large insurer from a first meeting to Claude in production. Where does it usually stall?"
- "Tell me about a time you told a customer, or your own sales team, that something wasn't a good fit."
- "A customer says they want to fine-tune a model on their support tickets. What do you ask before answering?"

For each, answer in under three minutes, with one real example and one number.

> **Key takeaways**
>
> - The architect decides whether, where and how to use the model, proves it on the customer's data, and hands off a design others can build.
> - "Trusted advisor" means quantified claims, honest unknowns, and recommending against yourself when that's right.
> - You own the technical win; the account executive owns the deal. Start the security review early.
> - The role differs from Applied AI Engineer and FDE by output: decisions and designs rather than production code.
> - Interview data for this role is thin. Plan for a technical design conversation, a customer scenario and a values round, and confirm with your recruiter.
