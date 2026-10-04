---
title: "The Brief: Meet NorthStar Logistics"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Describe the customer, the problem and the people involved in the capstone engagement
> - Pick out the facts in discovery notes that will shape scope, design and success metrics
> - Plan the engagement as the sequence of exercises in this module

## Welcome to your engagement

This module is a complete, simulated FDE engagement. You'll use skills from every module: discovery and scoping (Modules 1-2), data wrangling (3), integrations (4), SQL thinking (5), the Anthropic SDK (6), tools and agents (7), evals and cost (8), and production practices (9). Each exercise builds one deliverable, and the module ends with the executive readout.

## The customer

**NorthStar Logistics** is a mid-sized freight company in the US Midwest. It moves pallets and truckloads for about 300 business customers, using partner carriers (FastFreight, BlueLine Express and NorthPeak Carriers). Your engagement covers their **Chicago hub**.

When a shipment goes wrong (delayed, damaged, held at customs, a bad address, a missed pickup), the carrier sends an event, and the shipment becomes an **exception**. A team of ops coordinators handles exceptions by hand: they read the carrier event, look up the shipment and customer, decide what to do, open tickets, and email the customer.

Customers have SLA tiers for how quickly NorthStar must respond to an exception:

| Tier | First response within | Example customers |
|---|---|---|
| Platinum | 2 hours | Halvorsen Medical Supply, Ironline Auto Parts |
| Gold | 4 hours | Lakeshore Electronics, Cedar Valley Foods |
| Standard | 24 hours | Prairie Home Goods, Bramble & Oak Furniture |

## Discovery notes (abridged)

These are your notes from the discovery week. Read them as an FDE: what is a fact, what is an opinion, what is a requirement, and what is a risk?

> **Dana Whitfield, VP Operations (executive sponsor).** "My coordinators spend their whole day reading carrier messages and typing the same emails. We're breaching SLAs with our best customers, and Halvorsen nearly left us last quarter. I want exceptions triaged automatically, with the customer email drafted, so my team handles the hard cases. I need a weekly report I can take to the CEO. Budget is one FDE for **20 working days** for this phase."
>
> **Marcus Bell, ops team lead.** "Delays are most of the volume and mostly routine. Damage and customs holds take the longest: claims paperwork, brokers, photos. When a pickup is missed we scramble to find another carrier, and rerouting costs real money, so a coordinator or I always approve it. Never let anything promise a refund or credit to a customer: only account managers can do that, and it's in the contracts."
>
> **Priya Raman, customer success.** "Platinum customers want to hear from us before they notice the problem. Honestly, they'd love proactive ETA emails on every shipment."
>
> **Sam Ortiz, IT security.** "Anything automated needs SSO and an audit log of every action it takes. Customer data stays in our cloud account. We use the Claude API through our existing AWS setup."
>
> **Finance (by email).** "While you're in there, could you also rebuild carrier invoice reconciliation?"
>
> **Data.** You received a shipment export (CSV), a dump of carrier events, the customer list, and 30 days of exception-handling history from their ticketing system. The ops team warned that "the export is a bit messy."

## What jumps out

- **The sponsor's success** is visible SLA improvement and time given back to her team, reported weekly.
- **Platinum customers breach the most** (you'll confirm this in the baseline). That's both the business risk and the best story for the readout.
- **Hard constraints:** no compensation promises in customer messages; reroutes need human approval; SSO and an audit log; data stays in their cloud.
- **Scope pressure:** proactive ETAs for every shipment and invoice reconciliation are reasonable asks, but they don't fit 20 days alongside the core work. You'll need to say no clearly and kindly, with a path for later.
- **Data risk:** a "messy" export means cleaning and joining come before any model work.

## The engagement plan

| Step | Exercise | Deliverable |
|---|---|---|
| 1 | Scope the engagement | Baseline numbers, prioritized scope, success metrics, draft brief |
| 2 | Clean and join the data | Clean shipments, the exception queue, a data-quality report |
| 3 | Design the system | Architecture choices (next reading) |
| 4 | Build the triage agent | Tools, guardrails, approval gate, audit trail |
| 5 | Evaluate the agent | Eval suite and a ship / don't-ship decision |
| 6 | The numbers for the readout | Impact model and a fact-checked summary |
| 7 | The executive readout | Presentation structure (final reading), then the final assessment |

> **Key takeaways**
> - NorthStar's coordinators triage shipment exceptions by hand, and platinum customers are breaching SLAs.
> - Hard constraints: no compensation promises, human approval for reroutes, SSO plus audit log, data in their cloud.
> - The budget is 20 working days, so some reasonable asks will be out of scope; data cleaning comes before model work.
