---
title: "The Brief: Meet NorthStar Logistics"
type: reading
minutes: 5
---

> **By the end of this lesson you will be able to:**
> - Pick out the discovery facts that shape scope, design and metrics

Dana Whitfield's coordinators spend their days reading carrier messages and typing the same emails, while NorthStar's best customers breach SLAs. You have 20 working days, and every earlier module feeds in.

## The customer

**NorthStar Logistics**, a Midwest freight company, serves about 300 business customers through partner carriers (FastFreight, BlueLine Express, NorthPeak Carriers). Scope: the **Chicago hub**. When a shipment goes wrong (delay, damage, customs hold, bad address, missed pickup), the carrier event makes it an **exception**, which coordinators handle by hand.

| Tier | First response within | Example customers |
|---|---|---|
| Platinum | 2 hours | Halvorsen Medical Supply, Ironline Auto Parts |
| Gold | 4 hours | Lakeshore Electronics, Cedar Valley Foods |
| Standard | 24 hours | Prairie Home Goods, Bramble & Oak Furniture |

## Discovery notes (abridged)

Sort each line: fact, opinion, requirement or risk?

> **Dana Whitfield, VP Operations (sponsor).** "We're breaching SLAs with our best customers, and Halvorsen nearly left us last quarter. I want exceptions triaged automatically, with the email drafted, so my team handles the hard cases. I need a weekly report for the CEO. Budget: one FDE for **20 working days**."
>
> **Marcus Bell, ops lead.** "Delays are most of the volume and mostly routine. Damage and customs holds take longest. Rerouting a missed pickup costs real money, so a coordinator or I always approve it. Never promise a customer a refund or credit: only account managers can, and it's in the contracts."
>
> **Priya Raman, customer success.** "Platinum customers would love proactive ETA emails on every shipment."
>
> **Sam Ortiz, IT security.** "Anything automated needs SSO and an audit log of every action. Customer data stays in our cloud account; we use Claude through our existing AWS setup."
>
> **Finance (email).** "Could you also rebuild carrier invoice reconciliation?"
>
> **Data.** Shipment CSV, carrier events, customer list, 30 days of exception history. "The export is a bit messy."

## What jumps out

| Signal | What it means for you |
|---|---|
| Sponsor's success | SLA improvement and time back, reported weekly |
| Platinum breaches | Biggest risk, best readout story (confirm in baseline) |
| Hard constraints | No compensation promises; reroutes need human approval; SSO and audit log; data stays in their cloud |
| Scope pressure | ETAs and invoice reconciliation don't fit 20 days: say no kindly, with a path for later |
| Data risk | Cleaning and joining come before any model work |

## The engagement plan

Scope (baseline, metrics) → clean and join the data → design → build the triage agent → evaluate and decide → readout numbers → the executive readout, a live readout with Dana, and the final assessment.

> **Key takeaways**
> - Coordinators triage exceptions by hand, and platinum customers breach SLAs most.
> - Hard constraints: no compensation promises, approved reroutes, SSO plus audit log, data in their cloud.
> - 20 days means some reasonable asks wait; data cleaning comes first.
