---
title: Running a Discovery Call
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Prepare and structure a 45-minute discovery call
> - Use a question bank that reliably surfaces workflow, pain, cost, and constraints
> - Apply four listening techniques that separate great discovery from interrogation
> - Turn a call into a follow-up email the customer will actually reply to

## Before the call: 20 minutes of prep

Walking in cold wastes the customer's time and signals that you don't take them seriously. Do this first:

1. **Read what exists:** sales notes, the contract, previous emails, the company's website and recent news.
2. **Write three hypotheses.** For example: *"Intake is slow because faxes are re-keyed by hand."* Hypotheses make your questions sharper, and you'll learn the most when one turns out to be wrong.
3. **Send a short agenda the day before.** It sets expectations and often gets the right people into the room.

```
Subject: Tomorrow's discovery call — agenda (45 min)

Hi Priya,
Looking forward to tomorrow. So we use the time well:
  1. How referral intake works today, step by step (20 min)
  2. Where it hurts most, and what that costs (10 min)
  3. What success would look like by end of Q2 (10 min)
  4. Next steps and data we'd need (5 min)
If it's easy, could you bring 2-3 example referrals (redacted is fine)?
Thanks, Alex
```

## The shape of a good call

| Phase | Time | Your goal |
|---|---|---|
| Open | 3 min | State the purpose, confirm time, ask permission to take notes |
| Workflow | 15-20 min | Understand how work happens today, step by step |
| Pain and cost | 10 min | Find where it hurts and quantify it |
| Success | 5-10 min | Learn how they'll judge success, in their words |
| Close | 5 min | Summarize back, agree next steps, ask for data |

Notice how much time goes to *workflow*. You can't find the real problem until you understand how work actually flows, including the workarounds nobody mentions in a sales call.

## The question bank

You won't ask all of these. Pick 8-12 based on your hypotheses. Notice that almost all of them are **open questions**: they can't be answered with yes or no.

**Workflow and context**
- "Walk me through what happens from the moment a referral arrives until it's in the EHR."
- "Tell me about the last time this went wrong. What happened?"
- "Who touches this along the way?"
- "What tools do you use for each step? Where do people copy and paste?"

**Pain and cost**
- "Which step takes the longest? How long, roughly?"
- "How often does that happen: daily, weekly?"
- "How many people spend time on this?"
- "What happens downstream when it's late or wrong?"
- "If we did nothing for a year, what would happen?"

**Past attempts**
- "What have you tried already? What happened?"
- "Why didn't that stick?" *(This one prevents you from repeating a failed project.)*

**Success**
- "Six months from now, what would make you say this was a great investment?"
- "Which number would you show your boss?"
- "What would make you consider this a failure, even if it technically works?"

**Data and systems**
- "Where does the data live today? Who owns it?"
- "Could we look at a sample of 50 real examples next week?"
- "What approvals do we need to access it?"

**People and process**
- "Who else should we talk to? Who might be worried about this?"
- "Who signs off on going live?"

**Constraints and risks**
- "Are there compliance or security requirements we should design for from day one?"
- "Anything coming up that could get in the way: audits, migrations, holidays?"

## Four techniques that make the difference

### 1. "Walk me through the last time…"

Asking about a *specific recent instance* gets you real detail. Asking about the general case gets you the idealized process from the policy document.

> Weak: "How does intake work?"
> Strong: "Walk me through the last referral you processed this morning."

### 2. Quantify everything

Every pain needs a number. When someone says "it takes forever," gently ask:
- *How long?* (minutes, hours, days)
- *How often?* (per day, per week)
- *How many people?*

"It takes forever" becomes "6 people spend about 2 hours a day re-keying faxes," which is about 60 person-hours a week. Now you have a business case and a baseline.

### 3. Ask "why" more than once

The first answer is usually the surface. Ask why again, politely, until you reach something structural.

> "Why are referrals delayed?" → "Because the fax queue backs up."
> "Why does it back up?" → "Because we have to re-type everything into the EHR."
> "Why re-type?" → "The EHR has no import, and IT said integration would take a year."

Now you know the real constraint (no EHR import) and a political fact (IT has already said no once).

### 4. Talk less: aim for under 30%

The customer should do most of the talking. If you're talking more than about 30% of the time, you're pitching, not discovering. Useful habits:

- **Pause** for 3 seconds after they finish. People often add the most important detail after a silence.
- **Summarize back:** "So what I'm hearing is… did I get that right?" This catches misunderstandings and makes people feel heard.
- **Avoid leading questions.** "Wouldn't it be great if AI did this?" teaches you nothing.

## An annotated transcript

Here's an excerpt from a real-style call with Priya, the intake lead at Brightline Health. Notice what the FDE does.

```text
FDE: Thanks for making time. Could you walk me through the last referral you handled today?
     ← Open question about a specific instance.
Priya: Sure. A fax came in at 8:10 from a cardiology practice. Leo printed it, typed the
       patient details into the EHR, then called the practice because the insurance ID
       was unreadable. It got entered around 2pm.
FDE: What happened between 8:10 and 2pm?
     ← Follow the thread instead of jumping to the next question.
Priya: Mostly waiting. The callback took 4 hours. Honestly about 30% of faxes have
       something unreadable.
     ← A quantified pain. Write it down exactly.
FDE: How many referrals come in on a typical day?
Priya: Around 120. We have 6 people on intake.
FDE: Is the delay a problem for anyone outside your team?
Priya: Oh yes. Patients wait, and Dana's team gets complaints. We lost two referring
       practices last quarter because of slow turnaround.
     ← Business impact, and a hint about the sponsor's priorities.
FDE: So if I've got this right: about 120 referrals a day, 30% need a callback, and
     slow turnaround has cost you referring practices. Is that fair?
     ← Summarize back.
Priya: Exactly. And the callbacks are the worst part.
```

In under three minutes, the FDE learned the volume, the failure rate, the bottleneck, the business cost, and who else cares. They spoke about 25% of the words. In the next exercise you'll write code that measures exactly these things in a transcript.

## Red flags to listen for

| What you hear | What it might mean | What to do |
|---|---|---|
| "Everyone wants this." | Nobody specific owns it | Ask "Who would be most upset if we stopped?" |
| "The data is all in one place." | It almost never is | Ask for a sample this week |
| "IT is fine with it." | IT hasn't been asked | Get IT into a meeting early |
| "We tried this before…" | Past failure, possible scar tissue | Ask what happened and why |
| "Can it also do…?" (10 times) | Scope will sprawl | Capture, then prioritize together |
| Nobody can name a metric | No clear business case | Work out the cost of the problem together |

## After the call

Within 24 hours, send a short recap. This is the single most underrated FDE habit.

```
Subject: Recap — referral intake discovery (Mar 3)

Thanks Priya and Leo. What we heard:
  • ~120 referrals/day, 6 people on intake
  • ~30% need a callback (unreadable fields), adding hours of delay
  • Slow turnaround cost 2 referring practices last quarter
What we'll do next:
  • Profile 1 month of faxes to confirm the 30% and where errors cluster (Alex, by Mar 10)
What we need:
  • Access to the fax archive (Sam, by Mar 7)
Did we miss or misstate anything?
```

Ending with a question invites corrections. Corrections now are cheap; corrections in week six are not.

> **Key takeaways**
> - Prepare hypotheses and send an agenda; spend most of the call on workflow.
> - Ask open questions about specific recent events, and quantify every pain.
> - Ask "why" repeatedly, summarize back, and keep your talk time under about 30%.
> - Send a written recap within 24 hours that ends with a question.
