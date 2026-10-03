---
title: Scope, Change Requests, and the Art of Saying No
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Write a scope that names what's out as clearly as what's in
> - Run a lightweight change-request process that keeps the sponsor in charge of trade-offs
> - Say no (or "not now") in a way that strengthens the relationship

## Scope creep is the default

Every successful engagement attracts requests. Once users see something working, they imagine ten more things it could do. That's a good sign! It's also how a six-week pilot becomes a five-month slog that never quite launches.

Scope creep rarely arrives as one big request. It arrives as many small, reasonable-sounding ones:

- "While you're in there, could it also…"
- "Can we add one more document type? It's basically the same."
- "The CFO saw the demo and wants a dashboard."
- An FDE's own perfectionism: polishing features nobody asked for, which is called *gold-plating*.

You can't stop requests, and you shouldn't want to; they're valuable signals. What you need is a **process** that turns each request into an explicit decision.

## Writing a scope that holds

Your engagement brief (Module 1) contains a scope. Make it sturdy:

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

Three things make this work:

1. **An explicit "out of scope" list.** It's much easier to point at something already written down than to argue about it later.
2. **Assumptions.** If an assumption breaks (no API by March 17), you have a legitimate reason to revisit the plan.
3. **Capacity in days.** Requests can then be discussed in a common unit: time.

## The iron triangle

Scope, time, and resources are linked. If one grows, at least one of the others must give:

```
           SCOPE
           /   \
          /     \
       TIME ─── PEOPLE
```

For most FDE engagements, **time is fixed** (a pilot ends on a date, or a renewal is coming) and **people are fixed** (you and maybe one more engineer). So the honest answer to "can we add X?" is almost always: **"Yes, if we remove Y or move the date."** Your job is to make that trade-off visible, and let the sponsor choose.

## A lightweight change-request process

You don't need forms and committees. You need five steps, and you need to do them every time:

1. **Log it.** Write down the request, who asked, and why. Use a shared doc or tracker.
2. **Understand the problem behind it.** "What would this let you do?" Sometimes the real need is met by something already in scope.
3. **Estimate it** in days, roughly.
4. **Lay out the options.** Accept (if it fits), swap (drop lower-priority work), slip (move the date), or defer (phase 2).
5. **Let the sponsor decide, then record the decision** in a short email.

Priority matters in step 4. A new *must-have* can justify dropping *could-haves*. A new *could-have* shouldn't displace anything; it waits for phase 2 unless there's spare capacity.

## How to say no without saying "no"

Saying a flat "no" damages relationships. Saying "yes" to everything destroys engagements. Here are the scripts experienced FDEs use.

**"Yes, and here's the trade-off."**
> "We can absolutely add commercial claims. It's about 6 days of work. To keep the April 18 date, we'd defer the weekly metrics report. Or we keep everything and finish around April 28. Which would you prefer?"

**"Not now, but it's on the list."**
> "That's a great idea for phase 2. I've added it to the phase 2 list with your name on it, so it won't get lost. For now, let's get intake live."

**"Help me understand the problem."**
> "Before we scope a dashboard, what decision would the CFO make with it?" *(Often a weekly email with three numbers solves it.)*

**"Let's ask the sponsor."**
> "This changes our plan, so I'd like Joan to make the call. I'll send her the options today."

Notice that none of these say no. They make the cost visible and route the decision to the right person. This keeps you on the customer's side of the table.

## Writing the decision down

Every scope decision deserves a two-line email, sent the same day:

```
Subject: Decision — commercial claims (CR-3)

Hi Joan, confirming today's decision: we're adding commercial claims to phase 1
and deferring the weekly metrics report to phase 2. The April 18 date is unchanged.
```

Six weeks later, when someone asks "why isn't the report done?", you'll be glad you sent it.

## Protecting the team from yourself

The hardest scope to control is your own. FDEs are builders, and building is fun. Before starting anything not in the plan, ask:

- Does this move the agreed metric?
- Did the customer ask for it, or did I decide they need it?
- What am I *not* doing while I do this?

If you can't answer those well, write it on the phase 2 list and move on.

## Turning it into a tool

Evaluating a change request is mostly arithmetic: current load, capacity, the request's size and priority, and which lower-priority items could make room. In the next exercise you'll build a calculator that does this and drafts the message to the sponsor, so every request gets the same fair, fast treatment.

> **Key takeaways**
> - Write an explicit out-of-scope list, assumptions, and capacity in days.
> - Time and people are usually fixed, so added scope means removing scope or moving the date.
> - Run every request through: log → understand → estimate → options → sponsor decides → record.
> - Don't say "no": make the trade-off visible and let the sponsor choose.
