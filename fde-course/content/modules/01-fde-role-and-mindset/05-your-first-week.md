---
title: Your First Week on an Engagement
type: reading
minutes: 12
---

The first week of an engagement sets the tone for everything that follows. Customers decide quickly whether you're a vendor to be managed or a partner to be trusted. Here is a playbook that works.

## Before day one

Read everything your company already knows about the customer: the sales notes, the contract or order form, any proof-of-concept results, and support tickets. Then write down three things:

1. **What was promised.** Sales may have committed to outcomes, timelines, or features. You need to know before the customer reminds you.
2. **Your hypotheses.** "I think the highest-value use case is X because of Y." You'll test these in discovery.
3. **Your questions.** Especially about data access, security review, and who decides.

## The kickoff meeting

The kickoff is usually a 60-minute call or meeting with the customer's key people. Your goals:

- Confirm the **business problem** and how success will be measured.
- Identify the **people** and their roles (more on this below).
- Surface **risks** early: data access, security reviews, competing projects, holidays, budget cycles.
- Leave with **action items** that have an owner and a date.

Take structured notes during the meeting. You'll parse a set of real-looking kickoff notes in the next exercise, and the format there is a good template.

## The four people you must find

Every engagement has these roles, even if nobody has the title. Find them in week one.

| Role | Who they are | What they need from you |
|---|---|---|
| **Executive sponsor** | Owns the budget and the business outcome | Brief, regular proof that the investment is working |
| **Champion** | Day-to-day advocate who wants this to succeed, often a team lead | Quick wins they can show their boss, and responsiveness |
| **Users** | The people whose workflow changes | A tool that saves them time, and to be listened to |
| **Gatekeepers / blockers** | IT, security, legal, data owners who can say no | Clear documentation, respect for their process, early involvement |

> **The most common way engagements die:** there's a champion but no sponsor. The champion loves the pilot, but nobody with budget authority cares, so it never expands. If you can't name the sponsor by the end of week one, make it your top priority.

Blockers aren't villains. A security team that blocks you usually has a legitimate concern you haven't addressed yet. Meet them early, bring a clear data-flow diagram, and ask what they need to approve.

## The engagement brief

By the end of week one, write a one-page **engagement brief** and share it with the sponsor and champion. It should fit on one page:

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
Next 2 wks: Profile 1 month of faxes; extraction prototype on 50 samples.
Asks:       Sandbox credentials (Sam, Mar 8). 2 hrs/wk of Priya's time.
```

Why this matters:

- It forces **clarity**. If you can't fill a line, you've found a gap in discovery.
- It creates **agreement**. Ask the sponsor to reply "looks right" or correct it. Now you have a written scope.
- It's a **baseline for change**. When someone asks for something new in week 5, you can point to the brief and have a calm conversation about trade-offs.

## Week-one checklist

- [ ] Kickoff held; notes shared within 24 hours
- [ ] Sponsor, champion, users, and gatekeepers identified by name
- [ ] Success metric agreed, with a baseline (or a plan to measure one)
- [ ] Data access requested; security review started
- [ ] First look at real data (even a small sample)
- [ ] Engagement brief v1 sent and acknowledged
- [ ] Weekly update cadence agreed (day, time, format)

## A note on communication cadence

Pick one day of the week and send a short written update, every week, without fail. A good format is four headings: **Shipped**, **Metric**, **Next**, **Need from you**. Consistency matters more than length. Sponsors who receive a crisp update every Friday rarely need status meetings.
