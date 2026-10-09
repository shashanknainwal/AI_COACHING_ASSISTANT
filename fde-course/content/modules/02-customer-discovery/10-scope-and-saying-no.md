---
title: Scope, Change Requests, and the Art of Saying No
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Write a scope that names what's out as clearly as what's in
> - Run a change-request process that keeps the sponsor in charge of trade-offs
> - Say "not now" in a way that strengthens the relationship

Lumen's claims pilot is working, and now everyone wants more: commercial claims, fraud scoring, a dashboard for the CFO. Each one is asked for as if it's small. This is how a six-week pilot becomes a five-month slog.

Scope creep arrives as many reasonable requests ("while you're in there…", "it's basically the same") plus your own *gold-plating*. Requests are valuable signals. You need a process that turns each one into an explicit decision.

## A scope that holds

```
SCOPE — Lumen Insurance claims intake, phase 1 (Mar 10 – Apr 18)

In scope
  • Auto-read claim emails + PDF attachments (auto and property claims)
  • Pre-fill 8 core fields in ClaimsPro; adjuster reviews before submit
  • Highlight low-confidence fields
  • Weekly metrics report: intake time, rework rate

Out of scope (phase 2 candidates)
  • Commercial claims (different forms, ~6% of volume)
  • Fraud scoring
  • Automatic submission without adjuster review

Assumptions
  • ClaimsPro import API available in staging by Mar 17
  • Two adjusters available 2 hrs/week for feedback

Capacity: 25 engineering days
```

The **out-of-scope list** is easier to point at than to argue about. **Assumptions** give a legitimate reason to revisit the plan when one breaks. **Capacity in days** gives every request a common unit.

## The iron triangle

Scope, time and people are linked. In most engagements time and people are fixed, so the honest answer to "can we add X?" is: **"Yes, if we remove Y or move the date."** Make the trade-off visible and let the sponsor choose.

## Change requests in five steps

1. **Log it:** what, who asked, why.
2. **Understand the problem:** "What would this let you do?" It may already be met by something in scope.
3. **Estimate** in days.
4. **Lay out options:** accept (if it fits), swap (drop lower-priority work), slip (move the date) or defer (phase 2).
5. **Sponsor decides; record it** the same day.

A new *must-have* can justify dropping *could-haves*. A new *could-have* displaces nothing; it waits unless there's spare capacity.

## Saying no without "no"

**"Yes, and here's the trade-off."**
> "We can add commercial claims. It's about 6 days. To keep April 18 we'd defer the weekly metrics report, or keep everything and finish around April 28. Which do you prefer?"

**"Not now, but it's on the list."**
> "Great phase 2 idea. It's on the list with your name on it."

**"Help me understand the problem."**
> "Before we scope a dashboard, what decision would the CFO make with it?" *(Often a weekly email with three numbers.)*

**"Let's ask the sponsor."**
> "This changes our plan, so I'd like Joan to make the call. I'll send her the options today."

None say no. They make the cost visible and route the decision to the right person.

```
Subject: Decision — commercial claims (CR-3)

Hi Joan, confirming today's decision: we're adding commercial claims to phase 1
and deferring the weekly metrics report to phase 2. The April 18 date is unchanged.
```

**Your own scope:** before building anything unplanned, ask whether it moves the agreed metric, whether the customer asked for it, and what you're not doing instead.

The next exercise builds a calculator that evaluates a request and drafts the sponsor message.

> **Key takeaways**
> - Write an out-of-scope list, assumptions and capacity in days.
> - Added scope means removing scope or moving the date.
> - Log → understand → estimate → options → sponsor decides → record.
