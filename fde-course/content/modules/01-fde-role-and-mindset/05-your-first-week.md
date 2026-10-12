---
title: Your First Week on an Engagement
type: reading
minutes: 7
---

> **By the end of this lesson** you will be able to run a kickoff, find the four key people, and write a one-page engagement brief.

Monday is your Brightline kickoff with Dana Ruiz. By Friday she'll have decided whether you're a vendor to manage or a partner to trust.

## Before and during the kickoff

Beforehand, read the sales notes and contract and write down **what was promised** and **your questions**. Leave the kickoff with the **problem and success metric**, the **people**, early **risks** (data access, security, competing projects, budget cycles), and **actions with an owner and a date**.

## The four people you must find

| Role | Who | What they need from you |
|---|---|---|
| **Executive sponsor** | Owns budget and business outcome | Brief, regular proof the investment works |
| **Champion** | Day-to-day advocate, often a team lead | Quick wins to show their boss |
| **Users** | People whose workflow changes | Time saved, and being listened to |
| **Gatekeepers** | IT, security, legal, data owners | Clear documentation, early involvement |

> **The most common way engagements die:** a champion but no sponsor. The pilot is loved but never expands. No named sponsor by Friday? Make it your top priority.

Meet gatekeepers early with a data-flow diagram and ask what they need to approve.

## The engagement brief

By the end of week one, send the sponsor and champion one page:

```
ENGAGEMENT BRIEF — Brightline Health — v1 (March 6)

Problem:    Referral intake takes ~3 days because faxed referrals are
            hand-keyed into the EHR by a team of 6.
Goal:       Same-day intake for 80% of referrals by June 30.
Metric:     Median hours from fax received → referral in EHR.
            Baseline: 71 hours (Feb sample, n=412).
Scope:      Fax OCR + field extraction + human review queue.
Not scope:  EHR write-back (phase 2, pending vendor API access).
People:     Sponsor: Dana Ruiz (VP Ops) · Champion: Priya Nair (Intake Lead)
            Security review: Sam Okafor (IT Director)
Risks:      EHR API approval may take 6+ weeks. Handwritten referrals ~15%.
            Referrals are PHI: no real faxes to the model until a BAA
            is signed and HIPAA scope is confirmed (Sam + account team).
Next 2 wks: Profile 1 month of faxes on-site; extraction prototype on 50
            de-identified samples until the BAA is in place.
Asks:       Sandbox credentials (Sam, Mar 8). 2 hrs/wk of Priya's time.
```

A line you can't fill is a discovery gap. Once the sponsor replies "looks right", it's your written scope for week-5 change requests.

## Regulated data changes week one

Brightline's referrals are protected health information (PHI) under HIPAA, and Brightline is a covered entity. That changes the order of work:

- **A Business Associate Agreement (BAA) comes first.** Any vendor that processes PHI for Brightline, including the AI provider and your own company, needs a BAA before real patient data flows. Ask in the kickoff who signs it and how long their legal review takes.
- **HIPAA readiness is set up, not assumed.** Anthropic offers HIPAA readiness for eligible Claude API features with a signed BAA, but not every platform or feature is covered (the Architect track's A2 module goes deeper). Confirm the exact scope, platform and features in writing with the customer's Anthropic account team before you design around them. "Claude is HIPAA compliant" is not a sentence an FDE says.
- **Prototype without PHI.** Until the BAA is in place, work with de-identified or synthetic referrals, or profile the data on Brightline's own machines without sending it anywhere.
- **Minimum necessary.** Send the model only the fields a step needs, and keep fax content and patient fields out of your logs. Request IDs, timings and token counts are enough to debug.

Put the BAA on the risk line of your brief with an owner and a date. In regulated work it is often the critical path, ahead of any code.

## Week-one checklist

- [ ] Notes shared within 24 hours; the four roles named
- [ ] Metric agreed with a baseline (or a plan for one)
- [ ] Data access requested; security review started; for regulated data, the BAA owner and timeline known
- [ ] Brief v1 acknowledged; weekly update agreed

**Cadence:** a short written update, same day every week: **Shipped**, **Metric**, **Next**, **Need from you**.

> **Key takeaways**
> - Leave the kickoff with a metric, named people, risks and owned actions.
> - No sponsor by end of week one is your top risk.
> - With regulated data (PHI), the BAA and confirmed HIPAA scope come before any real data reaches a model.
